# Shinobi-RPG1 Project Spec

## Goal
Build a lightweight MVP foundation for a ninja-inspired open-world RPG with progression, combat choices, and replay tracking.

## Player Setup
- Player starts with a name and base stats.
- Player completes an affinity mini-game.
- One affinity is assigned from: Fire, Water, Earth, Wind.

## Combat Move Rules
- Move sets: Escape, Attack, Defense, Summon, Ultimate.
- Non-ultimate moves must use a single affinity.
- Ultimate moves may combine multiple affinities.

## Progression Systems
- Stats and leveling progression affect gameplay outcomes.
- Reputation tracks player behavior and alignment.
- Rogue Ninja path unlocks through reputation progression.
- Black Market unlocks after Rogue Ninja path conditions are met.

## Equipment and Rewards
- Core weapons: sword, kunai, bow staff, ninja stars.
- Region and boss progression grants reward choices:
  - weapon
  - clothing
  - move
- Unlockable skins provide stat boosts.

## World and Questing
- Region progression gates access to tougher content.
- Bosses act as progression milestones.
- Quest chain includes stealth-required content.
- Fast travel unlocks through progression milestones.

## Allies
- Seed default allies: Dan, Moon, Sleep, Dot, Porter.
- Support auto-generation of allies to at least 10 total.

## Replay and Persistence
- Include a vault archive that stores historic ninja runs for replay/history tracking.

## Narrative and Meta Backlog
- Add main-character backstories that branch story outcomes.
- Add villain backstories that influence behavior over time.
- Villain aggression/passivity should react to in-game decisions.
- Support a highly unlikely but possible full nonlethal completion path using charm, stealth, and ninja evasion.
- Start compiling a player trophy list to accumulate over playthroughs; define final trophy set in a later design pass.

## Build-Ready MVP Acceptance Criteria
1. A new player can be created and assigned one affinity via mini-game input.
2. All five move set categories exist and affinity rules are enforced.
3. At least one full region clear + boss reward flow works.
4. Reputation changes can unlock Rogue Ninja path and Black Market.
5. Weapon, clothing, and move rewards can all be granted.
6. Stealth quest content is reachable and completable.
7. Fast travel unlock condition is reachable through normal progression.
8. Vault archive records completed runs.
9. Seed allies exist and auto-generation reaches 10+ allies.

## Validation
- Run tests with:
  - `python -m unittest discover -s tests -p "test_*.py"`
