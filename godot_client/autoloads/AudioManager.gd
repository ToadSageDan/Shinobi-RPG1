## AudioManager.gd — Centralized audio singleton.
## Manages music layers (base + intensity overlay), one-shot SFX pooling,
## and affinity-themed audio routing.
extends Node

# ── Audio buses (set up matching names in Godot's Audio Bus layout) ───────────
# Master → Music → MusicIntensity
#        → SFX   → Combat / UI / Ambient

const BUS_MUSIC    := "Music"
const BUS_SFX      := "SFX"
const BUS_AMBIENT  := "Ambient"

# ── Music players ─────────────────────────────────────────────────────────────

var _music_base: AudioStreamPlayer
var _music_intensity: AudioStreamPlayer

# ── SFX pool (reuse players to avoid allocation spikes) ──────────────────────

const SFX_POOL_SIZE := 12
var _sfx_pool: Array[AudioStreamPlayer] = []
var _sfx_index: int = 0

# ── Stream registry (populated via load_audio_manifest) ──────────────────────

var _music_tracks: Dictionary = {}   # key → AudioStream
var _sfx_clips: Dictionary    = {}   # key → AudioStream

func _ready() -> void:
	_music_base = AudioStreamPlayer.new()
	_music_base.bus = BUS_MUSIC
	_music_base.volume_db = 0.0
	add_child(_music_base)

	_music_intensity = AudioStreamPlayer.new()
	_music_intensity.bus = BUS_MUSIC
	_music_intensity.volume_db = -80.0  # start silent; crossfade in during combat
	add_child(_music_intensity)

	for i in range(SFX_POOL_SIZE):
		var p := AudioStreamPlayer.new()
		p.bus = BUS_SFX
		add_child(p)
		_sfx_pool.append(p)

# ── Public API ────────────────────────────────────────────────────────────────

## Load audio resources from a dictionary of {key: res_path}.
func register_streams(music: Dictionary, sfx: Dictionary) -> void:
	for key in music:
		var stream: Variant = load(music[key])
		if stream:
			_music_tracks[key] = stream
	for key in sfx:
		var stream: Variant = load(sfx[key])
		if stream:
			_sfx_clips[key] = stream

## Play a looping music track by key.
## If fade_time > 0 the current track fades out while the new one fades in.
func play_music(key: String, fade_time: float = 1.5) -> void:
	var stream: Variant = _music_tracks.get(key)
	if not stream:
		return
	if fade_time > 0.0 and _music_base.playing:
		var tween := create_tween()
		tween.tween_property(_music_base, "volume_db", -80.0, fade_time)
		tween.tween_callback(func() -> void:
			_music_base.stream = stream
			_music_base.volume_db = -80.0
			_music_base.play()
			var tween2 := create_tween()
			tween2.tween_property(_music_base, "volume_db", 0.0, fade_time * 0.5)
		)
	else:
		_music_base.stream = stream
		_music_base.play()

## Blend in a combat intensity layer (e.g. drums/bass when boss activates phase 2).
func set_intensity_layer(key: String, volume_db: float = 0.0, fade_time: float = 1.0) -> void:
	var stream: Variant = _music_tracks.get(key)
	if stream and not _music_intensity.playing:
		_music_intensity.stream = stream
		_music_intensity.play()
	var tween := create_tween()
	tween.tween_property(_music_intensity, "volume_db", volume_db, fade_time)

func clear_intensity_layer(fade_time: float = 1.0) -> void:
	var tween := create_tween()
	tween.tween_property(_music_intensity, "volume_db", -80.0, fade_time)
	tween.tween_callback(func() -> void: _music_intensity.stop())

## Play a one-shot SFX by key. Uses pool to avoid allocations.
func play_sfx(key: String, volume_db: float = 0.0, pitch: float = 1.0) -> void:
	var stream: Variant = _sfx_clips.get(key)
	if not stream:
		return
	var player := _sfx_pool[_sfx_index]
	_sfx_index = (_sfx_index + 1) % SFX_POOL_SIZE
	player.stream = stream
	player.volume_db = volume_db
	player.pitch_scale = pitch
	player.play()

## Returns the SFX key for an affinity-themed hit sound.
func hit_sfx_for_affinity(affinity: String) -> String:
	match affinity:
		"fire":  return "hit_fire"
		"water": return "hit_water"
		"earth": return "hit_earth"
		"wind":  return "hit_wind"
		_:       return "hit_generic"

## Returns a region biome music key.
func music_key_for_region(region_key: String) -> String:
	match region_key:
		"verdant_gate":    return "music_forest"
		"ashen_cradle":    return "music_volcanic"
		"tideglass":       return "music_coastal"
		"stormwall_ridge": return "music_alpine"
		"sunken_hollow":   return "music_cave"
		_:                 return "music_menu"

func stop_music(fade_time: float = 1.5) -> void:
	if fade_time > 0.0:
		var tween := create_tween()
		tween.tween_property(_music_base, "volume_db", -80.0, fade_time)
		tween.tween_callback(func() -> void: _music_base.stop())
	else:
		_music_base.stop()
