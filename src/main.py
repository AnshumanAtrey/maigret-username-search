"""
Maigret Username Search - the accounts that use a username on 5,000+ sites, with the profile details
Maigret reads from each page.

Wraps soxoj/maigret 0.6.6 (MIT) as a library, not a subprocess:
- Sites: Maigret's bundled database (maigret.db_updater.BUNDLED_DB_PATH; Settings().sites_db_path is a
  relative path that only resolves inside the package) without the sites Maigret marks disabled.
  maxSites keeps the most popular N, and Maigret adds the mirror sites of those N, as its CLI does.
- One maigret.checking.maigret() scan per username, in this event loop. It writes every finished site
  check into an output_container dict: that feeds the progress message, and a scan cut by the run's
  time limit keeps every site it already checked.
- Linked usernames (rows.linked_usernames) are searched after the typed ones when recursive is on,
  at most MAX_LINKED per run, each billed like a typed one.
- Charging: one "profile" event per delivered row. A username found nowhere, a skipped entry and a
  run that fails on its input cost $0. The SDK delivers only the rows the spending limit can pay for
  (most popular sites first); after that no further username is started.
- No summary row in the dataset (CSV and Excel exports hold profiles only). The summary is the
  OUTPUT record, written after each username and at the end.
- The run SUCCEEDS when at least one scan ran, including one that found nothing (that is an answer),
  and FAILS when the input cannot be read or no scan could run.
- The status message can never fail the run: SDK 3.x raises on some run origins after storing it.
"""
import asyncio
import logging
import sys
import time
from datetime import datetime, timezone
from functools import lru_cache

from apify import Actor
from maigret.checking import maigret as maigret_scan
from maigret.db_updater import BUNDLED_DB_PATH
from maigret.notify import QueryNotifyPrint
from maigret.result import MaigretCheckStatus
from maigret.sites import MaigretDatabase

from .inputs import Config, InputError, parse_input
from .rows import is_profile, is_search_page_match, profile_row

PROFILE_EVENT = 'profile'        # must equal the event key of the pricing in .actor/store.json
MAX_LINKED = 3                   # linked usernames searched per run: 4 scans of 500 sites stay far inside the
                                 # 5-minute daily QA run of the prefill (about 50 s each, measured 2026-09-29)
MAX_CONNECTIONS = 100            # Maigret's own default
RUN_SAFETY_MARGIN_S = 45         # cut a scan this close to the run's time limit, so rows and OUTPUT are saved
MIN_SCAN_S = 15                  # start a username only if at least this much scanning fits before the cut
PROGRESS_EVERY_S = 10            # status message refresh while a scan runs
STOP_REASONS = {
    'limit': 'your spending limit for this run was reached. Raise the limit to get the rest.',
    'time': 'the run was about to reach its time limit. Raise the run timeout to get the rest.',
}

logging.getLogger('maigret').setLevel(logging.CRITICAL)   # blocked sites are expected; OUTPUT counts them


async def safe_status(message: str) -> None:
    """Set the run's status message without ever failing the run (see the module docstring)."""
    try:
        await Actor.set_status_message(message[:500])
    except Exception as exc:  # noqa: BLE001
        Actor.log.debug(f'status message stored but not confirmed by the SDK: {exc}')


def seconds_left_in_run() -> float | None:
    """Seconds until the platform stops this run, or None when not on the platform."""
    config = getattr(Actor, 'configuration', None) or getattr(Actor, 'config', None)
    timeout_at = getattr(config, 'timeout_at', None) if config else None
    if not timeout_at:
        return None
    return (timeout_at - datetime.now(timezone.utc)).total_seconds()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def plural(n: int, word: str) -> str:
    return f'{n:,} {word}' + ('' if n == 1 else 's')


class Delivery:
    """Pushes profile rows charged as PROFILE_EVENT and notices the spending limit."""

    def __init__(self):
        self.cm = Actor.get_charging_manager()
        self.ppe = self.cm.get_pricing_info().is_pay_per_event
        self.rows = 0
        self.limit = False

    def can_pay(self) -> bool:
        if self.ppe and not self.limit:
            left = self.cm.calculate_max_event_charge_count_within_limit(PROFILE_EVENT)
            self.limit = left is not None and left < 1
        return not self.limit

    async def push(self, rows: list[dict]) -> int:
        """Returns how many rows were delivered: the SDK drops the rows the limit cannot pay for."""
        if not rows:
            return 0
        result = await Actor.push_data(rows, charged_event_name=PROFILE_EVENT)
        done = result.charged_count if self.ppe else len(rows)
        if self.ppe and (result.event_charge_limit_reached or done < len(rows)):
            self.limit = True
        self.rows += done
        return done


class Run:
    def __init__(self, cfg: Config, db: MaigretDatabase, sites: dict, delivery: Delivery):
        self.cfg, self.db, self.sites, self.delivery = cfg, db, sites, delivery
        self.queue = [{'username': u, 'linkedFrom': None} for u in cfg.usernames]
        self.queued = {u.lower() for u in cfg.usernames}
        self.entries: list[dict] = []
        self.stop: str | None = None
        self.started = time.monotonic()
        self.checked_at = now_iso()
        self.url_to_usernames = lru_cache(maxsize=4096)(db.extract_ids_from_url)

    def progress_line(self, entry: dict, container: dict) -> str:
        found = sum(1 for res in container.values() if is_profile(res))
        saved = f' {plural(self.delivery.rows, "profile")} saved so far.' if self.delivery.rows else ''
        return (f'Searching {entry["username"]} ({len(self.entries)} of {len(self.queue)}): '
                f'{len(container):,} of {len(self.sites):,} sites checked, {plural(found, "profile")} found.{saved}')

    async def scan(self, entry: dict) -> None:
        cfg, container, t0 = self.cfg, {}, time.monotonic()
        task = asyncio.create_task(maigret_scan(
            username=entry['username'], site_dict=self.sites, logger=logging.getLogger('maigret'),
            query_notify=QueryNotifyPrint(color=False, silent=True, print_found_only=True),
            timeout=cfg.timeout, retries=cfg.retries, max_connections=MAX_CONNECTIONS,
            is_parsing_enabled=cfg.details, is_enrich_enabled=cfg.details, id_type='username',
            no_progressbar=True, output_container=container))
        cut = False
        while not task.done():
            left = seconds_left_in_run()
            wait = PROGRESS_EVERY_S if left is None else min(PROGRESS_EVERY_S, left - RUN_SAFETY_MARGIN_S)
            if wait <= 0:
                task.cancel()
                cut = True
                break
            await asyncio.wait({task}, timeout=wait)
            if not task.done():
                await safe_status(self.progress_line(entry, container))
        try:
            results = await task
        except asyncio.CancelledError:
            if not cut:
                raise
            results = container
        except Exception as exc:  # noqa: BLE001 - one bad scan must not lose the others
            entry['error'] = f'{type(exc).__name__}: {exc}'[:300]
            Actor.log.error(f'{entry["username"]}: the scan stopped with {entry["error"]}')
            results = container

        found = sorted(((name, res) for name, res in results.items() if is_profile(res)),
                       key=lambda item: (getattr(item[1].get('site'), 'alexa_rank', sys.maxsize), item[0].lower()))
        rows = [profile_row(entry['username'], entry['linkedFrom'], name, res, self.url_to_usernames, self.checked_at)
                for name, res in found]
        saved = await self.delivery.push(rows)
        entry.update({
            # a scan that broke after checking some sites still delivered (and charged) those rows
            'status': 'error' if entry.get('error') and not results else
                      'partial' if cut or saved < len(rows) or entry.get('error') else 'done',
            'sitesChecked': len(results),
            'sitesWithErrors': sum(1 for res in results.values()
                                   if getattr(res.get('status'), 'status', None) == MaigretCheckStatus.UNKNOWN),
            'searchPageMatches': sum(1 for res in results.values() if is_search_page_match(res)),
            'profilesFound': len(rows),
            'profilesSaved': saved,
            'seconds': round(time.monotonic() - t0, 1),
        })
        if cut:
            self.stop = 'time'
        elif self.delivery.limit:
            self.stop = 'limit'
        if cfg.recursive and not self.stop:
            self.queue_linked(entry['username'], rows[:saved])

    def queue_linked(self, username: str, rows: list[dict]) -> None:
        linked = sum(1 for item in self.queue if item['linkedFrom'])
        for row in rows:
            for handle in row['linkedUsernames']:
                if linked >= MAX_LINKED:
                    return
                if handle.lower() not in self.queued:
                    self.queued.add(handle.lower())
                    self.queue.append({'username': handle, 'linkedFrom': f'{username} on {row["siteName"]}'})
                    linked += 1
                    Actor.log.info(f'Queued the linked username {handle} (found on the {row["siteName"]} profile of {username})')

    async def execute(self) -> None:
        index = 0
        while index < len(self.queue):
            item = self.queue[index]
            index += 1
            entry = {'username': item['username'], 'linkedFrom': item['linkedFrom'], 'status': 'not started'}
            self.entries.append(entry)
            left = seconds_left_in_run()
            if not self.stop and left is not None and left < RUN_SAFETY_MARGIN_S + MIN_SCAN_S:
                self.stop = 'time'
            if not self.stop and not self.delivery.can_pay():
                self.stop = 'limit'
            if self.stop:
                continue
            await safe_status(self.progress_line(entry, {}))
            await self.scan(entry)
            Actor.log.info(f'{entry["username"]}: {plural(entry["profilesSaved"], "profile")} saved from '
                           f'{entry["sitesChecked"]:,} sites in {entry["seconds"]} s '
                           f'({entry["sitesWithErrors"]:,} sites could not be checked)')
            await self.write_output(final=False)

    def ran(self) -> list[dict]:
        return [e for e in self.entries if e['status'] in ('done', 'partial')]

    def message(self) -> str:
        ran = self.ran()
        typed = [e for e in ran if not e['linkedFrom']]
        linked = len(ran) - len(typed)
        seconds = round(time.monotonic() - self.started)
        cut = next((e for e in ran if e['sitesChecked'] < len(self.sites)), None)
        where = f'{len(self.sites):,} sites' + (f' ({cut["username"]} stopped after {cut["sitesChecked"]:,})' if cut else '')
        if not ran:
            first_error = next((e['error'] for e in self.entries if e.get('error')), None)
            text = 'No search could run' + (f': {first_error}' if first_error else '.')
        elif self.delivery.rows:
            text = (f'Found {plural(self.delivery.rows, "profile")} for {plural(len(typed), "username")}'
                    + (f' and {plural(linked, "linked username")}' if linked else '')
                    + f' on {where} in {seconds} s.')
        else:
            text = (f'No profiles found for {", ".join(e["username"] for e in typed)} on {where} in {seconds} s. '
                    f'The username may not be in use, or the sites that have it refused the check.')
        if self.stop:
            text += f' Stopped early: {STOP_REASONS[self.stop]}'
        skipped = len(self.cfg.skipped)
        if skipped:
            text += f' Skipped {skipped} entr{"y" if skipped == 1 else "ies"}: {self.cfg.skipped[0][1]}'
        return text

    def output(self, status: str) -> dict:
        cfg = self.cfg
        return {
            'status': status,
            'message': self.message(),
            'profilesSaved': self.delivery.rows,
            'sitesPerUsername': len(self.sites),
            'usernames': self.entries,
            'notes': cfg.notes,
            'skipped': [{'input': text, 'reason': why} for text, why in cfg.skipped],
            'settings': {'maxSites': cfg.max_sites, 'tags': cfg.tags, 'recursive': cfg.recursive,
                         'details': cfg.details, 'timeout': cfg.timeout, 'retries': cfg.retries},
            'finishedAt': now_iso() if status != 'running' else None,
        }

    async def write_output(self, final: bool) -> None:
        status = ('partial' if self.stop else 'done') if self.ran() else 'failed'
        try:
            await Actor.set_value('OUTPUT', self.output(status if final else 'running'))
        except Exception as exc:  # noqa: BLE001
            Actor.log.warning(f'Could not write the OUTPUT record: {exc}')


def load_database() -> MaigretDatabase:
    return MaigretDatabase().load_from_path(BUNDLED_DB_PATH)


def select_sites(db: MaigretDatabase, cfg: Config) -> dict:
    return db.ranked_sites_dict(top=cfg.max_sites or sys.maxsize, tags=cfg.tags, disabled=False, id_type='username')


async def main() -> None:
    async with Actor:
        raw = await Actor.get_input() or {}
        db = load_database()
        known_tags = {str(t).lower() for site in db.sites for t in site.tags}
        try:
            cfg = parse_input(raw, known_tags, db.extract_ids_from_url)
            sites = select_sites(db, cfg)
            if not sites:
                raise InputError('No site matches these tags together with the site limit. Remove a tag or '
                                 'leave maxSites empty to search every site.')
        except InputError as exc:
            await Actor.set_value('OUTPUT', {'status': 'failed', 'message': str(exc)})
            await Actor.fail(status_message=str(exc))
            return
        delivery = Delivery()
        Actor.log.info(f'Maigret Username Search: {plural(len(cfg.usernames), "username")} on {len(sites):,} of '
                       f'{len(db.sites):,} sites (maxSites={cfg.max_sites or "all"}, tags={cfg.tags or "all"}, '
                       f'recursive={cfg.recursive}, details={cfg.details}, timeout={cfg.timeout} s, '
                       f'retries={cfg.retries}, payPerEvent={delivery.ppe})')
        for note in cfg.notes:
            Actor.log.warning(note)
        for text, why in cfg.skipped:
            Actor.log.warning(f'Skipped "{text}": {why}')
        run = Run(cfg, db, sites, delivery)
        await run.execute()
        message = run.message()
        Actor.log.info(message)
        await run.write_output(final=True)
        if run.ran():
            await safe_status(message)
        else:
            await Actor.fail(status_message=message[:500])


if __name__ == '__main__':
    asyncio.run(main())
