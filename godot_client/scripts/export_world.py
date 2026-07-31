#!/usr/bin/env python3
"""export_world.py — Exports the Shinobi RPG world data to JSON for the Godot client.

Run from the repository root:
    python godot_client/scripts/export_world.py

Output: godot_client/data/world_data.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow importing shinobi_rpg from the repo root
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from shinobi_rpg.core import (
    Affinity,
    BOSS_EXCLUSIVE_MOVE_SPECS,
    ENEMY_EXCLUSIVE_MOVE_SPECS,
    MoveCategory,
    _seed_regions,
    _seed_quests,
    _seed_villains,
    _seed_allies,
    _seed_shop_inventory,
    _seed_moves,
    build_mvp_world,
)


def _serialise_move(move) -> dict:
    return {
        "name": move.name,
        "category": move.category.value,
        "affinities": [a.value for a in move.affinities],
        "power_scale": move.power_scale,
        "technique_type": move.technique_type.value,
        "status_effects": [e.value for e in move.status_effects],
    }


def _serialise_region(region) -> dict:
    return {
        "key": region.name.lower().replace(" ", "_"),
        "name": region.name,
        "village_hub": region.village_hub,
        "enemies": region.enemies,
        "encounter_table": region.encounter_table,
        "allies": region.allies,
        "boss": region.boss,
        "boss_rewards": region.boss_rewards,
        "arc_key": region.arc_key,
        "climate": region.climate,
        "terrain_profile": list(region.terrain_profile),
        "strategic_value": region.strategic_value,
        "minimum_level": region.minimum_level,
        "travel_nodes": list(region.travel_nodes),
        "points_of_interest": [
            {
                "name": poi.name,
                "poi_type": poi.poi_type,
                "summary": poi.summary,
                "control_faction": poi.control_faction,
                "threats": list(poi.threats),
                "services": list(poi.services),
            }
            for poi in region.points_of_interest
        ],
    }


def _serialise_quest(quest) -> dict:
    return {
        "quest_id": quest.quest_id,
        "title": quest.title,
        "objective": quest.objective,
        "stealth_required": quest.stealth_required,
        "reward_xp": quest.reward_xp,
        "premise": quest.premise,
        "choices": list(quest.choices),
        "branch_outcomes": quest.branch_outcomes,
        "follow_up_hook": quest.follow_up_hook,
    }


def _serialise_villain(villain) -> dict:
    return {
        "name": villain.name,
        "backstory": villain.backstory,
        "primary_affinity": villain.primary_affinity.value,
        "role": villain.role,
        "aggression_score": villain.aggression_score,
        "signature_move": _serialise_move(villain.signature_power),
        "power_origin": villain.power_origin,
        "arc_ties": list(villain.arc_ties),
    }


def _serialise_boss_data(villain_name: str, region) -> dict:
    spec = BOSS_EXCLUSIVE_MOVE_SPECS.get(villain_name, {})
    return {
        "affinity": next(
            (v.primary_affinity.value for v in _seed_villains() if v.name == villain_name),
            "fire",
        ),
        "hp": 350 + (region.minimum_level * 18),
        "power": 12 + region.minimum_level * 2,
        "defense": 10 + region.minimum_level,
        "signature_move": spec.get("name", ""),
        "signature_power_scale": spec.get("power_scale", 1.2),
        "signature_statuses": [e.value for e in spec.get("status_effects", [])],
        "phase2_hp_threshold": 0.5,
        "phase2_power_bonus": 6 + region.minimum_level,
        "taunt_lines": _boss_taunt_lines(villain_name),
    }


def _boss_taunt_lines(boss_name: str) -> list[str]:
    taunt_map = {
        "Kage Renda": [
            "These roads are mine by blood and wind.",
            "You crossed the last gate you will ever see.",
            "The Skybridge has claimed stronger shinobi than you.",
        ],
        "General Voln": [
            "This front never broke — it just ran out of recruits.",
            "You smell like forest. You are in the wrong war.",
            "Every furnace-city battle ended the same way. This one will too.",
        ],
        "Admiral Neris": [
            "The basin drowns everyone eventually.",
            "Every order I gave was law — until you.",
            "You can't outmanoeuvre the tide.",
        ],
        "Zephyr Tyrant": [
            "The ridge sings only for me.",
            "You climbed this high only to fall further.",
            "Every gust here answers to my will.",
        ],
        "Ashen Monarch": [
            "This vault was old when your bloodline was young.",
            "The earth always reclaims what it gave.",
            "You are walking into the deepest grave in the Confederacy.",
        ],
    }
    return taunt_map.get(boss_name, [f"{boss_name} stands ready."])


def _serialise_ally(ally) -> dict:
    return {"name": ally}


def _all_moves() -> list[dict]:
    all_moves = []
    seen_names = set()
    for affinity in Affinity:
        move_sets = _seed_moves(affinity)
        for category_moves in move_sets.values():
            for move in category_moves:
                if move.name not in seen_names:
                    all_moves.append(_serialise_move(move))
                    seen_names.add(move.name)
    # Add boss and enemy exclusive moves
    for spec in list(BOSS_EXCLUSIVE_MOVE_SPECS.values()) + list(ENEMY_EXCLUSIVE_MOVE_SPECS.values()):
        name = spec.get("name", "")
        if name and name not in seen_names:
            all_moves.append({
                "name": name,
                "category": spec["category"].value,
                "affinities": [a.value for a in spec["affinities"]],
                "power_scale": spec.get("power_scale", 1.0),
                "technique_type": spec["technique_type"].value,
                "status_effects": [e.value for e in spec.get("status_effects", [])],
            })
            seen_names.add(name)
    return all_moves


def _shop_items() -> list[dict]:
    # Build a minimal world to get shop inventory
    _, player = build_mvp_world("export_player", [5, 1, 1, 1])
    from shinobi_rpg.core import NinjaWorld, _seed_shop_inventory
    # Return raw shop inventory specs as serialisable dicts
    raw = _seed_shop_inventory()
    return [
        {
            "key": item.key if hasattr(item, "key") else str(i),
            "name": item.name if hasattr(item, "name") else "Item",
            "price": item.price if hasattr(item, "price") else 0,
            "description": item.description if hasattr(item, "description") else "",
        }
        for i, item in enumerate(raw)
    ]


def export(output_path: Path) -> None:
    regions = _seed_regions()
    quests = _seed_quests()
    villains = _seed_villains()
    allies = _seed_allies()

    boss_dict: dict = {}
    for region in regions:
        boss_dict[region.boss] = _serialise_boss_data(region.boss, region)

    data = {
        "regions": [_serialise_region(r) for r in regions],
        "quests": [_serialise_quest(q) for q in quests],
        "villains": [_serialise_villain(v) for v in villains],
        "bosses": boss_dict,
        "allies": [_serialise_ally(a) for a in allies],
        "moves": _all_moves(),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Exported world data → {output_path}")
    print(f"  Regions: {len(data['regions'])}")
    print(f"  Quests:  {len(data['quests'])}")
    print(f"  Villains:{len(data['villains'])}")
    print(f"  Moves:   {len(data['moves'])}")
    print(f"  Allies:  {len(data['allies'])}")


if __name__ == "__main__":
    out = ROOT / "godot_client" / "data" / "world_data.json"
    if len(sys.argv) > 1:
        out = Path(sys.argv[1])
    export(out)
