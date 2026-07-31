## Tideglass.gd — Tideglass arena (coastal reef, boss: Admiral Neris).
extends "res://scripts/BaseArena.gd"

func _ready() -> void:
	region_key       = "tideglass"
	region_min_level = 7
	super._ready()

func _play_boss_cutscene(boss_name: String) -> void:
	if _hud:
		_hud.call("show_boss_taunt",
			"The tide turns. Admiral Neris has flooded the lower amphitheater.")
	await get_tree().create_timer(2.5).timeout
