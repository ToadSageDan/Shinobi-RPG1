## Boss.gd — Boss AI extending Enemy with phase transitions, signature move,
##            cinematic taunt, dialogue stance, and per-region behaviors.
extends "res://scripts/Enemy.gd"

# ── Boss config ───────────────────────────────────────────────────────────────

@export var boss_name: String = "Kage Renda"
@export var signature_move_name: String = "Razorwind Spiral"
@export var signature_power_scale: float = 1.28
@export var signature_statuses: Array[String] = ["bleed", "crack_armor"]
@export var signature_cooldown_time: float = 8.0
@export var phase2_hp_threshold: float = 0.5
@export var phase2_power_bonus: int = 8
@export var taunt_lines: Array[String] = []

# ── Runtime ───────────────────────────────────────────────────────────────────

var _phase: int = 1
var _signature_cooldown: float = 0.0
var _entered_phase2: bool = false
var _cinematic_done: bool = false
var _dialogue_stance_delta: int = 0  # from player's pre-fight dialogue choice

signal phase_transition(new_phase: int)
signal boss_taunt(line: String)
signal boss_defeated(boss_name: String, approach: String, reward_move: String)

# Override base detection to be longer for bosses
func _ready() -> void:
	detect_range = 25.0
	attack_range = 3.0
	attack_cooldown_time = 2.0
	super._ready()
	# Apply dialogue stance delta to aggression (set from cutscene result)
	_apply_dialogue_stance()

func _apply_dialogue_stance() -> void:
	var enemy_data := CombatManager.get_enemy(enemy_id)
	if enemy_data and _dialogue_stance_delta != 0:
		enemy_data.power = maxi(1, enemy_data.power + _dialogue_stance_delta)

# ── Physics override ──────────────────────────────────────────────────────────

func _physics_process(delta: float) -> void:
	if not _cinematic_done:
		return  # wait for cutscene to finish before AI activates
	super._physics_process(delta)
	_tick_boss_specific(delta)

func _tick_boss_specific(delta: float) -> void:
	if _signature_cooldown > 0.0:
		_signature_cooldown -= delta

	# Phase 2 transition check
	if not _entered_phase2 and _hp <= int(_hp_max * phase2_hp_threshold):
		_enter_phase2()

	# Signature move trigger
	if _ai_state == AIState.CHASE and _signature_cooldown <= 0.0 and _player_in_range(12.0):
		_fire_signature_move()

# ── Phase 2 ───────────────────────────────────────────────────────────────────

func _enter_phase2() -> void:
	_entered_phase2 = true
	_phase = 2
	emit_signal("phase_transition", 2)

	# Boost stats in CombatManager
	var enemy_data := CombatManager.get_enemy(enemy_id)
	if enemy_data:
		enemy_data.power += phase2_power_bonus

	# Emit a taunt
	_emit_random_taunt()

	# Speed up attack cadence
	attack_cooldown_time = maxf(0.8, attack_cooldown_time - 0.5)
	charge_speed = minf(12.0, charge_speed + 2.0)

	# Blend intensity music layer
	AudioManager.set_intensity_layer(
		"music_boss_phase2_%s" % boss_name.to_snake_case(),
		0.0, 1.5
	)

func get_phase() -> int:
	return _phase

# ── Signature move ────────────────────────────────────────────────────────────

func _fire_signature_move() -> void:
	_signature_cooldown = signature_cooldown_time
	_play_anim("boss_signature")

	# Construct a move dict and resolve damage
	var sig_move := {
		"name": signature_move_name,
		"category": "attack",
		"power_scale": signature_power_scale,
		"affinities": [enemy_affinity],
		"status_effects": signature_statuses,
	}

	# Brief telegraph pause, then hit
	await get_tree().create_timer(0.6).timeout

	# Resolve higher-power enemy attack
	var enemy_data := CombatManager.get_enemy(enemy_id)
	if enemy_data:
		var orig_power := enemy_data.power
		enemy_data.power = int(orig_power * signature_power_scale)
		CombatManager.resolve_enemy_attack(enemy_id)
		# Apply signature statuses to player
		for status in signature_statuses:
			CombatManager.apply_status_to_player(status, 2, 1)
		enemy_data.power = orig_power

# ── Cinematic integration ─────────────────────────────────────────────────────

## Called by the arena once the opening cutscene finishes.
func cinematic_finished(dialogue_stance_delta: int) -> void:
	_dialogue_stance_delta = dialogue_stance_delta
	_cinematic_done = true
	_apply_dialogue_stance()
	_emit_random_taunt()

func _emit_random_taunt() -> void:
	if taunt_lines.is_empty():
		return
	var line := taunt_lines[randi() % taunt_lines.size()]
	emit_signal("boss_taunt", line)

# ── Approach-based defeat ─────────────────────────────────────────────────────

## Arena calls this when player confirms their victory approach.
func defeat(approach: String, reward_move: String) -> void:
	_ai_state = AIState.DEAD
	_play_anim("boss_defeat_%s" % approach)
	emit_signal("boss_defeated", boss_name, approach, reward_move)
	await get_tree().create_timer(3.0).timeout
	queue_free()
