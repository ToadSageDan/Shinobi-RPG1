from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Sequence, Set, Tuple

from ._constants import *
from ._types import *

def _empty_affinity_scores() -> Dict[Affinity, int]:
    return {affinity: 0 for affinity in AFFINITY_ORDER}


def _ordered_unique_affinities(affinities: Sequence[Affinity]) -> Tuple[Affinity, ...]:
    return tuple(dict.fromkeys(affinities))


def _region_encounter_xp_reward(encounter_name: str) -> int:
    normalized = encounter_name.strip().lower()
    shinobi_markers = (
        "shinobi",
        "ronin",
        "mercenar",
        "raider",
        "assassin",
        "monk",
        "scout",
        "hunter",
        "corsair",
        "adept",
        "stalker",
    )
    animal_markers = ("hound", "wolf", "boar", "mole", "otter", "bat")
    if "guard" in normalized or "sentry" in normalized:
        return REGION_ENCOUNTER_XP_GUARD
    if any(marker in normalized for marker in animal_markers):
        return REGION_ENCOUNTER_XP_ANIMAL
    if any(marker in normalized for marker in shinobi_markers):
        return REGION_ENCOUNTER_XP_SHINOBI
    return REGION_ENCOUNTER_XP_OTHER


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
    technique_type: TechniqueType = TechniqueType.ELEMENTAL
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
class RivalProfile:
    """A persistent rival shinobi that races the player through the world."""

    name: str
    affinity: Affinity
    alignment: str = "neutral"          # mirrors/opposes player: "mirror", "opposing", "neutral"
    cleared_regions: List[str] = field(default_factory=list)
    encounter_count: int = 0
    relationship: str = "stranger"      # stranger → rival → friend / nemesis
    loot_claims: List[str] = field(default_factory=list)

    def advance_region(self, region_name: str) -> None:
        if region_name not in self.cleared_regions:
            self.cleared_regions.append(region_name)

    def update_relationship(self, player_reputation: int, player_alignment: str) -> str:
        if self.encounter_count >= 3:
            alignment_matches = player_alignment == self.alignment
            # Heroic reputation nudges toward friendship; rogue reputation toward nemesis.
            # These override alignment when reputation is strongly committed (|rep| >= 50).
            if player_reputation >= 50:
                self.relationship = "friend"
            elif player_reputation <= -50:
                self.relationship = "nemesis"
            elif alignment_matches:
                self.relationship = "friend"
            else:
                self.relationship = "nemesis"
        elif self.encounter_count >= 1:
            self.relationship = "rival"
        return self.relationship


@dataclass
class BossEchoForm:
    """An optional harder echo rematch version of a defeated regional boss."""

    region_name: str
    boss_name: str
    echo_stance: VillainStance
    borrowed_move_names: List[str] = field(default_factory=list)
    times_challenged: int = 0
    times_defeated: int = 0

    @property
    def available(self) -> bool:
        return self.times_defeated < self.times_challenged + 1


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
    # Rich narrative fields — backstory expansion and story tie-ins
    power_origin: str = ""
    arc_ties: Tuple[str, ...] = field(default_factory=tuple)
    player_backstory_hooks: Dict[str, str] = field(default_factory=dict)

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
    region_name: str = ""
    city_hub: str = ""
    quest_giver: str = ""


@dataclass
class PointOfInterest:
    name: str
    poi_type: str
    summary: str
    control_faction: str = ""
    threats: Tuple[str, ...] = field(default_factory=tuple)
    services: Tuple[str, ...] = field(default_factory=tuple)
    connected_nodes: Tuple[str, ...] = field(default_factory=tuple)


@dataclass
class CityShop:
    key: str
    name: str
    region_name: str
    city_name: str
    specialty: str
    description: str
    inventory_item_keys: Tuple[str, ...] = field(default_factory=tuple)


@dataclass
class CityNPC:
    name: str
    region_name: str
    city_name: str
    role: str
    disposition: str
    dialogue: str
    services: Tuple[str, ...] = field(default_factory=tuple)
    pickpocket_difficulty: int = 6
    pickpocket_rewards: Tuple[str, ...] = field(default_factory=tuple)


@dataclass
class Region:
    name: str
    village_hub: str
    enemies: List[str]
    allies: List[str]
    boss: str
    boss_rewards: Dict[str, str]
    arc_key: str = "political_war"
    climate: str = "temperate"
    terrain_profile: Tuple[str, ...] = field(default_factory=tuple)
    strategic_value: str = ""
    minimum_level: int = 1
    assassin_hunter_name: str = "Regional Assassin Cell"
    travel_nodes: List[str] = field(default_factory=list)
    points_of_interest: List[PointOfInterest] = field(default_factory=list)
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
        default_factory=lambda: {"weapon": [], "clothing": [], "move": [], "tool": []}
    )
    red_bar_power_claims: Dict[str, str] = field(default_factory=dict)
    enemy_move_claims: Dict[str, str] = field(default_factory=dict)
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
    quest_resolution_state: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    ally_loyalty: Dict[str, int] = field(default_factory=dict)
    encounter_history: Dict[str, int] = field(default_factory=dict)
    credits: int = 100
    active_status_effects: Dict[str, Dict[str, int]] = field(default_factory=dict)
    locked_on_target: str | None = None
    owned_tools: List[str] = field(default_factory=list)
    mobile_fast_travel_node: str | None = None
    action_attributes: Dict[str, int] = field(
        default_factory=lambda: {
            key: int(spec["default"]) for key, spec in ACTION_ATTRIBUTE_SPECS.items()
        }
    )
    attribute_points: int = 0
    pickpocket_history: Dict[str, int] = field(
        default_factory=lambda: {"success": 0, "caught": 0}
    )
    # Feature 3 — Chakra resource
    chakra: int = CHAKRA_START
    # Feature 8 — Move proficiency tracking (move name → 0–100)
    move_proficiency: Dict[str, int] = field(default_factory=dict)
    # Feature 9 — Nonlethal flow state streak counter
    nonlethal_flow_streak: int = 0
    # Feature 12 — Weapon durability (weapon name → 0–100)
    weapon_durability: Dict[str, int] = field(default_factory=dict)
    # Feature 6 — Tracks consecutive non-reputation-changing decisions for decay
    reputation_inactivity_ticks: int = 0

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
            key=lambda item: (-item[1], OUTCOME_BRANCH_PATH_KEYS[item[0]]),
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
            existing = self.active_status_effects.get(effect.value)
            if existing:
                # Accumulate stacks up to the band cap; refresh duration to the higher value
                band = STATUS_EFFECT_BANDS[effect]
                new_stacks = min(existing["stacks"] + clamped["stacks"], band["max_stacks"])
                new_duration = max(existing["duration"], clamped["duration"])
                self.active_status_effects[effect.value] = {"duration": new_duration, "stacks": new_stacks}
            else:
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

    def set_lock_on_target(self, target_name: str) -> str:
        target = target_name.strip()
        if not target:
            raise ValueError("Lock-on target cannot be empty.")
        self.locked_on_target = target
        return target

    def clear_lock_on_target(self) -> None:
        self.locked_on_target = None

    def _resolve_targeting_profile(
        self,
        move: Move,
        *,
        target_name: str | None,
        lock_on: bool,
    ) -> Dict[str, Any]:
        if move.category in {MoveCategory.DEFENSE, MoveCategory.ESCAPE}:
            mode = "self"
        else:
            lowered_name = move.name.lower()
            if any(term in lowered_name for term in AOE_TARGETING_TERMS):
                mode = "aoe"
            elif any(term in lowered_name for term in STRAIGHT_LINE_TARGETING_TERMS):
                mode = "straight_line"
            else:
                mode = "tracking"

        tracking_required = move.category in {MoveCategory.ATTACK, MoveCategory.ULTIMATE} and mode == "tracking"
        selected_target = target_name.strip() if target_name is not None and target_name.strip() else None

        if lock_on:
            if selected_target is not None:
                self.set_lock_on_target(selected_target)
            elif self.locked_on_target is None:
                raise ValueError("Lock-on requires a target name when no lock target is currently set.")
        current_target = self.locked_on_target if lock_on else selected_target

        return {
            "mode": mode,
            "tracking_required": tracking_required,
            "target": current_target,
            "lock_on_active": lock_on and self.locked_on_target is not None,
            "tracking_applied": tracking_required and current_target is not None,
        }

    def execute_move(
        self,
        move_name: str,
        *,
        escape_difficulty: int = 6,
        target_name: str | None = None,
        lock_on: bool = False,
        weapon_name: str | None = None,
    ) -> Dict[str, Any]:
        """Execute an unlocked move and return deterministic MVP combat output.

        ``escape_difficulty`` is only used for Escape moves and ignored for
        Attack, Defense, and Ultimate categories.

        ``weapon_name`` optionally names the weapon being used.  When provided
        and the weapon is in the player's reward inventory, its durability is
        degraded each call and the resulting power ratio is applied to all
        damage / guard / power values.

        Chakra is consumed automatically based on move category; the remaining
        chakra and an ``insufficient_chakra`` flag are always included in the
        returned result so callers can react to chakra exhaustion.  Move
        proficiency is also tracked: each call restores proficiency for the
        executed move (reversing decay from unused encounters) and applies a
        scale modifier that reduces effectiveness below the low threshold.
        """
        move = self.get_move(move_name)
        if move.status_effects:
            self.apply_status_effects(move.status_effects)
        combat_physics = self._build_combat_physics(move)
        combat_targeting = self._resolve_targeting_profile(move, target_name=target_name, lock_on=lock_on)

        # --- Feature 3: Chakra ---
        chakra_sufficient = self.consume_chakra(move.category.value)

        # --- Feature 8: Move proficiency ---
        proficiency_result = self.use_move_proficiency(move_name)
        proficiency_modifier = proficiency_result["scale_modifier"]

        # --- Feature 12: Weapon durability (optional) ---
        durability_ratio = 1.0
        durability_result: Dict[str, Any] | None = None
        if weapon_name is not None and weapon_name in self.reward_inventory.get("weapon", []):
            durability_result = self.degrade_weapon(weapon_name)
            durability_ratio = durability_result["power_ratio"]

        effective_scale = move.power_scale * proficiency_modifier * durability_ratio

        chakra_meta = {
            "chakra_remaining": self.chakra,
            "insufficient_chakra": not chakra_sufficient,
            "proficiency": proficiency_result["proficiency"],
            "proficiency_modifier": proficiency_modifier,
            "durability_ratio": durability_ratio,
        }

        if move.category == MoveCategory.ATTACK:
            damage = int(self.stats.power * effective_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "damage": damage,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
                "combat_targeting": combat_targeting,
                **chakra_meta,
            }
        if move.category == MoveCategory.DEFENSE:
            guard = int(self.stats.defense * effective_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "guard": guard,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
                "combat_targeting": combat_targeting,
                **chakra_meta,
            }
        if move.category == MoveCategory.ESCAPE:
            escape_score = int(self.stats.agility * effective_scale)
            escaped = escape_score >= escape_difficulty
            return {
                "move": move.name,
                "category": move.category.value,
                "escape_score": escape_score,
                "escaped": escaped,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
                "combat_targeting": combat_targeting,
                **chakra_meta,
            }
        if move.category == MoveCategory.ULTIMATE:
            damage = int((self.stats.power + self.stats.focus) * effective_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "damage": damage,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
                "combat_targeting": combat_targeting,
                **chakra_meta,
            }
        if move.category == MoveCategory.SUMMON:
            summon_power = int((self.stats.focus + self.stats.defense) * effective_scale)
            return {
                "move": move.name,
                "category": move.category.value,
                "summon_power": summon_power,
                "summon_type": move.technique_type.value,
                "applied_statuses": [effect.value for effect in move.status_effects],
                "combat_physics": combat_physics,
                "combat_targeting": combat_targeting,
                **chakra_meta,
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

    def set_quest_resolution_context(
        self,
        quest_id: str,
        *,
        approach: str | None = None,
        stealth_required: bool | None = None,
        stealth_satisfied: bool | None = None,
        resolved_branch_key: str | None = None,
        completed: bool | None = None,
    ) -> Dict[str, Any]:
        state = self.quest_resolution_state.setdefault(
            quest_id,
            {
                "approach": None,
                "stealth_required": False,
                "stealth_satisfied": True,
                "stealth_gate_open": True,
                "resolved_branch_key": None,
                "completed": False,
            },
        )
        if approach is not None:
            state["approach"] = approach.strip().lower()
        if stealth_required is not None:
            state["stealth_required"] = bool(stealth_required)
        if stealth_satisfied is not None:
            state["stealth_satisfied"] = bool(stealth_satisfied)
        if resolved_branch_key is not None:
            state["resolved_branch_key"] = resolved_branch_key
        if completed is not None:
            state["completed"] = bool(completed)
        state["stealth_gate_open"] = (
            not bool(state.get("stealth_required", False))
            or bool(state.get("stealth_satisfied", False))
        )
        return dict(state)

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

    def gain_attribute_points(self, levels_gained: int) -> int:
        if levels_gained < 0:
            raise ValueError("Levels gained cannot be negative.")
        self.attribute_points += levels_gained * ATTRIBUTE_POINTS_PER_LEVEL
        return self.attribute_points

    def raise_action_attribute(self, attribute_name: str, points: int = 1) -> int:
        normalized = attribute_name.strip().lower()
        if normalized not in ACTION_ATTRIBUTE_SPECS:
            raise ValueError(f'Unknown action attribute "{attribute_name}".')
        if points <= 0:
            raise ValueError("Attribute spend must be greater than zero.")
        if points > self.attribute_points:
            raise ValueError("Insufficient attribute points.")
        cap = int(ACTION_ATTRIBUTE_SPECS[normalized]["cap"])
        current = int(self.action_attributes.get(normalized, ACTION_ATTRIBUTE_SPECS[normalized]["default"]))
        updated = min(cap, current + points)
        spent = updated - current
        if spent <= 0:
            raise ValueError(f'Action attribute "{attribute_name}" is already at cap.')
        self.action_attributes[normalized] = updated
        self.attribute_points -= spent
        return updated

    def resolve_action_check(
        self,
        action_name: str,
        *,
        difficulty: int = 6,
        situational_bonus: int = 0,
    ) -> Dict[str, Any]:
        normalized = action_name.strip().lower()
        if normalized not in ACTION_ATTRIBUTE_SPECS:
            raise ValueError(f'Unknown action attribute "{action_name}".')
        if difficulty < 0:
            raise ValueError("Difficulty cannot be negative.")
        spec = ACTION_ATTRIBUTE_SPECS[normalized]
        linked_stat_name = str(spec["linked_stat"])
        linked_stat_value = int(getattr(self.stats, linked_stat_name))
        attribute_value = int(self.action_attributes.get(normalized, spec["default"]))
        score = attribute_value * 2 + max(1, linked_stat_value // 4) + int(situational_bonus)
        return {
            "action": normalized,
            "attribute_value": attribute_value,
            "linked_stat": linked_stat_name,
            "linked_stat_value": linked_stat_value,
            "score": score,
            "difficulty": difficulty,
            "success": score >= difficulty,
        }

    def grant_boss_reward(self, reward_type: str, reward_name: str) -> None:
        if reward_type not in self.reward_inventory:
            raise ValueError("Reward choice must be weapon, clothing, or move.")
        if reward_name in self.reward_inventory[reward_type]:
            raise ValueError(f'"{reward_name}" has already been granted for {reward_type}.')
        self.reward_inventory[reward_type].append(reward_name)

    def unlock_tool(self, tool_name: str) -> str:
        normalized = tool_name.strip()
        if not normalized:
            raise ValueError("Tool name cannot be empty.")
        if normalized not in self.owned_tools:
            self.owned_tools.append(normalized)
        if normalized not in self.reward_inventory["tool"]:
            self.reward_inventory["tool"].append(normalized)
        return normalized

    def claim_red_bar_power(self, villain_name: str, move: Move) -> None:
        if villain_name in self.red_bar_power_claims:
            return
        self.red_bar_power_claims[villain_name] = move.name
        if move.name not in self.unlocked_move_names:
            self.add_move(move, allow_cross_affinity=True)

    def claim_enemy_exclusive_move(self, enemy_name: str, move: Move) -> bool:
        """Claim an important enemy's exclusive move on first defeat."""
        if enemy_name in self.enemy_move_claims:
            return False
        self.enemy_move_claims[enemy_name] = move.name
        if move.name not in self.unlocked_move_names:
            self.add_move(move, allow_cross_affinity=True)
        return True

    # ------------------------------------------------------------------
    # Feature 1 — Affinity Resonance
    # ------------------------------------------------------------------

    def get_affinity_resonance(self) -> Dict[str, Any]:
        """Return the strongest active resonance bonus for the player's unlocked move set.

        A resonance fires when the player has unlocked at least one non-ultimate
        move in each of two complementary affinities.  The highest-bonus pair wins;
        ties resolve alphabetically by pair label.
        """
        present_affinities: Set[str] = set()
        for moves in self.moves_by_set.values():
            for move in moves:
                if move.category != MoveCategory.ULTIMATE:
                    for affinity in move.affinities:
                        present_affinities.add(affinity.value)

        best: Dict[str, Any] = {"label": "none", "damage_bonus": 0.0, "flavor": "none", "affinities": []}
        for (a1, a2), spec in AFFINITY_RESONANCE_PAIRS.items():
            if a1 in present_affinities and a2 in present_affinities:
                if spec["damage_bonus"] > best["damage_bonus"] or (
                    spec["damage_bonus"] == best["damage_bonus"]
                    and spec["label"] < best["label"]
                ):
                    best = {
                        "label": spec["label"],
                        "damage_bonus": spec["damage_bonus"],
                        "flavor": spec["flavor"],
                        "affinities": [a1, a2],
                    }
        return best

    # ------------------------------------------------------------------
    # Feature 3 — Chakra resource
    # ------------------------------------------------------------------

    def consume_chakra(self, move_category: str) -> bool:
        """Deduct chakra for a move.  Returns True if the player had enough chakra.

        Escape moves regen instead of consuming chakra.
        """
        normalized = move_category.strip().lower()
        if normalized == "escape":
            self.chakra = min(CHAKRA_MAX, self.chakra + CHAKRA_REGEN_ESCAPE)
            return True
        cost = CHAKRA_COST.get(normalized, 10)
        if self.chakra < cost:
            return False
        self.chakra -= cost
        return True

    def restore_chakra(self, amount: int) -> int:
        """Restore chakra up to the cap and return the new value."""
        if amount < 0:
            raise ValueError("Chakra restore amount cannot be negative.")
        self.chakra = min(CHAKRA_MAX, self.chakra + amount)
        return self.chakra

    # ------------------------------------------------------------------
    # Feature 8 — Move proficiency
    # ------------------------------------------------------------------

    def use_move_proficiency(self, move_name: str) -> Dict[str, Any]:
        """Record active use of a move, resetting decay for this encounter.

        Returns the current proficiency and the effective power scale modifier.
        """
        current = self.move_proficiency.get(move_name, MOVE_PROFICIENCY_DEFAULT)
        # Using a move restores proficiency toward the max (diminishing returns).
        restored = min(MOVE_PROFICIENCY_MAX, current + MOVE_PROFICIENCY_DECAY_ON_SKIP)
        self.move_proficiency[move_name] = restored
        scale_mod = self._proficiency_scale_modifier(restored)
        return {"move": move_name, "proficiency": restored, "scale_modifier": scale_mod}

    def decay_unused_move_proficiency(self, used_move_names: Sequence[str]) -> Dict[str, int]:
        """Decay proficiency for every unlocked move that was not used this encounter."""
        decayed: Dict[str, int] = {}
        for name in self.unlocked_move_names:
            if name in used_move_names:
                continue
            current = self.move_proficiency.get(name, MOVE_PROFICIENCY_DEFAULT)
            updated = max(0, current - MOVE_PROFICIENCY_DECAY_ON_SKIP)
            self.move_proficiency[name] = updated
            if updated != current:
                decayed[name] = updated
        return decayed

    @staticmethod
    def _proficiency_scale_modifier(proficiency: int) -> float:
        """Linear interpolation: full scale at cap, floor scale at zero."""
        clamped = max(0, min(MOVE_PROFICIENCY_MAX, proficiency))
        if clamped >= MOVE_PROFICIENCY_LOW_THRESHOLD:
            return 1.0
        ratio = clamped / MOVE_PROFICIENCY_LOW_THRESHOLD
        return MOVE_PROFICIENCY_SCALE_FLOOR + ratio * (1.0 - MOVE_PROFICIENCY_SCALE_FLOOR)

    # ------------------------------------------------------------------
    # Feature 9 — Nonlethal flow state
    # ------------------------------------------------------------------

    def record_nonlethal_chain(self, outcome: str) -> Dict[str, Any]:
        """Track consecutive nonlethal outcomes and activate flow state when threshold is met.

        Returns a dict with the current streak and whether the flow state is active.
        """
        nonlethal_outcomes = {"charm", "stealth", "evasion"}
        normalized = outcome.strip().lower()
        if normalized in nonlethal_outcomes:
            self.nonlethal_flow_streak += 1
        else:
            self.nonlethal_flow_streak = 0
        flow_active = self.nonlethal_flow_streak >= NONLETHAL_FLOW_CHAIN_THRESHOLD
        return {
            "outcome": normalized,
            "streak": self.nonlethal_flow_streak,
            "flow_active": flow_active,
            "free_evasion_available": flow_active and NONLETHAL_FLOW_EVASION_BONUS,
            "stealth_buff_duration": NONLETHAL_FLOW_STEALTH_DURATION if flow_active else 0,
        }

    # ------------------------------------------------------------------
    # Feature 12 — Weapon durability
    # ------------------------------------------------------------------

    def degrade_weapon(self, weapon_name: str) -> Dict[str, Any]:
        """Record combat use of a weapon and reduce its durability.

        Returns the new durability and effective power ratio.
        """
        current = self.weapon_durability.get(weapon_name, WEAPON_DURABILITY_START)
        updated = max(0, current - WEAPON_DURABILITY_LOSS_PER_USE)
        self.weapon_durability[weapon_name] = updated
        power_ratio = self._durability_power_ratio(updated)
        return {
            "weapon": weapon_name,
            "durability": updated,
            "power_ratio": power_ratio,
            "needs_repair": updated <= WEAPON_DURABILITY_LOW_THRESHOLD,
        }

    @staticmethod
    def _durability_power_ratio(durability: int) -> float:
        """Linear scale: full power above low threshold, floor at zero."""
        clamped = max(0, min(WEAPON_DURABILITY_MAX, durability))
        if clamped >= WEAPON_DURABILITY_LOW_THRESHOLD:
            return 1.0
        ratio = clamped / WEAPON_DURABILITY_LOW_THRESHOLD
        return WEAPON_DURABILITY_SCALE_FLOOR + ratio * (1.0 - WEAPON_DURABILITY_SCALE_FLOOR)

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
            "enemy_move_claims": dict(self.enemy_move_claims),
            "moves_by_set": {
                category.value: [
                    {
                        "name": move.name,
                        "category": move.category.value,
                        "affinities": [affinity.value for affinity in move.affinities],
                        "power_scale": move.power_scale,
                        "technique_type": move.technique_type.value,
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
            "quest_resolution_state": {
                quest_id: dict(state) for quest_id, state in self.quest_resolution_state.items()
            },
            "ally_loyalty": dict(self.ally_loyalty),
            "encounter_history": dict(self.encounter_history),
            "credits": self.credits,
            "locked_on_target": self.locked_on_target,
            "owned_tools": list(self.owned_tools),
            "mobile_fast_travel_node": self.mobile_fast_travel_node,
            "action_attributes": {
                key: int(value) for key, value in self.action_attributes.items()
            },
            "attribute_points": self.attribute_points,
            "pickpocket_history": {
                key: int(value) for key, value in self.pickpocket_history.items()
            },
            "active_status_effects": {
                effect_name: {
                    "duration": int(payload.get("duration", 0)),
                    "stacks": int(payload.get("stacks", 0)),
                }
                for effect_name, payload in self.active_status_effects.items()
            },
            "chakra": int(self.chakra),
            "move_proficiency": {k: int(v) for k, v in self.move_proficiency.items()},
            "nonlethal_flow_streak": int(self.nonlethal_flow_streak),
            "weapon_durability": {k: int(v) for k, v in self.weapon_durability.items()},
            "reputation_inactivity_ticks": int(self.reputation_inactivity_ticks),
        }


