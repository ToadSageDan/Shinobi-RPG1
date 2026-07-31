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

## Project board

Create issues for items 6–10 by running:
```bash
export GITHUB_TOKEN=<your-PAT>
python scripts/setup_github_project.py
```
See `scripts/setup_github_project.py` for full setup instructions.
