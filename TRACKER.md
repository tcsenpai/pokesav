# Generation Support Tracker

## Status Legend
- ✅ Full support — parser, offsets, story guide all verified
- 🔧 Partial — parser works but some fields missing/unverified
- 🔜 Planned — research started, no implementation yet
- 📋 Tracked — known, no work started

---

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
- [x] Event flags (0x2037C, story milestones)

### Known issues
- [ ] Nickname trailing bytes (UTF-16LE terminator)
- [ ] Nature offset may need adjustment
- [ ] Map ID → location name not implemented
- [ ] PC box parsing not implemented
- [ ] B2W2 offsets differ (not yet implemented)

---

## Gen 3 (Ruby / Sapphire / Emerald / FRLG + ROM hacks) — 🔧 Partial

### Verified fields
- [x] Save slot detection (counter-based)
- [x] Section layout (0=SaveBlock2, 1-4=SaveBlock1, 5-13=PC Storage)
- [x] Footer parsing (offset 4084, signature 0x08012025)
- [x] Trainer name (GBA charset: 0xBB='A', 0xD5='a')
- [x] Party count and data
- [x] PKM decryption (XOR with PID^OT_ID)
- [x] Species, level, HP, stats, moves, IVs
- [x] ROM hack support (pokeemerald-expansion footer at 0xFF4)

### Known issues
- [ ] Trainer TID/SID offset varies by ROM hack
- [ ] Money/badges not extracted
- [ ] Custom species (ROM hacks) need per-hack species tables
- [ ] Nickname charset may differ per hack
- [ ] Fire Red party offset (0x038) vs Emerald (0x238)

---

## Gen 4 (Diamond / Pearl / Platinum / HGSS) — 📋 Tracked

### Research notes
- 512KB saves, two 256KB blocks
- PK4 structure similar to PK5 (136 bytes stored, 236 party)
- Encryption: LCRNG with checksum key, block shuffle (PID >> 13) & 31
- Trainer data at different offsets than Gen 5

---

## How to add a new generation
1. Research offsets from PKHeX source or community docs
2. Create `pokesav/genN/` with parser, offsets, encryption modules
3. Add to `GENERATIONS` dict in `__init__.py`
4. Update `detect.py` with detection logic
5. Add story guidance
6. Test against real save file
