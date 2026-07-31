## GameOver.gd — Death/defeat screen.
## Shows run stats and offers Try Again, Load Save, or Quit to Menu.
extends Control

@onready var title_label:    Label = $Panel/VBox/TitleLabel
@onready var stats_label:    Label = $Panel/VBox/StatsLabel
@onready var retry_btn:      Button = $Panel/VBox/Buttons/RetryButton
@onready var load_btn:       Button = $Panel/VBox/Buttons/LoadButton
@onready var menu_btn:       Button = $Panel/VBox/Buttons/MenuButton

func _ready() -> void:
	hide()
	retry_btn.pressed.connect(_on_retry)
	load_btn.pressed.connect(_on_load)
	menu_btn.pressed.connect(_on_menu)
	# Disable load button if no save exists
	load_btn.disabled = not GameState.has_save()

func populate_stats() -> void:
	title_label.text = "☠  DEFEATED"
	var lines: Array[String] = [
		"Shinobi: %s  (Lv.%d)" % [GameState.player_name, GameState.level],
		"Regions cleared: %d" % GameState.cleared_regions.size(),
		"Trophies: %d" % GameState.trophies.size(),
		"Reputation: %+d  [%s]" % [GameState.reputation, GameState.reputation_tier().to_upper()],
		"",
		"Kills: %d  |  Charm: %d  |  Stealth: %d  |  Evasion: %d" % [
			GameState.encounter_outcomes.get("kill", 0),
			GameState.encounter_outcomes.get("charm", 0),
			GameState.encounter_outcomes.get("stealth", 0),
			GameState.encounter_outcomes.get("evasion", 0),
		],
	]
	stats_label.text = "\n".join(lines)

func _on_retry() -> void:
	get_tree().paused = false
	CombatManager.end_combat()
	# Reload the current scene fresh (respawn at start of arena)
	get_tree().reload_current_scene()

func _on_load() -> void:
	get_tree().paused = false
	CombatManager.end_combat()
	if GameState.load_game():
		GameState.return_to_world_map()
	else:
		GameState.go_to_main_menu()

func _on_menu() -> void:
	get_tree().paused = false
	CombatManager.end_combat()
	GameState.go_to_main_menu()
