import unittest
from tempfile import TemporaryDirectory

from shinobi_rpg.core import (
    Affinity,
    Backstory,
    JutsuType,
    Move,
    MoveCategory,
    PlayerProfile,
    QuestStatus,
    ReputationTier,
    StatusEffectType,
    TrophyCategory,
    VillainStance,
    assign_affinity_from_choices,
    build_mvp_world,
    load_world_snapshot,
    resolve_affinity_minigame,
    save_world_snapshot,
)


class CoreSystemTests(unittest.TestCase):
    def test_non_ultimate_move_cannot_mix_affinities(self):
        player = PlayerProfile(name="Tester", affinity=Affinity.FIRE)
        move = Move("Invalid Strike", MoveCategory.ATTACK, (Affinity.FIRE, Affinity.WIND))
        with self.assertRaises(ValueError):
            player.add_move(move)

    def test_non_ultimate_move_must_match_player_affinity(self):
        player = PlayerProfile(name="Tester", affinity=Affinity.WATER)
        move = Move("Burn Dash", MoveCategory.ESCAPE, (Affinity.FIRE,))
        with self.assertRaises(ValueError):
            player.add_move(move)

    def test_ultimate_move_allows_mixed_affinities(self):
        player = PlayerProfile(name="Tester", affinity=Affinity.EARTH)
        move = Move("Elemental Surge", MoveCategory.ULTIMATE, (Affinity.FIRE, Affinity.WATER))
        player.add_move(move)
        self.assertEqual(player.moves_by_set[MoveCategory.ULTIMATE][-1].name, "Elemental Surge")

    def test_seeded_player_has_all_move_categories(self):
        world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
        self.assertTrue(all(player.moves_by_set[category] for category in MoveCategory))

    def test_execute_attack_move_scales_with_power(self):
        world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
        result = player.execute_move("Edge Current")
        self.assertEqual(result["category"], "attack")
        self.assertEqual(result["damage"], 10)

    def test_execute_defense_move_scales_with_defense(self):
        world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
        result = player.execute_move("Guarding Veil")
        self.assertEqual(result["category"], "defense")
        self.assertEqual(result["guard"], 8)

    def test_resolve_block_parry_uses_best_defense_move(self):
        world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
        parry_difficulty = 6
        result = player.resolve_block_parry(15, parry_difficulty=parry_difficulty)
        defense_move = player.moves_by_set[MoveCategory.DEFENSE][0]
        expected_guard = int(player.stats.defense * defense_move.power_scale)
        expected_parry_score = int(player.stats.agility * defense_move.power_scale)
        expected_remaining_damage = max(15 - expected_guard, 0)
        self.assertEqual(result["category"], "defense")
        self.assertEqual(result["move"], "Guarding Veil")
        self.assertEqual(result["guard"], expected_guard)
        self.assertEqual(result["parry_score"], expected_parry_score)
        self.assertEqual(result["remaining_damage"], expected_remaining_damage)
        self.assertEqual(result["blocked_damage"], 15 - expected_remaining_damage)
        self.assertEqual(result["parried"], expected_parry_score >= parry_difficulty)
        self.assertEqual(result["damage_taken"], 0)

    def test_resolve_block_parry_falls_back_without_defense_move(self):
        player = PlayerProfile(name="Tester", affinity=Affinity.WATER)
        result = player.resolve_block_parry(15, base_guard_scale=0.5)
        expected_guard = int(player.stats.defense * 0.5)
        expected_parry_score = int(player.stats.agility * 0.5)
        expected_remaining_damage = max(15 - expected_guard, 0)
        self.assertEqual(result["category"], "defense")
        self.assertIsNone(result["move"])
        self.assertEqual(result["guard"], expected_guard)
        self.assertEqual(result["parry_score"], expected_parry_score)
        self.assertEqual(result["remaining_damage"], expected_remaining_damage)
        self.assertEqual(result["blocked_damage"], 15 - expected_remaining_damage)
        self.assertFalse(result["parried"])
        self.assertEqual(result["damage_taken"], expected_remaining_damage)

    def test_execute_escape_move_returns_escape_status(self):
        world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
        result = player.execute_move("Smoke Step")
        escape_move = player.moves_by_set[MoveCategory.ESCAPE][0]
        expected_escape_score = int(player.stats.agility * escape_move.power_scale)
        self.assertEqual(result["category"], "escape")
        self.assertEqual(result["escape_score"], expected_escape_score)
        self.assertEqual(result["escaped"], expected_escape_score >= 6)

    def test_execute_ultimate_move_uses_power_plus_focus(self):
        world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
        result = player.execute_move("Twin Dragon Convergence")
        self.assertEqual(result["category"], "ultimate")
        self.assertEqual(result["damage"], 50)

    def test_execute_summon_move_uses_focus_and_defense(self):
        world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
        summon_name = player.moves_by_set[MoveCategory.SUMMON][0].name
        result = player.execute_move(summon_name)
        self.assertEqual(result["category"], "summon")
        self.assertEqual(result["summon_type"], JutsuType.SUMMONING.value)
        self.assertEqual(result["summon_power"], 20)

    def test_execute_move_rejects_unknown_move(self):
        world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
        with self.assertRaisesRegex(ValueError, 'Move "Nope" is not unlocked for this player.'):
            player.execute_move("Nope")

    def test_affinity_minigame_resolves_top_score(self):
        affinity = resolve_affinity_minigame([5, 1, 1, 1, 2])
        self.assertEqual(affinity, Affinity.FIRE)

    def test_affinity_minigame_tie_breaker_prefers_fire_then_order(self):
        affinity = resolve_affinity_minigame([5, 5, 1, 1, 0])
        self.assertEqual(affinity, Affinity.FIRE)

    def test_affinity_minigame_fifth_decision_can_push_fire_ahead(self):
        affinity = resolve_affinity_minigame([1, 2, 3, 4, 10])
        self.assertEqual(affinity, Affinity.FIRE)

    def test_assign_affinity_from_choices_counts_majority(self):
        affinity = assign_affinity_from_choices(["water", "fire", "water", "earth"])
        self.assertEqual(affinity, Affinity.WATER)

    def test_assign_affinity_from_choices_tie_breaker_prefers_fire_then_order(self):
        affinity = assign_affinity_from_choices(["wind", "fire", "water", "earth"])
        self.assertEqual(affinity, Affinity.FIRE)

    def test_assign_affinity_from_choices_rejects_empty_input(self):
        with self.assertRaisesRegex(ValueError, "Mini-game choices cannot be empty."):
            assign_affinity_from_choices([])

    def test_assign_affinity_from_choices_rejects_unknown_choice(self):
        with self.assertRaisesRegex(ValueError, 'Unknown affinity choice "lightning".'):
            assign_affinity_from_choices(["lightning"])

    def test_rogue_reputation_unlocks_black_market(self):
        player = PlayerProfile(name="Tester", affinity=Affinity.WIND)
        tier = player.update_reputation(-60)
        self.assertEqual(tier.value, ReputationTier.ROGUE.value)
        self.assertIn("black_market", player.unlocked_zones)

    def test_world_seed_meets_mvp_size(self):
        world, player = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
        self.assertGreaterEqual(len(world.allies), 10)

    def test_region_clear_reward_unlocks_fast_travel(self):
        world, player = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
        reward = world.clear_region(player, "Verdant Gate", "weapon")
        self.assertEqual(reward, "Renda Fang Blade")
        self.assertIn("Renda Fang Blade", player.reward_inventory["weapon"])
        self.assertIn("Verdant Gate", player.unlocked_fast_travel_nodes)

    def test_region_clear_requires_previous_region(self):
        world, player = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
        with self.assertRaisesRegex(ValueError, "Previous region must be cleared first."):
            world.clear_region(player, "Ashen Cradle", "move")

    def test_region_cannot_be_cleared_twice(self):
        world, player = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
        world.clear_region(player, "Verdant Gate", "weapon")
        with self.assertRaisesRegex(ValueError, 'Region "Verdant Gate" has already been cleared.'):
            world.clear_region(player, "Verdant Gate", "clothing")

    def test_duplicate_reward_grant_is_rejected(self):
        world, player = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
        world.clear_region(player, "Verdant Gate", "weapon")
        with self.assertRaisesRegex(ValueError, '"Renda Fang Blade" has already been granted for weapon.'):
            player.grant_boss_reward("weapon", "Renda Fang Blade")

    def test_leveling_progression_increases_stats(self):
        world, player = build_mvp_world("TestPlayer", [1, 1, 1, 1, 1])
        before_level = player.stats.level
        before_power = player.stats.power
        before_defense = player.stats.defense
        before_agility = player.stats.agility
        before_focus = player.stats.focus
        # With base XP-per-level at 100, 500 XP yields two level-ups:
        # level 1->2 costs 100 and level 2->3 costs 200 (200 XP remains).
        player.stats.gain_xp(500)
        self.assertEqual(player.stats.level, before_level + 2)
        self.assertEqual(player.stats.power, before_power + 4)
        self.assertEqual(player.stats.defense, before_defense + 4)
        self.assertEqual(player.stats.agility, before_agility + 4)
        self.assertEqual(player.stats.focus, before_focus + 4)

    def test_vault_archives_historic_ninja(self):
        world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
        world.archive_historic_ninja(player)
        archive = world.vault_historic_ninjas[0]
        self.assertEqual(archive["name"], "Dot")
        self.assertEqual(archive["affinity"], player.affinity.value)
        self.assertEqual(archive["level"], player.stats.level)
        self.assertEqual(archive["reputation"], player.reputation)

    def test_player_backstory_updates_tags_and_reputation(self):
        player = PlayerProfile(name="Tester", affinity=Affinity.WIND)
        backstory = Backstory(
            key="wandering_monk",
            title="Wandering Monk",
            narrative_tags=("pacifism", "discipline"),
            reputation_bias=10,
        )
        player.choose_backstory(backstory)
        self.assertEqual(player.selected_backstory.key, "wandering_monk")
        self.assertIn("pacifism", player.narrative_tags)
        self.assertEqual(player.reputation, 10)

    def test_world_decisions_shift_villain_stance(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        for _ in range(2):
            world.apply_player_decision(player, "kill")
        self.assertTrue(all(v.stance == VillainStance.AGGRESSIVE for v in world.villains))

    def test_nonlethal_path_and_trophy_unlock(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        for decision in ["stealth", "stealth", "stealth", "charm", "evasion"]:
            world.apply_player_decision(player, decision)
        self.assertTrue(player.is_nonlethal_path_active())
        self.assertIn("ghost_step", player.trophies)
        self.assertIn("pacifist_shadow", player.trophies)

    def test_archive_includes_backstory_trophies_and_nonlethal_flag(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[0])
        for decision in ["stealth", "charm"]:
            world.apply_player_decision(player, decision)
        world.archive_historic_ninja(player)
        archive = world.vault_historic_ninjas[0]
        self.assertEqual(archive["backstory"], world.player_backstories[0].key)
        self.assertEqual(archive["nonlethal_path"], True)
        self.assertIsInstance(archive["trophies"], list)

    def test_quest_branching_uses_selected_backstory(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        monk = next(backstory for backstory in world.player_backstories if backstory.key == "wandering_monk")
        player.choose_backstory(monk)
        result = world.resolve_quest_branch(player, "Q3")
        self.assertEqual(result["branch_key"], "wandering_monk")
        self.assertIn("without a killing blow", result["outcome"])

    def test_region_boss_behavior_uses_villain_specific_rules(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        behavior = world.get_region_boss_behavior("Verdant Gate", player)
        self.assertEqual(behavior["boss"], "Kage Renda")
        self.assertEqual(behavior["stance"], VillainStance.BALANCED.value)
        self.assertIn("measured strikes", behavior["behavior"])

    def test_clear_region_claims_red_bar_signature_power(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        world.clear_region(player, "Verdant Gate", "weapon")
        self.assertEqual(player.red_bar_power_claims["Kage Renda"], "Rending Spiral")
        self.assertTrue(any(move.name == "Rending Spiral" for move in player.moves_by_set[MoveCategory.ATTACK]))
        villain = next(v for v in world.villains if v.name == "Kage Renda")
        self.assertTrue(villain.defeated)

    def test_first_bosses_include_tutorial_mechanics(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        first_behavior = world.get_region_boss_behavior("Verdant Gate", player)
        second_behavior = world.get_region_boss_behavior("Ashen Cradle", player)
        self.assertIn("blocking", first_behavior["tutorial_mechanics"])
        self.assertIn("substitution", first_behavior["tutorial_mechanics"])
        self.assertIn("aoe_attacks", second_behavior["tutorial_mechanics"])

    def test_trophy_catalog_uses_categories_and_progression_unlocks(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        world.clear_region(player, "Verdant Gate", "weapon")
        self.assertIn("first_bloodline_victory", player.trophies)
        self.assertEqual(
            world.trophy_catalog["first_bloodline_victory"].category,
            TrophyCategory.PROGRESSION,
        )

    def test_generate_playthrough_summary_reports_core_state(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[0])
        world.apply_player_decision(player, "stealth")
        summary = world.generate_playthrough_summary(player)
        self.assertEqual(summary["player_name"], "TestPlayer")
        self.assertEqual(summary["backstory"], world.player_backstories[0].title)
        self.assertIn("encounter_outcomes", summary)
        self.assertIn("villain_stances", summary)
        self.assertIn("trophies", summary)

    def test_save_and_load_snapshot_restores_world_and_player_state(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        world.apply_player_decision(player, "kill")
        world.clear_region(player, "Verdant Gate", "weapon")
        world.complete_quest(player, "Q1")
        with TemporaryDirectory() as temp_dir:
            snapshot_path = f"{temp_dir}/snapshot.json"
            save_world_snapshot(world, player, snapshot_path)
            restored_world, restored_player = load_world_snapshot(snapshot_path)
        self.assertEqual(restored_player.name, player.name)
        self.assertEqual(restored_player.credits, player.credits)
        self.assertTrue(restored_world.regions[0].cleared)
        self.assertEqual(restored_player.quest_log["Q1"], QuestStatus.COMPLETED)
        self.assertEqual(restored_world.villains[0].decision_memory.get("kill"), 1)
        self.assertEqual(restored_player.red_bar_power_claims.get("Kage Renda"), "Rending Spiral")

    def test_quest_log_initializes_with_first_quest_active(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        self.assertEqual(player.quest_log["Q1"], QuestStatus.ACTIVE)
        self.assertNotIn("Q2", player.quest_log)

    def test_complete_quest_rewards_xp_credits_and_unlocks_next(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        result = world.complete_quest(player, "Q1")
        self.assertEqual(player.quest_log["Q1"], QuestStatus.COMPLETED)
        self.assertEqual(player.quest_log["Q2"], QuestStatus.ACTIVE)
        self.assertEqual(result["reward_xp"], 120)
        self.assertGreater(result["credit_reward"], 0)
        self.assertGreater(player.credits, 100)

    def test_start_quest_requires_previous_completion(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        with self.assertRaisesRegex(ValueError, "Previous quest must be completed first."):
            world.start_quest(player, "Q2")

    def test_fail_quest_marks_failed_and_reduces_loyalty(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        baseline = player.ally_loyalty["Dan"]
        world.fail_quest(player, "Q1")
        self.assertEqual(player.quest_log["Q1"], QuestStatus.FAILED)
        self.assertLess(player.ally_loyalty["Dan"], baseline)

    def test_resolve_region_encounter_uses_region_encounter_table_cycle(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        first = world.resolve_region_encounter(player, "Verdant Gate")
        second = world.resolve_region_encounter(player, "Verdant Gate")
        self.assertNotEqual(first["encounter"], second["encounter"])
        self.assertEqual(player.encounter_history["Verdant Gate"], 2)

    def test_shop_inventory_respects_black_market_unlock(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        public_inventory = {item["key"] for item in world.get_shop_inventory(player)}
        self.assertIn("market_smoke_bomb", public_inventory)
        self.assertNotIn("black_market_kunai", public_inventory)
        player.update_reputation(-60)
        rogue_inventory = {item["key"] for item in world.get_shop_inventory(player)}
        self.assertIn("black_market_kunai", rogue_inventory)

    def test_purchase_shop_item_spends_credits_and_grants_reward(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        player.update_reputation(-60)
        before = player.credits
        result = world.purchase_shop_item(player, "black_market_kunai")
        self.assertLess(player.credits, before)
        self.assertIn("Nightglass Kunai", player.reward_inventory["weapon"])
        self.assertEqual(result["remaining_credits"], player.credits)

    def test_trophy_progress_contains_near_miss(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        for _ in range(2):
            world.apply_player_decision(player, "stealth")
        progress = world.get_trophy_progress(player)
        ghost_step = next(item for item in progress if item["key"] == "ghost_step")
        self.assertEqual(ghost_step["remaining"], 1)
        self.assertTrue(ghost_step["near_miss"])

    def test_playthrough_summary_includes_new_tracking_fields(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        world.apply_player_decision(player, "charm")
        summary = world.generate_playthrough_summary(player)
        self.assertIn("villain_decision_memory", summary)
        self.assertIn("red_bar_power_claims", summary)
        self.assertIn("red_bar_progress", summary)
        self.assertIn("quest_log", summary)
        self.assertIn("ally_loyalty", summary)
        self.assertIn("credits", summary)
        self.assertIn("trophy_progress", summary)

    def test_ninjutsu_catalog_offers_diverse_affinity_and_summon_paths(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        self.assertGreaterEqual(len(world.ninjutsu_library), 20)
        summon_catalog = world.get_ninjutsu_catalog(jutsu_type=JutsuType.SUMMONING)
        self.assertTrue(summon_catalog)
        self.assertTrue(any(item["category"] == MoveCategory.SUMMON.value for item in summon_catalog))

    def test_shared_move_pool_is_evenly_represented(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        counts = {category: 0 for category in MoveCategory}
        for move in world.ninjutsu_library:
            counts[move.category] += 1
        self.assertTrue(all(count == 12 for count in counts.values()))

    def test_execute_move_applies_status_effects(self):
        world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
        result = player.execute_move("Cinder Lance")
        self.assertIn(StatusEffectType.BURN.value, result["applied_statuses"])
        self.assertIn(StatusEffectType.BURN.value, player.active_status_effects)
        self.assertEqual(player.active_status_effects[StatusEffectType.BURN.value]["duration"], 2)
        self.assertEqual(player.active_status_effects[StatusEffectType.BURN.value]["stacks"], 1)

    def test_combo_resolution_applies_status_synergy_bonus(self):
        world, player = build_mvp_world("TestPlayer", [1, 5, 1, 1])
        skyline = next(move for move in world.ninjutsu_library if move.name == "Skyline Covenant")
        player.add_move(skyline, allow_cross_affinity=True)
        combo = player.resolve_combo("Undertow Slice", "Tidal Blink", "Skyline Covenant")
        self.assertEqual(combo["combo_bonus"], "storm_burst")
        self.assertGreater(combo["total_damage"], combo["base_damage"])

    def test_animation_preview_and_villain_kits_exposed_in_summary(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        preview = world.get_move_animation_preview("Edge Current")
        self.assertIn("startup", preview["animation_profile"])
        combo_preview = world.preview_affinity_combo_animation(
            "Undertow Slice",
            "Crosswind Fade",
            "Skyline Covenant",
        )
        self.assertEqual(len(combo_preview["combo_path"]), 3)
        summary = world.generate_playthrough_summary(player)
        self.assertIn("villain_kits", summary)
        self.assertGreaterEqual(len(summary["villain_kits"]), 15)


if __name__ == "__main__":
    unittest.main()
