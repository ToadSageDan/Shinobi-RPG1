# Ordered Implementation Backlog - Next Steps

This list is intentionally ordered and should be worked top-to-bottom.
Items marked `[x]` are complete and correspond to closed GitHub Issues.

## v0.2.0 — In Progress

- [x] 1) Complete quest branch outcomes for all remaining seeded quests so backstory, nonlethal, and reputation choices consistently affect outcomes. *(Q16–Q50 handcrafted — done)*
- [x] 2) Expand villain stance evolution triggers and add additional trophy conditions tied to stealth/charm/nonlethal mastery. *(6 new trophies + relationship_arc/active_triggers — done)*
- [x] 3) Run a focused balance pass for status-effect stacking, signature moves, and nonlethal viability across playstyles. *(stack accumulation fix + nonlethal rep gains — done)*
- [x] 4) Improve replay/snapshot summary fidelity so playstyle shifts, villain relationship arcs, and trophy near-miss context are clearer. *(playstyle_summary + villain_relationship_arcs + trophy_near_miss — done)*
- [x] 5) Add targeted automated tests for branch outcomes, stance deltas, nonlethal paths, and trophy unlock edge cases. *(31 new tests, 160 total — done)*

## v0.3.0 — Next Horizon (after systems stabilize)

- [x] 6) Implement stealth quest gating enforcement — Q3, Q5, Q10 require `stealth_required=True` outcomes to unlock nonlethal victory conditions in-engine. *(persisted quest-resolution state + explicit approach tracking — done)*
- [x] 7) Add arc-transition summary events — when the world crosses an arc boundary (opening → escalation → apex), emit a narrative summary event to the vault and tapestry. *(transition history now logged in world events, tapestry, and summaries — done)*
- [x] 8) Expand the Black Market shop inventory — add at least 5 new items gated behind reputation tiers and quest completions. *(5 new quest-gated Black Market items — done)*
- [x] 9) Add villain "reformed" dialogue hooks — when a villain reaches `relationship_arc == "reformed"`, surface a unique narrative line in quest branch outcomes. *(quest outcome hooks added for key villain-facing quests — done)*
- [x] 10) Expand villain backstories, power origins, and arc tie-ins — each villain now carries a full narrative backstory, a `power_origin` explaining how their signature technique emerged from their history, `arc_ties` linking them to story arcs, and `player_backstory_hooks` for all three player backstory paths plus nonlethal/rogue/heroic paths. Exposed via `get_villain_backstory_profile()` and `generate_playthrough_summary`. *(26 new tests, 203 total — done)*

## v0.4.0 — UI Pass + Boss Cinematic Layer *(current)*

- [x] 11) Add boss cinematic intro and dialogue engine (`cutscenes.py`) — each of the 5 main bosses
  has a multi-beat environmental intro, a personality-driven opening monologue, 3 player dialogue
  choices that shift villain stance, and approach-specific defeat scenes (kill/charm/stealth/evasion).
  Player inputs drive the "create your own story" arc. *(28 new tests, 253 total — done)*
- [x] 12) Upgrade CLI HUD — added HP/Chakra/Stamina visual bars derived from stats, active
  status-effects row with icons and stack counts, and a denser layout matching the Mock A/B designs
  from the README. *(done)*
- [x] 13) Wire cutscene engine into `_fight_boss()` — boss fight now runs the full cinematic intro
  before combat, applies stance delta from player dialogue, injects backstory hook and reformed-arc
  lines, shows a taunt mid-fight, asks for approach choice (kill/charm/stealth/evasion), and plays
  the approach-specific defeat scene. *(done)*
- [x] 14) Add four new main-menu screens — **Villain Intel** (arc checkpoints + stance status),
  **Playthrough Summary** (playstyle, arcs, trophies), **Fast Travel** (unlocked node navigation),
  **Vault History** (active run + archive analytics). *(done)*



- Current power scope to animate is managed by reusable shared move pools plus selective signature powers.
- Keep adding powers in a measured way only when they support gameplay depth, not just raw move count.

## v0.5.0 — Godot 4 Real-Time Client *(current)*

- [x] 15) Initialize Godot 4 project under `godot_client/` with Forward Plus renderer,
  SDFGI global illumination, volumetric fog, bloom, and SSAO enabled per biome.
- [x] 16) Implement `PlayerCharacter` (`CharacterBody3D`) with wall-run (raycast detection),
  double-jump, dash (i-frames), dodge (i-frames), combo input buffer, and
  third-person lock-on camera (`SpringArm3D` with orbit-toward-target). *(Player.gd, PlayerCamera.gd)*
- [x] 17) Implement `CombatManager` singleton — real-time HP tracking for player and all
  active enemies, affinity damage matrix (16-entry fire/water/earth/wind cross-table),
  combo bonus detection, status-effect tick damage (burn 8 DPS, bleed 6 DPS, fear 4 DPS),
  enemy stagger system, and all signals consumed by the HUD. *(CombatManager.gd)*
- [x] 18) Implement enemy AI state machine (IDLE → PATROL → DETECT → CHASE → ATTACK →
  STAGGERED → RECOVER → DEAD) and boss AI with phase-2 transition, signature-move
  cooldown (8 s), per-phase power bonus, and cinematic taunt. *(Enemy.gd, Boss.gd)*
- [x] 19) Implement `Hitbox` / `JutsuProjectile` — area-based melee collision and
  charge-scaled jutsu projectiles with AoE / straight-line routing, affinity hit SFX,
  and learnable enemy move unlock on defeat. *(Hitbox.gd, JutsuProjectile.gd)*
- [x] 20) Create all five arena scenes with per-biome `WorldEnvironment` (forest, volcanic,
  coastal, alpine, cave), enemy spawn points, player spawn, HUD, and GameOver overlay.
  *(VerdantGate / AshenCradle / Tideglass / StormwallRidge / SunkenHollow .tscn)*
- [x] 21) Implement `InputBuffer` singleton — 0.45 s window combo detection for
  triple-slash, launcher, evade-counter, dash-slam, and charged jutsu sequences.
- [x] 22) Implement full UI layer — `HUD.gd` (HP/Chakra/Stamina bars with status icons,
  enemy HP bars, combo popups, boss phase banner, hit flash vignette), `GameOver.gd`
  (run stats + retry/load/menu), `MainMenu`, `CharacterCreation`, `WorldMap`. *(scenes/ui/)*
- [x] 23) Write three shaders — `cel_shading.gdshader` (anime diffuse_toon + rim light +
  affinity tint), `chakra_glow.gdshader` (pulsing fill bar), `damage_vignette.gdshader`
  (screen-edge red flash + chromatic aberration on hit). *(resources/shaders/)*
- [x] 24) Write `export_world.py` Python bridge — exports all 5 regions, 50 quests,
  17 villains, 68 moves, 10 allies to `godot_client/data/world_data.json`.
  `WorldData.gd` autoload reads and serves data; full hardcoded fallback included.
- [x] 25) Add `ASSETS_GUIDE.md` covering Mixamo characters, Kenney.nl environments,
  freesound audio, cel-shader application, and minimum-viable art-pass instructions.

## v0.6.0 — Art Pass + Polish *(current)*

- [x] 26) Import Mixamo character rig + animations for player and at least one enemy type.
  *(`PlaceholderRig.gd` procedural mesh rig; Player.tscn + Enemy.tscn updated to include it.
  Drop in Mixamo FBX + AnimationPlayer to replace — see ASSETS_GUIDE.md for steps. — done)*
- [x] 27) Replace placeholder terrain meshes with biome-specific environment assets.
  *(`BiomeTerrain.gd` procedural terrain called from BaseArena: coloured ground, boundary walls,
  and scatter objects for all 5 biomes. Replace with real meshes when available. — done)*
- [x] 28) Add `GPUParticles3D` VFX for each affinity jutsu (fire trail, water splash, etc.).
  *(`AffinityVFX.gd` — per-affinity gradient, shape, gravity, velocity presets; auto-configured
  on `JutsuProjectile.launch()` + impact burst on hit. — done)*
- [x] 29) Wire AudioManager with real music tracks and SFX clips.
  *(`AudioManifest.gd` autoload — registers all music/SFX paths, gracefully skips missing files,
  logs free-source hints. Add .ogg/.wav to `res://assets/audio/` to enable audio. — done)*
- [x] 30) Add quest waypoints in-world (world-space markers showing active quest region).
  *(`QuestWaypoint.gd` + `QuestWaypoint.tscn` — spinning diamond + beacon beam + Label3D;
  `BaseArena._spawn_quest_waypoints()` places one per active quest in the region. — done)*
- [x] 31) Implement Shop and Playthrough Summary UI scenes.
  *(`Shop.gd` + `Shop.tscn` — rep-gated item list + detail panel + purchase flow with credits deduction.
  `PlaythroughSummary.gd` + `PlaythroughSummary.tscn` — tabbed screen: Overview / Trophies /
  Villains / Quests. Both scenes linked from WorldMap buttons. — done)*
- [x] 32) Add controller/gamepad remapping screen under Options.
  *(`Options.gd` + `Options.tscn` — full keyboard + gamepad remap table for all 15 actions,
  Audio sliders, Fullscreen toggle, settings persisted to `user://options.cfg`.
  MainMenu Options button now navigates to this screen. — done)*

## Project board

Create issues for items 6–10 by running:
```bash
export GITHUB_TOKEN=<your-PAT>
python scripts/setup_github_project.py
```
See `scripts/setup_github_project.py` for full setup instructions.
