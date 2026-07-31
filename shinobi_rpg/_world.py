from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Sequence, Set, Tuple

from ._constants import *
from ._models import *
from ._models import _ordered_unique_affinities, _region_encounter_xp_reward
from ._seed import (
    _boss_exclusive_move_for,
    _seed_arcs,
    _seed_city_npcs,
    _seed_city_shops,
    _seed_era_timeline,
    enemy_exclusive_move_for,
)
from ._types import *

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
    technique_library: List[Move] = field(default_factory=list)
    shop_inventory: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    city_shops: List[CityShop] = field(default_factory=list)
    city_npcs: List[CityNPC] = field(default_factory=list)
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
    npc_evil_profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    city_immersion_state: Dict[str, Dict[str, int]] = field(default_factory=dict)
    npc_consequence_state: Dict[str, Dict[str, int]] = field(default_factory=dict)
    npc_consequence_log: List[Dict[str, Any]] = field(default_factory=list)
    external_pressure_history: List[Dict[str, Any]] = field(default_factory=list)
    intel_discovery_log: List[Dict[str, Any]] = field(default_factory=list)
    arc_transition_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_store: Dict[str, List[str]] = field(default_factory=dict)
    time_cycle_index: int = 0
    weather_cycle_index: int = 0
    environment_cycle_step: int = 0
    # Feature 7 — Rival NPC
    rival_profile: RivalProfile | None = None
    # Feature 10 — Boss echo forms (region_name → BossEchoForm)
    boss_echo_registry: Dict[str, BossEchoForm] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.era_timeline:
            self.era_timeline = _seed_era_timeline()
        if not self.arcs:
            self.arcs = _seed_arcs()
        if not self.city_shops:
            self.city_shops = _seed_city_shops()
        if not self.city_npcs:
            self.city_npcs = _seed_city_npcs()
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
        if not self.npc_evil_profiles:
            self.npc_evil_profiles = self._seed_npc_evil_profiles()
        if not self.city_immersion_state:
            city_names = sorted({npc.city_name for npc in self.city_npcs})
            self.city_immersion_state = {
                city_name: {"alert_level": 0, "intel_noise": 0, "quest_pressure": 0}
                for city_name in city_names
            }
        if not self.npc_consequence_state:
            self.npc_consequence_state = {
                npc.name: {"suspicion": 0, "trust": 0, "intel_shared": 0}
                for npc in self.city_npcs
            }
        self.time_cycle_index = self.time_cycle_index % len(DAY_NIGHT_CYCLE)
        self.weather_cycle_index = self.weather_cycle_index % len(WEATHER_CYCLE)

    def _current_era(self) -> Dict[str, Any]:
        timeline = self.era_timeline or _seed_era_timeline()
        bounded_index = min(max(self.current_era_index, 0), len(timeline) - 1)
        return timeline[bounded_index]

    def _current_arc_phase(self) -> str:
        if self.current_era_index >= 2:
            return "apex"
        if self.current_era_index >= 1:
            return "escalation"
        return "opening"

    def _ensure_quest_resolution_state(
        self, player: PlayerProfile, quest: Quest
    ) -> Dict[str, Any]:
        return player.set_quest_resolution_context(
            quest.quest_id,
            stealth_required=quest.stealth_required,
            stealth_satisfied=not quest.stealth_required
            if quest.quest_id not in player.quest_resolution_state
            else None,
        )

    def record_quest_resolution(
        self,
        player: PlayerProfile,
        quest_id: str,
        *,
        approach: str = "direct",
        stealth_satisfied: bool | None = None,
    ) -> Dict[str, Any]:
        quest = next((q for q in self.quests if q.quest_id == quest_id), None)
        if not quest:
            raise ValueError(f'Quest "{quest_id}" not found.')
        normalized_approach = approach.strip().lower()
        inferred_stealth = normalized_approach == "stealth" if stealth_satisfied is None else stealth_satisfied
        self._ensure_quest_resolution_state(player, quest)
        return player.set_quest_resolution_context(
            quest_id,
            approach=normalized_approach,
            stealth_required=quest.stealth_required,
            stealth_satisfied=(not quest.stealth_required) or bool(inferred_stealth),
        )

    def _emit_arc_transition_event(
        self,
        *,
        previous_phase: str,
        previous_arc_key: str,
        previous_era_key: str,
    ) -> Dict[str, Any]:
        current_phase = self._current_arc_phase()
        current_era = self._current_era()
        record = {
            "event_key": f"arc_transition::{previous_phase}_to_{current_phase}",
            "event_type": "arc_transition",
            "label": f"The world shifts from {previous_phase} to {current_phase}.",
            "from_phase": previous_phase,
            "to_phase": current_phase,
            "from_arc_key": previous_arc_key,
            "to_arc_key": self.current_arc_key,
            "from_era": previous_era_key,
            "to_era": current_era["key"],
            "age": self.current_age,
        }
        self.arc_transition_history.append(record)
        self.world_event_history.append(dict(record))
        self._log_tapestry(
            event_type="arc_transition",
            label=record["label"],
            causes=[f"phase:{previous_phase}", f"phase:{current_phase}"],
            effects={
                "from_arc_key": previous_arc_key,
                "to_arc_key": self.current_arc_key,
                "from_era": previous_era_key,
                "to_era": current_era["key"],
            },
        )
        return record

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
        previous_phase = self._current_arc_phase()
        previous_arc_key = self.current_arc_key
        previous_era_key = self._current_era()["key"]
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
        current_phase = self._current_arc_phase()
        if previous_phase != current_phase and (previous_phase, current_phase) in {
            ("opening", "escalation"),
            ("escalation", "apex"),
        }:
            self._emit_arc_transition_event(
                previous_phase=previous_phase,
                previous_arc_key=previous_arc_key,
                previous_era_key=previous_era_key,
            )

    def get_environment_state(self) -> Dict[str, Any]:
        return {
            "time_of_day": DAY_NIGHT_CYCLE[self.time_cycle_index % len(DAY_NIGHT_CYCLE)],
            "weather": WEATHER_CYCLE[self.weather_cycle_index % len(WEATHER_CYCLE)],
            "cycle_step": self.environment_cycle_step,
        }

    def advance_environment_cycle(self, steps: int = 1) -> Dict[str, Any]:
        if steps <= 0:
            raise ValueError("Environment cycle steps must be greater than zero.")
        self.environment_cycle_step += steps
        self.time_cycle_index = (self.time_cycle_index + steps) % len(DAY_NIGHT_CYCLE)
        # Weather advances at half-speed to avoid overly frequent weather changes.
        self.weather_cycle_index = (self.weather_cycle_index + max(1, steps // 2)) % len(WEATHER_CYCLE)
        return self.get_environment_state()

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

    def _seed_npc_evil_profiles(self) -> Dict[str, Dict[str, Any]]:
        profiles: Dict[str, Dict[str, Any]] = {}
        weighted_tiers: List[str] = []
        for tier, weight in NPC_EVIL_TIER_WEIGHTS:
            weighted_tiers.extend([tier] * max(weight, 1))
        for name in sorted(self.antagonist_candidates):
            seed = sum(ord(ch) for ch in name)
            tier = weighted_tiers[seed % len(weighted_tiers)]
            threshold = NPC_EVIL_TIER_THRESHOLDS[tier]
            profiles[name] = {
                "evil_tier": tier,
                "evil_score": 0,
                "evil_threshold": threshold,
                "can_turn": True,
                "last_trigger": None,
            }
        return profiles

    def _apply_npc_evil_shift(
        self,
        npc_name: str,
        *,
        delta: int,
        event_key: str,
        source: str,
    ) -> Dict[str, Any] | None:
        if npc_name not in self.npc_evil_profiles:
            return None
        profile = self.npc_evil_profiles[npc_name]
        before = int(profile.get("evil_score", 0))
        threshold = int(profile.get("evil_threshold", NPC_EVIL_TIER_THRESHOLDS["balanced"]))
        after = max(-3, min(20, before + delta))
        profile["evil_score"] = after
        profile["last_trigger"] = event_key
        crossed_threshold = before < threshold <= after
        if crossed_threshold:
            self._update_antagonist_scores(
                signal=f"evil_threshold:{event_key}",
                intensity=2,
                focal_points=[npc_name],
                causes=[source],
            )
        record = {
            "npc": npc_name,
            "event_key": event_key,
            "source": source,
            "delta": delta,
            "before": before,
            "after": after,
            "threshold": threshold,
            "crossed_threshold": crossed_threshold,
        }
        self.external_pressure_history.append(record)
        return record

    def trigger_external_pressure_event(
        self,
        player: PlayerProfile,
        *,
        event_key: str | None = None,
        causes: Sequence[str] | None = None,
    ) -> Dict[str, Any]:
        if event_key is None:
            keys = sorted(EXTERNAL_PRESSURE_EVENT_LIBRARY.keys())
            # Blend run progression (history length), world drift (recovery score),
            # and event cadence to keep selection deterministic but non-static.
            selector = (
                len(self.external_pressure_history)
                + len(self.world_event_history)
                + abs(self.world_recovery_score)
            ) % len(keys)
            event_key = keys[selector]
        if event_key not in EXTERNAL_PRESSURE_EVENT_LIBRARY:
            raise ValueError(f'External pressure event "{event_key}" is not recognized.')
        event = dict(EXTERNAL_PRESSURE_EVENT_LIBRARY[event_key])
        if not self.npc_evil_profiles:
            self.npc_evil_profiles = self._seed_npc_evil_profiles()
        candidates = sorted(self.npc_evil_profiles.keys())
        if not candidates:
            raise ValueError("No NPC candidates are available for external pressure events.")
        seed = len(self.external_pressure_history) + len(self.world_event_history) + abs(player.reputation)
        ranked_candidates = sorted(
            candidates,
            key=lambda name: ((sum(ord(ch) for ch in name) + seed) % 97, name),
        )
        target_count = max(1, int(event.get("target_count", 1)))
        targets = ranked_candidates[:target_count]
        span = max(1, int(event.get("max_shift", 1)) - int(event.get("min_shift", 1)) + 1)
        affected = []
        for index, target in enumerate(targets):
            name_seed = seed + sum(ord(ch) for ch in target) + index
            delta = int(event.get("min_shift", 1)) + (name_seed % span)
            shift_record = self._apply_npc_evil_shift(
                target,
                delta=delta,
                event_key=event_key,
                source="external_random",
            )
            if shift_record:
                affected.append(shift_record)

        target_region = self.dynamic_region_chain[0] if self.dynamic_region_chain else self.regions[0].name
        event_record = {
            "event_key": event_key,
            "label": event["label"],
            "headline": event["headline"],
            "region": target_region,
            "causes": list(causes or []),
            "affected_npcs": [record["npc"] for record in affected],
            "unlock_signal": event.get("unlock_signal", "intel_route"),
        }
        self.world_event_history.append(
            {
                "event_key": f"external::{event_key}",
                "label": event["label"],
                "region": target_region,
                "causes": list(causes or []),
                "effects": {
                    "external_pressure": True,
                    "affected_npcs": [record["npc"] for record in affected],
                    "unlock_signal": event.get("unlock_signal", "intel_route"),
                },
            }
        )
        self._log_tapestry(
            event_type="external_event",
            label=event["label"],
            causes=causes,
            effects={
                "event_key": event_key,
                "region": target_region,
                "affected_npcs": [record["npc"] for record in affected],
            },
        )
        self._refresh_arc_and_era()
        self._schedule_dynamic_regions(player)
        return event_record

    def discover_world_intel(
        self,
        player: PlayerProfile,
        *,
        channel: str = "newspaper",
        stealth_probe: bool = False,
    ) -> Dict[str, Any]:
        normalized_channel = channel.strip().lower()
        if normalized_channel not in INTEL_CHANNELS:
            raise ValueError('Intel channel must be "newspaper" or "overheard".')
        external_events = [
            entry
            for entry in reversed(self.world_event_history)
            if str(entry.get("event_key", "")).startswith("external::")
        ]
        if not external_events:
            intel = {
                "channel": normalized_channel,
                "headline": "No fresh intelligence has surfaced yet.",
                "region": None,
                "unlock_node": None,
                "stealth_probe": stealth_probe,
            }
            self.intel_discovery_log.append(intel)
            return intel
        latest = external_events[0]
        region = str(latest.get("region", self.regions[0].name))
        unlock_signal = str(latest.get("effects", {}).get("unlock_signal", "intel_route"))
        unlock_node = f"{region.lower().replace(' ', '_')}_{unlock_signal}"
        if stealth_probe and unlock_node not in player.unlocked_zones:
            player.unlocked_zones.append(unlock_node)
        intel = {
            "channel": normalized_channel,
            "headline": latest.get("label"),
            "region": region,
            "unlock_node": unlock_node if stealth_probe else None,
            "stealth_probe": stealth_probe,
            "event_key": latest.get("event_key"),
        }
        self.intel_discovery_log.append(intel)
        return intel

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
        environment_state = self.advance_environment_cycle()
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
            "environment": environment_state,
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
        self.advance_environment_cycle()
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
        player.unlock_fast_travel(region.village_hub)
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
                "enemy_move_claims": dict(player.enemy_move_claims),
                "enemy_exclusive_moves": sorted(set(player.enemy_move_claims.values())),
            }
        )
        for entry in archived_tapestry:
            meta_entry = dict(entry)
            meta_entry["run_id"] = self.run_counter
            self.vault_meta_tapestry.append(meta_entry)
        self.active_run_tapestry = []

    def store_memory(self, subject: str, memory: str) -> int:
        normalized_subject = subject.strip()
        normalized_memory = memory.strip()
        if not normalized_subject:
            raise ValueError("Memory subject cannot be empty.")
        if not normalized_memory:
            raise ValueError("Memory value cannot be empty.")
        entries = self.memory_store.setdefault(normalized_subject, [])
        entries.append(normalized_memory)
        return len(entries)

    def get_memory_store(self, subject: str) -> List[str]:
        normalized_subject = subject.strip()
        if not normalized_subject:
            raise ValueError("Memory subject cannot be empty.")
        return list(self.memory_store.get(normalized_subject, []))

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

            # Build a list of named triggers that contributed to this villain's arc
            active_triggers: List[str] = []
            if villain.decision_memory.get("kill", 0) >= VILLAIN_AGGRESSIVE_TRIGGER_COUNT:
                active_triggers.append("kill_pressure")
            if villain.decision_memory.get("betray", 0) >= 1:
                active_triggers.append("betrayal_memory")
            if pacification_index >= VILLAIN_PASSIVE_TRIGGER_COUNT:
                active_triggers.append("pacification_effort")
            if villain.decision_memory.get("stealth", 0) >= 2:
                active_triggers.append("stealth_encroachment")
            if villain.decision_memory.get("evasion", 0) >= 2:
                active_triggers.append("evasion_pattern")
            if villain.stance == VillainStance.PASSIVE:
                active_triggers.append("stance_pacified")
            elif villain.stance == VillainStance.AGGRESSIVE:
                active_triggers.append("stance_enraged")

            # Relationship arc label derived from stance trajectory
            if villain.stance == VillainStance.PASSIVE and pacification_index >= 3:
                relationship_arc = "reformed"
            elif villain.stance == VillainStance.AGGRESSIVE and pressure >= 8:
                relationship_arc = "nemesis"
            elif villain.stance == VillainStance.BALANCED and raw_pressure >= 4:
                relationship_arc = "rival"
            elif raw_pressure == 0:
                relationship_arc = "dormant"
            else:
                relationship_arc = "active"

            checkpoints.append(
                {
                    "villain": villain.name,
                    "phase": phase,
                    "pressure_index": pressure,
                    "raw_pressure": raw_pressure,
                    "pacification_index": pacification_index,
                    "stance": villain.stance.value,
                    "relationship_arc": relationship_arc,
                    "active_triggers": active_triggers,
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
        # Balance pass (Issue 3): nonlethal decisions grant incremental reputation gains
        # to make stealth/charm/evasion playstyles competitively viable with lethal ones.
        if normalized == "charm":
            player.update_reputation(NONLETHAL_CHARM_REP_GAIN)
        elif normalized == "stealth":
            player.update_reputation(NONLETHAL_STEALTH_REP_GAIN)
        elif normalized == "evasion":
            player.update_reputation(NONLETHAL_EVASION_REP_GAIN)
        elif normalized == "kill":
            player.update_reputation(KILL_REP_LOSS)
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
        decision_total = sum(player.encounter_outcomes.values())
        if decision_total > 0 and decision_total % 4 == 0:
            self.trigger_external_pressure_event(
                player,
                causes=[f"decision_cadence:{decision_total}"],
            )

    def get_villain_backstory_profile(self, villain_name: str) -> Dict[str, Any]:
        """Return the full backstory, power origin, arc ties, and player hooks for a villain."""
        villain = self._find_villain(villain_name)
        villain_affinities = self._villain_affinity_loadout(villain)
        return {
            "name": villain.name,
            "backstory": villain.backstory,
            "power_origin": villain.power_origin,
            "signature_power": villain.signature_power.name,
            "primary_affinity": villain.primary_affinity.value,
            "secondary_affinities": [affinity.value for affinity in villain_affinities[1:]],
            "affinities": [affinity.value for affinity in villain_affinities],
            "signature_affinities": [affinity.value for affinity in villain.signature_power.affinities],
            "ultimate_affinities": [
                affinity.value for affinity in self._move_affinities_by_name(villain.ultimate_skin_name)
            ],
            "role": villain.role,
            "arc_ties": list(villain.arc_ties),
            "player_backstory_hooks": dict(villain.player_backstory_hooks),
            "stance": villain.stance.value,
            "relationship_arc": next(
                (
                    cp["relationship_arc"]
                    for cp in self.get_villain_evolution_checkpoints()
                    if cp["villain"] == villain_name
                ),
                "dormant",
            ),
        }

    def _move_affinities_by_name(self, move_name: str) -> Tuple[Affinity, ...]:
        if not move_name:
            return ()
        for move in self.technique_library:
            if move.name == move_name:
                return move.affinities
        for spec in BOSS_EXCLUSIVE_MOVE_SPECS.values():
            if spec["name"] == move_name:
                return tuple(spec["affinities"])
        return ()

    def _villain_affinity_loadout(self, villain: VillainProfile) -> Tuple[Affinity, ...]:
        return _ordered_unique_affinities(
            (
                villain.primary_affinity,
                *villain.signature_power.affinities,
                *self._move_affinities_by_name(villain.ultimate_skin_name),
            )
        )

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

    def _find_city_shop(self, shop_key: str) -> CityShop:
        shop = next((item for item in self.city_shops if item.key == shop_key), None)
        if not shop:
            raise ValueError(f'City shop "{shop_key}" not found.')
        return shop

    def _find_city_npc(self, npc_name: str) -> CityNPC:
        normalized = npc_name.strip().lower()
        npc = next((item for item in self.city_npcs if item.name.strip().lower() == normalized), None)
        if not npc:
            raise ValueError(f'City NPC "{npc_name}" not found.')
        return npc

    def _ensure_city_state(self, city_name: str) -> Dict[str, int]:
        state = self.city_immersion_state.setdefault(
            city_name,
            {"alert_level": 0, "intel_noise": 0, "quest_pressure": 0},
        )
        state["alert_level"] = max(0, int(state.get("alert_level", 0)))
        state["intel_noise"] = max(0, int(state.get("intel_noise", 0)))
        state["quest_pressure"] = max(0, int(state.get("quest_pressure", 0)))
        return state

    def _ensure_npc_consequence_state(self, npc_name: str) -> Dict[str, int]:
        state = self.npc_consequence_state.setdefault(
            npc_name,
            {"suspicion": 0, "trust": 0, "intel_shared": 0},
        )
        state["suspicion"] = max(0, int(state.get("suspicion", 0)))
        state["trust"] = max(0, int(state.get("trust", 0)))
        state["intel_shared"] = max(0, int(state.get("intel_shared", 0)))
        return state

    def _record_npc_consequence(
        self,
        *,
        npc: CityNPC,
        action: str,
        outcome: str,
        detail: str,
    ) -> Dict[str, Any]:
        city_state = self._ensure_city_state(npc.city_name)
        npc_state = self._ensure_npc_consequence_state(npc.name)
        record = {
            "npc": npc.name,
            "city_name": npc.city_name,
            "region_name": npc.region_name,
            "action": action,
            "outcome": outcome,
            "detail": detail,
            "city_alert_level": city_state["alert_level"],
            "city_intel_noise": city_state["intel_noise"],
            "city_quest_pressure": city_state["quest_pressure"],
            "npc_suspicion": npc_state["suspicion"],
            "npc_trust": npc_state["trust"],
            "npc_intel_shared": npc_state["intel_shared"],
        }
        self.npc_consequence_log.append(record)
        self.npc_consequence_log = self.npc_consequence_log[-200:]
        return record

    def get_quest_distribution(self) -> Dict[str, List[Dict[str, str]]]:
        distribution: Dict[str, List[Dict[str, str]]] = {}
        for quest in self.quests:
            region_name = quest.region_name or "Unassigned"
            city_hub = ""
            if region_name != "Unassigned":
                city_hub = quest.city_hub or self._find_region(region_name).village_hub
            distribution.setdefault(region_name, []).append(
                {
                    "quest_id": quest.quest_id,
                    "title": quest.title,
                    "city_hub": city_hub,
                    "quest_giver": quest.quest_giver,
                }
            )
        return distribution

    def generate_mock_world_map(self) -> Dict[str, Any]:
        markers: List[Dict[str, Any]] = []
        legend: List[Dict[str, Any]] = []
        routes: List[Dict[str, Any]] = []
        for index, region in enumerate(self.regions, start=1):
            x, y = WORLD_MAP_REGION_COORDINATES.get(region.name, (2 + index * 5, 2 + (index % 4) * 3))
            boss_arena = next((poi.name for poi in region.points_of_interest if poi.poi_type == "boss_arena"), region.boss)
            marker = {
                "marker": str(index),
                "region": region.name,
                "city_hub": region.village_hub,
                "boss": region.boss,
                "boss_location": boss_arena,
                "coordinates": {"x": x, "y": y},
                "climate": region.climate,
                "terrain_profile": list(region.terrain_profile),
                "interactive": True,
            }
            markers.append(marker)
            legend.append(dict(marker))
            if index < len(self.regions):
                routes.append(
                    {
                        "from_marker": str(index),
                        "to_marker": str(index + 1),
                        "from_region": region.name,
                        "to_region": self.regions[index].name,
                        "route_type": "recommended_story_path",
                    }
                )
        return {
            "title": "Interactive World Map: Quiet Steel Confederacy",
            "markers": markers,
            "legend": legend,
            "routes": routes,
            "recommended_route": [region.name for region in self.regions],
            "active_dynamic_route": list(self.dynamic_region_chain),
        }

    def get_technique_catalog(
        self, *, affinity: Affinity | None = None, technique_type: TechniqueType | None = None
    ) -> List[Dict[str, Any]]:
        moves = self.technique_library
        if affinity is not None:
            moves = [move for move in moves if affinity in move.affinities]
        if technique_type is not None:
            moves = [move for move in moves if move.technique_type == technique_type]
        return [
            {
                "name": move.name,
                "category": move.category.value,
                "affinities": [affinity.value for affinity in move.affinities],
                "technique_type": move.technique_type.value,
                "status_effects": [effect.value for effect in move.status_effects],
                "animation_profile": dict(move.animation_profile),
            }
            for move in moves
        ]

    def get_move_animation_preview(self, move_name: str) -> Dict[str, Any]:
        move = next((item for item in self.technique_library if item.name == move_name), None)
        if not move:
            raise ValueError(f'Move "{move_name}" not found in technique catalog.')
        action_timeline = self._build_action_timeline(move)
        return {
            "move": move.name,
            "affinities": [affinity.value for affinity in move.affinities],
            "animation_profile": dict(move.animation_profile),
            "skill_physics": self._build_skill_physics(move),
            "action_timeline": action_timeline,
        }

    def preview_affinity_combo_animation(
        self, starter_move: str, link_move: str, finisher_move: str
    ) -> Dict[str, Any]:
        staged = []
        for beat, move_name in enumerate((starter_move, link_move, finisher_move), start=1):
            move = next((item for item in self.technique_library if item.name == move_name), None)
            if not move:
                raise ValueError(f'Move "{move_name}" not found in technique catalog.')
            timeline = self._build_action_timeline(move, actor=f"combo_actor_{beat}", beat=beat)
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
                    "action_timeline": timeline,
                }
            )
        return {"combo_path": staged}

    def _build_action_timeline(
        self,
        move: Move,
        *,
        actor: str = "player",
        beat: int | None = None,
    ) -> List[Dict[str, Any]]:
        phase_duration_ms = {"startup": 320, "travel": 260, "hit": 180, "recovery": 300}
        phases = ("startup", "travel", "hit", "recovery")
        timeline: List[Dict[str, Any]] = []
        for phase in phases:
            cue = move.animation_profile.get(phase, "")
            timeline.append(
                {
                    "phase": phase,
                    "actor": actor,
                    "beat": beat,
                    "cue": cue,
                    "duration_ms": phase_duration_ms[phase],
                    "camera": "impact_push" if phase == "hit" else "tracking_follow",
                }
            )
        return timeline

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

    def _build_city_quest_layer(self, quest: Quest, branch_key: str) -> Dict[str, Any]:
        city_name = quest.city_hub or (
            self._find_region(quest.region_name).village_hub if quest.region_name else "Unassigned"
        )
        city_state = self._ensure_city_state(city_name)
        pressure_delta = int(CITY_QUEST_PRESSURE_BY_BRANCH.get(branch_key, CITY_QUEST_PRESSURE_BY_BRANCH["default"]))
        prior_pressure = city_state["quest_pressure"]
        city_state["quest_pressure"] = max(0, min(12, prior_pressure + pressure_delta))
        city_state["intel_noise"] = max(
            0,
            min(8, city_state["intel_noise"] + (1 if pressure_delta > 1 else 0) - (1 if pressure_delta < 0 else 0)),
        )
        if pressure_delta > 1:
            city_state["alert_level"] = min(8, city_state["alert_level"] + 1)
        elif pressure_delta < 0:
            city_state["alert_level"] = max(0, city_state["alert_level"] - 1)
        region_pressure = 0
        if quest.region_name:
            region_pressure = int(self.region_state.get(quest.region_name, {}).get("pressure", 0))
        total_pressure = city_state["quest_pressure"] + region_pressure
        if total_pressure >= 8:
            city_mood = "lockdown"
        elif total_pressure >= 4:
            city_mood = "uneasy watch"
        else:
            city_mood = "measured calm"
        narrative = (
            f"{city_name} reacts with {city_mood}: {quest.quest_giver} tracks the fallout while wardens adjust "
            f"patrol routes around this quest line."
        )
        return {
            "city_name": city_name,
            "region_name": quest.region_name,
            "quest_giver": quest.quest_giver,
            "branch_pressure_delta": pressure_delta,
            "quest_pressure_before": prior_pressure,
            "quest_pressure_after": city_state["quest_pressure"],
            "alert_level": city_state["alert_level"],
            "intel_noise": city_state["intel_noise"],
            "region_pressure": region_pressure,
            "mood": city_mood,
            "narrative": narrative,
        }

    def resolve_quest_branch(self, player: PlayerProfile, quest_id: str) -> Dict[str, Any]:
        quest = next((q for q in self.quests if q.quest_id == quest_id), None)
        if not quest:
            raise ValueError(f'Quest "{quest_id}" not found.')
        state = self._ensure_quest_resolution_state(player, quest)

        if not quest.branch_outcomes:
            city_layer = self._build_city_quest_layer(quest, "default")
            return {
                "quest_id": quest.quest_id,
                "title": quest.title,
                "branch_key": "default",
                "outcome": f"{quest.objective} {city_layer['narrative']}",
                "premise": quest.premise or quest.objective,
                "objective": quest.objective,
                "choices": list(quest.choices),
                "rewards": dict(quest.rewards),
                "follow_up_hook": quest.follow_up_hook,
                "villain_stance_impacts": dict(quest.villain_stance_impacts),
                "reputation_impacts": dict(quest.reputation_impacts),
                "trophy_hooks": list(quest.trophy_hooks),
                "quest_resolution": dict(state),
                "city_layer": city_layer,
                "reformed_villain_hook": None,
            }

        branch_key = self._resolve_branch_key(player, quest, quest.branch_outcomes)

        outcome = quest.branch_outcomes.get(branch_key) or quest.branch_outcomes.get(
            "default", quest.objective
        )
        reformed_hook = self._get_reformed_villain_hook(quest.quest_id)
        if reformed_hook:
            outcome = f"{outcome} {reformed_hook}"
        city_layer = self._build_city_quest_layer(quest, branch_key)
        outcome = f"{outcome} {city_layer['narrative']}"
        state = player.set_quest_resolution_context(
            quest.quest_id,
            stealth_required=quest.stealth_required,
            resolved_branch_key=branch_key,
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
            "quest_resolution": dict(state),
            "city_layer": city_layer,
            "reformed_villain_hook": reformed_hook,
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
        branch_result = self.resolve_quest_branch(player, quest_id)
        player.set_quest_resolution_context(
            quest_id,
            stealth_required=quest.stealth_required,
            resolved_branch_key=branch_result["branch_key"],
            completed=True,
        )
        levels_gained = player.stats.gain_xp(quest.reward_xp)
        player.gain_attribute_points(levels_gained)
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
            "resolved_branch_key": branch_result["branch_key"],
            "stealth_gate_open": branch_result["quest_resolution"]["stealth_gate_open"],
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

    def _get_reformed_villain_hook(self, quest_id: str) -> str | None:
        hook = REFORMED_VILLAIN_DIALOGUE_HOOKS.get(quest_id)
        if not hook:
            return None
        checkpoints = {
            checkpoint["villain"]: checkpoint
            for checkpoint in self.get_villain_evolution_checkpoints()
        }
        villain_checkpoint = checkpoints.get(hook["villain"])
        if villain_checkpoint and villain_checkpoint.get("relationship_arc") == "reformed":
            return hook["line"]
        return None

    def _resolve_branch_key(
        self, player: PlayerProfile, quest: Quest, branch_outcomes: Dict[str, str]
    ) -> str:
        """Resolve branch precedence: backstory, path states, narrative tags, then default.

        Narrative tags are checked in alphabetical order to keep matching deterministic.
        """
        state = self._ensure_quest_resolution_state(player, quest)
        if player.selected_backstory and player.selected_backstory.key in branch_outcomes:
            return player.selected_backstory.key
        tactical_approach = OUTCOME_BRANCH_PATH_KEYS.get(str(state.get("approach")))
        if tactical_approach in branch_outcomes:
            return tactical_approach
        if (
            player.is_nonlethal_path_active()
            and "nonlethal_path" in branch_outcomes
            and (
                not quest.stealth_required
                or bool(state.get("stealth_satisfied"))
            )
        ):
            return "nonlethal_path"
        dominant_outcome = player.dominant_encounter_outcome()
        if dominant_outcome:
            tactical_path_key = OUTCOME_BRANCH_PATH_KEYS.get(dominant_outcome)
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
        environment_state = self.advance_environment_cycle()
        region = self._find_region(region_name)
        encounter_pool = region.encounter_table if region.encounter_table else region.enemies
        if not encounter_pool:
            raise ValueError(f'Region "{region_name}" has no encounters configured.')
        level_gap = max(region.minimum_level - player.stats.level, 0)
        unauthorized_region = level_gap > 0
        if unauthorized_region:
            hunt_chance = min(0.2 + (0.15 * level_gap), 0.95)
            if random.random() < hunt_chance:
                encounter_count = player.record_region_encounter(region_name)
                assassin_strength = max(region.minimum_level, player.stats.level + level_gap * 2)
                return {
                    "region": region_name,
                    "encounter": region.assassin_hunter_name,
                    "encounter_index": None,
                    "times_seen": encounter_count,
                    "unauthorized_region": True,
                    "recommended_level": region.minimum_level,
                    "player_level": player.stats.level,
                    "level_gap": level_gap,
                    "assassin_hunt_triggered": True,
                    "assassin_strength": assassin_strength,
                    "outcome": "killed",
                    "player_survived": False,
                    "environment": environment_state,
                }
        encounter_index = player.encounter_history.get(region_name, 0) % len(encounter_pool)
        encounter = encounter_pool[encounter_index]
        encounter_count = player.record_region_encounter(region_name)
        reward_xp = _region_encounter_xp_reward(encounter)
        levels_gained = player.stats.gain_xp(reward_xp)
        player.gain_attribute_points(levels_gained)
        enemy_exclusive_move = enemy_exclusive_move_for(encounter)
        enemy_exclusive_move_name = enemy_exclusive_move.name if enemy_exclusive_move else None
        enemy_exclusive_move_unlocked = None
        if enemy_exclusive_move and player.claim_enemy_exclusive_move(encounter, enemy_exclusive_move):
            enemy_exclusive_move_unlocked = enemy_exclusive_move.name
        return {
            "region": region_name,
            "encounter": encounter,
            "encounter_index": encounter_index,
            "times_seen": encounter_count,
            "reward_xp": reward_xp,
            "levels_gained": levels_gained,
            "level": player.stats.level,
            "enemy_exclusive_move": enemy_exclusive_move_name,
            "enemy_exclusive_move_unlocked": enemy_exclusive_move_unlocked,
            "unauthorized_region": unauthorized_region,
            "recommended_level": region.minimum_level,
            "player_level": player.stats.level,
            "level_gap": level_gap,
            "assassin_hunt_triggered": False,
            "player_survived": True,
            "environment": environment_state,
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
            commerce_discount = min(max(player.action_attributes.get("commerce", 1) - 1, 0), 4)
            price = max(1, price - commerce_discount)
            if item.get("requires_nonlethal") and not player.is_nonlethal_path_active():
                continue
            if player.nonlethal_action_count() < int(item.get("min_nonlethal_actions", 0)):
                continue
            required_quests = item.get("required_quests", ())
            if any(player.quest_log.get(quest_id) != QuestStatus.COMPLETED for quest_id in required_quests):
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
                    "shop_tags": list(item.get("shop_tags", ())),
                }
            )
        return visible_items

    def get_city_shops(
        self,
        player: PlayerProfile,
        *,
        region_name: str | None = None,
        city_name: str | None = None,
    ) -> List[Dict[str, Any]]:
        visible_items = {item["key"]: item for item in self.get_shop_inventory(player)}
        shops: List[Dict[str, Any]] = []
        for shop in self.city_shops:
            if region_name and shop.region_name != region_name:
                continue
            if city_name and shop.city_name != city_name:
                continue
            inventory = [
                dict(visible_items[item_key])
                for item_key in shop.inventory_item_keys
                if item_key in visible_items
            ]
            shops.append(
                {
                    "key": shop.key,
                    "name": shop.name,
                    "region_name": shop.region_name,
                    "city_name": shop.city_name,
                    "specialty": shop.specialty,
                    "description": shop.description,
                    "inventory": inventory,
                }
            )
        return shops

    def purchase_shop_item(
        self,
        player: PlayerProfile,
        item_key: str,
        *,
        city_shop_key: str | None = None,
    ) -> Dict[str, Any]:
        inventory = {item["key"]: item for item in self.get_shop_inventory(player)}
        if item_key not in inventory:
            raise ValueError(f'Item "{item_key}" is not available for this player.')
        if city_shop_key is not None:
            shop = self._find_city_shop(city_shop_key)
            if item_key not in shop.inventory_item_keys:
                raise ValueError(f'Item "{item_key}" is not sold at shop "{city_shop_key}".')
        item = inventory[item_key]
        player.spend_credits(item["price"])
        if item["reward_type"] == "tool":
            player.unlock_tool(item["reward_name"])
        else:
            player.grant_boss_reward(item["reward_type"], item["reward_name"])
            if item["reward_type"] == "move":
                shop_move = next((move for move in self.technique_library if move.name == item["reward_name"]), None)
                if shop_move and shop_move.name not in player.unlocked_move_names:
                    player.add_move(shop_move, allow_cross_affinity=True)
        return {
            "item_key": item_key,
            "price": item["price"],
            "remaining_credits": player.credits,
        }

    def get_city_npcs(
        self,
        *,
        region_name: str | None = None,
        city_name: str | None = None,
    ) -> List[Dict[str, Any]]:
        return [
            {
                "name": npc.name,
                "region_name": npc.region_name,
                "city_name": npc.city_name,
                "role": npc.role,
                "disposition": npc.disposition,
                "dialogue": npc.dialogue,
                "services": list(npc.services),
                "pickpocket_difficulty": npc.pickpocket_difficulty,
            }
            for npc in self.city_npcs
            if (region_name is None or npc.region_name == region_name)
            and (city_name is None or npc.city_name == city_name)
        ]

    def interact_city_npc(
        self,
        player: PlayerProfile,
        npc_name: str,
        *,
        interaction: str = "talk",
    ) -> Dict[str, Any]:
        npc = self._find_city_npc(npc_name)
        normalized = interaction.strip().lower()
        result = {
            "npc": npc.name,
            "city_name": npc.city_name,
            "region_name": npc.region_name,
            "role": npc.role,
            "interaction": normalized,
            "dialogue": npc.dialogue,
            "services": list(npc.services),
        }
        city_state = self._ensure_city_state(npc.city_name)
        npc_state = self._ensure_npc_consequence_state(npc.name)
        if normalized == "trade":
            result["shops"] = self.get_city_shops(player, region_name=npc.region_name, city_name=npc.city_name)
        elif normalized == "gather_intel":
            suspicion_gap = max(0, npc_state["suspicion"] - npc_state["trust"])
            intel_difficulty = max(3, 6 + city_state["intel_noise"] + suspicion_gap)
            intel_bonus = max(0, npc_state["trust"] - npc_state["suspicion"])
            intel_check = player.resolve_action_check(
                "scouting",
                difficulty=intel_difficulty,
                situational_bonus=intel_bonus,
            )
            result["intel_check"] = intel_check
            if intel_check["success"]:
                npc_state["trust"] = min(6, npc_state["trust"] + 1)
                npc_state["intel_shared"] = min(99, npc_state["intel_shared"] + 1)
                city_state["quest_pressure"] = max(0, city_state["quest_pressure"] - 1)
                result["intel"] = (
                    f"{npc.name} shares verified route windows, checkpoint routines, and faction mood shifts around "
                    f"{npc.city_name}."
                )
                consequence = self._record_npc_consequence(
                    npc=npc,
                    action="gather_intel",
                    outcome="success",
                    detail="Detailed intel shared after trust gains.",
                )
            else:
                npc_state["suspicion"] = min(8, npc_state["suspicion"] + 1)
                city_state["intel_noise"] = min(8, city_state["intel_noise"] + 1)
                result["intel"] = (
                    f"{npc.name} shares only rumor fragments while patrol chatter in {npc.city_name} grows louder."
                )
                consequence = self._record_npc_consequence(
                    npc=npc,
                    action="gather_intel",
                    outcome="failure",
                    detail="Intel access narrowed by rising suspicion.",
                )
            result["intel_difficulty"] = intel_difficulty
            result["npc_consequence"] = consequence
        result["city_state"] = dict(city_state)
        result["npc_state"] = dict(npc_state)
        return result

    def set_mobile_fast_travel(self, player: PlayerProfile, node_name: str) -> Dict[str, Any]:
        node = node_name.strip()
        if not node:
            raise ValueError("Mobile fast travel node cannot be empty.")
        if MOBILE_FAST_TRAVEL_TOOL_NAME not in player.owned_tools:
            raise ValueError(f'Player must own "{MOBILE_FAST_TRAVEL_TOOL_NAME}" to set a mobile fast travel point.')
        known_nodes = {
            poi.name
            for region in self.regions
            for poi in region.points_of_interest
        } | {region.name for region in self.regions} | {region.village_hub for region in self.regions}
        if node not in known_nodes:
            raise ValueError(f'Fast travel node "{node}" is not recognized.')
        travel_check = player.resolve_action_check("mobility", difficulty=4)
        player.mobile_fast_travel_node = node
        return {
            "node": node,
            "tool": MOBILE_FAST_TRAVEL_TOOL_NAME,
            "mobility_check": travel_check,
        }

    def get_available_fast_travel_points(self, player: PlayerProfile) -> List[str]:
        points = list(player.unlocked_fast_travel_nodes)
        if player.mobile_fast_travel_node and player.mobile_fast_travel_node not in points:
            points.append(player.mobile_fast_travel_node)
        return points

    def fast_travel(self, player: PlayerProfile, destination: str) -> Dict[str, Any]:
        target = destination.strip()
        if not target:
            raise ValueError("Fast travel destination cannot be empty.")
        if target not in self.get_available_fast_travel_points(player):
            raise ValueError(f'Fast travel destination "{destination}" is not unlocked.')
        environment_state = self.advance_environment_cycle()
        return {
            "destination": target,
            "available_points": self.get_available_fast_travel_points(player),
            "environment": environment_state,
            "used_mobile_anchor": target == player.mobile_fast_travel_node,
        }

    def attempt_pickpocket(self, player: PlayerProfile, npc_name: str) -> Dict[str, Any]:
        npc = self._find_city_npc(npc_name)
        city_state = self._ensure_city_state(npc.city_name)
        npc_state = self._ensure_npc_consequence_state(npc.name)
        suspicion_gap = max(0, npc_state["suspicion"] - npc_state["trust"])
        effective_difficulty = max(
            3,
            npc.pickpocket_difficulty + city_state["alert_level"] + suspicion_gap,
        )
        check = player.resolve_action_check("pickpocket", difficulty=effective_difficulty)
        if check["success"]:
            reward_base = npc.pickpocket_difficulty * 4 + player.action_attributes.get("pickpocket", 1)
            reward = max(6, reward_base - (city_state["alert_level"] * 2))
            player.earn_credits(reward)
            player.pickpocket_history["success"] = int(player.pickpocket_history.get("success", 0)) + 1
            player.update_reputation(PICKPOCKET_REPUTATION_PENALTY_ON_SUCCESS)
            npc_state["suspicion"] = min(8, npc_state["suspicion"] + 1)
            npc_state["trust"] = max(0, npc_state["trust"] - 1)
            city_state["alert_level"] = min(8, city_state["alert_level"] + 1)
            city_state["intel_noise"] = min(8, city_state["intel_noise"] + 1)
            city_state["quest_pressure"] = min(12, city_state["quest_pressure"] + 1)
            self.store_memory(
                player.name,
                f"Picked {npc.name}'s pocket in {npc.city_name} and escaped with {reward} credits.",
            )
            consequence = self._record_npc_consequence(
                npc=npc,
                action="pickpocket",
                outcome="success",
                detail="NPC notices inventory tampering and hardens local routines.",
            )
            result = {
                "npc": npc.name,
                "city_name": npc.city_name,
                "success": True,
                "credits_stolen": reward,
                "stolen_item_hint": npc.pickpocket_rewards[0] if npc.pickpocket_rewards else "loose coin purse",
                "check": check,
                "remaining_credits": player.credits,
                "npc_consequence": consequence,
            }
        else:
            player.pickpocket_history["caught"] = int(player.pickpocket_history.get("caught", 0)) + 1
            player.update_reputation(PICKPOCKET_REPUTATION_PENALTY_ON_CAUGHT)
            npc_state["suspicion"] = min(8, npc_state["suspicion"] + 2)
            npc_state["trust"] = max(0, npc_state["trust"] - 2)
            city_state["alert_level"] = min(8, city_state["alert_level"] + 2)
            city_state["intel_noise"] = min(8, city_state["intel_noise"] + 1)
            city_state["quest_pressure"] = min(12, city_state["quest_pressure"] + 2)
            self._update_antagonist_scores(
                signal="pickpocket_caught",
                intensity=1,
                focal_points=self.allies[:1],
                causes=[npc.name, npc.city_name],
            )
            consequence = self._record_npc_consequence(
                npc=npc,
                action="pickpocket",
                outcome="caught",
                detail="Local patrols escalate sweeps and informants become hostile.",
            )
            result = {
                "npc": npc.name,
                "city_name": npc.city_name,
                "success": False,
                "credits_stolen": 0,
                "check": check,
                "remaining_credits": player.credits,
                "npc_consequence": consequence,
            }
        self._log_tapestry(
            event_type="city_action",
            label=f"Pickpocket attempt against {npc.name} in {npc.city_name}.",
            causes=[f"success:{result['success']}"],
            effects={"credits_delta": result["credits_stolen"], "region": npc.region_name},
        )
        result["effective_difficulty"] = effective_difficulty
        result["city_state"] = dict(city_state)
        result["npc_state"] = dict(npc_state)
        return result

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
        red_bar_villains = [villain for villain in self.villains if villain.health_bar_color.lower() == "red"]
        if red_bar_villains and all(villain.defeated for villain in red_bar_villains):
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

        # --- Stance evolution mastery trophies (Issue 2) ---

        # Pacifier: drive at least N villains to PASSIVE via charm/mercy/diplomacy
        passive_count = sum(
            1 for v in self.villains
            if v.stance == VillainStance.PASSIVE
            and sum(v.decision_memory.get(k, 0) for k in ("charm", "mercy", "diplomacy")) >= VILLAIN_PASSIVE_TRIGGER_COUNT
        )
        if passive_count >= VILLAIN_PASSIVE_TRIGGER_COUNT:
            _award(TROPHY_PACIFIER)

        # Terror: drive at least N villains to AGGRESSIVE via kill/betray
        aggressive_count = sum(
            1 for v in self.villains
            if v.stance == VillainStance.AGGRESSIVE
            and (v.decision_memory.get("kill", 0) + v.decision_memory.get("betray", 0)) >= VILLAIN_AGGRESSIVE_TRIGGER_COUNT
        )
        if aggressive_count >= VILLAIN_AGGRESSIVE_TRIGGER_COUNT:
            _award(TROPHY_TERROR)

        # Stance Breaker: shift at least N different villains through 2+ stances during the run
        multi_stance_count = sum(
            1 for v in self.villains
            if sum(1 for k in ("kill", "charm", "stealth") if v.decision_memory.get(k, 0) > 0) >= 2
        )
        if multi_stance_count >= STANCE_BREAKER_VILLAIN_COUNT:
            _award(TROPHY_STANCE_BREAKER)

        # Shadow Whisperer: nonlethal run with stealth mastery
        if player.is_nonlethal_path_active() and player.encounter_outcomes["stealth"] >= NONLETHAL_STEALTH_MASTER_THRESHOLD:
            _award(TROPHY_SHADOW_WHISPERER)

        # Silver Mask: nonlethal run with charm mastery
        if player.is_nonlethal_path_active() and player.encounter_outcomes["charm"] >= NONLETHAL_CHARM_MASTER_THRESHOLD:
            _award(TROPHY_SILVER_MASK)

        # Wind Dancer: nonlethal run with evasion mastery
        if player.is_nonlethal_path_active() and player.encounter_outcomes["evasion"] >= NONLETHAL_EVASION_MASTER_THRESHOLD:
            _award(TROPHY_WIND_DANCER)

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

    def _build_playstyle_summary(self, player: PlayerProfile) -> Dict[str, Any]:
        """Return a human-readable playstyle breakdown for the summary (Issue 4)."""
        outcomes = player.encounter_outcomes
        total = sum(outcomes.values())
        nonlethal_total = player.nonlethal_action_count()
        if total == 0:
            dominant = "none"
            style_label = "No encounters recorded"
        else:
            dominant = max(outcomes, key=lambda k: (outcomes[k], k))
            if player.is_nonlethal_path_active():
                if outcomes.get("stealth", 0) >= max(outcomes.get("charm", 0), outcomes.get("evasion", 0)):
                    style_label = "Shadow Operative — stealth-led nonlethal approach"
                elif outcomes.get("charm", 0) >= max(outcomes.get("stealth", 0), outcomes.get("evasion", 0)):
                    style_label = "Silver Diplomat — charm-led nonlethal approach"
                else:
                    style_label = "Wind Walker — evasion-led nonlethal approach"
            elif outcomes.get("kill", 0) >= nonlethal_total:
                style_label = "Lethal Shinobi — direct and decisive"
            else:
                style_label = "Mixed Tactician — blend of force and finesse"
        # Playstyle shift detection: check if the dominant style changed mid-run
        tapestry_kills = sum(
            1 for e in self.active_run_tapestry
            if "kill" in str(e.get("causes", []))
        )
        tapestry_nonlethal = sum(
            1 for e in self.active_run_tapestry
            if any(k in str(e.get("causes", [])) for k in ("charm", "stealth", "evasion"))
        )
        if tapestry_kills > 0 and tapestry_nonlethal > 0:
            shift_detected = tapestry_nonlethal > tapestry_kills
            shift_note = "Shifted toward nonlethal midway" if shift_detected else "Consistent playstyle throughout"
        else:
            shift_note = "Single playstyle throughout"
        return {
            "dominant_action": dominant,
            "style_label": style_label,
            "nonlethal_total": nonlethal_total,
            "lethal_total": outcomes.get("kill", 0),
            "playstyle_shift_note": shift_note,
        }

    def _build_trophy_near_miss(self, player: PlayerProfile) -> List[Dict[str, Any]]:
        """Return a list of trophies that are close to unlocking (Issue 4)."""
        near_miss: List[Dict[str, Any]] = []
        outcomes = player.encounter_outcomes

        def _check(trophy_key: str, current: int, target: int, label: str) -> None:
            if trophy_key not in player.trophies:
                remaining = target - current
                if 0 < remaining <= 3:
                    near_miss.append({
                        "trophy_key": trophy_key,
                        "name": self.trophy_catalog[trophy_key].name if trophy_key in self.trophy_catalog else trophy_key,
                        "remaining": remaining,
                        "hint": label,
                    })

        _check(TROPHY_GHOST_STEP, outcomes["stealth"], STEALTH_TROPHY_BASE_THRESHOLD, "stealth encounters")
        _check(TROPHY_VEIL_MASTER, outcomes["stealth"], STEALTH_TROPHY_ADVANCED_THRESHOLD, "stealth encounters")
        _check(TROPHY_PHANTOM_VEIL, outcomes["stealth"], STEALTH_TROPHY_MASTER_THRESHOLD, "stealth encounters")
        _check(TROPHY_SILVER_TONGUE, outcomes["charm"], CHARM_TROPHY_BASE_THRESHOLD, "charm encounters")
        _check(TROPHY_DIPLOMAT_SUPREME, outcomes["charm"], CHARM_TROPHY_ADVANCED_THRESHOLD, "charm encounters")
        _check(TROPHY_HARMONY_VOICE, outcomes["charm"], CHARM_TROPHY_MASTER_THRESHOLD, "charm encounters")
        _check(TROPHY_WINDWALK_SURVIVOR, outcomes["evasion"], EVASION_TROPHY_THRESHOLD, "evasion encounters")
        _check(TROPHY_UNTOUCHABLE_GHOST, outcomes["evasion"], EVASION_TROPHY_MASTER_THRESHOLD, "evasion encounters")
        _check(TROPHY_BATTLE_HARDENED, outcomes["kill"], KILL_TROPHY_BASE_THRESHOLD, "lethal encounters")
        _check(TROPHY_WAR_VETERAN, outcomes["kill"], KILL_TROPHY_ADVANCED_THRESHOLD, "lethal encounters")
        _check(TROPHY_CRIMSON_REAPER, outcomes["kill"], KILL_TROPHY_ELITE_THRESHOLD, "lethal encounters")
        _check(TROPHY_APEX_PREDATOR, outcomes["kill"], KILL_TROPHY_MASTER_THRESHOLD, "lethal encounters")
        _check(TROPHY_RISING_NINJA, player.stats.level, LEVEL_TROPHY_BASE_THRESHOLD, "levels to gain")
        _check(TROPHY_SEASONED_NINJA, player.stats.level, LEVEL_TROPHY_ADVANCED_THRESHOLD, "levels to gain")
        if player.is_nonlethal_path_active():
            _check(TROPHY_SHADOW_WHISPERER, outcomes["stealth"], NONLETHAL_STEALTH_MASTER_THRESHOLD, "nonlethal stealth encounters")
            _check(TROPHY_SILVER_MASK, outcomes["charm"], NONLETHAL_CHARM_MASTER_THRESHOLD, "nonlethal charm encounters")
            _check(TROPHY_WIND_DANCER, outcomes["evasion"], NONLETHAL_EVASION_MASTER_THRESHOLD, "nonlethal evasion encounters")
        return near_miss

    def build_world_map(self) -> Dict[str, Any]:
        return {
            "region_count": len(self.regions),
            "environment": self.get_environment_state(),
            "quest_distribution": self.get_quest_distribution(),
            "regions": [
                {
                    "name": region.name,
                    "village_hub": region.village_hub,
                    "arc_key": region.arc_key,
                    "climate": region.climate,
                    "terrain_profile": list(region.terrain_profile),
                    "strategic_value": region.strategic_value,
                    "minimum_level": region.minimum_level,
                    "assassin_hunter_name": region.assassin_hunter_name,
                    "travel_nodes": list(region.travel_nodes),
                    "city_shops": [
                        {
                            "key": shop.key,
                            "name": shop.name,
                            "specialty": shop.specialty,
                        }
                        for shop in self.city_shops
                        if shop.region_name == region.name
                    ],
                    "city_npcs": [
                        {
                            "name": npc.name,
                            "role": npc.role,
                            "services": list(npc.services),
                        }
                        for npc in self.city_npcs
                        if npc.region_name == region.name
                    ],
                    "quests": [
                        {
                            "quest_id": quest.quest_id,
                            "title": quest.title,
                            "quest_giver": quest.quest_giver,
                        }
                        for quest in self.quests
                        if quest.region_name == region.name
                    ],
                    "points_of_interest": [
                        {
                            "name": poi.name,
                            "type": poi.poi_type,
                            "summary": poi.summary,
                            "control_faction": poi.control_faction,
                            "threats": list(poi.threats),
                            "services": list(poi.services),
                            "connected_nodes": list(poi.connected_nodes),
                        }
                        for poi in region.points_of_interest
                    ],
                }
                for region in self.regions
            ],
        }

    def generate_lore_dump(self) -> Dict[str, Any]:
        region_by_boss = {region.boss: region for region in self.regions}
        points_of_interest = [
            {
                "region": region.name,
                "name": poi.name,
                "type": poi.poi_type,
                "control_faction": poi.control_faction,
                "summary": poi.summary,
                "threats": list(poi.threats),
                "services": list(poi.services),
            }
            for region in self.regions
            for poi in region.points_of_interest
        ]
        summon_catalog = sorted(
            {
                (
                    move.name,
                    move.affinities[0].value if move.affinities else "unknown",
                    ", ".join(effect.value for effect in move.status_effects) or "none",
                )
                for move in self.technique_library
                if move.category == MoveCategory.SUMMON
            }
        )
        villain_records = []
        for villain in self.villains:
            region = region_by_boss.get(villain.name)
            hook_data = VILLAIN_HOOK_REGISTRY.get(villain.name, {})
            villain_records.append(
                {
                    "name": villain.name,
                    "role": villain.role,
                    "primary_affinity": villain.primary_affinity.value,
                    "backstory": villain.backstory,
                    "arc_tie": hook_data.get("arc_tie", region.arc_key if region else "free_agent"),
                    "hook_quests": list(hook_data.get("hook_quests", ())),
                    "region_anchor": region.name if region else None,
                    "signature_power": villain.signature_power.name,
                    "summon_skin": villain.skinned_move_names.get("summon_skin"),
                }
            )

        return {
            "country": dict(COUNTRY_LORE),
            "allies": [
                {
                    "name": ally_name,
                    "title": ALLY_LORE_PROFILES.get(ally_name, {}).get("title", "Field Operative"),
                    "backstory": ALLY_LORE_PROFILES.get(ally_name, {}).get(
                        "backstory",
                        "A skilled operative supporting local stabilization efforts.",
                    ),
                    "hook": ALLY_LORE_PROFILES.get(ally_name, {}).get(
                        "hook",
                        "Supports player progression and regional continuity.",
                    ),
                }
                for ally_name in self.allies
            ],
            "villains": villain_records,
            "points_of_interest": points_of_interest,
            "city_shops": [
                {
                    "key": shop.key,
                    "name": shop.name,
                    "region_name": shop.region_name,
                    "city_name": shop.city_name,
                    "specialty": shop.specialty,
                }
                for shop in self.city_shops
            ],
            "city_npcs": [
                {
                    "name": npc.name,
                    "region_name": npc.region_name,
                    "city_name": npc.city_name,
                    "role": npc.role,
                    "services": list(npc.services),
                }
                for npc in self.city_npcs
            ],
            "quest_distribution": self.get_quest_distribution(),
            "legendary_weapons": [
                {
                    "name": weapon.name,
                    "type": weapon.weapon_type.value,
                    "play_style": weapon.play_style,
                    "status_effects": [effect.value for effect in weapon.status_effects],
                }
                for weapon in self.weapons
            ]
            + [
                {
                    "name": region.boss_rewards["weapon"],
                    "type": "boss_relic",
                    "region": region.name,
                    "boss": region.boss,
                }
                for region in self.regions
            ],
            "summons": [
                {"name": name, "affinity": affinity, "status_signature": status}
                for name, affinity, status in summon_catalog
            ],
            "arc_manifest": [
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
            "action_attributes": dict(player.action_attributes),
            "attribute_points": player.attribute_points,
            "owned_tools": list(player.owned_tools),
            "mobile_fast_travel_node": player.mobile_fast_travel_node,
            "available_fast_travel_points": self.get_available_fast_travel_points(player),
            "pickpocket_history": dict(player.pickpocket_history),
            "playstyle_summary": self._build_playstyle_summary(player),
            "cleared_regions": [region.name for region in self.regions if region.cleared],
            "quest_distribution": self.get_quest_distribution(),
            "city_shops": self.get_city_shops(player),
            "city_npcs": self.get_city_npcs(),
            "villain_stances": villain_states,
            "villain_decision_memory": villain_memories,
            "villain_relationship_arcs": {
                cp["villain"]: {
                    "arc": cp["relationship_arc"],
                    "phase": cp["phase"],
                    "active_triggers": cp["active_triggers"],
                }
                for cp in self.get_villain_evolution_checkpoints()
            },
            "villain_kits": [
                {
                    "name": villain.name,
                    "role": villain.role,
                    "primary_affinity": villain.primary_affinity.value,
                    "secondary_affinities": [
                        affinity.value for affinity in self._villain_affinity_loadout(villain)[1:]
                    ],
                    "affinities": [
                        affinity.value for affinity in self._villain_affinity_loadout(villain)
                    ],
                    "signature": villain.signature_power.name,
                    "signature_affinities": [
                        affinity.value for affinity in villain.signature_power.affinities
                    ],
                    "skinned_moves": dict(villain.skinned_move_names),
                    "ultimate_skin": villain.ultimate_skin_name,
                    "ultimate_affinities": [
                        affinity.value for affinity in self._move_affinities_by_name(villain.ultimate_skin_name)
                    ],
                }
                for villain in self.villains
            ],
            "villain_backstory_profiles": {
                villain.name: {
                    "backstory": villain.backstory,
                    "power_origin": villain.power_origin,
                    "affinities": [
                        affinity.value for affinity in self._villain_affinity_loadout(villain)
                    ],
                    "secondary_affinities": [
                        affinity.value for affinity in self._villain_affinity_loadout(villain)[1:]
                    ],
                    "arc_ties": list(villain.arc_ties),
                    "player_backstory_hooks": dict(villain.player_backstory_hooks),
                }
                for villain in self.villains
            },
            "red_bar_power_claims": dict(player.red_bar_power_claims),
            "enemy_move_claims": dict(player.enemy_move_claims),
            "enemy_exclusive_moves_unlocked": sorted(set(player.enemy_move_claims.values())),
            "enemy_exclusive_move_progress": {
                "unlocked": len(player.enemy_move_claims),
                "total": len(ENEMY_EXCLUSIVE_MOVE_SPECS),
            },
            "red_bar_progress": red_bar_progress,
            "quest_log": {quest_id: status.value for quest_id, status in player.quest_log.items()},
            "quest_resolution_state": {
                quest_id: dict(state) for quest_id, state in player.quest_resolution_state.items()
            },
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
            "trophy_near_miss": self._build_trophy_near_miss(player),
            "villain_evolution": self.get_villain_evolution_checkpoints(),
            "npc_evil_profiles": {name: dict(profile) for name, profile in self.npc_evil_profiles.items()},
            "external_pressure_history": [dict(entry) for entry in self.external_pressure_history[-20:]],
            "intel_discovery_log": [dict(entry) for entry in self.intel_discovery_log[-20:]],
            "world_map": self.build_world_map(),
            "arc_state": {
                "current_arc_key": self.current_arc_key,
                "scheduled_regions": list(self.dynamic_region_chain),
                "era": dict(self._current_era()),
                "age": self.current_age,
                "transition_history": [dict(entry) for entry in self.arc_transition_history],
            },
            "living_tapestry": {
                "active_run_entries": [dict(entry) for entry in self.active_run_tapestry],
                "vault_meta_entries": len(self.vault_meta_tapestry),
                "delta_vs_prior_runs": self.get_living_tapestry_delta()["event_differences"],
            },
            "world_events": [dict(entry) for entry in self.world_event_history],
            "environment": self.get_environment_state(),
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

    # ------------------------------------------------------------------
    # Feature 2 — Ally active abilities
    # ------------------------------------------------------------------

    def invoke_ally_ability(
        self, player: PlayerProfile, ally_name: str
    ) -> Dict[str, Any]:
        """Invoke the named ally's combat ability if the ally has sufficient loyalty.

        Requires ally loyalty >= 1.  Returns a result dict describing what happened.
        """
        if ally_name not in self.allies:
            raise ValueError(f'Ally "{ally_name}" is not in the active roster.')
        loyalty = player.ally_loyalty.get(ally_name, 0)
        if loyalty < 1:
            raise ValueError(f'Ally "{ally_name}" requires at least 1 loyalty to invoke.')
        ability = ALLY_COMBAT_ABILITIES.get(ally_name)
        if not ability:
            raise ValueError(f'No combat ability defined for ally "{ally_name}".')
        result: Dict[str, Any] = {
            "ally": ally_name,
            "ability": ability["ability_name"],
            "category": ability["category"],
            "description": ability["description"],
            "loyalty_used": loyalty,
        }
        # Apply ability effects to player state
        if "stat_bonus" in ability:
            for stat, bonus in ability["stat_bonus"].items():
                current = getattr(player.stats, stat, 0)
                setattr(player.stats, stat, current + bonus)
            result["stat_bonus"] = dict(ability["stat_bonus"])
        if "status_effect" in ability:
            effect = StatusEffectType(ability["status_effect"])
            player.apply_status_effects([effect], duration=int(ability.get("duration", 1)))
            result["applied_status"] = ability["status_effect"]
        if "status_effects" in ability:
            effects = [StatusEffectType(e) for e in ability["status_effects"]]
            player.apply_status_effects(effects, duration=int(ability.get("duration", 1)))
            result["applied_statuses"] = list(ability["status_effects"])
        if "chakra_restore" in ability:
            player.restore_chakra(int(ability["chakra_restore"]))
            result["chakra_restored"] = ability["chakra_restore"]
        if ability.get("grants_free_escape"):
            result["free_escape_granted"] = True
        if "ally_loyalty_bonus" in ability:
            bonus = int(ability["ally_loyalty_bonus"])
            for name in self.allies:
                player.adjust_ally_loyalty(name, bonus)
            result["ally_loyalty_bonus"] = bonus
        self._log_tapestry(
            event_type="ally_ability",
            label=f"{ally_name} activated {ability['ability_name']}.",
            causes=[ally_name],
            effects={"ability": ability["ability_name"], "category": ability["category"]},
        )
        return result

    # ------------------------------------------------------------------
    # Feature 4 — Patrol / stealth aggro state
    # ------------------------------------------------------------------

    def resolve_stealth_approach(
        self,
        player: PlayerProfile,
        region_name: str,
        *,
        patrol_state: str = PATROL_STATE_UNDETECTED,
        consecutive_failures: int = 0,
    ) -> Dict[str, Any]:
        """Resolve a stealth approach against a region's patrol network.

        Uses the player's stealth action attribute.  Returns the new patrol state
        and whether the stealth attempt succeeded.
        """
        region = self._find_region(region_name)
        environment = self.get_environment_state()
        # Fog and night give a stealth situational bonus.
        situational_bonus = 0
        if environment["weather"] == "fog":
            situational_bonus += 2
        if environment["time_of_day"] == "night":
            situational_bonus += 1
        difficulty_by_state = {
            PATROL_STATE_UNDETECTED: 5,
            PATROL_STATE_ALERTED: 8,
            PATROL_STATE_COMBAT_LOCKED: 11,
        }
        difficulty = difficulty_by_state.get(patrol_state, 5)
        check = player.resolve_action_check(
            "stealth", difficulty=difficulty, situational_bonus=situational_bonus
        )
        success = check["success"]
        new_failures = 0 if success else consecutive_failures + 1

        if not success:
            if patrol_state == PATROL_STATE_UNDETECTED and new_failures >= PATROL_AGGRO_WINDOW:
                new_state = PATROL_STATE_ALERTED
            elif patrol_state == PATROL_STATE_ALERTED and new_failures >= PATROL_LOCKDOWN_WINDOW:
                new_state = PATROL_STATE_COMBAT_LOCKED
            else:
                new_state = patrol_state
        else:
            # Successful stealth can de-escalate alerted state back to undetected.
            if patrol_state == PATROL_STATE_ALERTED:
                new_state = PATROL_STATE_UNDETECTED
            else:
                new_state = patrol_state

        return {
            "region": region_name,
            "patrol_state_before": patrol_state,
            "patrol_state_after": new_state,
            "stealth_check": check,
            "success": success,
            "consecutive_failures": new_failures if not success else 0,
            "environment_bonus": situational_bonus,
            "escalated": (not success) and new_state != patrol_state,
            "de_escalated": success and new_state != patrol_state,
        }

    # ------------------------------------------------------------------
    # Feature 5 — Day/Night and Weather modifiers
    # ------------------------------------------------------------------

    def compute_environment_modifiers(self, move: Move) -> Dict[str, Any]:
        """Return situational damage/guard/stealth modifiers from current time and weather.

        Modifiers stack additively.  A damage_bonus of 0.1 means +10 % to base damage.
        """
        env = self.get_environment_state()
        time_of_day = env["time_of_day"]
        weather = env["weather"]
        damage_bonus = 0.0
        guard_bonus = 0.0
        stealth_bonus = 0
        notes: List[str] = []

        # Rain: buffs Water, nerfs Fire
        if weather == "rain":
            if Affinity.WATER in move.affinities:
                damage_bonus += 0.10
                notes.append("rain_water_boost")
            if Affinity.FIRE in move.affinities:
                damage_bonus -= 0.10
                notes.append("rain_fire_nerf")

        # Storm: bigger bonus for Wind, strong penalty for Fire
        if weather == "storm":
            if Affinity.WIND in move.affinities:
                damage_bonus += 0.15
                notes.append("storm_wind_boost")
            if Affinity.FIRE in move.affinities:
                damage_bonus -= 0.15
                notes.append("storm_fire_nerf")

        # Fog: stealth bonus for all moves; slight damage nerf for ranged/straight-line
        if weather == "fog":
            stealth_bonus += 2
            notes.append("fog_stealth_boost")
            move_lower = move.name.lower()
            if any(t in move_lower for t in STRAIGHT_LINE_TARGETING_TERMS):
                damage_bonus -= 0.05
                notes.append("fog_ranged_nerf")

        # Night: ambush moves and Blind status get a bonus; defenses weaken slightly
        if time_of_day == "night":
            if StatusEffectType.BLIND in move.status_effects:
                damage_bonus += 0.10
                notes.append("night_blind_boost")
            if move.category == MoveCategory.DEFENSE:
                guard_bonus -= 0.05
                notes.append("night_defense_nerf")

        # Breezy: Wind moves get a speed-up bonus (represented as minor damage bonus)
        if weather == "breezy" and Affinity.WIND in move.affinities:
            damage_bonus += 0.05
            notes.append("breezy_wind_boost")

        # Earth moves get a boost during clear day (solid ground, no environmental interference)
        if weather == "clear" and time_of_day == "day" and Affinity.EARTH in move.affinities:
            damage_bonus += 0.05
            notes.append("clear_day_earth_boost")

        return {
            "time_of_day": time_of_day,
            "weather": weather,
            "damage_bonus": round(damage_bonus, 3),
            "guard_bonus": round(guard_bonus, 3),
            "stealth_bonus": stealth_bonus,
            "notes": notes,
        }

    # ------------------------------------------------------------------
    # Feature 6 — Reputation decay
    # ------------------------------------------------------------------

    def tick_reputation_decay(self, player: PlayerProfile, *, ticks: int = 1) -> Dict[str, Any]:
        """Apply reputation decay toward neutral after prolonged inactivity.

        Each tick increments the inactivity counter.  When the counter reaches
        REPUTATION_DECAY_INACTIVITY_TICKS, one unit of reputation decays toward zero.
        """
        if ticks < 1:
            raise ValueError("Ticks must be at least 1.")
        decayed = 0
        for _ in range(ticks):
            player.reputation_inactivity_ticks += 1
            if player.reputation_inactivity_ticks >= REPUTATION_DECAY_INACTIVITY_TICKS:
                player.reputation_inactivity_ticks = 0
                if player.reputation > 0:
                    player.reputation -= REPUTATION_DECAY_AMOUNT
                    decayed += 1
                elif player.reputation < 0:
                    player.reputation += REPUTATION_DECAY_AMOUNT
                    decayed += 1
        return {
            "ticks_applied": ticks,
            "decayed_units": decayed,
            "reputation": player.reputation,
            "inactivity_ticks": player.reputation_inactivity_ticks,
            "reputation_tier": player.current_reputation_tier().value,
        }

    # ------------------------------------------------------------------
    # Feature 7 — Rival NPC
    # ------------------------------------------------------------------

    def initialize_rival(self, player: PlayerProfile) -> RivalProfile:
        """Spawn or return the world's rival shinobi, aligned opposite the player."""
        if self.rival_profile:
            return self.rival_profile
        opposing_affinity = {
            Affinity.FIRE: Affinity.WATER,
            Affinity.WATER: Affinity.FIRE,
            Affinity.EARTH: Affinity.WIND,
            Affinity.WIND: Affinity.EARTH,
        }.get(player.affinity, Affinity.WIND)
        alignment = "opposing" if player.current_reputation_tier().value != "neutral" else "mirror"
        self.rival_profile = RivalProfile(
            name="Shin — The Scarred Wanderer",
            affinity=opposing_affinity,
            alignment=alignment,
        )
        return self.rival_profile

    def update_rival_progress(self, player: PlayerProfile, *, region_just_cleared: str) -> Dict[str, Any]:
        """Advance the rival's cleared-region list one region behind the player."""
        rival = self.initialize_rival(player)
        rival.encounter_count += 1
        cleared_player = [r.name for r in self.regions if r.cleared]
        # Rival clears the previous region the player was in (one step behind).
        for region_name in cleared_player:
            if region_name != region_just_cleared and region_name not in rival.cleared_regions:
                rival.advance_region(region_name)
                # Rival claims one item from that region as competition.
                region = self._find_region(region_name)
                if region.boss_rewards:
                    loot_key = sorted(region.boss_rewards.keys())[0]
                    loot_name = region.boss_rewards[loot_key]
                    if loot_name not in rival.loot_claims:
                        rival.loot_claims.append(loot_name)
        player_alignment = player.current_reputation_tier().value
        relationship = rival.update_relationship(player.reputation, player_alignment)
        return {
            "rival_name": rival.name,
            "rival_affinity": rival.affinity.value,
            "rival_cleared_regions": list(rival.cleared_regions),
            "rival_loot_claims": list(rival.loot_claims),
            "relationship": relationship,
            "encounter_count": rival.encounter_count,
        }

    # ------------------------------------------------------------------
    # Feature 8 — Move training (repair proficiency)
    # ------------------------------------------------------------------

    def train_move(self, player: PlayerProfile, move_name: str) -> Dict[str, Any]:
        """Restore a move's proficiency to full by spending credits at a hub village.

        Cost scales with how degraded the proficiency is.
        """
        if move_name not in player.unlocked_move_names:
            raise ValueError(f'Move "{move_name}" is not unlocked.')
        current = player.move_proficiency.get(move_name, MOVE_PROFICIENCY_DEFAULT)
        deficit = MOVE_PROFICIENCY_MAX - current
        cost = MOVE_TRAIN_CREDIT_COST + deficit // 2
        player.spend_credits(cost)
        player.move_proficiency[move_name] = MOVE_PROFICIENCY_MAX
        return {
            "move": move_name,
            "proficiency_before": current,
            "proficiency_after": MOVE_PROFICIENCY_MAX,
            "credits_spent": cost,
            "remaining_credits": player.credits,
        }

    # ------------------------------------------------------------------
    # Feature 10 — Boss echo rematch
    # ------------------------------------------------------------------

    def initiate_boss_echo(self, player: PlayerProfile, region_name: str) -> Dict[str, Any]:
        """Trigger an optional echo rematch for a previously defeated region boss.

        The echo boss fights with an aggressive stance and borrows one of the
        player's most-used attack move names.
        """
        region = self._find_region(region_name)
        if not region.cleared:
            raise ValueError(f'Region "{region_name}" must be cleared before an echo rematch.')
        villain = self._find_villain(region.boss)
        if not villain.defeated:
            raise ValueError(f'Boss "{region.boss}" has not been defeated yet.')
        # Determine borrowed moves from player's top attack moves
        attack_moves = player.moves_by_set.get(MoveCategory.ATTACK, [])
        borrowed = [m.name for m in attack_moves[:BOSS_ECHO_EXTRA_MOVE_COUNT]]
        echo = self.boss_echo_registry.get(region_name)
        if echo is None:
            echo = BossEchoForm(
                region_name=region_name,
                boss_name=region.boss,
                echo_stance=BOSS_ECHO_STANCE_OVERRIDE,
                borrowed_move_names=borrowed,
            )
            self.boss_echo_registry[region_name] = echo
        else:
            echo.borrowed_move_names = borrowed
        echo.times_challenged += 1
        boosted_scale = round(villain.signature_power.power_scale + BOSS_ECHO_POWER_SCALE_BOOST, 3)
        self._log_tapestry(
            event_type="boss_echo",
            label=f"Echo of {region.boss} rises at {region_name}.",
            causes=[f"region:{region_name}"],
            effects={"echo_stance": BOSS_ECHO_STANCE_OVERRIDE.value, "boosted_scale": boosted_scale},
        )
        return {
            "region": region_name,
            "boss": region.boss,
            "echo_stance": BOSS_ECHO_STANCE_OVERRIDE.value,
            "boosted_power_scale": boosted_scale,
            "borrowed_moves": list(echo.borrowed_move_names),
            "times_challenged": echo.times_challenged,
            "original_signature": villain.signature_power.name,
        }

    def resolve_boss_echo_defeat(self, player: PlayerProfile, region_name: str) -> Dict[str, Any]:
        """Record a successful echo rematch completion and grant a small reward."""
        echo = self.boss_echo_registry.get(region_name)
        if not echo:
            raise ValueError(f'No echo rematch registered for region "{region_name}".')
        echo.times_defeated += 1
        xp_bonus = 25
        credit_bonus = 30
        player.stats.gain_xp(xp_bonus)
        player.earn_credits(credit_bonus)
        self._log_tapestry(
            event_type="boss_echo_defeat",
            label=f"Echo of {echo.boss_name} defeated at {region_name}.",
            causes=[f"region:{region_name}"],
            effects={"xp_bonus": xp_bonus, "credit_bonus": credit_bonus},
        )
        return {
            "region": region_name,
            "boss": echo.boss_name,
            "times_defeated": echo.times_defeated,
            "xp_bonus": xp_bonus,
            "credit_bonus": credit_bonus,
            "remaining_credits": player.credits,
        }

    # ------------------------------------------------------------------
    # Feature 11 — Trophy near-miss live visibility
    # ------------------------------------------------------------------

    def get_trophy_near_miss_live(self, player: PlayerProfile) -> List[Dict[str, Any]]:
        """Return live trophy near-miss data for HUD display during an active run.

        Identical to the end-of-run trophy near-miss but surfaced as a public
        method so it can be called at any point during play.
        """
        return self._build_trophy_near_miss(player)

    # ------------------------------------------------------------------
    # Feature 12 — Weapon repair (hub service)
    # ------------------------------------------------------------------

    def repair_weapon(self, player: PlayerProfile, weapon_name: str) -> Dict[str, Any]:
        """Restore a weapon's durability to full by spending credits.

        Raises ValueError if the player cannot afford the repair.
        """
        known = {weapon.name for weapon in self.weapons} | {weapon.name for weapon in player.weapons}
        if weapon_name not in known:
            raise ValueError(f'Weapon "{weapon_name}" is not recognised.')
        current = player.weapon_durability.get(weapon_name, WEAPON_DURABILITY_START)
        deficit = WEAPON_DURABILITY_MAX - current
        cost = WEAPON_REPAIR_CREDIT_COST_BASE + deficit * WEAPON_REPAIR_CREDIT_COST_PER_UNIT
        player.spend_credits(cost)
        player.weapon_durability[weapon_name] = WEAPON_DURABILITY_MAX
        return {
            "weapon": weapon_name,
            "durability_before": current,
            "durability_after": WEAPON_DURABILITY_MAX,
            "credits_spent": cost,
            "remaining_credits": player.credits,
        }

    # ------------------------------------------------------------------
    # Feature 13 — Scouting payoff
    # ------------------------------------------------------------------

    def scout_region(self, player: PlayerProfile, region_name: str) -> Dict[str, Any]:
        """Use the player's scouting attribute to reveal pre-mission intel about a region.

        Higher scouting values reveal more accurate or valuable intelligence categories.
        The revealed category rotates deterministically based on the player's scouting
        attribute and how many times the region has been scouted.
        """
        region = self._find_region(region_name)
        scout_value = player.action_attributes.get("scouting", 1)
        scout_count = player.encounter_history.get(region_name, 0)
        # Deterministic category rotation based on scout value and encounter count
        category_index = (scout_value + scout_count) % len(SCOUTING_INTEL_CATEGORIES)
        category = SCOUTING_INTEL_CATEGORIES[category_index]
        reliable = scout_value >= SCOUTING_MIN_ATTRIBUTE

        intel: Dict[str, Any] = {
            "region": region_name,
            "scouting_value": scout_value,
            "reliable": reliable,
            "category": category,
        }

        if category == "enemy_count":
            enemy_pool = region.encounter_table or region.enemies
            intel["enemy_count"] = len(enemy_pool)
            intel["hint"] = (
                f"{region_name} has {len(enemy_pool)} distinct encounter types."
                if reliable else
                "Intel is too noisy to get an accurate enemy count."
            )
        elif category == "elite_position":
            important_enemies = [
                e for e in (region.encounter_table or region.enemies)
                if e in ENEMY_EXCLUSIVE_MOVE_SPECS
            ]
            intel["elite_enemies"] = important_enemies if reliable else []
            intel["hint"] = (
                f"Elite enemies spotted: {', '.join(important_enemies) or 'none detected'}."
                if reliable else
                "Scout confirms elite presence but cannot pinpoint location."
            )
        elif category == "boss_move_preview":
            villain = self._find_villain(region.boss) if region.boss else None
            if villain and reliable:
                intel["boss_signature_move"] = villain.signature_power.name
                intel["boss_affinity"] = villain.primary_affinity.value
                intel["hint"] = (
                    f"{region.boss} relies on {villain.signature_power.name} "
                    f"({villain.primary_affinity.value} affinity)."
                )
            else:
                intel["boss_signature_move"] = None
                intel["hint"] = "Scout reports unusual energy near the boss territory."
        elif category == "hidden_poi":
            hidden_pois = [poi.name for poi in region.points_of_interest if poi.poi_type != "hub"]
            intel["hidden_pois"] = hidden_pois[:2] if reliable else []
            intel["hint"] = (
                f"Hidden sites located: {', '.join(hidden_pois[:2]) or 'none found'}."
                if reliable else
                "Faint signs of hidden activity but nothing confirmed."
            )

        return intel

    # ------------------------------------------------------------------
    # Feature 14 — Cross-playthrough karmic inheritance
    # ------------------------------------------------------------------

    def compute_karmic_inheritance(self) -> Dict[str, Any]:
        """Derive a starting bonus for the next run based on the vault's dominant playstyle.

        Returns the best-fit inheritance style and the concrete bonuses it unlocks.
        Returns a no-bonus result if the vault has fewer than 2 archived runs.
        """
        if len(self.vault_historic_ninjas) < 2:
            return {
                "eligible": False,
                "reason": "At least 2 completed runs required for karmic inheritance.",
                "style": None,
                "reputation_bonus": 0,
                "free_move_style": None,
            }
        heroic_count = sum(
            1 for entry in self.vault_historic_ninjas
            if int(entry.get("reputation", 0)) >= HEROIC_THRESHOLD_MIN
        )
        rogue_count = sum(
            1 for entry in self.vault_historic_ninjas
            if int(entry.get("reputation", 0)) <= ROGUE_THRESHOLD_MIN
        )
        nonlethal_count = sum(
            1 for entry in self.vault_historic_ninjas
            if bool(entry.get("nonlethal_path", False))
        )
        counts = {
            "heroic": heroic_count,
            "rogue": rogue_count,
            "nonlethal": nonlethal_count,
        }
        dominant_style = max(counts, key=lambda k: (counts[k], k))
        if counts[dominant_style] == 0:
            return {
                "eligible": False,
                "reason": "No dominant playstyle has emerged across archived runs.",
                "style": None,
                "reputation_bonus": 0,
                "free_move_style": None,
            }
        rep_direction = {
            "heroic": KARMIC_INHERITANCE_REP_BONUS,
            "rogue": -KARMIC_INHERITANCE_REP_BONUS,
            "nonlethal": KARMIC_INHERITANCE_REP_BONUS,
        }[dominant_style]
        free_move_style = dominant_style  # The new run unlocks one matching-style move for free
        return {
            "eligible": True,
            "style": dominant_style,
            "dominant_counts": counts,
            "reputation_bonus": rep_direction,
            "free_move_style": free_move_style,
            "description": (
                f"Past runs favor the {dominant_style} path.  "
                f"New run gains {abs(rep_direction)} reputation toward that alignment "
                f"and may claim one {free_move_style}-style move for free."
            ),
        }

    def apply_karmic_inheritance(self, player: PlayerProfile) -> Dict[str, Any]:
        """Apply the karmic inheritance bonuses to a freshly started player profile."""
        inheritance = self.compute_karmic_inheritance()
        if not inheritance["eligible"]:
            return inheritance
        rep_bonus = int(inheritance["reputation_bonus"])
        player.update_reputation(rep_bonus)
        inheritance["applied"] = True
        inheritance["new_reputation"] = player.reputation
        return inheritance

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
                        "climate": region.climate,
                        "terrain_profile": list(region.terrain_profile),
                        "strategic_value": region.strategic_value,
                        "minimum_level": region.minimum_level,
                        "assassin_hunter_name": region.assassin_hunter_name,
                        "travel_nodes": list(region.travel_nodes),
                        "points_of_interest": [
                            {
                                "name": poi.name,
                                "poi_type": poi.poi_type,
                                "summary": poi.summary,
                                "control_faction": poi.control_faction,
                                "threats": list(poi.threats),
                                "services": list(poi.services),
                                "connected_nodes": list(poi.connected_nodes),
                            }
                            for poi in region.points_of_interest
                        ],
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
                        "region_name": quest.region_name,
                        "city_hub": quest.city_hub,
                        "quest_giver": quest.quest_giver,
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
                        "power_origin": villain.power_origin,
                        "arc_ties": list(villain.arc_ties),
                        "player_backstory_hooks": dict(villain.player_backstory_hooks),
                        "signature_power": {
                            "name": villain.signature_power.name,
                            "category": villain.signature_power.category.value,
                            "affinities": [affinity.value for affinity in villain.signature_power.affinities],
                            "power_scale": villain.signature_power.power_scale,
                            "technique_type": villain.signature_power.technique_type.value,
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
                "technique_library": [
                    {
                        "name": move.name,
                        "category": move.category.value,
                        "affinities": [affinity.value for affinity in move.affinities],
                        "power_scale": move.power_scale,
                        "technique_type": move.technique_type.value,
                        "status_effects": [effect.value for effect in move.status_effects],
                        "animation_profile": dict(move.animation_profile),
                    }
                    for move in self.technique_library
                ],
                "shop_inventory": {key: dict(value) for key, value in self.shop_inventory.items()},
                "city_shops": [
                    {
                        "key": shop.key,
                        "name": shop.name,
                        "region_name": shop.region_name,
                        "city_name": shop.city_name,
                        "specialty": shop.specialty,
                        "description": shop.description,
                        "inventory_item_keys": list(shop.inventory_item_keys),
                    }
                    for shop in self.city_shops
                ],
                "city_npcs": [
                    {
                        "name": npc.name,
                        "region_name": npc.region_name,
                        "city_name": npc.city_name,
                        "role": npc.role,
                        "disposition": npc.disposition,
                        "dialogue": npc.dialogue,
                        "services": list(npc.services),
                        "pickpocket_difficulty": npc.pickpocket_difficulty,
                        "pickpocket_rewards": list(npc.pickpocket_rewards),
                    }
                    for npc in self.city_npcs
                ],
                "vault_historic_ninjas": list(self.vault_historic_ninjas),
                "vault_meta_tapestry": list(self.vault_meta_tapestry),
                "active_run_tapestry": list(self.active_run_tapestry),
                "world_event_history": list(self.world_event_history),
                "arc_transition_history": [dict(entry) for entry in self.arc_transition_history],
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
                "npc_evil_profiles": {
                    name: {
                        "evil_tier": str(payload.get("evil_tier", "balanced")),
                        "evil_score": int(payload.get("evil_score", 0)),
                        "evil_threshold": int(
                            payload.get(
                                "evil_threshold",
                                NPC_EVIL_TIER_THRESHOLDS["balanced"],
                            )
                        ),
                        "can_turn": bool(payload.get("can_turn", True)),
                        "last_trigger": payload.get("last_trigger"),
                    }
                    for name, payload in self.npc_evil_profiles.items()
                },
                "city_immersion_state": {
                    city_name: {
                        "alert_level": int(state.get("alert_level", 0)),
                        "intel_noise": int(state.get("intel_noise", 0)),
                        "quest_pressure": int(state.get("quest_pressure", 0)),
                    }
                    for city_name, state in self.city_immersion_state.items()
                },
                "npc_consequence_state": {
                    npc_name: {
                        "suspicion": int(state.get("suspicion", 0)),
                        "trust": int(state.get("trust", 0)),
                        "intel_shared": int(state.get("intel_shared", 0)),
                    }
                    for npc_name, state in self.npc_consequence_state.items()
                },
                "npc_consequence_log": [dict(entry) for entry in self.npc_consequence_log],
                "external_pressure_history": [dict(entry) for entry in self.external_pressure_history],
                "intel_discovery_log": [dict(entry) for entry in self.intel_discovery_log],
                "memory_store": {
                    subject: [str(entry) for entry in entries]
                    for subject, entries in self.memory_store.items()
                },
                "time_cycle_index": self.time_cycle_index,
                "weather_cycle_index": self.weather_cycle_index,
                "environment_cycle_step": self.environment_cycle_step,
                "rival_profile": (
                    {
                        "name": self.rival_profile.name,
                        "affinity": self.rival_profile.affinity.value,
                        "alignment": self.rival_profile.alignment,
                        "cleared_regions": list(self.rival_profile.cleared_regions),
                        "encounter_count": self.rival_profile.encounter_count,
                        "relationship": self.rival_profile.relationship,
                        "loot_claims": list(self.rival_profile.loot_claims),
                    }
                    if self.rival_profile else None
                ),
                "boss_echo_registry": {
                    region_name: {
                        "region_name": echo.region_name,
                        "boss_name": echo.boss_name,
                        "echo_stance": echo.echo_stance.value,
                        "borrowed_move_names": list(echo.borrowed_move_names),
                        "times_challenged": echo.times_challenged,
                        "times_defeated": echo.times_defeated,
                    }
                    for region_name, echo in self.boss_echo_registry.items()
                },
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
                climate=item.get("climate", "temperate"),
                terrain_profile=tuple(item.get("terrain_profile", [])),
                strategic_value=item.get("strategic_value", ""),
                minimum_level=int(item.get("minimum_level", 1)),
                assassin_hunter_name=item.get("assassin_hunter_name", "Regional Assassin Cell"),
                travel_nodes=list(item.get("travel_nodes", [])),
                points_of_interest=[
                    PointOfInterest(
                        name=poi.get("name", ""),
                        poi_type=poi.get("poi_type", poi.get("type", "landmark")),
                        summary=poi.get("summary", ""),
                        control_faction=poi.get("control_faction", ""),
                        threats=tuple(poi.get("threats", [])),
                        services=tuple(poi.get("services", [])),
                        connected_nodes=tuple(poi.get("connected_nodes", [])),
                    )
                    for poi in item.get("points_of_interest", [])
                    if poi.get("name")
                ],
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
                region_name=item.get("region_name", ""),
                city_hub=item.get("city_hub", ""),
                quest_giver=item.get("quest_giver", ""),
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
                power_origin=item.get("power_origin", ""),
                arc_ties=tuple(item.get("arc_ties", [])),
                player_backstory_hooks=dict(item.get("player_backstory_hooks", {})),
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
                    technique_type=TechniqueType(
                        item.get("signature_power", {}).get("technique_type", TechniqueType.ELEMENTAL.value)
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
        technique_library = [
            Move(
                name=move["name"],
                category=MoveCategory(move["category"]),
                affinities=tuple(Affinity(affinity) for affinity in move["affinities"]),
                power_scale=move.get("power_scale", 1.0),
                technique_type=TechniqueType(move.get("technique_type", TechniqueType.ELEMENTAL.value)),
                status_effects=tuple(
                    StatusEffectType(effect) for effect in move.get("status_effects", [])
                ),
                animation_profile=dict(move.get("animation_profile", {})),
            )
            for move in world_snapshot.get("technique_library", [])
        ]
        city_shops = [
            CityShop(
                key=item["key"],
                name=item["name"],
                region_name=item.get("region_name", ""),
                city_name=item.get("city_name", ""),
                specialty=item.get("specialty", ""),
                description=item.get("description", ""),
                inventory_item_keys=tuple(item.get("inventory_item_keys", [])),
            )
            for item in world_snapshot.get("city_shops", [])
        ]
        city_npcs = [
            CityNPC(
                name=item["name"],
                region_name=item.get("region_name", ""),
                city_name=item.get("city_name", ""),
                role=item.get("role", ""),
                disposition=item.get("disposition", ""),
                dialogue=item.get("dialogue", ""),
                services=tuple(item.get("services", [])),
                pickpocket_difficulty=int(item.get("pickpocket_difficulty", 6)),
                pickpocket_rewards=tuple(item.get("pickpocket_rewards", [])),
            )
            for item in world_snapshot.get("city_npcs", [])
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

        rival_data = world_snapshot.get("rival_profile")
        rival_profile: RivalProfile | None = None
        if rival_data:
            rival_profile = RivalProfile(
                name=rival_data["name"],
                affinity=Affinity(rival_data["affinity"]),
                alignment=rival_data.get("alignment", "neutral"),
                cleared_regions=list(rival_data.get("cleared_regions", [])),
                encounter_count=int(rival_data.get("encounter_count", 0)),
                relationship=rival_data.get("relationship", "stranger"),
                loot_claims=list(rival_data.get("loot_claims", [])),
            )

        boss_echo_registry: Dict[str, BossEchoForm] = {
            region_name: BossEchoForm(
                region_name=echo_data["region_name"],
                boss_name=echo_data["boss_name"],
                echo_stance=VillainStance(echo_data["echo_stance"]),
                borrowed_move_names=list(echo_data.get("borrowed_move_names", [])),
                times_challenged=int(echo_data.get("times_challenged", 0)),
                times_defeated=int(echo_data.get("times_defeated", 0)),
            )
            for region_name, echo_data in world_snapshot.get("boss_echo_registry", {}).items()
        }

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
            technique_library=technique_library,
            shop_inventory={key: dict(value) for key, value in world_snapshot.get("shop_inventory", {}).items()},
            city_shops=city_shops,
            city_npcs=city_npcs,
            vault_historic_ninjas=list(world_snapshot.get("vault_historic_ninjas", [])),
            vault_meta_tapestry=list(world_snapshot.get("vault_meta_tapestry", [])),
            active_run_tapestry=list(world_snapshot.get("active_run_tapestry", [])),
            world_event_history=list(world_snapshot.get("world_event_history", [])),
            arc_transition_history=list(world_snapshot.get("arc_transition_history", [])),
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
            npc_evil_profiles={
                name: {
                    "evil_tier": str(payload.get("evil_tier", "balanced")),
                    "evil_score": int(payload.get("evil_score", 0)),
                    "evil_threshold": int(
                        payload.get("evil_threshold", NPC_EVIL_TIER_THRESHOLDS["balanced"])
                    ),
                    "can_turn": bool(payload.get("can_turn", True)),
                    "last_trigger": payload.get("last_trigger"),
                }
                for name, payload in world_snapshot.get("npc_evil_profiles", {}).items()
            },
            city_immersion_state={
                city_name: {
                    "alert_level": int(payload.get("alert_level", 0)),
                    "intel_noise": int(payload.get("intel_noise", 0)),
                    "quest_pressure": int(payload.get("quest_pressure", 0)),
                }
                for city_name, payload in world_snapshot.get("city_immersion_state", {}).items()
            },
            npc_consequence_state={
                npc_name: {
                    "suspicion": int(payload.get("suspicion", 0)),
                    "trust": int(payload.get("trust", 0)),
                    "intel_shared": int(payload.get("intel_shared", 0)),
                }
                for npc_name, payload in world_snapshot.get("npc_consequence_state", {}).items()
            },
            npc_consequence_log=list(world_snapshot.get("npc_consequence_log", [])),
            external_pressure_history=list(world_snapshot.get("external_pressure_history", [])),
            intel_discovery_log=list(world_snapshot.get("intel_discovery_log", [])),
            memory_store={
                str(subject): [str(entry) for entry in entries]
                for subject, entries in world_snapshot.get("memory_store", {}).items()
            },
            time_cycle_index=int(world_snapshot.get("time_cycle_index", 0)),
            weather_cycle_index=int(world_snapshot.get("weather_cycle_index", 0)),
            environment_cycle_step=int(world_snapshot.get("environment_cycle_step", 0)),
            rival_profile=rival_profile,
            boss_echo_registry=boss_echo_registry,
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
                    "reward_inventory", {"weapon": [], "clothing": [], "move": [], "tool": []}
                ).items()
            },
            red_bar_power_claims={
                villain_name: move_name
                for villain_name, move_name in player_snapshot.get("red_bar_power_claims", {}).items()
            },
            enemy_move_claims={
                enemy_name: move_name
                for enemy_name, move_name in player_snapshot.get("enemy_move_claims", {}).items()
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
            quest_resolution_state={
                quest_id: dict(state)
                for quest_id, state in player_snapshot.get("quest_resolution_state", {}).items()
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
            locked_on_target=player_snapshot.get("locked_on_target"),
            owned_tools=list(player_snapshot.get("owned_tools", [])),
            mobile_fast_travel_node=player_snapshot.get("mobile_fast_travel_node"),
            action_attributes={
                key: int(value)
                for key, value in player_snapshot.get(
                    "action_attributes",
                    {name: spec["default"] for name, spec in ACTION_ATTRIBUTE_SPECS.items()},
                ).items()
            },
            attribute_points=int(player_snapshot.get("attribute_points", 0)),
            pickpocket_history={
                key: int(value)
                for key, value in player_snapshot.get(
                    "pickpocket_history",
                    {"success": 0, "caught": 0},
                ).items()
            },
            unlocked_move_names=set(player_snapshot.get("unlocked_move_names", [])),
            active_status_effects={
                effect_name: {
                    "duration": int(payload.get("duration", 0)),
                    "stacks": int(payload.get("stacks", 0)),
                }
                for effect_name, payload in player_snapshot.get("active_status_effects", {}).items()
            },
            chakra=int(player_snapshot.get("chakra", CHAKRA_START)),
            move_proficiency={
                k: int(v) for k, v in player_snapshot.get("move_proficiency", {}).items()
            },
            nonlethal_flow_streak=int(player_snapshot.get("nonlethal_flow_streak", 0)),
            weapon_durability={
                k: int(v) for k, v in player_snapshot.get("weapon_durability", {}).items()
            },
            reputation_inactivity_ticks=int(
                player_snapshot.get("reputation_inactivity_ticks", 0)
            ),
        )
        for category_name, moves in player_snapshot.get("moves_by_set", {}).items():
            category = MoveCategory(category_name)
            player.moves_by_set[category] = [
                Move(
                    name=move["name"],
                    category=MoveCategory(move["category"]),
                    affinities=tuple(Affinity(affinity) for affinity in move["affinities"]),
                    power_scale=move.get("power_scale", 1.0),
                    technique_type=TechniqueType(move.get("technique_type", TechniqueType.ELEMENTAL.value)),
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
        player.reward_inventory.setdefault("tool", [])
        for attribute_name, spec in ACTION_ATTRIBUTE_SPECS.items():
            player.action_attributes.setdefault(attribute_name, int(spec["default"]))
        if not player.enemy_move_claims:
            move_to_enemy = {spec["name"]: enemy for enemy, spec in ENEMY_EXCLUSIVE_MOVE_SPECS.items()}
            player.enemy_move_claims = {
                enemy_name: move_name
                for move_name in player.unlocked_move_names
                for enemy_name in [move_to_enemy.get(move_name)]
                if enemy_name
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
