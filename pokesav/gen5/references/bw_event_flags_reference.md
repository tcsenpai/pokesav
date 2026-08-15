# Pokémon Black/White (Gen 5) Event Flag & Story Progress Reference

## Save File Structure

### EventWork Block (Block 45)
- **Absolute offset:** 0x20100
- **Size:** 0x03EC (1004 bytes)
- **Event Work values:** indices 0x000–0x13D (318 × 2 bytes = 0x27C bytes at offset 0x20100)
- **Event Flags bitfield:** 0xB60 flags = 2912 bits = 364 bytes at offset **0x2037C**

### Misc5 Block (Block 52) — Badge Flags, Money
- **Absolute offset:** 0x21200
- **Size:** 0x00EC
- **Badge count byte:** offset 0x04 → absolute **0x21204** (value 0–8)
- **Badge Victory species data:** offset 0x58 → absolute 0x21258 (6 species × 8 badges × 2 bytes)

---

## 1. Badge Count (Primary Method)

**NOT an event flag.** Stored as a single byte:

| Offset | Field | Values |
|--------|-------|--------|
| 0x21204 | Badges | 0–8 |

This is the most reliable way to determine how many badges the player has.

---

## 2. System Flags (Event Flags at 0x2037C)

### Story Milestone Flags

| Flag | Identifier | Description |
|------|-----------|-------------|
| **0x0961** | SYS_FLAG_GAME_CLEAR | Game beaten / Hall of Fame entered |
| **0x0962** | SYS_FLAG_FIRST_POKE_GET | Starter Pokémon received |
| 0x0963 | SYS_FLAG_ZUKAN_GET | Pokédex received |
| 0x0964 | SYS_FLAG_RUNNINGSHOES | Running Shoes obtained |
| 0x0965 | SYS_FLAG_KAIRIKI | Strength HM obtained |
| 0x096F | SYS_FLAG_ZENKOKU_GET | National Pokédex obtained |
| **0x097C** | SYS_FLAG_CHAMPION_WIN | Champion defeated |
| 0x097B | SYS_FLAG_ELBOARD_CHAMPWIN | Champion win shown on electronic board |
| 0x0980 | SYS_FLAG_PALACE_MISSION_START | Pokémon League mission started |
| 0x0981 | SYS_FLAG_PALACE_MISSION_CLEAR | Pokémon League mission cleared |

### Gym Victory Flags (Electronic Leaderboard)

| Flag | Identifier | Gym |
|------|-----------|-----|
| **0x0972** | SYS_FLAG_ELBOARD_C01GYMWIN | Striaton Gym (Cilan/Chili/Cress) — Badge 1 |
| **0x0973** | SYS_FLAG_ELBOARD_C02GYMWIN | Nacrene Gym (Lenora) — Badge 2 |
| **0x0974** | SYS_FLAG_ELBOARD_C03GYMWIN | Castelia Gym (Burgh) — Badge 3 |
| **0x0975** | SYS_FLAG_ELBOARD_C04GYMWIN | Nimbasa Gym (Elesa) — Badge 4 |
| **0x0976** | SYS_FLAG_ELBOARD_C05GYMWIN | Driftveil Gym (Clay) — Badge 5 |
| **0x0977** | SYS_FLAG_ELBOARD_C06GYMWIN | Mistralton Gym (Skyla) — Badge 6 |
| **0x0978** | SYS_FLAG_ELBOARD_C07GYMWIN | Icirrus Gym (Brycen) — Badge 7 |
| **0x0979** | SYS_FLAG_ELBOARD_C08WGYMWIN | Opelucid Gym (Drayden, White) — Badge 8 |
| **0x097A** | SYS_FLAG_ELBOARD_C08BGYMWIN | Opelucid Gym (Iris, Black) — Badge 8 |

### Elite Four Defeat Flags

| Flag | Identifier | Member |
|------|-----------|--------|
| **0x096A** | SYS_FLAG_BIGFOUR_GHOSTWIN | Shauntal (Ghost) beaten |
| **0x096B** | SYS_FLAG_BIGFOUR_EVILWIN | Grimsley (Dark) beaten |
| **0x096C** | SYS_FLAG_BIGFOUR_FIGHTWIN | Marshal (Fighting) beaten |
| **0x096D** | SYS_FLAG_BIGFOUR_ESPWIN | Caitlin (Psychic) beaten |

### Area Arrival Flags

| Flag | Identifier | Location |
|------|-----------|----------|
| 0x09B1 | SYS_FLAG_ARRIVE_T01 | Nuvema Town |
| 0x09B2 | SYS_FLAG_ARRIVE_T02 | Accumula Town |
| 0x09B3 | SYS_FLAG_ARRIVE_C01 | Striaton City |
| 0x09B4 | SYS_FLAG_ARRIVE_C02 | Nacrene City |
| 0x09B5 | SYS_FLAG_ARRIVE_C03 | Castelia City |
| 0x09B6 | SYS_FLAG_ARRIVE_C04 | Nimbasa City |
| 0x09B7 | SYS_FLAG_ARRIVE_C05 | Driftveil City |
| 0x09B8 | SYS_FLAG_ARRIVE_C06 | Mistralton City |
| 0x09B9 | SYS_FLAG_ARRIVE_C07 | Icirrus City |
| 0x09BA | SYS_FLAG_ARRIVE_C08 | Opelucid City |
| 0x09BB | SYS_FLAG_ARRIVE_T03 | Undella Town |
| 0x09BC | SYS_FLAG_ARRIVE_C09 | Lacunosa Town |
| 0x09BD | SYS_FLAG_ARRIVE_C10 | Village Bridge |
| 0x09BE | SYS_FLAG_ARRIVE_T04 | Black City / White Forest |
| 0x09BF | SYS_FLAG_ARRIVE_C11 | Undella Bay / Route 14 |
| 0x09C0 | SYS_FLAG_ARRIVE_D09 | Giant Chasm |

---

## 3. Badge Gate & Gym Item Flags

### Badge Gate Opening Flags

| Flag | Identifier | Gate |
|------|-----------|------|
| 0x088 | FE_BADGEGATE01_OPEN | Badge 1 gate opened |
| 0x089 | FE_BADGEGATE02_OPEN | Badge 2 gate opened |
| 0x08A | FE_BADGEGATE03_OPEN | Badge 3 gate opened |
| 0x08B | FE_BADGEGATE04_OPEN | Badge 4 gate opened |
| 0x08C | FE_BADGEGATE05_OPEN | Badge 5 gate opened |
| 0x08D | FE_BADGEGATE06_OPEN | Badge 6 gate opened |
| 0x08E | FE_BADGEGATE07_OPEN | Badge 7 gate opened |
| 0x08F | FE_BADGEGATE08_OPEN | Badge 8 gate opened |

### Gym Item Received Flags (TM/HM from gym leaders)

| Flag | Identifier | Gym |
|------|-----------|-----|
| 0x077 | FE_C01GYM_ITEM | Striaton Gym item |
| 0x078 | FE_C02GYM_ITEM | Nacrene Gym item |
| 0x079 | FE_C03GYM_ITEM | Castelia Gym item |
| 0x07A | FE_C04GYM_ITEM | Nimbasa Gym item |
| 0x07B | FE_C05GYM_ITEM | Driftveil Gym item |
| 0x07C | FE_C06GYM_ITEM | Mistralton Gym item |
| 0x07D | FE_C07GYM_ITEM | Icirrus Gym item |
| 0x07E | FE_C08GYM_ITEM | Opelucid Gym item |

---

## 4. Legendary Encounter Flags

| Flag | Identifier | Description |
|------|-----------|-------------|
| 0x0A7 | FE_LEGEND1_GET | Reshiram/Zekrom captured |
| 0x0A8 | FE_LEGEND2_GET | Legendary 2 captured |
| 0x0A9 | FE_LEGEND3_GET | Legendary 3 captured |
| 0x0B7 | FE_LEGEND1_BATTLE | Reshiram/Zekrom battle initiated |
| 0x117 | FE_R08R0101_LEG_FIRST | Dragonspiral Tower legendary first encounter |
| 0x13A | FE_R14R0201_LEG_GET | Route 14 legendary captured |
| 0x13E | FE_R14R0201_LEG_MEET | Route 14 legendary met |

---

## 5. Team Plasma Flags

| Flag | Identifier | Description |
|------|-----------|-------------|
| 0x11B | FE_D05R0201_PLASMA_01 | Cold Storage Plasma event 1 |
| 0x11C | FE_D05R0201_PLASMA_02 | Cold Storage Plasma event 2 |
| 0x11D | FE_D05R0201_PLASMA_03 | Cold Storage Plasma event 3 |
| 0x11E | FE_D05R0201_PLASMA_04 | Cold Storage Plasma event 4 |

---

## 6. N-Related Flags

| Flag | Identifier | Description |
|------|-----------|-------------|
| 0x155 | FE_N_LASTMESSAGE | N's final message |
| 0x16B | FE_N01R0304_TALK | N conversation |

---

## 7. Rival Battle Flags (Trainer Defeat)

| Flag | Identifier | Rival Battle |
|------|-----------|-------------|
| 0x5C2 | TRID_RIVAL_01 | Rival battle 1 |
| 0x5C3 | TRID_RIVAL_02 | Rival battle 2 |
| 0x5C4 | TRID_RIVAL_03 | Rival battle 3 |
| 0x5C5 | TRID_RIVAL_04 | Rival battle 4 |
| 0x5C6 | TRID_RIVAL_05 | Rival battle 5 |
| 0x5C7 | TRID_RIVAL_06 | Rival battle 6 |
| 0x5E7 | TRID_RIVAL_07 | Rival battle 7 |
| 0x5E8 | TRID_RIVAL_08 | Rival battle 8 |
| 0x5E9 | TRID_RIVAL_09 | Rival battle 9 |
| 0x6AC | TRID_RIVAL_10 | Rival battle 10 |
| 0x6AD | TRID_RIVAL_11 | Rival battle 11 |
| 0x6AE | TRID_RIVAL_12 | Rival battle 12 |
| 0x720 | TRID_RIVAL_13 | Rival battle 13 |
| 0x721 | TRID_RIVAL_14 | Rival battle 14 |
| 0x722 | TRID_RIVAL_15 | Rival battle 15 |
| 0x78B | TRID_RIVAL_16 | Rival battle 16 |
| 0x78C | TRID_RIVAL_17 | Rival battle 17 |
| 0x78D | TRID_RIVAL_18 | Rival battle 18 |
| 0x7A8 | TRID_RIVAL_19 | Rival battle 19 |
| 0x7A9 | TRID_RIVAL_20 | Rival battle 20 |
| 0x7AA | TRID_RIVAL_21 | Rival battle 21 |
| 0x7D9 | TRID_RIVAL_22 | Rival battle 22 |
| 0x7DA | TRID_RIVAL_23 | Rival battle 23 |
| 0x7DB | TRID_RIVAL_24 | Rival battle 24 |
| 0x7DC | TRID_RIVAL_25 | Rival battle 25 |
| 0x7DD | TRID_RIVAL_26 | Rival battle 26 |
| 0x7DE | TRID_RIVAL_27 | Rival battle 27 |

### Elite Four Trainer Defeat Flags

| Flag | Identifier |
|------|-----------|
| 0x5F0 | TRID_ELITEW_01 |
| 0x5F1 | TRID_ELITEW_02 |
| 0x5F2 | TRID_ELITEW_03 |
| 0x5F3 | TRID_ELITEW_04 |
| 0x5F4 | TRID_ELITEM_01 |
| 0x5F5 | TRID_ELITEM_02 |
| 0x5F6 | TRID_ELITEM_03 |
| 0x5F7 | TRID_ELITEM_04 |
| 0x671 | TRID_BIGFOUR1_01 | (Shauntal?) |
| 0x672 | TRID_BIGFOUR3_01 | (Marshal?) |
| 0x673 | TRID_BIGFOUR2_01 | (Grimsley?) |
| 0x674 | TRID_BIGFOUR4_01 | (Caitlin?) |
| 0x724 | TRID_CHAMPION_01 | Champion N/Alder battle |
| 0x7C4 | TRID_DPCHAMPION_01 | Post-game Champion battle |

---

## 8. Event Work Values (16-bit at EventWork block offset 0x20100)

### Starter & Key Story Progress

| Work Index | Identifier | Values |
|-----------|-----------|--------|
| 0x030 (48) | *(starter selection)* | 0=Snivy, 1=Tepig, 2=Oshawott |
| 0x031 | WK_SYS_FIRST_POKETYPE | Starter type |
| 0x083 (131) | *(Dreamyard monkey)* | 0=not received, 2=received |

### Scene Progress Work Values

| Work Index | Identifier | Description |
|-----------|-----------|-------------|
| 0x07B | WK_SCENE_T02 | Accumula Town |
| 0x07D | WK_SCENE_R01 | Route 1 |
| 0x07E | WK_SCENE_R02 | Route 2 |
| 0x07F | WK_SCENE_R03 | Route 3 |
| 0x083 | WK_SCENE_C01GYM0101 | Striaton Gym |
| 0x085 | WK_SCENE_C02GYM0101 | Nacrene Gym |
| 0x089 | WK_SCENE_C01 | Striaton City |
| 0x092 | WK_SCENE_VICTORY | Victory Road progress |
| 0x093 | WK_SCENE_C02 | Nacrene City |
| 0x098 | WK_SCENE_C07 | Icirrus City |
| 0x0A9 | WK_SCENE_C08 | Opelucid City |
| 0x0AA | WK_SCENE_C08GYM0101 | Opelucid Gym |

### N's Castle / Endgame Scene Progress

| Work Index | Identifier | Values |
|-----------|-----------|--------|
| **0x0B7** | WK_SCENE_N01R0502 | N's Castle: 0=Event, 1=Event, 2=Before Reshiram/Zekrom, 3=Before N, 4=Event, 5=Before Ghetsis |
| 0x0B9 | WK_SCENE_C08_GYMCLEAR | 8th gym cleared |
| 0x0D3 | WK_SCENE_R07R0105_CHAMPION | Champion's room scene |
| 0x0D5 | WK_SCENE_N01R0301 | N's Castle room 3 |
| 0x0D6 | WK_SCENE_N01R0401 | N's Castle room 4 |
| 0x0DD | WK_SCENE_N01R0501 | N's Castle room 5 |

### Team Plasma Scene Progress

| Work Index | Identifier | Description |
|-----------|-----------|-------------|
| 0x08C | WK_SCENE_D05_PLASMA | Cold Storage Plasma |
| 0x0A5 | WK_SCENE_H03_PLASMA | Plasma event at house |

### Dragonspiral Tower (R06/D06)

| Work Index | Identifier | Description |
|-----------|-----------|-------------|
| 0x09B | WK_SCENE_D06 | Dragonspiral Tower exterior |
| 0x09C | WK_SCENE_D06R0101 | Dragonspiral Tower interior |
| 0x0B8 | WK_SCENE_R06R0202 | Route 6 Dragonspiral area |

---

## 9. Recommended Story Progress Detection Strategy

For a save parser, use this detection order:

### 1. Badge Count (Primary)
```
Read byte at save offset 0x21204 → value 0-8
```

### 2. Game Cleared / Champion
```
Check event flag 0x0961 (SYS_FLAG_GAME_CLEAR) → game beaten
Check event flag 0x097C (SYS_FLAG_CHAMPION_WIN) → champion defeated
```

### 3. Starter Chosen
```
Check event flag 0x0962 (SYS_FLAG_FIRST_POKE_GET) → starter received
Read event work[0x030] → which starter (0/1/2)
```

### 4. Gym Victories (Alternative to badge count)
```
Check flags 0x0972–0x097A (SYS_FLAG_ELBOARD_C0XGYMWIN)
```

### 5. Elite Four Beaten
```
Check all 4 flags: 0x096A, 0x096B, 0x096C, 0x096D
```

### 6. N's Castle / Legendary
```
Read event work[0x0B7] for N's Castle scene progress (0-5)
Check flag 0x0A7 (FE_LEGEND1_GET) for legendary captured
```

### 7. Dragonspiral Tower Accessed
```
Check flag 0x09BA (SYS_FLAG_ARRIVE_C08) → arrived at Opelucid
Read work[0x09B] for Dragonspiral scene progress
```

---

## Sources

- PKHeX source code: `SaveBlockAccessor5BW.cs`, `EventWork5.cs`, `Misc5.cs`
- FlagsEditorEXPlugin: `flagslist/flags_gen5bw_en.txt` (2911 documented flags)
- ProjectPokemon forums: BW Flag/Event Research thread
- PKHeX GitHub issue #2607 (badge data offsets)
- PKHeX GitHub issue #2201 (event flag handling)

## Notes

- Event flags are **little-endian bitfield** at offset 0x2037C
- Flag N is at byte offset `N/8`, bit `N%8` within the EventWork block
- Absolute position: `0x2037C + (flag_number / 8)`, bit `flag_number % 8`
- The 0xB60 flags (2912) cover flags 0x000 through 0x0B5F
- Many flags are undocumented/unused in the 0x180-0x960 range (trainer IDs, NPC states, etc.)
- The user's save at 6 badges / Mistralton City should have flags set up through ~0x0977 (Skyla gym win) and arrivals through 0x09B8 (Mistralton City)
