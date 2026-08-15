"""
Gen 5 (BW/B2W2) save file parser.

Parses trainer data, party, badges, money, location, and provides story guidance.
"""

import struct
from pathlib import Path

from .encryption import decrypt_pokemon_data
from .offsets import BLOCKS, TRAINER, POSITION, MISC, PARTY, GAME_VERSIONS, LANGUAGES
from .story import BADGE_NAMES, get_story_guidance
from .event_flags import parse_event_flags, format_event_report
from ..data.species import SPECIES
from ..data.natures import NATURES


def parse(filepath: str) -> dict:
    """Parse a Gen 5 .sav file and return structured game state."""
    data = Path(filepath).read_bytes()
    if len(data) != 524288:
        return {"error": f"Invalid save size: {len(data)} (expected 524288)"}

    result = {
        "generation": 5,
        "game": _get_game_name(data),
        "trainer": _parse_trainer(data),
        "playtime": _parse_playtime(data),
        "money": _parse_money(data),
        "badges": _parse_badges(data),
        "location": _parse_location(data),
        "party": _parse_party(data),
    }

    # Event flags analysis
    badge_count = result["badges"]["count"]
    ef = parse_event_flags(data)

    # Story guidance (badge-based with event flag refinement)
    story = get_story_guidance(badge_count)

    # Refine story guidance based on event flags
    # Badge count is primary (from Misc block byte)
    # Gym leader flags are secondary (some may be unreliable for Striaton)
    # Legendary flags indicate Dragonspiral progress
    legendary_battled = ef["legendary_status"].get("LEGEND1_BATTLE (battled legendary 1)", False)
    legendary_caught = any(ef["legendary_status"].values())

    if legendary_battled and not legendary_caught and badge_count == 6:
        story = {
            "location": "Mistralton City (post-Dragonspiral)",
            "next": "Route 7 → Icirrus City for 7th badge (Brycen, Ice). Then Opelucid for 8th.",
            "tip": "You've been to Dragonspiral. Brycen = Ice → Fire/Fighting/Steel. Grind to Lv37+.",
            "level_range": "35-48",
        }

    result["story"] = {
        "badges": badge_count,
        "progress_pct": round(badge_count / 8 * 100),
        "where_you_are": story["location"],
        "what_next": story["next"],
        "tip": story["tip"],
        "recommended_level": story["level_range"],
        "legendary_battled": legendary_battled,
        "legendary_caught": legendary_caught,
    }
    result["event_flags"] = ef
    result["_raw_data"] = data  # for event flag formatting

    return result


def _get_game_name(data: bytes) -> str:
    ver = data[BLOCKS["trainer_data"] + TRAINER["game_ver"]]
    name = GAME_VERSIONS.get(ver, f"Unknown ({ver})")
    return f"Pokémon {name}"


def _parse_trainer(data: bytes) -> dict:
    base = BLOCKS["trainer_data"]
    try:
        name = data[base + TRAINER["name"] : base + TRAINER["name"] + 16]
        name = name.decode("utf-16-le").rstrip("\x00").rstrip("\ufffd").rstrip("\uffff")
        name = name.replace("\x00", "").replace("\ufffd", "").replace("\uffff", "").strip()
    except (UnicodeDecodeError, ValueError):
        name = "???"

    tid = struct.unpack_from("<H", data, base + TRAINER["tid"])[0]
    sid = struct.unpack_from("<H", data, base + TRAINER["sid"])[0]
    lang = data[base + TRAINER["language"]]
    gender = "Male" if data[base + TRAINER["gender"]] == 0 else "Female"

    return {
        "name": name,
        "tid": tid,
        "sid": sid,
        "language": LANGUAGES.get(lang, f"Unknown ({lang})"),
        "gender": gender,
    }


def _parse_playtime(data: bytes) -> str:
    base = BLOCKS["trainer_data"]
    hours = struct.unpack_from("<H", data, base + TRAINER["play_hours"])[0]
    mins = data[base + TRAINER["play_mins"]]
    secs = data[base + TRAINER["play_secs"]]
    return f"{hours}h {mins:02d}m {secs:02d}s"


def _parse_money(data: bytes) -> int:
    return struct.unpack_from("<I", data, BLOCKS["misc"] + MISC["money"])[0]


def _parse_badges(data: bytes) -> dict:
    badge_byte = data[BLOCKS["misc"] + MISC["badges"]]
    count = bin(badge_byte).count("1")
    badges = []
    for i, (name, city, leader, types) in enumerate(BADGE_NAMES):
        badges.append({
            "name": name,
            "city": city,
            "leader": leader,
            "type": types,
            "earned": bool(badge_byte & (1 << i)),
        })
    return {"count": count, "bitmask": badge_byte, "badges": badges}


def _parse_location(data: bytes) -> dict:
    base = BLOCKS["player_pos"]
    map_id = struct.unpack_from("<i", data, base + POSITION["map_id"])[0]
    x = struct.unpack_from("<H", data, base + POSITION["player_x"])[0]
    y = struct.unpack_from("<H", data, base + POSITION["player_y"])[0]
    return {"map_id": map_id, "x": x, "y": y}


def _parse_party(data: bytes) -> list:
    base = BLOCKS["party"]
    count = struct.unpack_from("<I", data, base + PARTY["count_offset"])[0]
    start = base + PARTY["data_offset"]

    party = []
    for i in range(min(count, 6)):
        offset = start + i * PARTY["pk5_size"]
        raw = data[offset : offset + PARTY["pk5_size"]]
        pkm = decrypt_pokemon_data(raw)
        if pkm:
            pkm["species"] = SPECIES.get(pkm["species_id"], f"#{pkm['species_id']}")
            pkm["nature_name"] = NATURES.get(pkm["nature"], f"#{pkm['nature']}")
            party.append(pkm)

    return party


def format_text(result: dict) -> str:
    """Format parsed result as human-readable text."""
    lines = []
    t = result["trainer"]
    s = result["story"]

    lines.append(f"## {result['game']}")
    lines.append(f"**Trainer:** {t['name']} ({t['gender']}) | TID: {t['tid']} | {t['language']}")
    lines.append(f"**Playtime:** {result['playtime']} | **Money:** ¥{result['money']:,}")
    lines.append(f"**Badges:** {s['badges']}/8 ({s['progress_pct']}% of story)")
    lines.append("")

    for b in result["badges"]["badges"]:
        mark = "✓" if b["earned"] else "✗"
        lines.append(f"  {mark} {b['name']} — {b['leader']} ({b['type']})")
    lines.append("")

    party = result["party"]
    if party:
        avg_lv = sum(p.get("level", 0) for p in party) // len(party)
        lines.append(f"### Party ({len(party)} Pokémon, avg Lv{avg_lv})")
        for i, p in enumerate(party, 1):
            nick = f' "{p["nickname"]}"' if p.get("nickname") else ""
            lv = f"Lv{p['level']}" if "level" in p else "?"
            lines.append(f"  {i}. {p['species']} {lv}{nick} ({p['nature_name']})")
        lines.append("")

    lines.append(f"### Where you are: {s['where_you_are']}")
    lines.append(f"**Next:** {s['what_next']}")
    lines.append(f"**Tip:** {s['tip']}")
    lines.append(f"**Recommended level:** {s['recommended_level']}")
    if s.get("legendary_battled"):
        lines.append(f"**Legendary:** Battled (not caught)")
    if s.get("legendary_caught"):
        lines.append(f"**Legendary:** Caught")

    # Event flags summary
    ef = result.get("event_flags", {})
    if ef:
        lines.append("")
        lines.append(format_event_report(result.get("_raw_data", b"")))

    return "\n".join(lines)
