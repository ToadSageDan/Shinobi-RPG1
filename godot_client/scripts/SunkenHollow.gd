## SunkenHollow.gd — Sunken Hollow arena (subterranean toxic, boss: Ashen Monarch).
extends "res://scripts/BaseArena.gd"

func _ready() -> void:
	region_key       = "sunken_hollow"
	region_min_level = 14
	super._ready()

func _play_boss_cutscene(boss_name: String) -> void:
	if _hud:
		_hud.call("show_boss_taunt",
			"The deep vault shudders. The Ashen Monarch channels seismic rage through relic pillars.")
	await get_tree().create_timer(2.5).timeout
