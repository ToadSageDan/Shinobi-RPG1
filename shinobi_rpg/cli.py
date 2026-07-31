"""Interactive CLI game loop for Shinobi RPG.

Run via:
    python -m shinobi_rpg play
or (after pip install -e .):
    shinobi-play
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path
from typing import List

from .core import (
    NinjaWorld,
    PlayerProfile,
    QuestStatus,
    ReputationTier,
    build_mvp_world,
    load_world_snapshot,
    save_world_snapshot,
)

# ── cosmetic helpers ──────────────────────────────────────────────────────────

_DIVIDER = "─" * 60
_THICK   = "═" * 60

AFFINITY_EMOJI = {
    "fire":  "🔥",
    "water": "💧",
    "earth": "🌿",
    "wind":  "💨",
}

APPROACH_EMOJI = {
    "kill":    "⚔️ ",
    "charm":   "🗣️ ",
    "stealth": "🌑 ",
    "evasion": "💨 ",
}


def _print(text: str = "") -> None:
    print(text)


def _header(title: str) -> None:
    _print()
    _print(_THICK)
    _print(f"  {title}")
    _print(_THICK)


def _section(title: str) -> None:
    _print()
    _print(_DIVIDER)
    _print(f"  {title}")
    _print(_DIVIDER)


def _wrap(text: str, indent: int = 4) -> str:
    prefix = " " * indent
    return "\n".join(
        textwrap.fill(line, width=72, initial_indent=prefix, subsequent_indent=prefix)
        for line in text.splitlines()
    )


def _prompt(question: str, choices: List[str] | None = None) -> str:
    """Print a prompt, optionally list numbered choices, and return stripped input."""
    if choices:
        _print()
        for idx, choice in enumerate(choices, 1):
            _print(f"  {idx}. {choice}")
        _print()
    while True:
        try:
            raw = input(f"  {question} > ").strip()
        except (EOFError, KeyboardInterrupt):
            _print("\n  [Interrupted — goodbye, shinobi.]")
            sys.exit(0)
        if raw:
            return raw


def _pick(question: str, choices: List[str]) -> int:
    """Display a numbered menu and return the 0-based chosen index."""
    while True:
        answer = _prompt(question, choices)
        if answer.isdigit():
            idx = int(answer) - 1
            if 0 <= idx < len(choices):
                return idx
        # also allow typing the label directly (case-insensitive prefix match)
        lower = answer.lower()
        matches = [i for i, c in enumerate(choices) if c.lower().startswith(lower)]
        if len(matches) == 1:
            return matches[0]
        _print("  ✗ Invalid choice — enter a number or a unique label prefix.")


def _confirm(question: str) -> bool:
    answer = _prompt(f"{question} [y/n]").lower()
    return answer.startswith("y")


# ── HUD ──────────────────────────────────────────────────────────────────────

def _show_hud(world: NinjaWorld, player: PlayerProfile) -> None:
    env = world.get_environment_state()
    aff_icon = AFFINITY_EMOJI.get(player.affinity.value, "●")
    tier = player.current_reputation_tier().value.upper()
    tier_icon = {"HEROIC": "🏅", "NEUTRAL": "⬜", "ROGUE": "💀"}.get(tier, "")
    xp_needed = player.stats.level * 100
    xp_bar_fill = int((player.stats.xp / xp_needed) * 20) if xp_needed else 0
    xp_bar = "█" * xp_bar_fill + "░" * (20 - xp_bar_fill)

    cleared = sum(1 for r in world.regions if r.cleared)
    active_quest = player.get_active_quest_id()
    quest_title = "—"
    if active_quest:
        quest_obj = next((q for q in world.quests if q.quest_id == active_quest), None)
        if quest_obj:
            quest_title = quest_obj.title

    _print()
    _print(_DIVIDER)
    _print(
        f"  {player.name}  {aff_icon} {player.affinity.value.capitalize()}  "
        f"│  Lv.{player.stats.level}  [{xp_bar}] {player.stats.xp}/{xp_needed} XP"
    )
    _print(
        f"  PWR {player.stats.power}  DEF {player.stats.defense}  "
        f"AGI {player.stats.agility}  FOC {player.stats.focus}  "
        f"│  Credits: {player.credits}"
    )
    _print(
        f"  Reputation: {player.reputation:+d}  ({tier_icon} {tier})  "
        f"│  Regions cleared: {cleared}/{len(world.regions)}"
    )
    _print(f"  Active quest: {quest_title}")
    _print(
        f"  World: {env['time_of_day'].capitalize()} · {env['weather'].capitalize()}"
    )
    _print(_DIVIDER)


# ── Character creation ────────────────────────────────────────────────────────

_AFFINITY_QUESTIONS = [
    (
        "You're crossing a mountain pass in a storm. You:",
        ["Sprint through before it worsens (FIRE)",
         "Find shelter and wait it out (WATER)",
         "Build a windbreak from loose rocks (EARTH)",
         "Read the wind and time a gap (WIND)"],
        ["fire", "water", "earth", "wind"],
    ),
    (
        "A rival blocks your path demanding tribute. You:",
        ["Step forward and make clear you won't pay (FIRE)",
         "Stall with talk until you spot an opening (WATER)",
         "Plant your feet; immovable refusal (EARTH)",
         "Side-step entirely — detour around (WIND)"],
        ["fire", "water", "earth", "wind"],
    ),
    (
        "Your training partner is overwhelmed in a sparring session. You:",
        ["Unleash a decisive finishing combo (FIRE)",
         "Drain their stamina with patient counters (WATER)",
         "Lock them down with grabs and holds (EARTH)",
         "Dance out of reach until they tire (WIND)"],
        ["fire", "water", "earth", "wind"],
    ),
    (
        "A village elder asks your ideal victory. You say:",
        ["Decisive — leave no room for a second round (FIRE)",
         "Adaptive — match the moment, never overcommit (WATER)",
         "Enduring — outlast every obstacle placed before you (EARTH)",
         "Unseen — end it before the enemy knows it began (WIND)"],
        ["fire", "water", "earth", "wind"],
    ),
    (
        "Describe your ideal terrain:",
        ["An open field under a burning noon sun (FIRE)",
         "A river delta at dusk, fog on the water (WATER)",
         "A fortress carved from a cliff face (EARTH)",
         "A high ridge where every step catches the wind (WIND)"],
        ["fire", "water", "earth", "wind"],
    ),
]


def _run_affinity_minigame() -> str:
    """Ask five questions and return the winning affinity string."""
    _header("🔮  AFFINITY TRIAL")
    _print(_wrap(
        "Five questions will reveal your elemental nature. "
        "Choose the answer that feels most like you."
    ))
    scores = {"fire": 0, "water": 0, "earth": 0, "wind": 0}
    for q_text, options, affinity_map in _AFFINITY_QUESTIONS:
        _section(q_text)
        idx = _pick("Your choice", options)
        scores[affinity_map[idx]] += 1

    winner = max(scores, key=lambda k: (scores[k], ["fire", "water", "earth", "wind"].index(k)))
    icon = AFFINITY_EMOJI[winner]
    _print()
    _print(f"  {icon}  Your affinity is revealed: {winner.upper()}")
    return winner


def _pick_backstory(world: NinjaWorld) -> int:
    """Show backstory options and return chosen index."""
    _header("📜  CHOOSE YOUR BACKSTORY")
    backstory_labels = []
    for bs in world.player_backstories:
        bias_str = f"+{bs.reputation_bias}" if bs.reputation_bias >= 0 else str(bs.reputation_bias)
        tags = ", ".join(bs.narrative_tags)
        backstory_labels.append(f"{bs.title}  (rep {bias_str})  [{tags}]")
    return _pick("Choose your origin", backstory_labels)


def _create_character() -> tuple[NinjaWorld, PlayerProfile]:
    _header("⚔️   SHINOBI RPG  —  NEW GAME")
    name = _prompt("Enter your shinobi name")

    # Affinity mini-game
    affinity_str = _run_affinity_minigame()
    affinity_map = {"fire": 1, "water": 2, "earth": 3, "wind": 4}
    # Encode the winning element as a high score in position 0 and low elsewhere.
    # resolve_affinity_minigame sums positionally: highest sum of affinity slots wins.
    decision_scores = [5 if ["fire","water","earth","wind"].index(affinity_str) == i else 1
                       for i in range(4)]

    world, player = build_mvp_world(name, decision_scores)

    # Backstory
    bs_idx = _pick_backstory(world)
    player.choose_backstory(world.player_backstories[bs_idx])
    _print(f"\n  ✓ Backstory chosen: {world.player_backstories[bs_idx].title}")

    return world, player


# ── Save / Load ───────────────────────────────────────────────────────────────

_DEFAULT_SAVE = Path.home() / ".shinobi_rpg" / "save.json"


def _do_save(world: NinjaWorld, player: PlayerProfile) -> None:
    save_world_snapshot(world, player, _DEFAULT_SAVE)
    _print(f"  ✓ Game saved to {_DEFAULT_SAVE}")


def _do_load() -> tuple[NinjaWorld, PlayerProfile] | None:
    if not _DEFAULT_SAVE.exists():
        _print("  ✗ No save file found.")
        return None
    world, player = load_world_snapshot(_DEFAULT_SAVE)
    _print(f"  ✓ Save loaded: {player.name}  Lv.{player.stats.level}")
    return world, player


# ── Encounter ─────────────────────────────────────────────────────────────────

def _do_encounter(world: NinjaWorld, player: PlayerProfile, region_name: str) -> None:
    result = world.resolve_region_encounter(player, region_name)

    _section(f"⚡  ENCOUNTER  —  {region_name}")
    if not result.get("player_survived"):
        _print(f"  ☠  {result['encounter']} drove you out of {region_name}!")
        _print(f"     Recommended level: {result['recommended_level']}  (your level: {result['player_level']})")
        return

    _print(f"  You face: {result['encounter']}")
    env = result["environment"]
    _print(f"  Conditions: {env['time_of_day'].capitalize()} · {env['weather'].capitalize()}")

    approach_choices = [
        f"{APPROACH_EMOJI['kill']}  Attack (kill)",
        f"{APPROACH_EMOJI['charm']}  Charm (talk your way through)",
        f"{APPROACH_EMOJI['stealth']}  Stealth (slip by unseen)",
        f"{APPROACH_EMOJI['evasion']}  Evasion (retreat and evade)",
    ]
    approach_keys = ["kill", "charm", "stealth", "evasion"]
    idx = _pick("How do you handle this?", approach_choices)
    chosen = approach_keys[idx]

    world.apply_player_decision(player, chosen)

    xp = result.get("reward_xp", 0)
    levels = result.get("levels_gained", 0)
    icon = APPROACH_EMOJI.get(chosen, "")
    _print(f"\n  {icon}  Outcome: {chosen.upper()}  (+{xp} XP)")
    if levels:
        _print(f"  ✦ Level up! Now Lv.{player.stats.level}")
    new_move = result.get("enemy_exclusive_move_unlocked")
    if new_move:
        _print(f"  📖 Learned enemy technique: {new_move}")

    # Surface world echoes if any fired
    drift = world.get_world_drift_signals()
    if drift.get("visible") and drift.get("signals"):
        latest = drift["signals"][-1]
        _print(f"\n  🌐 World echo: {latest['label']}")


# ── Quest ─────────────────────────────────────────────────────────────────────

def _show_quest(world: NinjaWorld, player: PlayerProfile) -> None:
    active_id = player.get_active_quest_id()
    if not active_id:
        _print("  No active quest.")
        return
    quest = next((q for q in world.quests if q.quest_id == active_id), None)
    if not quest:
        return

    _section(f"📋  QUEST  [{active_id}]  {quest.title}")
    _print(_wrap(quest.objective))
    if quest.stealth_required:
        _print("\n  ⚠  Stealth required for full branch unlock.")
    if quest.premise:
        _print()
        _print(_wrap(quest.premise))

    _print()
    _print("  Choices:")
    for choice in quest.choices:
        _print(f"    • {choice}")


def _complete_quest(world: NinjaWorld, player: PlayerProfile) -> None:
    active_id = player.get_active_quest_id()
    if not active_id:
        _print("  ✗ No active quest to complete.")
        return

    quest = next((q for q in world.quests if q.quest_id == active_id), None)
    if not quest:
        _print(f"  ✗ Quest {active_id} not found in quest list.")
        return

    _section(f"📋  COMPLETE QUEST  [{active_id}]  {quest.title}")

    approach_opts = ["kill", "charm", "stealth", "evasion"]
    approach_labels = [
        f"{APPROACH_EMOJI['kill']}  Force (kill)",
        f"{APPROACH_EMOJI['charm']}  Diplomacy (charm)",
        f"{APPROACH_EMOJI['stealth']}  Shadow (stealth)",
        f"{APPROACH_EMOJI['evasion']}  Slip away (evasion)",
    ]
    if quest.stealth_required:
        _print("  ⚠  This quest's full nonlethal outcome requires stealth approach.")

    idx = _pick("Choose your approach for this quest", approach_labels)
    approach = approach_opts[idx]
    world.record_quest_resolution(player, active_id, approach=approach)

    result = world.complete_quest(player, active_id)

    branch = world.resolve_quest_branch(player, active_id)
    _print()
    _print(_wrap(branch["outcome"]))
    _print()
    xp = result["reward_xp"]
    levels = result["levels_gained"]
    credits_earned = result["credit_reward"]
    _print(f"  ✓ +{xp} XP  +{credits_earned} credits")
    if levels:
        _print(f"  ✦ Level up! Now Lv.{player.stats.level}")
    if branch.get("reformed_villain_hook"):
        _print(f'\n  💬 {branch["reformed_villain_hook"]}')
    if branch.get("follow_up_hook"):
        _print(f"\n  → {branch['follow_up_hook']}")


# ── Region map ────────────────────────────────────────────────────────────────

def _show_map(world: NinjaWorld, player: PlayerProfile) -> None:
    _section("🗺️   WORLD MAP")
    for region in world.regions:
        status = "✅ CLEARED" if region.cleared else f"Lv.{region.minimum_level}+"
        _print(f"  {region.name:<28} [{status}]  Boss: {region.boss}")
    scheduled = world.dynamic_region_chain
    if scheduled:
        _print(f"\n  ▶  Next recommended region: {scheduled[0]}")


def _explore_region(world: NinjaWorld, player: PlayerProfile) -> None:
    uncleared = [r for r in world.regions if not r.cleared]
    all_regions = world.regions
    region_names = [r.name for r in all_regions]
    status_labels = [
        f"{r.name}  {'(cleared)' if r.cleared else f'Lv.{r.minimum_level}+'}"
        for r in all_regions
    ]
    _section("📍  CHOOSE REGION")
    idx = _pick("Which region?", status_labels)
    region = all_regions[idx]

    _section(f"🌍  {region.name}  —  {region.village_hub}")
    _print(_wrap(f"Climate: {region.climate}"))
    _print(_wrap(f"Terrain: {', '.join(region.terrain_profile)}"))
    _print(_wrap(f"Strategic value: {region.strategic_value}"))
    _print()
    _print("  Points of Interest:")
    for poi in region.points_of_interest:
        _print(f"    • {poi.name}  [{poi.poi_type}]  — {poi.summary}")
    _print()
    _print(f"  Boss: {region.boss}  |  Cleared: {'Yes' if region.cleared else 'No'}")
    _print()

    if region.cleared:
        _print("  This region is already cleared.")
        return

    actions = ["Enter an encounter", "Fight the boss (clear region)", "Back"]
    choice = _pick("What do you do?", actions)
    if choice == 0:
        _do_encounter(world, player, region.name)
    elif choice == 1:
        _fight_boss(world, player, region.name)


def _fight_boss(world: NinjaWorld, player: PlayerProfile, region_name: str) -> None:
    region = next((r for r in world.regions if r.name == region_name), None)
    if not region:
        return

    _section(f"💥  BOSS FIGHT  —  {region.boss}")
    behavior = world.get_region_boss_behavior(region_name, player)
    _print(_wrap(f"Stance: {behavior['stance'].upper()}"))
    _print(_wrap(f"Behavior: {behavior['behavior']}"))

    if not world.boss_availability.get(region.boss, True):
        _print("\n  ✗ This boss is currently unavailable due to world events.")
        return

    _print("\n  Defeat the boss and claim your reward.")
    reward_names = list(region.boss_rewards.keys())
    reward_labels = [
        f"{r.capitalize()}: {region.boss_rewards[r]}"
        for r in reward_names
    ]
    idx = _pick("Choose your victory reward", reward_labels)
    reward_choice = reward_names[idx]

    try:
        reward_name = world.clear_region(player, region_name, reward_choice)
    except ValueError as exc:
        _print(f"\n  ✗ {exc}")
        return

    _print(f"\n  ✦ {region.boss} defeated!")
    _print(f"  🎁 Reward: {reward_name}")
    if reward_choice == "move":
        _print(f"  📖 New move added to your loadout.")
    newly_awarded = list(player.trophies)
    _print(f"  Trophies earned: {len(player.trophies)}")


# ── Shop ──────────────────────────────────────────────────────────────────────

def _show_shop(world: NinjaWorld, player: PlayerProfile) -> None:
    _section(f"🛒  SHOP  —  Credits: {player.credits}")
    items = world.get_shop_inventory(player)
    if not items:
        _print("  No items available for your current standing.")
        return

    item_labels = [f"{item['name']}  ({item['price']} credits)" for item in items]
    item_labels.append("Exit shop")
    idx = _pick("Browse items", item_labels)
    if idx == len(items):
        return

    chosen = items[idx]
    _print(f"\n  {chosen['name']}  —  {chosen['price']} credits")
    if not _confirm("Purchase?"):
        return
    try:
        result = world.purchase_shop_item(player, chosen["key"])
        _print(f"  ✓ Purchased!  Remaining credits: {result['remaining_credits']}")
    except ValueError as exc:
        _print(f"  ✗ {exc}")


# ── Status screens ────────────────────────────────────────────────────────────

def _show_moves(player: PlayerProfile) -> None:
    _section("🥷  MOVE LOADOUT")
    for category, moves in player.moves_by_set.items():
        if moves:
            _print(f"  {category.value.upper()}:")
            for move in moves:
                affs = "/".join(a.value for a in move.affinities)
                fx = ", ".join(e.value for e in move.status_effects) or "—"
                _print(f"    • {move.name:<32} [{affs}]  power: {move.power_scale:.2f}  fx: {fx}")


def _show_allies(player: PlayerProfile) -> None:
    _section("🤝  ALLIES")
    if not player.ally_loyalty:
        _print("  No allies yet.")
        return
    for ally, loyalty in sorted(player.ally_loyalty.items()):
        bar = "♥" * max(0, loyalty) + "♡" * max(0, 10 - loyalty)
        _print(f"  {ally:<20}  loyalty: {loyalty:+3d}  [{bar}]")


def _show_quest_log(world: NinjaWorld, player: PlayerProfile) -> None:
    _section("📜  QUEST LOG")
    if not player.quest_log:
        _print("  No quests recorded yet.")
        return
    for quest in world.quests:
        status = player.quest_log.get(quest.quest_id)
        if not status:
            continue
        icon = {"active": "▶", "completed": "✓", "failed": "✗"}.get(status.value, "?")
        _print(f"  {icon}  [{quest.quest_id}]  {quest.title}")


def _show_trophies(world: NinjaWorld, player: PlayerProfile) -> None:
    _section("🏆  TROPHIES")
    if not player.trophies:
        _print("  No trophies earned yet.")
        return
    for key in sorted(player.trophies):
        trophy = world.trophy_catalog.get(key)
        if trophy:
            _print(f"  ✦  {trophy.name:<38} [{trophy.category.value}  {trophy.tier.value}]")
    near = world._build_trophy_near_miss(player)
    if near:
        _print()
        _print("  Near misses:")
        for item in near:
            _print(f"    → {item['name']}  — {item['remaining']} more {item['hint']}")


# ── Main menu loop ────────────────────────────────────────────────────────────

_MAIN_MENU = [
    "Explore a region (encounter or boss)",
    "View active quest",
    "Complete active quest",
    "View world map",
    "View move loadout",
    "View allies",
    "View quest log",
    "View trophies",
    "Visit shop",
    "Save game",
    "Quit",
]


def _main_loop(world: NinjaWorld, player: PlayerProfile) -> None:
    _header(f"⚔️   Welcome, {player.name}  —  Shinobi RPG")
    _print(_wrap(
        "The Quiet Steel Confederacy holds its peace by a thread. "
        "Your choices will shape who survives the next storm."
    ))

    while True:
        _show_hud(world, player)
        choice = _pick("What will you do?", _MAIN_MENU)

        if choice == 0:
            _explore_region(world, player)
        elif choice == 1:
            _show_quest(world, player)
        elif choice == 2:
            _complete_quest(world, player)
        elif choice == 3:
            _show_map(world, player)
        elif choice == 4:
            _show_moves(player)
        elif choice == 5:
            _show_allies(player)
        elif choice == 6:
            _show_quest_log(world, player)
        elif choice == 7:
            _show_trophies(world, player)
        elif choice == 8:
            _show_shop(world, player)
        elif choice == 9:
            _do_save(world, player)
        elif choice == 10:
            if _confirm("Quit Shinobi RPG?"):
                if _confirm("Save before quitting?"):
                    _do_save(world, player)
                _print("\n  Until next time, shinobi.\n")
                break


# ── Entry points ──────────────────────────────────────────────────────────────

def main() -> int:
    _header("⚔️   SHINOBI RPG")

    saved = _DEFAULT_SAVE
    if saved.exists():
        _print(f"\n  Save file found: {saved}")
        if _confirm("Load existing save?"):
            result = _do_load()
            if result:
                world, player = result
                _main_loop(world, player)
                return 0
            _print("  Save failed to load — starting new game.")

    world, player = _create_character()
    _main_loop(world, player)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
