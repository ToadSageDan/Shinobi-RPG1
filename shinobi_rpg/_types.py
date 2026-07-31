from __future__ import annotations

from enum import Enum

class Affinity(str, Enum):
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    WIND = "wind"


class MoveCategory(str, Enum):
    ESCAPE = "escape"
    ATTACK = "attack"
    DEFENSE = "defense"
    SUMMON = "summon"
    ULTIMATE = "ultimate"


class TechniqueType(str, Enum):
    ELEMENTAL = "elemental"
    BARRIER = "barrier"
    MOBILITY = "mobility"
    SUMMONING = "summoning"
    CLONE = "clone"
    SUPPORT = "support"
    SENSORY = "sensory"
    SEALING = "sealing"
    WEAPON_STYLE = "weapon_style"
    ILLUSION = "illusion"


class WeaponType(str, Enum):
    SWORD = "sword"
    KUNAI = "kunai"
    BOW_STAFF = "bow_staff"
    NINJA_STARS = "ninja_stars"


class StatusEffectType(str, Enum):
    BURN = "burn"
    BLEED = "bleed"
    CHILL = "chill"
    DRENCH = "drench"
    CRACK_ARMOR = "crack_armor"
    STAGGER = "stagger"
    BLIND = "blind"
    SILENCE = "silence"
    ROOT = "root"
    FEAR = "fear"


class VillainStance(str, Enum):
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    PASSIVE = "passive"


class TrophyCategory(str, Enum):
    COMBAT = "combat"
    STEALTH = "stealth"
    SOCIAL = "social"
    PROGRESSION = "progression"
    ALIGNMENT = "alignment"


class TrophyTier(str, Enum):
    EARLY = "early"
    MID = "mid"
    LATE = "late"


class ReputationTier(str, Enum):
    HEROIC = "heroic"
    NEUTRAL = "neutral"
    ROGUE = "rogue"


class QuestStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

