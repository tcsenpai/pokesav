"""
pokesav — Pokémon save file parser.

Modular architecture: each generation is a self-contained module.
Currently supported: Gen 5 (Black/White).
"""

__version__ = "0.1.0"

GENERATIONS = {
    5: "gen5",
    # Future: 3: "gen3", 4: "gen4", 6: "gen6", etc.
}
