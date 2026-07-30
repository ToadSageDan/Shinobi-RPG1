# Shinobi-RPG1

Lightweight MVP foundation for a ninja-inspired open-world RPG.

## Included MVP systems

- Affinity mini-game and assignment (Fire/Water/Earth/Wind)
- Five move sets: Escape, Attack, Defense, Summon, Ultimate
- Rule enforcement: non-ultimates are single-affinity; ultimates can mix affinities
- Stats and leveling progression
- Reputation system with Rogue Ninja path and Black Market unlock
- Weapons: sword, kunai, bow staff, ninja stars
- Region and boss progression with reward choices (weapon/clothing/move)
- Save/load snapshots for full world + player progression state
- Quest state flow (active/completed/failed) with sequential gating
- Quest chain including stealth-required content
- Seeded allies (Dan, Moon, Sleep, Dot, Porter) plus curated roster names, with AutoNinja fallback to 10+
- Ally loyalty tracking influenced by decisions and quest outcomes
- Region-specific encounter tables for replayable deterministic rotations
- Unlockable skins with stat boosts
- Fast travel unlocks from progression
- Vault archive for historic ninja runs
- Vault replay analytics for run history, trophy frequency, and top run summary
- Replay hub report combining active-run summary and archive analytics
- Player backstory selection with narrative/reputation impact
- Villain backstories with aggression/passivity shifts from player decisions
- Villain-specific decision memory in behavior and summary reporting
- Backstory-driven quest branch outcomes
- Dynamic quest branching that can react to nonlethal and reputation paths
- Region/boss-specific villain behavior rules by stance
- Expanded balanced shared move pool (12 per category) for reusable combat design
- Villain kit design with one signature move plus skinned shared move loadouts
- Status effects on weapons/jutsu/summons with capped duration and stack bands
- Combat physics output for moves (impact/knockback/stagger window) with blood intensity tracking
- Combo resolution helper with status-affinity synergy bonuses
- Affinity animation preview metadata for move startup/travel/hit/recovery beats
- Nonlethal progression tracking via charm, stealth, and evasion outcomes
- Reputation-aware shop inventory and Black Market purchasing
- Expanded trophy catalog with category-based unlock conditions
- Trophy tiers (early/mid/late) exposed in summary and progress views
- Trophy progress tracking with near-miss hints
- Playthrough summary report including backstory, trophies, reputation, and villain stances

## Run tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Project standards

- License: [MIT](LICENSE)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Community code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Ordered implementation backlog: [NEXT_STEPS.md](NEXT_STEPS.md)

## Example usage

```python
from shinobi_rpg.core import build_mvp_world

world, player = build_mvp_world("Dan", [3, 1, 2, 4, 5])
reward = world.clear_region(player, "Verdant Gate", "move")
print(player.affinity.value, reward)
```

## HUD display mocks

### Mock A: Minimal/Cinematic HUD (Skyrim-like feel)

| Zone | What shows | Example |
|---|---|---|
| Top-left | HP / Chakra / Stamina as slim bars | HP 120/150, Chakra 80/120, Stamina 65/100 |
| Bottom-center | Quick powers (small, low-noise) | 1: Chidori, 2: Gale Palm, Q: Shadow Step, R: Ultimate |
| Top-center | Name + level | Dan • Lv.17 |
| Top-right | Compass/minimap only | NE marker, objective ping |
| Right side (collapsed by default) | Current objective | Reach Hidden Pass |
| Near reticle/context area | Temporary status icons | Focus buff, Burn debuff |

### Mock B: Full RPG HUD (information-dense)

| Panel | What shows | Example |
|---|---|---|
| Character core | HP, Chakra, Stamina, XP, Level | HP 120/150, XP 72% to Lv.18 |
| Attributes panel | Strength, Agility, Intelligence, Defense, Speed | STR 14, AGI 18, INT 12 |
| Affinity panel | Primary/Secondary affinity + rank + bonuses | Lightning / Wind, Rank B |
| Powers loadout | Equipped jutsu, cooldowns, resource costs, lock states | Kirin locked, Chidori ready |
| Status tracker | Buff/debuff timers + stack counts | Burn x2 (6s), Focus (10s) |
| Quest tracker | Main + side objectives with progress | Main: Reach Hidden Pass (2/4) |
| World awareness | Minimap, alerts, stance/reputation hints | Rogue rep rising, stealth alert |
