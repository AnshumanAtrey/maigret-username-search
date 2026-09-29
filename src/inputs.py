"""
What people type -> a clean run configuration (manager/rules/SEO.md section 11.5).

One required field (usernames); every other field has a working default. Accepted as typed: @handles,
several usernames on one line split by commas, a pasted profile link (read with Maigret's own URL
patterns first, then the last part of the link), country names in the tag filter, and switches or
numbers sent as strings. Input that can be read one obvious way is fixed and noted; only input that
cannot be read fails, before anything is charged.

Pure module: no Apify or Maigret import, so the tests run without the network.
"""
import re
from dataclasses import dataclass, field

DEFAULT_TIMEOUT = 30          # Maigret's own default (maigret/resources/settings.json)
DEFAULT_RETRIES = 0           # Maigret's own default
TIMEOUT_RANGE = (5, 120)      # our guard: under 5 s most sites fail, over 120 s one dead site stalls a scan
RETRIES_RANGE = (0, 3)
MAX_USERNAME_CHARS = 100      # our guard: a longer "username" is pasted text, not a handle
BAD_CHARS = '#'               # maigret.checking.BAD_CHARS: Maigret refuses these usernames itself
SPLIT = re.compile(r'[,;\n\r\t]+')
URL_START = re.compile(r'^(?:[a-z][a-z0-9+.-]*://|(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)+/)', re.I)
SCHEME = re.compile(r'^[a-z][a-z0-9+.-]*://', re.I)
TAG_ALIASES = {'forums': 'forum', 'games': 'gaming', 'game': 'gaming', 'programming': 'coding', 'developer': 'coding',
               'adult': 'porn', 'nsfw': 'porn', 'videos': 'video', 'photos': 'photo', 'blogs': 'blog',
               'uk': 'gb', 'england': 'gb', 'usa': 'us', 'america': 'us'}
POPULAR_TAGS = 'social, forum, gaming, coding, dating, crypto, finance, music, photo, video, news, shopping'


class InputError(ValueError):
    """Input that cannot be read. The message says what to type."""


@dataclass
class Config:
    usernames: list[str]
    max_sites: int | None = None          # None: every site in the database
    tags: list[str] = field(default_factory=list)
    recursive: bool = True
    details: bool = True
    timeout: int = DEFAULT_TIMEOUT
    retries: int = DEFAULT_RETRIES
    notes: list[str] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)


def _items(value) -> list[str]:
    """A list, or one string, -> the separate entries (commas, semicolons and new lines split)."""
    raw = value if isinstance(value, list) else [value] if isinstance(value, str) else []
    return [part.strip() for item in raw if isinstance(item, str) for part in SPLIT.split(item) if part.strip()]


def read_username(token: str, url_to_usernames=None) -> tuple[str | None, str | None]:
    """One entry -> (username, note). A link is read with url_to_usernames (Maigret's site patterns),
    then its last part. Returns (None, reason) when no username can be read."""
    s = token.strip().strip('"\'<>()[]')
    if not URL_START.match(s):
        return s.lstrip('@').strip(), None
    link = s if SCHEME.match(s) else f'https://{s}'
    found = [u for u, kind in (url_to_usernames(link) if url_to_usernames else {}).items() if kind == 'username']
    if found:
        return found[0], f'Read the username "{found[0]}" from the link {s}.'
    path = SCHEME.sub('', s).split('?', 1)[0].split('#', 1)[0]
    parts = [p for p in path.split('/') if p][1:]            # drop the host
    if parts and parts[-1].lstrip('@'):
        username = parts[-1].lstrip('@')
        return username, f'Read the username "{username}" from the last part of the link {s}.'
    return None, f'"{s}" is a link with no username in it. Paste the profile link, such as https://github.com/torvalds.'


def why_not_username(username: str) -> str | None:
    if any(c.isspace() for c in username):
        joined = ''.join(username.split())
        return (f'"{username}" has a space, and usernames cannot. Did you mean {joined}? '
                f'Put each username on its own line.')
    if any(c in username for c in BAD_CHARS):
        return f'"{username}" has a "#", which Maigret cannot search.'
    if len(username) > MAX_USERNAME_CHARS:
        return f'"{username[:40]}..." is longer than {MAX_USERNAME_CHARS} characters, so it is not a username.'
    return None


def parse_usernames(value, url_to_usernames=None) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    """-> (usernames, notes, skipped). Case is kept as typed; duplicates are dropped ignoring case."""
    usernames, notes, skipped, seen = [], [], [], set()
    for token in _items(value):
        username, note = read_username(token, url_to_usernames)
        if username is None:
            skipped.append((token, note))
            continue
        problem = why_not_username(username)
        if problem:
            skipped.append((token, problem))
            continue
        if note:
            notes.append(note)
        if username.lower() not in seen:
            seen.add(username.lower())
            usernames.append(username)
    return usernames, notes, skipped


def _number(value, key: str, default: int, lo: int, hi: int, notes: list[str]) -> int:
    if value is None or value == '':
        return default
    try:
        n = int(float(str(value).strip()))
    except ValueError:
        notes.append(f'Could not read {key} "{value}" as a number, so it is {default}.')
        return default
    if not lo <= n <= hi:
        fixed = min(max(n, lo), hi)
        notes.append(f'{key} {n} is outside {lo} to {hi}, so it is {fixed}.')
        return fixed
    return n


def parse_max_sites(value, notes: list[str]) -> int | None:
    """None, empty, 0 or "all" -> every site. Anything else -> the most popular N."""
    if value is None or str(value).strip().lower() in ('', 'all', '0'):
        return None
    try:
        n = int(float(str(value).strip()))
    except ValueError:
        notes.append(f'Could not read maxSites "{value}" as a number, so every site is checked.')
        return None
    if n < 1:
        notes.append(f'maxSites {n} is below 1, so every site is checked.')
        return None
    return n


def _country_code(name: str) -> str | None:
    """"India" -> "in". pycountry ships with Maigret; without it, names are not translated."""
    try:
        import pycountry
        return pycountry.countries.lookup(name).alpha_2.lower()
    except (ImportError, LookupError):
        return None


def parse_tags(value, known_tags: set[str] | None, notes: list[str]) -> list[str]:
    """Site types and countries -> Maigret tags. Unknown tags are dropped with a note; when none is
    known the run cannot be what was asked, so it fails before anything is charged."""
    wanted = [t.lower().lstrip('#') for t in _items(value)]
    if not wanted or known_tags is None:
        return wanted
    tags, unknown = [], []
    for tag in wanted:
        if len(tag) > 2 and tag not in known_tags:
            tag = TAG_ALIASES.get(tag) or _country_code(tag) or tag
        tag = TAG_ALIASES.get(tag, tag)
        if tag in known_tags:
            if tag not in tags:
                tags.append(tag)
        else:
            unknown.append(tag)
    if unknown and tags:
        notes.append(f'No site has the tag {", ".join(unknown)}, so it was left out.')
    if unknown and not tags:
        raise InputError(f'No site has the tag {", ".join(unknown)}. Use site types such as {POPULAR_TAGS}, '
                         f'or two-letter country codes such as us, in or de. Leave it empty to search every site.')
    return tags


def parse_bool(value, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ('true', 'yes', 'on', '1'):
        return True
    if isinstance(value, str) and value.strip().lower() in ('false', 'no', 'off', '0'):
        return False
    return default


def parse_input(raw: dict | None, known_tags: set[str] | None = None, url_to_usernames=None) -> Config:
    raw = raw or {}
    usernames, notes, skipped = parse_usernames(raw.get('usernames'), url_to_usernames)
    if not usernames:
        reason = f' {skipped[0][1]}' if skipped else ''
        raise InputError('Enter at least one username to search, for example soxoj. You can paste an '
                         f'@handle or a profile link such as https://github.com/soxoj.{reason}')
    return Config(
        usernames=usernames,
        max_sites=parse_max_sites(raw.get('maxSites'), notes),
        tags=parse_tags(raw.get('tags'), known_tags, notes),
        recursive=parse_bool(raw.get('recursive'), True),
        details=parse_bool(raw.get('details'), True),
        timeout=_number(raw.get('timeout'), 'timeout', DEFAULT_TIMEOUT, *TIMEOUT_RANGE, notes),
        retries=_number(raw.get('retries'), 'retries', DEFAULT_RETRIES, *RETRIES_RANGE, notes),
        notes=notes,
        skipped=skipped,
    )
