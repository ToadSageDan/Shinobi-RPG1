## WorldMap.gd — Region selection map.
## Shows all five regions with lock/unlock state, level requirement, and
## links into encounter or boss arenas.
extends Control

const REGION_KEYS := [
	"verdant_gate",
	"ashen_cradle",
	"tideglass",
	"stormwall_ridge",
	"sunken_hollow",
]

const REGION_DISPLAY := {
	"verdant_gate":    {"name": "Verdant Gate",    "climate": "Humid Forest Frontier",    "emoji": "🌿"},
	"ashen_cradle":    {"name": "Ashen Cradle",    "climate": "Volcanic Dry Heat",         "emoji": "🔥"},
	"tideglass":       {"name": "Tideglass",       "climate": "Coastal Reef Network",      "emoji": "💧"},
	"stormwall_ridge": {"name": "Stormwall Ridge", "climate": "Alpine Thunder Belt",       "emoji": "💨"},
	"sunken_hollow":   {"name": "Sunken Hollow",   "climate": "Subterranean Toxic",        "emoji": "🌑"},
}

@onready var region_list:    VBoxContainer = $ScrollContainer/RegionList
@onready var detail_panel:   Panel         = $DetailPanel
@onready var detail_name:    Label         = $DetailPanel/VBox/NameLabel
@onready var detail_climate: Label         = $DetailPanel/VBox/ClimateLabel
@onready var detail_boss:    Label         = $DetailPanel/VBox/BossLabel
@onready var detail_level:   Label         = $DetailPanel/VBox/LevelLabel
@onready var detail_status:  Label         = $DetailPanel/VBox/StatusLabel
@onready var enter_btn:      Button        = $DetailPanel/VBox/EnterButton
@onready var boss_btn:       Button        = $DetailPanel/VBox/BossButton
@onready var back_btn:       Button        = $BackButton
@onready var player_label:   Label         = $PlayerInfoBar/PlayerLabel
@onready var shop_btn:       Button        = $ShopButton
@onready var summary_btn:    Button        = $SummaryButton

var _selected_region: String = ""

func _ready() -> void:
	detail_panel.visible = false
	enter_btn.pressed.connect(_on_enter_encounter)
	boss_btn.pressed.connect(_on_enter_boss)
	back_btn.pressed.connect(_on_back)
	shop_btn.pressed.connect(_on_shop)
	summary_btn.pressed.connect(_on_summary)

	_populate_player_bar()
	_build_region_list()
	AudioManager.play_music("music_menu")

func _populate_player_bar() -> void:
	player_label.text = "%s  ·  Lv.%d  ·  Rep: %+d [%s]  ·  Credits: %d" % [
		GameState.player_name,
		GameState.level,
		GameState.reputation,
		GameState.reputation_tier().to_upper(),
		GameState.credits,
	]

func _build_region_list() -> void:
	for child in region_list.get_children():
		child.queue_free()

	for key in REGION_KEYS:
		var region_data := WorldData.get_region(key)
		var info: Dictionary = REGION_DISPLAY.get(key, {})
		var cleared := GameState.is_region_cleared(key)
		var min_lvl: int = region_data.get("minimum_level", 1) if not region_data.is_empty() else 1
		var locked := GameState.level < min_lvl

		var btn := Button.new()
		var status_icon := "✅" if cleared else ("🔒" if locked else "▶")
		btn.text = "%s  %s  %s  (Lv.%d+)" % [
			status_icon,
			info.get("emoji", ""),
			info.get("name", key),
			min_lvl,
		]
		btn.disabled = locked
		btn.custom_minimum_size.y = 52
		if cleared:
			btn.modulate = Color(0.6, 1.0, 0.6)
		elif locked:
			btn.modulate = Color(0.5, 0.5, 0.5)
		btn.pressed.connect(_on_region_selected.bind(key))
		region_list.add_child(btn)

func _on_region_selected(key: String) -> void:
	_selected_region = key
	var region_data := WorldData.get_region(key)
	var info: Dictionary = REGION_DISPLAY.get(key, {})
	var cleared := GameState.is_region_cleared(key)
	var min_lvl: int = region_data.get("minimum_level", 1) if not region_data.is_empty() else 1
	var boss_name: String = region_data.get("boss", "Unknown") if not region_data.is_empty() else "Unknown"

	detail_name.text    = "%s  %s" % [info.get("emoji", ""), info.get("name", key)]
	detail_climate.text = info.get("climate", "")
	detail_boss.text    = "Boss: %s" % boss_name
	detail_level.text   = "Required level: %d  (yours: %d)" % [min_lvl, GameState.level]
	detail_status.text  = "CLEARED" if cleared else ("LOCKED" if GameState.level < min_lvl else "AVAILABLE")
	enter_btn.disabled  = cleared or GameState.level < min_lvl
	boss_btn.disabled   = GameState.level < min_lvl
	detail_panel.visible = true

func _on_enter_encounter() -> void:
	if _selected_region.is_empty():
		return
	GameState.enter_arena(_selected_region)

func _on_enter_boss() -> void:
	if _selected_region.is_empty():
		return
	# Pass a flag via GameState so the arena knows this is a boss run
	# (BaseArena checks is_boss_arena export, but we use scene naming convention)
	var region_data := WorldData.get_region(_selected_region)
	var cleared := GameState.is_region_cleared(_selected_region)
	if cleared:
		detail_status.text = "Already cleared."
		return
	GameState.enter_arena(_selected_region + "_boss")  # convention: boss arenas are separate scenes

func _on_back() -> void:
	GameState.go_to_main_menu()

func _on_shop() -> void:
	get_tree().change_scene_to_file("res://scenes/ui/Shop.tscn")

func _on_summary() -> void:
	get_tree().change_scene_to_file("res://scenes/ui/PlaythroughSummary.tscn")
