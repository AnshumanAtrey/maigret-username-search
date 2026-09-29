"""
One dataset row per found profile, from Maigret's per-site result dict (maigret.result.SiteResult).

The flat columns (name, bio, location) read the same ids_data keys, in the same order, as Maigret's own
report (maigret/report.py field_sources), so CSV exports get them as columns; every key Maigret
extracted stays in profileDetails. Linked usernames are the ones Maigret itself would search next:
its ids_usernames plus the usernames in the page's links (maigret.maigret.extract_ids_from_results).
"""
from maigret.result import MaigretCheckStatus
from maigret.utils import is_country_tag

FLAT = {                                   # column -> ids_data keys, first non-empty wins
    'fullName': ('fullname', 'name'),
    'bio': ('bio', 'about', 'description'),
    'location': ('location', 'country', 'city', 'country_code', 'locale', 'region'),
    'createdAt': ('created_at',),
    'imageUrl': ('image',),
}
FOLLOWERS = ('follower_count',)


def is_profile(res: dict) -> bool:
    """Found, and a profile page: sites marked similar_search answer with a search page
    (StackOverflow, Google Scholar, 11 sites in Maigret 0.6.6), which is not an account."""
    status = res.get('status')
    return bool(status) and status.status == MaigretCheckStatus.CLAIMED and not res.get('is_similar')


def is_search_page_match(res: dict) -> bool:
    status = res.get('status')
    return bool(status) and status.status == MaigretCheckStatus.CLAIMED and bool(res.get('is_similar'))


def _first(ids: dict, keys: tuple) -> str | None:
    for key in keys:
        value = ids.get(key)
        if value not in (None, '', [], {}):
            return str(value).strip() or None
    return None


def _count(value) -> int | None:
    digits = str(value or '').replace(',', '').strip()
    return int(digits) if digits.isdigit() else None


def linked_usernames(username: str, res: dict, url_to_usernames) -> list[str]:
    """Other usernames on this profile page: Maigret's ids_usernames of type username, plus the
    usernames Maigret's site patterns read from the page's links. The searched name is left out."""
    found: dict[str, str] = {}
    for handle, kind in (res.get('ids_usernames') or {}).items():
        if kind == 'username':
            found.setdefault(str(handle).lower(), str(handle))
    for link in res.get('ids_links') or []:
        for handle, kind in url_to_usernames(str(link)).items():
            if kind == 'username':
                found.setdefault(str(handle).lower(), str(handle))
    found.pop(username.lower(), None)
    return sorted(found.values(), key=str.lower)


def profile_row(username: str, linked_from: str | None, site_name: str, res: dict, url_to_usernames,
                checked_at: str) -> dict:
    site = res.get('site')
    ids = {str(k): v for k, v in (getattr(res.get('status'), 'ids_data', None) or {}).items()
           if not str(k).startswith('_')}          # _extractor and the like are Maigret internals
    tags = [str(t) for t in (getattr(site, 'tags', None) or [])]
    return {
        'username': username,
        'siteName': site_name,
        'profileUrl': res.get('url_user') or None,
        'fullName': _first(ids, FLAT['fullName']),
        'bio': _first(ids, FLAT['bio']),
        'location': _first(ids, FLAT['location']),
        'followers': _count(_first(ids, FOLLOWERS)),
        'createdAt': _first(ids, FLAT['createdAt']),
        'imageUrl': _first(ids, FLAT['imageUrl']),
        'linkedUsernames': linked_usernames(username, res, url_to_usernames),
        'links': [str(link) for link in (res.get('ids_links') or [])],
        'profileDetails': ids,
        'siteUrl': getattr(site, 'url_main', None) or None,
        'siteTags': [t for t in tags if not is_country_tag(t)],
        'siteCountries': [t for t in tags if is_country_tag(t)],
        'linkedFrom': linked_from,
        'checkedAt': checked_at,
    }
