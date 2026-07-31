## PlayerCamera.gd — Third-person camera with lock-on orbit.
## Attach to a SpringArm3D node parented to the Player.
extends SpringArm3D

# ── Tuning ────────────────────────────────────────────────────────────────────

const FREE_SENSITIVITY  := 0.003    # mouse look sensitivity
const LOCK_LERP_SPEED   := 6.0      # how fast camera snaps to lock-on target
const PITCH_MIN         := -0.7     # radians
const PITCH_MAX         := 0.5
const FREE_ARM_LENGTH   := 5.5      # default camera distance
const LOCK_ARM_LENGTH   := 6.5      # slightly zoomed out during lock-on

# ── State ─────────────────────────────────────────────────────────────────────

var _yaw: float   = 0.0
var _pitch: float = -0.25
var _locked_target: Node3D = null

var _player: CharacterBody3D

func _ready() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	_player = get_parent()
	spring_length = FREE_ARM_LENGTH

func _unhandled_input(event: InputEvent) -> void:
	if _locked_target:
		return
	if event is InputEventMouseMotion:
		var motion: InputEventMouseMotion = event
		_yaw   -= motion.relative.x * FREE_SENSITIVITY
		_pitch -= motion.relative.y * FREE_SENSITIVITY
		_pitch  = clampf(_pitch, PITCH_MIN, PITCH_MAX)

func _process(delta: float) -> void:
	if _locked_target and is_instance_valid(_locked_target):
		_orbit_toward_target(delta)
	else:
		_locked_target = null
		spring_length   = lerpf(spring_length, FREE_ARM_LENGTH, 5.0 * delta)
		rotation.y = _yaw
		rotation.x = _pitch

func _orbit_toward_target(delta: float) -> void:
	if not _player:
		return
	# Point the spring arm toward the target
	var to_target := _locked_target.global_position - _player.global_position
	to_target.y += 0.8   # bias upward so target stays visible
	var desired_basis := Basis.looking_at(-to_target.normalized(), Vector3.UP)
	var target_euler := desired_basis.get_euler()
	_yaw   = lerp_angle(_yaw,   target_euler.y, LOCK_LERP_SPEED * delta)
	_pitch = lerp_angle(_pitch, target_euler.x, LOCK_LERP_SPEED * delta)
	_pitch = clampf(_pitch, PITCH_MIN, PITCH_MAX)
	rotation.y = _yaw
	rotation.x = _pitch
	spring_length = lerpf(spring_length, LOCK_ARM_LENGTH, 4.0 * delta)

# ── API ───────────────────────────────────────────────────────────────────────

func set_lock_target(target: Node3D) -> void:
	_locked_target = target

func clear_lock() -> void:
	_locked_target = null

func get_forward_direction() -> Vector3:
	var basis: Basis = global_transform.basis
	return -basis.z

func set_free_camera_on_pause(paused: bool) -> void:
	if paused:
		Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	else:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
