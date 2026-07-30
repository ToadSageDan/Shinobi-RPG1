#!/usr/bin/env python3
"""
setup_github_project.py
=======================
One-time setup script that creates the full GitHub project infrastructure
for Shinobi-RPG1:

  - Labels (gameplay, balance, testing, narrative, enhancement, bug)
  - Milestone v0.2.0
  - Closed/backfilled issues for all completed v0.1.0 work
  - Open issues for the current NEXT_STEPS backlog
  - (Optional) Links all issues to a GitHub Project board if PROJECT_ID is set

Usage
-----
    export GITHUB_TOKEN=<your-PAT-with-repo+project-scopes>
    export GITHUB_REPO=ToadSageDan/Shinobi-RPG1   # default
    export PROJECT_ID=<numeric-project-id>          # optional
    python scripts/setup_github_project.py

Requirements
------------
    pip install requests
"""

import os
import sys
import time
import json
import requests

REPO = os.environ.get("GITHUB_REPO", "ToadSageDan/Shinobi-RPG1")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
PROJECT_ID = os.environ.get("PROJECT_ID", "")

API = "https://api.github.com"
HEADERS = {
    "Authorization": f"******",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def _req(method: str, path: str, **kwargs) -> requests.Response:
    url = f"{API}{path}" if path.startswith("/") else path
    resp = getattr(requests, method)(url, headers=HEADERS, **kwargs)
    if resp.status_code == 422:
        data = resp.json()
        if any("already_exists" in str(e) for e in data.get("errors", [])):
            return resp  # silently skip duplicate
    resp.raise_for_status()
    time.sleep(0.5)  # respect rate limits
    return resp


def create_label(name: str, color: str, description: str) -> None:
    _req("post", f"/repos/{REPO}/labels", json={
        "name": name, "color": color, "description": description,
    })
    print(f"  label: {name}")


def create_milestone(title: str, description: str, due_on: str) -> int:
    resp = _req("post", f"/repos/{REPO}/milestones", json={
        "title": title, "description": description, "due_on": due_on,
    })
    if resp.status_code == 422:
        # Already exists — look it up
        existing = _req("get", f"/repos/{REPO}/milestones").json()
        for m in existing:
            if m["title"] == title:
                print(f"  milestone already exists: {title} (#{m['number']})")
                return m["number"]
    ms = resp.json()
    print(f"  milestone: {title} (#{ms['number']})")
    return ms["number"]


def create_issue(
    title: str,
    body: str,
    labels: list[str],
    milestone: int | None = None,
    state: str = "open",
) -> int:
    payload: dict = {"title": title, "body": body, "labels": labels}
    if milestone:
        payload["milestone"] = milestone
    resp = _req("post", f"/repos/{REPO}/issues", json=payload)
    issue = resp.json()
    number = issue["number"]
    print(f"  issue #{number}: {title}")
    if state == "closed":
        _req("patch", f"/repos/{REPO}/issues/{number}", json={"state": "closed"})
        print(f"    → closed (backfilled)")
    return number


def add_issue_to_project(issue_node_id: str, project_id: str) -> None:
    """Add an issue to a GitHub Project (v2) using GraphQL."""
    query = """
    mutation($project: ID!, $item: ID!) {
      addProjectV2ItemById(input: {projectId: $project, contentId: $item}) {
        item { id }
      }
    }
    """
    resp = requests.post(
        "https://api.github.com/graphql",
        headers=HEADERS,
        json={"query": query, "variables": {"project": project_id, "item": issue_node_id}},
    )
    resp.raise_for_status()
    print(f"    → added to project board")


def get_issue_node_id(issue_number: int) -> str:
    resp = _req("get", f"/repos/{REPO}/issues/{issue_number}")
    return resp.json().get("node_id", "")


def main() -> None:
    if not TOKEN:
        print("ERROR: Set GITHUB_TOKEN env var to a PAT with repo + project scopes.")
        sys.exit(1)

    owner, repo_name = REPO.split("/")
    print(f"\n=== Setting up GitHub project infrastructure for {REPO} ===\n")

    # ── Labels ──────────────────────────────────────────────────────────────
    print("Creating labels…")
    create_label("gameplay",    "0075ca", "Gameplay systems, quests, and combat logic")
    create_label("balance",     "e4e669", "Balance pass: status effects, moves, viability")
    create_label("testing",     "d93f0b", "Automated tests and test coverage")
    create_label("narrative",   "c5def5", "Quests, backstories, and villain arcs")
    create_label("enhancement", "a2eeef", "New feature or improvement")
    create_label("bug",         "d73a4a", "Something is not working correctly")

    # ── Milestone v0.2.0 ────────────────────────────────────────────────────
    print("\nCreating milestone v0.2.0…")
    milestone_number = create_milestone(
        "v0.2.0",
        "Second feature milestone: quest branch completion, villain evolution, "
        "balance pass, replay fidelity, and expanded test coverage.",
        "2026-09-30T00:00:00Z",
    )

    issue_numbers: list[int] = []

    # ── Backfilled v0.1.0 closed issues ─────────────────────────────────────
    print("\nBackfilling completed v0.1.0 work as closed issues…")
    v010_completed = [
        ("Affinity mini-game and assignment system",
         "Implement the affinity mini-game (Fire/Water/Earth/Wind) and player assignment flow.",
         ["gameplay", "enhancement"]),
        ("Five move categories with affinity rule enforcement",
         "Add Escape/Attack/Defense/Summon/Ultimate move sets with single-affinity enforcement "
         "for non-ultimate moves.",
         ["gameplay", "enhancement"]),
        ("Stats, leveling, and reputation system",
         "Implement stat/level progression, reputation tracking, Rogue Ninja path, and Black Market unlock.",
         ["gameplay", "enhancement"]),
        ("Weapons and region/boss progression",
         "Add sword/kunai/bow-staff/ninja-stars weapons, region unlock gating, boss encounters, "
         "and reward choices (weapon/clothing/move).",
         ["gameplay", "enhancement"]),
        ("Save/load JSON snapshots",
         "Implement full-world + player snapshot serialization and deserialization.",
         ["gameplay", "enhancement"]),
        ("Quest system: Q1–Q15 with branching outcomes",
         "Implement quest state flow (active/completed/failed), stealth-required quests, "
         "and backstory/nonlethal/heroic/rogue branch outcomes for Q1–Q15.",
         ["gameplay", "narrative", "enhancement"]),
        ("Ally system and loyalty tracking",
         "Seed Dan/Moon/Sleep/Dot/Porter allies, add auto-generation to 10+, "
         "and implement loyalty changes from player decisions.",
         ["gameplay", "enhancement"]),
        ("Villain backstories and stance evolution",
         "Add villain backstories, aggression/passivity tracking from player decisions, "
         "and villain-specific decision memory.",
         ["narrative", "gameplay", "enhancement"]),
        ("Trophy catalog and nonlethal path tracking",
         "Add trophy catalog (30+ trophies), tier system, and nonlethal progression "
         "tracking via charm/stealth/evasion outcomes.",
         ["gameplay", "enhancement"]),
        ("Vault archive and replay analytics",
         "Implement vault archive for historic runs, replay hub report, "
         "living tapestry delta, and run-signature preview.",
         ["gameplay", "enhancement"]),
        ("NPC evil-threshold evolution and intel event systems",
         "Add NPC evil-tier evolution based on configurable thresholds and "
         "an intel event system that affects NPC states.",
         ["gameplay", "enhancement"]),
        ("Quest branch outcomes: Q16–Q50 handcrafted",
         "Replace template-generated branch outcomes for Q16–Q50 with "
         "handcrafted narrative text specific to each quest's scenario.",
         ["narrative", "gameplay", "enhancement"]),
    ]
    for title, body, labels in v010_completed:
        n = create_issue(title, body, labels, state="closed")
        issue_numbers.append(n)

    # ── Open v0.2.0 issues ───────────────────────────────────────────────────
    print("\nCreating open v0.2.0 backlog issues…")
    v020_open = [
        (
            "Expand villain stance evolution triggers and mastery trophies",
            """## Summary
Add richer villain evolution checkpoints that track `relationship_arc` and `active_triggers`.

## Acceptance criteria
- [ ] `get_villain_evolution_checkpoints()` returns `relationship_arc` (dormant/active/rival/nemesis/reformed) and `active_triggers` list per villain
- [ ] Six new mastery trophies in catalog: `pacifier`, `terror`, `stance_breaker`, `shadow_whisperer`, `silver_mask`, `wind_dancer`
- [ ] Trophy unlock logic wired and tested
- [ ] All new tests passing

**Backlog item**: NEXT_STEPS #2
""",
            ["gameplay", "narrative", "enhancement"],
        ),
        (
            "Balance pass: status-effect stacking, nonlethal viability, signature moves",
            """## Summary
Fix status-effect stacking (accumulate stacks, don't replace) and ensure nonlethal playstyles
earn reputation gains comparable to lethal playstyles.

## Acceptance criteria
- [ ] `apply_status_effects()` accumulates stacks up to band cap (not replace)
- [ ] Duration refreshes to the higher value on re-application
- [ ] `charm` decisions grant `+2` reputation per action
- [ ] `stealth` and `evasion` decisions grant `+1` reputation per action
- [ ] `kill` decisions cost `-1` reputation per action
- [ ] Nonlethal path can reach Heroic tier without kills
- [ ] All balance tests passing

**Backlog item**: NEXT_STEPS #3
""",
            ["balance", "gameplay", "enhancement"],
        ),
        (
            "Improve replay/snapshot summary fidelity",
            """## Summary
Enrich `generate_playthrough_summary()` with playstyle shift detection, villain relationship arcs,
and near-miss trophy hints.

## Acceptance criteria
- [ ] `playstyle_summary` key in summary with `style_label`, `nonlethal_total`, `lethal_total`, `playstyle_shift_note`
- [ ] `villain_relationship_arcs` key per villain with `arc`, `phase`, `active_triggers`
- [ ] `trophy_near_miss` list of trophies within 3 actions of unlock
- [ ] Vault snapshot roundtrip preserves new summary fields
- [ ] All summary fidelity tests passing

**Backlog item**: NEXT_STEPS #4
""",
            ["gameplay", "enhancement"],
        ),
        (
            "Add targeted automated tests: branch outcomes, stance deltas, nonlethal paths, trophy edge cases",
            """## Summary
Expand test coverage to cover handcrafted quest branches (Issue 1), villain evolution (Issue 2),
balance constants (Issue 3), and replay summary fidelity (Issue 4).

## Acceptance criteria
- [ ] Tests for Q16–Q50 branch outcome completeness and backstory override behaviour
- [ ] Tests for all six new mastery trophies
- [ ] Tests for status-effect stacking accumulation and cap
- [ ] Tests for nonlethal reputation gain and Heroic tier reachability
- [ ] Tests for `playstyle_summary`, `villain_relationship_arcs`, `trophy_near_miss`
- [ ] Vault snapshot roundtrip test
- [ ] Total test count ≥ 155 (was 129)

**Backlog item**: NEXT_STEPS #5
""",
            ["testing", "enhancement"],
        ),
    ]
    for title, body, labels in v020_open:
        n = create_issue(title, body, labels, milestone=milestone_number)
        issue_numbers.append(n)

    # ── Link to project board (optional) ────────────────────────────────────
    if PROJECT_ID:
        print(f"\nLinking issues to project board {PROJECT_ID}…")
        for number in issue_numbers:
            node_id = get_issue_node_id(number)
            if node_id:
                add_issue_to_project(node_id, PROJECT_ID)
    else:
        print(
            "\nSkipping project board linking (set PROJECT_ID env var to link issues).\n"
            "To get your project ID, open your project board URL:\n"
            "  https://github.com/users/ToadSageDan/projects/<number>\n"
            "Then run: gh project view <number> --owner ToadSageDan --format json | jq .id"
        )

    print(f"\n✅  Done. Created {len(issue_numbers)} issues.")
    print(f"    Open issues are assigned to milestone v0.2.0 (#{milestone_number}).")
    print(f"    Closed issues represent completed v0.1.0 backfill.")


if __name__ == "__main__":
    main()
