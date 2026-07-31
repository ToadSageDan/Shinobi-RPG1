## BiomeTerrain.gd — Procedural placeholder terrain for all five biomes.
## Builds ground, boundary walls, and scatter objects using primitive meshes
## with biome-appropriate colors. No art assets needed.
## Replace the generated geometry with real terrain meshes when available.
## See ASSETS_GUIDE.md for free environment asset sources.
extends RefCounted
class_name BiomeTerrain

# ── Biome color palettes ──────────────────────────────────────────────────────

const BIOMES: Dictionary = {
	"verdant_gate": {
		"ground":      Color(0.20, 0.42, 0.15, 1),   # deep green
		"wall":        Color(0.18, 0.35, 0.12, 1),
		"scatter":     Color(0.12, 0.30, 0.10, 1),
		"light_color": Color(0.88, 1.00, 0.72, 1),
		"light_energy": 1.1,
		"scatter_label": "forest trees",
	},
	"ashen_cradle": {
		"ground":      Color(0.25, 0.18, 0.14, 1),   # dark ash
		"wall":        Color(0.35, 0.20, 0.10, 1),
		"scatter":     Color(0.55, 0.15, 0.05, 1),   # lava rock
		"light_color": Color(1.00, 0.60, 0.30, 1),
		"light_energy": 1.3,
		"scatter_label": "volcanic rocks",
	},
	"tideglass": {
		"ground":      Color(0.08, 0.32, 0.50, 1),   # ocean blue
		"wall":        Color(0.10, 0.25, 0.42, 1),
		"scatter":     Color(0.15, 0.55, 0.65, 1),   # reef teal
		"light_color": Color(0.72, 0.92, 1.00, 1),
		"light_energy": 1.0,
		"scatter_label": "reef pillars",
	},
	"stormwall_ridge": {
		"ground":      Color(0.55, 0.55, 0.58, 1),   # grey stone
		"wall":        Color(0.40, 0.42, 0.45, 1),
		"scatter":     Color(0.70, 0.72, 0.75, 1),   # lighter stone
		"light_color": Color(0.80, 0.85, 1.00, 1),
		"light_energy": 0.9,
		"scatter_label": "stone boulders",
	},
	"sunken_hollow": {
		"ground":      Color(0.12, 0.10, 0.08, 1),   # dark cave floor
		"wall":        Color(0.20, 0.15, 0.10, 1),
		"scatter":     Color(0.15, 0.35, 0.20, 1),   # bioluminescent moss
		"light_color": Color(0.45, 0.70, 0.55, 1),   # eerie green
		"light_energy": 0.7,
		"scatter_label": "cave stalagmites",
	},
}

# Arena ground half-dimensions
const GROUND_W := 20.0
const GROUND_D := 20.0
const WALL_H   := 4.0
const WALL_T   := 0.6

# ── Public API ────────────────────────────────────────────────────────────────

## Builds placeholder terrain geometry under `parent_node`.
## Replaces the empty GroundMesh/GroundCollision placeholders.
static func build(parent_node: Node3D, biome_key: String) -> void:
	var palette: Dictionary = BIOMES.get(biome_key, BIOMES["verdant_gate"])

	_build_ground(parent_node, palette)
	_build_boundary_walls(parent_node, palette)
	_build_scatter(parent_node, palette, biome_key)
	_update_directional_light(parent_node, palette)

# ── Ground ────────────────────────────────────────────────────────────────────

static func _build_ground(parent: Node3D, palette: Dictionary) -> void:
	# Replace or augment the existing GroundMesh node
	var ground_node: Node3D = parent.get_node_or_null("Ground")
	if not ground_node:
		ground_node = StaticBody3D.new()
		ground_node.name = "Ground"
		parent.add_child(ground_node)

	var mesh_node: MeshInstance3D = ground_node.get_node_or_null("GroundMesh")
	if not mesh_node:
		mesh_node = MeshInstance3D.new()
		mesh_node.name = "GroundMesh"
		ground_node.add_child(mesh_node)

	var box := BoxMesh.new()
	box.size = Vector3(GROUND_W * 2.0, 0.3, GROUND_D * 2.0)
	mesh_node.mesh = box
	mesh_node.position = Vector3(0.0, -0.15, 0.0)
	mesh_node.set_surface_override_material(0, _mat(palette["ground"]))

	var col_node: CollisionShape3D = ground_node.get_node_or_null("GroundCollision")
	if not col_node:
		col_node = CollisionShape3D.new()
		col_node.name = "GroundCollision"
		ground_node.add_child(col_node)
	var shape := BoxShape3D.new()
	shape.size = Vector3(GROUND_W * 2.0, 0.3, GROUND_D * 2.0)
	col_node.shape = shape
	col_node.position = Vector3(0.0, -0.15, 0.0)

# ── Boundary walls ────────────────────────────────────────────────────────────

static func _build_boundary_walls(parent: Node3D, palette: Dictionary) -> void:
	var walls_root: Node3D = parent.get_node_or_null("Walls")
	if not walls_root:
		walls_root = Node3D.new()
		walls_root.name = "Walls"
		parent.add_child(walls_root)
	# Clear old wall children
	for c in walls_root.get_children():
		c.queue_free()

	var wall_defs := [
		[Vector3(0,              WALL_H * 0.5,  GROUND_D + WALL_T * 0.5), Vector3(GROUND_W * 2.0 + WALL_T * 2.0, WALL_H, WALL_T)],
		[Vector3(0,              WALL_H * 0.5, -GROUND_D - WALL_T * 0.5), Vector3(GROUND_W * 2.0 + WALL_T * 2.0, WALL_H, WALL_T)],
		[Vector3( GROUND_W + WALL_T * 0.5, WALL_H * 0.5, 0),              Vector3(WALL_T, WALL_H, GROUND_D * 2.0 + WALL_T * 2.0)],
		[Vector3(-GROUND_W - WALL_T * 0.5, WALL_H * 0.5, 0),              Vector3(WALL_T, WALL_H, GROUND_D * 2.0 + WALL_T * 2.0)],
	]
	var wall_names := ["WallN", "WallS", "WallE", "WallW"]
	for i in range(wall_defs.size()):
		var sb := StaticBody3D.new()
		sb.name = wall_names[i]
		walls_root.add_child(sb)

		var mi := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = wall_defs[i][1]
		mi.mesh = bm
		mi.position = wall_defs[i][0]
		mi.set_surface_override_material(0, _mat(palette["wall"]))
		sb.add_child(mi)

		var cs := CollisionShape3D.new()
		var bs := BoxShape3D.new()
		bs.size = wall_defs[i][1]
		cs.shape = bs
		cs.position = wall_defs[i][0]
		sb.add_child(cs)

# ── Scatter objects ───────────────────────────────────────────────────────────

static func _build_scatter(parent: Node3D, palette: Dictionary, biome_key: String) -> void:
	var scatter_root := Node3D.new()
	scatter_root.name = "ScatterObjects"
	parent.add_child(scatter_root)

	var scatter_count := 12
	var rng := RandomNumberGenerator.new()
	rng.seed = biome_key.hash()

	for i in range(scatter_count):
		var angle := rng.randf() * TAU
		var dist  := rng.randf_range(5.0, GROUND_W - 2.0)
		var pos   := Vector3(cos(angle) * dist, 0.0, sin(angle) * dist)

		match biome_key:
			"verdant_gate":    _add_tree(scatter_root, pos, palette, rng)
			"ashen_cradle":    _add_rock(scatter_root, pos, palette, rng)
			"tideglass":       _add_pillar(scatter_root, pos, palette, rng)
			"stormwall_ridge": _add_rock(scatter_root, pos, palette, rng)
			"sunken_hollow":   _add_stalagmite(scatter_root, pos, palette, rng)
			_:                 _add_rock(scatter_root, pos, palette, rng)

static func _add_tree(parent: Node3D, pos: Vector3, palette: Dictionary, rng: RandomNumberGenerator) -> void:
	var h := rng.randf_range(1.8, 3.5)
	var trunk := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.12; cyl.bottom_radius = 0.18; cyl.height = h
	trunk.mesh = cyl
	trunk.position = pos + Vector3(0, h * 0.5, 0)
	trunk.set_surface_override_material(0, _mat(Color(0.30, 0.18, 0.08)))
	parent.add_child(trunk)
	# Canopy sphere
	var canopy := MeshInstance3D.new()
	var sph := SphereMesh.new()
	sph.radius = rng.randf_range(0.6, 1.2)
	canopy.mesh = sph
	canopy.position = pos + Vector3(0, h + sph.radius * 0.7, 0)
	canopy.set_surface_override_material(0, _mat(palette["scatter"]))
	parent.add_child(canopy)

static func _add_rock(parent: Node3D, pos: Vector3, palette: Dictionary, rng: RandomNumberGenerator) -> void:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	var sz := rng.randf_range(0.4, 1.2)
	bm.size = Vector3(sz, sz * rng.randf_range(0.5, 1.3), sz * rng.randf_range(0.6, 1.1))
	mi.mesh = bm
	mi.position = pos + Vector3(0, bm.size.y * 0.5, 0)
	mi.rotation_degrees.y = rng.randf_range(0, 360)
	mi.set_surface_override_material(0, _mat(palette["scatter"]))
	parent.add_child(mi)

static func _add_pillar(parent: Node3D, pos: Vector3, palette: Dictionary, rng: RandomNumberGenerator) -> void:
	var h := rng.randf_range(1.0, 3.0)
	var mi := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = rng.randf_range(0.15, 0.35)
	cyl.bottom_radius = cyl.top_radius * rng.randf_range(0.8, 1.4)
	cyl.height = h
	mi.mesh = cyl
	mi.position = pos + Vector3(0, h * 0.5, 0)
	mi.set_surface_override_material(0, _mat(palette["scatter"]))
	parent.add_child(mi)

static func _add_stalagmite(parent: Node3D, pos: Vector3, palette: Dictionary, rng: RandomNumberGenerator) -> void:
	var h := rng.randf_range(0.5, 2.0)
	var mi := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius    = 0.02
	cyl.bottom_radius = rng.randf_range(0.1, 0.25)
	cyl.height        = h
	mi.mesh = cyl
	mi.position = pos + Vector3(0, h * 0.5, 0)
	mi.set_surface_override_material(0, _mat(palette["scatter"]))
	parent.add_child(mi)

# ── Directional light tint ────────────────────────────────────────────────────

static func _update_directional_light(parent: Node3D, palette: Dictionary) -> void:
	var light: DirectionalLight3D = parent.get_node_or_null("DirectionalLight3D")
	if light:
		light.light_color  = palette["light_color"]
		light.light_energy = float(palette["light_energy"])

# ── Material helper ───────────────────────────────────────────────────────────

static func _mat(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness    = 0.85
	m.metallic     = 0.0
	return m
