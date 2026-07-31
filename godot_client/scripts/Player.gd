## Player.gd — CharacterBody3D player controller.
## Handles: movement, jumping, wall-running, dashing,
##           attack combos, jutsu, lock-on, dodge, and chakra charge.
extends CharacterBody3D

# ── Tuning constants ──────────────────────────────────────────────────────────

const WALK_SPEED       := 6.0
const SPRINT_SPEED     := 10.0
const JUMP_VELOCITY    := 9.0
const GRAVITY          := 20.0
const DASH_SPEED       := 22.0
const DASH_DURATION    := 0.18
const WALL_RUN_SPEED   := 8.5
const WALL_RUN_UPWARD  := 3.0      # vertical bonus while wall-running
const WALL_RUN_MAX_TIME:= 1.4      # seconds before wall run ends
const WALL_JUMP_VEL    := 7.0
const DODGE_STAMINA_COST := 15
const ATTACK_STAMINA_COST := 8

# Wall-run raycast distances
const WALL_RAY_DIST    := 0.75

# ── State ─────────────────────────────────────────────────────────────────────

enum State {IDLE, MOVING, JUMPING, FALLING, DASHING, WALL_RUNNING, ATTACKING, DODGE, HURT, DEAD}

var _state: State = State.IDLE
var _prev_state: State = State.IDLE

# Movement
var _move_dir: Vector3 = Vector3.ZERO
var _dash_timer: float = 0.0
var _dash_dir: Vector3 = Vector3.ZERO
var _double_jump_available: bool = true

# Wall-run
var _wall_run_timer: float = 0.0
var _wall_normal: Vector3 = Vector3.ZERO
var _wall_side: String = ""          # "left" or "right"

# Attack / combo
var _attack_timer: float = 0.0      # window for next combo hit
var _combo_count: int = 0
const COMBO_WINDOW := 0.55
const ATTACK_LOCKOUT := 0.25        # brief freeze at end of attack anim slot

# Lock-on
var _lock_target: Node3D = null
var _lock_target_id: int = -1

# Jutsu charge
var _jutsu_charging: bool = false
var _jutsu_charge_time: float = 0.0
const JUTSU_FULL_CHARGE := 0.8

# Invincibility (dodge i-frames)
var _iframes: float = 0.0
const DODGE_IFRAMES := 0.3

# Move slot → move dictionary (populated from GameState.unlocked_moves)
var _jutsu_slots: Array[Dictionary] = [{}, {}, {}, {}]  # slots 1-4

# ── Node references (assigned in _ready) ─────────────────────────────────────

var _camera: Node3D
var _anim: AnimationPlayer
var _hitbox: Area3D
var _wall_ray_left: RayCast3D
var _wall_ray_right: RayCast3D
var _wall_ray_front: RayCast3D
var _hud: Control

# Signals
signal attacked(move_dict: Dictionary, target_id: int)
signal dodge_performed()
signal jutsu_fired(move_dict: Dictionary, charge_ratio: float)
signal chakra_charged(amount: int)
signal player_died_signal()

func _ready() -> void:
	_camera        = get_node_or_null("CameraArm/Camera3D")
	_anim          = get_node_or_null("AnimationPlayer")
	_hitbox        = get_node_or_null("Hitbox")
	_wall_ray_left  = get_node_or_null("WallRayLeft")
	_wall_ray_right = get_node_or_null("WallRayRight")
	_wall_ray_front = get_node_or_null("WallRayFront")

	# Connect CombatManager signals
	CombatManager.player_took_damage.connect(_on_player_took_damage)
	CombatManager.player_died.connect(_on_player_died)
	InputBuffer.combo_detected.connect(_on_combo_detected)

	# Populate jutsu slots from unlocked moves
	_refresh_jutsu_slots()

func _refresh_jutsu_slots() -> void:
	var attack_moves := GameState.get_moves_by_category("attack")
	var ultimate_moves := GameState.get_moves_by_category("ultimate")
	var all_combat := attack_moves + ultimate_moves
	for i in range(4):
		if i < all_combat.size():
			_jutsu_slots[i] = all_combat[i]
		else:
			_jutsu_slots[i] = {}

# ── Main update ───────────────────────────────────────────────────────────────

func _physics_process(delta: float) -> void:
	if _state == State.DEAD:
		return

	# Tick i-frames
	if _iframes > 0.0:
		_iframes = maxf(0.0, _iframes - delta)

	# Passive stamina regen
	if _state not in [State.ATTACKING, State.DASHING]:
		GameState.recover_stamina(int(GameState.agility * 0.4 * delta))

	# Route to state handlers
	match _state:
		State.IDLE, State.MOVING:
			_handle_movement(delta)
		State.JUMPING, State.FALLING:
			_handle_airborne(delta)
		State.WALL_RUNNING:
			_handle_wall_run(delta)
		State.DASHING:
			_handle_dash(delta)
		State.ATTACKING:
			_handle_attack_state(delta)
		State.DODGE:
			_handle_dodge_state(delta)
		State.HURT:
			pass  # handled by timer in _on_player_took_damage

	# Jutsu charge check (any state except dead/hurt)
	if _state not in [State.DEAD, State.HURT]:
		_handle_jutsu_charge(delta)

	# Attack combo timeout
	if _combo_count > 0:
		_attack_timer -= delta
		if _attack_timer <= 0.0:
			_combo_count = 0

	# Wall run check while airborne
	if _state in [State.JUMPING, State.FALLING]:
		_check_wall_run()

	move_and_slide()

# ── Movement ──────────────────────────────────────────────────────────────────

func _handle_movement(delta: float) -> void:
	var cam_basis := _get_camera_basis()
	var input_dir := _get_input_dir()
	_move_dir = (cam_basis * input_dir).normalized()

	if CombatManager.is_player_rooted():
		_move_dir = Vector3.ZERO

	var speed := SPRINT_SPEED if Input.is_action_pressed("sprint") else WALK_SPEED
	velocity.x = _move_dir.x * speed
	velocity.z = _move_dir.z * speed

	# Apply gravity
	if not is_on_floor():
		velocity.y -= GRAVITY * delta
		_state = State.FALLING
		return

	velocity.y = -0.5  # keep grounded

	if _move_dir.length() > 0.05:
		_state = State.MOVING
		_face_direction(_move_dir)
		_play_anim("run")
		_double_jump_available = true
	else:
		_state = State.IDLE
		_play_anim("idle")

	# Jump
	if Input.is_action_just_pressed("jump") and not CombatManager.is_player_rooted():
		velocity.y = JUMP_VELOCITY
		_state = State.JUMPING
		_play_anim("jump")
		_double_jump_available = true

	# Dodge
	if Input.is_action_just_pressed("dodge") and GameState.stamina >= DODGE_STAMINA_COST:
		_start_dodge()
		return

	# Dash (double-tap direction or sprint+dodge)
	if Input.is_action_just_pressed("dodge") and _move_dir.length() > 0.1:
		_start_dash()
		return

	# Attack
	if Input.is_action_just_pressed("attack") and not CombatManager.is_player_staggered():
		_start_attack("light")

	if Input.is_action_just_pressed("heavy_attack") and not CombatManager.is_player_staggered():
		_start_attack("heavy")

	# Lock-on toggle
	if Input.is_action_just_pressed("lock_on"):
		_toggle_lock_on()

	# Chakra charge
	if Input.is_action_just_pressed("chakra_charge"):
		_do_chakra_charge()

	# Record inputs for combo buffer
	for action in ["attack", "heavy_attack", "dodge", "jutsu_1", "jutsu_2",
				   "jutsu_3", "jutsu_4", "chakra_charge"]:
		if Input.is_action_just_pressed(action):
			InputBuffer.record(action)

func _handle_airborne(delta: float) -> void:
	var cam_basis := _get_camera_basis()
	var input_dir := _get_input_dir()
	var air_dir := (cam_basis * input_dir).normalized()
	velocity.x = lerp(velocity.x, air_dir.x * WALK_SPEED, 0.12)
	velocity.z = lerp(velocity.z, air_dir.z * WALK_SPEED, 0.12)
	velocity.y -= GRAVITY * delta

	if velocity.y < 0.0:
		_state = State.FALLING
		_play_anim("fall")

	if is_on_floor():
		_state = State.IDLE
		_play_anim("land")

	# Double jump
	if Input.is_action_just_pressed("jump") and _double_jump_available:
		velocity.y = JUMP_VELOCITY * 0.85
		_double_jump_available = false
		_play_anim("double_jump")

	# Dodge in air
	if Input.is_action_just_pressed("dodge") and GameState.stamina >= DODGE_STAMINA_COST:
		_start_dodge()

	# Air attack
	if Input.is_action_just_pressed("attack") and not CombatManager.is_player_staggered():
		_start_attack("air_light")

# ── Wall run ──────────────────────────────────────────────────────────────────

func _check_wall_run() -> void:
	if not _wall_ray_left or not _wall_ray_right:
		return
	var on_wall_left  := _wall_ray_left.is_colliding()  and not is_on_floor()
	var on_wall_right := _wall_ray_right.is_colliding() and not is_on_floor()
	if (on_wall_left or on_wall_right) and Input.is_action_pressed("move_forward"):
		_wall_normal = (_wall_ray_left.get_collision_normal()
						if on_wall_left else _wall_ray_right.get_collision_normal())
		_wall_side   = "left" if on_wall_left else "right"
		_state       = State.WALL_RUNNING
		_wall_run_timer = WALL_RUN_MAX_TIME
		_play_anim("wall_run_" + _wall_side)

func _handle_wall_run(delta: float) -> void:
	_wall_run_timer -= delta
	if _wall_run_timer <= 0.0 or is_on_floor():
		_state = State.FALLING
		return

	# Check wall is still there
	var ray := _wall_ray_left if _wall_side == "left" else _wall_ray_right
	if ray and not ray.is_colliding():
		_state = State.FALLING
		return

	# Run along wall
	var run_dir := -_wall_normal.cross(Vector3.UP).normalized()
	velocity = run_dir * WALL_RUN_SPEED + Vector3.UP * WALL_RUN_UPWARD

	# Wall jump
	if Input.is_action_just_pressed("jump"):
		var jump_dir := (_wall_normal + Vector3.UP).normalized()
		velocity = jump_dir * WALL_JUMP_VEL * 1.5
		_state = State.JUMPING
		_double_jump_available = true
		_play_anim("wall_jump")
		return

	# Cancel wall run
	if Input.is_action_just_pressed("dodge"):
		_state = State.FALLING

# ── Dash ──────────────────────────────────────────────────────────────────────

func _start_dash() -> void:
	if GameState.stamina < 20:
		return
	GameState.spend_stamina(20)
	_dash_dir = _move_dir if _move_dir.length() > 0.1 else -global_transform.basis.z
	_dash_timer = DASH_DURATION
	_state = State.DASHING
	_play_anim("dash")
	_iframes = 0.12  # brief i-frames during dash

func _handle_dash(delta: float) -> void:
	velocity = _dash_dir * DASH_SPEED
	velocity.y = 0.0
	_dash_timer -= delta
	if _dash_timer <= 0.0:
		_state = State.IDLE

# ── Dodge ─────────────────────────────────────────────────────────────────────

func _start_dodge() -> void:
	GameState.spend_stamina(DODGE_STAMINA_COST)
	_iframes = DODGE_IFRAMES
	_dash_dir = _move_dir if _move_dir.length() > 0.1 else global_transform.basis.z
	velocity = -_dash_dir * DASH_SPEED * 0.7
	_state = State.DODGE
	_dash_timer = 0.25
	_play_anim("dodge")
	emit_signal("dodge_performed")

func _handle_dodge_state(delta: float) -> void:
	_dash_timer -= delta
	velocity.x = lerp(velocity.x, 0.0, 0.25)
	velocity.z = lerp(velocity.z, 0.0, 0.25)
	if _dash_timer <= 0.0:
		_state = State.IDLE

# ── Attack ────────────────────────────────────────────────────────────────────

func _start_attack(attack_type: String) -> void:
	if GameState.stamina < ATTACK_STAMINA_COST:
		return
	GameState.spend_stamina(ATTACK_STAMINA_COST)
	_combo_count += 1
	_attack_timer = COMBO_WINDOW
	_state = State.ATTACKING

	# Face lock-on target
	if _lock_target:
		var dir := (_lock_target.global_position - global_position)
		dir.y = 0.0
		if dir.length() > 0.01:
			_face_direction(dir.normalized())

	# Choose move based on combo depth and type
	var move_dict := _pick_attack_move(attack_type, _combo_count)
	_play_anim(_attack_anim(attack_type, _combo_count))

	# Fire hitbox after brief startup
	await get_tree().create_timer(0.1).timeout
	if _state == State.ATTACKING:
		_activate_hitbox(move_dict)
		emit_signal("attacked", move_dict, _lock_target_id)

func _handle_attack_state(delta: float) -> void:
	# Slide toward target during attack
	if _lock_target:
		var to_target := _lock_target.global_position - global_position
		to_target.y = 0.0
		if to_target.length() > 1.0:
			velocity = to_target.normalized() * 4.0
	else:
		velocity.x = lerp(velocity.x, 0.0, 0.35)
		velocity.z = lerp(velocity.z, 0.0, 0.35)

	if not is_on_floor():
		velocity.y -= GRAVITY * delta

	# Return to idle after attack lockout
	_attack_timer -= delta
	if _attack_timer <= -ATTACK_LOCKOUT:
		_state = State.IDLE

func _pick_attack_move(attack_type: String, combo: int) -> Dictionary:
	var category := "attack" if attack_type in ["light", "air_light"] else "attack"
	var moves := GameState.get_moves_by_category(category)
	if moves.is_empty():
		return {"name": "Basic Strike", "category": "attack", "power_scale": 1.0, "affinities": [GameState.affinity], "status_effects": []}
	return moves[clampi(combo - 1, 0, moves.size() - 1)]

func _attack_anim(attack_type: String, combo: int) -> String:
	if attack_type == "heavy":
		return "attack_heavy"
	if attack_type == "air_light":
		return "attack_air"
	match combo:
		1: return "attack_1"
		2: return "attack_2"
		3: return "attack_3"
		_: return "attack_1"

func _activate_hitbox(move_dict: Dictionary) -> void:
	if _hitbox:
		_hitbox.monitoring = true
		await get_tree().create_timer(0.12).timeout
		_hitbox.monitoring = false

# ── Jutsu ─────────────────────────────────────────────────────────────────────

func _handle_jutsu_charge(delta: float) -> void:
	if CombatManager.is_player_silenced():
		return
	for i in range(4):
		var action := "jutsu_%d" % (i + 1)
		if Input.is_action_pressed(action) and not _jutsu_slots[i].is_empty():
			_jutsu_charging = true
			_jutsu_charge_time += delta
			_play_anim("jutsu_charge")
			break
		elif Input.is_action_just_released(action) and _jutsu_charging:
			_fire_jutsu(i, _jutsu_charge_time / JUTSU_FULL_CHARGE)
			_jutsu_charging = false
			_jutsu_charge_time = 0.0
			break

func _fire_jutsu(slot: int, charge_ratio: float) -> void:
	var move := _jutsu_slots[slot]
	if move.is_empty():
		return
	var category := move.get("category", "attack")
	if not GameState.can_afford_chakra(category):
		_play_anim("jutsu_fail")
		return
	GameState.spend_chakra(category)
	emit_signal("chakra_changed", GameState.chakra, GameState.chakra_max)
	_play_anim("jutsu_fire")
	emit_signal("jutsu_fired", move, charge_ratio)

# ── Chakra charge ─────────────────────────────────────────────────────────────

func _do_chakra_charge() -> void:
	if _state in [State.ATTACKING, State.DASHING, State.DEAD]:
		return
	var gained := GameState.charge_chakra()
	_play_anim("chakra_charge")
	emit_signal("chakra_changed", GameState.chakra, GameState.chakra_max)
	emit_signal("chakra_charged", gained)

# ── Lock-on ───────────────────────────────────────────────────────────────────

func _toggle_lock_on() -> void:
	if _lock_target:
		_lock_target = null
		_lock_target_id = -1
		return
	# Find nearest living enemy
	var nearest: Node3D = null
	var nearest_dist := 999.0
	var nearest_id := -1
	for enemy_data in CombatManager.living_enemies():
		var enemy_node := get_tree().get_nodes_in_group("enemies").filter(
			func(n: Node) -> bool: return n.get("enemy_id") == enemy_data.id
		)
		if enemy_node.size() > 0:
			var node: Node3D = enemy_node[0]
			var dist := global_position.distance_to(node.global_position)
			if dist < nearest_dist:
				nearest_dist  = dist
				nearest       = node
				nearest_id    = enemy_data.id
	_lock_target    = nearest
	_lock_target_id = nearest_id

# ── Damage reception ──────────────────────────────────────────────────────────

func _on_player_took_damage(amount: int, _source: String) -> void:
	if _iframes > 0.0:
		return
	_play_anim("hurt")
	_state = State.HURT
	await get_tree().create_timer(0.35).timeout
	if _state == State.HURT:
		_state = State.IDLE

func _on_player_died() -> void:
	_state = State.DEAD
	_play_anim("death")
	emit_signal("player_died_signal")

# ── Combo buffer callback ─────────────────────────────────────────────────────

func _on_combo_detected(combo_id: String) -> void:
	match combo_id:
		"launcher_combo":
			_start_attack("heavy")
		"triple_slash":
			_start_attack("light")
		"evade_counter":
			_start_attack("light")
		"dash_slam":
			_start_dash()
			await get_tree().create_timer(0.1).timeout
			_start_attack("heavy")

# ── Helpers ───────────────────────────────────────────────────────────────────

func _get_camera_basis() -> Basis:
	if _camera:
		var b := _camera.global_transform.basis
		b.y = Vector3.ZERO
		return b.orthonormalized()
	return Basis.IDENTITY

func _get_input_dir() -> Vector3:
	var dir := Vector3.ZERO
	dir.x = Input.get_action_strength("move_right") - Input.get_action_strength("move_left")
	dir.z = Input.get_action_strength("move_back")  - Input.get_action_strength("move_forward")
	if dir.length() > 1.0:
		dir = dir.normalized()
	return dir

func _face_direction(dir: Vector3) -> void:
	if dir.length() < 0.01:
		return
	var target_basis := Basis.looking_at(dir, Vector3.UP)
	global_transform.basis = global_transform.basis.slerp(target_basis, 0.3)

func _play_anim(anim_name: String) -> void:
	if _anim and _anim.has_animation(anim_name):
		if _anim.current_animation != anim_name:
			_anim.play(anim_name)
