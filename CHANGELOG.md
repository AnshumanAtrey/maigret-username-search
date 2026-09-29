# Changelog

## [1.0] - 2026-09-29

First release: Maigret 0.6.6 (soxoj/maigret, MIT) run as a Python library on Apify.

### Added
- Username search on the 5,178 working sites of Maigret's bundled database (the 694 sites Maigret marks
  disabled are skipped), most popular first. `maxSites` keeps the top N (the form starts at 500); empty
  means every site, as Maigret's `-a`.
- One dataset row per account found: site, profile link, and what Maigret reads from the page (name, bio,
  location, followers, join date, photo, links, every extracted field in `profileDetails`), plus the site's
  type and country tags. Sites that answer with a search page instead of a profile (11 in Maigret 0.6.6)
  are left out and counted in the summary.
- Linked usernames: the usernames Maigret finds on the profiles (its own fields and link patterns) are
  searched after the typed ones when `recursive` is on, up to 3 per run, each row marked with `linkedFrom`.
- Input read as people type it: @handles, comma-separated usernames, profile links (Maigret's site patterns,
  then the last part of the link), site types and country names in `tags`, switches and numbers as strings.
  Unreadable entries are skipped with a plain note; a form with no usable username fails at $0.
- Pay per event: one `profile` event per saved row, $0.015. No start fee. The spending limit is checked before
  each username; rows are saved most popular site first, so a limit keeps the best rows.
- The run stops scanning 45 s before its time limit and keeps every site already checked (Maigret's
  `output_container`), with the reason in the status message.
- `OUTPUT` summary: each username with its status, sites checked, sites that could not be checked, search-page
  matches, profiles found and saved, the notes about the input and the settings used.
