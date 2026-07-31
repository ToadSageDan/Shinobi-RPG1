## HUD.gd — In-game HUD: HP/Chakra/Stamina bars, status effects row,
##           enemy HP bars, combo popups, level-up flash, boss phase banner.
extends Control

# ── Node references ───────────────────────────────────────────────────────────

@onready var hp_bar:       ProgressBar = $VBox/PlayerPanel/HPRow/HPBar
@onready var chakra_bar:   ProgressBar = $VBox/PlayerPanel/ChakraRow/ChakraBar
@onready var stamina_bar:  ProgressBar = $VBox/PlayerPanel/StaminaRow/StaminaBar
@onready var hp_label:     Label       = $VBox/PlayerPanel/HPRow/HPLabel
@onready var chakra_label: Label       = $VBox/PlayerPanel/ChakraRow/ChakraLabel
@onready var stamina_label:Label       = $VBox/PlayerPanel/StaminaRow/StaminaLabel
@onready var level_label:  Label       = $VBox/PlayerPanel/InfoRow/LevelLabel
@onready var rep_label:    Label       = $VBox/PlayerPanel/InfoRow/RepLabel
@onready var quest_label:  Label       = $VBox/PlayerPanel/QuestLabel
@onready var status_row:   HBoxContainer = $VBox/StatusRow
@onready var combo_popup:  Label       = $ComboPopup
@onready var boss_banner:  Label       = $BossBanner
@onready var taunt_label:  Label       = $TauntLabel
@onready var damage_vignette: ColorRect = $DamageVignette
@onready var hit_flash:    ColorRect   = $HitFlash
@onready var enemy_hp_container: VBoxContainer = $EnemyHPContainer

# Damage number pool
const MAX_DAMAGE_LABELS := 8
var _dmg_labels: Array[Label] = []
var _dmg_index: int = 0

# Status effect icon map
const STATUS_ICONS := {
	"burn":        "🔥", "bleed":      "🩸", "chill":     "❄️",
	"drench":      "💧", "crack_armor":"🛡",  "stagger":   "💥",
	"blind":       "👁",  "silence":    "🔇", "root":      "🌿",
	"fear":        "💀",
}

# Enemy HP bars keyed by enemy_id
var _enemy_hp_bars: Dictionary = {}  # enemy_id → ProgressBar

func _ready() -> void:
	_setup_damage_pool()
	combo_popup.visible = false
	boss_banner.visible = false
	taunt_label.visible = false
	damage_vignette.color = Color(0.8, 0.0, 0.0, 0.0)
	hit_flash.color = Color(1.0, 1.0, 1.0, 0.0)
	_refresh_player_bars()

func _process(_delta: float) -> void:
	_refresh_player_bars()
	_update_status_icons()

# ── Player bar refresh ────────────────────────────────────────────────────────

func _refresh_player_bars() -> void:
	hp_bar.max_value     = GameState.hp_max
	hp_bar.value         = GameState.hp
	chakra_bar.max_value = GameState.chakra_max
	chakra_bar.value     = GameState.chakra
	stamina_bar.max_value = GameState.stamina_max
	stamina_bar.value    = GameState.stamina

	hp_label.text      = "%d / %d" % [GameState.hp, GameState.hp_max]
	chakra_label.text  = "%d / %d" % [GameState.chakra, GameState.chakra_max]
	stamina_label.text = "%d / %d" % [GameState.stamina, GameState.stamina_max]
	level_label.text   = "Lv.%d" % GameState.level
	rep_label.text     = "Rep: %+d  [%s]" % [GameState.reputation,
											   GameState.reputation_tier().to_upper()]

# ── Called by BaseArena ───────────────────────────────────────────────────────

func update_player_hp(hp: int, hp_max: int) -> void:
	hp_bar.max_value = hp_max
	hp_bar.value     = hp
	hp_label.text    = "%d / %d" % [hp, hp_max]

func update_enemy_hp(enemy_id: int, _damage: int) -> void:
	var data := CombatManager.get_enemy(enemy_id)
	if not data:
		return
	if enemy_id not in _enemy_hp_bars:
		_create_enemy_hp_bar(enemy_id, data.display_name, data.hp_max)
	var bar: ProgressBar = _enemy_hp_bars.get(enemy_id)
	if bar:
		bar.value = float(data.hp) / float(data.hp_max) * 100.0

func show_damage_number(amount: int, enemy_data) -> void:
	if _dmg_labels.is_empty():
		return
	var lbl: Label = _dmg_labels[_dmg_index]
	_dmg_index = (_dmg_index + 1) % MAX_DAMAGE_LABELS
	lbl.text = "-%d" % amount
	lbl.visible = true
	var tween := create_tween()
	tween.tween_property(lbl, "position:y", lbl.position.y - 40.0, 0.7)
	tween.parallel().tween_property(lbl, "modulate:a", 0.0, 0.7)
	tween.tween_callback(func() -> void:
		lbl.visible = false
		lbl.modulate.a = 1.0
	)

func show_damage_flash() -> void:
	damage_vignette.color.a = 0.35
	var tween := create_tween()
	tween.tween_property(damage_vignette, "color:a", 0.0, 0.6)

func flash_hit_indicator(target: String) -> void:
	if target == "player":
		show_damage_flash()
		return
	hit_flash.color.a = 0.25
	var tween := create_tween()
	tween.tween_property(hit_flash, "color:a", 0.0, 0.2)

func show_combo_popup(label_text: String, bonus: int) -> void:
	combo_popup.text = "%s  +%d" % [label_text, bonus]
	combo_popup.visible = true
	var tween := create_tween()
	tween.tween_interval(1.2)
	tween.tween_callback(func() -> void: combo_popup.visible = false)

func show_boss_taunt(line: String) -> void:
	taunt_label.text = '"%s"' % line
	taunt_label.visible = true
	var tween := create_tween()
	tween.tween_interval(3.5)
	tween.tween_callback(func() -> void: taunt_label.visible = false)

func show_phase_transition(phase: int) -> void:
	boss_banner.text = "⚡  PHASE %d" % phase
	boss_banner.visible = true
	var tween := create_tween()
	tween.tween_interval(2.0)
	tween.tween_callback(func() -> void: boss_banner.visible = false)

func show_level_up(new_level: int) -> void:
	boss_banner.text = "✦  LEVEL UP!  Now Lv.%d" % new_level
	boss_banner.visible = true
	var tween := create_tween()
	tween.tween_interval(2.5)
	tween.tween_callback(func() -> void: boss_banner.visible = false)

func show_victory(boss_name: String, approach: String) -> void:
	boss_banner.text = "🏆  VICTORY  —  %s  [%s]" % [boss_name, approach.to_upper()]
	boss_banner.modulate = Color(1.0, 0.9, 0.2, 1.0)
	boss_banner.visible = true

func show_move_learned(move_name: String) -> void:
	show_combo_popup("Learned: " + move_name, 0)

func show_level_gate(required: int, current: int) -> void:
	boss_banner.text = "⚠  Level %d required  (your level: %d)" % [required, current]
	boss_banner.visible = true

func update_status_effects() -> void:
	_update_status_icons()

func set_active_quest(quest_title: String) -> void:
	quest_label.text = "◈ " + quest_title if not quest_title.is_empty() else ""

# ── Status icons ──────────────────────────────────────────────────────────────

func _update_status_icons() -> void:
	for child in status_row.get_children():
		child.queue_free()
	for effect_name in GameState.active_status_effects.keys():
		var data: Dictionary = GameState.active_status_effects[effect_name]
		var icon := STATUS_ICONS.get(effect_name, "•")
		var stacks: int = data.get("stacks", 1)
		var lbl := Label.new()
		lbl.text = "%s×%d" % [icon, stacks]
		lbl.add_theme_font_size_override("font_size", 16)
		status_row.add_child(lbl)

# ── Enemy HP bars ─────────────────────────────────────────────────────────────

func _create_enemy_hp_bar(enemy_id: int, name: String, hp_max: int) -> void:
	var container := HBoxContainer.new()
	var label := Label.new()
	label.text = name
	label.custom_minimum_size.x = 120
	var bar := ProgressBar.new()
	bar.max_value = 100
	bar.value = 100
	bar.custom_minimum_size = Vector2(180, 16)
	# Style it red
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.7, 0.1, 0.1)
	bar.add_theme_stylebox_override("fill", style)
	container.add_child(label)
	container.add_child(bar)
	enemy_hp_container.add_child(container)
	_enemy_hp_bars[enemy_id] = bar

# ── Damage label pool ─────────────────────────────────────────────────────────

func _setup_damage_pool() -> void:
	for i in range(MAX_DAMAGE_LABELS):
		var lbl := Label.new()
		lbl.visible = false
		lbl.add_theme_font_size_override("font_size", 22)
		lbl.add_theme_color_override("font_color", Color(1.0, 0.9, 0.2))
		lbl.position = Vector2(900, 400)
		add_child(lbl)
		_dmg_labels.append(lbl)
