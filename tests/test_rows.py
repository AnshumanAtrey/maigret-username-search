"""Row building from Maigret's per-site result dict (needs the maigret package, no network).

Run: python -m unittest discover -s tests -t .
"""
import unittest
from types import SimpleNamespace

from maigret.result import MaigretCheckResult, MaigretCheckStatus

from src.rows import is_profile, is_search_page_match, linked_usernames, profile_row

GITHUB = SimpleNamespace(tags=['coding', 'us'], url_main='https://www.github.com/', alexa_rank=30)
IDS = {'fullname': 'Soxoj', 'bio': 'CPO @ Social Links', 'location': 'Amsterdam, Netherlands',
       'follower_count': '2,252', 'created_at': '2017-08-14T17:03:07Z', 'image': 'https://a/1.png',
       'uid': '31013580', '_extractor': 'github'}


def result(status=MaigretCheckStatus.CLAIMED, ids=None, **extra) -> dict:
    res = {'site': GITHUB, 'url_user': 'https://github.com/soxoj',
           'status': MaigretCheckResult('soxoj', 'GitHub', 'https://github.com/soxoj', status, ids_data=ids)}
    res.update(extra)
    return res


def twitter_urls(url: str) -> dict:
    return {url.rsplit('/', 1)[-1]: 'username'} if url.startswith('https://twitter.com/') else {}


class Rows(unittest.TestCase):
    def test_flat_columns_and_details(self):
        row = profile_row('soxoj', None, 'GitHub', result(ids=dict(IDS)), twitter_urls, '2026-09-29T10:46:03+00:00')
        self.assertEqual((row['fullName'], row['bio'], row['location']), ('Soxoj', 'CPO @ Social Links', 'Amsterdam, Netherlands'))
        self.assertEqual((row['followers'], row['createdAt'], row['imageUrl']), (2252, '2017-08-14T17:03:07Z', 'https://a/1.png'))
        self.assertNotIn('_extractor', row['profileDetails'])
        self.assertEqual(row['profileDetails']['uid'], '31013580')
        self.assertEqual((row['siteTags'], row['siteCountries']), (['coding'], ['us']))
        self.assertEqual((row['profileUrl'], row['siteUrl'], row['linkedFrom']), ('https://github.com/soxoj', 'https://www.github.com/', None))

    def test_no_details_gives_empty_columns(self):
        row = profile_row('soxoj', 'jack on GitHub', 'GitHub', result(ids=None), twitter_urls, 't')
        self.assertEqual((row['fullName'], row['followers'], row['profileDetails'], row['linkedUsernames']), (None, None, {}, []))
        self.assertEqual(row['linkedFrom'], 'jack on GitHub')

    def test_linked_usernames_from_fields_and_links(self):
        res = result(ids_usernames={'sox0j': 'username', 'Soxoj': 'username', '12345': 'gaia_id'},
                     ids_links=['https://twitter.com/SOX0J', 'https://twitter.com/other', 'https://example.org/x'])
        self.assertEqual(linked_usernames('soxoj', res, twitter_urls), ['other', 'sox0j'])

    def test_profile_and_search_page(self):
        self.assertTrue(is_profile(result()))
        self.assertFalse(is_profile(result(MaigretCheckStatus.AVAILABLE)))
        self.assertFalse(is_profile(result(MaigretCheckStatus.UNKNOWN)))
        self.assertFalse(is_profile(result(is_similar=True)))
        self.assertTrue(is_search_page_match(result(is_similar=True)))
        self.assertFalse(is_profile({'site': GITHUB}))


if __name__ == '__main__':
    unittest.main()
