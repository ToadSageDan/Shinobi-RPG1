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


@dataclass
class Quest:
    quest_id: str
    title: str
    objective: str
    stealth_required: bool
    reward_xp: int
    branch_outcomes: Dict[str, str] = field(default_factory=dict)


@dataclass
class Region:
    name: str
    village_hub: str
    enemies: List[str]
    allies: List[str]
    boss: str
    boss_rewards: Dict[str, str]
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
        if move.category == MoveCategory.ATTACK:
            damage = int(self.stats.power * move.power_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "damage": damage,
                "applied_statuses": [effect.value for effect in move.status_effects],
            }
        if move.category == MoveCategory.DEFENSE:
            guard = int(self.stats.defense * move.power_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "guard": guard,
                "applied_statuses": [effect.value for effect in move.status_effects],
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
            }
        if move.category == MoveCategory.ULTIMATE:
            damage = int((self.stats.power + self.stats.focus) * move.power_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "damage": damage,
                "applied_statuses": [effect.value for effect in move.status_effects],
            }
        if move.category == MoveCategory.SUMMON:
            summon_power = int((self.stats.focus + self.stats.defense) * move.power_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "summon_power": summon_power,
                "summon_type": move.jutsu_type.value,
                "applied_statuses": [effect.value for effect in move.status_effects],
            }
        raise ValueError(f'Unsupported move category "{move.category.value}".')

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
    ninjutsu_library: List[Move] = field(default_factory=list)
    shop_inventory: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    vault_historic_ninjas: List[dict] = field(default_factory=list)

    def clear_region(
        self,
        player: PlayerProfile,
        region_name: str,
        reward_choice: str,
    ) -> str:
        region_index = next((idx for idx, r in enumerate(self.regions) if r.name == region_name), -1)
        if region_index == -1:
            raise ValueError(f'Region "{region_name}" not found.')
        region = self.regions[region_index]
        if region.cleared:
            raise ValueError(f'Region "{region_name}" has already been cleared.')
        if region_index > 0 and not self.regions[region_index - 1].cleared:
            raise ValueError("Previous region must be cleared first.")
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
        self.evaluate_trophies(player)
        return reward_name

    def archive_historic_ninja(self, player: PlayerProfile) -> None:
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
            }
        )

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
        self.evaluate_trophies(player)

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
                }
            )
        return {"combo_path": staged}

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

    def resolve_quest_branch(self, player: PlayerProfile, quest_id: str) -> Dict[str, str]:
        quest = next((q for q in self.quests if q.quest_id == quest_id), None)
        if not quest:
            raise ValueError(f'Quest "{quest_id}" not found.')

        if not quest.branch_outcomes:
            return {
                "quest_id": quest.quest_id,
                "title": quest.title,
                "branch_key": "default",
                "outcome": quest.objective,
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
        }

    def start_quest(self, player: PlayerProfile, quest_id: str) -> Dict[str, str]:
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

    def _resolve_branch_key(self, player: PlayerProfile, branch_outcomes: Dict[str, str]) -> str:
        """Resolve branch precedence: explicit backstory first, then narrative tags, then default.

        Narrative tags are checked in alphabetical order to keep matching deterministic.
        """
        if player.selected_backstory and player.selected_backstory.key in branch_outcomes:
            return player.selected_backstory.key
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

        return newly_awarded

    def generate_playthrough_summary(self, player: PlayerProfile) -> Dict[str, Any]:
        trophy_details = [
            {
                "key": key,
                "name": self.trophy_catalog[key].name,
                "category": self.trophy_catalog[key].category.value,
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
            "trophies": trophy_details,
            "trophy_progress": self.get_trophy_progress(player),
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
        }
        nonlethal_actions = player.nonlethal_action_count()
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
            else:
                current_value = player.encounter_outcomes.get(metric_key, 0)
            remaining = max(target - current_value, 0)
            if trophy.key == TROPHY_SILENT_LEGEND and player.encounter_outcomes["kill"] > 0:
                remaining = target
            progress.append(
                {
                    "key": trophy.key,
                    "name": trophy.name,
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
                        "objective": quest.objective,
                        "stealth_required": quest.stealth_required,
                        "reward_xp": quest.reward_xp,
                        "branch_outcomes": dict(quest.branch_outcomes),
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
                objective=item["objective"],
                stealth_required=item["stealth_required"],
                reward_xp=item["reward_xp"],
                branch_outcomes=dict(item.get("branch_outcomes", {})),
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
            ninjutsu_library=ninjutsu_library,
            shop_inventory={key: dict(value) for key, value in world_snapshot.get("shop_inventory", {}).items()},
            vault_historic_ninjas=list(world_snapshot.get("vault_historic_ninjas", [])),
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
    return [
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
    ]


def _seed_allies(min_count: int = 10) -> List[str]:
    """Return ally names with seeded characters plus autogenerated fillers.

    Guarantees at least ``min_count`` allies for early world population.
    ``AutoNinja-*`` placeholders are MVP-safe filler names until a richer
    ally-name pool is added.
    """
    allies = ["Dan", "Moon", "Sleep", "Dot", "Porter"]
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
        ),
        Trophy(
            TROPHY_GHOST_STEP,
            "Ghost Step",
            "Complete three encounters through stealth.",
            TrophyCategory.STEALTH,
        ),
        Trophy(
            TROPHY_SILVER_TONGUE,
            "Silver Tongue",
            "Resolve three encounters through charm.",
            TrophyCategory.SOCIAL,
        ),
        Trophy(
            TROPHY_WINDWALK_SURVIVOR,
            "Windwalk Survivor",
            "Escape danger through evasion three times.",
            TrophyCategory.STEALTH,
        ),
        Trophy(
            TROPHY_VEIL_MASTER,
            "Veil Master",
            "Complete five encounters through stealth.",
            TrophyCategory.STEALTH,
        ),
        Trophy(
            TROPHY_DIPLOMAT_SUPREME,
            "Diplomat Supreme",
            "Resolve five encounters through charm.",
            TrophyCategory.SOCIAL,
        ),
        Trophy(
            TROPHY_PACIFIST_SHADOW,
            "Pacifist Shadow",
            "Maintain a kill-free run while using charm, stealth, and evasion tactics.",
            TrophyCategory.ALIGNMENT,
        ),
        Trophy(
            TROPHY_SILENT_LEGEND,
            "Silent Legend",
            "Clear every seeded region in a kill-free run.",
            TrophyCategory.ALIGNMENT,
        ),
        Trophy(
            TROPHY_PHANTOM_VEIL,
            "Phantom Veil",
            "Complete eight encounters through stealth.",
            TrophyCategory.STEALTH,
        ),
        Trophy(
            TROPHY_HARMONY_VOICE,
            "Harmony Voice",
            "Resolve eight encounters through charm.",
            TrophyCategory.SOCIAL,
        ),
        Trophy(
            TROPHY_UNTOUCHABLE_GHOST,
            "Untouchable Ghost",
            "Escape danger through evasion five times.",
            TrophyCategory.STEALTH,
        ),
        Trophy(
            TROPHY_TRINITY_OPERATOR,
            "Trinity Operator",
            "Use charm, stealth, and evasion at least twice each without any kills.",
            TrophyCategory.ALIGNMENT,
        ),
        Trophy(
            TROPHY_ORIGIN_AWAKENED,
            "Origin Awakened",
            "Choose a protagonist backstory and set your narrative path.",
            TrophyCategory.PROGRESSION,
        ),
        Trophy(
            TROPHY_FIRST_BLOODLINE_VICTORY,
            "First Bloodline Victory",
            "Clear your first region and claim a boss reward.",
            TrophyCategory.PROGRESSION,
        ),
        Trophy(
            TROPHY_WORLD_WALKER,
            "World Walker",
            "Clear every seeded region in the current world.",
            TrophyCategory.PROGRESSION,
        ),
        Trophy(
            TROPHY_ROGUE_ASCENDANT,
            "Rogue Ascendant",
            "Reach Rogue reputation tier.",
            TrophyCategory.ALIGNMENT,
        ),
        Trophy(
            TROPHY_HEROIC_CREST,
            "Heroic Crest",
            "Reach Heroic reputation tier.",
            TrophyCategory.ALIGNMENT,
        ),
        Trophy(
            TROPHY_PEACEKEEPER_EMBLEM,
            "Peacekeeper Emblem",
            "Reach Heroic status while resolving at least three encounters through charm.",
            TrophyCategory.ALIGNMENT,
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
        ninjutsu_library=_seed_ninjutsu_library(),
        shop_inventory=_seed_shop_inventory(),
    )
    player.weapons.extend(world.weapons)
    player.unlocked_skins.append(world.skins[0])
    player.initialize_quest_log([quest.quest_id for quest in world.quests])
    for ally in world.allies:
        player.ally_loyalty[ally] = 0
    return world, player
