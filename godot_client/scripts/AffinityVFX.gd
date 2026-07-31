## AffinityVFX.gd — Configures GPUParticles3D nodes for each elemental affinity.
## Call AffinityVFX.configure_particles(node, affinity) after placing a
## GPUParticles3D node in your scene or projectile.  Each affinity gets a
## distinct color gradient, emission shape, and physics feel.
## No texture assets are required — everything uses Godot's built-in gradient
## and primitive emitter shapes.
extends RefCounted
class_name AffinityVFX

# ── Per-affinity preset tables ────────────────────────────────────────────────

## Map of affinity key → visual descriptor dictionary.
const PRESETS: Dictionary = {
	"fire": {
		"color_start":  Color(1.0, 0.5, 0.1, 0.9),
		"color_mid":    Color(1.0, 0.15, 0.0, 0.6),
		"color_end":    Color(0.3, 0.05, 0.0, 0.0),
		"emission_shape": 1,          # sphere
		"emission_radius": 0.12,
		"gravity": Vector3(0.0, 1.5, 0.0),   # rises
		"initial_velocity_min": 1.8,
		"initial_velocity_max": 4.5,
		"angular_velocity": 120.0,
		"scale_min": 0.08,
		"scale_max": 0.22,
		"lifetime": 0.8,
		"amount": 24,
		"spread": 30.0,
	},
	"water": {
		"color_start":  Color(0.2, 0.7, 1.0, 0.85),
		"color_mid":    Color(0.0, 0.45, 0.9, 0.55),
		"color_end":    Color(0.0, 0.2, 0.5, 0.0),
		"emission_shape": 2,          # box
		"emission_radius": 0.10,
		"gravity": Vector3(0.0, -2.0, 0.0),  # falls like droplets
		"initial_velocity_min": 0.6,
		"initial_velocity_max": 2.2,
		"angular_velocity": 60.0,
		"scale_min": 0.06,
		"scale_max": 0.18,
		"lifetime": 1.1,
		"amount": 28,
		"spread": 20.0,
	},
	"earth": {
		"color_start":  Color(0.6, 0.38, 0.18, 1.0),
		"color_mid":    Color(0.45, 0.28, 0.10, 0.75),
		"color_end":    Color(0.25, 0.15, 0.05, 0.0),
		"emission_shape": 2,          # box — like chunks of debris
		"emission_radius": 0.14,
		"gravity": Vector3(0.0, -4.5, 0.0),  # heavy, falls fast
		"initial_velocity_min": 1.0,
		"initial_velocity_max": 3.0,
		"angular_velocity": 200.0,
		"scale_min": 0.10,
		"scale_max": 0.30,
		"lifetime": 0.9,
		"amount": 20,
		"spread": 45.0,
	},
	"wind": {
		"color_start":  Color(0.85, 0.95, 1.0, 0.65),
		"color_mid":    Color(0.60, 0.80, 0.90, 0.35),
		"color_end":    Color(0.4, 0.6, 0.8, 0.0),
		"emission_shape": 0,          # point — streaks outward
		"emission_radius": 0.05,
		"gravity": Vector3(0.0, 0.5, 0.0),
		"initial_velocity_min": 4.0,
		"initial_velocity_max": 8.0,
		"angular_velocity": 40.0,
		"scale_min": 0.04,
		"scale_max": 0.14,
		"lifetime": 0.5,
		"amount": 32,
		"spread": 12.0,
	},
}

# ── Public API ────────────────────────────────────────────────────────────────

## Applies an affinity-specific particle preset to a GPUParticles3D node.
## If the node has no ParticleProcessMaterial, one is created automatically.
static func configure_particles(node: GPUParticles3D, affinity: String) -> void:
	var preset: Dictionary = PRESETS.get(affinity, PRESETS["fire"])

	node.amount    = int(preset["amount"])
	node.lifetime  = float(preset["lifetime"])
	node.emitting  = true
	node.one_shot  = false

	var mat := ParticleProcessMaterial.new()

	# Emission shape
	mat.emission_shape = int(preset["emission_shape"])
	match int(preset["emission_shape"]):
		1:  # sphere
			mat.emission_sphere_radius = float(preset["emission_radius"])
		2:  # box
			var r := float(preset["emission_radius"])
			mat.emission_box_extents = Vector3(r, r, r)

	# Velocity + spread
	mat.initial_velocity_min = float(preset["initial_velocity_min"])
	mat.initial_velocity_max = float(preset["initial_velocity_max"])
	mat.spread               = float(preset["spread"])
	mat.gravity              = preset["gravity"]
	mat.angular_velocity_min = float(preset["angular_velocity"]) * -1.0
	mat.angular_velocity_max = float(preset["angular_velocity"])

	# Scale
	mat.scale_min = float(preset["scale_min"])
	mat.scale_max = float(preset["scale_max"])

	# Color gradient (start → mid → end via color_ramp)
	var gradient := Gradient.new()
	gradient.colors = PackedColorArray([
		preset["color_start"],
		preset["color_mid"],
		preset["color_end"],
	])
	gradient.offsets = PackedFloat32Array([0.0, 0.4, 1.0])
	var ramp_tex := GradientTexture1D.new()
	ramp_tex.gradient = gradient
	mat.color_ramp = ramp_tex

	node.process_material = mat

## One-shot burst (e.g. hit impact) at a specific world position.
## Spawns a temporary GPUParticles3D, plays it once, and removes it.
static func spawn_burst(parent: Node3D, world_pos: Vector3, affinity: String, amount: int = 12) -> void:
	var burst := GPUParticles3D.new()
	burst.global_position = world_pos
	burst.one_shot  = true
	burst.amount    = amount
	burst.lifetime  = 0.7
	burst.explosiveness = 0.95
	parent.add_child(burst)
	configure_particles(burst, affinity)
	burst.emitting = true
	# Auto-free after lifetime + small buffer
	var timer := parent.get_tree().create_timer(burst.lifetime + 0.5)
	timer.timeout.connect(func() -> void: burst.queue_free())
