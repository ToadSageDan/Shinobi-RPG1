## Shop.gd — Reputation-aware shop and Black Market UI.
## Lists purchasable items from WorldData.shop_inventory, gated by rep tier
## and optional quest completion requirements. Unlocked moves are added to
## GameState.unlocked_moves on purchase.
extends Control

@onready var title_label:    Label         = $HeaderPanel/HBox/TitleLabel
@onready var rep_label:      Label         = $HeaderPanel/HBox/RepLabel
@onready var credits_label:  Label         = $HeaderPanel/HBox/CreditsLabel
@onready var item_list:      VBoxContainer = $ScrollContainer/ItemList
@onready var detail_panel:   Panel         = $DetailPanel
@onready var detail_name:    Label         = $DetailPanel/VBox/NameLabel
@onready var detail_desc:    Label         = $DetailPanel/VBox/DescLabel
@onready var detail_cost:    Label         = $DetailPanel/VBox/CostLabel
@onready var detail_req:     Label         = $DetailPanel/VBox/ReqLabel
@onready var buy_btn:        Button        = $DetailPanel/VBox/BuyButton
@onready var back_btn:       Button        = $BackButton
@onready var feedback_label: Label         = $FeedbackLabel

var _selected_item: Dictionary = {}

func _ready() -> void:
	title_label.text = "🛒  Shinobi Marketplace"
	buy_btn.pressed.connect(_on_buy)
	back_btn.pressed.connect(_on_back)
	detail_panel.visible = false
	feedback_label.visible = false
	_refresh_header()
	_build_item_list()

# ── Header ────────────────────────────────────────────────────────────────────

func _refresh_header() -> void:
	rep_label.text     = "Rep: %+d  [%s]" % [GameState.reputation, GameState.reputation_tier().to_upper()]
	credits_label.text = "Credits: %d" % GameState.credits

# ── Item list ─────────────────────────────────────────────────────────────────

func _build_item_list() -> void:
	for child in item_list.get_children():
		child.queue_free()

	var items := WorldData.shop_inventory
	if items.is_empty():
		items = _fallback_shop_items()

	var tier := GameState.reputation_tier()
	for item in items:
		var req_tier: String = item.get("reputation_required", "neutral")
		var quest_req: String = item.get("quest_required", "")
		var tier_ok    := _tier_meets(tier, req_tier)
		var quest_ok   := quest_req.is_empty() or GameState.quest_log.get(quest_req, "") == "completed"
		var affordable := GameState.credits >= int(item.get("cost", 0))
		var owned      := _is_owned(item)

		var suffix := ""
		if owned:
			suffix = "  ✅"
		elif not tier_ok:
			suffix = "  🔒 [%s rep]" % req_tier.to_upper()
		elif not quest_ok:
			suffix = "  🔒 [quest: %s]" % quest_req
		elif not affordable:
			suffix = "  💰 (need %d cr)" % int(item.get("cost", 0))

		var btn := Button.new()
		btn.text = "%s  %s  — %d cr%s" % [
			item.get("emoji", "📦"),
			item.get("name", "Item"),
			int(item.get("cost", 0)),
			suffix,
		]
		btn.disabled = not tier_ok or not quest_ok or owned
		btn.custom_minimum_size.y = 48
		btn.pressed.connect(_on_item_selected.bind(item))
		item_list.add_child(btn)

# ── Detail panel ──────────────────────────────────────────────────────────────

func _on_item_selected(item: Dictionary) -> void:
	_selected_item = item
	detail_name.text = item.get("name", "Unknown")
	detail_desc.text = item.get("description", "No description available.")
	detail_cost.text = "Cost: %d credits" % int(item.get("cost", 0))
	var req_tier: String = item.get("reputation_required", "neutral")
	var quest_req: String = item.get("quest_required", "")
	var req_str := "Required rep: %s" % req_tier.to_upper()
	if not quest_req.is_empty():
		req_str += "   |   Quest: %s" % quest_req
	detail_req.text = req_str
	buy_btn.disabled = GameState.credits < int(item.get("cost", 0)) or _is_owned(item)
	detail_panel.visible = true
	feedback_label.visible = false

# ── Purchase ──────────────────────────────────────────────────────────────────

func _on_buy() -> void:
	if _selected_item.is_empty():
		return
	var cost := int(_selected_item.get("cost", 0))
	if GameState.credits < cost:
		_show_feedback("❌  Not enough credits!")
		return
	GameState.credits -= cost
	# If item provides a move, add it to unlocked_moves
	var item_move: Variant = _selected_item.get("move", null)
	if item_move is Dictionary and not item_move.is_empty():
		GameState.unlocked_moves.append(item_move)
	_show_feedback("✅  Purchased: %s" % _selected_item.get("name", "item"))
	_refresh_header()
	_build_item_list()
	detail_panel.visible = false
	GameState.save_game()

func _show_feedback(msg: String) -> void:
	feedback_label.text = msg
	feedback_label.visible = true
	var tween := create_tween()
	tween.tween_interval(2.5)
	tween.tween_callback(func() -> void: feedback_label.visible = false)

func _on_back() -> void:
	GameState.return_to_world_map()

# ── Helpers ───────────────────────────────────────────────────────────────────

func _is_owned(item: Dictionary) -> bool:
	var iname: String = item.get("name", "")
	for m in GameState.unlocked_moves:
		if m.get("name", "") == iname:
			return true
	return false

## Returns true if the player's current rep tier meets the minimum requirement.
func _tier_meets(current: String, required: String) -> bool:
	var rank := {"rogue": -1, "neutral": 0, "heroic": 1}
	return rank.get(current, 0) >= rank.get(required, 0)

## Fallback item list used when WorldData has no shop_inventory.
func _fallback_shop_items() -> Array[Dictionary]:
	return [
		{
			"name": "Iron Kunai Upgrade", "emoji": "🔪", "cost": 80,
			"reputation_required": "neutral", "quest_required": "",
			"description": "Forged-steel kunai with improved weight balance. Faster throw arc, +3 Attack.",
		},
		{
			"name": "Shadow Step Scroll", "emoji": "📜", "cost": 120,
			"reputation_required": "neutral", "quest_required": "",
			"description": "Teaches the Shadow Step evasion technique. Grants 0.5 s invisibility on dodge activation.",
		},
		{
			"name": "Healer's Salve (×3)", "emoji": "💚", "cost": 60,
			"reputation_required": "neutral", "quest_required": "",
			"description": "Restores 30 HP on use. Stackable consumable — keeps your run alive.",
		},
		{
			"name": "Jade Armor Fragment", "emoji": "🛡", "cost": 150,
			"reputation_required": "neutral", "quest_required": "",
			"description": "+5 Defense bonus. Recovered from fallen Jade Guard soldiers at Verdant Gate.",
		},
		{
			"name": "Wind Dancer Wraps", "emoji": "🌀", "cost": 180,
			"reputation_required": "neutral", "quest_required": "",
			"description": "Light-woven chakra wraps that reduce dodge stamina cost by 5.",
		},
		{
			"name": "Rogue Cipher Kit", "emoji": "🗝", "cost": 200,
			"reputation_required": "rogue", "quest_required": "",
			"description": "Black Market infiltration toolkit. Unlocks hidden rogue quest branches across all regions.",
		},
		{
			"name": "Void Mark Tattoo", "emoji": "🖤", "cost": 350,
			"reputation_required": "rogue", "quest_required": "",
			"description": "Marks you as a feared rogue. Costs 20 reputation but grants +15 power via fear aura.",
		},
		{
			"name": "Heroic Blade Blessing", "emoji": "⚔️", "cost": 300,
			"reputation_required": "heroic", "quest_required": "",
			"description": "Sacred rite from the Verdant Gate temple. +10 Attack, available to Heroic tier only.",
		},
		{
			"name": "Obsidian Shuriken Set", "emoji": "💫", "cost": 95,
			"reputation_required": "neutral", "quest_required": "",
			"description": "Volcanic-glass throwing stars from Ashen Cradle. Applies Bleed on hit.",
		},
		{
			"name": "Tidal Chakra Vial", "emoji": "💧", "cost": 130,
			"reputation_required": "neutral", "quest_required": "",
			"description": "Restores 40 Chakra instantly. Brewed from Tideglass reef minerals.",
		},
	]
