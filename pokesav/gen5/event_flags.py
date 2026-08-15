"""
Gen 5 (BW/B2W2) event flag parser — REAL flags from FlagsEditorEXPlugin.

Source: https://raw.githubusercontent.com/fattard/FlagsEditorEXPlugin/main/flagslist/flags_gen5bw_en.txt
PKHeX: SaveBlockAccessor5BW.cs, Misc5.cs

Event flags are stored as a bitfield in Block 45 (EventWork).
Block 45: 0x20100, size 0x3EC
  - Work values (uint16): 0x20100 - 0x20377 (316 values)
  - Event flags (bitfield): 0x20378 - 0x204EB (2912 bits)

IMPORTANT: Badge count is stored as a BYTE at 0x21204 (Misc block),
NOT as event flags. Event flags track NPC interactions, items, etc.
"""

import struct

# Block 45: EventWork
EVENT_WORK_BASE = 0x20100
EVENT_FLAGS_START = 0x20378
EVENT_FLAGS_BYTES = 364  # 2912 bits / 8

# ─── Gym Leader Trainer Battle Flags ───
# These are set when you DEFEAT the gym leader in battle.
# Note: Striaton has 3 leaders (you fight 1 based on starter).
GYM_LEADER_FLAGS = [
    (0x597, "Cilan", "Striaton", "Grass"),
    (0x598, "Chili", "Striaton", "Fire"),
    (0x599, "Cress", "Striaton", "Water"),
    (0x5A1, "Lenora", "Nacrene", "Normal"),
    (0x5A2, "Burgh", "Castelia", "Bug"),
    (0x5A3, "Elesa", "Nimbasa", "Electric"),
    (0x5A4, "Clay", "Driftveil", "Ground"),
    (0x5A5, "Skyla", "Mistralton", "Flying"),
    (0x60F, "Brycen", "Icirrus", "Ice"),
    (0x610, "Drayden", "Opelucid", "Dragon"),
    (0x611, "Iris", "Opelucid", "Dragon"),
]

# ─── Gym Item Flags ───
# Set when you receive the TM from the gym leader.
GYM_ITEM_FLAGS = [
    (0x076, "Gym 1 TM"),
    (0x077, "Gym 2 TM"),
    (0x078, "Gym 3 TM"),
    (0x079, "Gym 4 TM"),
    (0x07A, "Gym 5 TM"),
    (0x07B, "Gym 6 TM"),
    (0x07C, "Gym 7 TM"),
    (0x07D, "Gym 8 TM"),
]

# ─── Legendary Flags ───
LEGENDARY_FLAGS = {
    0x0A6: "LEGEND1_GET (caught/obtained legendary 1)",
    0x0A7: "LEGEND2_GET (caught/obtained legendary 2)",
    0x0A8: "LEGEND3_GET (caught/obtained legendary 3)",
    0x0B6: "LEGEND1_BATTLE (battled legendary 1)",
}

# ─── Key Story Event Flags ───
STORY_EVENTS = {
    0x070: ("ITEM_GIFT", "Received gift item"),
    0x071: ("SODATEYA_FIRSTTALK", "First talked to Daycare"),
    0x072: ("RIVALTALK", "Rival conversation"),
    0x074: ("CGEAR_GET", "Received C-Gear"),
    0x075: ("C04GYM_TRBTL1", "Gym 4 trainer battle 1"),
    0x076: ("C04GYM_TRBTL2", "Gym 4 trainer battle 2"),
    0x07F: ("MUSEUM_TOUNAN", "Museum event"),
    0x080: ("C02GYM_TRBTL1", "Gym 2 trainer battle 1"),
    0x081: ("C02GYM_TRBTL2", "Gym 2 trainer battle 2"),
    0x082: ("C03GYM_TRBTL1", "Gym 3 trainer battle 1"),
    0x083: ("C03GYM_TRBTL2", "Gym 3 trainer battle 2"),
    0x088: ("BADGEGATE01_OPEN", "Badge gate 1 open"),
    0x089: ("BADGEGATE02_OPEN", "Badge gate 2 open"),
    0x08A: ("BADGEGATE03_OPEN", "Badge gate 3 open"),
    0x08B: ("BADGEGATE04_OPEN", "Badge gate 4 open"),
    0x08C: ("BADGEGATE05_OPEN", "Badge gate 5 open"),
    0x08D: ("BADGEGATE06_OPEN", "Badge gate 6 open"),
    0x08E: ("BADGEGATE07_OPEN", "Badge gate 7 open"),
    0x08F: ("BADGEGATE08_OPEN", "Badge gate 8 open"),
    0x098: ("ELBOARD_C02GYMWIN", "Nacrene gym victory announced"),
    0x099: ("SODATEYAOLDMAN_OPEN", "Daycare man available"),
    0x0A2: ("POKEID_FIRSTTALK", "First PokéID conversation"),
    0x0AC: ("MEZAPA_FIRSTTALK", "First conversation (unknown)"),
    0x0B6: ("LEGEND1_BATTLE", "Battled legendary 1"),
    0x0C0: ("RIVALBATTLE", "Rival battle"),
    0x0EC: ("RES_REQ_LEADER_COUNT", "Leader request count"),
    0x0FE: ("RES_LEADER_FIRSTTALK", "First leader conversation"),
    0x116: ("R08_LEG_FIRST", "Route 8 legendary first encounter"),
    0x11A: ("PLASMA_01", "Team Plasma event 1"),
    0x11B: ("PLASMA_02", "Team Plasma event 2"),
    0x11C: ("PLASMA_03", "Team Plasma event 3"),
    0x11D: ("PLASMA_04", "Team Plasma event 4"),
}

# ─── Rival Battle Flags ───
RIVAL_FLAGS = {
    0x0C0: "RIVALBATTLE (Route 1)",
    0x161: "RIVAL (Victory Road)",
    0x1F4: "RIVAL (Nuvema)",
    0x1FA: "RIVAL (accumula)",
    0x201: "RIVAL (Striaton area)",
    0x205: "RIVAL (Route 3)",
    0x207: "RIVAL (Nacrene PC)",
    0x209: "RIVAL (Nacrene)",
    0x210: "RIVAL (Nacrene 2)",
    0x21E: "RIVAL (Castelia)",
    0x220: "RIVAL (Desert 1)",
    0x221: "RIVAL (Desert 2)",
    0x22E: "RIVAL (Desert area)",
    0x236: "RIVAL (Route 5)",
    0x23D: "RIVAL (Route 3 later)",
    0x23E: "RIVAL (Route 3 area)",
}

# ─── ELBOARD flags (gym victory announcements) ───
ELBOARD_FLAGS = {
    0x971: "Striaton gym victory",
    0x972: "Nacrene gym victory",
    0x973: "Castelia gym victory",
    0x974: "Nimbasa gym victory",
    0x975: "Driftveil gym victory",
    0x976: "Mistralton gym victory",
    0x977: "Icirrus gym victory",
    0x978: "Opelucid gym victory (White)",
    0x979: "Opelucid gym victory (Black)",
}


def is_flag_set(data: bytes, flag_id: int) -> bool:
    """Check if an event flag is set."""
    byte_idx = flag_id // 8
    bit_idx = flag_id % 8
    offset = EVENT_FLAGS_START + byte_idx
    if offset >= len(data):
        return False
    return bool(data[offset] & (1 << bit_idx))


def get_work_val(data: bytes, idx: int) -> int:
    """Get a work value (uint16) by index."""
    return struct.unpack_from("<H", data, EVENT_WORK_BASE + idx * 2)[0]


def parse_event_flags(data: bytes) -> dict:
    """Parse event flags from save data.

    Returns dict with gym leaders, legendary status, story events, rival battles.
    """
    result = {
        "gym_leaders_beaten": [],
        "gym_items_received": [],
        "legendary_status": {},
        "story_events": [],
        "rival_battles": [],
        "elboard_victories": [],
        "total_flags_set": 0,
    }

    # Count total set flags
    for byte_idx in range(EVENT_FLAGS_BYTES):
        offset = EVENT_FLAGS_START + byte_idx
        if offset >= len(data):
            break
        val = data[offset]
        result["total_flags_set"] += bin(val).count("1")

    # Gym leaders
    for fid, name, city, ptype in GYM_LEADER_FLAGS:
        if is_flag_set(data, fid):
            result["gym_leaders_beaten"].append({
                "flag": fid, "name": name, "city": city, "type": ptype
            })

    # Gym items
    for fid, desc in GYM_ITEM_FLAGS:
        if is_flag_set(data, fid):
            result["gym_items_received"].append({"flag": fid, "desc": desc})

    # Legendaries
    for fid, desc in LEGENDARY_FLAGS.items():
        result["legendary_status"][desc] = is_flag_set(data, fid)

    # Story events
    for fid, (code, desc) in STORY_EVENTS.items():
        if is_flag_set(data, fid):
            result["story_events"].append({"flag": fid, "code": code, "desc": desc})

    # Rival battles
    for fid, desc in RIVAL_FLAGS.items():
        if is_flag_set(data, fid):
            result["rival_battles"].append({"flag": fid, "desc": desc})

    # ELBOARD
    for fid, desc in ELBOARD_FLAGS.items():
        if is_flag_set(data, fid):
            result["elboard_victories"].append({"flag": fid, "desc": desc})

    return result


def format_event_report(data: bytes) -> str:
    """Format event flag analysis as human-readable text."""
    result = parse_event_flags(data)
    lines = []

    lines.append(f"### Event Flags ({result['total_flags_set']} flags set)")
    lines.append("")

    # Gym leaders
    lines.append("**Gym Leaders Defeated:**")
    for entry in result["gym_leaders_beaten"]:
        lines.append(f"  ✓ {entry['name']} ({entry['city']}, {entry['type']})")
    if not result["gym_leaders_beaten"]:
        lines.append("  (none)")
    lines.append("")

    # Gym items
    if result["gym_items_received"]:
        lines.append("**Gym TMs Received:**")
        for entry in result["gym_items_received"]:
            lines.append(f"  ✓ {entry['desc']}")
        lines.append("")

    # Legendary
    lines.append("**Legendary Status:**")
    for desc, status in result["legendary_status"].items():
        lines.append(f"  {'✓' if status else '✗'} {desc}")
    lines.append("")

    # Rival battles
    if result["rival_battles"]:
        lines.append(f"**Rival Battles:** {len(result['rival_battles'])} fought")
        for entry in result["rival_battles"]:
            lines.append(f"  ✓ {entry['desc']}")
        lines.append("")

    # ELBOARD
    if result["elboard_victories"]:
        lines.append("**Gym Victories Announced:**")
        for entry in result["elboard_victories"]:
            lines.append(f"  ✓ {entry['desc']}")
        lines.append("")

    # Story events
    if result["story_events"]:
        lines.append(f"**Story Events:** {len(result['story_events'])} completed")
        for entry in result["story_events"][:20]:
            lines.append(f"  ✓ [{entry['flag']:#06x}] {entry['desc']}")
        if len(result["story_events"]) > 20:
            lines.append(f"  ... and {len(result['story_events']) - 20} more")
        lines.append("")

    return "\n".join(lines)
