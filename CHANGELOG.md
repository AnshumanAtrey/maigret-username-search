# Changelog

## 2026-11-14

- A run given no username (a blank row, which Apify's input check lets through) no longer fails with "Enter at least
  one username". It searches the form's example, soxoj on the top 500 sites, free of charge, and says so in the
  status message, so the run shows what it returns. Typed text that is not a username still fails with the reason.

## [1.0] - 2026-10-30: SDK 4, Store discounts, example tasks

- Apify SDK 4 (`apify>=4.1,<5`): SDK 3.4.1 raised on runs started by Apify's AI assistant (run origin APIFY_AI)
  wherever a status message was read back. `pycountry`, which `src/inputs.py` imports, is now declared instead of
  arriving through maigret. 41 tests pass; the example (soxoj, 500 sites) gave 36 profiles and 36 charges locally.
- Store discounts: $0.0135 per profile on Scale, $0.012 on Business and above; Free and Starter stay at $0.015.
- Three example tasks on the Store (`.actor/tasks.json`, published by CI).

## [1.0] - 2026-10-07: fewer failed runs

Four of the seven runs that other users shared with us in the week of 2026-10-01 failed, all of them on input or on a limit,
none on a scan: three from one free-plan user whose credit could not pay for one profile, one from a number typed in the
tags field. A failed run shows in the Actor's run statistics whoever caused it, and maigret had the lowest quality score
in the portfolio (0.74, 30th percentile, flagged for reliability).

### Changed
- **A run whose own limits leave no room to search now succeeds, with nothing searched or charged.** A spending limit
  that cannot pay for one profile ($0.015), or a timeout under a minute, used to end the run as failed with "No search could
  run". The status message now gives the numbers: "this run's spending limit is $0.0043, which cannot pay for one profile
  ($0.015). Raise the run's maximum cost in the run options, or add credit, then run it again." The `OUTPUT` record says
  `not_run`. A scan that broke before saving anything, and a form with no usable username, still fail.
- **A tag no site has no longer fails the run.** It is left out, noted in the status message and the `OUTPUT` record, and
  the scan stays as wide as it would be without the filter (options only narrow). A number in the tags field also points to
  the Number of sites field, which is what the user who typed `2000` meant. The same rule covers a real country tag whose
  sites are all disabled in Maigret (`mk`, `tm`), which used to fail with "No site matches these tags".
- **Input that is not an object reads as no input**, with the plain "Enter at least one username" message instead of a
  traceback.
- **One profile page that cannot be read no longer loses the scan.** It is left out with a warning and counted in
  `profilesLeftOut`; the other rows are saved.
- **An unexpected error no longer skips the summary.** The rows already saved stay, `OUTPUT` is written, the status message
  names the error (`partial` when something was saved, `failed` when not) and the traceback is in the log.

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
- Key-value store schema for the `OUTPUT` record, so Console shows it as a named collection.
- Default memory 2048 MB: measured on Apify, it finds the same accounts as 4096 MB for 24% to 42% less compute.
- `OUTPUT` summary: each username with its status, sites checked, sites that could not be checked, search-page
  matches, profiles found and saved, the notes about the input and the settings used.
