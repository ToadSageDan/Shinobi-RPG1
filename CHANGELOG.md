# Changelog

All notable changes to Shinobi-RPG1 will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Quest Q6 "Legacy of the Fallen Shinobi": final epilogue quest at the Ashen Spire with full backstory, nonlethal, heroic, and rogue branch outcomes
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
