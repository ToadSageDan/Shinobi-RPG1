## AudioManifest.gd — Registers all music and SFX paths with AudioManager.
## Loads files that exist under res://assets/audio/ and gracefully skips any
## that are missing — the game runs silently until you drop real .ogg/.wav
## files into the folder structure described in ASSETS_GUIDE.md.
##
## Free asset sources (no payment required):
##   Music:  https://opengameart.org  (search "ninja", "shinobi", "action rpg")
##   SFX:    https://freesound.org    (CC0 licensed game sounds)
##   Alt SFX:https://kenney.nl/assets (Impact Sounds, UI Audio)
##
## Expected folder layout:
##   res://assets/audio/music/
##     menu_theme.ogg
##     forest_theme.ogg
##     volcanic_theme.ogg
##     coastal_theme.ogg
##     alpine_theme.ogg
##     cave_theme.ogg
##     boss_intense.ogg
##   res://assets/audio/sfx/
##     hit_fire.wav     hit_water.wav  hit_earth.wav  hit_wind.wav
##     hit_generic.wav  sfx_death.wav  sfx_dodge.wav  sfx_dash.wav
##     sfx_jutsu.wav    sfx_level_up.wav
extends Node

const MUSIC_MAP: Dictionary = {
	"music_menu":   "res://assets/audio/music/menu_theme.ogg",
	"music_forest": "res://assets/audio/music/forest_theme.ogg",
	"music_volcanic": "res://assets/audio/music/volcanic_theme.ogg",
	"music_coastal":  "res://assets/audio/music/coastal_theme.ogg",
	"music_alpine":   "res://assets/audio/music/alpine_theme.ogg",
	"music_cave":     "res://assets/audio/music/cave_theme.ogg",
	# Boss intensity layers — one shared track is fine until per-boss music exists
	"music_boss_phase2_kage_renda":   "res://assets/audio/music/boss_intense.ogg",
	"music_boss_phase2_ember_sovereign": "res://assets/audio/music/boss_intense.ogg",
	"music_boss_phase2_tidecaller":   "res://assets/audio/music/boss_intense.ogg",
	"music_boss_phase2_stormwall":    "res://assets/audio/music/boss_intense.ogg",
	"music_boss_phase2_voidweaver":   "res://assets/audio/music/boss_intense.ogg",
}

const SFX_MAP: Dictionary = {
	"hit_fire":       "res://assets/audio/sfx/hit_fire.wav",
	"hit_water":      "res://assets/audio/sfx/hit_water.wav",
	"hit_earth":      "res://assets/audio/sfx/hit_earth.wav",
	"hit_wind":       "res://assets/audio/sfx/hit_wind.wav",
	"hit_generic":    "res://assets/audio/sfx/hit_generic.wav",
	"sfx_death":      "res://assets/audio/sfx/sfx_death.wav",
	"sfx_dodge":      "res://assets/audio/sfx/sfx_dodge.wav",
	"sfx_dash":       "res://assets/audio/sfx/sfx_dash.wav",
	"sfx_jutsu_fire": "res://assets/audio/sfx/sfx_jutsu.wav",
	"sfx_level_up":   "res://assets/audio/sfx/sfx_level_up.wav",
}

func _ready() -> void:
	_register_streams()

func _register_streams() -> void:
	var valid_music: Dictionary = {}
	var valid_sfx: Dictionary   = {}

	for key in MUSIC_MAP:
		var path: String = MUSIC_MAP[key]
		if ResourceLoader.exists(path):
			valid_music[key] = path
		else:
			push_warning("AudioManifest: missing music '%s' at %s — add .ogg to enable" % [key, path])

	for key in SFX_MAP:
		var path: String = SFX_MAP[key]
		if ResourceLoader.exists(path):
			valid_sfx[key] = path
		else:
			push_warning("AudioManifest: missing SFX '%s' at %s — add .wav/.ogg to enable" % [key, path])

	AudioManager.register_streams(valid_music, valid_sfx)

	var loaded_m := valid_music.size()
	var loaded_s := valid_sfx.size()
	var total_m  := MUSIC_MAP.size()
	var total_s  := SFX_MAP.size()
	print("AudioManifest: loaded %d/%d music tracks, %d/%d SFX clips." % [loaded_m, total_m, loaded_s, total_s])
	if loaded_m == 0 and loaded_s == 0:
		print("  → No audio files found. See godot_client/ASSETS_GUIDE.md for free sources.")
