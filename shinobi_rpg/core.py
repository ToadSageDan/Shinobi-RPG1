from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
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
    ULTIMATE = "ultimate"


class WeaponType(str, Enum):
    SWORD = "sword"
    KUNAI = "kunai"
    BOW_STAFF = "bow_staff"
    NINJA_STARS = "ninja_stars"


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

# Reputation at or below this value unlocks Rogue Ninja state and Black Market.
ROGUE_THRESHOLD_MIN = -50
# Reputation at or above this value sets Heroic status.
HEROIC_THRESHOLD_MIN = 50
# Base XP requirement per level in the level-based progression curve.
BASE_XP_PER_LEVEL = 100
DECISION_OUTCOMES = {"kill", "charm", "stealth", "evasion"}
STEALTH_TROPHY_BASE_THRESHOLD = 3
STEALTH_TROPHY_ADVANCED_THRESHOLD = 5
CHARM_TROPHY_BASE_THRESHOLD = 3
CHARM_TROPHY_ADVANCED_THRESHOLD = 5
EVASION_TROPHY_THRESHOLD = 3
PACIFIST_TROPHY_ACTIONS_THRESHOLD = 5
TROPHY_FIRST_STRIKE = "first_strike"
TROPHY_GHOST_STEP = "ghost_step"
TROPHY_SILVER_TONGUE = "silver_tongue"
TROPHY_WINDWALK_SURVIVOR = "windwalk_survivor"
TROPHY_VEIL_MASTER = "veil_master"
TROPHY_DIPLOMAT_SUPREME = "diplomat_supreme"
TROPHY_PACIFIST_SHADOW = "pacifist_shadow"
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
    aggression_score: int = 0
    stance: VillainStance = VillainStance.BALANCED

    def apply_decision(self, decision_tag: str, intensity: int = 1) -> VillainStance:
        """Update villain temperament from player decisions over time."""
        normalized = decision_tag.strip().lower()
        if normalized in {"kill", "aggressive", "betray"}:
            self.aggression_score += 2 * intensity
        elif normalized in {"stealth", "evasion"}:
            self.aggression_score += intensity
        elif normalized in {"charm", "mercy", "diplomacy"}:
            self.aggression_score -= 2 * intensity

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
    moves_by_set: Dict[MoveCategory, List[Move]] = field(
        default_factory=lambda: {
            MoveCategory.ESCAPE: [],
            MoveCategory.ATTACK: [],
            MoveCategory.DEFENSE: [],
            MoveCategory.ULTIMATE: [],
        }
    )
    selected_backstory: Backstory | None = None
    narrative_tags: Set[str] = field(default_factory=set)
    encounter_outcomes: Dict[str, int] = field(
        default_factory=lambda: {"kill": 0, "charm": 0, "stealth": 0, "evasion": 0}
    )
    trophies: Set[str] = field(default_factory=set)

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
        nonlethal_actions = (
            self.encounter_outcomes["charm"]
            + self.encounter_outcomes["stealth"]
            + self.encounter_outcomes["evasion"]
        )
        return self.encounter_outcomes["kill"] == 0 and nonlethal_actions > 0

    def current_reputation_tier(self) -> ReputationTier:
        return _reputation_tier_for(self.reputation)

    def add_move(self, move: Move) -> None:
        move.validate()
        if move.category != MoveCategory.ULTIMATE and (
            not move.affinities or move.affinities[0] != self.affinity
        ):
            raise ValueError("Non-ultimate moves must match player affinity.")
        self.moves_by_set[move.category].append(move)

    def get_move(self, move_name: str) -> Move:
        for move_set in self.moves_by_set.values():
            for move in move_set:
                if move.name == move_name:
                    return move
        raise ValueError(f'Move "{move_name}" is not unlocked for this player.')

    def execute_move(self, move_name: str, *, escape_difficulty: int = 6) -> Dict[str, Any]:
        """Execute an unlocked move and return deterministic MVP combat output.

        ``escape_difficulty`` is only used for Escape moves and ignored for
        Attack, Defense, and Ultimate categories.
        """
        move = self.get_move(move_name)
        if move.category == MoveCategory.ATTACK:
            damage = int(self.stats.power * move.power_scale)
            return {"move": move.name, "category": move.category.value, "damage": damage}
        if move.category == MoveCategory.DEFENSE:
            guard = int(self.stats.defense * move.power_scale)
            return {"move": move.name, "category": move.category.value, "guard": guard}
        if move.category == MoveCategory.ESCAPE:
            escape_score = int(self.stats.agility * move.power_scale)
            escaped = escape_score >= escape_difficulty
            return {
                "move": move.name,
                "category": move.category.value,
                "escape_score": escape_score,
                "escaped": escaped,
            }
        if move.category == MoveCategory.ULTIMATE:
            damage = int((self.stats.power + self.stats.focus) * move.power_scale)
            return {"move": move.name, "category": move.category.value, "damage": damage}
        raise ValueError(f'Unsupported move category "{move.category.value}".')

    def resolve_block_parry(
        self,
        incoming_damage: int,
        *,
        base_guard_scale: float = 0.5,
        parry_difficulty: int = 6,
    ) -> Dict[str, Any]:
        """Resolve defensive block/parry output with a no-defense fallback."""
        if incoming_damage < 0:
            raise ValueError("Incoming damage cannot be negative.")
        if base_guard_scale <= 0:
            raise ValueError("Base guard scale must be greater than zero.")
        if parry_difficulty < 0:
            raise ValueError("Parry difficulty cannot be negative.")

        defense_moves = self.moves_by_set[MoveCategory.DEFENSE]
        selected_move = max(defense_moves, key=lambda move: move.power_scale) if defense_moves else None
        guard_scale = selected_move.power_scale if selected_move else base_guard_scale
        guard = int(self.stats.defense * guard_scale)
        parry_score = int(self.stats.agility * guard_scale)
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

    def grant_boss_reward(self, reward_type: str, reward_name: str) -> None:
        if reward_type not in self.reward_inventory:
            raise ValueError("Reward choice must be weapon, clothing, or move.")
        if reward_name in self.reward_inventory[reward_type]:
            raise ValueError(f'"{reward_name}" has already been granted for {reward_type}.')
        self.reward_inventory[reward_type].append(reward_name)


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
        player.unlock_fast_travel(region.name)
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
            }
        )

    def apply_player_decision(self, player: PlayerProfile, decision_tag: str, intensity: int = 1) -> None:
        normalized = decision_tag.strip().lower()
        for villain in self.villains:
            villain.apply_decision(normalized, intensity=intensity)
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

    def get_region_boss_behavior(self, region_name: str, player: PlayerProfile) -> Dict[str, str]:
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
        if player.is_nonlethal_path_active() and (
            player.encounter_outcomes["charm"]
            + player.encounter_outcomes["stealth"]
            + player.encounter_outcomes["evasion"]
        ) >= PACIFIST_TROPHY_ACTIONS_THRESHOLD:
            _award(TROPHY_PACIFIST_SHADOW)
        if player.selected_backstory:
            _award(TROPHY_ORIGIN_AWAKENED)
        cleared_regions = sum(1 for region in self.regions if region.cleared)
        if cleared_regions >= 1:
            _award(TROPHY_FIRST_BLOODLINE_VICTORY)
        if cleared_regions >= len(self.regions):
            _award(TROPHY_WORLD_WALKER)
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
            "trophies": trophy_details,
        }


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


def _seed_weapons() -> List[Weapon]:
    return [
        Weapon("Dawn Cutter", WeaponType.SWORD, "balanced duelist", 18),
        Weapon("Silent Fang", WeaponType.KUNAI, "high-mobility burst", 14),
        Weapon("Temple Branch", WeaponType.BOW_STAFF, "control and spacing", 16),
        Weapon("Storm Scatter", WeaponType.NINJA_STARS, "ranged precision", 15),
    ]


def _seed_moves(player_affinity: Affinity) -> Dict[MoveCategory, List[Move]]:
    return {
        MoveCategory.ESCAPE: [
            Move("Smoke Step", MoveCategory.ESCAPE, (player_affinity,), power_scale=0.6)
        ],
        MoveCategory.ATTACK: [
            Move("Edge Current", MoveCategory.ATTACK, (player_affinity,), power_scale=1.0)
        ],
        MoveCategory.DEFENSE: [
            Move("Guarding Veil", MoveCategory.DEFENSE, (player_affinity,), power_scale=0.8)
        ],
        MoveCategory.ULTIMATE: [
            Move(
                "Twin Dragon Convergence",
                MoveCategory.ULTIMATE,
                (player_affinity, _paired_affinity_for_ultimate(player_affinity)),
                power_scale=2.5,
            )
        ],
    }


def _seed_regions() -> List[Region]:
    return [
        Region(
            name="Verdant Gate",
            village_hub="Leafrise Village",
            enemies=["Bandit Scouts", "Mist Ronin", "Root Stalkers"],
            allies=["Dan"],
            boss="Kage Renda",
            boss_rewards={
                "weapon": "Renda Fang Blade",
                "clothing": "Shadow Mantle",
                "move": "Rending Spiral",
            },
        ),
        Region(
            name="Ashen Cradle",
            village_hub="Cinder Port",
            enemies=["Ash Mercenaries", "Lava Hounds"],
            allies=["Moon", "Sleep"],
            boss="General Voln",
            boss_rewards={
                "weapon": "Cradle Cleaver",
                "clothing": "Molten Gi",
                "move": "Ember Cyclone",
            },
        ),
        Region(
            name="Tideglass Basin",
            village_hub="Azure Rest",
            enemies=["Tide Hunters", "Reef Assassins"],
            allies=["Dot", "Porter"],
            boss="Admiral Neris",
            boss_rewards={
                "weapon": "Basin Pike",
                "clothing": "Tidewoven Cloak",
                "move": "Abyss Arc",
            },
        ),
    ]


def _seed_quests() -> List[Quest]:
    return [
        Quest(
            quest_id="Q1",
            title="Trial of Quiet Steps",
            objective="Infiltrate the watchpost unseen and recover clan records.",
            stealth_required=True,
            reward_xp=120,
            branch_outcomes={
                "street_ghost": "Your underworld contacts open a tunnel route into the watchpost.",
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
    return [
        VillainProfile(
            name="Kage Renda",
            backstory="A fallen bodyguard who distrusts direct violence and respects subtlety.",
        ),
        VillainProfile(
            name="General Voln",
            backstory="A warlord strategist who escalates force when the player leaves survivors.",
            aggression_score=1,
        ),
        VillainProfile(
            name="Admiral Neris",
            backstory="A former naval hero who can be swayed by diplomacy and mercy.",
        ),
    ]


def _seed_villain_behavior_rules() -> Dict[str, Dict[VillainStance, str]]:
    return {
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


def build_mvp_world(player_name: str, affinity_decisions: Sequence[int]) -> Tuple[NinjaWorld, PlayerProfile]:
    """Build the MVP world and player state.

    ``affinity_decisions`` is an integer sequence from the affinity mini-game;
    values are accumulated and mapped cyclically to Fire, Water, Earth, Wind.
    The top score determines the starting affinity.
    """
    affinity = resolve_affinity_minigame(affinity_decisions)
    player = PlayerProfile(name=player_name, affinity=affinity)

    for move_set, moves in _seed_moves(affinity).items():
        for move in moves:
            player.moves_by_set[move_set].append(move)

    world = NinjaWorld(
        regions=_seed_regions(),
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
    )
    player.weapons.extend(world.weapons)
    player.unlocked_skins.append(world.skins[0])
    return world, player
