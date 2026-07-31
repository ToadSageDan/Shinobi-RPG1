## VerdantGate.gd — Verdant Gate arena (forest, humid, boss: Kage Renda).
## Overrides _spawn_arena_contents to configure the environment and
## enemy positions specific to this biome.
extends "res://scripts/BaseArena.gd"

func _ready() -> void:
	region_key      = "verdant_gate"
	region_min_level = 1
	super._ready()

func _play_boss_cutscene(boss_name: String) -> void:
	# Display a brief narrative intro via the HUD banner
	if _hud:
		_hud.call("show_boss_taunt",
			"The canopy whispers your name. Kage Renda awaits at the Skybridge.")
	await get_tree().create_timer(2.5).timeout
