## JutsuProjectile.gd — A fired jutsu projectile.
## Spawned by the arena's JutsuSpawner in response to Player.jutsu_fired.
## Travels in a direction, applies damage + statuses on first hit.
extends Area3D

var move_dict: Dictionary = {}
var charge_ratio: float = 1.0
var player_affinity: String = "fire"
var travel_speed: float = 18.0
var lifetime: float = 3.0
var _traveled: float = 0.0
var _direction: Vector3 = Vector3.FORWARD
var _hit_ids: Array[int] = []    # prevent hitting same enemy twice

# Visual node references
var _vfx: GPUParticles3D
var _mesh: MeshInstance3D

func _ready() -> void:
	area_entered.connect(_on_area_entered)
	body_entered.connect(_on_body_entered)
	_vfx  = get_node_or_null("VFX")
	_mesh = get_node_or_null("Mesh")

## Call after instantiation to configure travel direction.
func launch(direction: Vector3, p_move: Dictionary, p_charge: float, p_affinity: String) -> void:
	_direction    = direction.normalized()
	move_dict     = p_move
	charge_ratio  = p_charge
	player_affinity = p_affinity
	# Scale visual intensity by charge
	if _vfx:
		_vfx.amount = int(lerp(8.0, 32.0, charge_ratio))
	if _mesh:
		var scale_val := lerpf(0.25, 0.8, charge_ratio)
		_mesh.scale = Vector3.ONE * scale_val

func _process(delta: float) -> void:
	_traveled += delta
	if _traveled >= lifetime:
		_expire()
		return
	global_position += _direction * travel_speed * delta

func _on_area_entered(area: Area3D) -> void:
	_try_hit_node(area.get_parent())

func _on_body_entered(body: Node3D) -> void:
	_try_hit_node(body)

func _try_hit_node(node: Node) -> void:
	if not node.is_in_group("enemies"):
		return
	var enemy_id: Variant = node.get("enemy_id")
	if enemy_id == null:
		return
	var eid := int(enemy_id)
	if eid in _hit_ids:
		return
	_hit_ids.append(eid)

	# Boost power by charge ratio
	var boosted_move := move_dict.duplicate()
	boosted_move["power_scale"] = float(move_dict.get("power_scale", 1.0)) * lerpf(0.6, 1.4, charge_ratio)
	CombatManager.resolve_player_attack(boosted_move, eid, player_affinity)
	AudioManager.play_sfx(AudioManager.hit_sfx_for_affinity(player_affinity))

	# AoE moves don't expire on first hit; single-target ones do
	var name_lower: String = str(move_dict.get("name", "")).to_lower()
	var is_aoe := false
	for term in ["nova", "storm", "maelstrom", "burst", "eruption", "field"]:
		if term in name_lower:
			is_aoe = true
			break
	if not is_aoe:
		_expire()

func _expire() -> void:
	if _vfx:
		_vfx.emitting = false
	await get_tree().create_timer(1.0).timeout
	queue_free()
