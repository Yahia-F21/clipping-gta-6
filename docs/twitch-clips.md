# Twitch category clip discovery (unofficial)

`clipper/twitch_clips.py` lists a game's most-clipped Twitch moments, a lead for "what viewers chose to clip".

    python -m clipper.twitch_clips "Grand Theft Auto VI" --period LAST_WEEK --limit 40

## Limits (read these)
- **Unofficial endpoint.** It uses Twitch's public web GraphQL endpoint and the public web client id. It is not a
  documented API, can change or stop working at any time, and may be rate limited. For anything important use the
  official Helix API with your own app credentials.
- **Game identity comes from the creator's Twitch category tag.** That tag can be wrong. Confirm the game in the footage.
- **The title filter is a keyword screen only.** In a real test on a GTA VI category, many of the most-clipped moments
  were adult scenes, and the screen does not see the video. Always review clips visually before using them.
- A popular clip says nothing about reposting rights, and does not predict views on another platform.
- Clips sorted by views favor the biggest streamers and the newest content.

Test (offline, no network): `python tests/test_twitch_clips.py`
