## StormwallRidge.gd — Stormwall Ridge arena (alpine thunder, boss: Zephyr Tyrant).
extends "res://scripts/BaseArena.gd"

func _ready() -> void:
	region_key       = "stormwall_ridge"
	region_min_level = 10
	super._ready()

func _play_boss_cutscene(boss_name: String) -> void:
	if _hud:
		_hud.call("show_boss_taunt",
			"Lightning spires crown the mesa. Zephyr Tyrant controls every current here.")
	await get_tree().create_timer(2.5).timeout
