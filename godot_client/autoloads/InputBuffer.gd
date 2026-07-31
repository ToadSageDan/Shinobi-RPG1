## InputBuffer.gd — Combo input buffering singleton.
## Records recent button presses and detects registered combo sequences.
## Emits combo_detected when a complete sequence is matched.
extends Node

signal combo_detected(combo_id: String)

# How long (seconds) a buffered input stays valid
const BUFFER_WINDOW := 0.45

# ── Buffer entry ──────────────────────────────────────────────────────────────

class BufferEntry:
	var action: String
	var timestamp: float

	func _init(a: String, t: float) -> void:
		action    = a
		timestamp = t

var _buffer: Array = []   # Array[BufferEntry]

# ── Combo definitions ─────────────────────────────────────────────────────────
# Each combo: { "inputs": ["attack","attack","heavy_attack"], "id": "triple_slash" }
# Evaluated longest-first so more specific combos beat shorter prefixes.
var _combos: Array[Dictionary] = [
	{"inputs": ["attack", "attack", "heavy_attack"],       "id": "launcher_combo"},
	{"inputs": ["attack", "attack", "attack"],             "id": "triple_slash"},
	{"inputs": ["attack", "heavy_attack"],                 "id": "sweep_strike"},
	{"inputs": ["dodge", "attack"],                        "id": "evade_counter"},
	{"inputs": ["dodge", "heavy_attack"],                  "id": "dash_slam"},
	{"inputs": ["chakra_charge", "jutsu_1"],               "id": "charged_jutsu_1"},
	{"inputs": ["chakra_charge", "jutsu_2"],               "id": "charged_jutsu_2"},
	{"inputs": ["attack", "jutsu_1"],                      "id": "jutsu_cancel_1"},
	{"inputs": ["attack", "jutsu_2"],                      "id": "jutsu_cancel_2"},
	{"inputs": ["heavy_attack", "heavy_attack"],           "id": "double_heavy"},
]

# Sort descending by input length so longest sequences are checked first.
func _ready() -> void:
	_combos.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return a["inputs"].size() > b["inputs"].size()
	)

# ── Per-frame update ──────────────────────────────────────────────────────────

func _process(_delta: float) -> void:
	var now := Time.get_ticks_msec() / 1000.0
	# Expire old entries
	_buffer = _buffer.filter(func(e: BufferEntry) -> bool:
		return now - e.timestamp < BUFFER_WINDOW
	)

# ── Input recording ───────────────────────────────────────────────────────────

## Call this from the Player node whenever a tracked action is just_pressed.
func record(action: String) -> void:
	var entry := BufferEntry.new(action, Time.get_ticks_msec() / 1000.0)
	_buffer.append(entry)
	_check_combos()

# ── Combo detection ───────────────────────────────────────────────────────────

func _check_combos() -> void:
	if _buffer.is_empty():
		return
	var actions: Array[String] = []
	for e: BufferEntry in _buffer:
		actions.append(e.action)

	for combo in _combos:
		var seq: Array = combo["inputs"]
		if _buffer_ends_with(actions, seq):
			emit_signal("combo_detected", combo["id"])
			# Consume the matched inputs to prevent re-triggering
			for _i in range(seq.size()):
				if not _buffer.is_empty():
					_buffer.pop_back()
			return

func _buffer_ends_with(actions: Array[String], sequence: Array) -> bool:
	if actions.size() < sequence.size():
		return false
	var offset := actions.size() - sequence.size()
	for i in range(sequence.size()):
		if actions[offset + i] != sequence[i]:
			return false
	return true

func clear() -> void:
	_buffer.clear()
