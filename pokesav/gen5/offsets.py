"""
Gen 5 (BW/B2W2) verified save file offsets.

All offsets verified against PKHeX source (SaveBlockAccessor5BW.cs)
and the user's actual save file.

Block map:
    Block 27: Trainer Data      @ 0x19400, size 0x0068
    Block 28: Trainer Position   @ 0x19500, size 0x009C
    Block 32: Skin Info          @ 0x1C000, size 0x002C
    Block 33: Gym Badge Data     @ 0x1C100, size 0x0658
    Block 37: Adventure Info     @ 0x1D900, size 0x005C
    Block 45: EventWork/Flags    @ 0x20100, size 0x03EC
    Block 52: Misc (Money+Badge) @ 0x21200, size 0x00EC
"""

# Block base addresses
BLOCKS = {
    "trainer_data":   0x19400,
    "player_pos":     0x19500,
    "skin_info":      0x1C000,
    "gym_badge_data": 0x1C100,
    "adventure_info": 0x1D900,
    "event_work":     0x20100,
    "misc":           0x21200,
    "party":          0x18E00,
    "backup":         0x24000,
}

# Trainer Data fields (relative to block base 0x19400)
TRAINER = {
    "name":       0x04,   # 16 bytes, UTF-16LE
    "tid":        0x14,   # uint16
    "sid":        0x16,   # uint16
    "language":   0x1E,   # uint8 (1=JP, 2=EN, 4=IT, 5=DE, 7=ES)
    "game_ver":   0x1F,   # uint8 (20=Black, 21=White, 22=Black2, 23=White2)
    "gender":     0x21,   # uint8 (0=male, 1=female)
    "play_hours": 0x24,   # uint16
    "play_mins":  0x26,   # uint8
    "play_secs":  0x27,   # uint8
}

# Player Position fields (relative to block base 0x19500)
POSITION = {
    "map_id":  0x80,   # int32
    "player_x": 0x86,  # uint16
    "player_z": 0x8A,  # uint16
    "player_y": 0x8E,  # uint16
}

# Misc fields (relative to block base 0x21200)
MISC = {
    "money":   0x00,   # uint32
    "badges":  0x04,   # uint8, bitmask (bit0=badge1, etc.)
}

# Party structure
PARTY = {
    "count_offset": 0x00,   # uint32 party count
    "data_offset":  0x08,   # PK5 data starts 8 bytes after count
    "pk5_size":     220,    # bytes per party Pokémon
}

# Game version codes
GAME_VERSIONS = {
    20: "Black",
    21: "White",
    22: "Black 2",
    23: "White 2",
}

# Language codes
LANGUAGES = {
    1: "Japanese",
    2: "English",
    3: "French",
    4: "Italian",
    5: "German",
    7: "Spanish",
    8: "Korean",
}
