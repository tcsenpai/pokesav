#!/usr/bin/env python3
"""
GBA Pokémon ROM Hack Save Parser
Handles pokeemerald-expansion and Fire Red ROM hacks with:
- Non-standard section_id (low 16 bits = real ID, high 16 bits = hash)
- Variable Pokémon struct size (100 or 104 bytes)
- Multiple party offsets (Emerald: 0x238, Fire Red: 0x0038)
"""

import struct
import sys
from pathlib import Path

# GBA character encoding (pokeemerald charmap)
CHAR_MAP = {0x00: ' ', 0xFF: '\0'}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    CHAR_MAP[0xBB + i] = c
for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
    CHAR_MAP[0xD5 + i] = c
for i in range(10):
    CHAR_MAP[0xA1 + i] = str(i)

def decode_gba_string(data, max_len=7):
    result = []
    for b in data[:max_len]:
        if b == 0xFF:
            break
        result.append(CHAR_MAP.get(b, f'\\x{b:02x}'))
    return ''.join(result)

def decrypt_pkm_data(personality, ot_id, encrypted_data):
    key = personality ^ ot_id
    key_bytes = struct.pack('<I', key)
    return bytes(encrypted_data[i] ^ key_bytes[i % 4] for i in range(len(encrypted_data)))

SUBSTRUCT_ORDERS = [
    [0, 1, 2, 3], [0, 1, 3, 2], [0, 2, 1, 3], [0, 2, 3, 1], [0, 3, 1, 2], [0, 3, 2, 1],
    [1, 0, 2, 3], [1, 0, 3, 2], [1, 2, 0, 3], [1, 2, 3, 0], [1, 3, 0, 2], [1, 3, 2, 0],
    [2, 0, 1, 3], [2, 0, 3, 1], [2, 1, 0, 3], [2, 1, 3, 0], [2, 3, 0, 1], [2, 3, 1, 0],
    [3, 0, 1, 2], [3, 0, 2, 1], [3, 1, 0, 2], [3, 1, 2, 0], [3, 2, 0, 1], [3, 2, 1, 0],
]

def parse_pokemon(large_data, pkm_offset):
    """Parse a single Pokémon from the large block data."""
    pv = struct.unpack_from('<I', large_data, pkm_offset)[0]
    ot = struct.unpack_from('<I', large_data, pkm_offset + 4)[0]
    nickname = decode_gba_string(large_data[pkm_offset+8:pkm_offset+18], 10)
    
    encrypted = bytes(large_data[pkm_offset+0x20:pkm_offset+0x20+48])
    decrypted = decrypt_pkm_data(pv, ot, encrypted)
    
    order = SUBSTRUCT_ORDERS[pv % 24]
    sub_names = ['Growth', 'Attack', 'EVs_Cond', 'Misc']
    
    growth_idx = order.index(0)
    growth = decrypted[growth_idx*12:(growth_idx+1)*12]
    species = struct.unpack_from('<H', growth, 0)[0]
    item = struct.unpack_from('<H', growth, 2)[0]
    exp = struct.unpack_from('<I', growth, 4)[0]
    friendship = growth[9]
    
    attack_idx = order.index(1)
    attack = decrypted[attack_idx*12:(attack_idx+1)*12]
    moves = [struct.unpack_from('<H', attack, j*2)[0] for j in range(4)]
    pp = list(attack[8:12])
    
    misc_idx = order.index(3)
    misc = decrypted[misc_idx*12:(misc_idx+1)*12]
    ivs_word = struct.unpack_from('<I', misc, 8)[0]
    ivs = {
        'HP': ivs_word & 0x1F,
        'Atk': (ivs_word >> 5) & 0x1F,
        'Def': (ivs_word >> 10) & 0x1F,
        'Spd': (ivs_word >> 15) & 0x1F,
        'SpA': (ivs_word >> 20) & 0x1F,
        'SpD': (ivs_word >> 25) & 0x1F,
    }
    
    # Read party-specific fields (unencrypted, after the encrypted block)
    level = large_data[pkm_offset + 84]
    hp = struct.unpack_from('<H', large_data, pkm_offset + 86)[0]
    max_hp = struct.unpack_from('<H', large_data, pkm_offset + 88)[0]
    atk = struct.unpack_from('<H', large_data, pkm_offset + 90)[0]
    dfn = struct.unpack_from('<H', large_data, pkm_offset + 92)[0]
    spd = struct.unpack_from('<H', large_data, pkm_offset + 94)[0]
    spa = struct.unpack_from('<H', large_data, pkm_offset + 96)[0]
    spd2 = struct.unpack_from('<H', large_data, pkm_offset + 98)[0]

    return {
        'personality': pv, 'ot_id': ot, 'nickname': nickname,
        'species': species, 'item': item, 'exp': exp, 'friendship': friendship,
        'moves': moves, 'pp': pp, 'ivs': ivs,
        'level': level,
        'stats': {'hp': hp, 'max_hp': max_hp, 'atk': atk, 'def': dfn, 'spe': spd, 'spa': spa, 'spd': spd2},
    }

def parse_save(filepath):
    """Parse a GBA Pokémon save file."""
    with open(filepath, "rb") as f:
        data = f.read()
    
    if len(data) < 0x1000 * 14:
        return {"error": "File too small for GBA save"}
    
    # Step 1: Parse all section footers
    sections_by_ctr = {}
    for block in range(len(data) // 0x1000):
        off = block * 0x1000
        sig = struct.unpack_from('<H', data, off + 0xFFA)[0]
        if sig == 0x0801:
            sid = struct.unpack_from('<H', data, off + 0xFF4)[0]  # u16!
            ctr = struct.unpack_from('<I', data, off + 0xFFC)[0]
            if ctr not in sections_by_ctr:
                sections_by_ctr[ctr] = {}
            sections_by_ctr[ctr][sid] = block
    
    if not sections_by_ctr:
        return {"error": "No valid sections found"}
    
    # Step 2: Find primary save (highest counter)
    primary_ctr = max(sections_by_ctr.keys())
    sections = sections_by_ctr[primary_ctr]
    
    if not all(s in sections for s in range(14)):
        missing = [s for s in range(14) if s not in sections]
        return {"error": f"Missing sections: {missing}"}
    
    # Step 3: Reassemble blocks
    small_data = bytearray()  # Section 0
    large_data = bytearray()  # Sections 1-4
    storage_data = bytearray()  # Sections 5-13
    
    for sid in range(14):
        block = sections[sid]
        off = block * 0x1000
        chunk = data[off:off+0xF80]
        if sid == 0:
            small_data.extend(chunk)
        elif sid <= 4:
            large_data.extend(chunk)
        else:
            storage_data.extend(chunk)
    
    # Step 4: Parse trainer info from Small block
    trainer = {
        'name': decode_gba_string(small_data[:7], 7),
        'gender': 'Female' if small_data[0x08] else 'Male',
        'tid': struct.unpack_from('<H', small_data, 0x0A)[0],
        'sid': struct.unpack_from('<H', small_data, 0x0C)[0],
    }
    trainer['ot_combined'] = (trainer['sid'] << 16) | trainer['tid']
    
    # Step 5: Find party data in Large block
    party = []
    party_count = 0
    party_offset = None
    
    # Try known offsets: 0x238 (Emerald), 0x0038 (Fire Red)
    for candidate_off in [0x238, 0x0038]:
        count_off = candidate_off - 4  # party count is 4 bytes before party array
        if count_off >= 0 and count_off < len(large_data):
            count = large_data[count_off]
            if 1 <= count <= 6:
                # Verify by checking OT match
                pkm_ot = struct.unpack_from('<I', large_data, candidate_off + 4)[0]
                if pkm_ot == trainer['ot_combined']:
                    party_count = count
                    party_offset = candidate_off
                    break
    
    if party_offset is None:
        # Fallback: scan for OT match
        for off in range(0, min(len(large_data) - 100, 0x4000), 4):
            test_ot = struct.unpack_from('<I', large_data, off + 4)[0]
            if test_ot == trainer['ot_combined']:
                pv = struct.unpack_from('<I', large_data, off)[0]
                if pv > 0 and pv < 0xFFFFFFFF:
                    # Count consecutive Pokémon with matching OT
                    count = 0
                    for size in [100, 104]:
                        c = 0
                        for i in range(6):
                            check_off = off + i * size
                            if check_off + size <= len(large_data):
                                if struct.unpack_from('<I', large_data, check_off + 4)[0] == trainer['ot_combined']:
                                    c += 1
                        if c > count:
                            count = c
                    if count > 0:
                        party_count = count
                        party_offset = off
                        break
    
    # Step 6: Parse party Pokémon (auto-detect size)
    if party_offset and party_count > 0:
        # Determine Pokémon struct size
        for pkm_size in [100, 104]:
            matches = sum(1 for i in range(party_count)
                         if party_offset + i * pkm_size + 4 <= len(large_data)
                         and struct.unpack_from('<I', large_data, party_offset + i * pkm_size + 4)[0] == trainer['ot_combined'])
            if matches == party_count:
                for i in range(party_count):
                    pkm_off = party_offset + i * pkm_size
                    pkm = parse_pokemon(large_data, pkm_off)
                    party.append(pkm)
                break
    
    return {
        'file': str(filepath),
        'size': len(data),
        'save_counter': primary_ctr,
        'sections_present': sorted(sections.keys()),
        'trainer': trainer,
        'party_count': party_count,
        'party_offset': party_offset,
        'party': party,
    }

def main():
    if len(sys.argv) < 2:
        # Default: parse all saves in inbox
        inbox = Path("/tmp/pokesav_inbox")
        saves = sorted(inbox.glob("*.sav"))
    else:
        saves = [Path(p) for p in sys.argv[1:]]
    
    for save_path in saves:
        if save_path.stat().st_size < 0x1000 * 14:
            continue  # Skip non-GBA saves
        
        result = parse_save(save_path)
        
        if "error" in result:
            print(f"\n{save_path.name}: ERROR - {result['error']}")
            continue
        
        t = result['trainer']
        print(f"\n{'='*60}")
        print(f"  {save_path.name}")
        print(f"{'='*60}")
        print(f"  Size: {result['size']} bytes | Save counter: 0x{result['save_counter']:02X}")
        print(f"  Trainer: '{t['name']}' ({t['gender']}) TID={t['tid']:05d} SID={t['sid']:05d}")
        print(f"  Party: {result['party_count']} Pokémon")
        
        for i, pkm in enumerate(result['party']):
            iv_str = '/'.join(f"{v}" for v in pkm['ivs'].values())
            print(f"    [{i+1}] #{pkm['species']:3d} '{pkm['nickname']}' "
                  f"item={pkm['item']} exp={pkm['exp']} "
                  f"friendship={pkm['friendship']}")
            print(f"        Moves: {pkm['moves']} PP: {pkm['pp']}")
            print(f"        IVs: {iv_str}")

if __name__ == "__main__":
    main()
