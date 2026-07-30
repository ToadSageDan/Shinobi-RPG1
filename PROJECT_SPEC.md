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

## Regions and Region Bosses

| # | Region | Hub Village | Boss | Boss Arc |
|---|--------|-------------|------|----------|
| 1 | Verdant Gate | Leafrise Village | Kage Renda (Wind Duelist) | Political Warfront |
| 2 | Ashen Cradle | Cinder Port | General Voln (Fire Warlord) | Fracture Front |
| 3 | Tideglass Basin | Azure Rest | Admiral Neris (Water Controller) | Recovery Mandate |
| 4 | Stormwall Ridge | Crestfall Outpost | Zephyr Tyrant (Wind Warlord) | Highland Reckoning / Rebellion Wave |
| 5 | Sunken Hollow | Dusk Refuge | Ashen Monarch (Earth Breaker) | Depths Awakening / Fracture Front |

### Storyline Arcs
- **Political Warfront** — Council leverage and control of supply routes; first region.
- **Fracture Front** — Alliances fail or harden under pressure; fiery and underground zones.
- **Recovery Mandate** — World stabilizes or collapses into splinter rule; coastal / water region.
- **Rebellion Wave** — Minor actors radicalize into existential threats; spans early and storm regions.
- **Highland Reckoning** — A mountain warlord's domain falls or expands to swallow nearby territories.
- **Depths Awakening** — Forgotten underground power is weaponized or sealed before it destabilizes the surface.

## Enemies by Region

| Region | Field Enemies | Boss |
|--------|--------------|------|
| Verdant Gate | Bandit Scouts, Mist Ronin*, Root Stalkers*, Hidden Sentry | Kage Renda |
| Ashen Cradle | Ash Mercenaries*, Lava Hounds, Ember Raiders* | General Voln |
| Tideglass Basin | Tide Hunters*, Reef Assassins*, Basin Corsairs | Admiral Neris |
| Stormwall Ridge | Windcutter Raiders*, Gale Monks*, Ridge Wolves, Stormcaller Scouts*, Aerial Sentry | Zephyr Tyrant |
| Sunken Hollow | Cave Stalkers*, Poison Adepts*, Hollow Wraiths*, Ember Moles, Deep Sentries | Ashen Monarch |

`*` = Important enemy with an exclusive learnable move

## Enemy Exclusive Learnable Moves

Important field enemies carry a signature technique the player may learn after defeating them.
These are separate from boss rewards — earned through field encounters.

| Enemy | Learnable Move | Category | Affinity | Key Effects |
|-------|---------------|----------|----------|-------------|
| Mist Ronin | Fog Dagger Surge | Attack | Water | Blind |
| Root Stalkers | Creeping Vine Bind | Defense | Earth | Root |
| Ash Mercenaries | Scorch Rush | Attack | Fire | Burn |
| Ember Raiders | Ember Burst | Attack | Fire | Burn, Stagger |
| Tide Hunters | Deep Current Drag | Escape | Water | Drench |
| Reef Assassins | Reef Shadow Lunge | Attack | Water | Bleed, Drench |
| Windcutter Raiders | Gale Blade Flurry | Attack | Wind | Bleed, Stagger |
| Gale Monks | Resonant Wind Seal | Defense | Wind | Silence |
| Stormcaller Scouts | Lightning Thread | Attack | Wind | Stagger, Crack Armor |
| Cave Stalkers | Blind Ambush | Attack | Earth | Blind |
| Poison Adepts | Venom Weave | Attack | Earth | Bleed, Crack Armor |
| Hollow Wraiths | Wraith Shriek | Attack | Wind | Fear, Silence |


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
