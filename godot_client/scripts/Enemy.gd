## Enemy.gd — Base enemy AI using a simple state machine.
## States: IDLE → DETECT → CHASE → ATTACK → STAGGERED → RECOVER → DEAD
## Each arena instantiates enemy scenes and registers them with CombatManager.
extends CharacterBody3D

# ── Configuration (set in inspector or via setup()) ───────────────────────────

@export var display_name: String = "Enemy"
@export var enemy_affinity: String = "fire"
@export var base_hp: int = 80
@export var base_power: int = 12
@export var base_defense: int = 8
@export var patrol_radius: float = 6.0
@export var detect_range: float = 14.0
@export var attack_range: float = 2.2
@export var charge_speed: float = 5.5
@export var patrol_speed: float = 2.5
@export var attack_cooldown_time: float = 1.8
@export var learnable_move_name: String = ""   # "" = no learnable move

# ── Runtime ───────────────────────────────────────────────────────────────────

var enemy_id: int = -1
var _hp: int = 0
var _hp_max: int = 0
var _registered: bool = false

enum AIState {IDLE, PATROL, DETECT, CHASE, ATTACK, STAGGERED, RECOVER, DEAD}
var _ai_state: AIState = AIState.IDLE

var _player: CharacterBody3D = null
var _attack_cooldown: float = 0.0
var _patrol_target: Vector3 = Vector3.ZERO
var _origin: Vector3 = Vector3.ZERO
var _stagger_timer: float = 0.0
var _recover_timer: float = 0.0

var _anim: AnimationPlayer
var _hp_bar: ProgressBar     # optional overhead HP bar node

const GRAVITY := 20.0

# Signals
signal died(enemy_id: int, learnable_move: String)

func _ready() -> void:
	add_to_group("enemies")
	_anim    = get_node_or_null("AnimationPlayer")
	_hp_bar  = get_node_or_null("HPBar3D/SubViewport/ProgressBar")
	_origin  = global_position
	_patrol_target = global_position

	# Register with CombatManager
	if not _registered:
		_register()

	# Connect CombatManager death signal to ourselves
	CombatManager.enemy_died.connect(_on_combat_enemy_died)

func setup(id: int, p_name: String, p_affinity: String, p_hp: int,
		   p_power: int, p_defense: int) -> void:
	enemy_id       = id
	display_name   = p_name
	enemy_affinity = p_affinity
	base_hp        = p_hp
	base_power     = p_power
	base_defense   = p_defense
	_register()

func _register() -> void:
	if _registered:
		return
	_registered = true
	enemy_id = CombatManager.register_enemy(
		display_name, base_hp, enemy_affinity,
		base_defense, base_power, false
	)
	_hp     = base_hp
	_hp_max = base_hp

func _physics_process(delta: float) -> void:
	if _ai_state == AIState.DEAD:
		return

	# Sync HP from CombatManager
	var enemy_data := CombatManager.get_enemy(enemy_id)
	if enemy_data:
		_hp = enemy_data.hp
		_update_hp_bar()

	# Apply gravity
	if not is_on_floor():
		velocity.y -= GRAVITY * delta
	else:
		velocity.y = -0.1

	# Find player reference lazily
	if not _player:
		_player = get_tree().get_first_node_in_group("player") as CharacterBody3D

	# Tick cooldowns
	if _attack_cooldown > 0.0:
		_attack_cooldown -= delta
	if _stagger_timer > 0.0:
		_stagger_timer -= delta
		if _stagger_timer <= 0.0 and _ai_state == AIState.STAGGERED:
			_ai_state = AIState.RECOVER

	# State machine
	match _ai_state:
		AIState.IDLE:     _state_idle(delta)
		AIState.PATROL:   _state_patrol(delta)
		AIState.DETECT:   _state_detect()
		AIState.CHASE:    _state_chase(delta)
		AIState.ATTACK:   _state_attack(delta)
		AIState.RECOVER:  _state_recover(delta)

	move_and_slide()

# ── State handlers ────────────────────────────────────────────────────────────

func _state_idle(_delta: float) -> void:
	velocity.x = 0.0
	velocity.z = 0.0
	_play_anim("idle")
	if _player_in_range(detect_range):
		_ai_state = AIState.DETECT
	else:
		# Occasionally patrol
		if randf() < 0.005:
			_pick_patrol_target()
			_ai_state = AIState.PATROL

func _state_patrol(delta: float) -> void:
	_play_anim("walk")
	_move_toward(_patrol_target, patrol_speed, delta)
	if global_position.distance_to(_patrol_target) < 0.5:
		_ai_state = AIState.IDLE
	if _player_in_range(detect_range):
		_ai_state = AIState.DETECT

func _state_detect() -> void:
	_play_anim("alert")
	# Brief pause then chase
	_ai_state = AIState.CHASE

func _state_chase(delta: float) -> void:
	if not _player:
		_ai_state = AIState.IDLE
		return
	_play_anim("run")
	_move_toward(_player.global_position, charge_speed, delta)
	_face_player()
	if _player_in_range(attack_range):
		_ai_state = AIState.ATTACK

func _state_attack(_delta: float) -> void:
	if _attack_cooldown > 0.0:
		_ai_state = AIState.CHASE
		return
	_play_anim("attack")
	_attack_cooldown = attack_cooldown_time
	# Deal damage via CombatManager
	CombatManager.resolve_enemy_attack(enemy_id)
	_ai_state = AIState.RECOVER

func _state_recover(delta: float) -> void:
	_recover_timer += delta
	_play_anim("recover")
	velocity.x = lerp(velocity.x, 0.0, 0.3)
	velocity.z = lerp(velocity.z, 0.0, 0.3)
	if _recover_timer >= 0.6:
		_recover_timer = 0.0
		_ai_state = AIState.CHASE

# ── CombatManager callbacks ───────────────────────────────────────────────────

func _on_combat_enemy_died(dead_id: int) -> void:
	if dead_id != enemy_id:
		return
	_ai_state = AIState.DEAD
	_play_anim("death")
	velocity = Vector3.ZERO
	emit_signal("died", enemy_id, learnable_move_name)
	# Dissolve after delay
	await get_tree().create_timer(2.5).timeout
	queue_free()

# ── Helpers ───────────────────────────────────────────────────────────────────

func _player_in_range(range_dist: float) -> bool:
	if not _player:
		return false
	return global_position.distance_to(_player.global_position) <= range_dist

func _move_toward(target: Vector3, speed: float, _delta: float) -> void:
	var dir := (target - global_position)
	dir.y = 0.0
	if dir.length() > 0.1:
		dir = dir.normalized()
		velocity.x = dir.x * speed
		velocity.z = dir.z * speed

func _face_player() -> void:
	if not _player:
		return
	var dir := _player.global_position - global_position
	dir.y = 0.0
	if dir.length() > 0.01:
		global_transform.basis = global_transform.basis.slerp(
			Basis.looking_at(dir, Vector3.UP), 0.25
		)

func _pick_patrol_target() -> void:
	var angle := randf() * TAU
	_patrol_target = _origin + Vector3(cos(angle), 0.0, sin(angle)) * patrol_radius

func _update_hp_bar() -> void:
	if _hp_bar:
		_hp_bar.value = float(_hp) / float(_hp_max) * 100.0

func _play_anim(anim_name: String) -> void:
	if _anim and _anim.has_animation(anim_name):
		if _anim.current_animation != anim_name:
			_anim.play(anim_name)
