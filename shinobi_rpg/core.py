from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Sequence, Set, Tuple


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


class JutsuType(str, Enum):
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
DECISION_OUTCOMES = {"kill", "charm", "stealth", "evasion"}
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
        "jutsu_type": JutsuType.WEAPON_STYLE,
        "status_effects": (StatusEffectType.BLEED, StatusEffectType.CRACK_ARMOR),
    },
    "General Voln": {
        "name": "Inferno Vortex",
        "category": MoveCategory.ATTACK,
        "affinities": (Affinity.FIRE,),
        "power_scale": 1.3,
        "jutsu_type": JutsuType.ELEMENTAL,
        "status_effects": (StatusEffectType.BURN, StatusEffectType.STAGGER),
    },
    "Admiral Neris": {
        "name": "Maelstrom Guard",
        "category": MoveCategory.DEFENSE,
        "affinities": (Affinity.WATER,),
        "power_scale": 1.08,
        "jutsu_type": JutsuType.BARRIER,
        "status_effects": (StatusEffectType.DRENCH, StatusEffectType.CHILL),
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


def _empty_affinity_scores() -> Dict[Affinity, int]:
    return {affinity: 0 for affinity in AFFINITY_ORDER}


def _reputation_tier_for(reputation: int) -> ReputationTier:
    if reputation <= ROGUE_THRESHOLD_MIN:
        return ReputationTier.ROGUE
    if reputation >= HEROIC_THRESHOLD_MIN:
        return ReputationTier.HEROIC
    return ReputationTier.NEUTRAL


@dataclass(frozen=True)
class Move:
    name: str
    category: MoveCategory
    affinities: Tuple[Affinity, ...]
    power_scale: float = 1.0
    jutsu_type: JutsuType = JutsuType.ELEMENTAL
    status_effects: Tuple[StatusEffectType, ...] = ()
    animation_profile: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if self.category != MoveCategory.ULTIMATE and len(self.affinities) != 1:
            raise ValueError("Non-ultimate moves must have exactly one affinity.")
        if self.category == MoveCategory.ULTIMATE and not self.affinities:
            raise ValueError("Ultimate moves must include at least one affinity.")


@dataclass(frozen=True)
class Weapon:
    name: str
    weapon_type: WeaponType
    play_style: str
    base_power: int
    status_effects: Tuple[StatusEffectType, ...] = ()


@dataclass(frozen=True)
class MoveSkin:
    skin_name: str
    base_move_name: str
    affinity: Affinity
    visual_theme: str
    animation_profile: Dict[str, str]


@dataclass(frozen=True)
class Skin:
    name: str
    stat_boosts: Dict[str, int]


@dataclass(frozen=True)
class Backstory:
    key: str
    title: str
    narrative_tags: Tuple[str, ...]
    reputation_bias: int = 0


@dataclass(frozen=True)
class ArcDefinition:
    key: str
    title: str
    tone: str
    stakes: str
    regions: Tuple[str, ...]
    era_band: str


@dataclass
class VillainProfile:
    name: str
    backstory: str
    signature_power: Move
    primary_affinity: Affinity = Affinity.FIRE
    role: str = "duelist"
    skinned_move_names: Dict[str, str] = field(default_factory=dict)
    ultimate_skin_name: str = ""
    aggression_score: int = 0
    stance: VillainStance = VillainStance.BALANCED
    decision_memory: Dict[str, int] = field(default_factory=dict)
    health_bar_color: str = "red"
    defeated: bool = False

    def apply_decision(self, decision_tag: str, intensity: int = 1) -> VillainStance:
        """Update villain temperament from player decisions over time."""
        normalized = decision_tag.strip().lower()
        self.decision_memory[normalized] = self.decision_memory.get(normalized, 0) + intensity
        role_bias = ROLE_STANCE_BIAS.get(self.role, 0)
        stance_delta = 0
        if normalized in {"kill", "aggressive", "betray"}:
            stance_delta = 2
        elif normalized in {"stealth", "evasion"}:
            stance_delta = 1 + (2 * role_bias)
        elif normalized in {"charm", "mercy", "diplomacy"}:
            stance_delta = -2 + role_bias
        self.aggression_score += stance_delta * intensity

        if self.aggression_score >= 4:
            self.stance = VillainStance.AGGRESSIVE
        elif self.aggression_score <= -3:
            self.stance = VillainStance.PASSIVE
        else:
            self.stance = VillainStance.BALANCED
        return self.stance


@dataclass(frozen=True)
class Trophy:
    key: str
    name: str
    description: str
    category: TrophyCategory
    tier: TrophyTier = TrophyTier.EARLY


@dataclass
class Quest:
    quest_id: str
    title: str
    objective: str
    stealth_required: bool
    reward_xp: int
    premise: str = ""
    choices: Tuple[str, ...] = field(default_factory=tuple)
    branch_outcomes: Dict[str, str] = field(default_factory=dict)
    rewards: Dict[str, Any] = field(default_factory=dict)
    follow_up_hook: str = ""
    villain_stance_impacts: Dict[str, int] = field(default_factory=dict)
    reputation_impacts: Dict[str, int] = field(default_factory=dict)
    trophy_hooks: Tuple[str, ...] = field(default_factory=tuple)


@dataclass
class Region:
    name: str
    village_hub: str
    enemies: List[str]
    allies: List[str]
    boss: str
    boss_rewards: Dict[str, str]
    arc_key: str = "political_war"
    tutorial_mechanics: Tuple[str, ...] = field(default_factory=tuple)
    encounter_table: List[str] = field(default_factory=list)
    cleared: bool = False


@dataclass
class PlayerStats:
    level: int = 1
    xp: int = 0
    power: int = 10
    defense: int = 10
    agility: int = 10
    focus: int = 10

    def gain_xp(self, amount: int) -> int:
        self.xp += amount
        levels_gained = 0
        while self.xp >= self.level * BASE_XP_PER_LEVEL:
            self.xp -= self.level * BASE_XP_PER_LEVEL
            self.level += 1
            self.power += 2
            self.defense += 2
            self.agility += 2
            self.focus += 2
            levels_gained += 1
        return levels_gained


@dataclass
class PlayerProfile:
    name: str
    affinity: Affinity
    stats: PlayerStats = field(default_factory=PlayerStats)
    reputation: int = 0
    unlocked_zones: List[str] = field(default_factory=lambda: ["village_hub"])
    unlocked_fast_travel_nodes: List[str] = field(default_factory=lambda: ["village_hub"])
    unlocked_skins: List[Skin] = field(default_factory=list)
    weapons: List[Weapon] = field(default_factory=list)
    reward_inventory: Dict[str, List[str]] = field(
        default_factory=lambda: {"weapon": [], "clothing": [], "move": []}
    )
    red_bar_power_claims: Dict[str, str] = field(default_factory=dict)
    moves_by_set: Dict[MoveCategory, List[Move]] = field(
        default_factory=lambda: {
            MoveCategory.ESCAPE: [],
            MoveCategory.ATTACK: [],
            MoveCategory.DEFENSE: [],
            MoveCategory.SUMMON: [],
            MoveCategory.ULTIMATE: [],
        }
    )
    unlocked_move_names: Set[str] = field(default_factory=set)
    selected_backstory: Backstory | None = None
    narrative_tags: Set[str] = field(default_factory=set)
    encounter_outcomes: Dict[str, int] = field(
        default_factory=lambda: {"kill": 0, "charm": 0, "stealth": 0, "evasion": 0}
    )
    trophies: Set[str] = field(default_factory=set)
    quest_log: Dict[str, QuestStatus] = field(default_factory=dict)
    ally_loyalty: Dict[str, int] = field(default_factory=dict)
    encounter_history: Dict[str, int] = field(default_factory=dict)
    credits: int = 100
    active_status_effects: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def choose_backstory(self, backstory: Backstory) -> None:
        self.selected_backstory = backstory
        self.narrative_tags.update(backstory.narrative_tags)
        if backstory.reputation_bias:
            self.update_reputation(backstory.reputation_bias)

    def record_encounter_outcome(
        self, outcome: Literal["kill", "charm", "stealth", "evasion"]
    ) -> None:
        if outcome not in DECISION_OUTCOMES:
            raise ValueError("Outcome must be kill, charm, stealth, or evasion.")
        self.encounter_outcomes[outcome] += 1

    def is_nonlethal_path_active(self) -> bool:
        return self.encounter_outcomes["kill"] == 0 and self.nonlethal_action_count() > 0

    def nonlethal_action_count(self) -> int:
        return (
            self.encounter_outcomes["charm"]
            + self.encounter_outcomes["stealth"]
            + self.encounter_outcomes["evasion"]
        )

    def dominant_encounter_outcome(self) -> str | None:
        ranked_outcomes = sorted(
            self.encounter_outcomes.items(),
            key=lambda item: (-item[1], item[0]),
        )
        if not ranked_outcomes or ranked_outcomes[0][1] <= 0:
            return None
        return ranked_outcomes[0][0]

    def current_reputation_tier(self) -> ReputationTier:
        return _reputation_tier_for(self.reputation)

    def add_move(self, move: Move, *, allow_cross_affinity: bool = False) -> None:
        move.validate()
        if not allow_cross_affinity and move.category != MoveCategory.ULTIMATE and (
            not move.affinities or move.affinities[0] != self.affinity
        ):
            raise ValueError("Non-ultimate moves must match player affinity.")
        self.moves_by_set[move.category].append(move)
        self.unlocked_move_names.add(move.name)

    def get_move(self, move_name: str) -> Move:
        if move_name not in self.unlocked_move_names:
            raise ValueError(f'Move "{move_name}" is not unlocked for this player.')
        for move_set in self.moves_by_set.values():
            for move in move_set:
                if move.name == move_name:
                    return move
        raise ValueError(f'Move "{move_name}" is not unlocked for this player.')

    def _clamp_status_effect(
        self, effect: StatusEffectType, *, duration: int, stacks: int
    ) -> Dict[str, int]:
        band = STATUS_EFFECT_BANDS[effect]
        return {
            "duration": max(band["duration_min"], min(duration, band["duration_max"])),
            "stacks": max(1, min(stacks, band["max_stacks"])),
        }

    def apply_status_effects(
        self, effects: Sequence[StatusEffectType], *, duration: int = 2, stacks: int = 1
    ) -> Dict[str, Dict[str, int]]:
        for effect in effects:
            clamped = self._clamp_status_effect(effect, duration=duration, stacks=stacks)
            self.active_status_effects[effect.value] = clamped
        return dict(self.active_status_effects)

    def resolve_combo(
        self, starter_move: str, link_move: str, finisher_move: str
    ) -> Dict[str, Any]:
        starter = self.get_move(starter_move)
        link = self.get_move(link_move)
        finisher = self.get_move(finisher_move)
        if starter.category == MoveCategory.ULTIMATE:
            raise ValueError("Starter move cannot be an ultimate.")
        if finisher.category != MoveCategory.ULTIMATE:
            raise ValueError("Finisher move must be an ultimate.")
        base_damage = int((self.stats.power + self.stats.focus) * finisher.power_scale)
        applied_bonus = {"label": "none", "damage_bonus": 0.0}
        for active_effect in starter.status_effects + link.status_effects:
            for finisher_affinity in finisher.affinities:
                bonus = COMBO_BONUSES.get((active_effect, finisher_affinity))
                if bonus and bonus["damage_bonus"] > applied_bonus["damage_bonus"]:
                    applied_bonus = bonus
        bonus_damage = int(base_damage * applied_bonus["damage_bonus"])
        total_damage = base_damage + bonus_damage
        return {
            "starter": starter.name,
            "link": link.name,
            "finisher": finisher.name,
            "base_damage": base_damage,
            "bonus_damage": bonus_damage,
            "total_damage": total_damage,
            "combo_bonus": applied_bonus["label"],
        }

    def execute_move(self, move_name: str, *, escape_difficulty: int = 6) -> Dict[str, Any]:
        """Execute an unlocked move and return deterministic MVP combat output.

        ``escape_difficulty`` is only used for Escape moves and ignored for
        Attack, Defense, and Ultimate categories.
        """
        move = self.get_move(move_name)
        if move.status_effects:
            self.apply_status_effects(move.status_effects)
        combat_physics = self._build_combat_physics(move)
        if move.category == MoveCategory.ATTACK:
            damage = int(self.stats.power * move.power_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "damage": damage,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
            }
        if move.category == MoveCategory.DEFENSE:
            guard = int(self.stats.defense * move.power_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "guard": guard,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
            }
        if move.category == MoveCategory.ESCAPE:
            escape_score = int(self.stats.agility * move.power_scale)
            escaped = escape_score >= escape_difficulty
            return {
                "move": move.name,
                "category": move.category.value,
                "escape_score": escape_score,
                "escaped": escaped,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
            }
        if move.category == MoveCategory.ULTIMATE:
            damage = int((self.stats.power + self.stats.focus) * move.power_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "damage": damage,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
            }
        if move.category == MoveCategory.SUMMON:
            summon_power = int((self.stats.focus + self.stats.defense) * move.power_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "summon_power": summon_power,
                "summon_type": move.jutsu_type.value,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
            }
        raise ValueError(f'Unsupported move category "{move.category.value}".')

    def _build_combat_physics(self, move: Move) -> Dict[str, Any]:
        impact_force = int((self.stats.power + self.stats.agility) * move.power_scale)
        bleed_stacks = self.active_status_effects.get(StatusEffectType.BLEED.value, {}).get("stacks", 0)
        blood_intensity = BLOOD_INTENSITY_BY_BLEED_STACK.get(
            min(max(int(bleed_stacks), 0), 3), BLOOD_INTENSITY_BY_BLEED_STACK[3]
        )
        stagger_window = max(1, int(round(move.power_scale * 2)))
        knockback = max(
            0,
            int(round((self.stats.power * move.power_scale) / 8))
            + (1 if StatusEffectType.STAGGER in move.status_effects else 0),
        )
        return {
            "impact_force": impact_force,
            "knockback": knockback,
            "stagger_window": stagger_window,
            "blood_intensity": blood_intensity,
            "blooded": blood_intensity != "none",
        }

    def resolve_block_parry(
        self,
        incoming_damage: int,
        *,
        base_guard_scale: float = 0.5,
        parry_difficulty: int = 6,
    ) -> Dict[str, Any]:
        """Resolve defensive block/parry output with a no-defense fallback.

        If multiple defense moves are unlocked, the highest ``power_scale`` move is
        selected to represent the strongest available defensive technique (ties break
        lexicographically by move name). The same defense scale is applied to both guard
        reduction and agility-based parry timing in this MVP model.
        """
        if incoming_damage < 0:
            raise ValueError("Incoming damage cannot be negative.")
        if base_guard_scale <= 0:
            raise ValueError("Base guard scale must be greater than zero.")
        if parry_difficulty < 0:
            raise ValueError("Parry difficulty cannot be negative.")

        defense_moves = self.moves_by_set[MoveCategory.DEFENSE]
        # Secondary move-name ordering makes equal-scale defensive choice deterministic.
        selected_move = (
            max(defense_moves, key=lambda move: (move.power_scale, move.name))
            if defense_moves
            else None
        )
        defense_scale = selected_move.power_scale if selected_move else base_guard_scale
        guard = int(self.stats.defense * defense_scale)
        parry_score = int(self.stats.agility * defense_scale)
        remaining_damage = max(incoming_damage - guard, 0)
        blocked_damage = incoming_damage - remaining_damage
        parried = parry_score >= parry_difficulty
        damage_taken = 0 if parried else remaining_damage

        return {
            "category": MoveCategory.DEFENSE.value,
            "move": selected_move.name if selected_move else None,
            "guard": guard,
            "parry_score": parry_score,
            "parried": parried,
            "blocked_damage": blocked_damage,
            "remaining_damage": remaining_damage,
            "damage_taken": damage_taken,
        }

    def update_reputation(self, delta: int) -> ReputationTier:
        self.reputation += delta
        tier = _reputation_tier_for(self.reputation)
        if tier == ReputationTier.ROGUE:
            if "black_market" not in self.unlocked_zones:
                self.unlocked_zones.append("black_market")
        return tier

    def unlock_fast_travel(self, node_name: str) -> None:
        if node_name not in self.unlocked_fast_travel_nodes:
            self.unlocked_fast_travel_nodes.append(node_name)

    def initialize_quest_log(self, quest_ids: Sequence[str]) -> None:
        if self.quest_log:
            return
        if quest_ids:
            self.quest_log[quest_ids[0]] = QuestStatus.ACTIVE

    def get_active_quest_id(self) -> str | None:
        return next(
            (quest_id for quest_id, status in self.quest_log.items() if status == QuestStatus.ACTIVE),
            None,
        )

    def set_quest_status(self, quest_id: str, status: QuestStatus) -> None:
        self.quest_log[quest_id] = status

    def adjust_ally_loyalty(self, ally_name: str, delta: int) -> int:
        current = self.ally_loyalty.get(ally_name, 0)
        updated = max(-100, min(100, current + delta))
        self.ally_loyalty[ally_name] = updated
        return updated

    def record_region_encounter(self, region_name: str) -> int:
        current = self.encounter_history.get(region_name, 0)
        updated = current + 1
        self.encounter_history[region_name] = updated
        return updated

    def earn_credits(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("Credit gain cannot be negative.")
        self.credits += amount
        return self.credits

    def spend_credits(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("Credit spend cannot be negative.")
        if amount > self.credits:
            raise ValueError("Insufficient credits.")
        self.credits -= amount
        return self.credits

    def grant_boss_reward(self, reward_type: str, reward_name: str) -> None:
        if reward_type not in self.reward_inventory:
            raise ValueError("Reward choice must be weapon, clothing, or move.")
        if reward_name in self.reward_inventory[reward_type]:
            raise ValueError(f'"{reward_name}" has already been granted for {reward_type}.')
        self.reward_inventory[reward_type].append(reward_name)

    def claim_red_bar_power(self, villain_name: str, move: Move) -> None:
        if villain_name in self.red_bar_power_claims:
            return
        self.red_bar_power_claims[villain_name] = move.name
        if move.name not in self.unlocked_move_names:
            self.add_move(move, allow_cross_affinity=True)

    def to_snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "affinity": self.affinity.value,
            "stats": {
                "level": self.stats.level,
                "xp": self.stats.xp,
                "power": self.stats.power,
                "defense": self.stats.defense,
                "agility": self.stats.agility,
                "focus": self.stats.focus,
            },
            "reputation": self.reputation,
            "unlocked_zones": list(self.unlocked_zones),
            "unlocked_fast_travel_nodes": list(self.unlocked_fast_travel_nodes),
            "unlocked_skins": [skin.name for skin in self.unlocked_skins],
            "weapons": [weapon.name for weapon in self.weapons],
            "reward_inventory": {key: list(values) for key, values in self.reward_inventory.items()},
            "red_bar_power_claims": dict(self.red_bar_power_claims),
            "moves_by_set": {
                category.value: [
                    {
                        "name": move.name,
                        "category": move.category.value,
                        "affinities": [affinity.value for affinity in move.affinities],
                        "power_scale": move.power_scale,
                        "jutsu_type": move.jutsu_type.value,
                        "status_effects": [effect.value for effect in move.status_effects],
                        "animation_profile": dict(move.animation_profile),
                    }
                    for move in moves
                ]
                for category, moves in self.moves_by_set.items()
            },
            "unlocked_move_names": sorted(self.unlocked_move_names),
            "selected_backstory": self.selected_backstory.key if self.selected_backstory else None,
            "narrative_tags": sorted(self.narrative_tags),
            "encounter_outcomes": dict(self.encounter_outcomes),
            "trophies": sorted(self.trophies),
            "quest_log": {quest_id: status.value for quest_id, status in self.quest_log.items()},
            "ally_loyalty": dict(self.ally_loyalty),
            "encounter_history": dict(self.encounter_history),
            "credits": self.credits,
            "active_status_effects": {
                effect_name: {
                    "duration": int(payload.get("duration", 0)),
                    "stacks": int(payload.get("stacks", 0)),
                }
                for effect_name, payload in self.active_status_effects.items()
            },
        }


@dataclass
class NinjaWorld:
    regions: List[Region]
    quests: List[Quest]
    allies: List[str]
    weapons: List[Weapon]
    skins: List[Skin]
    villains: List[VillainProfile]
    villain_behavior_rules: Dict[str, Dict[VillainStance, str]]
    player_backstories: List[Backstory]
    trophy_catalog: Dict[str, Trophy]
    arcs: List[ArcDefinition] = field(default_factory=list)
    era_timeline: List[Dict[str, Any]] = field(default_factory=list)
    ninjutsu_library: List[Move] = field(default_factory=list)
    shop_inventory: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    vault_historic_ninjas: List[dict] = field(default_factory=list)
    vault_meta_tapestry: List[Dict[str, Any]] = field(default_factory=list)
    active_run_tapestry: List[Dict[str, Any]] = field(default_factory=list)
    world_event_history: List[Dict[str, Any]] = field(default_factory=list)
    dynamic_region_chain: List[str] = field(default_factory=list)
    recent_boss_chains: List[List[str]] = field(default_factory=list)
    region_state: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    boss_availability: Dict[str, bool] = field(default_factory=dict)
    antagonist_candidates: List[str] = field(default_factory=list)
    antagonist_scoreboard: Dict[str, int] = field(default_factory=dict)
    antagonist_signal_log: Dict[str, List[str]] = field(default_factory=dict)
    selected_final_antagonist: Dict[str, Any] | None = None
    current_arc_key: str = "political_war"
    current_age: int = 16
    current_era_index: int = 0
    world_recovery_score: int = 0
    run_counter: int = 0
    latent_decision_seeds: Dict[str, int] = field(default_factory=dict)
    latent_echo_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.era_timeline:
            self.era_timeline = _seed_era_timeline()
        if not self.arcs:
            self.arcs = _seed_arcs()
        if not self.region_state:
            self.region_state = {
                region.name: {
                    "region": region.name,
                    "arc_key": region.arc_key,
                    "pressure": 0,
                    "recovery": 0,
                    "disasters": 0,
                    "rebuilds": 0,
                }
                for region in self.regions
            }
        if not self.boss_availability:
            self.boss_availability = {region.boss: True for region in self.regions}
        if not self.antagonist_candidates:
            allied_candidates = sorted(set(self.allies[:5]))
            villain_candidates = [villain.name for villain in self.villains]
            self.antagonist_candidates = villain_candidates + allied_candidates
        if not self.antagonist_scoreboard:
            self.antagonist_scoreboard = {name: 0 for name in self.antagonist_candidates}
        if not self.antagonist_signal_log:
            self.antagonist_signal_log = {name: [] for name in self.antagonist_candidates}
        if not self.dynamic_region_chain:
            self.dynamic_region_chain = [region.name for region in self.regions]

    def _current_era(self) -> Dict[str, Any]:
        timeline = self.era_timeline or _seed_era_timeline()
        bounded_index = min(max(self.current_era_index, 0), len(timeline) - 1)
        return timeline[bounded_index]

    def _arc_for_region(self, region_name: str) -> ArcDefinition | None:
        for arc in self.arcs:
            if region_name in arc.regions:
                return arc
        return None

    def _log_tapestry(
        self,
        *,
        event_type: str,
        label: str,
        causes: Sequence[str] | None = None,
        effects: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        entry = {
            "index": len(self.active_run_tapestry) + 1,
            "event_type": event_type,
            "label": label,
            "arc_key": self.current_arc_key,
            "era_key": self._current_era()["key"],
            "age": self.current_age,
            "causes": list(causes or []),
            "effects": dict(effects or {}),
        }
        self.active_run_tapestry.append(entry)
        return entry

    def _refresh_arc_and_era(self) -> None:
        cleared = sum(1 for region in self.regions if region.cleared)
        if cleared >= 3:
            self.current_era_index = min(2, len(self.era_timeline) - 1)
        elif cleared >= 1:
            self.current_era_index = min(1, len(self.era_timeline) - 1)
        else:
            self.current_era_index = 0
        self.current_age = 16 + len(self.world_event_history) + cleared

        arc_pressure: Dict[str, int] = {}
        for state in self.region_state.values():
            arc_key = str(state.get("arc_key", "political_war"))
            pressure = int(state.get("pressure", 0))
            recovery = int(state.get("recovery", 0))
            arc_pressure[arc_key] = arc_pressure.get(arc_key, 0) + pressure - recovery
        if arc_pressure:
            self.current_arc_key = sorted(arc_pressure.items(), key=lambda item: (-item[1], item[0]))[0][0]

    def _penalty_for_recent_boss_chain(self, chain: Sequence[str]) -> int:
        if not self.recent_boss_chains:
            return 0
        penalty = 0
        for prior in self.recent_boss_chains[-5:]:
            overlap = sum(1 for idx, boss in enumerate(chain) if idx < len(prior) and prior[idx] == boss)
            penalty += overlap
        return penalty

    def _schedule_dynamic_regions(self, player: PlayerProfile) -> List[str]:
        uncleared_regions = [region for region in self.regions if not region.cleared]
        if not uncleared_regions:
            self.dynamic_region_chain = []
            return []
        if not self.world_event_history:
            scheduled = [region.name for region in self.regions if not region.cleared]
            self.dynamic_region_chain = scheduled
            return scheduled

        base_signal = (
            player.reputation
            + player.nonlethal_action_count()
            + sum(player.ally_loyalty.values())
            + len(self.world_event_history)
        )
        region_scores: Dict[str, int] = {}
        for idx, region in enumerate(uncleared_regions):
            state = self.region_state.get(region.name, {})
            pressure = int(state.get("pressure", 0))
            recovery = int(state.get("recovery", 0))
            region_seed = sum(ord(ch) for ch in region.name)
            pseudo_random = (base_signal + region_seed + idx * 7) % 6
            availability_penalty = 0 if self.boss_availability.get(region.boss, True) else 10
            original_index = next((index for index, item in enumerate(self.regions) if item.name == region.name), idx)
            progression_anchor = -original_index * 3
            region_scores[region.name] = (
                pressure * 3
                - recovery
                + pseudo_random
                + progression_anchor
                - availability_penalty
            )

        ordered = sorted(uncleared_regions, key=lambda region: (-region_scores[region.name], region.name))
        scheduled = [region.name for region in ordered]

        if scheduled:
            opening_regions = {
                region.name
                for region in uncleared_regions
                if region.arc_key == "political_war"
            }
            if opening_regions and scheduled[0] not in opening_regions:
                scheduled = sorted(scheduled, key=lambda name: (name not in opening_regions, scheduled.index(name)))

        boss_chain = [self._find_region(name).boss for name in scheduled]
        if self._penalty_for_recent_boss_chain(boss_chain) >= max(2, len(boss_chain) - 1):
            scheduled = list(reversed(scheduled))

        self.dynamic_region_chain = scheduled
        return scheduled

    def _update_antagonist_scores(
        self,
        *,
        signal: str,
        intensity: int = 1,
        focal_points: Sequence[str] | None = None,
        causes: Sequence[str] | None = None,
    ) -> None:
        if focal_points:
            targets = [name for name in focal_points if name in self.antagonist_candidates]
            if not targets:
                targets = list(self.antagonist_candidates)
        else:
            targets = list(self.antagonist_candidates)
        for name in targets:
            self.antagonist_scoreboard[name] += intensity
            reason = signal if not causes else f"{signal}: {' -> '.join(causes)}"
            self.antagonist_signal_log[name].append(reason)

    def _resolve_final_antagonist(self) -> Dict[str, Any]:
        if not self.antagonist_scoreboard:
            self.selected_final_antagonist = {
                "name": None,
                "origin_story": "No antagonist pressure registered.",
                "score": 0,
                "signals": [],
            }
            return self.selected_final_antagonist

        ranked = sorted(self.antagonist_scoreboard.items(), key=lambda item: (-item[1], item[0]))
        winner, score = ranked[0]
        signals = self.antagonist_signal_log.get(winner, [])
        origin_story = (
            f"{winner} emerged through {'; '.join(signals[-3:])}."
            if signals
            else f"{winner} emerged from accumulating regional pressure."
        )
        self.selected_final_antagonist = {
            "name": winner,
            "origin_story": origin_story,
            "score": score,
            "signals": list(signals[-6:]),
        }
        return self.selected_final_antagonist

    def _plant_decision_seed(self, decision_tag: str, intensity: int = 1) -> None:
        """Silently accumulate a decision seed without triggering any immediate effect.

        Seeds are checked and fired by tick_latent_effects, which is called on
        significant player milestones rather than on every individual decision.
        Only tracked decision types (keys in DECISION_SEED_THRESHOLDS) accumulate.
        Raises ValueError if intensity is not a positive integer.
        """
        if intensity < 1:
            raise ValueError("Seed intensity must be a positive integer.")
        key = decision_tag.strip().lower()
        if key in DECISION_SEED_THRESHOLDS:
            self.latent_decision_seeds[key] = (
                self.latent_decision_seeds.get(key, 0) + intensity
            )

    def tick_latent_effects(self, player: PlayerProfile) -> List[Dict[str, Any]]:
        """Fire any accumulated decision seeds that have crossed their threshold.

        Called after quest completion or region clearing so that world consequences
        emerge organically from the player's pattern of play rather than immediately
        on each decision. Returns the list of echo records that fired.
        """
        fired: List[Dict[str, Any]] = []
        for seed_key, threshold in DECISION_SEED_THRESHOLDS.items():
            accumulated = self.latent_decision_seeds.get(seed_key, 0)
            if accumulated < threshold:
                continue
            echo_key = f"{seed_key}_echo"
            if echo_key not in LATENT_ECHO_LIBRARY:
                continue
            # Suppress if the immediately prior echo was the same type, preventing
            # the same world echo from dominating every consecutive milestone.
            recent_keys = [e.get("echo_key") for e in self.latent_echo_history[-1:]]
            if recent_keys == [echo_key]:
                continue
            echo = dict(LATENT_ECHO_LIBRARY[echo_key])
            # Drain the threshold portion; any remainder carries over.
            self.latent_decision_seeds[seed_key] = accumulated - threshold
            target_region = (
                self.dynamic_region_chain[0]
                if self.dynamic_region_chain
                else next(
                    (r.name for r in self.regions if not r.cleared),
                    self.regions[0].name,
                )
            )
            state = self.region_state.setdefault(
                target_region,
                {
                    "region": target_region,
                    "arc_key": "political_war",
                    "pressure": 0,
                    "recovery": 0,
                    "disasters": 0,
                    "rebuilds": 0,
                },
            )
            pressure_delta = int(echo.get("region_pressure", 0))
            recovery_delta = int(echo.get("recovery_delta", 0))
            state["pressure"] = max(0, int(state.get("pressure", 0)) + pressure_delta)
            state["recovery"] = max(0, int(state.get("recovery", 0)) + max(recovery_delta, 0))
            if pressure_delta > 0:
                state["disasters"] = int(state.get("disasters", 0)) + 1
            if recovery_delta > 0:
                state["rebuilds"] = int(state.get("rebuilds", 0)) + 1
            self.world_recovery_score += recovery_delta
            narrative_tag = str(echo.get("narrative_tag", ""))
            if narrative_tag:
                player.narrative_tags.add(narrative_tag)
            villain_signal = str(echo.get("villain_signal", seed_key))
            for villain in self.villains:
                villain.apply_decision(villain_signal, intensity=1)
            echo_record: Dict[str, Any] = {
                "echo_key": echo_key,
                "seed_key": seed_key,
                "label": echo["label"],
                "region": target_region,
                "narrative_tag": narrative_tag,
            }
            self.latent_echo_history.append(echo_record)
            self._log_tapestry(
                event_type="world_drift",
                label=echo["label"],
                causes=[f"latent:{seed_key}"],
                effects={
                    "echo_key": echo_key,
                    "region": target_region,
                    "pressure_delta": pressure_delta,
                    "recovery_delta": recovery_delta,
                    "narrative_tag": narrative_tag,
                },
            )
            fired.append(echo_record)
        if fired:
            self._refresh_arc_and_era()
            self._schedule_dynamic_regions(player)
        return fired

    def get_world_drift_signals(self) -> Dict[str, Any]:
        """Return accumulated drift indicators from the latent decision network.

        Returns visible=False until once three or more decision seeds have been planted,
        so the system stays undetectable during the first couple of choices and only
        surfaces once the world has started to genuinely respond to the player's pattern.
        """
        total_seeds = sum(self.latent_decision_seeds.values())
        if total_seeds < 3:
            return {
                "visible": False,
                "signals": [],
                "total_decision_weight": total_seeds,
                "dominant_pattern": None,
                "echo_count": 0,
            }
        dominant: Tuple[str, int] = max(
            self.latent_decision_seeds.items(),
            key=lambda item: item[1],
            default=("", 0),
        )
        return {
            "visible": True,
            "signals": [dict(e) for e in self.latent_echo_history[-5:]],
            "total_decision_weight": total_seeds,
            "dominant_pattern": dominant[0],
            "echo_count": len(self.latent_echo_history),
        }

    def trigger_world_event(
        self,
        player: PlayerProfile,
        *,
        event_key: str | None = None,
        causes: Sequence[str] | None = None,
    ) -> Dict[str, Any]:
        if event_key is None:
            keys = sorted(WORLD_EVENT_LIBRARY.keys())
            index = (len(self.world_event_history) + player.nonlethal_action_count() + abs(player.reputation)) % len(keys)
            event_key = keys[index]
        if event_key not in WORLD_EVENT_LIBRARY:
            raise ValueError(f'World event "{event_key}" is not recognized.')
        event = dict(WORLD_EVENT_LIBRARY[event_key])
        target_region = self.dynamic_region_chain[0] if self.dynamic_region_chain else next(
            (region.name for region in self.regions if not region.cleared),
            self.regions[0].name,
        )
        state = self.region_state.setdefault(
            target_region,
            {"region": target_region, "arc_key": "political_war", "pressure": 0, "recovery": 0, "disasters": 0, "rebuilds": 0},
        )
        state["pressure"] = max(0, int(state.get("pressure", 0)) + int(event.get("region_pressure", 0)))
        state["recovery"] = max(0, int(state.get("recovery", 0)) + max(int(event.get("recovery_delta", 0)), 0))
        if int(event.get("region_pressure", 0)) > 0:
            state["disasters"] = int(state.get("disasters", 0)) + 1
        if int(event.get("recovery_delta", 0)) > 0:
            state["rebuilds"] = int(state.get("rebuilds", 0)) + 1
        target_boss = self._find_region(target_region).boss
        pressure_value = int(state.get("pressure", 0))
        self.boss_availability[target_boss] = pressure_value < 4

        self.world_recovery_score += int(event.get("recovery_delta", 0))
        event_record = {
            "event_key": event_key,
            "label": event["label"],
            "region": target_region,
            "causes": list(causes or []),
            "effects": {
                "region_pressure": int(event.get("region_pressure", 0)),
                "recovery_delta": int(event.get("recovery_delta", 0)),
                "arc_bias": event.get("arc_bias"),
            },
        }
        self.world_event_history.append(event_record)

        stance_shift = str(event.get("stance_shift", "kill"))
        for villain in self.villains:
            villain.apply_decision(stance_shift, intensity=1)
        self._update_antagonist_scores(
            signal=f"world_event:{event_key}",
            intensity=max(1, int(event.get("region_pressure", 1))),
            focal_points=[self._find_region(target_region).boss, *self.allies[:2]],
            causes=causes,
        )

        if event_key == "rebuild_failure" and "tornado" in {entry["event_key"] for entry in self.world_event_history}:
            radicalized = self.allies[0] if self.allies else "Unknown Operative"
            self._update_antagonist_scores(
                signal="minor_event_escalation",
                intensity=4,
                focal_points=[radicalized],
                causes=["tornado", "hardship", "rebuild_failure", "radicalization"],
            )

        self._refresh_arc_and_era()
        self._schedule_dynamic_regions(player)
        self._log_tapestry(
            event_type="world_event",
            label=event["label"],
            causes=causes,
            effects={
                "event_key": event_key,
                "region": target_region,
                "region_pressure": int(event.get("region_pressure", 0)),
                "recovery_delta": int(event.get("recovery_delta", 0)),
            },
        )
        return event_record

    def clear_region(
        self,
        player: PlayerProfile,
        region_name: str,
        reward_choice: str,
    ) -> str:
        self._schedule_dynamic_regions(player)
        region_index = next((idx for idx, r in enumerate(self.regions) if r.name == region_name), -1)
        if region_index == -1:
            raise ValueError(f'Region "{region_name}" not found.')
        region = self.regions[region_index]
        if region.cleared:
            raise ValueError(f'Region "{region_name}" has already been cleared.')
        if self.dynamic_region_chain and self.dynamic_region_chain[0] != region_name:
            raise ValueError("Previous region must be cleared first.")
        if not self.boss_availability.get(region.boss, True):
            raise ValueError(f'Region "{region_name}" boss is currently unavailable due to world events.')
        if reward_choice not in region.boss_rewards:
            valid_choices = ", ".join(region.boss_rewards.keys())
            raise ValueError(
                f'Invalid reward choice "{reward_choice}" for region "{region_name}". '
                f"Valid choices: {valid_choices}."
            )

        region.cleared = True
        reward_name = region.boss_rewards[reward_choice]
        player.grant_boss_reward(reward_choice, reward_name)
        if reward_choice == "move":
            boss_move = _boss_exclusive_move_for(region.boss)
            player.add_move(boss_move, allow_cross_affinity=True)
        player.unlock_fast_travel(region.name)
        self.defeat_red_bar_ninja(player, region.boss)
        for ally in region.allies:
            player.adjust_ally_loyalty(ally, 1)
        self.region_state.setdefault(
            region.name,
            {"region": region.name, "arc_key": region.arc_key, "pressure": 0, "recovery": 0, "disasters": 0, "rebuilds": 0},
        )
        self.region_state[region.name]["recovery"] = int(self.region_state[region.name].get("recovery", 0)) + 2
        self.region_state[region.name]["pressure"] = max(
            0,
            int(self.region_state[region.name].get("pressure", 0)) - 1,
        )
        self.world_recovery_score += 1
        cleared_chain = [item.boss for item in self.regions if item.cleared]
        if len(cleared_chain) >= 2:
            self.recent_boss_chains.append(cleared_chain)
            self.recent_boss_chains = self.recent_boss_chains[-10:]
        self._update_antagonist_scores(
            signal="boss_outcome",
            intensity=2,
            focal_points=[region.boss],
            causes=[f"region_clear:{region.name}", f"reward:{reward_choice}"],
        )
        self._refresh_arc_and_era()
        self._schedule_dynamic_regions(player)
        self._resolve_final_antagonist()
        self._log_tapestry(
            event_type="boss_outcome",
            label=f"{region.boss} fell at {region.name}.",
            causes=[f"reward_choice:{reward_choice}"],
            effects={
                "region": region.name,
                "boss": region.boss,
                "reward": reward_name,
                "remaining_chain": list(self.dynamic_region_chain),
            },
        )
        self.tick_latent_effects(player)
        self.evaluate_trophies(player)
        return reward_name

    def archive_historic_ninja(self, player: PlayerProfile) -> None:
        run_signature = self.generate_run_signature(player)
        archived_tapestry = [dict(entry) for entry in self.active_run_tapestry]
        self.run_counter += 1
        self.vault_historic_ninjas.append(
            {
                "name": player.name,
                "affinity": player.affinity.value,
                "level": player.stats.level,
                "reputation": player.reputation,
                "backstory": player.selected_backstory.key if player.selected_backstory else None,
                "trophies": sorted(player.trophies),
                "nonlethal_path": player.is_nonlethal_path_active(),
                "credits": player.credits,
                "run_signature": run_signature,
                "living_tapestry": archived_tapestry,
            }
        )
        for entry in archived_tapestry:
            meta_entry = dict(entry)
            meta_entry["run_id"] = self.run_counter
            self.vault_meta_tapestry.append(meta_entry)
        self.active_run_tapestry = []

    def get_player_vault_history(self, player_name: str) -> List[Dict[str, Any]]:
        normalized_name = player_name.strip()
        if not normalized_name:
            raise ValueError("Player name cannot be empty.")
        return [
            dict(entry)
            for entry in self.vault_historic_ninjas
            if str(entry.get("name", "")).strip() == normalized_name
        ]

    def get_vault_replay_summary(self) -> Dict[str, Any]:
        if not self.vault_historic_ninjas:
            return {
                "total_runs": 0,
                "unique_ninjas": [],
                "nonlethal_runs": 0,
                "heroic_runs": 0,
                "rogue_runs": 0,
                "highest_level_run": None,
                "most_collected_trophies": [],
                "meta_tapestry_entries": 0,
                "run_signatures": [],
            }

        unique_ninjas: Set[str] = set()
        nonlethal_runs = 0
        heroic_runs = 0
        rogue_runs = 0
        highest_level_run: Dict[str, Any] | None = None
        trophy_counts: Dict[str, int] = {}

        for entry in self.vault_historic_ninjas:
            name = str(entry.get("name", "")).strip()
            if name:
                unique_ninjas.add(name)

            if bool(entry.get("nonlethal_path", False)):
                nonlethal_runs += 1

            reputation = int(entry.get("reputation", 0))
            if reputation >= HEROIC_THRESHOLD_MIN:
                heroic_runs += 1
            if reputation <= ROGUE_THRESHOLD_MIN:
                rogue_runs += 1

            level = int(entry.get("level", 0))
            if (
                highest_level_run is None
                or level > highest_level_run["level"]
                or (
                    level == highest_level_run["level"]
                    and name
                    and name < highest_level_run["name"]
                )
            ):
                highest_level_run = {
                    "name": name,
                    "affinity": entry.get("affinity"),
                    "level": level,
                    "backstory": entry.get("backstory"),
                    "trophies": list(entry.get("trophies", [])),
                }

            for trophy_key in entry.get("trophies", []):
                if not isinstance(trophy_key, str):
                    continue
                trophy_counts[trophy_key] = trophy_counts.get(trophy_key, 0) + 1

        most_collected_trophies = [
            {
                "key": key,
                "name": self.trophy_catalog[key].name if key in self.trophy_catalog else key,
                "category": (
                    self.trophy_catalog[key].category.value if key in self.trophy_catalog else "unknown"
                ),
                "earned_runs": count,
            }
            for key, count in sorted(trophy_counts.items(), key=lambda item: (-item[1], item[0]))
        ]

        return {
            "total_runs": len(self.vault_historic_ninjas),
            "unique_ninjas": sorted(unique_ninjas),
            "nonlethal_runs": nonlethal_runs,
            "heroic_runs": heroic_runs,
            "rogue_runs": rogue_runs,
            "highest_level_run": highest_level_run,
            "most_collected_trophies": most_collected_trophies,
            "meta_tapestry_entries": len(self.vault_meta_tapestry),
            "run_signatures": [
                dict(entry.get("run_signature", {}))
                for entry in self.vault_historic_ninjas
                if isinstance(entry.get("run_signature"), dict)
            ],
        }

    def get_villain_evolution_checkpoints(self) -> List[Dict[str, Any]]:
        checkpoints: List[Dict[str, Any]] = []
        for villain in self.villains:
            raw_pressure = sum(villain.decision_memory.values())
            pacification_index = sum(
                villain.decision_memory.get(key, 0) for key in ("charm", "mercy", "diplomacy")
            )
            pressure = max(raw_pressure - pacification_index, 0)
            if pressure >= 8:
                phase = "apex"
            elif pressure >= 4:
                phase = "escalation"
            else:
                phase = "opening"
            checkpoints.append(
                {
                    "villain": villain.name,
                    "phase": phase,
                    "pressure_index": pressure,
                    "raw_pressure": raw_pressure,
                    "pacification_index": pacification_index,
                    "stance": villain.stance.value,
                    "encounter_variant": self.villain_behavior_rules.get(villain.name, {}).get(villain.stance, ""),
                }
            )
        return checkpoints

    def apply_player_decision(self, player: PlayerProfile, decision_tag: str, intensity: int = 1) -> None:
        normalized = decision_tag.strip().lower()
        for villain in self.villains:
            villain.apply_decision(normalized, intensity=intensity)
        loyalty_delta = 0
        if normalized == "kill":
            loyalty_delta = -1
        elif normalized == "charm":
            loyalty_delta = 1
        if loyalty_delta:
            for ally in self.allies:
                player.adjust_ally_loyalty(ally, loyalty_delta)
        if normalized in DECISION_OUTCOMES:
            player.record_encounter_outcome(normalized)
        self._update_antagonist_scores(
            signal=f"decision:{normalized}",
            intensity=max(1, intensity),
            focal_points=[villain.name for villain in self.villains[:3]],
            causes=[normalized],
        )
        if normalized in {"kill", "betray"}:
            self.world_recovery_score -= 1
        elif normalized in {"charm", "stealth", "evasion"}:
            self.world_recovery_score += 1
        self._refresh_arc_and_era()
        self._schedule_dynamic_regions(player)
        self._resolve_final_antagonist()
        self._log_tapestry(
            event_type="major_choice",
            label=f"Player choice registered: {normalized}.",
            causes=[normalized],
            effects={
                "intensity": intensity,
                "reputation": player.reputation,
                "nonlethal_path": player.is_nonlethal_path_active(),
            },
        )
        self.evaluate_trophies(player)
        self._plant_decision_seed(normalized, intensity)

    def _find_villain(self, name: str) -> VillainProfile:
        villain = next((v for v in self.villains if v.name == name), None)
        if not villain:
            raise ValueError(f'Villain "{name}" not found.')
        return villain

    def _find_region(self, region_name: str) -> Region:
        region = next((r for r in self.regions if r.name == region_name), None)
        if not region:
            raise ValueError(f'Region "{region_name}" not found.')
        return region

    def get_ninjutsu_catalog(
        self, *, affinity: Affinity | None = None, jutsu_type: JutsuType | None = None
    ) -> List[Dict[str, Any]]:
        moves = self.ninjutsu_library
        if affinity is not None:
            moves = [move for move in moves if affinity in move.affinities]
        if jutsu_type is not None:
            moves = [move for move in moves if move.jutsu_type == jutsu_type]
        return [
            {
                "name": move.name,
                "category": move.category.value,
                "affinities": [affinity.value for affinity in move.affinities],
                "jutsu_type": move.jutsu_type.value,
                "status_effects": [effect.value for effect in move.status_effects],
                "animation_profile": dict(move.animation_profile),
            }
            for move in moves
        ]

    def get_move_animation_preview(self, move_name: str) -> Dict[str, Any]:
        move = next((item for item in self.ninjutsu_library if item.name == move_name), None)
        if not move:
            raise ValueError(f'Move "{move_name}" not found in ninjutsu catalog.')
        return {
            "move": move.name,
            "affinities": [affinity.value for affinity in move.affinities],
            "animation_profile": dict(move.animation_profile),
            "skill_physics": self._build_skill_physics(move),
        }

    def preview_affinity_combo_animation(
        self, starter_move: str, link_move: str, finisher_move: str
    ) -> Dict[str, Any]:
        staged = []
        for beat, move_name in enumerate((starter_move, link_move, finisher_move), start=1):
            move = next((item for item in self.ninjutsu_library if item.name == move_name), None)
            if not move:
                raise ValueError(f'Move "{move_name}" not found in ninjutsu catalog.')
            staged.append(
                {
                    "beat": beat,
                    "move": move.name,
                    "category": move.category.value,
                    "affinities": [affinity.value for affinity in move.affinities],
                    "startup": move.animation_profile.get("startup", ""),
                    "travel": move.animation_profile.get("travel", ""),
                    "hit": move.animation_profile.get("hit", ""),
                    "recovery": move.animation_profile.get("recovery", ""),
                    "physics": self._build_skill_physics(move),
                }
            )
        return {"combo_path": staged}

    def _build_skill_physics(self, move: Move) -> Dict[str, Any]:
        blood_scale = 0
        if StatusEffectType.BLEED in move.status_effects:
            blood_scale = 2
        elif StatusEffectType.BURN in move.status_effects:
            blood_scale = 1
        intensity = BLOOD_INTENSITY_BY_BLEED_STACK.get(blood_scale, "none")
        return {
            "impact_class": "heavy" if move.power_scale >= 1.2 else "medium" if move.power_scale >= 1.0 else "light",
            "launch_force": int(round(move.power_scale * 10)),
            "recovery_frames": max(6, int(round(12 * move.power_scale))),
            "blood_intensity": intensity,
        }

    def defeat_red_bar_ninja(self, player: PlayerProfile, villain_name: str) -> Dict[str, Any]:
        villain = self._find_villain(villain_name)
        if villain.health_bar_color.lower() != "red":
            raise ValueError(f'Villain "{villain_name}" is not a red-bar target.')
        already_defeated = villain.defeated
        villain.defeated = True
        player.claim_red_bar_power(villain.name, villain.signature_power)
        return {
            "villain": villain.name,
            "claimed_power": villain.signature_power.name,
            "already_defeated": already_defeated,
        }

    def resolve_quest_branch(self, player: PlayerProfile, quest_id: str) -> Dict[str, Any]:
        quest = next((q for q in self.quests if q.quest_id == quest_id), None)
        if not quest:
            raise ValueError(f'Quest "{quest_id}" not found.')

        if not quest.branch_outcomes:
            return {
                "quest_id": quest.quest_id,
                "title": quest.title,
                "branch_key": "default",
                "outcome": quest.objective,
                "premise": quest.premise or quest.objective,
                "objective": quest.objective,
                "choices": list(quest.choices),
                "rewards": dict(quest.rewards),
                "follow_up_hook": quest.follow_up_hook,
                "villain_stance_impacts": dict(quest.villain_stance_impacts),
                "reputation_impacts": dict(quest.reputation_impacts),
                "trophy_hooks": list(quest.trophy_hooks),
            }

        branch_key = self._resolve_branch_key(player, quest.branch_outcomes)

        outcome = quest.branch_outcomes.get(branch_key) or quest.branch_outcomes.get(
            "default", quest.objective
        )
        return {
            "quest_id": quest.quest_id,
            "title": quest.title,
            "branch_key": branch_key,
            "outcome": outcome,
            "premise": quest.premise or quest.objective,
            "objective": quest.objective,
            "choices": list(quest.choices),
            "rewards": dict(quest.rewards),
            "follow_up_hook": quest.follow_up_hook,
            "villain_stance_impacts": dict(quest.villain_stance_impacts),
            "reputation_impacts": dict(quest.reputation_impacts),
            "trophy_hooks": list(quest.trophy_hooks),
        }

    def start_quest(self, player: PlayerProfile, quest_id: str) -> Dict[str, Any]:
        if not any(q.quest_id == quest_id for q in self.quests):
            raise ValueError(f'Quest "{quest_id}" not found.')
        if not player.quest_log:
            player.initialize_quest_log([quest.quest_id for quest in self.quests])

        quest_index = next(idx for idx, quest in enumerate(self.quests) if quest.quest_id == quest_id)
        if quest_index > 0:
            previous_quest = self.quests[quest_index - 1].quest_id
            if player.quest_log.get(previous_quest) != QuestStatus.COMPLETED:
                raise ValueError("Previous quest must be completed first.")

        active_quest_id = player.get_active_quest_id()
        if active_quest_id and active_quest_id != quest_id:
            raise ValueError("Another quest is already active.")

        if player.quest_log.get(quest_id) == QuestStatus.COMPLETED:
            raise ValueError(f'Quest "{quest_id}" has already been completed.')
        player.set_quest_status(quest_id, QuestStatus.ACTIVE)
        return self.resolve_quest_branch(player, quest_id)

    def complete_quest(self, player: PlayerProfile, quest_id: str) -> Dict[str, Any]:
        quest = next((q for q in self.quests if q.quest_id == quest_id), None)
        if not quest:
            raise ValueError(f'Quest "{quest_id}" not found.')
        if player.quest_log.get(quest_id) != QuestStatus.ACTIVE:
            raise ValueError(f'Quest "{quest_id}" must be active before completion.')

        player.set_quest_status(quest_id, QuestStatus.COMPLETED)
        levels_gained = player.stats.gain_xp(quest.reward_xp)
        credit_reward = QUEST_CREDIT_REWARD_BASE + (max(player.stats.level - 1, 0) * QUEST_CREDIT_REWARD_STEP)
        player.earn_credits(credit_reward)

        for ally in self.allies:
            player.adjust_ally_loyalty(ally, 1)

        quest_index = next(idx for idx, q in enumerate(self.quests) if q.quest_id == quest_id)
        if quest_index + 1 < len(self.quests):
            next_quest_id = self.quests[quest_index + 1].quest_id
            if player.quest_log.get(next_quest_id) != QuestStatus.COMPLETED:
                player.set_quest_status(next_quest_id, QuestStatus.ACTIVE)

        self._refresh_arc_and_era()
        self._schedule_dynamic_regions(player)
        self._update_antagonist_scores(
            signal="quest_completion",
            intensity=1,
            focal_points=[self.villains[0].name, *self.allies[:1]],
            causes=[quest_id],
        )
        self._log_tapestry(
            event_type="rebuild",
            label=f"Quest {quest_id} completed.",
            causes=[quest_id],
            effects={"credit_reward": credit_reward, "levels_gained": levels_gained},
        )
        if quest_id in {"Q3", "Q5", "Q7"}:
            self.trigger_world_event(player, causes=[f"quest:{quest_id}"])

        self.tick_latent_effects(player)
        self.evaluate_trophies(player)
        return {
            "quest_id": quest.quest_id,
            "reward_xp": quest.reward_xp,
            "levels_gained": levels_gained,
            "credit_reward": credit_reward,
            "new_balance": player.credits,
        }

    def fail_quest(self, player: PlayerProfile, quest_id: str) -> None:
        if not any(q.quest_id == quest_id for q in self.quests):
            raise ValueError(f'Quest "{quest_id}" not found.')
        if player.quest_log.get(quest_id) != QuestStatus.ACTIVE:
            raise ValueError(f'Quest "{quest_id}" must be active before failing.')
        player.set_quest_status(quest_id, QuestStatus.FAILED)
        for ally in self.allies:
            player.adjust_ally_loyalty(ally, -1)
        self._update_antagonist_scores(
            signal="quest_failure",
            intensity=2,
            focal_points=self.allies[:2],
            causes=[quest_id],
        )
        self._log_tapestry(
            event_type="betrayal",
            label=f"Quest {quest_id} failed.",
            causes=[quest_id],
            effects={"loyalty_impact": -1},
        )

    def _resolve_branch_key(self, player: PlayerProfile, branch_outcomes: Dict[str, str]) -> str:
        """Resolve branch precedence: backstory, path states, narrative tags, then default.

        Narrative tags are checked in alphabetical order to keep matching deterministic.
        """
        if player.selected_backstory and player.selected_backstory.key in branch_outcomes:
            return player.selected_backstory.key
        if player.is_nonlethal_path_active() and "nonlethal_path" in branch_outcomes:
            return "nonlethal_path"
        dominant_outcome = player.dominant_encounter_outcome()
        if dominant_outcome:
            tactical_path_key = f"{dominant_outcome}_path"
            if tactical_path_key in branch_outcomes:
                return tactical_path_key
        if player.current_reputation_tier() == ReputationTier.HEROIC and "heroic_path" in branch_outcomes:
            return "heroic_path"
        if player.current_reputation_tier() == ReputationTier.ROGUE and "rogue_path" in branch_outcomes:
            return "rogue_path"
        for tag in sorted(player.narrative_tags):
            if tag in branch_outcomes:
                return tag
        return "default"

    def get_region_boss_behavior(self, region_name: str, player: PlayerProfile) -> Dict[str, Any]:
        region = self._find_region(region_name)
        villain = self._find_villain(region.boss)
        behavior_by_stance = self.villain_behavior_rules.get(villain.name, {})
        behavior = behavior_by_stance.get(villain.stance, "Unpredictable tactics.")
        if "pacifism" in player.narrative_tags:
            behavior = f"{behavior} This boss shows small restraint toward pacifist choices."
        return {
            "region": region.name,
            "boss": villain.name,
            "stance": villain.stance.value,
            "behavior": behavior,
            "decision_memory": dict(villain.decision_memory),
            "tutorial_mechanics": list(region.tutorial_mechanics),
        }

    def get_dynamic_arc_schedule(self, player: PlayerProfile) -> Dict[str, Any]:
        scheduled = self._schedule_dynamic_regions(player)
        return {
            "current_arc_key": self.current_arc_key,
            "era": dict(self._current_era()),
            "scheduled_regions": list(scheduled),
            "scheduled_bosses": [self._find_region(region_name).boss for region_name in scheduled],
            "boss_availability": dict(self.boss_availability),
        }

    def get_final_antagonist_projection(self) -> Dict[str, Any]:
        return self._resolve_final_antagonist()

    def resolve_region_encounter(self, player: PlayerProfile, region_name: str) -> Dict[str, Any]:
        region = self._find_region(region_name)
        encounter_pool = region.encounter_table if region.encounter_table else region.enemies
        if not encounter_pool:
            raise ValueError(f'Region "{region_name}" has no encounters configured.')
        encounter_index = player.encounter_history.get(region_name, 0) % len(encounter_pool)
        encounter = encounter_pool[encounter_index]
        encounter_count = player.record_region_encounter(region_name)
        return {
            "region": region_name,
            "encounter": encounter,
            "encounter_index": encounter_index,
            "times_seen": encounter_count,
        }

    def get_shop_inventory(self, player: PlayerProfile) -> List[Dict[str, Any]]:
        can_access_black_market = "black_market" in player.unlocked_zones
        regions_cleared = sum(1 for region in self.regions if region.cleared)
        visible_items = []
        for item_key, item in self.shop_inventory.items():
            if item.get("requires_black_market") and not can_access_black_market:
                continue
            rep_min = item.get("min_reputation")
            rep_max = item.get("max_reputation")
            if rep_min is not None and player.reputation < rep_min:
                continue
            if rep_max is not None and player.reputation > rep_max:
                continue
            price = int(item.get("price", 0))
            if (
                player.current_reputation_tier() == ReputationTier.ROGUE
                and item.get("requires_black_market")
            ):
                price = max(1, int(round(price * (100 - ROGUE_SHOP_DISCOUNT_PERCENT) / 100)))
            if item.get("requires_nonlethal") and not player.is_nonlethal_path_active():
                continue
            if player.nonlethal_action_count() < int(item.get("min_nonlethal_actions", 0)):
                continue
            if (
                item.get("requires_world_clear_nonlethal")
                and (
                    not player.is_nonlethal_path_active()
                    or regions_cleared < len(self.regions)
                )
            ):
                continue
            visible_items.append(
                {
                    "key": item_key,
                    "name": item.get("name", item_key),
                    "reward_type": item.get("reward_type"),
                    "reward_name": item.get("reward_name"),
                    "price": price,
                }
            )
        return visible_items

    def purchase_shop_item(self, player: PlayerProfile, item_key: str) -> Dict[str, Any]:
        inventory = {item["key"]: item for item in self.get_shop_inventory(player)}
        if item_key not in inventory:
            raise ValueError(f'Item "{item_key}" is not available for this player.')
        item = inventory[item_key]
        player.spend_credits(item["price"])
        player.grant_boss_reward(item["reward_type"], item["reward_name"])
        return {
            "item_key": item_key,
            "price": item["price"],
            "remaining_credits": player.credits,
        }

    def evaluate_trophies(self, player: PlayerProfile) -> Set[str]:
        newly_awarded: Set[str] = set()

        def _award(trophy_key: str) -> None:
            if trophy_key in self.trophy_catalog and trophy_key not in player.trophies:
                player.trophies.add(trophy_key)
                newly_awarded.add(trophy_key)

        if player.encounter_outcomes["kill"] > 0:
            _award(TROPHY_FIRST_STRIKE)
        if player.encounter_outcomes["stealth"] >= STEALTH_TROPHY_BASE_THRESHOLD:
            _award(TROPHY_GHOST_STEP)
        if player.encounter_outcomes["charm"] >= CHARM_TROPHY_BASE_THRESHOLD:
            _award(TROPHY_SILVER_TONGUE)
        if player.encounter_outcomes["evasion"] >= EVASION_TROPHY_THRESHOLD:
            _award(TROPHY_WINDWALK_SURVIVOR)
        if player.encounter_outcomes["stealth"] >= STEALTH_TROPHY_ADVANCED_THRESHOLD:
            _award(TROPHY_VEIL_MASTER)
        if player.encounter_outcomes["charm"] >= CHARM_TROPHY_ADVANCED_THRESHOLD:
            _award(TROPHY_DIPLOMAT_SUPREME)
        if player.is_nonlethal_path_active() and player.nonlethal_action_count() >= PACIFIST_TROPHY_ACTIONS_THRESHOLD:
            _award(TROPHY_PACIFIST_SHADOW)
        if player.encounter_outcomes["stealth"] >= STEALTH_TROPHY_MASTER_THRESHOLD:
            _award(TROPHY_PHANTOM_VEIL)
        if player.encounter_outcomes["charm"] >= CHARM_TROPHY_MASTER_THRESHOLD:
            _award(TROPHY_HARMONY_VOICE)
        if player.encounter_outcomes["evasion"] >= EVASION_TROPHY_MASTER_THRESHOLD:
            _award(TROPHY_UNTOUCHABLE_GHOST)
        if player.is_nonlethal_path_active() and all(
            player.encounter_outcomes[action] >= NONLETHAL_STYLE_BALANCE_THRESHOLD
            for action in ("charm", "stealth", "evasion")
        ):
            _award(TROPHY_TRINITY_OPERATOR)
        if player.selected_backstory:
            _award(TROPHY_ORIGIN_AWAKENED)
        cleared_regions = sum(1 for region in self.regions if region.cleared)
        if cleared_regions >= 1:
            _award(TROPHY_FIRST_BLOODLINE_VICTORY)
        if cleared_regions >= len(self.regions):
            _award(TROPHY_WORLD_WALKER)
        if player.is_nonlethal_path_active() and cleared_regions >= len(self.regions):
            _award(TROPHY_SILENT_LEGEND)
        if player.reputation <= ROGUE_THRESHOLD_MIN:
            _award(TROPHY_ROGUE_ASCENDANT)
        if player.reputation >= HEROIC_THRESHOLD_MIN:
            _award(TROPHY_HEROIC_CREST)
        if (
            player.current_reputation_tier() == ReputationTier.HEROIC
            and player.encounter_outcomes["charm"] >= CHARM_TROPHY_BASE_THRESHOLD
        ):
            _award(TROPHY_PEACEKEEPER_EMBLEM)
        if player.is_nonlethal_path_active() and all(
            player.quest_log.get(quest.quest_id) == QuestStatus.COMPLETED for quest in self.quests
        ):
            _award(TROPHY_MERCY_CROWN)

        # Combat milestone trophies
        if player.encounter_outcomes["kill"] >= KILL_TROPHY_BASE_THRESHOLD:
            _award(TROPHY_BATTLE_HARDENED)
        if player.encounter_outcomes["kill"] >= KILL_TROPHY_ADVANCED_THRESHOLD:
            _award(TROPHY_WAR_VETERAN)
        if player.encounter_outcomes["kill"] >= KILL_TROPHY_ELITE_THRESHOLD:
            _award(TROPHY_CRIMSON_REAPER)
        if player.encounter_outcomes["kill"] >= KILL_TROPHY_MASTER_THRESHOLD:
            _award(TROPHY_APEX_PREDATOR)

        # Level progression trophies
        if player.stats.level >= LEVEL_TROPHY_BASE_THRESHOLD:
            _award(TROPHY_RISING_NINJA)
        if player.stats.level >= LEVEL_TROPHY_ADVANCED_THRESHOLD:
            _award(TROPHY_SEASONED_NINJA)

        # Ally loyalty trophy
        high_loyalty_count = sum(
            1
            for loyalty in player.ally_loyalty.values()
            if loyalty >= ALLY_LOYALTY_TROPHY_THRESHOLD
        )
        if high_loyalty_count >= ALLY_LOYALTY_TROPHY_COUNT:
            _award(TROPHY_LOYAL_BONDS)

        # Villain slayer: all red-bar villains defeated
        if self.villains and all(villain.defeated for villain in self.villains):
            _award(TROPHY_VILLAIN_SLAYER)

        # Quest master: complete all quests (any run style)
        if self.quests and all(
            player.quest_log.get(quest.quest_id) == QuestStatus.COMPLETED for quest in self.quests
        ):
            _award(TROPHY_QUESTMASTER)

        # Backstory world-clear trophies
        if cleared_regions >= len(self.regions) and player.selected_backstory:
            if player.selected_backstory.key == "exiled_heir":
                _award(TROPHY_SHADOW_HEIR)
            elif player.selected_backstory.key == "street_ghost":
                _award(TROPHY_GHOST_SOVEREIGN)
            elif player.selected_backstory.key == "wandering_monk":
                _award(TROPHY_MONK_ASCENDANT)

        return newly_awarded

    def get_living_tapestry_delta(self) -> Dict[str, Any]:
        current_counts: Dict[str, int] = {}
        prior_counts: Dict[str, int] = {}
        for entry in self.active_run_tapestry:
            key = str(entry.get("event_type", "unknown"))
            current_counts[key] = current_counts.get(key, 0) + 1
        for entry in self.vault_meta_tapestry:
            key = str(entry.get("event_type", "unknown"))
            prior_counts[key] = prior_counts.get(key, 0) + 1
        differences = []
        for key in sorted(set(current_counts) | set(prior_counts)):
            current = current_counts.get(key, 0)
            prior_avg = 0
            if self.vault_historic_ninjas:
                prior_avg = int(round(prior_counts.get(key, 0) / len(self.vault_historic_ninjas)))
            differences.append(
                {
                    "event_type": key,
                    "current_run": current,
                    "prior_average": prior_avg,
                    "delta": current - prior_avg,
                }
            )
        return {"event_differences": differences}

    def generate_run_signature(self, player: PlayerProfile) -> Dict[str, Any]:
        arc_counts: Dict[str, int] = {}
        for entry in self.active_run_tapestry:
            arc_key = str(entry.get("arc_key", "political_war"))
            arc_counts[arc_key] = arc_counts.get(arc_key, 0) + 1
        dominant_arc = None
        if arc_counts:
            dominant_arc = sorted(arc_counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
        final_antagonist = self._resolve_final_antagonist()
        critical_events = [
            f'{item.get("event_type")}::{item.get("label")}'
            for item in self.active_run_tapestry[-6:]
        ]
        return {
            "dominant_arc_path": dominant_arc or self.current_arc_key,
            "final_antagonist_origin_story": final_antagonist.get("origin_story"),
            "world_recovery_decay_score": self.world_recovery_score,
            "critical_event_chain": critical_events,
            "era_endpoint": self._current_era().get("key"),
            "age_endpoint": self.current_age,
            "nonlethal_signature": player.is_nonlethal_path_active(),
        }

    def generate_playthrough_summary(self, player: PlayerProfile) -> Dict[str, Any]:
        self._refresh_arc_and_era()
        self._schedule_dynamic_regions(player)
        final_antagonist = self._resolve_final_antagonist()
        trophy_details = [
            {
                "key": key,
                "name": self.trophy_catalog[key].name,
                "category": self.trophy_catalog[key].category.value,
                "tier": self.trophy_catalog[key].tier.value,
            }
            for key in sorted(player.trophies)
            if key in self.trophy_catalog
        ]
        villain_states = {villain.name: villain.stance.value for villain in self.villains}
        villain_memories = {villain.name: dict(villain.decision_memory) for villain in self.villains}
        red_bar_progress = {
            villain.name: {
                "defeated": villain.defeated,
                "signature_power": villain.signature_power.name,
            }
            for villain in self.villains
            if villain.health_bar_color.lower() == "red"
        }
        return {
            "player_name": player.name,
            "affinity": player.affinity.value,
            "backstory": player.selected_backstory.title if player.selected_backstory else None,
            "reputation": player.reputation,
            "reputation_tier": player.current_reputation_tier().value,
            "nonlethal_path": player.is_nonlethal_path_active(),
            "encounter_outcomes": dict(player.encounter_outcomes),
            "cleared_regions": [region.name for region in self.regions if region.cleared],
            "villain_stances": villain_states,
            "villain_decision_memory": villain_memories,
            "villain_kits": [
                {
                    "name": villain.name,
                    "role": villain.role,
                    "primary_affinity": villain.primary_affinity.value,
                    "signature": villain.signature_power.name,
                    "skinned_moves": dict(villain.skinned_move_names),
                    "ultimate_skin": villain.ultimate_skin_name,
                }
                for villain in self.villains
            ],
            "red_bar_power_claims": dict(player.red_bar_power_claims),
            "red_bar_progress": red_bar_progress,
            "quest_log": {quest_id: status.value for quest_id, status in player.quest_log.items()},
            "ally_loyalty": dict(player.ally_loyalty),
            "credits": player.credits,
            "kill_counter": {
                "total_kills": player.encounter_outcomes["kill"],
                "next_milestones": [
                    {
                        "trophy_key": trophy_key,
                        "target": target,
                        "remaining": max(target - player.encounter_outcomes["kill"], 0),
                    }
                    for trophy_key, target in (
                        (TROPHY_BATTLE_HARDENED, KILL_TROPHY_BASE_THRESHOLD),
                        (TROPHY_WAR_VETERAN, KILL_TROPHY_ADVANCED_THRESHOLD),
                        (TROPHY_CRIMSON_REAPER, KILL_TROPHY_ELITE_THRESHOLD),
                        (TROPHY_APEX_PREDATOR, KILL_TROPHY_MASTER_THRESHOLD),
                    )
                    if trophy_key not in player.trophies
                ],
            },
            "trophies": trophy_details,
            "trophy_progress": self.get_trophy_progress(player),
            "villain_evolution": self.get_villain_evolution_checkpoints(),
            "arc_state": {
                "current_arc_key": self.current_arc_key,
                "scheduled_regions": list(self.dynamic_region_chain),
                "era": dict(self._current_era()),
                "age": self.current_age,
            },
            "living_tapestry": {
                "active_run_entries": [dict(entry) for entry in self.active_run_tapestry],
                "vault_meta_entries": len(self.vault_meta_tapestry),
                "delta_vs_prior_runs": self.get_living_tapestry_delta()["event_differences"],
            },
            "world_events": [dict(entry) for entry in self.world_event_history],
            "final_antagonist": dict(final_antagonist),
            "run_signature_preview": self.generate_run_signature(player),
        }

    def generate_replay_hub_report(self, player: PlayerProfile) -> Dict[str, Any]:
        return {
            "active_run": self.generate_playthrough_summary(player),
            "vault_overview": self.get_vault_replay_summary(),
            "player_archive_history": self.get_player_vault_history(player.name),
            "living_tapestry_delta": self.get_living_tapestry_delta(),
        }

    def get_trophy_progress(self, player: PlayerProfile) -> List[Dict[str, Any]]:
        progress = []
        cleared_regions = sum(1 for region in self.regions if region.cleared)
        trophy_targets = {
            TROPHY_GHOST_STEP: ("stealth", STEALTH_TROPHY_BASE_THRESHOLD),
            TROPHY_VEIL_MASTER: ("stealth", STEALTH_TROPHY_ADVANCED_THRESHOLD),
            TROPHY_SILVER_TONGUE: ("charm", CHARM_TROPHY_BASE_THRESHOLD),
            TROPHY_DIPLOMAT_SUPREME: ("charm", CHARM_TROPHY_ADVANCED_THRESHOLD),
            TROPHY_WINDWALK_SURVIVOR: ("evasion", EVASION_TROPHY_THRESHOLD),
            TROPHY_PACIFIST_SHADOW: ("nonlethal_actions", PACIFIST_TROPHY_ACTIONS_THRESHOLD),
            TROPHY_PHANTOM_VEIL: ("stealth", STEALTH_TROPHY_MASTER_THRESHOLD),
            TROPHY_HARMONY_VOICE: ("charm", CHARM_TROPHY_MASTER_THRESHOLD),
            TROPHY_UNTOUCHABLE_GHOST: ("evasion", EVASION_TROPHY_MASTER_THRESHOLD),
            TROPHY_TRINITY_OPERATOR: ("balanced_nonlethal", NONLETHAL_STYLE_BALANCE_THRESHOLD),
            TROPHY_FIRST_BLOODLINE_VICTORY: ("regions_cleared", 1),
            TROPHY_WORLD_WALKER: ("regions_cleared", len(self.regions)),
            TROPHY_SILENT_LEGEND: ("regions_cleared", len(self.regions)),
            TROPHY_MERCY_CROWN: ("completed_quests", len(self.quests)),
            TROPHY_BATTLE_HARDENED: ("kill", KILL_TROPHY_BASE_THRESHOLD),
            TROPHY_WAR_VETERAN: ("kill", KILL_TROPHY_ADVANCED_THRESHOLD),
            TROPHY_CRIMSON_REAPER: ("kill", KILL_TROPHY_ELITE_THRESHOLD),
            TROPHY_APEX_PREDATOR: ("kill", KILL_TROPHY_MASTER_THRESHOLD),
        }
        nonlethal_actions = player.nonlethal_action_count()
        completed_quests = sum(
            1 for quest in self.quests if player.quest_log.get(quest.quest_id) == QuestStatus.COMPLETED
        )
        for trophy_key, trophy in self.trophy_catalog.items():
            tracked = trophy_targets.get(trophy_key)
            if tracked is None:
                continue
            metric_key, target = tracked
            if metric_key == "regions_cleared":
                current_value = cleared_regions
            elif metric_key == "nonlethal_actions":
                current_value = nonlethal_actions
            elif metric_key == "balanced_nonlethal":
                current_value = min(player.encounter_outcomes[action] for action in ("charm", "stealth", "evasion"))
            elif metric_key == "completed_quests":
                current_value = completed_quests
            else:
                current_value = player.encounter_outcomes.get(metric_key, 0)
            remaining = max(target - current_value, 0)
            if trophy.key == TROPHY_SILENT_LEGEND and player.encounter_outcomes["kill"] > 0:
                remaining = target
            if trophy.key == TROPHY_MERCY_CROWN and player.encounter_outcomes["kill"] > 0:
                remaining = target
            progress.append(
                {
                    "key": trophy.key,
                    "name": trophy.name,
                    "tier": trophy.tier.value,
                    "current": current_value,
                    "target": target,
                    "remaining": remaining,
                    "near_miss": trophy.key not in player.trophies and remaining == 1,
                    "unlocked": trophy.key in player.trophies,
                }
            )
        return sorted(progress, key=lambda item: item["key"])

    def to_snapshot(self, player: PlayerProfile) -> Dict[str, Any]:
        return {
            "world": {
                "regions": [
                    {
                        "name": region.name,
                        "village_hub": region.village_hub,
                        "enemies": list(region.enemies),
                        "allies": list(region.allies),
                        "boss": region.boss,
                        "boss_rewards": dict(region.boss_rewards),
                        "arc_key": region.arc_key,
                        "tutorial_mechanics": list(region.tutorial_mechanics),
                        "encounter_table": list(region.encounter_table),
                        "cleared": region.cleared,
                    }
                    for region in self.regions
                ],
                "quests": [
                    {
                        "quest_id": quest.quest_id,
                        "title": quest.title,
                        "premise": quest.premise,
                        "objective": quest.objective,
                        "stealth_required": quest.stealth_required,
                        "reward_xp": quest.reward_xp,
                        "choices": list(quest.choices),
                        "branch_outcomes": dict(quest.branch_outcomes),
                        "rewards": dict(quest.rewards),
                        "follow_up_hook": quest.follow_up_hook,
                        "villain_stance_impacts": dict(quest.villain_stance_impacts),
                        "reputation_impacts": dict(quest.reputation_impacts),
                        "trophy_hooks": list(quest.trophy_hooks),
                    }
                    for quest in self.quests
                ],
                "allies": list(self.allies),
                "weapons": [
                    {
                        "name": weapon.name,
                        "weapon_type": weapon.weapon_type.value,
                        "play_style": weapon.play_style,
                        "base_power": weapon.base_power,
                        "status_effects": [effect.value for effect in weapon.status_effects],
                    }
                    for weapon in self.weapons
                ],
                "skins": [
                    {"name": skin.name, "stat_boosts": dict(skin.stat_boosts)} for skin in self.skins
                ],
                "villains": [
                    {
                        "name": villain.name,
                        "backstory": villain.backstory,
                        "signature_power": {
                            "name": villain.signature_power.name,
                            "category": villain.signature_power.category.value,
                            "affinities": [affinity.value for affinity in villain.signature_power.affinities],
                            "power_scale": villain.signature_power.power_scale,
                            "jutsu_type": villain.signature_power.jutsu_type.value,
                            "status_effects": [effect.value for effect in villain.signature_power.status_effects],
                            "animation_profile": dict(villain.signature_power.animation_profile),
                        },
                        "primary_affinity": villain.primary_affinity.value,
                        "role": villain.role,
                        "skinned_move_names": dict(villain.skinned_move_names),
                        "ultimate_skin_name": villain.ultimate_skin_name,
                        "aggression_score": villain.aggression_score,
                        "stance": villain.stance.value,
                        "decision_memory": dict(villain.decision_memory),
                        "health_bar_color": villain.health_bar_color,
                        "defeated": villain.defeated,
                    }
                    for villain in self.villains
                ],
                "villain_behavior_rules": {
                    villain_name: {stance.value: text for stance, text in behavior_by_stance.items()}
                    for villain_name, behavior_by_stance in self.villain_behavior_rules.items()
                },
                "player_backstories": [
                    {
                        "key": backstory.key,
                        "title": backstory.title,
                        "narrative_tags": list(backstory.narrative_tags),
                        "reputation_bias": backstory.reputation_bias,
                    }
                    for backstory in self.player_backstories
                ],
                "trophy_catalog": {
                    trophy_key: {
                        "key": trophy.key,
                        "name": trophy.name,
                        "description": trophy.description,
                        "category": trophy.category.value,
                        "tier": trophy.tier.value,
                    }
                    for trophy_key, trophy in self.trophy_catalog.items()
                },
                "ninjutsu_library": [
                    {
                        "name": move.name,
                        "category": move.category.value,
                        "affinities": [affinity.value for affinity in move.affinities],
                        "power_scale": move.power_scale,
                        "jutsu_type": move.jutsu_type.value,
                        "status_effects": [effect.value for effect in move.status_effects],
                        "animation_profile": dict(move.animation_profile),
                    }
                    for move in self.ninjutsu_library
                ],
                "shop_inventory": {key: dict(value) for key, value in self.shop_inventory.items()},
                "vault_historic_ninjas": list(self.vault_historic_ninjas),
                "vault_meta_tapestry": list(self.vault_meta_tapestry),
                "active_run_tapestry": list(self.active_run_tapestry),
                "world_event_history": list(self.world_event_history),
                "dynamic_region_chain": list(self.dynamic_region_chain),
                "recent_boss_chains": [list(chain) for chain in self.recent_boss_chains],
                "region_state": {key: dict(value) for key, value in self.region_state.items()},
                "boss_availability": dict(self.boss_availability),
                "antagonist_candidates": list(self.antagonist_candidates),
                "antagonist_scoreboard": dict(self.antagonist_scoreboard),
                "antagonist_signal_log": {
                    key: list(value) for key, value in self.antagonist_signal_log.items()
                },
                "selected_final_antagonist": (
                    dict(self.selected_final_antagonist) if self.selected_final_antagonist else None
                ),
                "arcs": [
                    {
                        "key": arc.key,
                        "title": arc.title,
                        "tone": arc.tone,
                        "stakes": arc.stakes,
                        "regions": list(arc.regions),
                        "era_band": arc.era_band,
                    }
                    for arc in self.arcs
                ],
                "era_timeline": [dict(item) for item in self.era_timeline],
                "current_arc_key": self.current_arc_key,
                "current_age": self.current_age,
                "current_era_index": self.current_era_index,
                "world_recovery_score": self.world_recovery_score,
                "run_counter": self.run_counter,
                "latent_decision_seeds": dict(self.latent_decision_seeds),
                "latent_echo_history": [dict(e) for e in self.latent_echo_history],
            },
            "player": player.to_snapshot(),
        }

    @classmethod
    def from_snapshot(cls, snapshot: Dict[str, Any]) -> Tuple["NinjaWorld", PlayerProfile]:
        world_snapshot = snapshot["world"]
        player_snapshot = snapshot["player"]

        regions = [
            Region(
                name=item["name"],
                village_hub=item["village_hub"],
                enemies=list(item["enemies"]),
                allies=list(item["allies"]),
                boss=item["boss"],
                boss_rewards=dict(item["boss_rewards"]),
                arc_key=item.get("arc_key", "political_war"),
                tutorial_mechanics=tuple(item.get("tutorial_mechanics", [])),
                encounter_table=list(item.get("encounter_table", [])),
                cleared=item.get("cleared", False),
            )
            for item in world_snapshot["regions"]
        ]
        quests = [
            Quest(
                quest_id=item["quest_id"],
                title=item["title"],
                premise=item.get("premise", item["objective"]),
                objective=item["objective"],
                stealth_required=item["stealth_required"],
                reward_xp=item["reward_xp"],
                choices=tuple(item.get("choices", ())),
                branch_outcomes=dict(item.get("branch_outcomes", {})),
                rewards=dict(item.get("rewards", {})),
                follow_up_hook=item.get("follow_up_hook", ""),
                villain_stance_impacts=dict(item.get("villain_stance_impacts", {})),
                reputation_impacts=dict(item.get("reputation_impacts", {})),
                trophy_hooks=tuple(item.get("trophy_hooks", ())),
            )
            for item in world_snapshot["quests"]
        ]
        weapons = [
            Weapon(
                name=item["name"],
                weapon_type=WeaponType(item["weapon_type"]),
                play_style=item["play_style"],
                base_power=item["base_power"],
                status_effects=tuple(
                    StatusEffectType(effect) for effect in item.get("status_effects", [])
                ),
            )
            for item in world_snapshot["weapons"]
        ]
        skins = [Skin(name=item["name"], stat_boosts=dict(item["stat_boosts"])) for item in world_snapshot["skins"]]
        villains = [
            VillainProfile(
                name=item["name"],
                backstory=item["backstory"],
                signature_power=Move(
                    name=item.get("signature_power", {}).get("name", f'{item["name"]} Signature Art'),
                    category=MoveCategory(
                        item.get("signature_power", {}).get("category", MoveCategory.ATTACK.value)
                    ),
                    affinities=tuple(
                        Affinity(affinity)
                        for affinity in item.get("signature_power", {}).get("affinities", [Affinity.FIRE.value])
                    ),
                    power_scale=item.get("signature_power", {}).get("power_scale", 1.0),
                    jutsu_type=JutsuType(
                        item.get("signature_power", {}).get("jutsu_type", JutsuType.ELEMENTAL.value)
                    ),
                    status_effects=tuple(
                        StatusEffectType(effect)
                        for effect in item.get("signature_power", {}).get("status_effects", [])
                    ),
                    animation_profile=dict(
                        item.get("signature_power", {}).get("animation_profile", {})
                    ),
                ),
                primary_affinity=Affinity(item.get("primary_affinity", Affinity.FIRE.value)),
                role=item.get("role", "duelist"),
                skinned_move_names=dict(item.get("skinned_move_names", {})),
                ultimate_skin_name=item.get("ultimate_skin_name", ""),
                aggression_score=item.get("aggression_score", 0),
                stance=VillainStance(item.get("stance", VillainStance.BALANCED.value)),
                decision_memory=dict(item.get("decision_memory", {})),
                health_bar_color=item.get("health_bar_color", "red"),
                defeated=bool(item.get("defeated", False)),
            )
            for item in world_snapshot["villains"]
        ]
        behavior_rules = {
            villain_name: {
                VillainStance(stance): text for stance, text in behavior_by_stance.items()
            }
            for villain_name, behavior_by_stance in world_snapshot["villain_behavior_rules"].items()
        }
        backstories = [
            Backstory(
                key=item["key"],
                title=item["title"],
                narrative_tags=tuple(item["narrative_tags"]),
                reputation_bias=item.get("reputation_bias", 0),
            )
            for item in world_snapshot["player_backstories"]
        ]
        trophy_catalog = {
            trophy_key: Trophy(
                key=item["key"],
                name=item["name"],
                description=item["description"],
                category=TrophyCategory(item["category"]),
                tier=TrophyTier(item.get("tier", TrophyTier.EARLY.value)),
            )
            for trophy_key, item in world_snapshot["trophy_catalog"].items()
        }
        ninjutsu_library = [
            Move(
                name=move["name"],
                category=MoveCategory(move["category"]),
                affinities=tuple(Affinity(affinity) for affinity in move["affinities"]),
                power_scale=move.get("power_scale", 1.0),
                jutsu_type=JutsuType(move.get("jutsu_type", JutsuType.ELEMENTAL.value)),
                status_effects=tuple(
                    StatusEffectType(effect) for effect in move.get("status_effects", [])
                ),
                animation_profile=dict(move.get("animation_profile", {})),
            )
            for move in world_snapshot.get("ninjutsu_library", [])
        ]
        arcs = [
            ArcDefinition(
                key=item["key"],
                title=item["title"],
                tone=item["tone"],
                stakes=item["stakes"],
                regions=tuple(item.get("regions", [])),
                era_band=item.get("era_band", "war_age"),
            )
            for item in world_snapshot.get("arcs", [])
        ]

        world = cls(
            regions=regions,
            quests=quests,
            allies=list(world_snapshot["allies"]),
            weapons=weapons,
            skins=skins,
            villains=villains,
            villain_behavior_rules=behavior_rules,
            player_backstories=backstories,
            trophy_catalog=trophy_catalog,
            arcs=arcs,
            era_timeline=[dict(item) for item in world_snapshot.get("era_timeline", [])],
            ninjutsu_library=ninjutsu_library,
            shop_inventory={key: dict(value) for key, value in world_snapshot.get("shop_inventory", {}).items()},
            vault_historic_ninjas=list(world_snapshot.get("vault_historic_ninjas", [])),
            vault_meta_tapestry=list(world_snapshot.get("vault_meta_tapestry", [])),
            active_run_tapestry=list(world_snapshot.get("active_run_tapestry", [])),
            world_event_history=list(world_snapshot.get("world_event_history", [])),
            dynamic_region_chain=list(world_snapshot.get("dynamic_region_chain", [])),
            recent_boss_chains=[list(chain) for chain in world_snapshot.get("recent_boss_chains", [])],
            region_state={
                key: dict(value) for key, value in world_snapshot.get("region_state", {}).items()
            },
            boss_availability=dict(world_snapshot.get("boss_availability", {})),
            antagonist_candidates=list(world_snapshot.get("antagonist_candidates", [])),
            antagonist_scoreboard={
                key: int(value) for key, value in world_snapshot.get("antagonist_scoreboard", {}).items()
            },
            antagonist_signal_log={
                key: list(value) for key, value in world_snapshot.get("antagonist_signal_log", {}).items()
            },
            selected_final_antagonist=world_snapshot.get("selected_final_antagonist"),
            current_arc_key=world_snapshot.get("current_arc_key", "political_war"),
            current_age=int(world_snapshot.get("current_age", 16)),
            current_era_index=int(world_snapshot.get("current_era_index", 0)),
            world_recovery_score=int(world_snapshot.get("world_recovery_score", 0)),
            run_counter=int(world_snapshot.get("run_counter", 0)),
            latent_decision_seeds={
                key: int(value)
                for key, value in world_snapshot.get("latent_decision_seeds", {}).items()
            },
            latent_echo_history=list(world_snapshot.get("latent_echo_history", [])),
        )

        skin_by_name = {skin.name: skin for skin in world.skins}
        weapon_by_name = {weapon.name: weapon for weapon in world.weapons}
        backstory_by_key = {backstory.key: backstory for backstory in world.player_backstories}

        player = PlayerProfile(
            name=player_snapshot["name"],
            affinity=Affinity(player_snapshot["affinity"]),
            stats=PlayerStats(
                level=player_snapshot["stats"]["level"],
                xp=player_snapshot["stats"]["xp"],
                power=player_snapshot["stats"]["power"],
                defense=player_snapshot["stats"]["defense"],
                agility=player_snapshot["stats"]["agility"],
                focus=player_snapshot["stats"]["focus"],
            ),
            reputation=player_snapshot["reputation"],
            unlocked_zones=list(player_snapshot.get("unlocked_zones", [])),
            unlocked_fast_travel_nodes=list(player_snapshot.get("unlocked_fast_travel_nodes", [])),
            unlocked_skins=[
                skin_by_name[name] for name in player_snapshot.get("unlocked_skins", []) if name in skin_by_name
            ],
            weapons=[weapon_by_name[name] for name in player_snapshot.get("weapons", []) if name in weapon_by_name],
            reward_inventory={
                key: list(values)
                for key, values in player_snapshot.get(
                    "reward_inventory", {"weapon": [], "clothing": [], "move": []}
                ).items()
            },
            red_bar_power_claims={
                villain_name: move_name
                for villain_name, move_name in player_snapshot.get("red_bar_power_claims", {}).items()
            },
            selected_backstory=backstory_by_key.get(player_snapshot.get("selected_backstory")),
            narrative_tags=set(player_snapshot.get("narrative_tags", [])),
            encounter_outcomes=dict(
                player_snapshot.get(
                    "encounter_outcomes",
                    {"kill": 0, "charm": 0, "stealth": 0, "evasion": 0},
                )
            ),
            trophies=set(player_snapshot.get("trophies", [])),
            quest_log={
                quest_id: QuestStatus(status)
                for quest_id, status in player_snapshot.get("quest_log", {}).items()
            },
            ally_loyalty={
                ally_name: int(value)
                for ally_name, value in player_snapshot.get("ally_loyalty", {}).items()
            },
            encounter_history={
                region_name: int(value)
                for region_name, value in player_snapshot.get("encounter_history", {}).items()
            },
            credits=int(player_snapshot.get("credits", 100)),
            unlocked_move_names=set(player_snapshot.get("unlocked_move_names", [])),
            active_status_effects={
                effect_name: {
                    "duration": int(payload.get("duration", 0)),
                    "stacks": int(payload.get("stacks", 0)),
                }
                for effect_name, payload in player_snapshot.get("active_status_effects", {}).items()
            },
        )
        for category_name, moves in player_snapshot.get("moves_by_set", {}).items():
            category = MoveCategory(category_name)
            player.moves_by_set[category] = [
                Move(
                    name=move["name"],
                    category=MoveCategory(move["category"]),
                    affinities=tuple(Affinity(affinity) for affinity in move["affinities"]),
                    power_scale=move.get("power_scale", 1.0),
                    jutsu_type=JutsuType(move.get("jutsu_type", JutsuType.ELEMENTAL.value)),
                    status_effects=tuple(
                        StatusEffectType(effect) for effect in move.get("status_effects", [])
                    ),
                    animation_profile=dict(move.get("animation_profile", {})),
                )
                for move in moves
            ]
        if not player.unlocked_move_names:
            player.unlocked_move_names = {
                move.name for move_set in player.moves_by_set.values() for move in move_set
            }

        if not player.quest_log:
            player.initialize_quest_log([quest.quest_id for quest in world.quests])
        for ally in world.allies:
            player.ally_loyalty.setdefault(ally, 0)

        return world, player


def save_world_snapshot(world: NinjaWorld, player: PlayerProfile, path: str | Path) -> None:
    snapshot_path = Path(path)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(world.to_snapshot(player), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_world_snapshot(path: str | Path) -> Tuple[NinjaWorld, PlayerProfile]:
    snapshot_path = Path(path)
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    return NinjaWorld.from_snapshot(snapshot)


def resolve_affinity_minigame(decisions: Sequence[int]) -> Affinity:
    """Resolve starting affinity from mini-game decisions.

    Scores are applied in affinity order (Fire, Water, Earth, Wind) and
    wrap cyclically when more than four decisions are provided.
    Higher total score wins; ties resolve by the same affinity order.
    """
    scores = _empty_affinity_scores()
    for idx, value in enumerate(decisions):
        scores[AFFINITY_ORDER[idx % len(AFFINITY_ORDER)]] += value
    ranked = sorted(
        scores.items(),
        key=lambda item: (-item[1], AFFINITY_ORDER.index(item[0])),
    )
    return ranked[0][0]


def assign_affinity_from_choices(choices: Sequence[str]) -> Affinity:
    """Resolve starting affinity from explicit mini-game choice answers.

    The affinity with the highest answer count wins; ties resolve by
    Fire, then Water, then Earth, then Wind.
    """
    if not choices:
        raise ValueError("Mini-game choices cannot be empty.")

    scores = _empty_affinity_scores()
    for raw_choice in choices:
        normalized = raw_choice.strip().lower()
        affinity = AFFINITY_MINIGAME_CHOICES.get(normalized)
        if not affinity:
            raise ValueError(f'Unknown affinity choice "{normalized}".')
        scores[affinity] += 1

    ranked = sorted(
        scores.items(),
        key=lambda item: (-item[1], AFFINITY_ORDER.index(item[0])),
    )
    return ranked[0][0]


def _paired_affinity_for_ultimate(primary: Affinity) -> Affinity:
    """Select a simple paired affinity for starter mixed ultimates.

    MVP design pairs Wind with Fire; all other primaries pair with Wind
    to keep two-element ultimates broadly balanced around mobility/control.
    """
    if primary == Affinity.WIND:
        return Affinity.FIRE
    return Affinity.WIND


def _summon_names_for_affinity(primary: Affinity) -> Tuple[str, str]:
    return {
        Affinity.FIRE: ("Blazehound Pact", "Cinder Mantis Pact"),
        Affinity.WATER: ("Undertow Serpent Pact", "Mist Heron Pact"),
        Affinity.EARTH: ("Stone Ram Pact", "Granite Tortoise Pact"),
        Affinity.WIND: ("Sky Hawk Pact", "Tempest Lynx Pact"),
    }[primary]


def _seed_weapons() -> List[Weapon]:
    return [
        Weapon(
            "Dawn Cutter",
            WeaponType.SWORD,
            "balanced duelist",
            18,
            status_effects=(StatusEffectType.BLEED,),
        ),
        Weapon(
            "Silent Fang",
            WeaponType.KUNAI,
            "high-mobility burst",
            14,
            status_effects=(StatusEffectType.BLIND,),
        ),
        Weapon(
            "Temple Branch",
            WeaponType.BOW_STAFF,
            "control and spacing",
            16,
            status_effects=(StatusEffectType.STAGGER,),
        ),
        Weapon(
            "Storm Scatter",
            WeaponType.NINJA_STARS,
            "ranged precision",
            15,
            status_effects=(StatusEffectType.CRACK_ARMOR,),
        ),
    ]


def _affinity_animation_profile(affinity: Affinity, category: MoveCategory) -> Dict[str, str]:
    style = {
        Affinity.FIRE: {
            "startup": "embers flare at shoulders",
            "travel": "corkscrew flame lane",
            "hit": "expanding orange-red shock ring",
            "recovery": "ash drift and heat shimmer",
        },
        Affinity.WATER: {
            "startup": "water ribbon spiral at feet",
            "travel": "mist-lined current slash",
            "hit": "splash arc with ripple pulse",
            "recovery": "droplets fall into still wake",
        },
        Affinity.EARTH: {
            "startup": "seal stamp with rising rock plates",
            "travel": "debris-skid pressure lane",
            "hit": "fissure burst and heavy camera thud",
            "recovery": "stone fragments settle",
        },
        Affinity.WIND: {
            "startup": "compressed air ring gathers",
            "travel": "slicing crescent streaks",
            "hit": "pressure ripple cross-cut",
            "recovery": "feather-light afterimage fade",
        },
    }[affinity]
    return {
        "startup": style["startup"],
        "travel": style["travel"],
        "hit": f'{style["hit"]} ({category.value})',
        "recovery": style["recovery"],
    }


def _make_move(
    name: str,
    category: MoveCategory,
    affinities: Tuple[Affinity, ...],
    power_scale: float,
    jutsu_type: JutsuType,
    status_effects: Tuple[StatusEffectType, ...] = (),
) -> Move:
    primary = affinities[0]
    return Move(
        name=name,
        category=category,
        affinities=affinities,
        power_scale=power_scale,
        jutsu_type=jutsu_type,
        status_effects=status_effects,
        animation_profile=_affinity_animation_profile(primary, category),
    )


def _seed_shared_move_pool() -> Dict[MoveCategory, List[Move]]:
    return {
        MoveCategory.ESCAPE: [
            _make_move("Smoke Step", MoveCategory.ESCAPE, (Affinity.FIRE,), 0.6, JutsuType.MOBILITY),
            _make_move("Afterimage Drift", MoveCategory.ESCAPE, (Affinity.WATER,), 0.7, JutsuType.CLONE),
            _make_move("Silent Reed Slip", MoveCategory.ESCAPE, (Affinity.EARTH,), 0.75, JutsuType.SENSORY),
            _make_move("Mistfold Break", MoveCategory.ESCAPE, (Affinity.WATER,), 0.72, JutsuType.ILLUSION),
            _make_move("Stone Skip Dash", MoveCategory.ESCAPE, (Affinity.EARTH,), 0.68, JutsuType.MOBILITY),
            _make_move("Crosswind Fade", MoveCategory.ESCAPE, (Affinity.WIND,), 0.74, JutsuType.CLONE),
            _make_move(
                "Ember Veil Vault",
                MoveCategory.ESCAPE,
                (Affinity.FIRE,),
                0.71,
                JutsuType.MOBILITY,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Tidal Blink",
                MoveCategory.ESCAPE,
                (Affinity.WATER,),
                0.73,
                JutsuType.SUPPORT,
                (StatusEffectType.DRENCH,),
            ),
            _make_move("Burrow Snap", MoveCategory.ESCAPE, (Affinity.EARTH,), 0.69, JutsuType.MOBILITY),
            _make_move("Gale Feather Shift", MoveCategory.ESCAPE, (Affinity.WIND,), 0.76, JutsuType.SENSORY),
            _make_move(
                "Phantom Lantern Exit",
                MoveCategory.ESCAPE,
                (Affinity.WIND,),
                0.75,
                JutsuType.ILLUSION,
                (StatusEffectType.BLIND,),
            ),
            _make_move("Iron Cicada Swap", MoveCategory.ESCAPE, (Affinity.EARTH,), 0.7, JutsuType.CLONE),
        ],
        MoveCategory.ATTACK: [
            _make_move("Edge Current", MoveCategory.ATTACK, (Affinity.FIRE,), 1.0, JutsuType.ELEMENTAL),
            _make_move(
                "Threadline Volley",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.05,
                JutsuType.WEAPON_STYLE,
            ),
            _make_move(
                "Pressure Knot Strike",
                MoveCategory.ATTACK,
                (Affinity.EARTH,),
                1.1,
                JutsuType.SUPPORT,
            ),
            _make_move(
                "Cinder Lance",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.02,
                JutsuType.ELEMENTAL,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Undertow Slice",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.03,
                JutsuType.ELEMENTAL,
                (StatusEffectType.DRENCH,),
            ),
            _make_move(
                "Faultline Jab",
                MoveCategory.ATTACK,
                (Affinity.EARTH,),
                1.04,
                JutsuType.WEAPON_STYLE,
                (StatusEffectType.CRACK_ARMOR,),
            ),
            _make_move("Razor Gale Arc", MoveCategory.ATTACK, (Affinity.WIND,), 1.0, JutsuType.ELEMENTAL),
            _make_move(
                "Ash Fang Drive",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.08,
                JutsuType.WEAPON_STYLE,
                (StatusEffectType.BLEED,),
            ),
            _make_move(
                "Torrent Breaker",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.06,
                JutsuType.SUPPORT,
                (StatusEffectType.CHILL,),
            ),
            _make_move("Granite Spearline", MoveCategory.ATTACK, (Affinity.EARTH,), 1.07, JutsuType.ELEMENTAL),
            _make_move(
                "Tempest Hook",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.05,
                JutsuType.WEAPON_STYLE,
                (StatusEffectType.STAGGER,),
            ),
            _make_move(
                "Shadow Nail Burst",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.09,
                JutsuType.ILLUSION,
                (StatusEffectType.FEAR,),
            ),
        ],
        MoveCategory.DEFENSE: [
            _make_move("Guarding Veil", MoveCategory.DEFENSE, (Affinity.FIRE,), 0.8, JutsuType.BARRIER),
            _make_move("Lattice Ward", MoveCategory.DEFENSE, (Affinity.WATER,), 0.78, JutsuType.SEALING),
            _make_move("Flowback Mantle", MoveCategory.DEFENSE, (Affinity.EARTH,), 0.75, JutsuType.SUPPORT),
            _make_move("Current Shell", MoveCategory.DEFENSE, (Affinity.WATER,), 0.9, JutsuType.BARRIER),
            _make_move("Ash Aegis", MoveCategory.DEFENSE, (Affinity.FIRE,), 0.74, JutsuType.BARRIER),
            _make_move("Granite Net Seal", MoveCategory.DEFENSE, (Affinity.EARTH,), 0.95, JutsuType.SEALING),
            _make_move(
                "Pressure Dome",
                MoveCategory.DEFENSE,
                (Affinity.WIND,),
                0.84,
                JutsuType.BARRIER,
                (StatusEffectType.STAGGER,),
            ),
            _make_move("Mirror Bark Plate", MoveCategory.DEFENSE, (Affinity.EARTH,), 0.88, JutsuType.SUPPORT),
            _make_move(
                "Cyclone Parry Ring",
                MoveCategory.DEFENSE,
                (Affinity.WIND,),
                0.86,
                JutsuType.WEAPON_STYLE,
                (StatusEffectType.BLIND,),
            ),
            _make_move("Reef Anchor Guard", MoveCategory.DEFENSE, (Affinity.WATER,), 0.89, JutsuType.BARRIER),
            _make_move("Dune Bastion", MoveCategory.DEFENSE, (Affinity.EARTH,), 0.87, JutsuType.SEALING),
            _make_move(
                "Moonlit Counter Seal",
                MoveCategory.DEFENSE,
                (Affinity.WIND,),
                0.83,
                JutsuType.ILLUSION,
                (StatusEffectType.SILENCE,),
            ),
        ],
        MoveCategory.SUMMON: [
            _make_move(
                "Blazehound Pact",
                MoveCategory.SUMMON,
                (Affinity.FIRE,),
                1.0,
                JutsuType.SUMMONING,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Cinder Mantis Pact",
                MoveCategory.SUMMON,
                (Affinity.FIRE,),
                1.1,
                JutsuType.SUMMONING,
                (StatusEffectType.BLEED,),
            ),
            _make_move(
                "Undertow Serpent Pact",
                MoveCategory.SUMMON,
                (Affinity.WATER,),
                1.0,
                JutsuType.SUMMONING,
                (StatusEffectType.DRENCH,),
            ),
            _make_move(
                "Mist Heron Pact",
                MoveCategory.SUMMON,
                (Affinity.WATER,),
                1.08,
                JutsuType.SUMMONING,
                (StatusEffectType.BLIND,),
            ),
            _make_move(
                "Stone Ram Pact",
                MoveCategory.SUMMON,
                (Affinity.EARTH,),
                1.0,
                JutsuType.SUMMONING,
                (StatusEffectType.STAGGER,),
            ),
            _make_move(
                "Granite Tortoise Pact",
                MoveCategory.SUMMON,
                (Affinity.EARTH,),
                1.1,
                JutsuType.SUMMONING,
                (StatusEffectType.CRACK_ARMOR,),
            ),
            _make_move(
                "Sky Hawk Pact",
                MoveCategory.SUMMON,
                (Affinity.WIND,),
                1.0,
                JutsuType.SUMMONING,
                (StatusEffectType.BLIND,),
            ),
            _make_move(
                "Tempest Lynx Pact",
                MoveCategory.SUMMON,
                (Affinity.WIND,),
                1.1,
                JutsuType.SUMMONING,
                (StatusEffectType.CHILL,),
            ),
            _make_move(
                "Ember Jackal Pact",
                MoveCategory.SUMMON,
                (Affinity.FIRE,),
                1.06,
                JutsuType.SUMMONING,
                (StatusEffectType.FEAR,),
            ),
            _make_move(
                "Tide Eel Pact",
                MoveCategory.SUMMON,
                (Affinity.WATER,),
                1.04,
                JutsuType.SUMMONING,
                (StatusEffectType.ROOT,),
            ),
            _make_move(
                "Obsidian Ape Pact",
                MoveCategory.SUMMON,
                (Affinity.EARTH,),
                1.07,
                JutsuType.SUMMONING,
                (StatusEffectType.STAGGER,),
            ),
            _make_move(
                "Whisper Owl Pact",
                MoveCategory.SUMMON,
                (Affinity.WIND,),
                1.05,
                JutsuType.SUMMONING,
                (StatusEffectType.SILENCE,),
            ),
        ],
        MoveCategory.ULTIMATE: [
            _make_move(
                "Twin Dragon Convergence",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.WIND),
                2.5,
                JutsuType.ELEMENTAL,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Covenant Horizon Break",
                MoveCategory.ULTIMATE,
                (Affinity.WATER, Affinity.EARTH),
                2.2,
                JutsuType.SUMMONING,
                (StatusEffectType.ROOT,),
            ),
            _make_move(
                "Concord Nova",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.WIND),
                2.4,
                JutsuType.ELEMENTAL,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Tidal Monolith Break",
                MoveCategory.ULTIMATE,
                (Affinity.WATER, Affinity.EARTH),
                2.35,
                JutsuType.SUPPORT,
                (StatusEffectType.DRENCH,),
            ),
            _make_move(
                "Skyline Covenant",
                MoveCategory.ULTIMATE,
                (Affinity.WIND, Affinity.WATER),
                2.3,
                JutsuType.SUMMONING,
                (StatusEffectType.BLIND,),
            ),
            _make_move(
                "Furnace Eclipse",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.EARTH),
                2.45,
                JutsuType.ELEMENTAL,
                (StatusEffectType.BURN, StatusEffectType.CRACK_ARMOR),
            ),
            _make_move(
                "Leviathan Breakfall",
                MoveCategory.ULTIMATE,
                (Affinity.WATER, Affinity.WIND),
                2.42,
                JutsuType.SUMMONING,
                (StatusEffectType.DRENCH, StatusEffectType.CHILL),
            ),
            _make_move(
                "Worldroot Fracture",
                MoveCategory.ULTIMATE,
                (Affinity.EARTH, Affinity.FIRE),
                2.38,
                JutsuType.SEALING,
                (StatusEffectType.ROOT, StatusEffectType.STAGGER),
            ),
            _make_move(
                "Tempest Throne Collapse",
                MoveCategory.ULTIMATE,
                (Affinity.WIND, Affinity.EARTH),
                2.36,
                JutsuType.ELEMENTAL,
                (StatusEffectType.STAGGER,),
            ),
            _make_move(
                "Ashen Moon Sever",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.WATER),
                2.33,
                JutsuType.ILLUSION,
                (StatusEffectType.FEAR,),
            ),
            _make_move(
                "Abyss Crown Rupture",
                MoveCategory.ULTIMATE,
                (Affinity.WATER, Affinity.FIRE),
                2.37,
                JutsuType.BARRIER,
                (StatusEffectType.SILENCE,),
            ),
            _make_move(
                "Fourfold Shinobi Oath",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.WIND),
                2.32,
                JutsuType.SUPPORT,
                (StatusEffectType.BLIND, StatusEffectType.BURN),
            ),
        ],
    }


def _seed_moves(player_affinity: Affinity) -> Dict[MoveCategory, List[Move]]:
    paired = _paired_affinity_for_ultimate(player_affinity)
    pool = _seed_shared_move_pool()
    selected: Dict[MoveCategory, List[Move]] = {category: [] for category in MoveCategory}
    for category in (MoveCategory.ESCAPE, MoveCategory.ATTACK, MoveCategory.DEFENSE, MoveCategory.SUMMON):
        selected[category] = [move for move in pool[category] if move.affinities[0] == player_affinity][:3]
    selected[MoveCategory.ULTIMATE] = [
        move
        for move in pool[MoveCategory.ULTIMATE]
        if player_affinity in move.affinities and paired in move.affinities
    ][:2]
    if len(selected[MoveCategory.ULTIMATE]) < 2:
        selected[MoveCategory.ULTIMATE] = pool[MoveCategory.ULTIMATE][:2]
    return selected


def _seed_ninjutsu_library() -> List[Move]:
    pool = _seed_shared_move_pool()
    ordered_categories = [
        MoveCategory.ESCAPE,
        MoveCategory.ATTACK,
        MoveCategory.DEFENSE,
        MoveCategory.SUMMON,
        MoveCategory.ULTIMATE,
    ]
    return [move for category in ordered_categories for move in pool[category]]


def _seed_era_timeline() -> List[Dict[str, Any]]:
    return [
        {
            "key": "war_age",
            "title": "War Age",
            "tone": "fractured",
            "stakes": "survival and territorial pressure",
        },
        {
            "key": "recovery_age",
            "title": "Recovery Age",
            "tone": "fragile",
            "stakes": "rebuild momentum and social trust",
        },
        {
            "key": "hidden_age",
            "title": "Hidden Age",
            "tone": "transformative",
            "stakes": "long-term balance or irreversible decay",
        },
    ]


def _seed_arcs() -> List[ArcDefinition]:
    return [
        ArcDefinition(
            key="political_war",
            title="Political Warfront",
            tone="siege politics",
            stakes="council leverage and control of supply routes",
            regions=("Verdant Gate",),
            era_band="war_age",
        ),
        ArcDefinition(
            key="fracture_front",
            title="Fracture Front",
            tone="attrition",
            stakes="alliances fail or harden under pressure",
            regions=("Ashen Cradle",),
            era_band="recovery_age",
        ),
        ArcDefinition(
            key="recovery_mandate",
            title="Recovery Mandate",
            tone="reconstruction",
            stakes="world stabilizes or collapses into splinter rule",
            regions=("Tideglass Basin",),
            era_band="hidden_age",
        ),
        ArcDefinition(
            key="rebellion_wave",
            title="Rebellion Wave",
            tone="volatile",
            stakes="minor actors radicalize into existential threats",
            regions=("Verdant Gate", "Ashen Cradle"),
            era_band="hidden_age",
        ),
    ]


def _seed_regions() -> List[Region]:
    return [
        Region(
            name="Verdant Gate",
            village_hub="Leafrise Village",
            enemies=["Bandit Scouts", "Mist Ronin", "Root Stalkers"],
            encounter_table=["Bandit Scouts", "Mist Ronin", "Root Stalkers", "Hidden Sentry"],
            allies=["Dan"],
            boss="Kage Renda",
            boss_rewards={
                "weapon": "Renda Fang Blade",
                "clothing": "Shadow Mantle",
                "move": "Razorwind Spiral",
            },
            arc_key="political_war",
            tutorial_mechanics=("blocking", "substitution"),
        ),
        Region(
            name="Ashen Cradle",
            village_hub="Cinder Port",
            enemies=["Ash Mercenaries", "Lava Hounds"],
            encounter_table=["Ash Mercenaries", "Lava Hounds", "Ember Raiders"],
            allies=["Moon", "Sleep"],
            boss="General Voln",
            boss_rewards={
                "weapon": "Cradle Cleaver",
                "clothing": "Molten Gi",
                "move": "Inferno Vortex",
            },
            arc_key="fracture_front",
            tutorial_mechanics=("aoe_attacks",),
        ),
        Region(
            name="Tideglass Basin",
            village_hub="Azure Rest",
            enemies=["Tide Hunters", "Reef Assassins"],
            encounter_table=["Tide Hunters", "Reef Assassins", "Basin Corsairs"],
            allies=["Dot", "Porter"],
            boss="Admiral Neris",
            boss_rewards={
                "weapon": "Basin Pike",
                "clothing": "Tidewoven Cloak",
                "move": "Maelstrom Guard",
            },
            arc_key="recovery_mandate",
        ),
    ]


def _boss_exclusive_move_for(villain_name: str) -> Move:
    """Build the boss-only move reward configured for a region boss."""
    spec = BOSS_EXCLUSIVE_MOVE_SPECS.get(villain_name)
    if not spec:
        raise ValueError(
            f'Boss-exclusive move specification is not defined for villain "{villain_name}".'
        )
    return _make_move(
        spec["name"],
        spec["category"],
        spec["affinities"],
        spec["power_scale"],
        spec["jutsu_type"],
        spec["status_effects"],
    )


def _validate_boss_move_reward_config(regions: Sequence[Region]) -> None:
    """Validate seeded region bosses that grant move rewards in the current design."""
    for region in regions:
        move_reward_name = region.boss_rewards.get("move")
        if not move_reward_name:
            raise ValueError(f'Region "{region.name}" is missing a boss move reward.')
        spec = BOSS_EXCLUSIVE_MOVE_SPECS.get(region.boss)
        if not spec:
            raise ValueError(
                f'Boss-exclusive move specification is not defined for villain "{region.boss}".'
            )
        if move_reward_name != spec["name"]:
            raise ValueError(
                f'Boss move reward mismatch for "{region.boss}": '
                f'expected "{spec["name"]}", got "{move_reward_name}".'
            )


def _seed_quests() -> List[Quest]:
    quests = [
        Quest(
            quest_id="Q1",
            title="Trial of Quiet Steps",
            objective="Infiltrate the watchpost unseen and recover clan records.",
            stealth_required=True,
            reward_xp=120,
            branch_outcomes={
                "exiled_heir": "A hidden oath marker grants passage, and old sentries stand down at your approach.",
                "street_ghost": "Your underworld contacts open a tunnel route into the watchpost.",
                "wandering_monk": "You walk the patrol rhythm and slip through blind spots without raising alarm.",
                "infiltration": "You bypass the front line by scaling hidden cliff routes.",
                "default": "You infiltrate through the drainage channel under moonlight.",
            },
        ),
        Quest(
            quest_id="Q2",
            title="Allies in the Dark",
            objective="Escort Dan through the forest and repel ambushes.",
            stealth_required=False,
            reward_xp=140,
            branch_outcomes={
                "exiled_heir": "Old clan loyalists reveal a safe path and reinforce your escort line.",
                "street_ghost": "You reroute the caravan through smuggler trails and avoid the heaviest trap lines.",
                "wandering_monk": "Your calm mediation de-escalates the ambush, turning a standoff into safe passage.",
                "honor_bound": "You challenge the ambushers openly, earning their retreat.",
                "default": "You hold the line and protect Dan until dawn.",
            },
        ),
        Quest(
            quest_id="Q3",
            title="Break the Gate",
            objective="Defeat Kage Renda and secure Verdant Gate.",
            stealth_required=False,
            reward_xp=220,
            branch_outcomes={
                "exiled_heir": "You invoke a legacy challenge and force Kage Renda into a formal duel for the gate.",
                "street_ghost": "You cut supply lines and spring a precision trap before Renda can form a full defense.",
                "wandering_monk": "Through restraint and focus, you disarm Kage Renda without a killing blow.",
                "pacifism": "You force a surrender and secure the gate through discipline.",
                "default": "You overpower Kage Renda in a direct final clash.",
            },
        ),
        Quest(
            quest_id="Q4",
            title="Siege of Ember Court",
            objective="Stabilize Ashen Cradle by choosing between alliance, sabotage, or silent containment.",
            stealth_required=False,
            reward_xp=260,
            branch_outcomes={
                "exiled_heir": "You invoke treaty lineage and secure a formal truce with Ember captains.",
                "street_ghost": "You collapse black-market routes and starve the siege from the shadows.",
                "wandering_monk": "You broker a ceasefire and evacuate civilians before hostilities reignite.",
                "nonlethal_path": "You disable siege weapons without casualties and force both sides to stand down.",
                "heroic_path": "Your heroic standing rallies defenders into a disciplined counter-push.",
                "rogue_path": "Rogue operatives accept your contract and burn enemy supply caches overnight.",
                "default": "You seize command of the frontline and end the siege through direct pressure.",
            },
        ),
        Quest(
            quest_id="Q5",
            title="Moonlit Reckoning",
            objective="Confront the Tideglass command ring and decide the final terms of peace.",
            stealth_required=False,
            reward_xp=320,
            branch_outcomes={
                "exiled_heir": "You restore the old charter and bind the command ring to a public oath.",
                "street_ghost": "You expose the ring's hidden ledgers and force surrender through leverage.",
                "wandering_monk": "You dismantle the command ring without executions and secure a disarmament pact.",
                "nonlethal_path": "You neutralize every squad with charm, stealth, and evasion before talks begin.",
                "heroic_path": "Your heroic standing secures a regionwide truce under your witness.",
                "rogue_path": "You force compliance through shadow contracts that keep open war at bay.",
                "default": "You break the command ring in a decisive final confrontation.",
            },
        ),
        Quest(
            quest_id="Q6",
            title="Legacy of the Fallen Shinobi",
            objective="Reach the summit of the Ashen Spire and forge your legacy against the final warlord council.",
            stealth_required=False,
            reward_xp=420,
            branch_outcomes={
                "exiled_heir": (
                    "You invoke your bloodline covenant at the summit gate. The council recognizes the ancient seal "
                    "and grants passage — but demands a duel of honor before the final reckoning."
                ),
                "street_ghost": (
                    "You slip past the summit sentries using stolen council sigils and trigger a blackout across "
                    "their communications before they can coordinate a defense."
                ),
                "wandering_monk": (
                    "You climb in silence and meet the council unarmed. Your willingness to lay down arms forces "
                    "the council into a peace deliberation they cannot publicly refuse."
                ),
                "nonlethal_path": (
                    "Every warlord falls to charm, stealth, and evasion in turn. The final council session "
                    "ends in total surrender — no blood, only shadow."
                ),
                "heroic_path": (
                    "Your heroic reputation precedes you to the summit. Council defectors open a hidden passage "
                    "and stand behind you as witnesses to the reckoning."
                ),
                "rogue_path": (
                    "Rogue guild allies surround the spire before dawn. The council capitulates under the threat "
                    "of coordinated shadow strikes from every side."
                ),
                "default": (
                    "You storm the summit in a direct assault, overpower the warlord council, and carve your "
                    "legend into the walls of the Ashen Spire."
                ),
            },
        ),
        Quest(
            quest_id="Q7",
            title="Shattered Moon Accord",
            objective="Secure the Moonwell sanctum and decide whether to bind, expose, or dissolve the surviving war pacts.",
            stealth_required=False,
            reward_xp=520,
            branch_outcomes={
                "exiled_heir": (
                    "You restore the moon oath in your clan's name, forcing rival houses to swear peace under your seal."
                ),
                "street_ghost": (
                    "You leak pact ledgers to every syndicate at once and collapse the war pacts through public betrayal."
                ),
                "wandering_monk": (
                    "You disarm both factions in the sanctum and guide them into a shared vow of restraint."
                ),
                "nonlethal_path": (
                    "You disable every sentry and lock the sanctum without a single execution, leaving the pact leaders no path but negotiation."
                ),
                "heroic_path": (
                    "Your heroic banner unites scattered villages around the sanctum and compels the war pacts to surrender terms."
                ),
                "rogue_path": (
                    "You seize the pact archives and force signatures through covert leverage before dawn."
                ),
                "default": (
                    "You break into the Moonwell vaults and dictate the accord after a brutal sanctum showdown."
                ),
            },
        ),
        Quest(
            quest_id="Q8",
            title="Dawn of the Hidden Age",
            objective="Lead the first council of the new era and secure a lasting balance between shinobi factions.",
            stealth_required=False,
            reward_xp=620,
            branch_outcomes={
                "exiled_heir": (
                    "You inaugurate the hidden council from your ancestral seat and bind every faction to a bloodline charter."
                ),
                "street_ghost": (
                    "You establish a decentralized council of informants, ensuring no single faction can seize absolute control again."
                ),
                "wandering_monk": (
                    "You dissolve old rank lines, creating a peace council where restraint and service outrank conquest."
                ),
                "nonlethal_path": (
                    "With no blood debt behind you, the final council ratifies a disarmament era in your name."
                ),
                "heroic_path": (
                    "Your heroic record crowns you first guardian of the new age, with former enemies pledging open cooperation."
                ),
                "rogue_path": (
                    "You broker a shadow compact that keeps open war impossible while preserving your underground influence."
                ),
                "default": (
                    "You force a final compromise after one last clash and declare the dawn of a harder but united age."
                ),
            },
        ),
        Quest(
            quest_id="Q9",
            title="Ashes Beneath the Banner",
            objective="Investigate uprising cells in the reclaimed provinces and decide whether to absorb, expose, or silence them.",
            stealth_required=False,
            reward_xp=700,
            branch_outcomes={
                "exiled_heir": (
                    "You call old province captains to your banner and fold the uprising into a sworn reconstruction guard."
                ),
                "street_ghost": (
                    "You trace courier rings through abandoned safehouses and flip the uprising's network into your own shadow relay."
                ),
                "wandering_monk": (
                    "You disarm the cell leaders and broker amnesty terms that trade vengeance for service to the villages."
                ),
                "nonlethal_path": (
                    "You collapse every raid plan with stealth and misdirection, leaving the uprising disarmed without a single grave."
                ),
                "heroic_path": (
                    "Your heroic authority wins public testimony from the provinces, exposing the true agitators behind the revolt."
                ),
                "rogue_path": (
                    "You seize the rebellion's war chest and bind its commanders through covert contracts before they can regroup."
                ),
                "default": (
                    "You break the uprising in a series of relentless strikes and restore control by force."
                ),
            },
        ),
        Quest(
            quest_id="Q10",
            title="Veil of the Eternal Watch",
            objective="Secure the Eternal Watch archive and lock in the final doctrine that will govern the next shinobi generation.",
            stealth_required=True,
            reward_xp=820,
            branch_outcomes={
                "exiled_heir": (
                    "You inscribe your clan's final covenant into the archive and bind the doctrine to sworn guardians."
                ),
                "street_ghost": (
                    "You scatter mirrored copies of the archive and ensure no throne can ever monopolize its truths."
                ),
                "wandering_monk": (
                    "You open the archive to every village and anchor the doctrine in restraint, service, and shared accountability."
                ),
                "nonlethal_path": (
                    "Without blood debt to settle, you secure unanimous passage for a doctrine built on stealth, mercy, and balance."
                ),
                "heroic_path": (
                    "Your heroic legacy earns the final vote, and the Eternal Watch pledges to defend villages before crowns."
                ),
                "rogue_path": (
                    "You encode hidden enforcement clauses and keep the doctrine stable through unseen pressure from the shadows."
                ),
                "default": (
                    "You force a hard compromise into law and secure the archive after one final midnight confrontation."
                ),
            },
        ),
    ]
    quests.extend(_build_extended_quest_chain())
    _normalize_seeded_quest_metadata(quests)
    return quests


def _build_extended_quest_chain() -> List[Quest]:
    specs: List[Dict[str, Any]] = [
        {
            "quest_id": "Q11",
            "title": "Ashes of the Courier",
            "premise": "A missing courier carrying ceasefire terms could trigger renewed war.",
            "objective": "Track down the courier and secure the terms before rival factions intercept them.",
            "choices": ("rescue the courier", "forge replacement terms", "erase the treaty route"),
            "follow_up_hook": "Recovered message routes point to hidden supply ports.",
            "reward_theme": "diplomatic_intel",
        },
        {
            "quest_id": "Q12",
            "title": "Lanterns in the Mist",
            "premise": "Fogbound docks are moving contraband for masked jonin cells.",
            "objective": "Expose, repurpose, or dismantle the port smuggling network.",
            "choices": ("infiltrate the docks", "seize shipments", "negotiate with smugglers"),
            "follow_up_hook": "Smuggler ledgers name tribunal sponsors and hidden judges.",
            "reward_theme": "black_market_influence",
        },
        {
            "quest_id": "Q13",
            "title": "The Silent Tribunal",
            "premise": "A village tribunal weaponizes your past choices to shift power.",
            "objective": "Protect an ally, condemn them, or collapse the hearing without civil bloodshed.",
            "choices": ("defend the ally", "turn state witness", "expose forged evidence"),
            "follow_up_hook": "Court records reveal tunnels beneath the Hollow Tree shrine.",
            "reward_theme": "political_access",
        },
        {
            "quest_id": "Q14",
            "title": "Roots of the Hollow Tree",
            "premise": "Ancient tunnel wards protect a relic tied to fractured clan claims.",
            "objective": "Recover, seal, or relocate the relic while surviving legacy traps.",
            "choices": ("disarm seals", "claim relic authority", "destroy the relic"),
            "follow_up_hook": "Relic inscriptions expose a banquet assassination schedule.",
            "reward_theme": "relic_mastery",
        },
        {
            "quest_id": "Q15",
            "title": "Feast of Knives",
            "premise": "A peace banquet hides layered assassination contracts.",
            "objective": "Identify the real target and decide whether to protect or exploit them.",
            "choices": ("guard the target", "stage a decoy kill", "broker assassin truces"),
            "follow_up_hook": "Captured assassins trace orders to the Red Pass command.",
            "reward_theme": "court_influence",
        },
        {
            "quest_id": "Q16",
            "title": "Crows Over Red Pass",
            "premise": "Border defenses crack as rival commands test your loyalties.",
            "objective": "Hold, evacuate, or sabotage Red Pass before a full invasion lands.",
            "choices": ("fortify and defend", "evacuate civilians", "cripple both armies"),
            "follow_up_hook": "Pass survivors report a broken summoning pact behind the assault.",
            "reward_theme": "military_command",
        },
        {
            "quest_id": "Q17",
            "title": "The Broken Summoning Pact",
            "premise": "A rogue summon spirit turns on every faction at once.",
            "objective": "Rebind, negotiate release, or defeat the spirit before it levels border towns.",
            "choices": ("seal the spirit", "mediate pact terms", "weaponize the summon"),
            "follow_up_hook": "Pact records identify a prisoner tied to moonlit escape plans.",
            "reward_theme": "summon_affinity",
        },
        {
            "quest_id": "Q18",
            "title": "Moonlit Prison Break",
            "premise": "A political prisoner holds proof that could rewrite alliances.",
            "objective": "Extract, exchange, or fake the prisoner's death without exposing your network.",
            "choices": ("silent extraction", "public exchange", "false execution"),
            "follow_up_hook": "Prison intel points to the origin of your first blade lineage.",
            "reward_theme": "spy_network",
        },
        {
            "quest_id": "Q19",
            "title": "Echoes of the First Blade",
            "premise": "A backstory phantom duel determines your ideological legacy.",
            "objective": "Survive the ancestral duel and claim or reject its doctrine.",
            "choices": ("accept legacy", "break the doctrine", "share the doctrine"),
            "follow_up_hook": "The duel's verdict sets terms for the Shattered Gate siege.",
            "reward_theme": "signature_technique",
        },
        {
            "quest_id": "Q20",
            "title": "Dawn at Shattered Gate",
            "premise": "A siege at Shattered Gate decides who commands the next era.",
            "objective": "Lead defense, trigger a breach, or broker ceasefire before total collapse.",
            "choices": ("defend the gate", "open the gate", "mediate ceasefire"),
            "follow_up_hook": "War aftermath fractures faction trust and starts internal schisms.",
            "reward_theme": "arc_transition",
        },
        {
            "quest_id": "Q21",
            "title": "Beneath the Shrine Bell",
            "premise": "Shrine custodians accuse both armies of desecration to spark holy retaliation.",
            "objective": "Find the true instigator and decide whether to expose or leverage them.",
            "choices": ("protect shrine neutrals", "publish proof", "coerce confessions"),
            "follow_up_hook": "Recovered tokens reveal a coordinated courier sabotage ring.",
            "reward_theme": "spiritual_favor",
        },
        {
            "quest_id": "Q22",
            "title": "Paper Wings, Iron Chains",
            "premise": "Intercepted messenger birds isolate allied villages.",
            "objective": "Restore secure communication and determine who controls the cipher routes.",
            "choices": ("restore old ciphers", "create new network", "trap interceptors"),
            "follow_up_hook": "Cipher metadata exposes the Fifth Mask syndicate.",
            "reward_theme": "intel_speed",
        },
        {
            "quest_id": "Q23",
            "title": "The Fifth Mask",
            "premise": "A hidden masked leader manipulates every side of the conflict.",
            "objective": "Unmask, recruit, or publicly ruin the Fifth Mask.",
            "choices": ("recruit quietly", "public reveal", "erase all records"),
            "follow_up_hook": "Mask safehouses map directly to sabotaged farmlands.",
            "reward_theme": "covert_control",
        },
        {
            "quest_id": "Q24",
            "title": "Salt in the Ricefields",
            "premise": "Systematic crop sabotage threatens famine and uprising.",
            "objective": "Stop field poisoning and choose civilian relief or military stockpiles.",
            "choices": ("prioritize civilians", "secure war reserves", "split aid lines"),
            "follow_up_hook": "Supply caravan routes become immediate high-value targets.",
            "reward_theme": "civilian_trust",
        },
        {
            "quest_id": "Q25",
            "title": "Wolves at Noon",
            "premise": "Neutral caravans are attacked to force economic allegiance.",
            "objective": "Protect, raid, or redirect caravans to reshape the war economy.",
            "choices": ("escort caravans", "tax and redirect goods", "stage false raids"),
            "follow_up_hook": "Captured manifests contain forged Kage directives.",
            "reward_theme": "resource_pipeline",
        },
        {
            "quest_id": "Q26",
            "title": "Threads of the Kage Cloak",
            "premise": "Forged executive orders are tearing command ranks apart.",
            "objective": "Prove authenticity or exploit the confusion to force leadership change.",
            "choices": ("validate chain of command", "install proxy leadership", "collapse both hierarchies"),
            "follow_up_hook": "Competing leaders hide evidence in poisoned waterways.",
            "reward_theme": "command_authority",
        },
        {
            "quest_id": "Q27",
            "title": "When the River Runs Black",
            "premise": "Toxic river sabotage threatens every village downstream.",
            "objective": "Trace the source and choose transparent justice or strategic secrecy.",
            "choices": ("public trial", "quiet purge", "controlled cover-up"),
            "follow_up_hook": "Witnesses flee to an abandoned dojo linked to disappearances.",
            "reward_theme": "medical_network",
        },
        {
            "quest_id": "Q28",
            "title": "The Empty Dojo",
            "premise": "A legendary dojo is empty after a forced conscription experiment.",
            "objective": "Recover the missing students and choose reform, retaliation, or secrecy.",
            "choices": ("free students", "weaponize training logs", "bury the scandal"),
            "follow_up_hook": "Recovered logs expose a summit ambush timetable.",
            "reward_theme": "advanced_training",
        },
        {
            "quest_id": "Q29",
            "title": "Storm over Ironwood",
            "premise": "A final summit is interrupted by synchronized ambush teams.",
            "objective": "Save delegates, secure records, and choose who speaks for peace.",
            "choices": ("save delegates", "secure evidence first", "eliminate ambushers"),
            "follow_up_hook": "Summit survivors call for a total banner war.",
            "reward_theme": "faction_alignment",
        },
        {
            "quest_id": "Q30",
            "title": "Last Light of the Five Banners",
            "premise": "Five alliances collapse into one final campaign for dominance.",
            "objective": "End the campaign through unity, domination, or shadow governance.",
            "choices": ("forge unity", "enforce rule", "rule from shadows"),
            "follow_up_hook": "Emergency succession powers activate after the banner collapse.",
            "reward_theme": "ending_lock",
        },
        {
            "quest_id": "Q31",
            "title": "Ash Crown Protocol",
            "premise": "Emergency war succession powers trigger a contested regency.",
            "objective": "Support, restrain, or remove the temporary sovereign.",
            "choices": ("stabilize rule", "limit powers", "topple regency"),
            "follow_up_hook": "Regency decrees expose chakra ore seizure operations.",
            "reward_theme": "regime_control",
        },
        {
            "quest_id": "Q32",
            "title": "Veins of the Mountain",
            "premise": "Chakra ore mines become the new center of wartime leverage.",
            "objective": "Retake mines, negotiate labor terms, or destroy extraction sites.",
            "choices": ("retake by force", "broker labor pact", "cripple extraction"),
            "follow_up_hook": "Mine ledgers reveal identity theft operations on clan archives.",
            "reward_theme": "crafting_scale",
        },
        {
            "quest_id": "Q33",
            "title": "The Thief of Names",
            "premise": "Clan identity records are stolen to weaponize bloodlines.",
            "objective": "Recover records and decide who controls lineage truth.",
            "choices": ("restore full archives", "privatize key records", "burn bloodline lists"),
            "follow_up_hook": "Recovered aliases connect to frozen signal tower failures.",
            "reward_theme": "clan_loyalty",
        },
        {
            "quest_id": "Q34",
            "title": "Frost on the Signal Fires",
            "premise": "Warning towers go dark during coordinated winter raids.",
            "objective": "Relight the defense chain and handle the traitor behind the outage.",
            "choices": ("publicly expose traitor", "flip traitor as double-agent", "silent execution"),
            "follow_up_hook": "Traitor dispatches mention toxin vials in envoy circles.",
            "reward_theme": "early_warning",
        },
        {
            "quest_id": "Q35",
            "title": "Three Cups of Poison",
            "premise": "Envoys are dosed to collapse fragile diplomacy.",
            "objective": "Find antidote supply and identify who profits from delayed deaths.",
            "choices": ("distribute antidotes", "control antidote access", "booby-trap toxin stocks"),
            "follow_up_hook": "Antidote brokers carry references to a forbidden oath ledger.",
            "reward_theme": "toxin_resistance",
        },
        {
            "quest_id": "Q36",
            "title": "The Ninth Oath",
            "premise": "An obsolete oath forces a mission that could restart war.",
            "objective": "Honor, rewrite, or break the oath with lasting legitimacy.",
            "choices": ("honor oath", "rewrite oath terms", "break and replace oath"),
            "follow_up_hook": "Oath chambers reveal coordinates for the Bone Orchard.",
            "reward_theme": "legacy_authority",
        },
        {
            "quest_id": "Q37",
            "title": "Bone Orchard",
            "premise": "A grave site begins producing hostile summoned remnants.",
            "objective": "Purify, bind, or weaponize the Orchard before factions claim it.",
            "choices": ("purify shrine", "bind remnants", "weaponize remnants"),
            "follow_up_hook": "Recovered relic shards point to a forged treaty draft.",
            "reward_theme": "summon_depth",
        },
        {
            "quest_id": "Q38",
            "title": "Ink of the Last Treaty",
            "premise": "A forged treaty is leaked to lock in false peace terms.",
            "objective": "Validate, replace, or manipulate the final treaty text.",
            "choices": ("publish authentic treaty", "forge better terms", "hold treaty hostage"),
            "follow_up_hook": "Treaty dispute collapses into simultaneous fort uprisings.",
            "reward_theme": "diplomatic_lock",
        },
        {
            "quest_id": "Q39",
            "title": "Night of Falling Banners",
            "premise": "Allied fortresses fail at once, forcing irreversible triage.",
            "objective": "Choose which fronts survive and absorb the political cost.",
            "choices": ("save civilians first", "save military core", "preserve archives first"),
            "follow_up_hook": "The final power vacuum opens the Quiet Steel succession.",
            "reward_theme": "ally_survival",
        },
        {
            "quest_id": "Q40",
            "title": "Throne of Quiet Steel",
            "premise": "A final succession crisis decides long-term world order.",
            "objective": "Define rule by unity, dominance, or shadow balance.",
            "choices": ("federal unity model", "centralized rule", "hidden arbitration network"),
            "follow_up_hook": "Winter relief collapses under sabotage despite formal victory.",
            "reward_theme": "true_ending",
        },
        {
            "quest_id": "Q41",
            "title": "Embers Under Snow",
            "premise": "A winter ceasefire is hiding targeted sabotage in relief camps.",
            "objective": "Uncover the saboteurs and protect relief lines without reigniting war.",
            "choices": ("defend camps", "trace saboteurs", "use ceasefire as trap"),
            "follow_up_hook": "Temple bells vanish from guarded sanctuaries overnight.",
            "reward_theme": "postwar_stability",
        },
        {
            "quest_id": "Q42",
            "title": "The Sixth Bell",
            "premise": "A missing temple bell is used to mark assassination targets.",
            "objective": "Recover the bell and decode the hit-list ritual.",
            "choices": ("recover bell quietly", "publicly reveal list", "replace list with decoys"),
            "follow_up_hook": "Bell couriers connect to the Glass Sparrow network.",
            "reward_theme": "ritual_counterintel",
        },
        {
            "quest_id": "Q43",
            "title": "Glass Sparrow Network",
            "premise": "Children are coerced into courier duty for rival spymasters.",
            "objective": "Free the couriers and dismantle the handlers controlling them.",
            "choices": ("rescue and relocate", "flip handlers", "burn entire network"),
            "follow_up_hook": "Courier testimonies expose the Daimyo debt archive.",
            "reward_theme": "ethical_intel",
        },
        {
            "quest_id": "Q44",
            "title": "Debt of the Daimyo",
            "premise": "A secret debt bankrolls opposing factions at once.",
            "objective": "Audit the debt ledger and choose repayment, exposure, or seizure.",
            "choices": ("forgive debt", "public exposure", "seize collateral"),
            "follow_up_hook": "Seized records prove staged atrocities under your banner.",
            "reward_theme": "macro_economy",
        },
        {
            "quest_id": "Q45",
            "title": "The Hollow Banner",
            "premise": "Your faction banner is forged to justify civilian atrocities.",
            "objective": "Stop false-flag operations and decide how publicly to respond.",
            "choices": ("public tribunal", "secret retaliation", "counter-propaganda strike"),
            "follow_up_hook": "False-flag operators trade forbidden scrolls in a night market.",
            "reward_theme": "legitimacy_control",
        },
        {
            "quest_id": "Q46",
            "title": "Night Market of Teeth",
            "premise": "Forbidden jutsu auctions attract every surviving power broker.",
            "objective": "Disrupt, infiltrate, or dominate the auction economy.",
            "choices": ("destroy auction stock", "buy and seal scrolls", "control auction ring"),
            "follow_up_hook": "Auction maps reveal tampered borders with no true north.",
            "reward_theme": "forbidden_jutsu",
        },
        {
            "quest_id": "Q47",
            "title": "The Map with No North",
            "premise": "Border maps are altered to trigger legal territorial wars.",
            "objective": "Restore authoritative maps and settle claims before armies mobilize.",
            "choices": ("restore neutral maps", "redraw in your favor", "erase all claims"),
            "follow_up_hook": "Border casualties spark conflict at a fallen allies memorial.",
            "reward_theme": "territorial_stability",
        },
        {
            "quest_id": "Q48",
            "title": "Ash Garden Requiem",
            "premise": "A memorial for fallen allies becomes a battlefield of memory and blame.",
            "objective": "Protect the memorial and resolve who controls historical narrative.",
            "choices": ("honor all fallen", "elevate one faction", "seal memorial archives"),
            "follow_up_hook": "Memorial archives reference an unnamed heir claimant.",
            "reward_theme": "legacy_memory",
        },
        {
            "quest_id": "Q49",
            "title": "The Unwritten Name",
            "premise": "A hidden heir emerges with evidence of legitimate succession.",
            "objective": "Confirm, deny, or co-rule with the new claimant.",
            "choices": ("endorse heir", "disprove claim", "form dual governance"),
            "follow_up_hook": "Final settlement council convenes for lasting peace terms.",
            "reward_theme": "succession_resolution",
        },
        {
            "quest_id": "Q50",
            "title": "After the Last War Drum",
            "premise": "The final settlement determines justice, memory, and long-term peace.",
            "objective": "Define post-war governance and lock the world into your legacy framework.",
            "choices": ("restorative justice", "deterrence doctrine", "shadow equilibrium"),
            "follow_up_hook": "Legacy state enters replay-vault history for future ages.",
            "reward_theme": "new_game_plus",
        },
    ]

    reward_cycle = (
        "intel",
        "allies",
        "techniques",
        "economy",
        "political_access",
        "status_mastery",
    )
    extended_quests: List[Quest] = []
    for index, spec in enumerate(specs, start=11):
        xp = 820 + (index - 10) * 55
        reward_focus = reward_cycle[(index - 11) % len(reward_cycle)]
        arc_tag = (
            "escalation" if index <= 20 else "faction_fracture" if index <= 30 else "regime_endgame"
        )
        if index > 40:
            arc_tag = "postwar_continuation"
        branch_outcomes = _build_structured_branch_outcomes(spec)
        extended_quests.append(
            Quest(
                quest_id=spec["quest_id"],
                title=spec["title"],
                premise=spec["premise"],
                objective=spec["objective"],
                stealth_required=any(
                    marker in " ".join(spec["choices"]).lower()
                    for marker in ("infiltrate", "silent", "quiet", "stealth")
                ),
                reward_xp=xp,
                choices=tuple(spec["choices"]),
                branch_outcomes=branch_outcomes,
                rewards={
                    "xp": xp,
                    "credits": QUEST_CREDIT_REWARD_BASE + (index * 2),
                    "theme": spec["reward_theme"],
                    "focus": reward_focus,
                    "arc": arc_tag,
                },
                follow_up_hook=spec["follow_up_hook"],
                villain_stance_impacts={"kill": 2, "stealth": -1, "charm": -2, "evasion": -1},
                reputation_impacts={"heroic": 6, "neutral": 2, "rogue": -6},
                trophy_hooks=_quest_trophy_hooks(index),
            )
        )
    return extended_quests


def _build_structured_branch_outcomes(spec: Dict[str, Any]) -> Dict[str, str]:
    title = spec["title"]
    objective = spec["objective"]
    return {
        "exiled_heir": (
            f"Your clan authority reframes {title} as a lawful mandate, giving you sanctioned access before rivals mobilize."
        ),
        "street_ghost": (
            f"Your underworld network reroutes pressure points in {title}, letting you control outcomes through covert leverage."
        ),
        "wandering_monk": (
            f"You guide {title} toward restraint and service, stabilizing the objective without escalating blood debt."
        ),
        "nonlethal_path": (
            f"You complete {title} through stealth, charm, and evasion, proving the objective can be resolved without executions."
        ),
        "stealth_path": (
            f"You center {title} on stealth-first tactics, removing key obstacles before open conflict can form."
        ),
        "charm_path": (
            f"You resolve {title} by turning rivals into temporary allies and redirecting the conflict through diplomacy."
        ),
        "evasion_path": (
            f"You complete {title} through evasive maneuvers, exhausting enemies while preserving your force."
        ),
        "kill_path": (
            f"You drive {title} to a brutal conclusion, eliminating command targets to end resistance immediately."
        ),
        "heroic_path": (
            f"Your heroic standing unifies local support during {title}, turning public trust into operational momentum."
        ),
        "rogue_path": (
            f"Your rogue reputation weaponizes fear and favors in {title}, forcing compliance from hidden power brokers."
        ),
        "default": f"You execute the core objective directly: {objective}",
    }


def _quest_trophy_hooks(quest_number: int) -> Tuple[str, ...]:
    if quest_number <= 20:
        return (TROPHY_SILENT_LEGEND, TROPHY_TRINITY_OPERATOR)
    if quest_number <= 30:
        return (TROPHY_HARMONY_VOICE, TROPHY_UNTOUCHABLE_GHOST)
    if quest_number <= 40:
        return (TROPHY_HEROIC_CREST, TROPHY_ROGUE_ASCENDANT)
    return (TROPHY_MERCY_CROWN, TROPHY_QUESTMASTER)


def _normalize_seeded_quest_metadata(quests: List[Quest]) -> None:
    required_branch_keys = ("exiled_heir", "street_ghost", "wandering_monk", "default")
    for idx, quest in enumerate(quests):
        if not quest.premise:
            quest.premise = quest.objective
        if not quest.choices:
            quest.choices = (
                "stealth-forward approach",
                "direct confrontation",
                "negotiated resolution",
            )
        if not quest.rewards:
            quest.rewards = {
                "xp": quest.reward_xp,
                "credits": QUEST_CREDIT_REWARD_BASE + (idx * 2),
                "theme": "legacy_progression",
            }
        if not quest.follow_up_hook:
            next_quest_id = quests[idx + 1].quest_id if idx + 1 < len(quests) else "finale"
            quest.follow_up_hook = f"Completion of {quest.quest_id} points toward {next_quest_id}."
        if not quest.villain_stance_impacts:
            quest.villain_stance_impacts = {"kill": 2, "stealth": -1, "charm": -2, "evasion": -1}
        if not quest.reputation_impacts:
            quest.reputation_impacts = {"heroic": 5, "neutral": 1, "rogue": -5}
        if not quest.trophy_hooks:
            quest_number = int(quest.quest_id[1:]) if quest.quest_id[1:].isdigit() else 1
            quest.trophy_hooks = _quest_trophy_hooks(quest_number)
        if "default" not in quest.branch_outcomes:
            quest.branch_outcomes["default"] = quest.objective
        for branch_key in required_branch_keys:
            if branch_key not in quest.branch_outcomes:
                quest.branch_outcomes[branch_key] = quest.branch_outcomes["default"]


def _seed_allies(min_count: int = DEFAULT_ALLY_MIN_COUNT) -> List[str]:
    """Return ally names with seeded characters plus curated fillers.

    The five core seeded allies are always included. ``min_count`` is the
    total minimum ally count (including those five core allies).
    ``AutoNinja-*`` placeholders are only used if counts exceed the curated
    name pool.
    """
    allies = ["Dan", "Moon", "Sleep", "Dot", "Porter"]
    filler_pool = [
        "Ren",
        "Kaida",
        "Shiro",
        "Emi",
        "Toma",
        "Riku",
        "Sora",
        "Kiko",
        "Hayate",
        "Mika",
    ]
    for name in filler_pool:
        if len(allies) >= min_count:
            return allies
        allies.append(name)

    index = 1
    while len(allies) < min_count:
        allies.append(f"AutoNinja-{index}")
        index += 1
    return allies


def _seed_player_backstories() -> List[Backstory]:
    return [
        Backstory(
            key="exiled_heir",
            title="Exiled Heir",
            narrative_tags=("clan_politics", "honor_bound"),
            reputation_bias=5,
        ),
        Backstory(
            key="street_ghost",
            title="Street Ghost",
            narrative_tags=("underworld", "infiltration"),
            reputation_bias=-5,
        ),
        Backstory(
            key="wandering_monk",
            title="Wandering Monk",
            narrative_tags=("pacifism", "discipline"),
            reputation_bias=10,
        ),
    ]


def _seed_villains() -> List[VillainProfile]:
    def _kit(*, attack: str, defense: str, escape: str, summon: str, link: str) -> Dict[str, str]:
        return {
            "attack_skin": attack,
            "defense_skin": defense,
            "escape_skin": escape,
            "summon_skin": summon,
            "link_skin": link,
        }

    return [
        VillainProfile(
            name="Kage Renda",
            backstory="A fallen bodyguard who channels wind edges through precision bladework.",
            signature_power=_make_move(
                "Rending Spiral",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.2,
                JutsuType.WEAPON_STYLE,
                (StatusEffectType.BLEED,),
            ),
            primary_affinity=Affinity.WIND,
            role="duelist",
            skinned_move_names=_kit(
                attack="Tempest Hook",
                defense="Cyclone Parry Ring",
                escape="Crosswind Fade",
                summon="Sky Hawk Pact",
                link="Shadow Nail Burst",
            ),
            ultimate_skin_name="Tempest Throne Collapse",
        ),
        VillainProfile(
            name="General Voln",
            backstory="A warlord strategist using fire-forged pressure fields to break formations.",
            signature_power=_make_move(
                "Ember Cyclone",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.25,
                JutsuType.ELEMENTAL,
                (StatusEffectType.BURN, StatusEffectType.STAGGER),
            ),
            primary_affinity=Affinity.FIRE,
            role="warlord",
            skinned_move_names=_kit(
                attack="Cinder Lance",
                defense="Ash Aegis",
                escape="Ember Veil Vault",
                summon="Ember Jackal Pact",
                link="Ash Fang Drive",
            ),
            ultimate_skin_name="Furnace Eclipse",
            aggression_score=1,
        ),
        VillainProfile(
            name="Admiral Neris",
            backstory="A former naval hero who bends water currents into defensive tides.",
            signature_power=_make_move(
                "Abyss Arc",
                MoveCategory.DEFENSE,
                (Affinity.WATER,),
                1.0,
                JutsuType.BARRIER,
                (StatusEffectType.DRENCH,),
            ),
            primary_affinity=Affinity.WATER,
            role="controller",
            skinned_move_names=_kit(
                attack="Undertow Slice",
                defense="Current Shell",
                escape="Tidal Blink",
                summon="Tide Eel Pact",
                link="Torrent Breaker",
            ),
            ultimate_skin_name="Leviathan Breakfall",
        ),
        VillainProfile(
            name="Mist Widow",
            backstory="An ex-assassin who cloaks battlefields in toxic fog and panic.",
            signature_power=_make_move(
                "Widow Fog Domain",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.22,
                JutsuType.ILLUSION,
                (StatusEffectType.BLIND, StatusEffectType.FEAR),
            ),
            primary_affinity=Affinity.WATER,
            role="assassin",
            skinned_move_names=_kit(
                attack="Shadow Nail Burst",
                defense="Reef Anchor Guard",
                escape="Mistfold Break",
                summon="Mist Heron Pact",
                link="Threadline Volley",
            ),
            ultimate_skin_name="Abyss Crown Rupture",
        ),
        VillainProfile(
            name="Iron Lotus",
            backstory="A defensive grandmaster who turns enemy force into punishing counters.",
            signature_power=_make_move(
                "Lotus Counter Bloom",
                MoveCategory.DEFENSE,
                (Affinity.EARTH,),
                1.12,
                JutsuType.WEAPON_STYLE,
                (StatusEffectType.STAGGER,),
            ),
            primary_affinity=Affinity.EARTH,
            role="counter",
            skinned_move_names=_kit(
                attack="Granite Spearline",
                defense="Mirror Bark Plate",
                escape="Iron Cicada Swap",
                summon="Obsidian Ape Pact",
                link="Faultline Jab",
            ),
            ultimate_skin_name="Worldroot Fracture",
        ),
        VillainProfile(
            name="Stone Maw",
            backstory="A siege enforcer who breaks formations with tectonic bite patterns.",
            signature_power=_make_move(
                "Seismic Bite",
                MoveCategory.ATTACK,
                (Affinity.EARTH,),
                1.24,
                JutsuType.ELEMENTAL,
                (StatusEffectType.CRACK_ARMOR,),
            ),
            primary_affinity=Affinity.EARTH,
            role="breaker",
            skinned_move_names=_kit(
                attack="Faultline Jab",
                defense="Dune Bastion",
                escape="Burrow Snap",
                summon="Stone Ram Pact",
                link="Pressure Knot Strike",
            ),
            ultimate_skin_name="Worldroot Fracture",
        ),
        VillainProfile(
            name="Storm Needle",
            backstory="A precision hunter who threads wind pressure through armor gaps.",
            signature_power=_make_move(
                "Rail Gale Shot",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.2,
                JutsuType.WEAPON_STYLE,
                (StatusEffectType.BLEED,),
            ),
            primary_affinity=Affinity.WIND,
            role="sniper",
            skinned_move_names=_kit(
                attack="Razor Gale Arc",
                defense="Pressure Dome",
                escape="Gale Feather Shift",
                summon="Whisper Owl Pact",
                link="Tempest Hook",
            ),
            ultimate_skin_name="Tempest Throne Collapse",
        ),
        VillainProfile(
            name="Bone Weaver",
            backstory="A cursed tactician who binds targets with marrow-thread seals.",
            signature_power=_make_move(
                "Marrow Thread Prison",
                MoveCategory.DEFENSE,
                (Affinity.EARTH,),
                1.08,
                JutsuType.SEALING,
                (StatusEffectType.ROOT, StatusEffectType.BLEED),
            ),
            primary_affinity=Affinity.EARTH,
            role="controller",
            skinned_move_names=_kit(
                attack="Threadline Volley",
                defense="Granite Net Seal",
                escape="Stone Skip Dash",
                summon="Granite Tortoise Pact",
                link="Shadow Nail Burst",
            ),
            ultimate_skin_name="Fourfold Shinobi Oath",
        ),
        VillainProfile(
            name="Crimson Lantern",
            backstory="A ritual illusionist who weaponizes fear through radiant seals.",
            signature_power=_make_move(
                "Red Night Mandala",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.18,
                JutsuType.ILLUSION,
                (StatusEffectType.FEAR, StatusEffectType.BLIND),
            ),
            primary_affinity=Affinity.FIRE,
            role="illusionist",
            skinned_move_names=_kit(
                attack="Cinder Lance",
                defense="Moonlit Counter Seal",
                escape="Phantom Lantern Exit",
                summon="Ember Jackal Pact",
                link="Ash Fang Drive",
            ),
            ultimate_skin_name="Ashen Moon Sever",
        ),
        VillainProfile(
            name="Silent Bell",
            backstory="A shrine exile whose resonant bells suppress enemy jutsu flow.",
            signature_power=_make_move(
                "Null Resonance",
                MoveCategory.DEFENSE,
                (Affinity.WIND,),
                1.06,
                JutsuType.SENSORY,
                (StatusEffectType.SILENCE,),
            ),
            primary_affinity=Affinity.WIND,
            role="support_denial",
            skinned_move_names=_kit(
                attack="Tempest Hook",
                defense="Pressure Dome",
                escape="Crosswind Fade",
                summon="Whisper Owl Pact",
                link="Shadow Nail Burst",
            ),
            ultimate_skin_name="Skyline Covenant",
        ),
        VillainProfile(
            name="Frost Viper",
            backstory="A cold-blooded tracker who layers chill and venom pressure over time.",
            signature_power=_make_move(
                "White Venom Coil",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.19,
                JutsuType.SUPPORT,
                (StatusEffectType.CHILL, StatusEffectType.BLEED),
            ),
            primary_affinity=Affinity.WATER,
            role="attrition",
            skinned_move_names=_kit(
                attack="Torrent Breaker",
                defense="Current Shell",
                escape="Tidal Blink",
                summon="Tide Eel Pact",
                link="Undertow Slice",
            ),
            ultimate_skin_name="Leviathan Breakfall",
        ),
        VillainProfile(
            name="Vanta Puppetmaster",
            backstory="A rogue artisan who chains souls through forbidden marionette rites.",
            signature_power=_make_move(
                "Funeral Marionette",
                MoveCategory.SUMMON,
                (Affinity.WIND,),
                1.16,
                JutsuType.SUMMONING,
                (StatusEffectType.ROOT, StatusEffectType.FEAR),
            ),
            primary_affinity=Affinity.WIND,
            role="summoner",
            skinned_move_names=_kit(
                attack="Threadline Volley",
                defense="Lattice Ward",
                escape="Afterimage Drift",
                summon="Whisper Owl Pact",
                link="Phantom Lantern Exit",
            ),
            ultimate_skin_name="Fourfold Shinobi Oath",
        ),
        VillainProfile(
            name="Torch Baron",
            backstory="A black-market tyrant who scorches routes to force desperate choices.",
            signature_power=_make_move(
                "Black Market Inferno",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.23,
                JutsuType.ELEMENTAL,
                (StatusEffectType.BURN, StatusEffectType.CRACK_ARMOR),
            ),
            primary_affinity=Affinity.FIRE,
            role="zone_control",
            skinned_move_names=_kit(
                attack="Cinder Lance",
                defense="Ash Aegis",
                escape="Smoke Step",
                summon="Blazehound Pact",
                link="Pressure Knot Strike",
            ),
            ultimate_skin_name="Furnace Eclipse",
        ),
        VillainProfile(
            name="Dusk Paladin",
            backstory="A fallen protector who duels by oath and punishes disordered offense.",
            signature_power=_make_move(
                "Oathbreaker Radiance",
                MoveCategory.ATTACK,
                (Affinity.EARTH,),
                1.17,
                JutsuType.SUPPORT,
                (StatusEffectType.STAGGER,),
            ),
            primary_affinity=Affinity.EARTH,
            role="duelist",
            skinned_move_names=_kit(
                attack="Granite Spearline",
                defense="Mirror Bark Plate",
                escape="Iron Cicada Swap",
                summon="Obsidian Ape Pact",
                link="Faultline Jab",
            ),
            ultimate_skin_name="Tidal Monolith Break",
        ),
        VillainProfile(
            name="Eclipse Maw",
            backstory="An abyssal war-chief who collapses light and spacing into panic zones.",
            signature_power=_make_move(
                "Midnight Gravity Well",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.21,
                JutsuType.ILLUSION,
                (StatusEffectType.FEAR, StatusEffectType.ROOT),
            ),
            primary_affinity=Affinity.WIND,
            role="disruptor",
            skinned_move_names=_kit(
                attack="Shadow Nail Burst",
                defense="Moonlit Counter Seal",
                escape="Phantom Lantern Exit",
                summon="Tempest Lynx Pact",
                link="Tempest Hook",
            ),
            ultimate_skin_name="Tempest Throne Collapse",
        ),
    ]


def _seed_villain_behavior_rules() -> Dict[str, Dict[VillainStance, str]]:
    behavior_rules: Dict[str, Dict[VillainStance, str]] = {
        "Kage Renda": {
            VillainStance.AGGRESSIVE: "Rushes with relentless sword pressure and trap counters.",
            VillainStance.BALANCED: "Alternates measured strikes with defensive feints.",
            VillainStance.PASSIVE: "Maintains distance and probes for diplomatic openings.",
        },
        "General Voln": {
            VillainStance.AGGRESSIVE: "Calls reinforcements and overwhelms lanes with heavy assaults.",
            VillainStance.BALANCED: "Controls space and rotates formations around choke points.",
            VillainStance.PASSIVE: "Commits to shield walls, preferring containment over eliminations.",
        },
        "Admiral Neris": {
            VillainStance.AGGRESSIVE: "Presses tide-form attacks in rapid, high-risk sequences.",
            VillainStance.BALANCED: "Keeps tempo steady with spacing and terrain control.",
            VillainStance.PASSIVE: "Seeks negotiation windows while guarding key positions.",
        },
    }
    for villain in _seed_villains():
        if villain.name in behavior_rules:
            continue
        behavior_rules[villain.name] = {
            VillainStance.AGGRESSIVE: (
                f"{villain.name} chains {villain.skinned_move_names.get('attack_skin', 'attack')} "
                f"into {villain.signature_power.name} with relentless pressure."
            ),
            VillainStance.BALANCED: (
                f"{villain.name} rotates {villain.skinned_move_names.get('defense_skin', 'defense')} "
                f"and {villain.skinned_move_names.get('link_skin', 'link')} before committing."
            ),
            VillainStance.PASSIVE: (
                f"{villain.name} repositions with {villain.skinned_move_names.get('escape_skin', 'escape')} "
                "and waits for negotiation openings."
            ),
        }
    return behavior_rules


def _seed_trophy_catalog() -> Dict[str, Trophy]:
    trophies = [
        Trophy(
            TROPHY_FIRST_STRIKE,
            "First Strike",
            "Defeat an enemy lethally for the first time.",
            TrophyCategory.COMBAT,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_GHOST_STEP,
            "Ghost Step",
            "Complete three encounters through stealth.",
            TrophyCategory.STEALTH,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_SILVER_TONGUE,
            "Silver Tongue",
            "Resolve three encounters through charm.",
            TrophyCategory.SOCIAL,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_WINDWALK_SURVIVOR,
            "Windwalk Survivor",
            "Escape danger through evasion three times.",
            TrophyCategory.STEALTH,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_VEIL_MASTER,
            "Veil Master",
            "Complete five encounters through stealth.",
            TrophyCategory.STEALTH,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_DIPLOMAT_SUPREME,
            "Diplomat Supreme",
            "Resolve five encounters through charm.",
            TrophyCategory.SOCIAL,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_PACIFIST_SHADOW,
            "Pacifist Shadow",
            "Maintain a kill-free run while using charm, stealth, and evasion tactics.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_SILENT_LEGEND,
            "Silent Legend",
            "Clear every seeded region in a kill-free run.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_PHANTOM_VEIL,
            "Phantom Veil",
            "Complete eight encounters through stealth.",
            TrophyCategory.STEALTH,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_HARMONY_VOICE,
            "Harmony Voice",
            "Resolve eight encounters through charm.",
            TrophyCategory.SOCIAL,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_UNTOUCHABLE_GHOST,
            "Untouchable Ghost",
            "Escape danger through evasion five times.",
            TrophyCategory.STEALTH,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_TRINITY_OPERATOR,
            "Trinity Operator",
            "Use charm, stealth, and evasion at least twice each without any kills.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_ORIGIN_AWAKENED,
            "Origin Awakened",
            "Choose a protagonist backstory and set your narrative path.",
            TrophyCategory.PROGRESSION,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_FIRST_BLOODLINE_VICTORY,
            "First Bloodline Victory",
            "Clear your first region and claim a boss reward.",
            TrophyCategory.PROGRESSION,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_WORLD_WALKER,
            "World Walker",
            "Clear every seeded region in the current world.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_ROGUE_ASCENDANT,
            "Rogue Ascendant",
            "Reach Rogue reputation tier.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_HEROIC_CREST,
            "Heroic Crest",
            "Reach Heroic reputation tier.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_PEACEKEEPER_EMBLEM,
            "Peacekeeper Emblem",
            "Reach Heroic status while resolving at least three encounters through charm.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_MERCY_CROWN,
            "Mercy Crown",
            "Complete every seeded quest in a kill-free run.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_BATTLE_HARDENED,
            "Battle Hardened",
            "Defeat five enemies in lethal combat.",
            TrophyCategory.COMBAT,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_WAR_VETERAN,
            "War Veteran",
            "Defeat twenty enemies in lethal combat.",
            TrophyCategory.COMBAT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_CRIMSON_REAPER,
            "Crimson Reaper",
            "Defeat thirty-five enemies in lethal combat.",
            TrophyCategory.COMBAT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_APEX_PREDATOR,
            "Apex Predator",
            "Defeat fifty enemies in lethal combat.",
            TrophyCategory.COMBAT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_RISING_NINJA,
            "Rising Ninja",
            "Reach level 5.",
            TrophyCategory.PROGRESSION,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_SEASONED_NINJA,
            "Seasoned Ninja",
            "Reach level 10.",
            TrophyCategory.PROGRESSION,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_LOYAL_BONDS,
            "Loyal Bonds",
            "Build high loyalty with three or more allies.",
            TrophyCategory.SOCIAL,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_VILLAIN_SLAYER,
            "Villain Slayer",
            "Defeat every red-bar villain in the world.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_QUESTMASTER,
            "Questmaster",
            "Complete every seeded quest.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_SHADOW_HEIR,
            "Shadow Heir",
            "Clear every region as the Exiled Heir.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_GHOST_SOVEREIGN,
            "Ghost Sovereign",
            "Clear every region as the Street Ghost.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_MONK_ASCENDANT,
            "Monk Ascendant",
            "Clear every region as the Wandering Monk.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
    ]
    return {trophy.key: trophy for trophy in trophies}


def _seed_shop_inventory() -> Dict[str, Dict[str, Any]]:
    return {
        "market_smoke_bomb": {
            "name": "Market Smoke Bomb",
            "reward_type": "move",
            "reward_name": "Smoke Lattice",
            "price": 40,
            "min_reputation": -49,
            "max_reputation": 1000,
            "requires_black_market": False,
        },
        "rogue_shadow_wrap": {
            "name": "Rogue Shadow Wrap",
            "reward_type": "clothing",
            "reward_name": "Shadow Wrap",
            "price": 70,
            "min_reputation": -1000,
            "max_reputation": -20,
            "requires_black_market": True,
        },
        "black_market_kunai": {
            "name": "Black Market Kunai",
            "reward_type": "weapon",
            "reward_name": "Nightglass Kunai",
            "price": 90,
            "min_reputation": -1000,
            "max_reputation": 1000,
            "requires_black_market": True,
        },
        "pacifist_thread_charm": {
            "name": "Pacifist Thread Charm",
            "reward_type": "move",
            "reward_name": "Mercy Knot",
            "price": 75,
            "min_reputation": -1000,
            "max_reputation": 1000,
            "requires_black_market": False,
            "requires_nonlethal": True,
        },
        "silent_legend_insignia": {
            "name": "Silent Legend Insignia",
            "reward_type": "clothing",
            "reward_name": "Moonveil Crest",
            "price": 120,
            "min_reputation": -1000,
            "max_reputation": 1000,
            "requires_black_market": False,
            "requires_nonlethal": True,
            "min_nonlethal_actions": 8,
            "requires_world_clear_nonlethal": True,
        },
    }


def build_mvp_world(player_name: str, affinity_decisions: Sequence[int]) -> Tuple[NinjaWorld, PlayerProfile]:
    """Build the MVP world and player state.

    ``affinity_decisions`` is an integer sequence from the affinity mini-game;
    values are accumulated and mapped cyclically to Fire, Water, Earth, Wind.
    The top score determines the starting affinity.
    """
    affinity = resolve_affinity_minigame(affinity_decisions)
    player = PlayerProfile(name=player_name, affinity=affinity)
    regions = _seed_regions()
    _validate_boss_move_reward_config(regions)

    for move_set, moves in _seed_moves(affinity).items():
        for move in moves:
            player.add_move(move, allow_cross_affinity=True)

    world = NinjaWorld(
        regions=regions,
        quests=_seed_quests(),
        allies=_seed_allies(),
        weapons=_seed_weapons(),
        skins=[
            Skin("Founder's Garb", {"power": 2, "focus": 1}),
            Skin("Rogue Nightwear", {"agility": 3}),
        ],
        villains=_seed_villains(),
        villain_behavior_rules=_seed_villain_behavior_rules(),
        player_backstories=_seed_player_backstories(),
        trophy_catalog=_seed_trophy_catalog(),
        arcs=_seed_arcs(),
        era_timeline=_seed_era_timeline(),
        ninjutsu_library=_seed_ninjutsu_library(),
        shop_inventory=_seed_shop_inventory(),
    )
    player.weapons.extend(world.weapons)
    player.unlocked_skins.append(world.skins[0])
    player.initialize_quest_log([quest.quest_id for quest in world.quests])
    for ally in world.allies:
        player.ally_loyalty[ally] = 0
    world._refresh_arc_and_era()
    world._schedule_dynamic_regions(player)
    world._log_tapestry(
        event_type="arc_shift",
        label="Run initialized with opening political arc.",
        causes=["new_run"],
        effects={
            "scheduled_regions": list(world.dynamic_region_chain),
            "era": world._current_era()["key"],
        },
    )
    return world, player
