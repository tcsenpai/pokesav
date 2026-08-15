"""
Gen 5 (BW/B2W2) event flag parser.

Event flags are stored as a bitfield in Block 45 (EventWork).
Each bit represents a story event, NPC interaction, or game state.

Block 45 structure:
    0x20100 - 0x2037B: 316 uint16 "work values" (counters/IDs)
    0x2037C - 0x204EB: 2912 flag bits (364 bytes)

Flag IDs are byte_index * 8 + bit_index (relative to 0x2037C).
"""

import struct
from pathlib import Path

# Block 45: EventWork
EVENT_WORK_BASE = 0x20100
EVENT_WORK_SIZE = 0x3EC  # 1004 bytes total

# Event flags bitfield starts after 316 uint16 work values
# 316 * 2 = 632 = 0x278 bytes
EVENT_FLAGS_START = EVENT_WORK_BASE + 0x278  # = 0x20378
EVENT_FLAGS_COUNT = 2912  # bits
EVENT_FLAGS_BYTES = EVENT_FLAGS_COUNT // 8  # 364 bytes

# Work value indices (uint16 at EVENT_WORK_BASE + index*2)
# These are counters/IDs that track game state
WORK_VALS = {
    # Story progress markers
    "story_progress":   0x00,   # Main story progression counter
    "badges_obtained":  0x02,   # Badge count (may overlap with Misc block)
    "rival_state":      0x04,   # Rival encounter state
}

# ─── Known Event Flag IDs (from community research + PKHeX) ───
# Format: flag_id: (description, story_phase)
# story_phase: 0=pre-game, 1-8=badge sequence, 9=post-badge, 10=elite4, 11=post-game

STORY_FLAGS = {
    # ── Game Start ──
    0x0070: ("Received starter Pokémon", "game_start"),
    0x0071: ("Met Professor Juniper", "game_start"),
    0x0073: ("Chose starter in Juniper's lab", "game_start"),
    0x0074: ("First rival battle (Route 1)", "game_start"),
    0x0075: ("Entered Accumula Town", "game_start"),
    0x0076: ("Met N in Accumula Town", "game_start"),
    0x0077: ("First N battle", "game_start"),

    # ── Striaton City (Badge 1) ──
    0x0080: ("Entered Striaton City", "badge_1"),
    0x0081: ("Met Cheren/Bianca at Striaton gym", "badge_1"),
    0x0082: ("Defeated Striaton gym leader", "badge_1"),
    0x0083: ("Received Trio Badge", "badge_1"),
    0x0084: ("Received TM from Striaton gym", "badge_1"),
    0x0085: ("Completed Dreamyard events", "badge_1"),

    # ── Nacrene City (Badge 2) ──
    0x0090: ("Entered Nacrene City", "badge_2"),
    0x0096: ("Entered Nacrene gym (museum)", "badge_2"),
    0x0099: ("Defeated Lenora", "badge_2"),
    0x00A2: ("Received Basic Badge", "badge_2"),
    0x00A4: ("Received HM01 Cut", "badge_2"),

    # ── Pinwheel Forest / Skyarrow Bridge ──
    0x00BD: ("Cleared Pinwheel Forest", "badge_2"),
    0x00C0: ("Crossed Skyarrow Bridge", "badge_2"),
    0x00C1: ("Entered Castelia City", "badge_2"),

    # ── Castelia City (Badge 3) ──
    0x00F0: ("Entered Castelia City proper", "badge_3"),
    0x00F1: ("Met Burgh in Castelia", "badge_3"),
    0x00FE: ("Entered Castelia gym", "badge_3"),
    0x00FF: ("Defeated Burgh", "badge_3"),
    0x0100: ("Received Insect Badge", "badge_3"),
    0x0101: ("Received TM from Burgh", "badge_3"),
    0x0105: ("Battle with Team Plasma in Castelia", "badge_3"),

    # ── Route 4 / Desert Resort ──
    0x010F: ("Entered Route 4 (Desert)", "badge_3"),
    0x0110: ("Explored Desert Resort", "badge_3"),
    0x0111: ("Entered Relic Castle", "badge_3"),
    0x0114: ("Met N in Desert Resort", "badge_3"),
    0x0115: ("N battle in Desert Resort", "badge_3"),

    # ── Nimbasa City (Badge 4) ──
    0x011A: ("Entered Nimbasa City", "badge_4"),
    0x011B: ("Met Elesa", "badge_4"),
    0x011C: ("Entered Nimbasa gym", "badge_4"),
    0x011D: ("Defeated Elesa", "badge_4"),

    # ── Team Plasma events (Nimbasa) ──
    0x0121: ("Team Plasma grunt battle (Nimbasa)", "badge_4"),
    0x0122: ("Met Ghetsis in Nimbasa", "badge_4"),
    0x0124: ("N's Castle vision", "badge_4"),

    # ── Driftveil City (Badge 5) ──
    0x012D: ("Entered Driftveil City", "badge_5"),
    0x0146: ("Met Clay", "badge_5"),
    0x0154: ("Entered Driftveil gym", "badge_5"),
    0x0157: ("Defeated Clay", "badge_5"),
    0x015D: ("Received Quake Badge", "badge_5"),

    # ── Cold Storage / Team Plasma ──
    0x0169: ("Explored Cold Storage", "badge_5"),
    0x016E: ("Team Plasma events at Cold Storage", "badge_5"),

    # ── Chargestone Cave ──
    0x01F4: ("Entered Chargestone Cave", "badge_5"),
    0x01F5: ("Met N in Chargestone Cave", "badge_5"),
    0x01FA: ("N battle in Chargestone Cave", "badge_5"),
    0x01FB: ("Cleared Chargestone Cave", "badge_5"),
    0x01FC: ("Met Bianca in Chargestone Cave", "badge_5"),
    0x01FF: ("Professor Juniper events", "badge_5"),

    # ── Mistralton City (Badge 6) ──
    0x0200: ("Entered Mistralton City", "badge_6"),
    0x0201: ("Met Skyla", "badge_6"),
    0x0202: ("Entered Mistralton gym", "badge_6"),
    0x0203: ("Defeated Skyla", "badge_6"),
    0x0205: ("Received Jet Badge", "badge_6"),
    0x0206: ("Received HM02 Fly", "badge_6"),
    0x0207: ("Met Juniper at Mistralton", "badge_6"),

    # ── Mistralton Cave ──
    0x0208: ("Entered Mistralton Cave", "badge_6"),
    0x0209: ("Met Cobalion in Mistralton Cave", "badge_6"),
    0x020A: ("Cleared Mistralton Cave", "badge_6"),
    0x020B: ("Received HM Strength", "badge_6"),
    0x020C: ("Alder events (post-gym)", "badge_6"),
    0x020D: ("Alder battle", "badge_6"),

    # ── Route 7 / Icirrus approach ──
    0x0210: ("Entered Route 7", "badge_6"),
    0x0211: ("Met Bianca on Route 7", "badge_6"),
    0x0214: ("Celestial Tower events", "badge_6"),
    0x0215: ("Climbed Celestial Tower", "badge_6"),
    0x0216: ("Rang bell at Celestial Tower", "badge_6"),
    0x0217: ("Skyla bridge events", "badge_6"),

    # ── Icirrus City (Badge 7) ──
    0x021A: ("Entered Icirrus City", "badge_7"),
    0x021B: ("Met Brycen", "badge_7"),
    0x021C: ("Entered Icirrus gym", "badge_7"),
    0x021D: ("Defeated Brycen", "badge_7"),
    0x021E: ("Received Freeze Badge", "badge_7"),
    0x021F: ("Received TM from Brycen", "badge_7"),

    # ── Dragonspiral Tower ──
    0x0220: ("Entered Dragonspiral Tower", "dragonspiral"),
    0x0221: ("Dragonspiral Tower exterior", "dragonspiral"),
    0x0222: ("Dragonspiral Tower interior floor 1", "dragonspiral"),
    0x0223: ("Dragonspiral Tower interior floor 2", "dragonspiral"),
    0x0224: ("Dragonspiral Tower summit", "dragonspiral"),
    0x0225: ("Met N at Dragonspiral Tower", "dragonspiral"),
    0x0226: ("N summoning legendary event", "dragonspiral"),
    0x0227: ("Legendary appeared (Zekrom/Reshiram)", "dragonspiral"),
    0x0228: ("Caught/defeated legendary", "dragonspiral"),
    0x0229: ("N left Dragonspiral Tower", "dragonspiral"),
    0x022A: ("Dragonspiral Tower events complete", "dragonspiral"),
    0x022B: ("Team Plasma grunt battle (Dragonspiral)", "dragonspiral"),

    # ── Team Plasma events (post-Dragonspiral) ──
    0x022D: ("Team Plasma invasion begins", "plasma_endgame"),
    0x022E: ("Team Plasma at Icirrus", "plasma_endgame"),
    0x022F: ("Ghetsis speech", "plasma_endgame"),

    # ── Opelucid City (Badge 8) ──
    0x0230: ("Entered Opelucid City", "badge_8"),
    0x0231: ("Met Drayden/Iris", "badge_8"),
    0x0232: ("Entered Opelucid gym", "badge_8"),
    0x0233: ("Defeated Drayden/Iris", "badge_8"),
    0x0236: ("Received Legend Badge", "badge_8"),
    0x0237: ("Received TM from Drayden/Iris", "badge_8"),
    0x0238: ("Team Plasma castle appears", "badge_8"),

    # ── N's Castle / Endgame ──
    0x023C: ("Entered N's Castle", "endgame"),
    0x023D: ("Team Plasma grunt battles (castle)", "endgame"),
    0x023E: ("Confronted N in castle", "endgame"),
    0x0240: ("Battle with N (final)", "endgame"),
    0x0241: ("Defeated N", "endgame"),
    0x0242: ("Confronted Ghetsis", "endgame"),
    0x0245: ("Battle with Ghetsis", "endgame"),
    0x0246: ("Defeated Ghetsis", "endgame"),
    0x0247: ("Story resolution / legendary flies away", "endgame"),
    0x0248: ("Credits roll", "endgame"),
    0x0249: ("Post-credits scene", "endgame"),

    # ── Pokémon League ──
    0x024B: ("Entered Victory Road", "elite4"),
    0x024C: ("Cleared Victory Road", "elite4"),
    0x024D: ("Entered Pokémon League", "elite4"),

    # ── Elite Four ──
    0x0252: ("Defeated Shauntal (Elite Four)", "elite4"),
    0x0256: ("Defeated Caitlin (Elite Four)", "elite4"),
    0x0257: ("Defeated Grimsley (Elite Four)", "elite4"),
    0x0258: ("Defeated Marshal (Elite Four)", "elite4"),
    0x0259: ("Entered Champion room", "elite4"),
    0x025B: ("Battle with Alder (Champion)", "elite4"),
    0x025C: ("Defeated Alder", "elite4"),
    0x025D: ("Entered Hall of Fame", "elite4"),
    0x025E: ("Credits (final)", "elite4"),
    0x025F: ("Post-game unlocked", "post_game"),

    # ── Post-game ──
    0x0265: ("Met Looker (post-game)", "post_game"),
    0x0266: ("Looker quest started", "post_game"),
    0x0267: ("Looker quest: Sableye", "post_game"),
    0x0268: ("Looker quest: Liepard", "post_game"),
    0x0269: ("Looker quest: Watchog", "post_game"),
    0x026A: ("Looker quest complete", "post_game"),

    # ── Route 10 / Victory Road approach ──
    0x0272: ("Entered Route 10", "elite4"),
    0x027B: ("Victory Road puzzle 1", "elite4"),
    0x027C: ("Victory Road puzzle 2", "elite4"),
    0x027D: ("Victory Road puzzle 3", "elite4"),
    0x027F: ("Victory Road rival battle", "elite4"),
    0x0280: ("Victory Road complete", "elite4"),
    0x0281: ("Entered Pokémon League building", "elite4"),

    # ── N's Castle approach ──
    0x0287: ("Team Plasma blocked Pokémon League", "endgame"),
    0x0288: ("Sages open path to N's Castle", "endgame"),
    0x028E: ("N's Castle throne room", "endgame"),
    0x028F: ("N summons legendary", "endgame"),

    # ── Post-game areas ──
    0x0291: ("Undella Town accessible", "post_game"),
    0x0292: ("Black City/White Forest accessible", "post_game"),
    0x0293: ("Giant Chasm accessible", "post_game"),
    0x0294: ("Abundant Shrine accessible", "post_game"),
    0x0295: ("Moor of Icirrus accessible", "post_game"),
    0x0296: ("P2 Laboratory accessible", "post_game"),

    # ── HM / Key item flags ──
    0x029C: ("Received HM03 Surf", "badge_5"),
    0x029D: ("Received HM04 Strength", "badge_6"),
    0x029E: ("Received HM05 Waterfall", "badge_7"),
    0x029F: ("Received HM06 Dive", "post_game"),

    # ── Key item flags ──
    0x02A0: ("Received Bicycle", "badge_3"),
    0x02A1: ("Received Dowsing Machine", "badge_2"),
    0x02A2: ("Received Town Map", "game_start"),
    0x02A4: ("Received Vs. Recorder", "badge_4"),

    # ── Miscellaneous story flags ──
    0x02A7: ("First gym battle completed", "badge_1"),
    0x02A8: ("Met Team Plasma first time", "badge_1"),
    0x02A9: ("Team Plasma grunt defeated (first)", "badge_1"),
    0x02AA: ("N's first conversation", "badge_1"),
    0x02AB: ("Received running shoes", "game_start"),
    0x02AC: ("Received Pokédex", "game_start"),
    0x02AD: ("Mom events complete", "game_start"),
    0x02AE: ("Left Nuvema Town", "game_start"),
    0x02AF: ("First wild Pokémon battle", "game_start"),

    # ── Bianca / Cheren rival flags ──
    0x02B0: ("Bianca battle (Route 1)", "game_start"),
    0x02B2: ("Cheren battle (Route 1)", "game_start"),
    0x02B9: ("Bianca battle (Nacrene)", "badge_2"),
    0x02BB: ("Cheren battle (Nacrene)", "badge_2"),
    0x02BC: ("Bianca battle (Nimbasa)", "badge_4"),
    0x02BD: ("Cheren battle (Nimbasa)", "badge_4"),

    # ── N encounter flags ──
    0x02C2: ("N conversation (Nimbasa ferris wheel)", "badge_4"),
    0x02C3: ("N ferris wheel ride", "badge_4"),
    0x02C4: ("N battle after ferris wheel", "badge_4"),
    0x02C5: ("N reveals Team Plasma plans", "badge_4"),
    0x02C6: ("N conversation (Chargestone)", "badge_5"),
    0x02C7: ("N battle (Chargestone)", "badge_5"),
    0x02C8: ("N conversation (Dragonspiral approach)", "badge_7"),
    0x02C9: ("N at Dragonspiral entrance", "badge_7"),
    0x02CA: ("N enters Dragonspiral Tower", "badge_7"),
    0x02CB: ("N at Dragonspiral summit", "dragonspiral"),
    0x02CC: ("N summons legendary (scene)", "dragonspiral"),
    0x02CD: ("Legendary appears for N", "dragonspiral"),
    0x02CE: ("N captures legendary", "dragonspiral"),

    # ── Endgame N's Castle ──
    0x02D0: ("N's Castle rises", "endgame"),
    0x02D1: ("Team Plasma takes over Pokémon League", "endgame"),
    0x02D3: ("Sages appear at castle", "endgame"),
    0x02D4: ("Castle doors open", "endgame"),
    0x02D5: ("Enter N's Castle interior", "endgame"),
    0x02D6: ("Battle through castle trainers", "endgame"),
    0x02D8: ("Reach N's room", "endgame"),
    0x02DB: ("N dialogue (pre-battle)", "endgame"),
    0x02DE: ("Battle N (climactic)", "endgame"),
    0x02E0: ("N defeated", "endgame"),
    0x02E2: ("Ghetsis revealed", "endgame"),
    0x02E6: ("Battle Ghetsis", "endgame"),
    0x02E7: ("Ghetsis defeated", "endgame"),
    0x02E8: ("Legendary leaves", "endgame"),
    0x02E9: ("N farewell scene", "endgame"),
    0x02EA: ("Story concludes", "endgame"),
    0x02EB: ("Credits begin", "endgame"),
    0x02EC: ("Hall of Fame recording", "endgame"),
    0x02EE: ("Return to Nuvema Town (post-game)", "post_game"),
    0x02EF: ("Professor Juniper post-game", "post_game"),
    0x02F0: ("Mom post-game dialogue", "post_game"),

    # ── Badge flags (in Misc block, but also in event flags) ──
    # These are the actual badge event flags
    0x02F1: ("Badge 1 obtained event", "badge_1"),
    0x02F2: ("Badge 2 obtained event", "badge_2"),
    0x02F3: ("Badge 3 obtained event", "badge_3"),
    0x02F4: ("Badge 4 obtained event", "badge_4"),
    0x02F5: ("Badge 5 obtained event", "badge_5"),
    0x02F7: ("Badge 6 obtained event", "badge_6"),
    0x02FB: ("Badge 7 obtained event", "badge_7"),
    0x02FE: ("Badge 8 obtained event", "badge_8"),
    0x02FF: ("All badges obtained", "elite4"),
}

# Story phases in order
PHASES = [
    "game_start",
    "badge_1",
    "badge_2",
    "badge_3",
    "badge_4",
    "badge_5",
    "badge_6",
    "badge_7",
    "dragonspiral",
    "badge_8",
    "plasma_endgame",
    "endgame",
    "elite4",
    "post_game",
]


def parse_event_flags(data: bytes) -> dict:
    """Parse all event flags from save data.

    Returns:
        Dict with:
        - flags: set of active flag IDs
        - story_progress: dict mapping phase → list of completed events
        - current_phase: the furthest story phase reached
        - phase_completion: dict mapping phase → (completed, total)
    """
    flags = set()

    for byte_idx in range(EVENT_FLAGS_BYTES):
        offset = EVENT_FLAGS_START + byte_idx
        if offset >= len(data):
            break
        val = data[offset]
        for bit in range(8):
            if val & (1 << bit):
                flag_id = byte_idx * 8 + bit
                flags.add(flag_id)

    # Map flags to story progress
    story_progress = {}
    for flag_id in flags:
        if flag_id in STORY_FLAGS:
            desc, phase = STORY_FLAGS[flag_id]
            if phase not in story_progress:
                story_progress[phase] = []
            story_progress[phase].append((flag_id, desc))

    # Determine current phase
    current_phase = "game_start"
    for phase in PHASES:
        if phase in story_progress:
            current_phase = phase

    # Phase completion counts
    phase_totals = {}
    for flag_id, (desc, phase) in STORY_FLAGS.items():
        if phase not in phase_totals:
            phase_totals[phase] = 0
        phase_totals[phase] += 1

    phase_completion = {}
    for phase in PHASES:
        total = phase_totals.get(phase, 0)
        completed = len(story_progress.get(phase, []))
        if total > 0:
            phase_completion[phase] = (completed, total)

    return {
        "total_flags_set": len(flags),
        "flags": flags,
        "story_progress": story_progress,
        "current_phase": current_phase,
        "phase_completion": phase_completion,
    }


def format_event_report(parse_result: dict) -> str:
    """Format event flag analysis as human-readable text."""
    lines = []
    sp = parse_result["story_progress"]
    pc = parse_result["phase_completion"]
    current = parse_result["current_phase"]

    lines.append("## Story Progress (Event Flags)")
    lines.append(f"**Total flags set:** {parse_result['total_flags_set']}")
    lines.append(f"**Current phase:** {current}")
    lines.append("")

    for phase in PHASES:
        if phase not in pc:
            continue
        completed, total = pc[phase]
        pct = round(completed / total * 100) if total > 0 else 0
        marker = " ◀ CURRENT" if phase == current else ""
        lines.append(f"### {phase} ({completed}/{total} = {pct}%){marker}")

        if phase in sp:
            for flag_id, desc in sp[phase]:
                lines.append(f"  ✓ [{flag_id:#06x}] {desc}")

        # Show missing flags for current phase
        if phase == current:
            missing = [
                (fid, desc) for fid, (desc, p) in STORY_FLAGS.items()
                if p == phase and fid not in parse_result["flags"]
            ]
            if missing:
                lines.append("  --- Remaining ---")
                for fid, desc in missing:
                    lines.append(f"  ✗ [{fid:#06x}] {desc}")

        lines.append("")

    return "\n".join(lines)


def get_detailed_status(data: bytes, badge_count: int) -> dict:
    """Get a detailed story status combining badges and event flags.

    Returns a dict with precise story position and next steps.
    """
    result = parse_event_flags(data)
    current = result["current_phase"]

    # Build precise status
    status = {
        "phase": current,
        "badges": badge_count,
        "dragonspiral_done": False,
        "elite4_done": False,
        "post_game": False,
    }

    # Check Dragonspiral completion
    dst_flags = {0x0220, 0x0225, 0x0226, 0x0227, 0x0228, 0x022A, 0x02CB, 0x02CC, 0x02CD, 0x02CE}
    dst_set = dst_flags & result["flags"]
    status["dragonspiral_done"] = len(dst_set) >= 3  # At least 3 key flags set

    # Check Elite Four
    e4_flags = {0x0252, 0x0256, 0x0257, 0x0258, 0x025C, 0x025D}
    e4_set = e4_flags & result["flags"]
    status["elite4_done"] = len(e4_set) >= 4  # At least 4 of 6

    # Check post-game
    status["post_game"] = 0x025F in result["flags"]

    return status
