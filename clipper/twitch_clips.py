"""Discover a game's most-clipped Twitch moments (a viewer-engagement lead, not a guarantee).

UNOFFICIAL: this calls Twitch's public web GraphQL endpoint with the public web client id. It is not a documented API,
may change or break without notice, and may be rate limited. Use the official Helix API (needs an app token) for anything
important. Standard library only. Respect creators' rights: a popular clip is not permission to repost it.

The title filter is a crude keyword screen. It does NOT detect adult or sensitive content in the footage itself.
Always review the clip visually before using it.

Usage:
  python -m clipper.twitch_clips "Grand Theft Auto VI" --period LAST_WEEK --limit 40 [--include-flagged]
  python -m clipper.twitch_clips "Grand Theft Auto VI" --live --limit 25     # who is live in the category right now

--live makes ONE request (no paging, limit capped at 100) and lists the top live streams by viewers. The category is the
streamer's own tag, not proof of gameplay: check the title and the footage. It is a visible lower bound, not a total.
"""
import argparse
import json
import re
import urllib.request

GQL_URL = "https://gql.twitch.tv/gql"
PUBLIC_WEB_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
PERIODS = ("LAST_DAY", "LAST_WEEK", "LAST_MONTH", "ALL_TIME")
FLAG_RE = re.compile(r"\b(nude|nudes|naked|sex|sexy|boob\w*|cheeks?|gyat+|ass|thicc|porn|nsfw|18\+|horny)\b", re.I)


def gql(query):
    req = urllib.request.Request(GQL_URL, data=json.dumps([{"query": query}]).encode(),
                                 headers={"Client-ID": PUBLIC_WEB_CLIENT_ID})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)[0]


def build_query(game, period, limit):
    if period not in PERIODS:
        raise ValueError(f"period must be one of {PERIODS}")
    name = json.dumps(game)
    return ("query{game(name:%s){id name clips(first:%d,criteria:{period:%s,sort:VIEWS_DESC}){edges{node{slug title "
            "viewCount durationSeconds createdAt videoOffsetSeconds broadcaster{login} game{name} video{id}}}}}}"
            % (name, int(limit), period))


def top_clips(game, period="LAST_WEEK", limit=40, fetch=gql):
    """Return [{slug,url,title,views,seconds,creator,vod,offset,game,flagged}] sorted by views."""
    data = fetch(build_query(game, period, limit))
    g = (data.get("data") or {}).get("game")
    if not g:
        raise ValueError(f"no Twitch category named {game!r}")
    out = []
    for e in g["clips"]["edges"]:
        n = e["node"]
        creator = (n.get("broadcaster") or {}).get("login", "")
        out.append({
            "slug": n["slug"], "url": f"https://www.twitch.tv/{creator}/clip/{n['slug']}", "title": n["title"],
            "views": n["viewCount"], "seconds": n["durationSeconds"], "creator": creator,
            "vod": (n.get("video") or {}).get("id"), "offset": n.get("videoOffsetSeconds"),
            "game": (n.get("game") or {}).get("name"), "flagged": bool(FLAG_RE.search(n["title"])),
        })
    return sorted(out, key=lambda c: -c["views"])


MAX_LIVE = 100  # one page, never paged: a single request per call


def build_live_query(game, limit):
    return ("query{game(name:%s){id name streams(first:%d,options:{sort:VIEWER_COUNT}){edges{node{title viewersCount "
            "broadcaster{login}}}}}}" % (json.dumps(game), max(1, min(int(limit), MAX_LIVE))))


def live_streams(game, limit=25, fetch=gql):
    """Return [{creator,url,title,viewers,flagged}] for the category's live streams, most viewers first.

    One request only. The result is the visible top of the list, not a total, and the category tag is the streamer's
    label: some streams in it are talk shows or other games."""
    data = fetch(build_live_query(game, limit))
    g = (data.get("data") or {}).get("game")
    if not g:
        raise ValueError(f"no Twitch category named {game!r}")
    out = []
    for e in (g.get("streams") or {}).get("edges") or []:
        n = e["node"]
        creator = (n.get("broadcaster") or {}).get("login", "")
        out.append({"creator": creator, "url": f"https://www.twitch.tv/{creator}", "title": n.get("title") or "",
                    "viewers": n.get("viewersCount") or 0, "flagged": bool(FLAG_RE.search(n.get("title") or ""))})
    return sorted(out, key=lambda c: -c["viewers"])


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("game")
    p.add_argument("--period", default="LAST_WEEK", choices=PERIODS)
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--live", action="store_true", help="list who is live in the category now (one request)")
    p.add_argument("--include-flagged", action="store_true", help="also list titles the keyword screen flagged")
    a = p.parse_args()
    if a.live:
        for c in live_streams(a.game, a.limit):
            if c["flagged"] and not a.include_flagged:
                continue
            print(f"{c['viewers']:>8} {c['creator']:<20} {c['title'][:60]} {c['url']}")
        return
    for c in top_clips(a.game, a.period, a.limit):
        if c["flagged"] and not a.include_flagged:
            continue
        print(f"{c['views']:>8} {c['seconds']:>3}s {c['creator']:<16} {c['title'][:60]} {c['url']}")


if __name__ == "__main__":
    main()
