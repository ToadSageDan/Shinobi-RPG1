## QuestWaypoint.gd — A world-space 3D marker that floats above a point in the
## arena and displays the active quest name.  Shown when the player enters a
## region that matches the active quest's target.
##
## Usage:
##   var wp := preload("res://scenes/ui/QuestWaypoint.tscn").instantiate()
##   arena.add_child(wp)
##   wp.global_position = Vector3(x, y + 2.0, z)
##   wp.setup("Q12", "Reach the Hidden Pass")
extends Node3D

# ── Node refs ─────────────────────────────────────────────────────────────────

@onready var label_3d:    Label3D     = $Label3D
@onready var icon_mesh:   MeshInstance3D = $IconMesh
@onready var beam_mesh:   MeshInstance3D = $BeamMesh

# ── Config ────────────────────────────────────────────────────────────────────

const BOB_SPEED   := 1.8      # up/down oscillation frequency
const BOB_AMOUNT  := 0.18     # metres of vertical travel
const SPIN_SPEED  := 90.0     # degrees/s rotation on Y axis
const BEAM_HEIGHT := 6.0      # how tall the beacon beam is

var quest_id:   String = ""
var quest_name: String = ""
var _time:      float  = 0.0
var _base_y:    float  = 0.0

# ── Lifecycle ─────────────────────────────────────────────────────────────────

func _ready() -> void:
	_base_y = global_position.y
	_apply_visuals()

func setup(p_quest_id: String, p_quest_name: String) -> void:
	quest_id   = p_quest_id
	quest_name = p_quest_name
	if is_node_ready():
		_apply_visuals()

func _apply_visuals() -> void:
	if label_3d:
		label_3d.text       = "[ %s ]\n%s" % [quest_id, quest_name]
		label_3d.font_size  = 18
		label_3d.modulate   = Color(0.95, 0.85, 0.4, 1.0)
		label_3d.billboard  = BaseMaterial3D.BILLBOARD_ENABLED
		label_3d.position.y = 1.2

	if icon_mesh:
		# Diamond / rhombus shape using a rotated BoxMesh as a placeholder icon
		var box := BoxMesh.new()
		box.size = Vector3(0.3, 0.3, 0.3)
		icon_mesh.mesh = box
		icon_mesh.position.y = 0.5
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(0.95, 0.85, 0.35, 1.0)
		mat.emission_enabled = true
		mat.emission = Color(1.0, 0.9, 0.3, 1.0)
		mat.emission_energy_multiplier = 1.4
		icon_mesh.set_surface_override_material(0, mat)

	if beam_mesh:
		# Thin vertical cylinder as a beacon beam
		var cyl := CylinderMesh.new()
		cyl.top_radius    = 0.04
		cyl.bottom_radius = 0.04
		cyl.height        = BEAM_HEIGHT
		beam_mesh.mesh = cyl
		beam_mesh.position.y = BEAM_HEIGHT * 0.5 - 0.5
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(0.95, 0.85, 0.35, 0.35)
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat.emission_enabled = true
		mat.emission = Color(1.0, 0.9, 0.3, 1.0)
		mat.emission_energy_multiplier = 0.6
		beam_mesh.set_surface_override_material(0, mat)

func _process(delta: float) -> void:
	_time += delta
	# Bob up and down
	var offset_y := sin(_time * BOB_SPEED) * BOB_AMOUNT
	global_position.y = _base_y + offset_y
	# Rotate icon on Y
	if icon_mesh:
		icon_mesh.rotation_degrees.y += SPIN_SPEED * delta
		icon_mesh.rotation_degrees.x += SPIN_SPEED * 0.5 * delta
