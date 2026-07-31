## PlaythroughSummary.gd — Full run overview screen.
## Shows playstyle label, villain relationship arcs, trophy progress,
## backstory, and encounter outcome breakdown. Driven entirely from GameState.
extends Control

@onready var title_label:    Label         = $HeaderPanel/HBox/TitleLabel
@onready var player_label:   Label         = $HeaderPanel/HBox/PlayerLabel
@onready var tab_bar:        HBoxContainer = $TabBar
@onready var content_scroll: ScrollContainer = $ContentScroll
@onready var content_label:  RichTextLabel = $ContentScroll/ContentLabel
@onready var back_btn:       Button        = $BackButton

var _active_tab: String = "overview"

const TABS := ["overview", "trophies", "villains", "quests"]

func _ready() -> void:
	title_label.text  = "📊  Playthrough Summary"
	player_label.text = "%s  ·  Lv.%d" % [GameState.player_name, GameState.level]
	back_btn.pressed.connect(_on_back)
	_build_tabs()
	_show_tab("overview")

# ── Tab bar ───────────────────────────────────────────────────────────────────

func _build_tabs() -> void:
	for child in tab_bar.get_children():
		child.queue_free()
	var labels := {"overview": "📋 Overview", "trophies": "🏆 Trophies", "villains": "👁 Villains", "quests": "📜 Quests"}
	for tab_key in TABS:
		var btn := Button.new()
		btn.text = labels.get(tab_key, tab_key)
		btn.custom_minimum_size = Vector2(160, 40)
		btn.toggle_mode = true
		btn.button_pressed = (tab_key == _active_tab)
		btn.pressed.connect(_show_tab.bind(tab_key))
		tab_bar.add_child(btn)

func _show_tab(tab: String) -> void:
	_active_tab = tab
	# Update button pressed states
	var i := 0
	for child in tab_bar.get_children():
		if child is Button:
			child.button_pressed = (TABS[i] == tab)
			i += 1
	match tab:
		"overview":  content_label.text = _build_overview()
		"trophies":  content_label.text = _build_trophies()
		"villains":  content_label.text = _build_villains()
		"quests":    content_label.text = _build_quests()

# ── Overview tab ──────────────────────────────────────────────────────────────

func _build_overview() -> String:
	var o := GameState.encounter_outcomes
	var total := int(o.get("kill", 0)) + int(o.get("charm", 0)) + int(o.get("stealth", 0)) + int(o.get("evasion", 0))
	var nl := int(o.get("charm", 0)) + int(o.get("stealth", 0)) + int(o.get("evasion", 0))
	var style := _playstyle_label(o)
	var tier  := GameState.reputation_tier().to_upper()
	var regions_done := GameState.cleared_regions.size()

	var lines := PackedStringArray()
	lines.append("[b]Character[/b]")
	lines.append("  Name:      %s" % GameState.player_name)
	lines.append("  Backstory: %s" % _backstory_display(GameState.backstory_key))
	lines.append("  Affinity:  %s" % GameState.affinity.capitalize())
	lines.append("  Level:     %d   (XP: %d)" % [GameState.level, GameState.xp])
	lines.append("")
	lines.append("[b]Standing[/b]")
	lines.append("  Reputation:   %+d  [%s]" % [GameState.reputation, tier])
	lines.append("  Credits:      %d" % GameState.credits)
	lines.append("  Regions cleared: %d / 5" % regions_done)
	lines.append("")
	lines.append("[b]Playstyle — %s[/b]" % style)
	lines.append("  Total encounters: %d" % total)
	lines.append("  Lethal (kill):    %d" % int(o.get("kill", 0)))
	lines.append("  Nonlethal total:  %d  (charm %d · stealth %d · evasion %d)" % [
		nl, int(o.get("charm", 0)), int(o.get("stealth", 0)), int(o.get("evasion", 0))
	])
	if total > 0:
		var nl_pct := int(float(nl) / float(total) * 100.0)
		lines.append("  Nonlethal rate:   %d%%" % nl_pct)
	lines.append("")
	lines.append("[b]Unlocked Moves[/b]  (%d total)" % GameState.unlocked_moves.size())
	for m in GameState.unlocked_moves:
		lines.append("  · %s  [%s]" % [m.get("name", "—"), str(m.get("affinities", []))])
	return "\n".join(lines)

func _backstory_display(key: String) -> String:
	match key:
		"exiled_heir":    return "Exiled Heir"
		"street_ghost":   return "Street Ghost"
		"wandering_monk": return "Wandering Monk"
		_:                return key.capitalize() if not key.is_empty() else "Unknown"

func _playstyle_label(o: Dictionary) -> String:
	var kills    := int(o.get("kill", 0))
	var charms   := int(o.get("charm", 0))
	var stealths := int(o.get("stealth", 0))
	var evasions := int(o.get("evasion", 0))
	var total    := kills + charms + stealths + evasions
	if total == 0:
		return "Unproven"
	if charms > stealths and charms > evasions and charms > kills:
		return "Silver Diplomat"
	if stealths > charms and stealths > evasions and stealths > kills:
		return "Shadow Operative"
	if evasions > charms and evasions > stealths and evasions > kills:
		return "Wind Walker"
	if kills > total - kills:
		return "Lethal Shinobi"
	return "Mixed Tactician"

# ── Trophies tab ──────────────────────────────────────────────────────────────

func _build_trophies() -> String:
	var unlocked := GameState.trophies
	var all_trophies := _all_trophy_catalog()
	var lines := PackedStringArray()
	lines.append("[b]Trophies — %d / %d[/b]" % [unlocked.size(), all_trophies.size()])
	lines.append("")
	var tiers := ["early", "mid", "late"]
	for tier_name in tiers:
		lines.append("[b]%s game[/b]" % tier_name.capitalize())
		for t in all_trophies:
			if t.get("tier") != tier_name:
				continue
			var owned := t.get("key") in unlocked
			var icon  := "✅" if owned else "○"
			lines.append("  %s  %s  — %s" % [icon, t.get("name", ""), t.get("description", "")])
		lines.append("")
	return "\n".join(lines)

func _all_trophy_catalog() -> Array[Dictionary]:
	return [
		{"key": "silent_legend",     "name": "Silent Legend",     "tier": "late",  "description": "Complete the game without a single kill."},
		{"key": "phantom_veil",      "name": "Phantom Veil",      "tier": "mid",   "description": "Complete 5 missions via stealth only."},
		{"key": "harmony_voice",     "name": "Harmony Voice",     "tier": "mid",   "description": "Charm 10 enemies into backing down."},
		{"key": "untouchable_ghost", "name": "Untouchable Ghost", "tier": "late",  "description": "Finish a boss fight without taking damage."},
		{"key": "trinity_operator",  "name": "Trinity Operator",  "tier": "late",  "description": "Use kill, charm, and stealth in a single run."},
		{"key": "battle_hardened",   "name": "Battle Hardened",   "tier": "early", "description": "5 lethal kills."},
		{"key": "war_veteran",       "name": "War Veteran",       "tier": "mid",   "description": "20 lethal kills."},
		{"key": "crimson_reaper",    "name": "Crimson Reaper",    "tier": "late",  "description": "35 lethal kills."},
		{"key": "apex_predator",     "name": "Apex Predator",     "tier": "late",  "description": "50 lethal kills."},
		{"key": "rising_ninja",      "name": "Rising Ninja",      "tier": "early", "description": "Reach level 5."},
		{"key": "seasoned_ninja",    "name": "Seasoned Ninja",    "tier": "mid",   "description": "Reach level 10."},
		{"key": "loyal_bonds",       "name": "Loyal Bonds",       "tier": "mid",   "description": "Build high loyalty with 3 or more allies."},
		{"key": "villain_slayer",    "name": "Villain Slayer",    "tier": "late",  "description": "Defeat every red-bar villain."},
		{"key": "questmaster",       "name": "Questmaster",       "tier": "late",  "description": "Complete every seeded quest."},
		{"key": "shadow_heir",       "name": "Shadow Heir",       "tier": "late",  "description": "Clear every region as Exiled Heir."},
		{"key": "ghost_sovereign",   "name": "Ghost Sovereign",   "tier": "late",  "description": "Clear every region as Street Ghost."},
		{"key": "monk_ascendant",    "name": "Monk Ascendant",    "tier": "late",  "description": "Clear every region as Wandering Monk."},
		{"key": "pacifier",          "name": "Pacifier",          "tier": "mid",   "description": "Drive 2+ villains to PASSIVE stance via diplomacy."},
		{"key": "terror",            "name": "Terror",            "tier": "mid",   "description": "Drive 2+ villains to AGGRESSIVE stance via lethal actions."},
		{"key": "stance_breaker",    "name": "Stance Breaker",    "tier": "late",  "description": "Force 3+ villains through multiple stance transitions."},
		{"key": "shadow_whisperer",  "name": "Shadow Whisperer",  "tier": "late",  "description": "Complete a kill-free run with 10 stealth outcomes."},
		{"key": "silver_mask",       "name": "Silver Mask",       "tier": "late",  "description": "Complete a kill-free run with 10 charm outcomes."},
		{"key": "wind_dancer",       "name": "Wind Dancer",       "tier": "late",  "description": "Complete a kill-free run with 8 evasion outcomes."},
	]

# ── Villains tab ──────────────────────────────────────────────────────────────

func _build_villains() -> String:
	var lines := PackedStringArray()
	lines.append("[b]Villain Relationship Arcs[/b]")
	lines.append("")
	# WorldData holds villain profiles; we display stances from GameState if available
	var villains := WorldData.bosses
	if villains.is_empty():
		lines.append("  No villain data loaded yet.")
		return "\n".join(lines)
	for vname in villains:
		var v: Dictionary = villains[vname]
		var arc: String   = v.get("relationship_arc", "dormant")
		var stance: String = v.get("current_stance", "neutral")
		var arc_icon := _arc_icon(arc)
		lines.append("  %s  [b]%s[/b]" % [arc_icon, vname])
		lines.append("      Arc: %s   Stance: %s" % [arc.capitalize(), stance.capitalize()])
		var power_origin: String = v.get("power_origin", "")
		if not power_origin.is_empty():
			lines.append("      Origin: %s" % power_origin)
		lines.append("")
	return "\n".join(lines)

func _arc_icon(arc: String) -> String:
	match arc:
		"dormant":  return "💤"
		"active":   return "⚡"
		"rival":    return "⚔️"
		"nemesis":  return "💀"
		"reformed": return "🌿"
		_:          return "●"

# ── Quests tab ────────────────────────────────────────────────────────────────

func _build_quests() -> String:
	var log   := GameState.quest_log
	var total := log.size()
	var done  := 0
	var failed := 0
	for qid in log:
		match str(log[qid]):
			"completed": done  += 1
			"failed":    failed += 1

	var lines := PackedStringArray()
	lines.append("[b]Quest Log — %d / %d completed[/b]" % [done, total])
	if failed > 0:
		lines.append("  Failed: %d" % failed)
	lines.append("")
	for qid in log:
		var status: String = str(log[qid])
		var icon := "✅" if status == "completed" else ("❌" if status == "failed" else "▶")
		var q_data := WorldData.get_quest(qid)
		var q_name := q_data.get("name", qid) if not q_data.is_empty() else qid
		lines.append("  %s  %s  [%s]" % [icon, q_name, status])
	if total == 0:
		lines.append("  No quests started yet.")
	return "\n".join(lines)

# ── Navigation ────────────────────────────────────────────────────────────────

func _on_back() -> void:
	GameState.return_to_world_map()
