# Platform support: what is built and what was tested

This page records what the repo already does for Twitch, Kick and YouTube, and what was actually tried on 2026-11-26 in one sandbox. It adds no new platform support. Results come from a few small, non-recurring checks, so treat them as a snapshot, not a guarantee.

| Platform | Built in the repo | Tested end to end | Known limit |
| --- | --- | --- | --- |
| Twitch | `live add twitch:NAME`, live probe, gapless chunk recording, `analyze`, render. Twitch clip discovery in `clipper/twitch_clips.py`. | Yes. One streamer was recorded for about 5 minutes, one 4-minute chunk was analyzed and rendered through the normal pipeline. | The category and clip helpers use Twitch's unofficial web GraphQL endpoint. It can change or limit requests. |
| Kick | `live add kick:NAME` and the same chunk recorder (`clipper/live.py`). No Kick clip or live-discovery code. | Partly. yt-dlp resolved one live Kick channel's metadata (live, 1080p, title). Recording and chunking on Kick were not tested. | Kick's web API answered HTTP 429 after many repeated calls. Do not poll it. Its category list endpoint did not look filtered to the category in one test, so no channel count is trusted. |
| YouTube | `live add youtube:@NAME`, clip discovery by yt-dlp search and channel watch (`clipper/sources.py`), most-replayed data for VODs. | Search discovery worked (a live-filtered search listed live streams with viewer counts). Resolving or downloading a live stream failed with "Sign in to confirm you're not a bot". | Live recording on YouTube needs cookies or another way past that check. This repo does not assume either. |

## Notes

- A category label or a search hit says what the creator tagged, not what is on screen. Review frames before you treat a stream as gameplay of a given game.
- Counts of live streams are per platform and are lower bounds unless the listing was read to its end. Do not add them across platforms: one creator can stream to several sites.
- The scoring and hook checks are the same on every platform. Failed checks and a missing payoff note still block a normal export (see `docs/payoff-gate.md`).
- Reposting a creator's footage can need their permission on each platform. Credit does not replace it.
- yt-dlp behavior changes often. Re-test a platform before you rely on it.
