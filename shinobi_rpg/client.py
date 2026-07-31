"""Presentation/runtime layer for visual-first Shinobi RPG experiences."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from .core import MoveCategory, build_mvp_world

VISUAL_TARGET = {
    "style": "2.5D_stylized",
    "camera": "third_person_cinematic",
    "ui_density": "adaptive_hud",
}


@dataclass(frozen=True)
class RuntimeScene:
    key: str
    title: str
    scene_type: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "scene_type": self.scene_type,
            "payload": dict(self.payload),
        }


class ShinobiRuntimeClient:
    """Client shell that renders simulation data into runtime scene models."""

    def __init__(self, player_name: str = "Dan") -> None:
        self.world, self.player = build_mvp_world(player_name, [3, 1, 2, 4, 5])

    def build_title_menu_scene(self) -> RuntimeScene:
        return RuntimeScene(
            key="title_menu",
            title="Shinobi RPG",
            scene_type="menu",
            payload={
                "subtitle": "A visual-first ninja world experience",
                "menu_options": [
                    {"label": "Start Vertical Slice", "route": "vertical_slice"},
                    {"label": "Open World Map", "route": "world_map"},
                    {"label": "Preview Combat Timelines", "route": "move_timelines"},
                    {"label": "Exit", "route": "exit"},
                ],
                "default_selection": "Start Vertical Slice",
                "visual_target": dict(VISUAL_TARGET),
            },
        )

    def build_world_map_scene(self) -> RuntimeScene:
        world_map = self.world.generate_mock_world_map()
        return RuntimeScene(
            key="interactive_world_map",
            title="World Map: Quiet Steel Confederacy",
            scene_type="world_map",
            payload={
                "camera_mode": "orbit_zoom_pan",
                "markers": list(world_map["markers"]),
                "routes": list(world_map["routes"]),
                "recommended_route": list(world_map["recommended_route"]),
                "active_dynamic_route": list(world_map["active_dynamic_route"]),
                "environment": self.world.get_environment_state(),
                "interaction_hint": "Select a marker to inspect region quests, NPC pressure, and boss pathing.",
            },
        )

    def build_move_timeline_scene(self, move_name: str = "Edge Current") -> RuntimeScene:
        preview = self.world.get_move_animation_preview(move_name)
        combo_preview = self.world.preview_affinity_combo_animation(
            "Undertow Slice",
            "Crosswind Fade",
            "Skyline Covenant",
        )
        return RuntimeScene(
            key="combat_timeline_preview",
            title="Combat Timeline Preview",
            scene_type="combat_timeline",
            payload={
                "move_preview": preview,
                "combo_preview": combo_preview,
                "camera_rules": {
                    "traversal": "steady_follow",
                    "impact": "impulse_shake_8px",
                    "boss_moment": "dramatic_push_in",
                },
                "hit_feedback": {
                    "impact_pause_ms": 70,
                    "spark_layer": True,
                    "blood_intensity": preview["skill_physics"]["blood_intensity"],
                    "audio_layering": "impact+affinity+status",
                },
            },
        )

    def build_vertical_slice_scene(self) -> RuntimeScene:
        region = self.world.regions[0]
        quest = next(item for item in self.world.quests if item.region_name == region.name)
        city_state = self.world.city_immersion_state.get(region.village_hub, {})
        boss_intro = (
            f"{region.boss} enters from {region.points_of_interest[-1].name} with {region.climate} pressure."
        )
        return RuntimeScene(
            key="vertical_slice_verdant_gate",
            title="Vertical Slice: Verdant Gate",
            scene_type="vertical_slice",
            payload={
                "hub": {
                    "region": region.name,
                    "village_hub": region.village_hub,
                    "explorable_nodes": list(region.travel_nodes),
                    "npcs": [
                        npc.name for npc in self.world.city_npcs if npc.region_name == region.name
                    ][:4],
                },
                "combat_encounter": {
                    "enemy": region.field_enemies[0] if region.field_enemies else "Bandit Scouts",
                    "playable_move_categories": [category.value for category in MoveCategory],
                    "timeline_quality_gate": "startup_travel_hit_recovery_required",
                },
                "quest_flow": {
                    "quest_id": quest.quest_id,
                    "quest_title": quest.title,
                    "quest_giver": quest.quest_giver,
                    "objective": quest.objective,
                    "city_pressure": city_state.get("quest_pressure", 0),
                },
                "boss_sequence": {
                    "intro": boss_intro,
                    "outro": f"{region.boss} defeat unlocks reward choice and route expansion.",
                },
                "reward_screen": {
                    "reward_types": ["weapon", "clothing", "move"],
                    "ui_layout": "three_card_choice",
                },
            },
        )

    def build_content_pipeline(self) -> Dict[str, Any]:
        return {
            "characters": {
                "assets": ["player_rig", "ally_rig", "villain_rig"],
                "required_states": ["idle", "run", "attack", "hit", "recover"],
            },
            "environments": {
                "kits": ["verdant_gate_kit", "ashen_cradle_kit", "tideglass_basin_kit"],
                "components": ["terrain", "props", "lighting_profile"],
            },
            "ui": {
                "kit": ["hud", "quest_tracker", "status_effect_strip", "minimap"],
                "accessibility": ["high_contrast_mode", "scalable_text", "color_safe_status_icons"],
            },
            "fx_audio": {
                "vfx_sets": ["fire", "water", "earth", "wind"],
                "audio_layers": ["impact", "affinity", "status"],
            },
        }

    def build_visual_acceptance_gates(self) -> Dict[str, Any]:
        return {
            "combat_animation_coverage": {
                "rule": "all moves require startup/travel/hit/recovery",
                "status": "enforced",
            },
            "quest_feedback_clarity": {
                "rule": "all quest steps must render objective and world reaction",
                "status": "enforced",
            },
            "hud_accessibility": {"rule": "core HUD supports readability/accessibility pass", "status": "enforced"},
            "performance_budget": {"rule": "scene frame budget checks required", "status": "enforced"},
        }

    def build_runtime_package(self) -> Dict[str, Any]:
        scenes: List[RuntimeScene] = [
            self.build_title_menu_scene(),
            self.build_world_map_scene(),
            self.build_move_timeline_scene(),
            self.build_vertical_slice_scene(),
        ]
        return {
            "visual_target": dict(VISUAL_TARGET),
            "simulation_layer": "shinobi_rpg.core",
            "presentation_layer": "shinobi_rpg.client",
            "scenes": [scene.to_dict() for scene in scenes],
            "content_pipeline": self.build_content_pipeline(),
            "cinematic_systems": {
                "camera_rules": "traversal, impact, and boss-specific camera states",
                "hit_feedback": "impact pause + shake + vfx/audio layering",
                "world_ambience": "time-of-day and weather drive regional mood",
            },
            "acceptance_gates": self.build_visual_acceptance_gates(),
            "expansion_strategy": "Scale to more regions only after vertical slice quality gates stay green.",
        }


def runtime_package_json(player_name: str = "Dan") -> str:
    client = ShinobiRuntimeClient(player_name=player_name)
    return json.dumps(client.build_runtime_package(), indent=2, sort_keys=True)
