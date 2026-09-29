# Username Search & OSINT - Maigret Profile Finder, 5,000+ Sites

Username search on 5,000+ sites with Maigret: find the social media accounts that use a handle and read each profile's name, bio, followers and join date. Type a username and get one row per account found, with the profile link, the site, and what Maigret reads from the page: display name, bio, location, follower count, account creation date, photo, links and the other usernames on the profile. The actor then searches those linked usernames too, the way Maigret turns one handle into a full digital footprint.

Use it as a username lookup, username checker, Sherlock alternative or WhatsMyName alternative for OSINT, fraud and trust and safety work, with nothing to install: run Maigret in the cloud from the Apify Console, the Apify API, Python, JavaScript, n8n, Make or an AI agent through the Apify MCP server, and export the rows as JSON, CSV or Excel. **$0.015 per profile found** ($15 per 1,000). No start fee: a username found nowhere costs nothing. Only the username is required.

---

## What does it do?

It runs [Maigret](https://github.com/soxoj/maigret), the open-source username OSINT tool (38,000+ GitHub stars), on Apify. For each username you type, Maigret checks the sites in its database, 5,178 of them in Maigret 0.6.6 once the sites Maigret itself marks as broken are left out, and keeps the ones where an account with that username exists.

- **One row per account found**: site, profile link, site type (75 types, such as social, forum, coding and dating) and the site's country.
- **Profile details** read from the page wherever Maigret has an extractor for the site: name, bio, location, followers, join date, photo, links, account IDs. On 2026-09-29 that was 41% of the accounts found for soxoj and 28% for torvalds.
- **Linked usernames**: a GitHub page that links a Twitter handle gives a second username. With Follow linked names on, the actor searches it too (up to 3 per run) and marks each row with where it came from.
- **Most popular sites first**: set Number of sites to 500 for a one-minute scan of the big platforms, or leave it empty for the whole database.

## How is it different from other username search tools?

Many username search actors on the Store run Sherlock (about 400 sites) and report found or not found. This one runs Maigret, which checks more than ten times as many sites and reads the profile pages it finds.

| Actor | Tool it runs | Sites, as its title states | What you pay for |
|---|---|---|---|
| **This actor** | **Maigret 0.6.6** | **5,178 (counted in the bundled database)** | **each profile found** |
| misceres/sherlock | Sherlock | not stated | Apify platform usage |
| tri_angle/social-media-finder | own | 13 platforms (in its description) | start + each result |
| ntriqpro/maigret-actor | Maigret | 3000+ | run + each profile |
| ntriqpro/sherlock-username-osint | Sherlock | 400+ | each account |
| bovi/social-media-finder | own | not stated | each profile |
| automation-lab/username-checker | own | 460+ | run + each username |
| lofomachines/watson | Watson | not stated | start + each account |
| datacach/userrecon | Sherlock | not stated | start + each result |
| crawlerbros/social-media-finder | own | 400+ (in its description) | start + each result |
| ntriqpro/socialscan-osint | socialscan | not stated | run + each account |
| bovi/maigret-username-osint | Maigret | 3000+ | start + each profile |
| anshumanatrey/social-analyzer | social-analyzer | 900+ | each profile |
| khadinakbar/username-osint-scraper | Sherlock | 480+ | start + each username |
| crawlerbros/sherlock-scraper | Sherlock | not stated | start + each result |

Inclusion rule: every actor that looks up one username or nickname across many sites and appeared in the Apify Store searches for username search, username lookup, username checker, username osint, social media finder, sherlock and maigret on 2026-09-29 with 30 or more users in the last 30 days, ordered by those users. social-analyzer is by the same maintainer.

What this actor adds on top of the Maigret command line: no Python install, a form, bulk usernames, pasted profile links read for you, rows you can export or send to another tool, a spending limit, and a summary of what every username returned.

## When should I use it?

- **OSINT and investigations**: map every public account behind a handle, then follow the linked usernames Maigret finds on those pages.
- **Fraud and trust and safety**: check whether a seller, a scammer's handle or a new sign-up name has a history on marketplaces, forums, crypto, gaming or dating sites.
- **Due diligence and hiring checks**: see a person's public footprint across social, developer and professional sites before a deal.
- **Brand and impersonation monitoring**: find where your brand's handle is registered, and by whom, across 5,000+ sites.
- **Security research**: enumerate the accounts tied to a handle seen in a leak, a phishing kit or a threat report.

## How much does it cost to search a username?

Pay per event: **$0.015 per profile found** ($15 per 1,000). No start fee, no monthly fee, platform usage included. A username found nowhere, a skipped entry and a run that fails on its input cost $0.

| Run (measured 2026-09-29) | Profiles | Price |
|---|---|---|
| The example input: soxoj on the top 500 sites, with its 2 linked usernames | 39 | $0.585 |
| torvalds on the top 500 sites | 116 | $1.74 |
| soxoj on all 5,178 sites, linked names off | 56 | $0.84 |
| A username found nowhere | 0 | $0.00 |

A common username belongs to many people, so it matches many sites: torvalds matched 116 of the top 509, and most of them are not Linus Torvalds. Set Number of sites, pick site types, or set a spending limit on the run for a hard cap: the actor saves the most popular sites' profiles first, stops cleanly at the limit, and every row you paid for is kept. Apify's free plan includes $5 of monthly credit, which covers about 330 profiles.

## How does the price compare with other username search actors?

Price for one username with 30 accounts found, from each actor's list price on the Apify free plan on 2026-09-29 (same inclusion rule as above). Where the price drops on paid Apify plans, the lowest paid-plan price is in brackets.

| Actor | Price for 30 accounts |
|---|---|
| **This actor** | **$0.45** |
| misceres/sherlock | free actor; you pay Apify platform usage |
| tri_angle/social-media-finder | $0.061 |
| ntriqpro/maigret-actor | $0.605 ($0.315) |
| ntriqpro/sherlock-username-osint | $0.60 |
| bovi/social-media-finder | $1.50 ($1.43) |
| automation-lab/username-checker | $0.01 per username ($0.0045) |
| lofomachines/watson | $0.35 ($0.11) |
| datacach/userrecon | $0.030 |
| crawlerbros/social-media-finder | $0.11 ($0.08) |
| ntriqpro/socialscan-osint | $0.605 ($0.315) |
| bovi/maigret-username-osint | $0.57 ($0.54) |
| anshumanatrey/social-analyzer | $0.15 |
| khadinakbar/username-osint-scraper | $0.04 per username |
| crawlerbros/sherlock-scraper | $0.035 |

Where others are cheaper: the Sherlock and presence-only actors (datacach, crawlerbros, khadinakbar, automation-lab, tri_angle) cost a few cents a username, but they check fewer sites and read no profile details. On Apify's Silver plan and above, ntriqpro's Maigret and socialscan actors are cheaper per profile ($0.013 to $0.0104), and so are lofomachines/watson and crawlerbros/social-media-finder on paid plans. This actor is cheaper than the other Maigret actors on the free and Starter plans, has no run fee, and checks all 5,178 sites.

## Which inputs does it take?

Only the usernames are required. Everything else has a working default: leave Number of sites empty and a bare username gets every site.

| Field | Default | What it does |
|---|---|---|
| Usernames to search (`usernames`) | required | One username per line. Accepts @handles, several usernames split by commas, and profile links such as https://github.com/soxoj (the username is read from the link). |
| Number of sites (`maxSites`) | empty: all 5,178 | How many sites to check, most popular first. The form starts at 500, about a minute per username. |
| Site types or countries (`tags`) | every site | Only sites with any of these tags: social, forum, gaming, coding, dating, crypto, finance, music, shopping and 66 more, or countries (India, us, de). Adult and dating sites are always part of a scan without tags. |
| Follow linked names (`recursive`) | on | Also search the usernames found on the profiles, up to 3 per run, billed like the ones you typed. |
| Read profile details (`details`) | on | Read name, bio, location, followers, join date, photo, links and account IDs from each profile page. Needed for linked names. |
| Wait per site (`timeout`) | 30 seconds | How long to wait for each site, from 5 to 120. |
| Retries per site (`retries`) | 0 | Re-check the sites that did not answer, up to 3 times. |

Example input (the form's starting input):

```json
{
  "usernames": ["soxoj"],
  "maxSites": 500
}
```

## What does the output look like?

One row per account. This is the GitHub row of the example run on 2026-09-29, with profileDetails shortened:

```json
{
  "username": "soxoj",
  "siteName": "GitHub",
  "profileUrl": "https://github.com/soxoj",
  "fullName": "Soxoj",
  "bio": "CPO @ Social Links",
  "location": "Amsterdam, Netherlands",
  "followers": 2252,
  "createdAt": "2017-08-14T17:03:07Z",
  "imageUrl": "https://avatars.githubusercontent.com/u/31013580?v=4",
  "linkedUsernames": ["sox0j", "soxoj.bsky.social"],
  "links": ["https://twitter.com/sox0j", "https://bsky.app/profile/soxoj.bsky.social", "https://infosec.exchange/@soxoj"],
  "profileDetails": {"uid": "31013580", "company": "Social Links", "public_repos_count": "112", "twitter_username": "sox0j"},
  "siteUrl": "https://www.github.com/",
  "siteTags": ["business", "coding", "networking"],
  "siteCountries": [],
  "linkedFrom": null,
  "checkedAt": "2026-09-29T10:46:03+00:00"
}
```

| Column | Meaning |
|---|---|
| Username searched (`username`) | The username this row was found for. |
| Site (`siteName`) | Where the account is. |
| Profile link (`profileUrl`) | The account page. |
| Name on profile (`fullName`), Profile bio (`bio`), Location on profile (`location`) | As written on the profile. |
| Follower count (`followers`), Account created (`createdAt`), Profile photo (`imageUrl`) | When the site shows them. |
| Linked handles (`linkedUsernames`), Links on profile (`links`) | Other usernames and links on the page. |
| All details (`profileDetails`) | Every field Maigret read, with its own key names. |
| Site home page (`siteUrl`), Site type (`siteTags`), Site country (`siteCountries`) | About the site. |
| Found through (`linkedFrom`) | For a linked username, the profile it came from, such as "soxoj on GitHub". |
| Time checked (`checkedAt`) | When the run started. |

The two dataset views are Profiles found (who the accounts belong to) and Links and details (linked handles, links, photos and every field). The run summary is the `OUTPUT` record in the key-value store: every username with its status, sites checked, sites that could not be checked, profiles found and saved, and each note about how your input was read. It is not a dataset row, so CSV exports hold profiles only.

## How fast is it?

Measured on 2026-09-29 from a home connection with the default settings (30 s per site, 100 sites at once):

- **500 most popular sites** (509 with Maigret's mirror sites): 43 to 50 seconds per username, in 4 scans.
- **All 5,178 sites**: 12 minutes for soxoj, when 2,412 sites did not answer within the 30-second limit; an earlier run with the same settings took 4.4 minutes. Most of the time goes to the sites that stall until the limit.
- **Linked usernames** are searched one after another, each as long as a typed username.
- Peak memory 211 MB on a 509-site scan and 228 MB on the full scan. The run gets 4 GB by default because Apify gives CPU in proportion to memory, and Maigret reads every page it loads.

The run stops scanning 45 seconds before its time limit and keeps every site already checked. For a long list of usernames on all sites, raise the run timeout (the default is one hour).

## Common questions

### Is this an alternative to Sherlock, WhatsMyName or the other Maigret actors?

Yes. It answers the same question, which accounts use this username, from Maigret's database of 5,178 working sites, which is larger than Sherlock's, and it adds the profile details and linked usernames Maigret reads. Against the other Maigret actors on the Store it has no run fee, reads pasted profile links, and costs less on the free and Starter plans.

### Is it the same Maigret as the open-source tool?

Yes: soxoj/maigret 0.6.6 from PyPI, run as a Python library with its bundled site database (5,897 sites, of which Maigret marks 694 as disabled and this actor skips, and 25 search other kinds of IDs). The Number of sites field is Maigret's `--top-sites`, Site types is `--tags`, and the other fields match `--no-recursion`, `--no-extracting`, `--timeout` and `--retries`.

### Does the person get a notification?

No. Maigret loads public profile pages, the same pages a browser opens. It does not log in, does not start a password reset, and does not contact the person.

### Why does a common username find hundreds of accounts?

Because different people use it. torvalds matched 116 of the top 509 sites, among them a Facebook account named Patrick Torvalds and a Pinterest account named Marco Migozzi. Read the name, bio, photo and location columns to tell the accounts apart, and narrow the search with Number of sites or Site types.

### Why could some sites not be checked?

Some sites block cloud servers, sit behind Cloudflare, limit requests or answer slower than the time limit. In local tests about 120 of the top 509 sites, and 2,412 of all 5,178, could not be checked. The OUTPUT record counts them for every username (`sitesWithErrors`). Raise Wait per site or Retries per site to get more of them.

### Can I search only some kinds of sites or countries?

Yes. Put site types (social, forum, gaming, coding, dating, crypto, finance) or countries (India, us, de) in Site types or countries. A site with any of them is checked.

### Are adult and dating sites included?

Yes. A scan without tags checks every kind of site, adult and dating sites included, since they matter for fraud and dating-safety work. To search only them, use the tags dating or porn.

### What are linked usernames?

Usernames Maigret finds on a profile: a Twitter handle on a GitHub page, a Bluesky handle, a Mastodon account. They are in the Linked handles column. With Follow linked names on, the actor searches up to 3 of them per run and marks each row with Found through, such as "soxoj on GitHub". Their profiles are billed like the ones you typed; turn the option off to search only your usernames.

### How do I search many usernames at once?

Put one username per line, or paste a comma-separated list on one line. Each is searched on its own, one after another, and the OUTPUT record lists every username with its own counts. On the top 500 sites that is about a minute per username; on all 5,178 sites it is several minutes each, so raise the run timeout for a long list.

### How accurate are the results?

Maigret decides from each site's page patterns whether an account exists, and marks the sites whose patterns broke as disabled (this actor skips all 694 of them). For a rare username most matches belong to the same person; for a common one many belong to different people with the same handle. Check the name, bio, photo and profile link before you rely on a match. The details come straight from the profile page.

### Can I try it for free?

Yes. Apify's free plan includes $5 of monthly credit: about 330 profiles, or the example input about 8 times.

### Can I paste a profile link instead of a username?

Yes. A link such as https://github.com/soxoj or https://www.reddit.com/user/spez is read with Maigret's own site patterns, then by its last part for sites Maigret does not know. The OUTPUT record notes each username it read from a link.

### How do I keep the cost down?

Set Number of sites (500 covers the big platforms), pick site types, turn off Follow linked names, and set a maximum cost per run in the run options. A username found nowhere costs nothing.

### Can I call it from code or an AI agent?

Yes. Use the Apify API or the Python and JavaScript clients (the API tab shows ready code), n8n, Make and Zapier, or the Apify MCP server, where agents see every field by its JSON key. Schedule it in Apify to check a username every week.

### What may I use it for?

For lawful investigation of public information: your own accounts, your brand, fraud and safety checks, authorized security research. Follow the laws that apply to you and the terms of the sites you use.

## Limitations

- Usernames only. Maigret's other ID types (Yandex, VK, Google GAIA IDs) are not offered.
- 11 sites in Maigret answer with a search page instead of a profile (StackOverflow and Google Scholar among them). Those matches are left out and not charged; the OUTPUT record counts them (`searchPageMatches`).
- Maigret's checks follow each site's page patterns. A site that changes its pages can give a wrong match until Maigret updates its database.
- Profile details exist only where the site shows them and Maigret has an extractor for it: 28% to 41% of the accounts found in the tests above.
- Up to 3 linked usernames per run, searched after the ones you typed.
- No proxy option in version 1.0: sites that block cloud servers are counted as could-not-check.
- A full scan takes minutes per username, so a long list on all sites needs a longer run timeout.

---

## About the maintainer (priority response within 1-2 hours)

Built and maintained by **Anshuman Atrey** ([@AnshumanAtrey](https://github.com/AnshumanAtrey)).

- Purple-team security researcher, 5x hackathon winner
- Co-founder of **Walrus Securitas** (AI cybersecurity SaaS) and **The Drone Syndicate** (autonomous defence drones)
- Author of the OSINT and data actor portfolio on Apify Store: 19 shipped actors covering email, phone, username, IP and domain, network, secret, social, LinkedIn, domain history, Telegram, Google Trends, Meta ads and Indian fintech data

### Custom feature requests shipped within 1-2 hours (priority)

If you need a field, a filter or an output format this actor does not have, the maintainer ships it directly into this actor, typically within 1-2 hours for priority requests during active hours and within 24 hours overnight. This is direct one-to-one service from the maintainer, not a contractor queue.

**Fastest contact channels (ranked by response speed):**
1. **LinkedIn DM** -> [linkedin.com/in/anshumanatrey](https://linkedin.com/in/anshumanatrey), typically under 1 hour during active hours
2. **GitHub issue** on this actor's repo
3. **Apify Console** DM to `@anshumanatrey`
4. **Email** via [atrey.dev](https://atrey.dev)

---

## Sibling actors by the same maintainer

| Actor | Use case |
|---|---|
| [social-analyzer](https://apify.com/anshumanatrey/social-analyzer) | Username -> profiles across 900+ social sites with confidence scoring |
| [instagram-profile-intel-no-login](https://apify.com/anshumanatrey/instagram-profile-intel-no-login) | Instagram username -> bio emails + phones + 25 fields (no login) |
| [holehe-email-osint](https://apify.com/anshumanatrey/holehe-email-osint) | Email -> registered accounts across 120+ platforms |
| [linkedin-harvester](https://apify.com/anshumanatrey/linkedin-harvester) | Email -> best-match public LinkedIn profile URL + confidence score |
| [phoneinfoga-phone-osint](https://apify.com/anshumanatrey/phoneinfoga-phone-osint) | International phone -> country, footprint URLs, OSINT trail |
| [upi-id-osint](https://apify.com/anshumanatrey/upi-id-osint) | Indian phone or VPA -> active UPI IDs + bank-registered name from NPCI |
| [telegram-channel-scraper](https://apify.com/anshumanatrey/telegram-channel-scraper) | Public Telegram channel -> posts, media links, inline buttons, reactions (no login) |
| [facebook-ads-library-api](https://apify.com/anshumanatrey/facebook-ads-library-api) | Facebook/Meta Ad Library -> ads, landing pages, creatives, advertiser leads, scam checks (no login) |
| [google-trends-api-scraper](https://apify.com/anshumanatrey/google-trends-api-scraper) | Google Trends interest over time, regions, related queries and Trending Now, no login |
| [domain-history-contact-osint](https://apify.com/anshumanatrey/domain-history-contact-osint) | Dead or expired domain -> previous owner's emails, phones, people + orgs, WHOIS + Wayback history, source URL on every row |
| [theharvester-osint](https://apify.com/anshumanatrey/theharvester-osint) | Domain -> emails + subdomains + IPs from 54+ public sources |
| [netintel](https://apify.com/anshumanatrey/netintel) | IP or domain -> unified WHOIS + DNS + GeoIP + ASN + ports |
| [bug-bounty-finder](https://apify.com/anshumanatrey/bug-bounty-finder) | Domain -> active HackerOne + Bugcrowd + security.txt programs |
| [nmap-scanner](https://apify.com/anshumanatrey/nmap-scanner) | Network -> port + service + version detection, NSE scripts |
| [gitleaks-github-secret-scanner](https://apify.com/anshumanatrey/gitleaks-github-secret-scanner) | GitHub -> leaked API keys across 30+ services |
| [betterleaks-cloud](https://apify.com/anshumanatrey/betterleaks-cloud) | GitHub + S3 -> leaked secrets with live vendor-API validation |
| [yt-dlp-video-link-extractor](https://apify.com/anshumanatrey/yt-dlp-video-link-extractor) | Any video URL -> direct stream and download links + metadata, 1000+ sites |
| [zomato-restaurant-scraper](https://apify.com/anshumanatrey/zomato-restaurant-scraper) | Zomato city page -> restaurants with phone, address, cuisines, rating and cost for two |

---

## Documentation

- Apify Store: https://apify.com/anshumanatrey/maigret-username-search
- GitHub repo: https://github.com/AnshumanAtrey/maigret-username-search
- Maigret (upstream, MIT): https://github.com/soxoj/maigret
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Issues / feature requests: open an issue on the GitHub repo or DM LinkedIn for the fastest response
- License: MIT

## Last updated

2026-09-29 (version 1.0)
