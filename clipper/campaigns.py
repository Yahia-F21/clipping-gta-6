"""GTA 6 clipping campaign presets and a per-pick compliance check.

Provenance: worker-compiled briefs (Nov 2026). These presets were NOT verified against the
campaigns' own documents; re-check the campaign's current brief before posting. Campaigns whose
rules live in external docs nobody has read yet are UNKNOWN, never guessed.

Sounds: official platform sounds cannot be bundled into a render. Every preset records the sound
name and start offset as a POSTING-TIME step (added on the platform when posting); nothing here
mixes third-party audio into a render.

Logos: logo campaigns need assets the user supplies. This repo never fetches or fabricates brand
logos, so logo campaigns stay blocked until an asset is supplied.

Vavada (casino) and Fanvue (AI-girlfriend promo) presets are intentionally absent until the user
approves building them.
"""

# Rules every listed campaign shares. None of these are auto-checkable from a pick; they ride
# along as verify items on every compliance report.
COMMON_VERIFY = [
    "GTA 6 gameplay only - no AI, modded, fake or leaked footage",
    "no other creators' watermarks on the footage",
    "organic posting only, no paid boosting",
    "on-screen text in English",
    "no NSFW, gore, hate or politics",
    "reposting permission for the creator's footage is unverified unless the campaign supplies it",
    "post stays up for the campaign's required window (30-60 days on some)",
]

CAMPAIGNS = {
    "whethan": {
        "lengths": [15],
        "hook_seconds": 2,
        "sound": {"name": "Bass Down Low", "start": "0:01", "where": "instagram"},
        "original_audio": "keep",
        "text_lines_max": 1,
        "tags": ["@whethan"],
        "hashtags": ["#GTAVI", "#GTA", "#BassDownLow"],
        "lanes": ["chases", "leonida-nights", "chaos-fails", "graphics"],
        "bans": ["do not say the single is out now", "no reuse of the same clip across accounts"],
    },
    "gameover": {
        "lengths": [15, 30],
        "loop": True,
        "hook_seconds": 2,
        "sound": {"name": "Game Over", "start": None, "where": "any"},
        "original_audio": "game SFX under 15% under the song",
        "tags": ["@DJDiamondz (TikTok, IG)", "@djdiamondzofficial (YouTube)"],
        "hashtags": ["#GameOver", "#Diamondz", "#HouseMusic"],
        "lanes": ["dramatic stunts", "WASTED moments"],
        "prerequisites": ["drafts need pre-approval before posting"],
    },
    "rexxlife": {
        "min_seconds": 10,
        "max_seconds": 60,
        "hook_seconds": 2,
        "sound": {"name": "Handful of Diamond Rings", "start": "0:09 or 0:26", "where": "any"},
        "original_audio": "keep, but mute any in-game radio",
        "no_voiceover": True,
        "no_cutscenes": True,
        "min_resolution": 1080,
        "caption": "Song: Handful of Diamond Rings by @rexxliferaj",
        "lanes": ["action or absurd payoff", "action in the first 2 seconds"],
        "prerequisites": ["post from a public account"],
    },
    "8lanco": {
        "min_seconds": 7,
        "hook_seconds": 2,
        "formats": ["GTA6 radio edit", "Toxic Relationship", "False Hero"],
        "sound": {"name": "Every Little Thing (official sound)", "start": None, "where": "any"},
        "original_audio": "mute - official sound at 100%",
        "caption": "EVERY LITTLE THING BY 8LANCO. OUT NOW. #8lanco #everylittlething",
        "tags": ["@8lanco (IG)", "@ban8lanco (TikTok)"],
        "notes": ["write your own hook", "analytics proof required once the post passes ~2K views"],
    },
    "denial": {
        "min_seconds": 15,
        "max_seconds": 60,
        "hook_seconds": 2,
        "sound": {"name": "HOSTILE", "start": None, "where": "any"},
        "original_audio": "keep",
        "caption": "song is HOSTILE - DENIAL #hostile #techno",
        "bans": ["no reuse of the same clip on multiple accounts"],
        "notes": ["English text/captions required"],
    },
    "naya-yeira": {
        "min_seconds": 15,
        "hook_seconds": 2,
        "sound": {"name": "official sound from the EP 'Almost There'", "start": None, "where": "any"},
        "original_audio": "keep",
        "caption": "[Song title] - Naya Yeira",
        "tags": ["@nayayeiraofficial (TikTok)", "@nayayeira (IG)"],
        "notes": ["the drop lands around 3s in - time the edit to it"],
    },
    "things-i-couldve-said": {
        "min_seconds": 20,
        "hook_seconds": 2,
        "sound": {"name": "Things I Could've Said", "start": "2:34", "where": "any"},
        "original_audio": "keep",
        "notes": ["audio must start exactly at 2:34; brief says 20-30s minimum, treat 20s as the floor"],
    },
    "310babii": {
        "hook_seconds": 2,
        "sound": {"name": "Soak City (Do It)", "start": None, "where": "any"},
        "original_audio": "keep",
        "lanes": ["swerving/drifting", "NPC memes"],
    },
    "gta-clipper-logo": {
        "hook_seconds": 2,
        "logo": {"position": "bottom-right, whole clip, uncovered by captions or facecam",
                 "asset": "user-supplied only - none supplied yet"},
        "hashtags": ["#gta6", "#gtaclipper", "#clipping"],
        "description_link": "gtaclipper.com",
        "blocked": ["requires joining the campaign Discord (not done)", "needs a user-supplied logo asset"],
    },
    "clipup": {
        "hook_seconds": 2,
        "logo": {"position": "on screen", "asset": "user-supplied only - none supplied yet"},
        "hashtags": ["#clipup"],
        "monetize": "Instagram only",
        "blocked": ["requires a Discord link in the bio (not done)", "needs a user-supplied logo asset"],
    },
}

# Rules sit in external docs nobody has read. Listing them so nobody guesses.
UNKNOWN_CAMPAIGNS = ["Foltyn", "Tokyo Girl", "Boeshi", "Donato", "DJ Tunez", "BrettLiftsXP",
                     "Distributed", "Lauren Hamden", "FR Bichou", "Bobby VanRiper"]

# Deliberately not built until the user approves: Vavada (casino promo), Fanvue (AI-girlfriend promo).
SKIPPED_CAMPAIGNS = {"vavada": "casino promo - held for the user's approval",
                     "fanvue": "AI-girlfriend promo - held for the user's approval"}


def pick_seconds(pick):
    """Render length of a pick: the sum of its segments, or end - start."""
    if pick.get("segments"):
        return round(sum(float(s["end"]) - float(s["start"]) for s in pick["segments"]), 2)
    return round(float(pick["end"]) - float(pick["start"]), 2)


def _length_fail(spec, seconds):
    lo, hi = spec.get("min_seconds"), spec.get("max_seconds")
    if spec.get("lengths") and int(round(seconds)) not in spec["lengths"]:
        loop = " (looping cut)" if spec.get("loop") else ""
        return f"length {seconds:g}s is not one of {spec['lengths']}{loop}"
    if lo is not None and seconds < lo:
        return f"length {seconds:g}s is under the {lo:g}s minimum"
    if hi is not None and seconds > hi:
        return f"length {seconds:g}s is over the {hi:g}s maximum"
    return None


def check(pick, key, seconds=None):
    """Compliance of one pick with a campaign preset. Returns {"fails", "verify", "posting"}:
    auto-checkable violations, judgment calls a human must confirm, and the posting-time steps
    (sound, caption, tags) that never go into the render itself."""
    spec = CAMPAIGNS[key]
    seconds = pick_seconds(pick) if seconds is None else float(seconds)
    verify = list(COMMON_VERIFY)
    fail_msgs = []
    if spec.get("blocked"):
        fail_msgs += [f"blocked: {b}" for b in spec["blocked"]]
    msg = _length_fail(spec, seconds)
    if msg:
        fail_msgs.append(msg)
    if spec.get("hook_seconds") and not (pick.get("hook") or pick.get("hooks")):
        fail_msgs.append(f"no hook - the campaign wants on-screen text within {spec['hook_seconds']}s")
    if spec.get("no_voiceover") and pick.get("voiceover"):
        fail_msgs.append("voiceover present - the campaign bans voiceover")
    if spec.get("text_lines_max") == 1:
        fail_msgs.append("one short text line max - the pipeline always burns captions from speech, "
                         "so a compliant render needs a captions-off path (not implemented)")
    if pick.get("music") and spec.get("sound"):
        fail_msgs.append("pick mixes in music - the official sound is added on the platform at posting "
                         "time, never mixed into the render")
    if spec.get("no_cutscenes"):
        verify.append("no cutscenes - confirm every segment is gameplay")
    if spec.get("min_resolution"):
        verify.append(f"source must be at least {spec['min_resolution']}p")
    if spec.get("original_audio", "").startswith("mute"):
        verify.append("original audio must be muted - the official sound carries the whole clip")
    if "%" in spec.get("original_audio", ""):
        verify.append(f"keep {spec['original_audio']}")
    if "radio" in spec.get("original_audio", ""):
        verify.append("confirm no in-game radio is audible; mute and re-render if it is")
    for lane in spec.get("lanes", []):
        verify.append(f"lane fit: {lane}")
    for ban in spec.get("bans", []):
        verify.append(f"campaign ban: {ban}")
    posting = {
        "sound": (f"add the platform sound \"{spec['sound']['name']}\""
                  + (f" starting at {spec['sound']['start']}" if spec["sound"].get("start") else "")
                  + " when posting - do not mix it into the render") if spec.get("sound") else None,
        "caption": spec.get("caption"),
        "tags": spec.get("tags"),
        "hashtags": spec.get("hashtags"),
        "description_link": spec.get("description_link"),
        "prerequisites": spec.get("prerequisites"),
    }
    return {"campaign": key, "seconds": seconds, "fails": fail_msgs, "verify": verify,
            "posting": {k: v for k, v in posting.items() if v}}


def report(pick, key, seconds=None):
    """The check as printable text."""
    r = check(pick, key, seconds)
    out = [f"campaign: {r['campaign']} ({r['seconds']:g}s pick)"]
    out += [f"  FAIL: {m}" for m in r["fails"]] or ["  no automatic failures"]
    out += [f"  verify: {m}" for m in r["verify"]]
    out += [f"  posting: {k}: {v}" for k, v in r["posting"].items()]
    return "\n".join(out)
