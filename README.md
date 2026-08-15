# pokesav

Parse Pokémon save files and get story guidance. Auto-detects generation, extracts trainer data, party, badges, money, and tells you what to do next — no spoilers.

## Supported Generations

| Gen | Games | Status |
|-----|-------|--------|
| 5   | Black, White, Black 2, White 2 | ✅ Full support |
| 4   | Diamond, Pearl, Platinum, HGSS | 🔜 Planned |
| 3   | Ruby, Sapphire, Emerald, FRLG | 🔜 Planned |
| 6   | X, Y, ORAS | 📋 Tracked |
| 7   | Sun, Moon, USUM | 📋 Tracked |

## Install

```bash
# Clone and use directly
git clone https://github.com/tcsenpai/pokesav.git
cd pokesav
python3 -m pokesav.cli path/to/save.sav
```

No external dependencies — pure Python 3.11+.

## Usage

```bash
# Auto-detect generation and parse
python3 -m pokesav.cli white.sav

# Force generation
python3 -m pokesav.cli white.sav --gen 5

# JSON output
python3 -m pokesav.cli white.sav --json
```

## Example Output

```
## Pokémon Black
**Trainer:** GEENO (Male) | TID: 26729 | English
**Playtime:** 15h 23m 15s | **Money:** ¥13,631
**Badges:** 6/8 (75% of story)

  ✓ Trio Badge — Cilan/Chili/Cress (Grass/Fire/Water)
  ✓ Basic Badge — Lenora (Normal)
  ✓ Insect Badge — Burgh (Bug)
  ✓ Bolt Badge — Elesa (Electric)
  ✓ Quake Badge — Clay (Ground)
  ✓ Jet Badge — Skyla (Flying)
  ✗ Freeze Badge — Brycen (Ice)
  ✗ Legend Badge — Drayden/Iris (Dragon)

### Party (6 Pokémon, avg Lv31)
  1. Panpour Lv24 (Hardy)
  2. Sigilyph Lv31 (Hardy)
  3. Servine Lv34 (Hardy)
  4. Darumaka Lv32 (Hardy)
  5. Excadrill Lv35 (Hardy)
  6. Cherrim Lv31 (Hardy)

### Where you are: Mistralton City
**Next:** Head to Route 7 → Icirrus City for the 7th badge (Brycen, Ice type).
**Tip:** Brycen uses Ice types — Fire, Fighting, or Steel moves crush him.
**Recommended level:** 35-42
```

## Architecture

```
pokesav/
├── __init__.py          # Generation registry
├── cli.py               # CLI entry point
├── detect.py            # Auto-detect generation from .sav
├── data/
│   ├── species.py       # National Pokédex names (1-649)
│   └── natures.py       # Nature names (0-24)
└── gen5/                # Gen 5 (BW/B2W2) parser
    ├── __init__.py
    ├── encryption.py    # PK5 decrypt/unshuffle (LCRNG)
    ├── offsets.py       # Verified save block offsets
    ├── parser.py        # Main parser + formatter
    └── story.py         # Story progression guide
```

### Adding a new generation

1. Create `pokesav/genN/` with `parser.py`, `offsets.py`, `encryption.py`
2. Add generation-specific data to `pokesav/data/` if needed
3. Register in `pokesav/__init__.py`: `GENERATIONS[N] = "genN"`
4. Update `detect.py` with detection logic
5. Update this README

## How it works

### Save structure (Gen 5)
- 512KB raw `.sav` file (DeSmuME format)
- Primary save at `0x0`, backup at `0x24000`
- Blocks with individual checksums (CRC16-CCITT)
- PK5 Pokémon data: encrypted with LCRNG cipher, shuffled into 4 blocks

### Key offsets (BW1, verified against PKHeX source)
| Field | Offset | Type |
|-------|--------|------|
| Trainer name | `0x19404` | UTF-16LE, 16 bytes |
| Game version | `0x1941F` | uint8 |
| Playtime | `0x19424` | hours(uint16) + mins + secs |
| Current map | `0x19580` | int32 |
| Money | `0x21200` | uint32 |
| Badges | `0x21204` | uint8 bitmask |
| Party | `0x18E08` | 6× 220-byte PK5 structs |

## Known issues

- Nickname parsing has trailing garbage bytes (UTF-16LE terminator handling)
- Nature always shows as "Hardy" (offset may need adjustment for traded Pokémon)
- Map ID → location name mapping not yet implemented (shows raw ID)
- No PC box parsing yet

## License

MIT
