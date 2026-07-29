# Ordered Implementation Backlog - Next Steps

This list is intentionally ordered and should be worked top-to-bottom.

- [ ] 1) Complete quest branch outcomes for all remaining seeded quests so backstory, nonlethal, and reputation choices consistently affect outcomes.
- [ ] 2) Expand villain stance evolution triggers and add additional trophy conditions tied to stealth/charm/nonlethal mastery.
- [ ] 3) Run a focused balance pass for status-effect stacking, signature moves, and nonlethal viability across playstyles.
- [ ] 4) Improve replay/snapshot summary fidelity so playstyle shifts, villain relationship arcs, and trophy near-miss context are clearer.
- [ ] 5) Add targeted automated tests for branch outcomes, stance deltas, nonlethal paths, and trophy unlock edge cases.

## Scope guard for animation realism

- Current power scope to animate is managed by reusable shared move pools plus selective signature powers.
- Keep adding powers in a measured way only when they support gameplay depth, not just raw move count.

## Later-phase milestone (after systems stabilize)

- Define the implementation plan for character models, animation pipeline, and physics architecture after gameplay systems are more locked.
