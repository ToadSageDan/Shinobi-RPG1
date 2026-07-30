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

- [ ] 6) Implement stealth quest gating enforcement — Q3, Q5, Q10 require `stealth_required=True` outcomes to unlock nonlethal victory conditions in-engine.
- [ ] 7) Add arc-transition summary events — when the world crosses an arc boundary (opening → escalation → apex), emit a narrative summary event to the vault and tapestry.
- [ ] 8) Expand the Black Market shop inventory — add at least 5 new items gated behind reputation tiers and quest completions.
- [ ] 9) Add villain "reformed" dialogue hooks — when a villain reaches `relationship_arc == "reformed"`, surface a unique narrative line in quest branch outcomes.
- [ ] 10) Define the implementation plan for character models, animation pipeline, and physics architecture after gameplay systems are more locked.

## Scope guard for animation realism

- Current power scope to animate is managed by reusable shared move pools plus selective signature powers.
- Keep adding powers in a measured way only when they support gameplay depth, not just raw move count.

## Project board

Create issues for items 6–10 by running:
```bash
export GITHUB_TOKEN=<your-PAT>
python scripts/setup_github_project.py
```
See `scripts/setup_github_project.py` for full setup instructions.

