## Hitbox.gd — Attach to an Area3D child of the Player.
## When the hitbox is active and overlaps a Hurtbox, resolves damage.
extends Area3D

## Set by the Player before each attack swing.
var current_move: Dictionary = {}
var owner_affinity: String = "fire"

func _ready() -> void:
	monitoring = false
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)

## Activate for one swing. Called by Player.gd.
func activate(move: Dictionary, affinity: String, duration: float = 0.12) -> void:
	current_move = move
	owner_affinity = affinity
	monitoring = true
	await get_tree().create_timer(duration).timeout
	monitoring = false

func _on_body_entered(body: Node3D) -> void:
	_try_hit(body)

func _on_area_entered(area: Area3D) -> void:
	_try_hit(area.get_parent())

func _try_hit(target: Node) -> void:
	if not monitoring:
		return
	if not target.is_in_group("enemies"):
		return
	var enemy_id: Variant = target.get("enemy_id")
	if enemy_id == null:
		return
	var result := CombatManager.resolve_player_attack(
		current_move, int(enemy_id), owner_affinity
	)
	if not result.is_empty():
		# Play hit SFX for the attacker's affinity
		AudioManager.play_sfx(AudioManager.hit_sfx_for_affinity(owner_affinity))
		# Stagger on heavy or launcher
		var category: String = current_move.get("category", "attack")
		if category == "heavy_attack":
			CombatManager.stagger_enemy(int(enemy_id), 1.0)
