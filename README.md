# Shinobi-RPG1

Lightweight MVP foundation for a ninja-inspired open-world RPG.

## Included MVP systems

- Affinity mini-game and assignment (Fire/Water/Earth/Wind)
- Four move sets: Escape, Attack, Defense, Ultimate
- Rule enforcement: non-ultimates are single-affinity; ultimates can mix affinities
- Stats and leveling progression
- Reputation system with Rogue Ninja path and Black Market unlock
- Weapons: sword, kunai, bow staff, ninja stars
- Region and boss progression with reward choices (weapon/clothing/move)
- Quest chain including stealth-required content
- Seeded allies (Dan, Moon, Sleep, Dot, Porter) with auto-generation to 10+
- Unlockable skins with stat boosts
- Fast travel unlocks from progression
- Vault archive for historic ninja runs
- Player backstory selection with narrative/reputation impact
- Villain backstories with aggression/passivity shifts from player decisions
- Backstory-driven quest branch outcomes
- Region/boss-specific villain behavior rules by stance
- Nonlethal progression tracking via charm, stealth, and evasion outcomes
- Expanded trophy catalog with category-based unlock conditions
- Playthrough summary report including backstory, trophies, reputation, and villain stances

## Run tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Example usage

```python
from shinobi_rpg.core import build_mvp_world

world, player = build_mvp_world("Dan", [3, 1, 2, 4, 5])
reward = world.clear_region(player, "Verdant Gate", "move")
print(player.affinity.value, reward)
```
