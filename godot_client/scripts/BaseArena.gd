## BaseArena.gd — Common logic shared by all five region arenas.
## Handles: spawning enemies/boss, connecting combat signals to HUD,
##           defeat/victory flow, jutsu spawning, and scene transitions.
extends Node3D

# ── Arena configuration (set by each subclass or @export) ────────────────────

@export var region_key: String = "verdant_gate"
@export var region_min_level: int = 1
@export var is_boss_arena: bool = false
@export var jutsu_projectile_scene: PackedScene

# ── Node references ───────────────────────────────────────────────────────────

var _player: CharacterBody3D
var _hud: Control
var _game_over_screen: Control
var _enemy_spawn_points: Array[Node3D] = []
var _boss_node = null          # Boss.gd instance (if boss arena)
var _jutsu_spawner: Node3D

# ── State ─────────────────────────────────────────────────────────────────────

var _combat_started: bool = false
var _all_enemies_defeated: bool = false
var _boss_approach: String = ""

const WAYPOINT_SCENE := "res://scenes/ui/QuestWaypoint.tscn"

# ── Lifecycle ─────────────────────────────────────────────────────────────────

func _ready() -> void:
	# Check level gate
	if GameState.level < region_min_level:
		_show_level_gate_message()
		return

	_player          = get_node_or_null("Player")
	_hud             = get_node_or_null("HUD")
	_game_over_screen = get_node_or_null("GameOver")
	_jutsu_spawner   = get_node_or_null("JutsuSpawner")

	# Collect spawn points
	for child in get_children():
		if child.is_in_group("enemy_spawn"):
			_enemy_spawn_points.append(child)

	# Connect player signals
	if _player:
		_player.attacked.connect(_on_player_attacked)
		_player.jutsu_fired.connect(_on_jutsu_fired)
		_player.player_died_signal.connect(_on_player_died)
		_player.add_to_group("player")

	# Connect CombatManager signals to HUD
	CombatManager.player_took_damage.connect(_on_player_damage_hud)
	CombatManager.enemy_took_damage.connect(_on_enemy_damage_hud)
	CombatManager.enemy_died.connect(_on_enemy_died)
	CombatManager.combo_registered.connect(_on_combo_hud)
	CombatManager.player_died.connect(_on_player_died)
	CombatManager.status_effect_applied.connect(_on_status_applied_hud)
	CombatManager.hit_flash_requested.connect(_on_hit_flash)

	# Initialize combat
	CombatManager.start_combat()
	AudioManager.play_music(AudioManager.music_key_for_region(region_key))

	# Build biome-specific placeholder terrain (replaced by real assets when available)
	BiomeTerrain.build(self, region_key)
	_spawn_quest_waypoints()
	_spawn_arena_contents()

func _process(delta: float) -> void:
	CombatManager.tick(delta)

# ── Quest waypoints ───────────────────────────────────────────────────────────

## Spawns in-world quest markers for any active quests whose target_region
## matches this arena's region_key.
func _spawn_quest_waypoints() -> void:
	if not ResourceLoader.exists(WAYPOINT_SCENE):
		return
	var wp_scene: PackedScene = load(WAYPOINT_SCENE)
	if not wp_scene:
		return
	for quest in WorldData.quests:
		var qid: String   = quest.get("quest_id", "")
		var status: String = str(GameState.quest_log.get(qid, ""))
		if status != "active":
			continue
		var target_region: String = quest.get("target_region", "")
		if not target_region.is_empty() and target_region != region_key:
			continue
		# Place waypoint near a random spawn point, or at arena centre offset
		var wp_pos := Vector3(randf_range(-4.0, 4.0), 0.0, randf_range(-4.0, 4.0))
		if not _enemy_spawn_points.is_empty():
			var sp := _enemy_spawn_points[randi() % _enemy_spawn_points.size()]
			wp_pos = sp.global_position
		var wp: Node3D = wp_scene.instantiate()
		add_child(wp)
		wp.global_position = wp_pos
		wp.call("setup", qid, quest.get("name", qid))

# ── Spawn ─────────────────────────────────────────────────────────────────────

func _spawn_arena_contents() -> void:
	# Subclasses override to place specific enemies/bosses.
	# Base spawns a generic encounter from WorldData.
	var region_data := WorldData.get_region(region_key)
	if region_data.is_empty():
		return

	if is_boss_arena:
		_spawn_boss(region_data)
	else:
		_spawn_encounter(region_data)

func _spawn_encounter(region_data: Dictionary) -> void:
	var table: Array = region_data.get("encounter_table", [])
	if table.is_empty():
		return

	var count := randi_range(1, mini(3, _enemy_spawn_points.size()))
	for i in range(count):
		var enemy_name: String = table[randi() % table.size()]
		var spawn_pos: Vector3 = _enemy_spawn_points[i].global_position if i < _enemy_spawn_points.size() else global_position + Vector3(randf_range(-5, 5), 0, randf_range(-5, 5))
		_spawn_enemy_at(enemy_name, spawn_pos, false)

func _spawn_boss(region_data: Dictionary) -> void:
	var boss_name: String = region_data.get("boss", "")
	if boss_name.is_empty():
		return
	var boss_data := WorldData.get_boss(boss_name)
	var spawn_pos := Vector3.ZERO
	if not _enemy_spawn_points.is_empty():
		spawn_pos = _enemy_spawn_points[0].global_position

	var boss_scene_path := "res://scenes/characters/Boss.tscn"
	var boss_scene: PackedScene = load(boss_scene_path)
	if not boss_scene:
		return

	_boss_node = boss_scene.instantiate()
	_boss_node.boss_name         = boss_name
	_boss_node.display_name      = boss_name
	_boss_node.enemy_affinity    = boss_data.get("affinity", "fire")
	_boss_node.base_hp           = boss_data.get("hp", 400)
	_boss_node.base_power        = boss_data.get("power", 20)
	_boss_node.base_defense      = boss_data.get("defense", 14)
	_boss_node.signature_move_name    = boss_data.get("signature_move", "")
	_boss_node.signature_power_scale  = float(boss_data.get("signature_power_scale", 1.2))
	_boss_node.signature_statuses     = boss_data.get("signature_statuses", [])
	_boss_node.phase2_power_bonus     = boss_data.get("phase2_power_bonus", 8)
	_boss_node.taunt_lines            = boss_data.get("taunt_lines", [])
	_boss_node.global_position        = spawn_pos
	add_child(_boss_node)

	_boss_node.boss_taunt.connect(_on_boss_taunt)
	_boss_node.boss_defeated.connect(_on_boss_defeated)
	_boss_node.phase_transition.connect(_on_boss_phase_transition)

	# Play opening cutscene then give cinematic control back
	await _play_boss_cutscene(boss_name)
	if is_instance_valid(_boss_node):
		_boss_node.cinematic_finished(0)

func _spawn_enemy_at(enemy_name: String, spawn_pos: Vector3, is_boss: bool) -> void:
	var enemy_scene: PackedScene = load("res://scenes/characters/Enemy.tscn")
	if not enemy_scene:
		return
	var enemy = enemy_scene.instantiate()
	enemy.display_name   = enemy_name
	enemy.global_position = spawn_pos
	enemy.enemy_affinity = _pick_encounter_affinity(enemy_name)
	enemy.learnable_move_name = _learnable_move_for(enemy_name)
	add_child(enemy)
	enemy.died.connect(_on_enemy_field_died)

# ── Combat event handlers ─────────────────────────────────────────────────────

func _on_player_attacked(move_dict: Dictionary, target_id: int) -> void:
	if target_id < 0:
		return
	var result := CombatManager.resolve_player_attack(
		move_dict, target_id, GameState.affinity
	)
	if _hud:
		_hud.call("show_damage_number", result.get("damage", 0),
				  CombatManager.get_enemy(target_id))

func _on_jutsu_fired(move_dict: Dictionary, charge_ratio: float) -> void:
	if not jutsu_projectile_scene or not _jutsu_spawner:
		return
	if not _player:
		return
	var projectile = jutsu_projectile_scene.instantiate()
	_jutsu_spawner.add_child(projectile)
	projectile.global_position = _player.global_position + Vector3(0, 1.2, 0)
	var forward := -_player.global_transform.basis.z
	projectile.launch(forward, move_dict, charge_ratio, GameState.affinity)

func _on_player_died() -> void:
	AudioManager.stop_music()
	AudioManager.play_sfx("sfx_death")
	if _game_over_screen:
		_game_over_screen.show()
		_game_over_screen.call("populate_stats")
	get_tree().paused = true

func _on_player_damage_hud(amount: int, source: String) -> void:
	if _hud:
		_hud.call("update_player_hp", GameState.hp, GameState.hp_max)
		_hud.call("show_damage_flash")

func _on_enemy_damage_hud(enemy_id: int, amount: int) -> void:
	if _hud:
		_hud.call("update_enemy_hp", enemy_id, amount)

func _on_enemy_died(enemy_id: int) -> void:
	var all_dead := CombatManager.living_enemies().is_empty()
	if all_dead and not is_boss_arena:
		_on_encounter_cleared()

func _on_enemy_field_died(enemy_id: int, learnable_move: String) -> void:
	GameState.encounter_outcomes["kill"] += 1
	if not learnable_move.is_empty():
		_offer_learnable_move(learnable_move)
	_check_encounter_cleared()

func _on_boss_taunt(line: String) -> void:
	if _hud:
		_hud.call("show_boss_taunt", line)

func _on_boss_phase_transition(new_phase: int) -> void:
	if _hud:
		_hud.call("show_phase_transition", new_phase)

func _on_boss_defeated(boss_name: String, approach: String, reward_move: String) -> void:
	GameState.mark_region_cleared(region_key)
	CombatManager.end_combat()
	AudioManager.stop_music()
	if _hud:
		_hud.call("show_victory", boss_name, approach)
	await get_tree().create_timer(3.5).timeout
	GameState.return_to_world_map()

func _on_combo_hud(combo_label: String, bonus: int) -> void:
	if _hud:
		_hud.call("show_combo_popup", combo_label, bonus)

func _on_status_applied_hud(target: String, effect_name: String, stacks: int) -> void:
	if _hud:
		_hud.call("update_status_effects")

func _on_hit_flash(target: String) -> void:
	if _hud:
		_hud.call("flash_hit_indicator", target)

# ── Encounter cleared ─────────────────────────────────────────────────────────

func _check_encounter_cleared() -> void:
	if CombatManager.living_enemies().is_empty():
		_on_encounter_cleared()

func _on_encounter_cleared() -> void:
	_all_enemies_defeated = true
	# Award XP
	var xp_reward := 15 * GameState.level
	var levels := GameState.gain_xp(xp_reward)
	if levels > 0:
		if _hud:
			_hud.call("show_level_up", GameState.level)
	GameState.save_game()
	await get_tree().create_timer(2.0).timeout
	GameState.return_to_world_map()

# ── Learnable moves ───────────────────────────────────────────────────────────

func _offer_learnable_move(move_name: String) -> void:
	# Look up move spec in WorldData.moves
	for m in WorldData.moves:
		if m.get("name") == move_name:
			GameState.register_move(m)
			if _hud:
				_hud.call("show_move_learned", move_name)
			return

func _learnable_move_for(enemy_name: String) -> String:
	# Map enemy names to their learnable move names (from Python ENEMY_EXCLUSIVE_MOVE_SPECS)
	var map := {
		"Mist Ronin":          "Fog Dagger Surge",
		"Root Stalkers":       "Creeping Vine Bind",
		"Ash Mercenaries":     "Scorch Rush",
		"Ember Raiders":       "Ember Burst",
		"Tide Hunters":        "Deep Current Drag",
		"Reef Assassins":      "Reef Shadow Lunge",
		"Windcutter Raiders":  "Gale Blade Flurry",
		"Gale Monks":          "Resonant Wind Seal",
		"Stormcaller Scouts":  "Lightning Thread",
		"Cave Stalkers":       "Blind Ambush",
		"Poison Adepts":       "Venom Weave",
		"Hollow Wraiths":      "Wraith Shriek",
	}
	return map.get(enemy_name, "")

func _pick_encounter_affinity(enemy_name: String) -> String:
	var lower := enemy_name.to_lower()
	if "ash" in lower or "ember" in lower or "fire" in lower or "lava" in lower:
		return "fire"
	if "mist" in lower or "tide" in lower or "reef" in lower or "water" in lower:
		return "water"
	if "root" in lower or "cave" in lower or "stone" in lower or "poison" in lower:
		return "earth"
	if "wind" in lower or "gale" in lower or "storm" in lower or "wraith" in lower:
		return "wind"
	return ["fire", "water", "earth", "wind"][randi() % 4]

# ── Cinematic stub (overridden in arena subclasses if needed) ─────────────────

func _play_boss_cutscene(_boss_name: String) -> void:
	# Default: no cutscene delay. Arena subclasses can override to
	# trigger their cutscene scene and await completion.
	await get_tree().create_timer(0.1).timeout

# ── Level gate ────────────────────────────────────────────────────────────────

func _show_level_gate_message() -> void:
	if _hud:
		_hud.call("show_level_gate", region_min_level, GameState.level)
	await get_tree().create_timer(3.0).timeout
	GameState.return_to_world_map()
