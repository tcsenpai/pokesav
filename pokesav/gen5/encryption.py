"""
Gen 5 (BW/B2W2) encryption and decryption.

Based on PKHeX PokeCrypto.cs:
https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/PKM/Util/PokeCrypto.cs
"""

import struct

# Block shuffle order table (from PKHeX)
BLOCK_POSITION = [
    0, 1, 2, 3, 0, 1, 3, 2, 0, 2, 1, 3, 0, 3, 1, 2,
    0, 2, 3, 1, 0, 3, 2, 1, 1, 0, 2, 3, 1, 0, 3, 2,
    2, 0, 1, 3, 3, 0, 1, 2, 2, 0, 3, 1, 3, 0, 2, 1,
    1, 2, 0, 3, 1, 3, 0, 2, 2, 1, 0, 3, 3, 1, 0, 2,
    2, 3, 0, 1, 3, 2, 0, 1, 1, 2, 3, 0, 1, 3, 2, 0,
    2, 1, 3, 0, 3, 1, 2, 0, 2, 3, 1, 0, 3, 2, 1, 0,
    # Duplicates of entries 0-7 for sv 24-31 (avoids modulus)
    0, 1, 2, 3, 0, 1, 3, 2,
]


def lcrng(seed: int) -> int:
    """Linear Congruential RNG used by Gen 5."""
    return ((seed * 0x41C64E6D) + 0x6073) & 0xFFFFFFFF


def crypt_array(data: bytearray, seed: int) -> bytearray:
    """XOR encrypt/decrypt a byte array using LCRNG keystream."""
    result = bytearray(data)
    for i in range(0, len(result), 2):
        seed = lcrng(seed)
        if i + 1 < len(result):
            val = struct.unpack_from("<H", result, i)[0]
            struct.pack_into("<H", result, i, val ^ ((seed >> 16) & 0xFFFF))
    return result


def shuffle_blocks(data_128: bytearray, sv: int) -> bytearray:
    """Unshuffle 4 data blocks of 32 bytes each.

    Args:
        data_128: 128 bytes of encrypted data (4 blocks × 32 bytes)
        sv: Shuffle value from (PID >> 13) & 31

    Returns:
        128 bytes with blocks in correct order (G, A, E, M)
    """
    pos = sv * 4
    if pos + 4 > len(BLOCK_POSITION):
        return data_128

    order = BLOCK_POSITION[pos : pos + 4]
    blocks = [data_128[i * 32 : (i + 1) * 32] for i in range(4)]
    result = bytearray(128)

    for dest in range(4):
        src = order[dest]
        result[dest * 32 : (dest + 1) * 32] = blocks[src]

    return result


def decrypt_pokemon_data(raw: bytes) -> dict | None:
    """Decrypt a Gen 5 PK5 structure (220 bytes for party, 136 for stored).

    Returns parsed dict or None if data is invalid.

    PK5 structure:
        0x00-0x03: PID (uint32, unencrypted)
        0x04-0x05: Unused (uint16)
        0x06-0x07: Checksum (uint16, unencrypted)
        0x08-0x87: Encrypted data (128 bytes, 4 blocks of 32)
            Block G (Growth): species, item, OT ID, exp, friendship, ability
            Block A (Attack): moves, PP, IVs, nature
            Block E (Misc):  nickname, origin game
            Block D (OT):    OT name, met location, ball
        0x88-0xDB: Battle stats (encrypted with PID, party only)
    """
    if len(raw) < 136:
        return None

    pid = struct.unpack_from("<I", raw, 0)[0]
    chk = struct.unpack_from("<H", raw, 6)[0]

    if pid == 0:
        return None

    # Decrypt data blocks
    sv = (pid >> 13) & 31
    dec_data = crypt_array(bytearray(raw[8:136]), chk)
    reordered = shuffle_blocks(dec_data, sv)

    # Parse Block G (Growth) — now at offset 0 in reordered
    species = struct.unpack_from("<H", reordered, 0)[0]
    if species < 1 or species > 649:
        return None

    item = struct.unpack_from("<H", reordered, 2)[0]
    ot_tid = struct.unpack_from("<H", reordered, 4)[0]
    ot_sid = struct.unpack_from("<H", reordered, 6)[0]
    exp = struct.unpack_from("<I", reordered, 8)[0]
    friendship = reordered[12]
    ability = reordered[13]

    # Parse Block A (Attack) — offset 32
    moves = [struct.unpack_from("<H", reordered, 32 + i * 2)[0] for i in range(4)]
    pp = [reordered[40 + i] for i in range(4)]
    ivs_raw = struct.unpack_from("<I", reordered, 48)[0]
    nature = reordered[65]

    ivs = {
        "hp": ivs_raw & 0x1F,
        "atk": (ivs_raw >> 5) & 0x1F,
        "def": (ivs_raw >> 10) & 0x1F,
        "spe": (ivs_raw >> 15) & 0x1F,
        "spa": (ivs_raw >> 20) & 0x1F,
        "spd": (ivs_raw >> 25) & 0x1F,
    }

    # Parse Block E (Misc) — offset 64
    try:
        nickname = reordered[64:86].decode("utf-16-le").rstrip("\x00").rstrip("\ufffd")
    except (UnicodeDecodeError, ValueError):
        nickname = ""

    # Parse Block D (OT) — offset 96
    try:
        ot_name = reordered[96:112].decode("utf-16-le").rstrip("\x00").rstrip("\ufffd")
    except (UnicodeDecodeError, ValueError):
        ot_name = ""

    result = {
        "pid": pid,
        "species_id": species,
        "item_id": item,
        "ot_tid": ot_tid,
        "ot_sid": ot_sid,
        "exp": exp,
        "friendship": friendship,
        "ability": ability,
        "moves": moves,
        "pp": pp,
        "ivs": ivs,
        "nature": nature,
        "nickname": nickname or None,
        "ot_name": ot_name or None,
    }

    # Parse battle stats (party only, encrypted with PID)
    if len(raw) >= 220:
        battle = crypt_array(bytearray(raw[136:220]), pid)
        result["level"] = battle[4]
        result["stats"] = {
            "hp": struct.unpack_from("<H", battle, 6)[0],
            "max_hp": struct.unpack_from("<H", battle, 8)[0],
            "atk": struct.unpack_from("<H", battle, 10)[0],
            "def": struct.unpack_from("<H", battle, 12)[0],
            "spe": struct.unpack_from("<H", battle, 14)[0],
            "spa": struct.unpack_from("<H", battle, 16)[0],
            "spd": struct.unpack_from("<H", battle, 18)[0],
        }

    return result
