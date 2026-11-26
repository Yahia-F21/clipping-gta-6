# Campaign presets and the compliance check

`clipper/campaigns.py` holds one preset per GTA 6 clipping campaign and a check that tests a pick
against a preset before anything is rendered or posted.

Provenance and limits, read this first:

- The presets are worker-compiled from campaign briefs (Nov 2026) and were **not verified against
  the campaigns' own documents**. Re-check the campaign's current brief before posting.
- Campaigns whose rules live in external docs nobody has read are listed as `UNKNOWN_CAMPAIGNS`
  (Foltyn, Tokyo Girl, Boeshi, Donato, DJ Tunez, BrettLiftsXP, Distributed, Lauren Hamden,
  FR Bichou, Bobby VanRiper). Their rules are not guessed.
- Vavada (casino promo) and Fanvue (AI-girlfriend promo) presets are **not built**; they wait on
  the user's approval (`SKIPPED_CAMPAIGNS`).
- Official platform sounds cannot be bundled into a render. Presets record the sound name and
  start offset as a **posting-time step**: add the sound on the platform when posting. Nothing in
  the pipeline mixes third-party audio in, and the check fails a pick that mixes music into a
  render meant for an official-sound campaign.
- Logo campaigns (GTA Clipper Logo, ClipUp) need logo assets **the user supplies**; brand logos are
  never fetched or fabricated. Both are also blocked on Discord steps that are not done, so their
  reports always show `blocked` failures for now.

## Usage

```
python3 -m clipper campaigns list                       # every preset, plus unknown and skipped lists
python3 -m clipper campaigns check rexxlife --picks picks.json
python3 -m clipper campaigns check whethan --picks picks.json --seconds 15
```

The report has three parts:

- `fails`: automatic violations (length, missing hook, banned voiceover, mixed-in music, blocked
  campaign, Whethan's one-text-line rule). Any fail exits 1.
- `verify`: judgment calls a human confirms by looking at the clip (GTA 6 gameplay only, no AI or
  modded footage, no watermarks, cutscenes, radio, lane fit, rights). These never auto-pass.
- `posting`: what happens at posting time and never in the render: the platform sound and its
  start offset, the required caption, tags, hashtags, prerequisites (public account, draft
  pre-approval, analytics proof around 2K views where a campaign asks for it).

Known gap: Whethan allows one short text line, but the render pipeline always burns captions from
speech, so no pick can pass the Whethan check until a captions-off render path exists.

Tests: `python -m unittest tests.test_campaigns` (15 tests, pure logic, no ffmpeg).
