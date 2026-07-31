## WorldData.gd — Loads and exposes world JSON exported from the Python RPG system.
## Call load_world() once at startup (e.g. from GameState or Main).
extends Node

var regions: Array[Dictionary] = []
var quests:  Array[Dictionary] = []
var moves:   Array[Dictionary] = []
var bosses:  Dictionary = {}
var allies:  Array[Dictionary] = []
var shop_inventory: Array[Dictionary] = []

const WORLD_DATA_PATH := "res://data/world_data.json"

func load_world() -> bool:
	if not FileAccess.file_exists(WORLD_DATA_PATH):
		push_warning("WorldData: world_data.json not found at %s" % WORLD_DATA_PATH)
		_load_fallback()
		return false

	var file := FileAccess.open(WORLD_DATA_PATH, FileAccess.READ)
	if not file:
		push_warning("WorldData: could not open world_data.json")
		_load_fallback()
		return false

	var text := file.get_as_text()
	file.close()

	var parsed: Variant = JSON.parse_string(text)
	if not parsed is Dictionary:
		push_warning("WorldData: failed to parse world_data.json")
		_load_fallback()
		return false

	var data: Dictionary = parsed
	regions        = _to_array_dict(data.get("regions", []))
	quests         = _to_array_dict(data.get("quests", []))
	moves          = _to_array_dict(data.get("moves", []))
	bosses         = data.get("bosses", {})
	allies         = _to_array_dict(data.get("allies", []))
	shop_inventory = _to_array_dict(data.get("shop_inventory", []))
	return true

func _to_array_dict(v: Variant) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if v is Array:
		for item in v:
			if item is Dictionary:
				result.append(item)
	return result

# ── Queries ───────────────────────────────────────────────────────────────────

func get_region(region_key: String) -> Dictionary:
	for r in regions:
		if r.get("key") == region_key:
			return r
	return {}

func get_boss(boss_name: String) -> Dictionary:
	return bosses.get(boss_name, {})

func get_quest(quest_id: String) -> Dictionary:
	for q in quests:
		if q.get("quest_id") == quest_id:
			return q
	return {}

func get_moves_for_affinity(affinity: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for m in moves:
		var affs: Array = m.get("affinities", [])
		if affinity in affs:
			result.append(m)
	return result

# ── Fallback hardcoded data (used if JSON export is missing) ──────────────────

func _load_fallback() -> void:
	regions = [
		{
			"key": "verdant_gate",
			"name": "Verdant Gate",
			"climate": "humid forest frontier",
			"minimum_level": 1,
			"boss": "Kage Renda",
			"boss_affinity": "wind",
			"boss_hp": 350,
			"boss_power": 18,
			"boss_defense": 12,
			"encounter_table": ["Bandit Scouts", "Mist Ronin", "Root Stalkers"],
			"biome_color": Color(0.1, 0.4, 0.1, 1.0),
			"fog_color": Color(0.3, 0.5, 0.2, 1.0),
		},
		{
			"key": "ashen_cradle",
			"name": "Ashen Cradle",
			"climate": "volcanic dry heat",
			"minimum_level": 4,
			"boss": "General Voln",
			"boss_affinity": "fire",
			"boss_hp": 500,
			"boss_power": 24,
			"boss_defense": 16,
			"encounter_table": ["Ash Mercenaries", "Ember Raiders", "Lava Hounds"],
			"biome_color": Color(0.6, 0.2, 0.05, 1.0),
			"fog_color": Color(0.8, 0.3, 0.1, 1.0),
		},
		{
			"key": "tideglass",
			"name": "Tideglass",
			"climate": "coastal reef network",
			"minimum_level": 7,
			"boss": "Admiral Neris",
			"boss_affinity": "water",
			"boss_hp": 680,
			"boss_power": 28,
			"boss_defense": 20,
			"encounter_table": ["Tide Hunters", "Reef Assassins", "Corsair Guards"],
			"biome_color": Color(0.05, 0.3, 0.55, 1.0),
			"fog_color": Color(0.15, 0.45, 0.6, 1.0),
		},
		{
			"key": "stormwall_ridge",
			"name": "Stormwall Ridge",
			"climate": "alpine thunder belt",
			"minimum_level": 10,
			"boss": "Zephyr Tyrant",
			"boss_affinity": "wind",
			"boss_hp": 900,
			"boss_power": 34,
			"boss_defense": 22,
			"encounter_table": ["Windcutter Raiders", "Gale Monks", "Stormcaller Scouts"],
			"biome_color": Color(0.55, 0.55, 0.7, 1.0),
			"fog_color": Color(0.7, 0.7, 0.85, 1.0),
		},
		{
			"key": "sunken_hollow",
			"name": "Sunken Hollow",
			"climate": "subterranean toxic",
			"minimum_level": 14,
			"boss": "Ashen Monarch",
			"boss_affinity": "earth",
			"boss_hp": 1200,
			"boss_power": 40,
			"boss_defense": 28,
			"encounter_table": ["Cave Stalkers", "Poison Adepts", "Hollow Wraiths"],
			"biome_color": Color(0.2, 0.1, 0.3, 1.0),
			"fog_color": Color(0.35, 0.15, 0.4, 1.0),
		},
	]

	bosses = {
		"Kage Renda": {
			"affinity": "wind",
			"hp": 350,
			"power": 18,
			"defense": 12,
			"signature_move": "Razorwind Spiral",
			"signature_power_scale": 1.28,
			"signature_statuses": ["bleed", "crack_armor"],
			"phase2_hp_threshold": 0.5,
			"phase2_power_bonus": 6,
			"taunt_lines": [
				"These roads are mine by blood and wind.",
				"You crossed the last gate you will ever see.",
			],
		},
		"General Voln": {
			"affinity": "fire",
			"hp": 500,
			"power": 24,
			"defense": 16,
			"signature_move": "Inferno Vortex",
			"signature_power_scale": 1.3,
			"signature_statuses": ["burn", "stagger"],
			"phase2_hp_threshold": 0.5,
			"phase2_power_bonus": 8,
			"taunt_lines": [
				"This front never broke — it just ran out of recruits.",
				"You smell like forest. You are in the wrong war.",
			],
		},
		"Admiral Neris": {
			"affinity": "water",
			"hp": 680,
			"power": 28,
			"defense": 20,
			"signature_move": "Maelstrom Guard",
			"signature_power_scale": 1.08,
			"signature_statuses": ["drench", "chill"],
			"phase2_hp_threshold": 0.5,
			"phase2_power_bonus": 10,
			"taunt_lines": [
				"The basin drowns everyone eventually.",
				"Every order I gave was law — until you.",
			],
		},
		"Zephyr Tyrant": {
			"affinity": "wind",
			"hp": 900,
			"power": 34,
			"defense": 22,
			"signature_move": "Cyclone Throne Shatter",
			"signature_power_scale": 2.55,
			"signature_statuses": ["stagger", "crack_armor"],
			"phase2_hp_threshold": 0.5,
			"phase2_power_bonus": 12,
			"taunt_lines": [
				"The ridge sings only for me.",
				"You climbed this high only to fall further.",
			],
		},
		"Ashen Monarch": {
			"affinity": "earth",
			"hp": 1200,
			"power": 40,
			"defense": 28,
			"signature_move": "Subterranean Collapse",
			"signature_power_scale": 1.35,
			"signature_statuses": ["crack_armor", "root"],
			"phase2_hp_threshold": 0.5,
			"phase2_power_bonus": 15,
			"taunt_lines": [
				"This vault was old when your bloodline was young.",
				"The earth always reclaims what it gave.",
			],
		},
	}
