---
name: pokemon-save-reader
description: "Parse Pokémon .sav files for party, badges, story."
---

# Pokémon Save Reader

Parses raw `.sav` files from DS Pokémon games to extract game state and provide story guidance without spoilers.

## Repository
https://github.com/tcsenpai/pokesav

## Usage
```bash
python3 -m pokesav.cli ~/white.sav
python3 -m pokesav.cli ~/white.sav --json
python3 -m pokesav.cli ~/white.sav --gen 5
```

## Supported Generations
- **Gen 5** (Black/White) — full support (parser, event flags, story guide)
- **Gen 3** (Ruby/Sapphire/Emerald + ROM hacks) — partial (party decrypt works, trainer/story WIP)
- Gen 4 — planned

## What it extracts
- Trainer name, TID/SID, gender, language, playtime, money
- Badges (bitmask at 0x21204)
- Party Pokémon (species, level, nickname, nature, moves, IVs, stats)
- Current location (map ID)
- Story progression: where you are, what to do next, tips, recommended level

## Architecture
Modular per-generation: `pokesav/genN/` with `parser.py`, `offsets.py`, `encryption.py`, `story.py`.
Shared data in `pokesav/data/` (species, natures, moves).
Auto-detection in `pokesav/detect.py`.

## Adding a new generation
See TRACKER.md in the repo for the full checklist.

## For the agent
When user asks "where am I in Pokémon X" or "what should I do next":
1. Run `python3 -m pokesav.cli <savefile>` for Gen 5
2. For Gen 3 ROM hacks, run the parser and cross-reference with story guides
3. Report the output directly
4. If generation not supported, tell user and offer to help add it

### ROM Hack Story Guides
- **Scorched Silver**: Johto, 8 gyms (Falkner→Clair), Team Phoenix villain, Celebi storyline. Starts Cherrygrove City. Event flags at SaveBlock1+0x0000 (pokeemerald layout).
- **Lazarus**: Ilios region (Greek), 5 chapters, Regulator Syndicate. NOT pokeemerald-based.
- **Emerald Rogue**: Roguelike — no traditional story. Track run depth + hub upgrades.
- **Pisces**: Hoenn sequel, pokeemerald-expansion → standard flags work.
- **Fire Red Multiverse**: FireRed-based, multiverse concept, different flag system.

### Gen 3 Event Flags (pokeemerald-expansion)
- Flags stored at SaveBlock1 + 0x0000 (bitfield)
- SYSTEM_FLAGS base: 0x860
- Gym defeat flags: 0x4F0-0x4F7
- Elite Four: 0x4FB-0x4FE
- Game clear: 0x864
- Starter received: 0x860
