## AshenCradle.gd — Ashen Cradle arena (volcanic, boss: General Voln).
extends "res://scripts/BaseArena.gd"

func _ready() -> void:
	region_key       = "ashen_cradle"
	region_min_level = 4
	super._ready()

func _play_boss_cutscene(boss_name: String) -> void:
	if _hud:
		_hud.call("show_boss_taunt",
			"The furnace roars. General Voln commands the slag fields ahead.")
	await get_tree().create_timer(2.5).timeout
