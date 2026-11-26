import unittest

from clipper import twitch_clips as tc


def fake(edges):
    calls = []

    def fetch(q):
        calls.append(q)
        return {"data": {"game": {"id": "1", "name": "G", "streams": {"edges": edges}}}}
    fetch.calls = calls
    return fetch


def edge(login, viewers, title):
    return {"node": {"title": title, "viewersCount": viewers, "broadcaster": {"login": login}}}


class LiveStreamsTest(unittest.TestCase):
    def test_sorted_by_viewers_with_urls(self):
        f = fake([edge("a", 10, "x"), edge("b", 500, "y")])
        out = tc.live_streams("G", 5, fetch=f)
        self.assertEqual([c["creator"] for c in out], ["b", "a"])
        self.assertEqual(out[0]["url"], "https://www.twitch.tv/b")

    def test_single_request_and_limit_capped(self):
        f = fake([edge("a", 1, "x")])
        tc.live_streams("G", 9999, fetch=f)
        self.assertEqual(len(f.calls), 1)
        self.assertIn("first:%d" % tc.MAX_LIVE, f.calls[0])
        self.assertIn("first:1,", tc.build_live_query("G", 0))

    def test_flagged_title_marked(self):
        out = tc.live_streams("G", 5, fetch=fake([edge("a", 1, "sexy stream")]))
        self.assertTrue(out[0]["flagged"])

    def test_unknown_category_raises(self):
        with self.assertRaises(ValueError):
            tc.live_streams("G", 5, fetch=lambda q: {"data": {"game": None}})

    def test_missing_streams_is_empty(self):
        self.assertEqual(tc.live_streams("G", 5, fetch=lambda q: {"data": {"game": {"streams": None}}}), [])


if __name__ == "__main__":
    unittest.main()
