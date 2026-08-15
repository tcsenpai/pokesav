"""
Gen 5 (BW/B2W2) save file parser.

Parses trainer data, party, badges, money, location, and provides story guidance.
"""

import struct
from pathlib import Path

from .encryption import decrypt_pokemon_data
from .offsets import BLOCKS, TRAINER, POSITION, MISC, PARTY, GAME_VERSIONS, LANGUAGES
from .story import BADGE_NAMES, get_story_guidance
from .event_flags import parse_event_flags, format_event_report, get_detailed_status
from ..data.species import SPECIES
from ..data.natures import NATURES


def parse(filepath: str) -> dict:
    """Parse a Gen 5 .sav file and return structured game state.

    Args:
        filepath: Path to the .sav file (512KB raw DeSmuME format)

    Returns:
        Dict with trainer, party, badges, money, location, story guidance.
    """
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
    event_result = parse_event_flags(data)
    detailed = get_detailed_status(data, badge_count)

    # Story guidance (uses event flags for precision)
    story = get_story_guidance(badge_count)

    # Override story guidance if event flags tell us more
    if detailed["elite4_done"]:
        story = {
            "location": "Post-game — Pokémon League cleared",
            "next": "Explore post-game areas: Undella Town, Giant Chasm, P2 Laboratory. Catch legendaries.",
            "tip": "The real game begins now. Battle Cynthia in Undella Town.",
            "level_range": "60-80",
        }
    elif detailed["dragonspiral_done"] and badge_count == 6:
        story = {
            "location": "Mistralton City → Opelucid City",
            "next": "Go to Route 7 → Icirrus City for the 7th badge (Brycen, Ice). Then Opelucid City for the 8th.",
            "tip": "Dragonspiral Tower is done. Focus on badges now. Brycen = Ice, Drayden/Iris = Dragon.",
            "level_range": "37-48",
        }
    elif detailed["dragonspiral_done"]:
        story = {
            "location": "Post-Dragonspiral Tower",
            "next": "Head to Opelucid City for the 8th and final badge (Drayden/Iris, Dragon type).",
            "tip": "Ice moves are essential for the Dragon gym. Lv42+ recommended.",
            "level_range": "42-48",
        }

    result["story"] = {
        "badges": badge_count,
        "progress_pct": round(badge_count / 8 * 100),
        "where_you_are": story["location"],
        "what_next": story["next"],
        "tip": story["tip"],
        "recommended_level": story["level_range"],
        "dragonspiral_done": detailed["dragonspiral_done"],
        "elite4_done": detailed["elite4_done"],
    }
    result["event_flags"] = {
        "total_set": event_result["total_flags_set"],
        "current_phase": event_result["current_phase"],
        "phase_completion": {
            phase: f"{done}/{total}"
            for phase, (done, total) in event_result["phase_completion"].items()
        },
        "key_events": {
            phase: events
            for phase, events in event_result["story_progress"].items()
        },
    }

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
    if s.get("dragonspiral_done"):
        lines.append(f"**Dragonspiral Tower:** ✓ Done")
    if s.get("elite4_done"):
        lines.append(f"**Elite Four:** ✓ Cleared")

    # Event flags summary
    ef = result.get("event_flags", {})
    if ef:
        lines.append("")
        lines.append(f"### Event Flags ({ef['total_set']} flags set)")
        lines.append(f"**Story phase:** {ef['current_phase']}")
        for phase, progress in ef.get("phase_completion", {}).items():
            marker = " ◀" if phase == ef["current_phase"] else ""
            lines.append(f"  {phase}: {progress}{marker}")

    return "\n".join(lines)
