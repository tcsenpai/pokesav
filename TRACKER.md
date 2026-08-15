# Generation Support Tracker

## Status Legend
- ✅ Full support — parser, offsets, story guide all verified
- 🔧 Partial — parser works but some fields missing/unverified
- 🔜 Planned — research started, no implementation yet
- 📋 Tracked — known, no work started

## Gen 5 (Black / White / Black 2 / White 2) — ✅ Full (BW1 only)

### Verified fields
- [x] Trainer name (0x19404, UTF-16LE)
- [x] TID/SID (0x19414/0x19416)
- [x] Game version (0x1941F: 20=Black, 21=White)
- [x] Gender (0x19421)
- [x] Language (0x1941E)
- [x] Playtime (0x19424-0x19427)
- [x] Money (0x21200, uint32)
- [x] Badges (0x21204, uint8 bitmask)
- [x] Current map (0x19580, int32)
- [x] Party Pokémon (0x18E08, 6×220 PK5 structs)
- [x] PK5 decryption (LCRNG cipher, block shuffle)
- [x] Story progression guide (badge → next step, no spoilers)

### Known issues
- [ ] Nickname trailing bytes (UTF-16LE terminator `\uffff`)
- [ ] Nature offset may be wrong for traded Pokémon (always shows Hardy)
- [ ] Map ID → location name not implemented
- [ ] PC box parsing not implemented
- [ ] B2W2 offsets differ (not yet implemented)

### Source
- [PKHeX source](https://github.com/kwsch/PKHeX): SaveBlockAccessor5BW.cs, PokeCrypto.cs
- [ProjectPokemon BW Save Structure](https://projectpokemon.org/home/docs/gen-5/bw-save-structure-r73/)
- [ProjectPokemon PK5 Structure](https://projectpokemon.org/home/docs/gen-5/bw-save-structure-r60/)

---

## Gen 4 (Diamond / Pearl / Platinum / HGSS) — 🔜 Planned

### Research notes
- 512KB saves, two 256KB blocks
- PK4 structure similar to PK5 but different block layout
- Trainer data at different offsets
- Need to find: SAV4 block map from PKHeX source

---

## Gen 3 (Ruby / Sapphire / Emerald / FRLG) — 🔜 Planned

### Research notes
- 128KB saves, two 64KB halves
- 80-byte Pokémon structure (PK3)
- Encryption: XOR with PID^OT_ID, no block shuffle
- Section-based layout with 4KB sections

---

## Gen 6 (X / Y / ORAS) — 📋 Tracked

### Research notes
- 3DS save format, different from NDS
- 512KB or larger
- PK6 structure (232 bytes)
- Need decryption algorithm

---

## Gen 7 (Sun / Moon / USUM) — 📋 Tracked

### Research notes
- 3DS save format
- Similar to Gen 6 but different offsets
- PK7 structure

---

## How to add a new generation

1. **Research**: Find the save structure from PKHeX source or community docs
2. **Offsets**: Create `pokesav/genN/offsets.py` with verified block map
3. **Encryption**: Implement decrypt/unshuffle in `pokesav/genN/encryption.py`
4. **Parser**: Write `pokesav/genN/parser.py` with parse() and format_text()
5. **Data**: Add generation-specific data (species, moves, etc.) to `pokesav/data/`
6. **Detection**: Update `detect.py` with generation detection logic
7. **Register**: Add to `GENERATIONS` dict in `__init__.py`
8. **Story**: Add progression guide to `pokesav/genN/story.py`
9. **Test**: Verify against a real save file
10. **Update**: Check off items in this tracker
