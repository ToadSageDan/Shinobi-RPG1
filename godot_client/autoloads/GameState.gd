## GameState.gd — Global persistent game state singleton.
## Stores player profile, progression, and bridges Python RPG data.
extends Node

# ── Player runtime state ──────────────────────────────────────────────────────

var player_name: String = ""
var affinity: String = "fire"        # fire / water / earth / wind
var backstory_key: String = ""

# Stats (mirror of Python PlayerStats)
var level: int = 1
var xp: int = 0
var power: int = 10
var defense: int = 10
var agility: int = 10
var focus: int = 10

# Resources
var hp: int = 150
var hp_max: int = 150
var chakra: int = 120
var chakra_max: int = 120
var stamina: int = 100
var stamina_max: int = 100

# Progression
var reputation: int = 0
var credits: int = 100
var trophies: Array[String] = []
var unlocked_moves: Array[Dictionary] = []
var encounter_outcomes: Dictionary = {"kill": 0, "charm": 0, "stealth": 0, "evasion": 0}
var quest_log: Dictionary = {}
var cleared_regions: Array[String] = []
var ally_loyalty: Dictionary = {}

# Active combat status effects (synced with CombatManager)
var active_status_effects: Dictionary = {}

# ── Save / Load ───────────────────────────────────────────────────────────────

const SAVE_PATH := "user://shinobi_save.json"

func save_game() -> void:
	var data := {
		"player_name": player_name,
		"affinity": affinity,
		"backstory_key": backstory_key,
		"level": level,
		"xp": xp,
		"power": power,
		"defense": defense,
		"agility": agility,
		"focus": focus,
		"hp": hp,
		"hp_max": hp_max,
		"chakra": chakra,
		"chakra_max": chakra_max,
		"stamina": stamina,
		"stamina_max": stamina_max,
		"reputation": reputation,
		"credits": credits,
		"trophies": trophies,
		"unlocked_moves": unlocked_moves,
		"encounter_outcomes": encounter_outcomes,
		"quest_log": quest_log,
		"cleared_regions": cleared_regions,
		"ally_loyalty": ally_loyalty,
	}
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data, "\t"))
		file.close()

func load_game() -> bool:
	if not FileAccess.file_exists(SAVE_PATH):
		return false
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if not file:
		return false
	var text := file.get_as_text()
	file.close()
	var parsed: Variant = JSON.parse_string(text)
	if not parsed is Dictionary:
		return false
	var data: Dictionary = parsed
	player_name       = data.get("player_name", "")
	affinity          = data.get("affinity", "fire")
	backstory_key     = data.get("backstory_key", "")
	level             = data.get("level", 1)
	xp                = data.get("xp", 0)
	power             = data.get("power", 10)
	defense           = data.get("defense", 10)
	agility           = data.get("agility", 10)
	focus             = data.get("focus", 10)
	reputation        = data.get("reputation", 0)
	credits           = data.get("credits", 100)
	trophies          = data.get("trophies", [])
	unlocked_moves    = data.get("unlocked_moves", [])
	encounter_outcomes = data.get("encounter_outcomes", {"kill":0,"charm":0,"stealth":0,"evasion":0})
	quest_log         = data.get("quest_log", {})
	cleared_regions   = data.get("cleared_regions", [])
	ally_loyalty      = data.get("ally_loyalty", {})
	_recalculate_vitals()
	hp = data.get("hp", hp_max)
	chakra = data.get("chakra", chakra_max)
	stamina = data.get("stamina", stamina_max)
	return true

func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)

func delete_save() -> void:
	if FileAccess.file_exists(SAVE_PATH):
		DirAccess.remove_absolute(SAVE_PATH)

# ── Stat helpers ──────────────────────────────────────────────────────────────

func _recalculate_vitals() -> void:
	hp_max      = defense * 10 + 50
	chakra_max  = focus   * 10 + 20
	stamina_max = agility * 8  + 20

func gain_xp(amount: int) -> int:
	xp += amount
	var levels_gained := 0
	while xp >= level * 100:
		xp -= level * 100
		level += 1
		power   += 2
		defense += 2
		agility += 2
		focus   += 2
		levels_gained += 1
	_recalculate_vitals()
	return levels_gained

func apply_level_up_hp_refill() -> void:
	hp      = hp_max
	chakra  = chakra_max
	stamina = stamina_max

func chakra_cost_for_category(category: String) -> int:
	match category:
		"ultimate": return maxi(20, int(chakra_max * 0.45))
		"summon":   return maxi(12, int(chakra_max * 0.28))
		_:          return 0

func can_afford_chakra(category: String) -> bool:
	return chakra >= chakra_cost_for_category(category)

func spend_chakra(category: String) -> void:
	chakra = maxi(0, chakra - chakra_cost_for_category(category))

func charge_chakra() -> int:
	var gain := maxi(10, int(chakra_max * 0.22) + focus / 2)
	var prev := chakra
	chakra = mini(chakra_max, chakra + gain)
	return chakra - prev

func spend_stamina(amount: int) -> void:
	stamina = maxi(0, stamina - amount)

func recover_stamina(amount: int) -> void:
	stamina = mini(stamina_max, stamina + amount)

func regen_chakra_passive(delta: float) -> void:
	if chakra < chakra_max:
		chakra = mini(chakra_max, chakra + int(focus * 0.5 * delta))

# ── Reputation ────────────────────────────────────────────────────────────────

func reputation_tier() -> String:
	if reputation <= -50:
		return "rogue"
	if reputation >= 50:
		return "heroic"
	return "neutral"

# ── Move registry ─────────────────────────────────────────────────────────────

func register_move(move_dict: Dictionary) -> void:
	for m in unlocked_moves:
		if m.get("name") == move_dict.get("name"):
			return
	unlocked_moves.append(move_dict)

func get_moves_by_category(category: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for m in unlocked_moves:
		if m.get("category") == category:
			result.append(m)
	return result

# ── Region tracking ───────────────────────────────────────────────────────────

func mark_region_cleared(region_name: String) -> void:
	if region_name not in cleared_regions:
		cleared_regions.append(region_name)
	save_game()

func is_region_cleared(region_name: String) -> bool:
	return region_name in cleared_regions

# ── Trophy helpers ────────────────────────────────────────────────────────────

func unlock_trophy(key: String) -> bool:
	if key in trophies:
		return false
	trophies.append(key)
	save_game()
	return true

# ── Scene management ──────────────────────────────────────────────────────────

var _current_arena: String = ""

func enter_arena(region_key: String) -> void:
	_current_arena = region_key
	var path := "res://scenes/arenas/%s.tscn" % _region_scene_name(region_key)
	get_tree().change_scene_to_file(path)

func _region_scene_name(key: String) -> String:
	match key:
		"verdant_gate":   return "VerdantGate"
		"ashen_cradle":   return "AshenCradle"
		"tideglass":      return "Tideglass"
		"stormwall_ridge": return "StormwallRidge"
		"sunken_hollow":  return "SunkenHollow"
		_:                return "VerdantGate"

func return_to_world_map() -> void:
	get_tree().change_scene_to_file("res://scenes/WorldMap.tscn")

func go_to_main_menu() -> void:
	get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")
