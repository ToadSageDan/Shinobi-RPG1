from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Sequence, Tuple


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
AFFINITY_ORDER = [Affinity.FIRE, Affinity.WATER, Affinity.EARTH, Affinity.WIND]
AFFINITY_MINIGAME_CHOICES = {
    "fire": Affinity.FIRE,
    "water": Affinity.WATER,
    "earth": Affinity.EARTH,
    "wind": Affinity.WIND,
}


def _empty_affinity_scores() -> Dict[Affinity, int]:
    return {affinity: 0 for affinity in AFFINITY_ORDER}


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


@dataclass
class Quest:
    quest_id: str
    title: str
    objective: str
    stealth_required: bool
    reward_xp: int


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

    def update_reputation(self, delta: int) -> ReputationTier:
        self.reputation += delta
        if self.reputation <= ROGUE_THRESHOLD_MIN:
            if "black_market" not in self.unlocked_zones:
                self.unlocked_zones.append("black_market")
            return ReputationTier.ROGUE
        if self.reputation >= HEROIC_THRESHOLD_MIN:
            return ReputationTier.HEROIC
        return ReputationTier.NEUTRAL

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
        return reward_name

    def archive_historic_ninja(self, player: PlayerProfile) -> None:
        self.vault_historic_ninjas.append(
            {
                "name": player.name,
                "affinity": player.affinity.value,
                "level": player.stats.level,
                "reputation": player.reputation,
            }
        )


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

    MVP design pairs Wind with Fire; all other primaries pair with Wind.
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
        ),
        Quest(
            quest_id="Q2",
            title="Allies in the Dark",
            objective="Escort Dan through the forest and repel ambushes.",
            stealth_required=False,
            reward_xp=140,
        ),
        Quest(
            quest_id="Q3",
            title="Break the Gate",
            objective="Defeat Kage Renda and secure Verdant Gate.",
            stealth_required=False,
            reward_xp=220,
        ),
    ]


def _seed_allies(min_count: int = 10) -> List[str]:
    """Return ally names with seeded characters plus autogenerated fillers.

    Guarantees at least ``min_count`` allies for early world population.
    """
    allies = ["Dan", "Moon", "Sleep", "Dot", "Porter"]
    index = 1
    while len(allies) < min_count:
        allies.append(f"AutoNinja-{index}")
        index += 1
    return allies


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
    )
    player.weapons.extend(world.weapons)
    player.unlocked_skins.append(world.skins[0])
    return world, player
