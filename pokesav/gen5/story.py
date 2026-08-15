"""
Story progression guide for Gen 5 (Black/White).

Maps badge count to location, next steps, and tips.
NO SPOILERS — only the immediate next step.
"""

STORY = {
    0: {
        "location": "Nuvema Town → Route 1",
        "next": "Head to Accumula Town, then Striaton City for your first gym battle.",
        "tip": "Pick your starter and battle the rivals along the way.",
        "level_range": "8-14",
    },
    1: {
        "location": "Striaton City → Route 2",
        "next": "Go through Pinwheel Forest to Nacrene City for the 2nd badge.",
        "tip": "Lenora's Watchog hits hard — bring a Fighting type if you have one.",
        "level_range": "14-20",
    },
    2: {
        "location": "Nacrene City → Castelia City",
        "next": "Explore Castelia City and challenge the Bug gym. Then head to Route 4.",
        "tip": "Castelia is the big city — lots of trainers and items in the alleyways.",
        "level_range": "20-25",
    },
    3: {
        "location": "Castelia City → Nimbasa City",
        "next": "Cross the Desert Resort or Route 4 to reach Nimbasa City for the 4th badge.",
        "tip": "Elesa's Emolgas are annoying — Rock or Ice moves help a lot.",
        "level_range": "25-30",
    },
    4: {
        "location": "Nimbasa City → Driftveil City",
        "next": "Take Route 5 to Driftveil City. Visit Cold Storage for extra training.",
        "tip": "Clay's Excadrill hits hard. Water and Fighting are your best friends.",
        "level_range": "28-33",
    },
    5: {
        "location": "Driftveil City → Mistralton City",
        "next": "Go through Chargestone Cave to reach Mistralton City and the 6th badge.",
        "tip": "Skyla's gym has a fan puzzle. Her Swoobat is annoying — Electric or Rock moves.",
        "level_range": "31-35",
    },
    6: {
        "location": "Mistralton City",
        "next": "Head to Route 7 → Icirrus City for the 7th badge (Brycen, Ice type). Then Dragonspiral Tower for story events.",
        "tip": "Brycen uses Ice types — Fire, Fighting, or Steel moves crush him. Grind to Lv37+ first.",
        "level_range": "35-42",
    },
    7: {
        "location": "Icirrus City → Opelucid City",
        "next": "After Dragonspiral Tower, head to Opelucid City for the 8th and final badge.",
        "tip": "Drayden/Iris use Dragon types — Ice moves are essential. Lv42+ recommended.",
        "level_range": "40-48",
    },
    8: {
        "location": "Opelucid City → Pokémon League",
        "next": "With all 8 badges, head through Victory Road to the Pokémon League!",
        "tip": "The Elite Four are Lv48-50. Make sure your team is Lv50+ with good type coverage.",
        "level_range": "48-55",
    },
}

BADGE_NAMES = [
    ("Trio Badge",   "Striaton City",   "Cilan/Chili/Cress",   "Grass/Fire/Water"),
    ("Basic Badge",  "Nacrene City",    "Lenora",               "Normal"),
    ("Insect Badge", "Castelia City",   "Burgh",                "Bug"),
    ("Bolt Badge",   "Nimbasa City",    "Elesa",                "Electric"),
    ("Quake Badge",  "Driftveil City",  "Clay",                 "Ground"),
    ("Jet Badge",    "Mistralton City", "Skyla",                "Flying"),
    ("Freeze Badge", "Icirrus City",    "Brycen",               "Ice"),
    ("Legend Badge", "Opelucid City",   "Drayden/Iris",         "Dragon"),
]


def get_story_guidance(badge_count: int) -> dict:
    """Get story guidance for the current badge count."""
    return STORY.get(badge_count, STORY[8])
