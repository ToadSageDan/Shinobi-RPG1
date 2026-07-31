## CharacterCreation.gd — Affinity trial + backstory picker.
## Mirrors the Python affinity mini-game and backstory selection.
extends Control

# ── Affinity questions (mirror of Python _AFFINITY_QUESTIONS) ────────────────
const QUESTIONS := [
	{
		"text": "You're crossing a mountain pass in a storm. You:",
		"options": [
			"Sprint through before it worsens",
			"Find shelter and wait it out",
			"Build a windbreak from loose rocks",
			"Read the wind and time a gap",
		],
		"affinities": ["fire", "water", "earth", "wind"],
	},
	{
		"text": "A rival blocks your path demanding tribute. You:",
		"options": [
			"Step forward — make clear you won't pay",
			"Stall with talk until you spot an opening",
			"Plant your feet; immovable refusal",
			"Side-step entirely — detour around",
		],
		"affinities": ["fire", "water", "earth", "wind"],
	},
	{
		"text": "Your training partner is overwhelmed. You:",
		"options": [
			"Unleash a decisive finishing combo",
			"Drain their stamina with patient counters",
			"Lock them down with grabs and holds",
			"Dance out of reach until they tire",
		],
		"affinities": ["fire", "water", "earth", "wind"],
	},
	{
		"text": "A village elder asks your ideal victory. You say:",
		"options": [
			"Decisive — leave no room for a second round",
			"Adaptive — match the moment, never overcommit",
			"Enduring — outlast every obstacle",
			"Unseen — end it before the enemy knows it began",
		],
		"affinities": ["fire", "water", "earth", "wind"],
	},
	{
		"text": "Describe your ideal terrain:",
		"options": [
			"An open field under a burning noon sun",
			"A river delta at dusk, fog on the water",
			"A fortress carved from a cliff face",
			"A high ridge where every step catches the wind",
		],
		"affinities": ["fire", "water", "earth", "wind"],
	},
]

const BACKSTORIES := [
	{
		"key": "exiled_heir",
		"title": "Exiled Heir",
		"description": "Stripped of title and estate, you carry the last seal of a fallen noble house. Every choice carries the weight of restoration — or revenge.",
		"reputation_bias": 5,
		"tags": ["noble", "political"],
	},
	{
		"key": "street_ghost",
		"title": "Street Ghost",
		"description": "You grew up unseen — in alley networks and courier warrens. Survival made you sharp. The Confederacy's politics are just another hazard to route around.",
		"reputation_bias": -5,
		"tags": ["stealth", "rogue"],
	},
	{
		"key": "wandering_monk",
		"title": "Wandering Monk",
		"description": "Trained in a mountain sanctuary long destroyed, you carry a pacifist discipline into a world that stopped believing in mercy.",
		"reputation_bias": 10,
		"tags": ["nonlethal", "wisdom"],
	},
]

const AFFINITY_COLORS := {
	"fire":  Color(0.95, 0.4, 0.1),
	"water": Color(0.2, 0.6, 0.95),
	"earth": Color(0.3, 0.7, 0.3),
	"wind":  Color(0.85, 0.85, 0.95),
}

const AFFINITY_ICONS := {
	"fire":  "🔥", "water": "💧", "earth": "🌿", "wind": "💨",
}

# ── State ─────────────────────────────────────────────────────────────────────

var _current_step: String = "name"     # name → affinity → backstory → confirm
var _question_index: int = 0
var _scores: Dictionary = {"fire": 0, "water": 0, "earth": 0, "wind": 0}
var _chosen_affinity: String = "fire"
var _chosen_backstory: Dictionary = {}
var _player_name: String = ""

# ── Nodes ─────────────────────────────────────────────────────────────────────

@onready var step_title:    Label       = $Panel/VBox/StepTitle
@onready var question_text: Label       = $Panel/VBox/QuestionText
@onready var options_box:   VBoxContainer = $Panel/VBox/OptionsBox
@onready var name_input:    LineEdit    = $Panel/VBox/NameInput
@onready var progress_label: Label      = $Panel/VBox/ProgressLabel
@onready var affinity_reveal: Label     = $Panel/VBox/AffinityReveal
@onready var continue_btn:  Button      = $Panel/VBox/ContinueButton

func _ready() -> void:
	continue_btn.pressed.connect(_on_continue)
	_show_name_step()

# ── Step rendering ────────────────────────────────────────────────────────────

func _show_name_step() -> void:
	_current_step = "name"
	step_title.text = "⚔  ENTER YOUR SHINOBI NAME"
	question_text.text = ""
	name_input.visible = true
	affinity_reveal.visible = false
	_clear_options()
	progress_label.text = "Step 1 of 3"
	continue_btn.text = "Begin Trial →"

func _show_affinity_question() -> void:
	_current_step = "affinity"
	name_input.visible = false
	affinity_reveal.visible = false
	var q: Dictionary = QUESTIONS[_question_index]
	step_title.text = "🔮  AFFINITY TRIAL  (%d/5)" % (_question_index + 1)
	question_text.text = q["text"]
	progress_label.text = "Step 2 of 3  —  Question %d / %d" % [_question_index + 1, QUESTIONS.size()]
	continue_btn.text = ""
	continue_btn.visible = false
	_clear_options()
	for i in range(q["options"].size()):
		var btn := Button.new()
		btn.text = q["options"][i]
		btn.custom_minimum_size.y = 44
		var aff: String = q["affinities"][i]
		btn.modulate = AFFINITY_COLORS.get(aff, Color.WHITE)
		btn.pressed.connect(_on_affinity_choice.bind(aff))
		options_box.add_child(btn)

func _show_affinity_result() -> void:
	_current_step = "affinity_result"
	_clear_options()
	var icon := AFFINITY_ICONS.get(_chosen_affinity, "●")
	var color := AFFINITY_COLORS.get(_chosen_affinity, Color.WHITE)
	affinity_reveal.text = "%s  Your affinity is revealed:  %s" % [icon, _chosen_affinity.to_upper()]
	affinity_reveal.add_theme_color_override("font_color", color)
	affinity_reveal.visible = true
	question_text.text = "This element shapes your jutsu, stat growth, and combat style."
	step_title.text = "🔮  AFFINITY REVEALED"
	continue_btn.text = "Choose Backstory →"
	continue_btn.visible = true

func _show_backstory_step() -> void:
	_current_step = "backstory"
	affinity_reveal.visible = false
	step_title.text = "📜  CHOOSE YOUR BACKSTORY"
	question_text.text = "Your past defines your path."
	progress_label.text = "Step 3 of 3"
	continue_btn.text = ""
	continue_btn.visible = false
	_clear_options()
	for bs in BACKSTORIES:
		var btn := Button.new()
		btn.text = "%s\n%s" % [bs["title"], bs["description"]]
		btn.custom_minimum_size.y = 70
		btn.autowrap_mode = TextServer.AUTOWRAP_WORD
		btn.pressed.connect(_on_backstory_choice.bind(bs))
		options_box.add_child(btn)

func _show_confirm_step() -> void:
	_current_step = "confirm"
	_clear_options()
	step_title.text = "✓  READY TO BEGIN"
	var icon := AFFINITY_ICONS.get(_chosen_affinity, "●")
	question_text.text = (
		"Name: %s\nAffinity: %s %s\nBackstory: %s\n\n%s" % [
			_player_name, icon, _chosen_affinity.to_upper(),
			_chosen_backstory.get("title", ""),
			_chosen_backstory.get("description", ""),
		]
	)
	continue_btn.text = "Begin Journey →"
	continue_btn.visible = true
	progress_label.text = ""

# ── Callbacks ─────────────────────────────────────────────────────────────────

func _on_continue() -> void:
	match _current_step:
		"name":
			var entered := name_input.text.strip_edges()
			if entered.is_empty():
				entered = "Shinobi"
			_player_name = entered
			_question_index = 0
			_show_affinity_question()
		"affinity_result":
			_show_backstory_step()
		"confirm":
			_apply_creation_and_start()

func _on_affinity_choice(affinity: String) -> void:
	_scores[affinity] += 1
	_question_index += 1
	if _question_index >= QUESTIONS.size():
		_chosen_affinity = _resolve_affinity()
		_show_affinity_result()
	else:
		_show_affinity_question()

func _on_backstory_choice(bs: Dictionary) -> void:
	_chosen_backstory = bs
	_show_confirm_step()

# ── Resolution ────────────────────────────────────────────────────────────────

func _resolve_affinity() -> String:
	var best := "fire"
	var best_score := -1
	for aff in ["fire", "water", "earth", "wind"]:
		if _scores[aff] > best_score:
			best_score = _scores[aff]
			best = aff
	return best

func _apply_creation_and_start() -> void:
	# Populate GameState
	GameState.player_name  = _player_name
	GameState.affinity     = _chosen_affinity
	GameState.backstory_key = _chosen_backstory.get("key", "")
	GameState.reputation   += int(_chosen_backstory.get("reputation_bias", 0))

	# Seed starting moves from WorldData for chosen affinity
	for m in WorldData.get_moves_for_affinity(_chosen_affinity):
		GameState.register_move(m)

	# Seed allies
	for ally in WorldData.allies:
		GameState.ally_loyalty[ally.get("name", "")] = 0

	# Initialize quest log
	for q in WorldData.quests:
		GameState.quest_log[q.get("quest_id", "")] = "inactive"

	GameState.save_game()
	GameState.return_to_world_map()

# ── Helpers ───────────────────────────────────────────────────────────────────

func _clear_options() -> void:
	for child in options_box.get_children():
		child.queue_free()
