## MainMenu.gd — Title screen: New Game, Continue, Options, Quit.
extends Control

@onready var new_game_btn:  Button = $Panel/VBox/NewGameButton
@onready var continue_btn:  Button = $Panel/VBox/ContinueButton
@onready var options_btn:   Button = $Panel/VBox/OptionsButton
@onready var quit_btn:      Button = $Panel/VBox/QuitButton
@onready var title_label:   Label  = $TitleLabel
@onready var subtitle_label:Label  = $SubtitleLabel

func _ready() -> void:
	WorldData.load_world()

	title_label.text    = "SHINOBI RPG"
	subtitle_label.text = "The Quiet Steel Confederacy"

	new_game_btn.pressed.connect(_on_new_game)
	continue_btn.pressed.connect(_on_continue)
	options_btn.pressed.connect(_on_options)
	quit_btn.pressed.connect(_on_quit)

	# Grey out Continue if no save
	continue_btn.disabled = not GameState.has_save()

	AudioManager.play_music("music_menu")

func _on_new_game() -> void:
	GameState.delete_save()
	get_tree().change_scene_to_file("res://scenes/CharacterCreation.tscn")

func _on_continue() -> void:
	if GameState.load_game():
		GameState.return_to_world_map()
	else:
		continue_btn.disabled = true

func _on_options() -> void:
	# Future: open options overlay
	pass

func _on_quit() -> void:
	get_tree().quit()
