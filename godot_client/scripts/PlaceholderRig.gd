## PlaceholderRig.gd — Procedural placeholder character mesh for Player and Enemy.
## Builds a capsule body + sphere head + limb indicators from primitive meshes
## so the game is fully playable without importing Mixamo or any art assets.
## Drop this as a child of the CharacterBody3D / Enemy node and call setup().
##
## When you import a real Mixamo FBX rig:
##   1. Delete this node from the scene.
##   2. Add the imported MeshInstance3D + AnimationPlayer under the character root.
##   3. The character scripts call _play_anim(name) which guards with has_animation(),
##      so they are forward-compatible and require no other code changes.
extends Node3D

@export var affinity_color: Color = Color(0.6, 0.7, 0.8, 1.0)
@export var character_height: float = 1.8

# ── Internal nodes built at runtime ──────────────────────────────────────────

var _body_mesh:    MeshInstance3D
var _head_mesh:    MeshInstance3D
var _left_arm:     MeshInstance3D
var _right_arm:    MeshInstance3D
var _left_leg:     MeshInstance3D
var _right_leg:    MeshInstance3D

# Simple procedural animation state
var _anim_state: String = "idle"
var _anim_time:  float  = 0.0

func _ready() -> void:
	_build_mesh()

## Called by the parent character script to set an affinity-tinted look.
func setup(p_affinity: String) -> void:
	affinity_color = _affinity_to_color(p_affinity)
	if _body_mesh:
		_apply_material(_body_mesh, affinity_color)

# ── Mesh construction ─────────────────────────────────────────────────────────

func _build_mesh() -> void:
	var half_h := character_height * 0.5
	var torso_h := character_height * 0.55
	var head_r  := character_height * 0.13

	# Body (capsule)
	_body_mesh = _make_mesh_node("Body", CapsuleMesh.new())
	(_body_mesh.mesh as CapsuleMesh).radius = character_height * 0.16
	(_body_mesh.mesh as CapsuleMesh).height = torso_h
	_body_mesh.position.y = half_h
	_apply_material(_body_mesh, affinity_color)
	add_child(_body_mesh)

	# Head (sphere)
	_head_mesh = _make_mesh_node("Head", SphereMesh.new())
	(_head_mesh.mesh as SphereMesh).radius = head_r
	_head_mesh.position.y = half_h + torso_h * 0.55 + head_r
	_apply_material(_head_mesh, affinity_color.lightened(0.15))
	add_child(_head_mesh)

	# Arms (cylinders)
	_left_arm  = _build_limb("LeftArm",  Vector3(-character_height * 0.24, half_h + torso_h * 0.2, 0))
	_right_arm = _build_limb("RightArm", Vector3( character_height * 0.24, half_h + torso_h * 0.2, 0))

	# Legs (cylinders)
	_left_leg  = _build_limb("LeftLeg",  Vector3(-character_height * 0.10, half_h - torso_h * 0.35, 0),
	                          character_height * 0.06, character_height * 0.42)
	_right_leg = _build_limb("RightLeg", Vector3( character_height * 0.10, half_h - torso_h * 0.35, 0),
	                          character_height * 0.06, character_height * 0.42)

## Changes the displayed animation state (called by the character controller).
func play_placeholder_anim(anim_name: String) -> void:
	_anim_state = anim_name
	_anim_time  = 0.0

func _process(delta: float) -> void:
	_anim_time += delta
	_animate(delta)

func _animate(_delta: float) -> void:
	if not is_instance_valid(_head_mesh):
		return
	match _anim_state:
		"idle":
			_body_mesh.position.y = character_height * 0.5 + sin(_anim_time * 1.5) * 0.02
		"run":
			if _left_leg and _right_leg:
				_left_leg.rotation_degrees.x  =  sin(_anim_time * 8.0) * 25.0
				_right_leg.rotation_degrees.x = -sin(_anim_time * 8.0) * 25.0
				_left_arm.rotation_degrees.x  = -sin(_anim_time * 8.0) * 20.0
				_right_arm.rotation_degrees.x =  sin(_anim_time * 8.0) * 20.0
		"jump", "double_jump":
			if _left_leg and _right_leg:
				_left_leg.rotation_degrees.x  = -30.0
				_right_leg.rotation_degrees.x = -30.0
		"fall":
			if _left_leg and _right_leg:
				_left_leg.rotation_degrees.x  = 20.0
				_right_leg.rotation_degrees.x = 20.0
		"attack_1", "attack_2", "attack_3", "attack_heavy":
			_right_arm.rotation_degrees.x = sin(_anim_time * 18.0) * 45.0
		"hurt":
			_body_mesh.rotation_degrees.z = sin(_anim_time * 25.0) * 8.0
		"death":
			_body_mesh.rotation_degrees.x = min(_anim_time * 80.0, 90.0)
		"dash":
			_body_mesh.rotation_degrees.x = -15.0
		_:
			# Reset to neutral pose for any unmapped animation
			if _left_leg:
				_left_leg.rotation_degrees  = Vector3.ZERO
				_right_leg.rotation_degrees = Vector3.ZERO
				_left_arm.rotation_degrees  = Vector3.ZERO
				_right_arm.rotation_degrees = Vector3.ZERO

# ── Helpers ───────────────────────────────────────────────────────────────────

func _build_limb(node_name: String, pos: Vector3, radius: float = 0.0, height: float = 0.0) -> MeshInstance3D:
	var r := radius  if radius > 0.0 else character_height * 0.07
	var h := height  if height > 0.0 else character_height * 0.35
	var node := _make_mesh_node(node_name, CylinderMesh.new())
	(node.mesh as CylinderMesh).top_radius    = r
	(node.mesh as CylinderMesh).bottom_radius = r
	(node.mesh as CylinderMesh).height        = h
	node.position = pos
	_apply_material(node, affinity_color.darkened(0.1))
	add_child(node)
	return node

func _make_mesh_node(node_name: String, mesh: Mesh) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = node_name
	mi.mesh = mesh
	return mi

func _apply_material(node: MeshInstance3D, color: Color) -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness    = 0.7
	mat.metallic     = 0.1
	node.set_surface_override_material(0, mat)

func _affinity_to_color(affinity: String) -> Color:
	match affinity:
		"fire":  return Color(0.9, 0.35, 0.15, 1.0)
		"water": return Color(0.2, 0.55, 0.9, 1.0)
		"earth": return Color(0.45, 0.32, 0.18, 1.0)
		"wind":  return Color(0.75, 0.9, 0.95, 1.0)
		_:       return Color(0.6, 0.65, 0.7, 1.0)
