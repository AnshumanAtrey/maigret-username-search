"""Input reading: defaults, what people paste, soft fixes and the plain error messages.

Run: python -m unittest discover -s tests -t .
"""
import unittest

from src.inputs import InputError, parse_input, read_username

KNOWN_TAGS = {'social', 'forum', 'gaming', 'coding', 'dating', 'porn', 'us', 'in', 'de', 'gb', 'ru'}


def github_urls(url: str) -> dict:
    """Stand-in for MaigretDatabase.extract_ids_from_url: knows GitHub only."""
    prefix = 'https://github.com/'
    return {url[len(prefix):].strip('/'): 'username'} if url.startswith(prefix) and url[len(prefix):].strip('/') else {}


def parse(raw: dict):
    return parse_input(raw, KNOWN_TAGS, github_urls)


class Defaults(unittest.TestCase):
    def test_example_input(self):
        cfg = parse({'usernames': ['soxoj'], 'maxSites': 500})
        self.assertEqual(cfg.usernames, ['soxoj'])
        self.assertEqual(cfg.max_sites, 500)
        self.assertEqual((cfg.tags, cfg.recursive, cfg.details, cfg.timeout, cfg.retries), ([], True, True, 30, 0))
        self.assertEqual((cfg.notes, cfg.skipped), ([], []))

    def test_only_the_username_checks_every_site(self):
        self.assertIsNone(parse({'usernames': ['soxoj']}).max_sites)

    def test_empty_zero_and_all_mean_every_site(self):
        for value in (None, '', 0, '0', 'all'):
            self.assertIsNone(parse({'usernames': ['a'], 'maxSites': value}).max_sites, value)

    def test_negative_site_count_checks_every_site_with_a_note(self):
        cfg = parse({'usernames': ['a'], 'maxSites': -5})
        self.assertIsNone(cfg.max_sites)
        self.assertIn('below 1', cfg.notes[0])


class Usernames(unittest.TestCase):
    def test_handles_commas_and_duplicates(self):
        cfg = parse({'usernames': ['@soxoj, torvalds', 'Soxoj', ' ', 'torvalds;jack']})
        self.assertEqual(cfg.usernames, ['soxoj', 'torvalds', 'jack'])

    def test_case_is_kept(self):
        self.assertEqual(parse({'usernames': ['JohnDoe']}).usernames, ['JohnDoe'])

    def test_a_single_string_is_accepted(self):
        self.assertEqual(parse({'usernames': 'soxoj,torvalds'}).usernames, ['soxoj', 'torvalds'])

    def test_profile_link_read_by_maigret_patterns(self):
        cfg = parse({'usernames': ['https://github.com/soxoj']})
        self.assertEqual(cfg.usernames, ['soxoj'])
        self.assertIn('from the link', cfg.notes[0])

    def test_link_without_scheme(self):
        self.assertEqual(parse({'usernames': ['github.com/soxoj']}).usernames, ['soxoj'])

    def test_unknown_site_link_uses_the_last_part(self):
        cfg = parse({'usernames': ['https://x.com/elonmusk?lang=en', 'https://www.youtube.com/@mkbhd/']})
        self.assertEqual(cfg.usernames, ['elonmusk', 'mkbhd'])
        self.assertIn('last part of the link', cfg.notes[0])

    def test_dotted_handle_is_not_a_link(self):
        self.assertEqual(read_username('john.doe'), ('john.doe', None))

    def test_link_with_no_username_is_skipped(self):
        cfg = parse({'usernames': ['https://github.com/', 'soxoj']})
        self.assertEqual(cfg.usernames, ['soxoj'])
        self.assertIn('no username', cfg.skipped[0][1])

    def test_space_is_skipped_with_a_suggestion(self):
        cfg = parse({'usernames': ['John Doe', 'soxoj']})
        self.assertEqual(cfg.usernames, ['soxoj'])
        self.assertIn('Did you mean JohnDoe?', cfg.skipped[0][1])

    def test_hash_and_long_text_are_skipped(self):
        cfg = parse({'usernames': ['a#b', 'x' * 101, 'ok']})
        self.assertEqual(cfg.usernames, ['ok'])
        self.assertEqual(len(cfg.skipped), 2)

    def test_nothing_usable_fails_with_what_to_type(self):
        for raw in ({}, {'usernames': []}, {'usernames': ['   ']}, {'usernames': ['John Doe']}):
            with self.assertRaises(InputError) as err:
                parse(raw)
            self.assertIn('Enter at least one username', str(err.exception))
        with self.assertRaises(InputError) as err:
            parse({'usernames': ['John Doe']})
        self.assertIn('Did you mean JohnDoe?', str(err.exception))


class Tags(unittest.TestCase):
    def test_types_countries_and_aliases(self):
        cfg = parse({'usernames': ['a'], 'tags': ['Social', 'forums', 'India', 'USA', 'UK', '#gaming', 'social']})
        self.assertEqual(cfg.tags, ['social', 'forum', 'in', 'us', 'gb', 'gaming'])
        self.assertEqual(cfg.notes, [])

    def test_adult_means_the_adult_tag(self):
        self.assertEqual(parse({'usernames': ['a'], 'tags': ['adult']}).tags, ['porn'])

    def test_unknown_tag_is_dropped_with_a_note(self):
        cfg = parse({'usernames': ['a'], 'tags': ['social', 'nosuchtag']})
        self.assertEqual(cfg.tags, ['social'])
        self.assertIn('nosuchtag', cfg.notes[0])

    def test_only_unknown_tags_fail(self):
        with self.assertRaises(InputError) as err:
            parse({'usernames': ['a'], 'tags': ['nosuchtag']})
        self.assertIn('Leave it empty to search every site', str(err.exception))

    def test_comma_string(self):
        self.assertEqual(parse({'usernames': ['a'], 'tags': 'coding, dating'}).tags, ['coding', 'dating'])


class Switches(unittest.TestCase):
    def test_strings_and_null(self):
        cfg = parse({'usernames': ['a'], 'recursive': 'false', 'details': None})
        self.assertEqual((cfg.recursive, cfg.details), (False, True))

    def test_numbers_are_clamped_with_a_note(self):
        cfg = parse({'usernames': ['a'], 'timeout': 1, 'retries': '9'})
        self.assertEqual((cfg.timeout, cfg.retries), (5, 3))
        self.assertEqual(len(cfg.notes), 2)

    def test_unreadable_number_keeps_the_default(self):
        cfg = parse({'usernames': ['a'], 'timeout': 'soon'})
        self.assertEqual(cfg.timeout, 30)
        self.assertIn('Could not read timeout', cfg.notes[0])


if __name__ == '__main__':
    unittest.main()
