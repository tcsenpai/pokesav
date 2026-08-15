"""
Auto-detect Pokémon game generation from a .sav file.
"""

import struct
from pathlib import Path


def detect_generation(filepath: str) -> int | None:
    """Detect the generation of a Pokémon save file.

    Returns generation number (3-8) or None if unknown.
    """
    path = Path(filepath)
    size = path.stat().st_size

    with open(filepath, "rb") as f:
        data = f.read()  # Read full file for detection

    # Gen 3 (GBA): 128KB saves, specific structure
    if size in (131072,):  # 128KB
        # Gen 3 saves have two 64KB halves with a game code
        if _check_gen3(data):
            return 3

    # Gen 4 (NDS): 512KB saves for DPPt/HGSS
    if size == 524288:  # 512KB
        # Check if it's Gen 4 or Gen 5
        # Gen 5 has specific block layout with trainer at 0x19400
        full_data = Path(filepath).read_bytes()
        if _check_gen5(full_data):
            return 5
        if _check_gen4(full_data):
            return 4

    # Gen 5 (NDS BW/B2W2): also 512KB
    # Already covered above

    # Gen 6+ (3DS): 512KB or larger, different format
    if size >= 524288:
        # Could be Gen 6/7/8 but need more checks
        pass

    return None


def _check_gen3(data: bytes) -> bool:
    """Check if data looks like a Gen 3 save."""
    # Gen 3 saves have a specific section structure
    # Section 0 starts at offset 0 with a 4-byte section ID
    if len(data) < 16:
        return False
    section_id = struct.unpack_from("<I", data, 0)[0]
    # Section IDs for Gen 3 range from 0 to ~13
    return 0 <= section_id <= 13


def _check_gen4(data: bytes) -> bool:
    """Check if data looks like a Gen 4 save (DPPt/HGSS)."""
    # Gen 4 saves have a specific structure with two 256KB halves
    # The active save has a higher save counter
    # Gen 4 trainer data is at different offsets than Gen 5
    # For now, use a simple heuristic: if Gen 5 check fails, assume Gen 4
    # (since both are 512KB NDS saves)
    return not _check_gen5(data)


def _check_gen5(data: bytes) -> bool:
    """Check if data looks like a Gen 5 save (BW/B2W2)."""
    if len(data) < 524288:
        return False

    # Gen 5 has trainer data at 0x19400 with a specific structure
    # The name should be readable UTF-16LE
    try:
        name = data[0x19404:0x19414].decode("utf-16-le").rstrip("\x00").rstrip("\ufffd").rstrip("\uffff")
        if len(name) >= 2:
            # Additional check: money at 0x21200 should be reasonable
            money = struct.unpack_from("<I", data, 0x21200)[0]
            if 0 <= money <= 9999999:
                return True
    except (UnicodeDecodeError, struct.error):
        pass

    return False


def get_game_name(data: bytes, generation: int) -> str:
    """Get the game name from save data."""
    if generation == 5:
        game_ver = data[0x1941F]
        if game_ver == 20:
            return "Pokémon Black"
        elif game_ver == 21:
            return "Pokémon White"
        elif game_ver == 22:
            return "Pokémon Black 2"
        elif game_ver == 23:
            return "Pokémon White 2"
    return f"Unknown Gen {generation} game"
