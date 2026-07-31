# Changelog

All notable changes to Shinobi-RPG1 will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- **v0.6.0 — Art Pass + Polish**
- `PlaceholderRig.gd` — procedural primitive-mesh character rig (capsule body + sphere head +
  limb cylinders) with scripted animation states for idle, run, jump, attack, hurt, death etc.
  Drives the `Player` and `Enemy` scenes when no Mixamo FBX is imported yet. Drop a real
  animated mesh under the character root and the rig is bypassed automatically.
- `Player.tscn` and `Enemy.tscn` updated to include `PlaceholderRig` as a child node with
  affinity-tinted colors; `AnimationPlayer` comment expanded with full clip name list.
- `BiomeTerrain.gd` — static helper that procedurally builds biome-appropriate terrain
  (coloured ground plane, four boundary walls, 12 scatter objects) for all five arenas from
  code at runtime. Called automatically from `BaseArena._ready()`. Each biome has a distinct
  color palette, light tint, and scatter shape (trees / rocks / reef pillars / stalagmites).
- `AffinityVFX.gd` — `RefCounted` class with per-affinity `GPUParticles3D` presets (color
  gradient, emission shape, gravity, velocity, lifetime, scale). Exposes `configure_particles()`
  and `spawn_burst()`. Wired into `JutsuProjectile.launch()` so every fired jutsu is visually
  distinct by element; impact bursts spawn on hit.
- `AudioManifest.gd` autoload — registers the full music + SFX path table with `AudioManager`.
  Gracefully skips missing files and prints console hints pointing to free audio sources
  (opengameart.org / freesound.org / kenney.nl). Registered in `project.godot`.
- `QuestWaypoint.gd` + `QuestWaypoint.tscn` — animated 3D world-space marker: spinning
  diamond icon + vertical beacon beam + billboard `Label3D` showing quest ID and name.
  Bobs and rotates each frame. `BaseArena._spawn_quest_waypoints()` places markers for all
  active quests whose `target_region` matches the current arena.
- `Shop.gd` + `Shop.tscn` — full shop UI: scrollable item list with rep-tier and quest-gate
  locks, detail panel with description / cost / requirements, purchase flow with credits
  deduction, move unlock, feedback toast, and save on buy. 10-item fallback catalog when
  `WorldData.shop_inventory` is empty. Navigated to from WorldMap **🛒 Shop** button.
- `PlaythroughSummary.gd` + `PlaythroughSummary.tscn` — tabbed summary screen with four
  tabs: **Overview** (character, rep, playstyle label, encounter breakdown, move list),
  **Trophies** (full 23-trophy catalog with ✅/○ per tier), **Villains** (arc + stance per
  villain from WorldData), **Quests** (log with ✅/❌ per entry). Navigated to from WorldMap
  **📊** button.
- `Options.gd` + `Options.tscn` — three-tab options screen: **Controls** (remappable table
  for all 15 actions showing keyboard key and gamepad button, click-to-remap with overlay
  prompt, Reset Defaults button), **Audio** (Music/SFX volume sliders with bus routing),
  **Display** (fullscreen toggle). Settings persisted to `user://options.cfg` and restored on
  load. MainMenu **⚙ Options** button now navigates here.
- `BaseArena.gd` updated: `BiomeTerrain.build()` called in `_ready()` for automatic terrain;
  `_spawn_quest_waypoints()` added to place active-quest 3D markers each arena entry.
- `MainMenu.gd` updated: `_on_options()` now navigates to `res://scenes/ui/Options.tscn`.

### Quest Q6 "Legacy of the Fallen Shinobi": final epilogue quest at the Ashen Spire with full backstory, nonlethal, heroic, and rogue branch outcomes
- Quest Q7 "Shattered Moon Accord" and Q8 "Dawn of the Hidden Age" with full backstory, nonlethal, heroic, and rogue branch outcomes
- Quest Q9 "Ashes Beneath the Banner" and Q10 "Veil of the Eternal Watch" to continue seeded quest progression with full backstory, nonlethal, heroic, and rogue branch outcomes
- Quest Q11 "Ashes of the Courier" through Q15 "Feast of Knives" now include handcrafted backstory, nonlethal, heroic, and rogue branch outcomes
- **Handcrafted branch outcomes for Q16–Q50** — all 35 remaining extended quests now have narrative-specific `branch_outcomes` covering `exiled_heir`, `street_ghost`, `wandering_monk`, `nonlethal_path`, `heroic_path`, `rogue_path`, and `default` keys; Q20 also includes `stealth_path` and `kill_path` for tactical override resolution
- Ten new trophies across combat, progression, social, and alignment categories:
  - **Battle Hardened** (combat/early) — 5 lethal kills
  - **War Veteran** (combat/mid) — 20 lethal kills
  - **Rising Ninja** (progression/early) — reach level 5
  - **Seasoned Ninja** (progression/mid) — reach level 10
  - **Loyal Bonds** (social/mid) — build high loyalty with 3 or more allies
  - **Villain Slayer** (progression/late) — defeat every red-bar villain
  - **Questmaster** (progression/late) — complete every seeded quest
  - **Shadow Heir** (progression/late) — clear every region as Exiled Heir
  - **Ghost Sovereign** (progression/late) — clear every region as Street Ghost
  - **Monk Ascendant** (progression/late) — clear every region as Wandering Monk
- Threshold constants for kill milestones, level milestones, and ally loyalty evaluation
- 20 new tests covering Q6 branching and all new trophy unlock conditions
- Extended kill-counter progression output in playthrough summaries, including remaining kills to next trophy milestones
- Two new combat trophies:
  - **Crimson Reaper** (combat/late) — 35 lethal kills
  - **Apex Predator** (combat/late) — 50 lethal kills
- **Six new stance-evolution mastery trophies** (Issue 2):
  - **Pacifier** (social/mid) — drive two or more villains to PASSIVE stance through charm/mercy/diplomacy
  - **Terror** (combat/mid) — drive two or more villains to AGGRESSIVE stance through lethal/betrayal actions
  - **Stance Breaker** (progression/late) — force three or more villains through multiple stance transitions
  - **Shadow Whisperer** (stealth/late) — complete a kill-free run with 10 stealth outcomes
  - **Silver Mask** (social/late) — complete a kill-free run with 10 charm outcomes
  - **Wind Dancer** (stealth/late) — complete a kill-free run with 8 evasion outcomes
- `get_villain_evolution_checkpoints()` now returns `relationship_arc` (dormant/active/rival/nemesis/reformed) and `active_triggers` list per villain checkpoint (Issue 2)
- `generate_playthrough_summary()` now includes (Issue 4):
  - `playstyle_summary` — dominant action, style label (Shadow Operative / Silver Diplomat / Wind Walker / Lethal Shinobi / Mixed Tactician), shift detection note
  - `villain_relationship_arcs` — per-villain arc, phase, and active triggers
  - `trophy_near_miss` — trophies within 3 actions of unlocking, with hints
- `_build_playstyle_summary()` and `_build_trophy_near_miss()` helper methods
- GitHub Actions `track_progress.yml` workflow — auto-labels PRs by changed files and keywords, posts backlog snapshot comment on PR open, marks NEXT_STEPS.md items complete when a relevant PR merges
- Four issue templates under `.github/ISSUE_TEMPLATE/`: gameplay_feature, narrative_quest, balance_pass, testing
- `scripts/setup_github_project.py` — one-time setup script to create labels, milestone v0.2.0, backfilled closed issues for all v0.1.0 work, and open issues for the v0.2.0 backlog
- 31 new targeted tests across four new test classes (Issue 5): `Issue1QuestBranchOutcomesTests`, `Issue2VillainEvolutionTests`, `Issue3BalancePassTests`, `Issue4ReplaySummaryTests`

### Changed

- `apply_status_effects()` now **accumulates** stacks up to the band cap and refreshes duration to the higher value rather than replacing the existing effect (Issue 3 balance pass)
- `apply_player_decision()` now grants incremental reputation deltas per decision type: `charm` +2, `stealth` +1, `evasion` +1, `kill` −1 — making nonlethal playstyles competitively viable for reaching Heroic tier (Issue 3)
- NEXT_STEPS.md updated — all five v0.2.0 items marked complete; v0.3.0 horizon items added

---

## [0.1.0] – 2026-07-28

### Added

- Affinity mini-game and assignment (Fire/Water/Earth/Wind)
- Five move categories: Escape, Attack, Defense, Summon, Ultimate
- Move rule enforcement: non-ultimates are single-affinity; ultimates can mix affinities
- Stats and leveling progression system
- Reputation system with Rogue Ninja path and Black Market unlock
- Weapons: sword, kunai, bow staff, ninja stars with status effects
- Region and boss progression with reward choices (weapon/clothing/move)
- Save/load JSON snapshots for full world + player progression state
- Quest state flow (active/completed/failed) with sequential gating
- Quest chain with stealth-required content
- Seeded allies (Dan, Moon, Sleep, Dot, Porter) plus curated roster with AutoNinja fallback
- Ally loyalty tracking influenced by decisions and quest outcomes
- Region-specific encounter tables for replayable deterministic rotations
- Unlockable skins with stat boosts and fast travel unlocks
- Vault archive for historic ninja runs with replay analytics
- Replay hub report combining active-run summary and archive analytics
- Player backstory selection (exiled_heir, street_ghost, wandering_monk) with narrative impact
- Villain backstories with aggression/passivity shifts driven by player decisions
- Villain-specific decision memory in behavior and summary reporting
- Backstory-driven quest branch outcomes for Q1–Q3
- Expanded balanced shared move pool (12 per category) for reusable combat design
- Villain kit design: one signature move plus skinned shared move loadouts
- Status effects on weapons/jutsu/summons with capped duration and stack bands
- Combat physics output for moves (impact/knockback/stagger window) with blood intensity tracking
- Combo resolution helper with status-affinity synergy bonuses
- Affinity animation preview metadata for startup/travel/hit/recovery beats
- Nonlethal progression tracking via charm, stealth, and evasion outcomes
- Reputation-aware shop inventory and Black Market purchasing
- Trophy catalog with category-based unlock conditions and tiers (early/mid/late)
- Trophies: silent_legend, phantom_veil, harmony_voice, untouchable_ghost, trinity_operator
- Playthrough summary report including backstory, trophies, reputation, and villain stances
- MIT license
- Contributing guidelines and code of conduct
- GitHub Actions CI workflow running unit tests on Python 3.11 and 3.12
