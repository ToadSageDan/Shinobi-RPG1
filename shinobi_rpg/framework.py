"""Project bootstrap helpers for the Shinobi RPG MVP."""

from __future__ import annotations

import json
from typing import Any, Dict, Sequence

from .core import Affinity, MoveCategory, build_mvp_world

DEFAULT_BOOTSTRAP_DECISIONS = (3, 1, 2, 4, 5)
DEFAULT_BOOTSTRAP_PLAYER_NAME = "Dan"
TEST_COMMAND = 'python -m unittest discover -s tests -p "test_*.py"'


def get_framework_overview(
    player_name: str = DEFAULT_BOOTSTRAP_PLAYER_NAME,
    affinity_decisions: Sequence[int] = DEFAULT_BOOTSTRAP_DECISIONS,
) -> Dict[str, Any]:
    """Return a build-ready snapshot of the current MVP framework."""

    world, player = build_mvp_world(player_name, affinity_decisions)
    return {
        "project": "Shinobi-RPG1",
        "player_bootstrap": {
            "name": player.name,
            "affinity": player.affinity.value,
            "starting_region": world.regions[0].name,
            "starting_skin": player.unlocked_skins[0].name,
        },
        "framework": {
            "affinities": [affinity.value for affinity in Affinity],
            "move_categories": [category.value for category in MoveCategory],
            "reward_types": ["weapon", "clothing", "move"],
            "supported_paths": ["heroic", "rogue", "nonlethal"],
        },
        "seeded_content": {
            "regions": len(world.regions),
            "points_of_interest": sum(len(region.points_of_interest) for region in world.regions),
            "quests": len(world.quests),
            "allies": len(world.allies),
            "weapons": len(world.weapons),
            "villains": len(world.villains),
            "trophies": len(world.trophy_catalog),
            "backstories": len(world.player_backstories),
            "arcs": len(world.arcs),
        },
        "development": {
            "package": "shinobi-rpg",
            "python": ">=3.11",
            "test_command": TEST_COMMAND,
            "entrypoint": "python -m shinobi_rpg",
        },
    }


def framework_overview_json(
    player_name: str = DEFAULT_BOOTSTRAP_PLAYER_NAME,
    affinity_decisions: Sequence[int] = DEFAULT_BOOTSTRAP_DECISIONS,
) -> str:
    """Serialize the framework overview for CLI use."""

    return json.dumps(
        get_framework_overview(player_name=player_name, affinity_decisions=affinity_decisions),
        indent=2,
        sort_keys=True,
    )
