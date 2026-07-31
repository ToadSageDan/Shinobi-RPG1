## CombatManager.gd — Real-time combat singleton.
## Owns HP pools for active combat, resolves damage, affinity bonuses,
## status effect ticking, and emits signals consumed by the HUD.
extends Node

# ── Signals ───────────────────────────────────────────────────────────────────

signal player_took_damage(amount: int, source: String)
signal enemy_took_damage(enemy_id: int, amount: int)
signal player_died()
signal enemy_died(enemy_id: int)
signal status_effect_applied(target: String, effect_name: String, stacks: int)
signal status_effect_expired(target: String, effect_name: String)
signal combo_registered(combo_label: String, bonus_damage: int)
signal chakra_changed(current: int, maximum: int)
signal stamina_changed(current: int, maximum: int)
signal hit_flash_requested(target: String)

# ── Affinity interaction matrix ───────────────────────────────────────────────
# [attacker_affinity][defender_affinity] = damage_multiplier
const AFFINITY_MATRIX := {
	"fire":  {"fire": 1.0, "water": 0.6, "earth": 1.3, "wind": 1.1},
	"water": {"fire": 1.4, "water": 1.0, "earth": 0.8, "wind": 1.1},
	"earth": {"fire": 0.8, "water": 1.2, "earth": 1.0, "wind": 0.7},
	"wind":  {"fire": 0.9, "water": 0.9, "earth": 1.3, "wind": 1.0},
}

# Status effect tick damage per second (per stack)
const STATUS_TICK_DPS := {
	"burn":       8.0,
	"bleed":      6.0,
	"chill":      0.0,   # slow, no damage
	"drench":     0.0,   # amplifier only
	"crack_armor":0.0,   # defense debuff
	"stagger":    0.0,   # stun
	"blind":      0.0,   # accuracy debuff
	"silence":    0.0,   # blocks jutsu
	"root":       0.0,   # immobilize
	"fear":       4.0,   # tick damage + movement penalty
}

# Combo bonuses: (status_on_target, attacker_affinity) → {label, bonus_pct}
const COMBO_BONUSES := {
	"drench+wind":       {"label": "Storm Burst",    "bonus": 0.20},
	"chill+earth":       {"label": "Shatter Window", "bonus": 0.15},
	"crack_armor+fire":  {"label": "Armor Melt",     "bonus": 0.25},
	"blind+wind":        {"label": "Ambush Strike",  "bonus": 0.10},
}

# ── Enemy registry (active combat) ───────────────────────────────────────────

class EnemyCombatState:
	var id: int
	var display_name: String
	var hp: int
	var hp_max: int
	var affinity: String
	var defense: int
	var power: int
	var is_boss: bool
	var phase: int = 1              # boss phase (1 or 2)
	var status_effects: Dictionary  # name → {duration, stacks, tick_accum}
	var stagger_timer: float = 0.0
	var attack_cooldown: float = 0.0
	var signature_cooldown: float = 0.0

	func _init(p_id: int, p_name: String, p_hp: int, p_affinity: String,
			   p_defense: int, p_power: int, p_boss: bool) -> void:
		id           = p_id
		display_name = p_name
		hp           = p_hp
		hp_max       = p_hp
		affinity     = p_affinity
		defense      = p_defense
		power        = p_power
		is_boss      = p_boss
		status_effects = {}

var _enemies: Dictionary = {}   # id → EnemyCombatState
var _next_enemy_id: int = 0
var _combat_active: bool = false

# Accumulated tick damage fractional parts (so float tick → int HP works cleanly)
var _player_tick_accum: float = 0.0

# ── Combat lifecycle ──────────────────────────────────────────────────────────

func start_combat() -> void:
	_enemies.clear()
	_next_enemy_id = 0
	_combat_active = true
	_player_tick_accum = 0.0

func end_combat() -> void:
	_combat_active = false
	_enemies.clear()
	GameState.active_status_effects.clear()

func register_enemy(display_name: String, hp: int, affinity: String,
					defense: int, power: int, is_boss: bool = false) -> int:
	var id := _next_enemy_id
	_next_enemy_id += 1
	_enemies[id] = EnemyCombatState.new(id, display_name, hp, affinity, defense, power, is_boss)
	return id

func get_enemy(id: int) -> EnemyCombatState:
	return _enemies.get(id, null)

func get_all_enemies() -> Array:
	return _enemies.values()

func living_enemies() -> Array:
	var result := []
	for e in _enemies.values():
		if e.hp > 0:
			result.append(e)
	return result

# ── Damage resolution ─────────────────────────────────────────────────────────

func resolve_player_attack(
		move: Dictionary,
		enemy_id: int,
		player_affinity: String) -> Dictionary:
	var enemy: EnemyCombatState = _enemies.get(enemy_id, null)
	if not enemy or enemy.hp <= 0:
		return {}

	var base_damage := int(GameState.power * move.get("power_scale", 1.0))

	# Affinity multiplier
	var attacker_row: Dictionary = AFFINITY_MATRIX.get(player_affinity, {})
	var affinity_mult: float = attacker_row.get(enemy.affinity, 1.0)
	var damage := int(base_damage * affinity_mult)

	# Combo bonus check
	var combo_label := ""
	var bonus_damage := 0
	for key in COMBO_BONUSES:
		var parts := key.split("+")
		if parts.size() == 2:
			var status_needed := parts[0]
			var affinity_needed := parts[1]
			if status_needed in enemy.status_effects and player_affinity == affinity_needed:
				var bonus_dict: Dictionary = COMBO_BONUSES[key]
				var bd := int(damage * float(bonus_dict.get("bonus", 0.0)))
				if bd > bonus_damage:
					bonus_damage = bd
					combo_label = bonus_dict.get("label", "")

	damage += bonus_damage

	# Apply status effects from move
	var applied_statuses := move.get("status_effects", [])
	for effect in applied_statuses:
		_apply_status_to_enemy(enemy, effect, 2, 1)

	# Enemy defense reduction (crack_armor doubles reduction removal)
	var armor_mult := 1.2 if "crack_armor" in enemy.status_effects else 1.0
	var defense_reduction := int(enemy.defense * 0.15 * armor_mult)
	damage = maxi(1, damage - defense_reduction)

	enemy.hp = maxi(0, enemy.hp - damage)
	emit_signal("enemy_took_damage", enemy_id, damage)
	emit_signal("hit_flash_requested", "enemy_%d" % enemy_id)

	if combo_label != "":
		emit_signal("combo_registered", combo_label, bonus_damage)

	if enemy.hp <= 0:
		emit_signal("enemy_died", enemy_id)

	return {
		"damage": damage,
		"affinity_mult": affinity_mult,
		"combo_label": combo_label,
		"bonus_damage": bonus_damage,
		"enemy_hp": enemy.hp,
		"enemy_hp_max": enemy.hp_max,
		"killed": enemy.hp <= 0,
	}

func resolve_enemy_attack(enemy_id: int) -> int:
	var enemy: EnemyCombatState = _enemies.get(enemy_id, null)
	if not enemy or enemy.hp <= 0:
		return 0
	if enemy.stagger_timer > 0.0:
		return 0

	# Affinity multiplier against player
	var attacker_row: Dictionary = AFFINITY_MATRIX.get(enemy.affinity, {})
	var affinity_mult: float = attacker_row.get(GameState.affinity, 1.0)

	var base := int(enemy.power * affinity_mult)
	# Player defense reduction
	var def_val := GameState.defense
	if "crack_armor" in GameState.active_status_effects:
		def_val = int(def_val * 0.6)
	var reduction := int(def_val * 0.12)
	var damage := maxi(1, base - reduction)

	# Blind debuff on player = -30% damage dealt (enemy can't see clearly)
	if "blind" in GameState.active_status_effects:
		damage = int(damage * 0.7)

	GameState.hp = maxi(0, GameState.hp - damage)
	emit_signal("player_took_damage", damage, enemy.display_name)
	emit_signal("hit_flash_requested", "player")

	if GameState.hp <= 0:
		emit_signal("player_died")

	return damage

# ── Status effects ────────────────────────────────────────────────────────────

const STATUS_BANDS := {
	"burn":        {"dur_min": 2, "dur_max": 4, "max_stacks": 3},
	"bleed":       {"dur_min": 2, "dur_max": 4, "max_stacks": 3},
	"chill":       {"dur_min": 1, "dur_max": 3, "max_stacks": 2},
	"drench":      {"dur_min": 1, "dur_max": 3, "max_stacks": 2},
	"crack_armor": {"dur_min": 1, "dur_max": 3, "max_stacks": 2},
	"stagger":     {"dur_min": 1, "dur_max": 2, "max_stacks": 1},
	"blind":       {"dur_min": 1, "dur_max": 2, "max_stacks": 1},
	"silence":     {"dur_min": 1, "dur_max": 2, "max_stacks": 1},
	"root":        {"dur_min": 1, "dur_max": 2, "max_stacks": 1},
	"fear":        {"dur_min": 1, "dur_max": 2, "max_stacks": 1},
}

func apply_status_to_player(effect_name: String, duration: int = 2, stacks: int = 1) -> void:
	var band: Dictionary = STATUS_BANDS.get(effect_name, {})
	if band.is_empty():
		return
	var clamped_dur   := clampi(duration, band["dur_min"], band["dur_max"])
	var clamped_stk   := clampi(stacks, 1, band["max_stacks"])
	var existing: Variant = GameState.active_status_effects.get(effect_name)
	if existing is Dictionary:
		var new_stacks := mini(existing["stacks"] + clamped_stk, band["max_stacks"])
		var new_dur    := maxi(existing["duration"], clamped_dur)
		GameState.active_status_effects[effect_name] = {
			"duration": new_dur, "stacks": new_stacks, "tick_accum": existing.get("tick_accum", 0.0)
		}
	else:
		GameState.active_status_effects[effect_name] = {
			"duration": clamped_dur, "stacks": clamped_stk, "tick_accum": 0.0
		}
	emit_signal("status_effect_applied", "player", effect_name, clamped_stk)

	if effect_name == "stagger":
		GameState.spend_stamina(30)
		emit_signal("stamina_changed", GameState.stamina, GameState.stamina_max)

func _apply_status_to_enemy(enemy: EnemyCombatState, effect_name: String,
		duration: int, stacks: int) -> void:
	var band: Dictionary = STATUS_BANDS.get(effect_name, {})
	if band.is_empty():
		return
	var clamped_dur := clampi(duration, band["dur_min"], band["dur_max"])
	var clamped_stk := clampi(stacks, 1, band["max_stacks"])
	var existing: Variant = enemy.status_effects.get(effect_name)
	if existing is Dictionary:
		var new_stacks := mini(existing["stacks"] + clamped_stk, band["max_stacks"])
		var new_dur    := maxi(existing["duration"], clamped_dur)
		enemy.status_effects[effect_name] = {
			"duration": new_dur, "stacks": new_stacks, "tick_accum": existing.get("tick_accum", 0.0)
		}
	else:
		enemy.status_effects[effect_name] = {
			"duration": clamped_dur, "stacks": clamped_stk, "tick_accum": 0.0
		}
	emit_signal("status_effect_applied", "enemy_%d" % enemy.id, effect_name, clamped_stk)

# ── Tick update (called from _process in arenas) ──────────────────────────────

func tick(delta: float) -> void:
	if not _combat_active:
		return
	_tick_player_statuses(delta)
	_tick_enemy_statuses(delta)
	GameState.regen_chakra_passive(delta)

func _tick_player_statuses(delta: float) -> void:
	var to_remove: Array[String] = []
	for effect_name in GameState.active_status_effects.keys():
		var data: Dictionary = GameState.active_status_effects[effect_name]
		# Tick damage
		var dps: float = STATUS_TICK_DPS.get(effect_name, 0.0) * float(data["stacks"])
		if dps > 0.0:
			_player_tick_accum += dps * delta
			var tick_int := int(_player_tick_accum)
			if tick_int > 0:
				_player_tick_accum -= tick_int
				GameState.hp = maxi(0, GameState.hp - tick_int)
				emit_signal("player_took_damage", tick_int, effect_name)
				if GameState.hp <= 0:
					emit_signal("player_died")
					return
		# Duration countdown
		data["duration"] -= delta
		if data["duration"] <= 0.0:
			to_remove.append(effect_name)
	for effect_name in to_remove:
		GameState.active_status_effects.erase(effect_name)
		emit_signal("status_effect_expired", "player", effect_name)

func _tick_enemy_statuses(delta: float) -> void:
	for enemy in _enemies.values():
		if enemy.hp <= 0:
			continue
		var to_remove: Array[String] = []
		for effect_name in enemy.status_effects.keys():
			var data: Dictionary = enemy.status_effects[effect_name]
			var dps: float = STATUS_TICK_DPS.get(effect_name, 0.0) * float(data["stacks"])
			if dps > 0.0:
				data["tick_accum"] = data.get("tick_accum", 0.0) + dps * delta
				var tick_int := int(data["tick_accum"])
				if tick_int > 0:
					data["tick_accum"] -= tick_int
					enemy.hp = maxi(0, enemy.hp - tick_int)
					emit_signal("enemy_took_damage", enemy.id, tick_int)
					if enemy.hp <= 0:
						emit_signal("enemy_died", enemy.id)
						break
			data["duration"] -= delta
			if data["duration"] <= 0.0:
				to_remove.append(effect_name)
		for effect_name in to_remove:
			enemy.status_effects.erase(effect_name)
			emit_signal("status_effect_expired", "enemy_%d" % enemy.id, effect_name)

		# Tick stagger and attack cooldowns
		if enemy.stagger_timer > 0.0:
			enemy.stagger_timer = maxf(0.0, enemy.stagger_timer - delta)
		if enemy.attack_cooldown > 0.0:
			enemy.attack_cooldown = maxf(0.0, enemy.attack_cooldown - delta)
		if enemy.signature_cooldown > 0.0:
			enemy.signature_cooldown = maxf(0.0, enemy.signature_cooldown - delta)

# ── Utility ───────────────────────────────────────────────────────────────────

func stagger_enemy(enemy_id: int, duration: float = 1.2) -> void:
	var enemy: EnemyCombatState = _enemies.get(enemy_id, null)
	if enemy:
		enemy.stagger_timer = duration
		_apply_status_to_enemy(enemy, "stagger", 1, 1)

func is_player_silenced() -> bool:
	return "silence" in GameState.active_status_effects

func is_player_rooted() -> bool:
	return "root" in GameState.active_status_effects

func is_player_staggered() -> bool:
	return "stagger" in GameState.active_status_effects

func player_defense_multiplier() -> float:
	var mult := 1.0
	if "crack_armor" in GameState.active_status_effects:
		mult *= 0.6
	if "chill" in GameState.active_status_effects:
		mult *= 0.85
	return mult

func enemy_is_staggered(enemy_id: int) -> bool:
	var e: EnemyCombatState = _enemies.get(enemy_id, null)
	return e != null and e.stagger_timer > 0.0
