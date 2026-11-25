"""Offline test for clipper.twitch_clips (no network). Run: python tests/test_twitch_clips.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from clipper import twitch_clips as t


def fake(_query):
    def node(slug, title, v):
        return {"node": {"slug": slug, "title": title, "viewCount": v, "durationSeconds": 20, "createdAt": "x",
                         "videoOffsetSeconds": 5, "broadcaster": {"login": "abc"}, "game": {"name": "G"}, "video": {"id": "9"}}}
    return {"data": {"game": {"id": "1", "name": "G", "clips": {"edges": [node("a", "funny fail", 10), node("b", "nude scene", 99)]}}}}


def main():
    q = t.build_query('Grand "Theft" Auto VI', "LAST_WEEK", 5)
    assert 'name:"Grand \\"Theft\\" Auto VI"' in q and "LAST_WEEK" in q
    try:
        t.build_query("G", "BAD", 1)
        raise SystemExit("expected ValueError")
    except ValueError:
        pass
    r = t.top_clips("G", fetch=fake)
    assert [c["slug"] for c in r] == ["b", "a"]  # sorted by views
    assert r[0]["flagged"] and not r[1]["flagged"]
    assert r[1]["url"] == "https://www.twitch.tv/abc/clip/a"
    try:
        t.top_clips("G", fetch=lambda q: {"data": {"game": None}})
        raise SystemExit("expected ValueError")
    except ValueError:
        pass
    print("ok")


if __name__ == "__main__":
    main()
