# Shinobi-RPG1

Lightweight MVP foundation for a ninja-inspired open-world RPG.

[![CI](https://github.com/ToadSageDan/Shinobi-RPG1/actions/workflows/ci.yml/badge.svg)](https://github.com/ToadSageDan/Shinobi-RPG1/actions/workflows/ci.yml)

## Official project bootstrap

Install the package in editable mode and print the current framework snapshot:

```bash
pip install -e .
python -m shinobi_rpg
```

The bootstrap command outputs a JSON summary of the seeded player setup, supported gameplay systems, packaged content counts, and the core development command for running tests.

## Included MVP systems

- Affinity mini-game and assignment (Fire/Water/Earth/Wind)
- Five move sets: Escape, Attack, Defense, Summon, Ultimate
- Rule enforcement: non-ultimates are single-affinity; ultimates can mix affinities
- Stats and leveling progression
- Reputation system with Rogue Ninja path and Black Market unlock — nonlethal playstyles (charm/stealth/evasion) grant incremental reputation gains
- Weapons: sword, kunai, bow staff, ninja stars
- Region and boss progression with reward choices (weapon/clothing/move)
- Save/load snapshots for full world + player progression state
- Quest state flow (active/completed/failed) with sequential gating
- Quest chain including stealth-required content
- **50 seeded quests (Q1–Q50)** with handcrafted backstory, nonlethal, heroic, and rogue branch outcomes
- Seeded allies (Dan, Moon, Sleep, Dot, Porter) plus curated roster names, with AutoNinja fallback to 10+
- Ally loyalty tracking influenced by decisions and quest outcomes
- Region-specific encounter tables for replayable deterministic rotations
- Unlockable skins with stat boosts
- Fast travel unlocks from progression
- Vault archive for historic ninja runs
- Vault replay analytics for run history, trophy frequency, and top run summary
- Replay hub report combining active-run summary and archive analytics
- Player backstory selection with narrative/reputation impact
- Villain backstories with aggression/passivity shifts from player decisions, `relationship_arc` tracking, and `active_triggers` per checkpoint
- Villain-specific decision memory in behavior and summary reporting
- Backstory-driven quest branch outcomes
- Dynamic quest branching that can react to nonlethal and reputation paths
- Region/boss-specific villain behavior rules by stance
- Expanded balanced shared move pool (12 per category) for reusable combat design
- Villain kit design with one signature move plus skinned shared move loadouts
- **Status effects accumulate stacks** up to the band cap, duration refreshes on re-application
- Combat physics output for moves (impact/knockback/stagger window) with blood intensity tracking
- Combo resolution helper with status-affinity synergy bonuses
- Affinity animation preview metadata for move startup/travel/hit/recovery beats
- Nonlethal progression tracking via charm, stealth, and evasion outcomes
- Reputation-aware shop inventory and Black Market purchasing
- Expanded trophy catalog (36 trophies) with category-based unlock conditions
- Trophy tiers (early/mid/late) exposed in summary and progress views
- Trophy progress tracking with near-miss hints in playthrough summary
- **Playstyle summary** in `generate_playthrough_summary()` — style label, shift detection, nonlethal vs lethal totals
- **Villain relationship arcs** in summary — dormant/active/rival/nemesis/reformed per villain
- Playthrough summary report including backstory, trophies, reputation, and villain stances
- NPC evil-threshold evolution and intel event systems

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

## How to contribute

1. Pick the next open item from [NEXT_STEPS.md](NEXT_STEPS.md) or an open GitHub Issue.
2. Create a branch from `main` (e.g. `feature/quest-gating`).
3. Make your changes and run `python -m unittest discover -s tests -p "test_*.py"`.
4. Open a PR — the **Track Progress** workflow will auto-label it and post the current backlog snapshot.
5. Once merged, the workflow marks the relevant NEXT_STEPS item complete automatically.

For bug reports and feature requests, use the issue templates under [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/).

### Set up the GitHub Project board (one-time, owner only)

1. Go to **https://github.com/ToadSageDan** → **Projects** → **New project** → name it **Shinobi RPG Development** → add columns: Backlog / In Progress / In Review / Done.
2. Run the setup script with a PAT that has `repo` + `project` scopes:

   ```bash
   export GITHUB_TOKEN=<your-PAT>
   python scripts/setup_github_project.py
   ```

   This creates labels, milestone v0.2.0, backfilled closed issues for all completed v0.1.0 work, and open issues for the remaining backlog.

3. Optionally set `PROJECT_ID` to auto-link issues to the board:

   ```bash
   export PROJECT_ID=$(gh project view <number> --owner ToadSageDan --format json | jq .id)
   python scripts/setup_github_project.py
   ```

## Example usage

```python
from shinobi_rpg.core import build_mvp_world

world, player = build_mvp_world("Dan", [3, 1, 2, 4, 5])
reward = world.clear_region(player, "Verdant Gate", "move")
print(player.affinity.value, reward)
```
