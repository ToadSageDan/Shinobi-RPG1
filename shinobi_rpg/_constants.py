from __future__ import annotations

from typing import Any, Dict, Tuple

from ._types import *

# Reputation at or below this value unlocks Rogue Ninja state and Black Market.
ROGUE_THRESHOLD_MIN = -50
# Reputation at or above this value sets Heroic status.
HEROIC_THRESHOLD_MIN = 50
# Base XP requirement per level in the level-based progression curve.
BASE_XP_PER_LEVEL = 100
DEFAULT_ALLY_MIN_COUNT = 10
QUEST_CREDIT_REWARD_BASE = 35
QUEST_CREDIT_REWARD_STEP = 10
ROGUE_SHOP_DISCOUNT_PERCENT = 20
REGION_ENCOUNTER_XP_SHINOBI = 12
REGION_ENCOUNTER_XP_GUARD = 10
REGION_ENCOUNTER_XP_ANIMAL = 8
REGION_ENCOUNTER_XP_OTHER = 9
DECISION_OUTCOMES = {"kill", "charm", "stealth", "evasion"}
DAY_NIGHT_CYCLE = ("dawn", "day", "dusk", "night")
WEATHER_CYCLE = ("clear", "breezy", "rain", "storm", "fog")
ACTION_ATTRIBUTE_SPECS: Dict[str, Dict[str, Any]] = {
    "stealth": {
        "linked_stat": "agility",
        "default": 1,
        "cap": 10,
        "label": "Stealth",
        "improves": "infiltration and silent route checks",
    },
    "diplomacy": {
        "linked_stat": "focus",
        "default": 1,
        "cap": 10,
        "label": "Diplomacy",
        "improves": "social and negotiation checks",
    },
    "commerce": {
        "linked_stat": "focus",
        "default": 1,
        "cap": 10,
        "label": "Commerce",
        "improves": "shop pricing and market access",
    },
    "pickpocket": {
        "linked_stat": "agility",
        "default": 1,
        "cap": 10,
        "label": "Pickpocket",
        "improves": "theft attempts against distracted targets",
    },
    "scouting": {
        "linked_stat": "focus",
        "default": 1,
        "cap": 10,
        "label": "Scouting",
        "improves": "field intel and route reading",
    },
    "mobility": {
        "linked_stat": "agility",
        "default": 1,
        "cap": 10,
        "label": "Mobility",
        "improves": "travel setup and traversal actions",
    },
}
ATTRIBUTE_POINTS_PER_LEVEL = 2
MOBILE_FAST_TRAVEL_TOOL_NAME = "Wayfarer Anchor"
PICKPOCKET_REPUTATION_PENALTY_ON_CAUGHT = -3
PICKPOCKET_REPUTATION_PENALTY_ON_SUCCESS = -1
QUEST_LOCATION_ROTATION = (
    ("Verdant Gate", "Leafrise Village", "Watch Captain Dan"),
    ("Ashen Cradle", "Cinder Port", "Harbormaster Moon"),
    ("Tideglass Basin", "Azure Rest", "Archivist Dot"),
    ("Stormwall Ridge", "Crestfall Outpost", "Warden Shiro"),
    ("Sunken Hollow", "Dusk Refuge", "Medic Sleep"),
)
AOE_TARGETING_TERMS = ("nova", "storm", "maelstrom", "cyclone", "burst", "eruption", "field", "convergence")
STRAIGHT_LINE_TARGETING_TERMS = ("line", "lance", "spear", "arc", "bolt", "shot", "slice", "current")
OUTCOME_BRANCH_PATH_KEYS = {
    "kill": "kill_path",
    "charm": "charm_path",
    "stealth": "stealth_path",
    "evasion": "evasion_path",
}
CITY_QUEST_PRESSURE_BY_BRANCH = {
    "kill_path": 2,
    "rogue_path": 2,
    "default": 1,
    "stealth_path": 1,
    "evasion_path": 1,
    "charm_path": -1,
    "heroic_path": -1,
    "nonlethal_path": -1,
}
WORLD_MAP_REGION_COORDINATES = {
    "Verdant Gate": (4, 6),
    "Ashen Cradle": (16, 3),
    "Tideglass Basin": (28, 5),
    "Stormwall Ridge": (24, 11),
    "Sunken Hollow": (12, 12),
}
STEALTH_GATED_QUEST_IDS = {"Q3", "Q5", "Q10"}
REFORMED_VILLAIN_DIALOGUE_HOOKS: Dict[str, Dict[str, str]] = {
    "Q3": {
        "villain": "Kage Renda",
        "line": '"Enough. I have no wish to feed the gate more graves," Kage Renda admits as he lowers his blade.',
    },
    "Q5": {
        "villain": "Admiral Neris",
        "line": '"The basin has drowned in orders for too long," Admiral Neris says. "Take the peace I should have offered first."',
    },
    "Q10": {
        "villain": "Mist Widow",
        "line": '"Guard the archive better than I did," Mist Widow says, abandoning the doctrine of fear for a final warning.',
    },
}
ROLE_STANCE_BIAS = {
    "assassin": 1,
    "attrition": 1,
    "breaker": 1,
    "disruptor": 1,
    "sniper": 1,
    "warlord": 1,
    "zone_control": 1,
    "controller": -1,
    "counter": -1,
    "support_denial": -1,
    "summoner": -1,
}
COUNTRY_LORE = {
    "name": "The Quiet Steel Confederacy",
    "former_name": "The Five Banner Marches",
    "identity": (
        "A war-scarred shinobi confederacy rebuilt from fractured clan provinces, "
        "trade ports, and highland fortress lines."
    ),
    "founding_wound": (
        "A century of treaty collapses, proxy assassinations, and succession coups turned "
        "every border road into a political fault line."
    ),
    "present_conflict": (
        "Peace is real but unstable: courier sabotage, forged decrees, shrine manipulation, "
        "and cartel pressure test whether reconstruction can survive."
    ),
}
ALLY_LORE_PROFILES: Dict[str, Dict[str, str]] = {
    "Dan": {
        "title": "Route Warden of Verdant Gate",
        "backstory": (
            "Dan rose from relay scout to corridor commander after saving Leafrise convoys during "
            "the gate wars."
        ),
        "hook": "Acts as the player's first field anchor and witness to opening arc decisions.",
    },
    "Moon": {
        "title": "Signal-Master of Ashen Cradle",
        "backstory": (
            "Moon kept furnace-city beacon lines alive through siege blackouts and now oversees "
            "ceasefire logistics."
        ),
        "hook": "Connects military attrition quests to reconstruction strategy.",
    },
    "Sleep": {
        "title": "Vault-Medic of Sunken Hollow",
        "backstory": (
            "Sleep learned toxin medicine in collapsed cave wards and built antidote routes no "
            "faction can fully control."
        ),
        "hook": "Links poison crises, envoy diplomacy, and postwar trust mechanics.",
    },
    "Dot": {
        "title": "Archivist of Tideglass",
        "backstory": (
            "Dot curates flood ledgers, tribunal transcripts, and lineage seals stolen during the "
            "war years."
        ),
        "hook": "Feeds identity, treaty, and succession quests with verifiable records.",
    },
    "Porter": {
        "title": "Quartermaster of Azure Rest",
        "backstory": (
            "Porter rebuilt basin supply chains by balancing refugee relief with anti-smuggling "
            "enforcement."
        ),
        "hook": "Bridges civilian survival stakes with black-market pressure systems.",
    },
    "Ren": {
        "title": "Cartographer of Broken Borders",
        "backstory": "Ren maps disputed lines to prevent legal map-forgery wars.",
        "hook": "Supports territorial and memorial truth arcs.",
    },
    "Kaida": {
        "title": "Shrine Liaison of the Sixth Bell",
        "backstory": "Kaida mediates shrine custodians, bell couriers, and ritual security patrols.",
        "hook": "Ties sacred-site quests to assassination-counterintel threads.",
    },
    "Shiro": {
        "title": "Marshal of Winter Relief",
        "backstory": "Shiro commands cold-route evacuations and camp hardening teams.",
        "hook": "Anchors postwar sabotage and ceasefire integrity content.",
    },
    "Emi": {
        "title": "Debt Auditor of the Daimyo Court",
        "backstory": "Emi traces war finance ledgers hidden behind private tribute systems.",
        "hook": "Connects macro-economy quests to legitimacy outcomes.",
    },
    "Toma": {
        "title": "Keeper of Quiet Steel Protocol",
        "backstory": "Toma drafts succession constraints that limit emergency rule abuse.",
        "hook": "Threads final governance and heir-claim resolution arcs.",
    },
}
VILLAIN_HOOK_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Kage Renda": {"arc_tie": "political_war", "hook_quests": ("Q3", "Q26")},
    "General Voln": {"arc_tie": "fracture_front", "hook_quests": ("Q4", "Q16")},
    "Admiral Neris": {"arc_tie": "recovery_mandate", "hook_quests": ("Q5", "Q22")},
    "Mist Widow": {"arc_tie": "rebellion_wave", "hook_quests": ("Q12", "Q42")},
    "Iron Lotus": {"arc_tie": "political_war", "hook_quests": ("Q13", "Q36")},
    "Stone Maw": {"arc_tie": "fracture_front", "hook_quests": ("Q32", "Q37")},
    "Storm Needle": {"arc_tie": "highland_reckoning", "hook_quests": ("Q29", "Q47")},
    "Bone Weaver": {"arc_tie": "depths_awakening", "hook_quests": ("Q35", "Q37")},
    "Crimson Lantern": {"arc_tie": "rebellion_wave", "hook_quests": ("Q23", "Q45")},
    "Silent Bell": {"arc_tie": "recovery_mandate", "hook_quests": ("Q21", "Q42")},
    "Frost Viper": {"arc_tie": "fracture_front", "hook_quests": ("Q27", "Q34")},
    "Vanta Puppetmaster": {"arc_tie": "rebellion_wave", "hook_quests": ("Q23", "Q43")},
    "Torch Baron": {"arc_tie": "fracture_front", "hook_quests": ("Q24", "Q46")},
    "Dusk Paladin": {"arc_tie": "highland_reckoning", "hook_quests": ("Q19", "Q30")},
    "Eclipse Maw": {"arc_tie": "depths_awakening", "hook_quests": ("Q17", "Q31")},
    "Zephyr Tyrant": {"arc_tie": "highland_reckoning", "hook_quests": ("Q20", "Q40")},
    "Ashen Monarch": {"arc_tie": "depths_awakening", "hook_quests": ("Q32", "Q41")},
}
STEALTH_TROPHY_BASE_THRESHOLD = 3
STEALTH_TROPHY_ADVANCED_THRESHOLD = 5
CHARM_TROPHY_BASE_THRESHOLD = 3
CHARM_TROPHY_ADVANCED_THRESHOLD = 5
EVASION_TROPHY_THRESHOLD = 3
PACIFIST_TROPHY_ACTIONS_THRESHOLD = 5
STEALTH_TROPHY_MASTER_THRESHOLD = 8
CHARM_TROPHY_MASTER_THRESHOLD = 8
EVASION_TROPHY_MASTER_THRESHOLD = 5
NONLETHAL_STYLE_BALANCE_THRESHOLD = 2
KILL_TROPHY_BASE_THRESHOLD = 5
KILL_TROPHY_ADVANCED_THRESHOLD = 20
KILL_TROPHY_ELITE_THRESHOLD = 35
KILL_TROPHY_MASTER_THRESHOLD = 50
LEVEL_TROPHY_BASE_THRESHOLD = 5
LEVEL_TROPHY_ADVANCED_THRESHOLD = 10
ALLY_LOYALTY_TROPHY_THRESHOLD = 5
ALLY_LOYALTY_TROPHY_COUNT = 3
TROPHY_FIRST_STRIKE = "first_strike"
TROPHY_GHOST_STEP = "ghost_step"
TROPHY_SILVER_TONGUE = "silver_tongue"
TROPHY_WINDWALK_SURVIVOR = "windwalk_survivor"
TROPHY_VEIL_MASTER = "veil_master"
TROPHY_DIPLOMAT_SUPREME = "diplomat_supreme"
TROPHY_PACIFIST_SHADOW = "pacifist_shadow"
TROPHY_SILENT_LEGEND = "silent_legend"
TROPHY_PHANTOM_VEIL = "phantom_veil"
TROPHY_HARMONY_VOICE = "harmony_voice"
TROPHY_UNTOUCHABLE_GHOST = "untouchable_ghost"
TROPHY_TRINITY_OPERATOR = "trinity_operator"
TROPHY_ORIGIN_AWAKENED = "origin_awakened"
TROPHY_FIRST_BLOODLINE_VICTORY = "first_bloodline_victory"
TROPHY_WORLD_WALKER = "world_walker"
TROPHY_ROGUE_ASCENDANT = "rogue_ascendant"
TROPHY_HEROIC_CREST = "heroic_crest"
TROPHY_PEACEKEEPER_EMBLEM = "peacekeeper_emblem"
TROPHY_MERCY_CROWN = "mercy_crown"
TROPHY_BATTLE_HARDENED = "battle_hardened"
TROPHY_WAR_VETERAN = "war_veteran"
TROPHY_CRIMSON_REAPER = "crimson_reaper"
TROPHY_APEX_PREDATOR = "apex_predator"
TROPHY_RISING_NINJA = "rising_ninja"
TROPHY_SEASONED_NINJA = "seasoned_ninja"
TROPHY_LOYAL_BONDS = "loyal_bonds"
TROPHY_VILLAIN_SLAYER = "villain_slayer"
TROPHY_QUESTMASTER = "questmaster"
TROPHY_SHADOW_HEIR = "shadow_heir"
TROPHY_GHOST_SOVEREIGN = "ghost_sovereign"
TROPHY_MONK_ASCENDANT = "monk_ascendant"
# Stance evolution mastery trophies (Issue 2)
TROPHY_PACIFIER = "pacifier"
TROPHY_TERROR = "terror"
TROPHY_SHADOW_WHISPERER = "shadow_whisperer"
TROPHY_SILVER_MASK = "silver_mask"
TROPHY_WIND_DANCER = "wind_dancer"
TROPHY_STANCE_BREAKER = "stance_breaker"
# Mastery threshold constants (Issue 2)
VILLAIN_PASSIVE_TRIGGER_COUNT = 2
VILLAIN_AGGRESSIVE_TRIGGER_COUNT = 2
STANCE_BREAKER_VILLAIN_COUNT = 3
NONLETHAL_CHARM_MASTER_THRESHOLD = 10
NONLETHAL_STEALTH_MASTER_THRESHOLD = 10
NONLETHAL_EVASION_MASTER_THRESHOLD = 8
# Balance pass: nonlethal playstyle reputation gains (Issue 3)
NONLETHAL_CHARM_REP_GAIN = 2
NONLETHAL_STEALTH_REP_GAIN = 1
NONLETHAL_EVASION_REP_GAIN = 1
KILL_REP_LOSS = -1
SUMMONING_TECH_BOSS_NAME = "Vanta Puppetmaster"
DEFAULT_REWARD_INVENTORY_KEYS = ("weapon", "clothing", "move", "ally", "tech")
AFFINITY_ORDER = [Affinity.FIRE, Affinity.WATER, Affinity.EARTH, Affinity.WIND]
AFFINITY_MINIGAME_CHOICES = {
    "fire": Affinity.FIRE,
    "water": Affinity.WATER,
    "earth": Affinity.EARTH,
    "wind": Affinity.WIND,
}
STATUS_EFFECT_BANDS: Dict[StatusEffectType, Dict[str, int]] = {
    StatusEffectType.BURN: {"duration_min": 2, "duration_max": 4, "max_stacks": 3},
    StatusEffectType.BLEED: {"duration_min": 2, "duration_max": 4, "max_stacks": 3},
    StatusEffectType.CHILL: {"duration_min": 1, "duration_max": 3, "max_stacks": 2},
    StatusEffectType.DRENCH: {"duration_min": 1, "duration_max": 3, "max_stacks": 2},
    StatusEffectType.CRACK_ARMOR: {"duration_min": 1, "duration_max": 3, "max_stacks": 2},
    StatusEffectType.STAGGER: {"duration_min": 1, "duration_max": 2, "max_stacks": 1},
    StatusEffectType.BLIND: {"duration_min": 1, "duration_max": 2, "max_stacks": 1},
    StatusEffectType.SILENCE: {"duration_min": 1, "duration_max": 2, "max_stacks": 1},
    StatusEffectType.ROOT: {"duration_min": 1, "duration_max": 2, "max_stacks": 1},
    StatusEffectType.FEAR: {"duration_min": 1, "duration_max": 2, "max_stacks": 1},
}
COMBO_BONUSES: Dict[Tuple[StatusEffectType, Affinity], Dict[str, Any]] = {
    (StatusEffectType.DRENCH, Affinity.WIND): {"damage_bonus": 0.2, "label": "storm_burst"},
    (StatusEffectType.CHILL, Affinity.EARTH): {"damage_bonus": 0.15, "label": "shatter_window"},
    (StatusEffectType.CRACK_ARMOR, Affinity.FIRE): {"damage_bonus": 0.25, "label": "armor_melt"},
    (StatusEffectType.BLIND, Affinity.WIND): {"damage_bonus": 0.1, "label": "ambush_followup"},
}
BLOOD_INTENSITY_BY_BLEED_STACK = {
    0: "none",
    1: "low",
    2: "medium",
    3: "high",
}
BOSS_EXCLUSIVE_MOVE_SPECS: Dict[str, Dict[str, Any]] = {
    "Kage Renda": {
        "name": "Razorwind Spiral",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.WIND,),
        "power_scale": 1.28,
        "technique_type": TechniqueType.WEAPON_STYLE,
        "status_effects": (StatusEffectType.BLEED, StatusEffectType.CRACK_ARMOR),
    },
    "General Voln": {
        "name": "Inferno Vortex",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.FIRE,),
        "power_scale": 1.3,
        "technique_type": TechniqueType.ELEMENTAL,
        "status_effects": (StatusEffectType.BURN, StatusEffectType.STAGGER),
    },
    "Admiral Neris": {
        "name": "Maelstrom Guard",
        "category": MoveCategory.DEFENSE,
        "affinities": (Affinity.WATER,),
        "power_scale": 1.08,
        "technique_type": TechniqueType.BARRIER,
        "status_effects": (StatusEffectType.DRENCH, StatusEffectType.CHILL),
    },
    "Zephyr Tyrant": {
        "name": "Cyclone Throne Shatter",
        "category": MoveCategory.ULTIMATE,
        "affinities": (Affinity.WIND, Affinity.EARTH),
        "power_scale": 2.55,
        "technique_type": TechniqueType.ELEMENTAL,
        "status_effects": (StatusEffectType.STAGGER, StatusEffectType.CRACK_ARMOR),
    },
    "Ashen Monarch": {
        "name": "Subterranean Collapse",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.EARTH,),
        "power_scale": 1.35,
        "technique_type": TechniqueType.ELEMENTAL,
        "status_effects": (StatusEffectType.CRACK_ARMOR, StatusEffectType.ROOT),
    },
}
SUMMONING_TECH_SUPPORT_REWARD_SPECS: Dict[str, Dict[str, Any]] = {
    "ally": {
        "reward_name": "Storm Hawk Pact",
        "move_name": "Storm Hawk Dive",
        "category": MoveCategory.SUMMON,
        "affinities": (Affinity.WIND,),
        "power_scale": 1.18,
        "technique_type": TechniqueType.SUMMONING,
        "status_effects": (StatusEffectType.STAGGER,),
    },
    "tech": {
        "reward_name": "Skyline Glider Rig",
        "move_name": "Skyline Glide Strike",
        "category": MoveCategory.ESCAPE,
        "affinities": (Affinity.WIND,),
        "power_scale": 0.9,
        "technique_type": TechniqueType.MOBILITY,
        "status_effects": (StatusEffectType.BLIND,),
    },
}

# Learnable moves exclusive to important field enemies (non-boss).
# When a player defeats an important enemy, they may claim this move.
ENEMY_EXCLUSIVE_MOVE_SPECS: Dict[str, Dict[str, Any]] = {
    "Mist Ronin": {
        "name": "Fog Dagger Surge",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.WATER,),
        "power_scale": 1.05,
        "technique_type": TechniqueType.ILLUSION,
        "status_effects": (StatusEffectType.BLIND,),
    },
    "Root Stalkers": {
        "name": "Creeping Vine Bind",
        "category": MoveCategory.DEFENSE,
        "affinities": (Affinity.EARTH,),
        "power_scale": 0.92,
        "technique_type": TechniqueType.SEALING,
        "status_effects": (StatusEffectType.ROOT,),
    },
    "Ash Mercenaries": {
        "name": "Scorch Rush",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.FIRE,),
        "power_scale": 1.07,
        "technique_type": TechniqueType.ELEMENTAL,
        "status_effects": (StatusEffectType.BURN,),
    },
    "Ember Raiders": {
        "name": "Ember Burst",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.FIRE,),
        "power_scale": 1.1,
        "technique_type": TechniqueType.ELEMENTAL,
        "status_effects": (StatusEffectType.BURN, StatusEffectType.STAGGER),
    },
    "Tide Hunters": {
        "name": "Deep Current Drag",
        "category": MoveCategory.ESCAPE,
        "affinities": (Affinity.WATER,),
        "power_scale": 0.78,
        "technique_type": TechniqueType.MOBILITY,
        "status_effects": (StatusEffectType.DRENCH,),
    },
    "Reef Assassins": {
        "name": "Reef Shadow Lunge",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.WATER,),
        "power_scale": 1.08,
        "technique_type": TechniqueType.WEAPON_STYLE,
        "status_effects": (StatusEffectType.BLEED, StatusEffectType.DRENCH),
    },
    "Windcutter Raiders": {
        "name": "Gale Blade Flurry",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.WIND,),
        "power_scale": 1.06,
        "technique_type": TechniqueType.WEAPON_STYLE,
        "status_effects": (StatusEffectType.BLEED, StatusEffectType.STAGGER),
    },
    "Gale Monks": {
        "name": "Resonant Wind Seal",
        "category": MoveCategory.DEFENSE,
        "affinities": (Affinity.WIND,),
        "power_scale": 0.88,
        "technique_type": TechniqueType.SEALING,
        "status_effects": (StatusEffectType.SILENCE,),
    },
    "Stormcaller Scouts": {
        "name": "Lightning Thread",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.WIND,),
        "power_scale": 1.09,
        "technique_type": TechniqueType.SENSORY,
        "status_effects": (StatusEffectType.STAGGER, StatusEffectType.CRACK_ARMOR),
    },
    "Cave Stalkers": {
        "name": "Blind Ambush",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.EARTH,),
        "power_scale": 1.1,
        "technique_type": TechniqueType.ILLUSION,
        "status_effects": (StatusEffectType.BLIND,),
    },
    "Poison Adepts": {
        "name": "Venom Weave",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.EARTH,),
        "power_scale": 1.06,
        "technique_type": TechniqueType.SUPPORT,
        "status_effects": (StatusEffectType.BLEED, StatusEffectType.CRACK_ARMOR),
    },
    "Hollow Wraiths": {
        "name": "Wraith Shriek",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.WIND,),
        "power_scale": 1.07,
        "technique_type": TechniqueType.ILLUSION,
        "status_effects": (StatusEffectType.FEAR, StatusEffectType.SILENCE),
    },
}

WORLD_EVENT_LIBRARY: Dict[str, Dict[str, Any]] = {
    "tornado": {
        "label": "Tornado tears through frontier villages.",
        "region_pressure": 2,
        "recovery_delta": -2,
        "villain_signal": "chaos",
        "arc_bias": "fracture_front",
        "stance_shift": "kill",
    },
    "supply_collapse": {
        "label": "Supply collapse starves border outposts.",
        "region_pressure": 1,
        "recovery_delta": -1,
        "villain_signal": "scarcity",
        "arc_bias": "political_war",
        "stance_shift": "aggressive",
    },
    "political_coup": {
        "label": "A political coup fractures council command.",
        "region_pressure": 1,
        "recovery_delta": -1,
        "villain_signal": "betrayal",
        "arc_bias": "rebellion_wave",
        "stance_shift": "betray",
    },
    "plague_wave": {
        "label": "A plague wave forces quarantines and mistrust.",
        "region_pressure": 2,
        "recovery_delta": -2,
        "villain_signal": "fear",
        "arc_bias": "recovery_mandate",
        "stance_shift": "kill",
    },
    "migration_surge": {
        "label": "Mass migration reshapes alliances and guard lines.",
        "region_pressure": 1,
        "recovery_delta": 0,
        "villain_signal": "pressure",
        "arc_bias": "fracture_front",
        "stance_shift": "stealth",
    },
    "reconstruction_success": {
        "label": "Reconstruction succeeds and villages regain leverage.",
        "region_pressure": -2,
        "recovery_delta": 2,
        "villain_signal": "stability",
        "arc_bias": "recovery_mandate",
        "stance_shift": "charm",
    },
    "rebuild_failure": {
        "label": "Rebuild failure sparks ration riots and extremism.",
        "region_pressure": 2,
        "recovery_delta": -2,
        "villain_signal": "radicalization",
        "arc_bias": "rebellion_wave",
        "stance_shift": "kill",
    },
}


# Minimum accumulated seeds before a latent echo fires for each decision type.
DECISION_SEED_THRESHOLDS: Dict[str, int] = {
    "kill": 3,
    "charm": 3,
    "stealth": 4,
    "evasion": 4,
    "betray": 2,
}

# Subtle world echoes that emerge from accumulated decision seeds.
# These are fired during tick_latent_effects, never immediately.
LATENT_ECHO_LIBRARY: Dict[str, Dict[str, Any]] = {
    "kill_echo": {
        "label": "Fear spreads through border settlements after violent encounters.",
        "region_pressure": 1,
        "recovery_delta": -1,
        "villain_signal": "fear",
        "arc_bias": "fracture_front",
        "narrative_tag": "feared_fighter",
    },
    "charm_echo": {
        "label": "Word of a persuasive wanderer spreads through distant contacts.",
        "region_pressure": -1,
        "recovery_delta": 1,
        "villain_signal": "diplomacy",
        "arc_bias": "recovery_mandate",
        "narrative_tag": "silver_voice",
    },
    "stealth_echo": {
        "label": "Unexplained gaps in patrols unsettle local commanders.",
        "region_pressure": 1,
        "recovery_delta": 0,
        "villain_signal": "paranoia",
        "arc_bias": "fracture_front",
        "narrative_tag": "phantom_presence",
    },
    "evasion_echo": {
        "label": "Rumors of an uncatchable wanderer circulate among village scouts.",
        "region_pressure": 0,
        "recovery_delta": 1,
        "villain_signal": "mystique",
        "arc_bias": "political_war",
        "narrative_tag": "elusive_ghost",
    },
    "betray_echo": {
        "label": "Trust fractures quietly among those who trade in information.",
        "region_pressure": 2,
        "recovery_delta": -2,
        "villain_signal": "betrayal",
        "arc_bias": "rebellion_wave",
        "narrative_tag": "shadow_agent",
    },
}


# Lower threshold means an NPC crosses into antagonist pressure sooner.
NPC_EVIL_TIER_THRESHOLDS: Dict[str, int] = {
    "volatile": 4,
    "balanced": 6,
    "unlikely": 8,
}
NPC_EVIL_TIER_WEIGHTS: Tuple[Tuple[str, int], ...] = (
    ("volatile", 1),
    ("balanced", 3),
    ("unlikely", 2),
)
# Event payload fields:
# - label: in-world consequence text used in summaries/tapestry
# - headline: intel-facing rumor text for newspaper/overheard channels
# - min_shift/max_shift: evil-score delta range applied per affected NPC
# - target_count: number of NPC profiles shifted by the event
# - unlock_signal: suffix used for stealth intel-route unlock nodes
EXTERNAL_PRESSURE_EVENT_LIBRARY: Dict[str, Dict[str, Any]] = {
    "blackmail_dossier": {
        "label": "Blackmail dossiers surface in back-channel markets.",
        "headline": "Leaked dossiers expose hidden debts among shinobi cells.",
        "min_shift": 1,
        "max_shift": 3,
        "target_count": 2,
        "unlock_signal": "hidden_archive",
    },
    "border_false_flag": {
        "label": "A false-flag strike blurs ally and enemy lines.",
        "headline": "Witnesses dispute who ordered the border strike.",
        "min_shift": 1,
        "max_shift": 2,
        "target_count": 3,
        "unlock_signal": "watch_post",
    },
    "scarcity_crackdown": {
        "label": "Supply scarcity drives hardline village crackdowns.",
        "headline": "Ration riots trigger emergency law in fringe districts.",
        "min_shift": 1,
        "max_shift": 2,
        "target_count": 2,
        "unlock_signal": "supply_route",
    },
    "forbidden_scroll_auction": {
        "label": "Forbidden scrolls reappear through masked brokers.",
        "headline": "Rumors point to a midnight scroll auction under guard.",
        "min_shift": 2,
        "max_shift": 3,
        "target_count": 1,
        "unlock_signal": "auction_den",
    },
}
INTEL_CHANNELS = {"newspaper", "overheard"}

# ---------------------------------------------------------------------------
# Gameplay improvement constants
# ---------------------------------------------------------------------------

# Feature 1 — Affinity Resonance pairs and passive damage multiplier
AFFINITY_RESONANCE_PAIRS: Dict[Tuple[str, str], Dict[str, Any]] = {
    ("wind", "water"): {"label": "Storm Doctrine", "damage_bonus": 0.15, "flavor": "storm_surge"},
    ("fire", "wind"): {"label": "Inferno Gale", "damage_bonus": 0.12, "flavor": "wildfire_rush"},
    ("earth", "water"): {"label": "Tide Bastion", "damage_bonus": 0.10, "flavor": "flood_lock"},
    ("fire", "earth"): {"label": "Magma Doctrine", "damage_bonus": 0.13, "flavor": "eruption_press"},
    ("wind", "earth"): {"label": "Gale Shatter", "damage_bonus": 0.11, "flavor": "sandstorm_rend"},
    ("fire", "water"): {"label": "Steam Veil", "damage_bonus": 0.08, "flavor": "scalding_mist"},
}

# Feature 3 — Chakra resource system
CHAKRA_MAX = 100
CHAKRA_START = 80
CHAKRA_REGEN_ESCAPE = 15
CHAKRA_COST: Dict[str, int] = {
    "attack": 10,
    "defense": 8,
    "summon": 12,
    "ultimate": 30,
    "escape": 0,
}

# Feature 4 — Enemy patrol / stealth aggro states
PATROL_STATE_UNDETECTED = "undetected"
PATROL_STATE_ALERTED = "alerted"
PATROL_STATE_COMBAT_LOCKED = "combat_locked"
PATROL_AGGRO_WINDOW = 2       # consecutive stealth failures to escalate undetected→alerted
PATROL_LOCKDOWN_WINDOW = 2    # consecutive failures at alerted to reach combat_locked

# Feature 6 — Reputation decay thresholds
REPUTATION_DECAY_INACTIVITY_TICKS = 5   # ticks without reinforcing decisions before decay fires
REPUTATION_DECAY_AMOUNT = 1             # absolute decay per tick toward neutral

# Feature 8 — Move proficiency / training cost
MOVE_PROFICIENCY_MAX = 100
MOVE_PROFICIENCY_DEFAULT = 80
MOVE_PROFICIENCY_DECAY_ON_SKIP = 5      # proficiency lost per encounter the move is unused
MOVE_PROFICIENCY_LOW_THRESHOLD = 40     # effective power_scale penalty kicks in below this
MOVE_PROFICIENCY_SCALE_FLOOR = 0.6      # minimum effective scale multiplier at zero proficiency
MOVE_TRAIN_CREDIT_COST = 20             # credits to restore full proficiency at a hub

# Feature 9 — Nonlethal flow state / combo chain
NONLETHAL_FLOW_CHAIN_THRESHOLD = 2      # consecutive nonlethal outcomes to enter flow state
NONLETHAL_FLOW_EVASION_BONUS = True     # flow state grants a free evasion opportunity
NONLETHAL_FLOW_STEALTH_DURATION = 1     # encounters the stealth buff lasts

# Feature 10 — Boss echo rematch
BOSS_ECHO_STANCE_OVERRIDE = VillainStance.AGGRESSIVE
BOSS_ECHO_POWER_SCALE_BOOST = 0.25      # added to the boss move's base power_scale
BOSS_ECHO_EXTRA_MOVE_COUNT = 1          # number of player moves the echo boss borrows

# Feature 12 — Weapon durability
WEAPON_DURABILITY_MAX = 100
WEAPON_DURABILITY_START = 100
WEAPON_DURABILITY_LOSS_PER_USE = 10
WEAPON_DURABILITY_LOW_THRESHOLD = 30    # power penalty begins below this
WEAPON_DURABILITY_SCALE_FLOOR = 0.7     # minimum effective power ratio at zero durability
WEAPON_REPAIR_CREDIT_COST_BASE = 25     # flat repair cost per weapon
WEAPON_REPAIR_CREDIT_COST_PER_UNIT = 1  # extra credit per durability point restored

# Feature 13 — Scouting payoff options
SCOUTING_INTEL_CATEGORIES = ("enemy_count", "elite_position", "boss_move_preview", "hidden_poi")
SCOUTING_MIN_ATTRIBUTE = 3              # scouting attribute needed for reliable intel

# Feature 14 — Karmic inheritance bonuses
KARMIC_INHERITANCE_REP_BONUS = 2        # reputation starting bonus from prior run
KARMIC_INHERITANCE_STYLES = ("rogue", "heroic", "nonlethal")

# Ally combat ability definitions (Feature 2)
ALLY_COMBAT_ABILITIES: Dict[str, Dict[str, Any]] = {
    "Dan": {
        "ability_name": "Warden's Bulwark",
        "category": "defense",
        "description": "Dan raises a corridor shield, granting the player a defense boost for one round.",
        "stat_bonus": {"defense": 5},
        "duration": 1,
        "cooldown_encounters": 3,
    },
    "Moon": {
        "ability_name": "Beacon Burst",
        "category": "attack",
        "description": "Moon launches a signal flare that distracts enemies, applying Blind for 1 turn.",
        "status_effect": "blind",
        "duration": 1,
        "cooldown_encounters": 3,
    },
    "Sleep": {
        "ability_name": "Venom Cloud",
        "category": "attack",
        "description": "Sleep drops a poison cloud that applies Bleed and Crack Armor.",
        "status_effects": ["bleed", "crack_armor"],
        "duration": 2,
        "cooldown_encounters": 4,
    },
    "Dot": {
        "ability_name": "Archive Seal",
        "category": "defense",
        "description": "Dot channels a treaty seal that temporarily Silences an enemy.",
        "status_effect": "silence",
        "duration": 1,
        "cooldown_encounters": 3,
    },
    "Porter": {
        "ability_name": "Supply Drop",
        "category": "support",
        "description": "Porter delivers a supply cache, restoring 20 chakra.",
        "chakra_restore": 20,
        "cooldown_encounters": 4,
    },
    "Ren": {
        "ability_name": "Terrain Read",
        "category": "escape",
        "description": "Ren reads the battlefield, granting a free escape opportunity.",
        "grants_free_escape": True,
        "cooldown_encounters": 4,
    },
    "Kaida": {
        "ability_name": "Shrine Ward",
        "category": "defense",
        "description": "Kaida invokes a ritual barrier, granting Root resistance for 2 turns.",
        "status_immunity": "root",
        "duration": 2,
        "cooldown_encounters": 5,
    },
    "Shiro": {
        "ability_name": "Cold March",
        "category": "attack",
        "description": "Shiro leads a cold-route flanking strike, applying Chill and Stagger.",
        "status_effects": ["chill", "stagger"],
        "duration": 1,
        "cooldown_encounters": 4,
    },
    "Emi": {
        "ability_name": "Debt Audit",
        "category": "support",
        "description": "Emi exposes a financial pressure point, applying Fear to the target.",
        "status_effect": "fear",
        "duration": 1,
        "cooldown_encounters": 3,
    },
    "Toma": {
        "ability_name": "Protocol Mandate",
        "category": "support",
        "description": "Toma invokes a succession clause that boosts all ally loyalty by 1.",
        "ally_loyalty_bonus": 1,
        "cooldown_encounters": 5,
    },
}


