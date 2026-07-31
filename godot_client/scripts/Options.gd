## Options.gd — Audio/display settings and controller/gamepad remapping screen.
## Remappable actions are listed dynamically from InputMap. Players can click
## any row then press a key or gamepad button to reassign it.
## Settings are persisted to "user://options.cfg".
extends Control

# ── Node refs ─────────────────────────────────────────────────────────────────

@onready var title_label:     Label         = $HeaderPanel/HBox/TitleLabel
@onready var tab_bar:         HBoxContainer = $TabBar
@onready var remap_scroll:    ScrollContainer = $RemapScroll
@onready var remap_list:      VBoxContainer = $RemapScroll/RemapList
@onready var settings_panel:  VBoxContainer = $SettingsPanel
@onready var listening_label: Label         = $ListeningOverlay/Label
@onready var listening_overlay: Panel       = $ListeningOverlay
@onready var back_btn:        Button        = $BackButton
@onready var reset_btn:       Button        = $ResetButton
@onready var music_slider:    HSlider       = $SettingsPanel/MusicRow/MusicSlider
@onready var sfx_slider:      HSlider       = $SettingsPanel/SFXRow/SFXSlider
@onready var fullscreen_check:CheckButton   = $SettingsPanel/DisplayRow/FullscreenCheck

# ── Remapping state ───────────────────────────────────────────────────────────

const REMAPPABLE_ACTIONS := [
	"move_forward", "move_back", "move_left", "move_right",
	"jump", "dodge", "attack", "heavy_attack",
	"jutsu_1", "jutsu_2", "jutsu_3", "jutsu_4",
	"lock_on", "chakra_charge", "pause",
]

const ACTION_LABELS := {
	"move_forward":  "Move Forward",
	"move_back":     "Move Back",
	"move_left":     "Move Left",
	"move_right":    "Move Right",
	"jump":          "Jump",
	"dodge":         "Dodge / Roll",
	"attack":        "Light Attack",
	"heavy_attack":  "Heavy Attack",
	"jutsu_1":       "Jutsu Slot 1",
	"jutsu_2":       "Jutsu Slot 2",
	"jutsu_3":       "Jutsu Slot 3",
	"jutsu_4":       "Jutsu Slot 4",
	"lock_on":       "Lock-On Target",
	"chakra_charge": "Chakra Charge",
	"pause":         "Pause / Menu",
}

const SETTINGS_PATH := "user://options.cfg"

var _listening_action: String = ""
var _row_buttons: Dictionary = {}   # action → Button (shows current binding)
var _active_tab: String = "controls"

func _ready() -> void:
	title_label.text = "⚙  Options"
	listening_overlay.visible = false
	back_btn.pressed.connect(_on_back)
	reset_btn.pressed.connect(_on_reset_defaults)
	_build_tabs()
	_load_settings()
	_show_tab("controls")
	_setup_settings_panel()

# ── Tabs ──────────────────────────────────────────────────────────────────────

func _build_tabs() -> void:
	for child in tab_bar.get_children():
		child.queue_free()
	var tab_defs := [["controls", "🎮 Controls"], ["audio", "🔊 Audio"], ["display", "🖥 Display"]]
	for td in tab_defs:
		var btn := Button.new()
		btn.text = td[1]
		btn.custom_minimum_size = Vector2(180, 40)
		btn.toggle_mode = true
		btn.button_pressed = (td[0] == _active_tab)
		btn.pressed.connect(_show_tab.bind(td[0]))
		tab_bar.add_child(btn)

func _show_tab(tab: String) -> void:
	_active_tab = tab
	var i := 0
	for child in tab_bar.get_children():
		if child is Button:
			var tabs := ["controls", "audio", "display"]
			child.button_pressed = (tabs[i] == tab)
			i += 1
	remap_scroll.visible   = (tab == "controls")
	settings_panel.visible = (tab in ["audio", "display"])
	reset_btn.visible      = (tab == "controls")
	if tab == "controls":
		_build_remap_list()
	elif tab == "audio":
		_show_audio_settings()
	elif tab == "display":
		_show_display_settings()

# ── Controls remap ────────────────────────────────────────────────────────────

func _build_remap_list() -> void:
	for child in remap_list.get_children():
		child.queue_free()
	_row_buttons.clear()

	for action in REMAPPABLE_ACTIONS:
		var row := HBoxContainer.new()
		row.custom_minimum_size.y = 48
		row.theme_override_constants = {"separation": 12}

		var name_lbl := Label.new()
		name_lbl.text = ACTION_LABELS.get(action, action)
		name_lbl.custom_minimum_size.x = 200
		name_lbl.vertical_alignment = 1
		name_lbl.theme_override_font_sizes = {"font_size": 16}
		row.add_child(name_lbl)

		var kb_btn := Button.new()
		kb_btn.text = _get_key_label(action, false)
		kb_btn.custom_minimum_size = Vector2(180, 40)
		kb_btn.pressed.connect(_start_remap.bind(action, false))
		row.add_child(kb_btn)

		var pad_btn := Button.new()
		pad_btn.text = _get_key_label(action, true)
		pad_btn.custom_minimum_size = Vector2(180, 40)
		pad_btn.pressed.connect(_start_remap.bind(action, true))
		row.add_child(pad_btn)

		_row_buttons[action] = [kb_btn, pad_btn]
		remap_list.add_child(row)

	# Column header row (prepend)
	var header := HBoxContainer.new()
	header.custom_minimum_size.y = 32
	var h0 := Label.new(); h0.text = "Action"; h0.custom_minimum_size.x = 200
	h0.theme_override_font_sizes = {"font_size": 14}; h0.theme_override_colors = {"font_color": Color(0.6, 0.65, 0.6, 1)}
	var h1 := Label.new(); h1.text = "Keyboard"; h1.custom_minimum_size.x = 180
	h1.theme_override_font_sizes = {"font_size": 14}; h1.theme_override_colors = {"font_color": Color(0.6, 0.65, 0.6, 1)}
	var h2 := Label.new(); h2.text = "Gamepad"; h2.custom_minimum_size.x = 180
	h2.theme_override_font_sizes = {"font_size": 14}; h2.theme_override_colors = {"font_color": Color(0.6, 0.65, 0.6, 1)}
	header.add_child(h0); header.add_child(h1); header.add_child(h2)
	remap_list.move_child(header, 0)

## Start listening for a new key/button for the given action.
func _start_remap(action: String, is_gamepad: bool) -> void:
	_listening_action = action
	_gamepad_remap = is_gamepad
	var device_str := "gamepad button" if is_gamepad else "keyboard key"
	listening_label.text = "Press a %s for:\n[b]%s[/b]\n\n(Escape to cancel)" % [device_str, ACTION_LABELS.get(action, action)]
	listening_overlay.visible = true
	set_process_input(true)

var _gamepad_remap: bool = false

func _input(event: InputEvent) -> void:
	if not listening_overlay.visible:
		return
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_ESCAPE:
			_cancel_remap()
			return
		if not _gamepad_remap:
			_apply_remap(event)
		get_viewport().set_input_as_handled()
	elif event is InputEventJoypadButton and event.pressed:
		if _gamepad_remap:
			_apply_remap(event)
		get_viewport().set_input_as_handled()

func _apply_remap(event: InputEvent) -> void:
	var action := _listening_action
	# Remove existing events of the same type for this action
	var existing := InputMap.action_get_events(action)
	for ev in existing:
		if _gamepad_remap and ev is InputEventJoypadButton:
			InputMap.action_erase_event(action, ev)
		elif not _gamepad_remap and ev is InputEventKey:
			InputMap.action_erase_event(action, ev)
	InputMap.action_add_event(action, event)
	_save_settings()
	_cancel_remap()
	_build_remap_list()

func _cancel_remap() -> void:
	_listening_action = ""
	listening_overlay.visible = false

func _on_reset_defaults() -> void:
	InputMap.load_from_project_settings()
	_build_remap_list()
	_save_settings()

func _get_key_label(action: String, gamepad: bool) -> String:
	if not InputMap.has_action(action):
		return "—"
	for ev in InputMap.action_get_events(action):
		if gamepad and ev is InputEventJoypadButton:
			return "Button %d" % (ev as InputEventJoypadButton).button_index
		if not gamepad and ev is InputEventKey:
			return OS.get_keycode_string((ev as InputEventKey).physical_keycode)
	return "—"

# ── Audio / Display settings ──────────────────────────────────────────────────

func _show_audio_settings() -> void:
	for child in settings_panel.get_children():
		child.visible = child.name in ["MusicRow", "SFXRow"]

func _show_display_settings() -> void:
	for child in settings_panel.get_children():
		child.visible = child.name == "DisplayRow"

func _setup_settings_panel() -> void:
	music_slider.value_changed.connect(_on_music_volume)
	sfx_slider.value_changed.connect(_on_sfx_volume)
	fullscreen_check.toggled.connect(_on_fullscreen_toggle)

func _on_music_volume(val: float) -> void:
	var db := linear_to_db(val / 100.0)
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Music"), db)
	_save_settings()

func _on_sfx_volume(val: float) -> void:
	var db := linear_to_db(val / 100.0)
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("SFX"), db)
	_save_settings()

func _on_fullscreen_toggle(pressed: bool) -> void:
	DisplayServer.window_set_mode(
		DisplayServer.WINDOW_MODE_FULLSCREEN if pressed else DisplayServer.WINDOW_MODE_WINDOWED
	)
	_save_settings()

# ── Persistence ───────────────────────────────────────────────────────────────

func _save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("audio", "music_volume", music_slider.value)
	cfg.set_value("audio", "sfx_volume", sfx_slider.value)
	cfg.set_value("display", "fullscreen", fullscreen_check.button_pressed)
	# Save remapped input actions
	for action in REMAPPABLE_ACTIONS:
		if not InputMap.has_action(action):
			continue
		var events_data: Array[Dictionary] = []
		for ev in InputMap.action_get_events(action):
			if ev is InputEventKey:
				events_data.append({"type": "key", "keycode": (ev as InputEventKey).physical_keycode})
			elif ev is InputEventJoypadButton:
				events_data.append({"type": "pad", "button": (ev as InputEventJoypadButton).button_index})
		cfg.set_value("input", action, events_data)
	cfg.save(SETTINGS_PATH)

func _load_settings() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SETTINGS_PATH) != OK:
		return
	var mv: float = cfg.get_value("audio", "music_volume", 80.0)
	var sv: float = cfg.get_value("audio", "sfx_volume", 80.0)
	music_slider.value = mv
	sfx_slider.value   = sv
	fullscreen_check.button_pressed = cfg.get_value("display", "fullscreen", false)
	_on_music_volume(mv)
	_on_sfx_volume(sv)
	# Restore remapped actions
	for action in REMAPPABLE_ACTIONS:
		if not InputMap.has_action(action):
			continue
		var events_data: Variant = cfg.get_value("input", action, null)
		if not events_data is Array:
			continue
		# Remove existing events of those types first
		var existing := InputMap.action_get_events(action)
		for ev in existing:
			if ev is InputEventKey or ev is InputEventJoypadButton:
				InputMap.action_erase_event(action, ev)
		for ed in events_data:
			if not ed is Dictionary:
				continue
			if ed.get("type") == "key":
				var ev := InputEventKey.new()
				ev.physical_keycode = int(ed.get("keycode", 0))
				InputMap.action_add_event(action, ev)
			elif ed.get("type") == "pad":
				var ev := InputEventJoypadButton.new()
				ev.button_index = int(ed.get("button", 0))
				InputMap.action_add_event(action, ev)

# ── Back ──────────────────────────────────────────────────────────────────────

func _on_back() -> void:
	get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")
