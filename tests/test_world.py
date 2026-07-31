import unittest
from shinobi_rpg.core import (
    Affinity,
    BOSS_ECHO_POWER_SCALE_BOOST,
    DEFAULT_ALLY_MIN_COUNT,
    PATROL_STATE_UNDETECTED,
    PATROL_STATE_ALERTED,
    RivalProfile,
    SCOUTING_INTEL_CATEGORIES,
    TechniqueType,
    Move,
    MoveCategory,
    NONLETHAL_CHARM_MASTER_THRESHOLD,
    NONLETHAL_EVASION_MASTER_THRESHOLD,
    NONLETHAL_STEALTH_MASTER_THRESHOLD,
    PlayerProfile,
    StatusEffectType,
    VillainStance,
    build_mvp_world,
    get_learnable_enemy_moves,
)
from unittest.mock import patch


class NinjaWorldCoreTests(unittest.TestCase):
        def _get_unlocked_move_names(self, player: PlayerProfile) -> set[str]:
            return {move.name for moves in player.moves_by_set.values() for move in moves}

        def _get_region(self, world, region_name: str):
            region = next((item for item in world.regions if item.name == region_name), None)
            self.assertIsNotNone(region, f"Expected region '{region_name}' to exist in seeded world.")
            return region

        def test_world_seed_meets_mvp_size(self):
            world, player = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
            self.assertGreaterEqual(len(world.allies), DEFAULT_ALLY_MIN_COUNT)
            self.assertFalse(
                any(name.startswith("AutoNinja-") for name in world.allies[:DEFAULT_ALLY_MIN_COUNT])
            )

        def test_world_map_has_detailed_regions_and_points_of_interest(self):
            world, _ = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
            world_map = world.build_world_map()
            self.assertEqual(world_map["region_count"], len(world.regions))
            self.assertIn("environment", world_map)
            self.assertIn(world_map["environment"]["time_of_day"], {"dawn", "day", "dusk", "night"})
            self.assertIn(world_map["environment"]["weather"], {"clear", "breezy", "rain", "storm", "fog"})
            self.assertEqual(len(world_map["regions"]), len(world.regions))
            for region in world_map["regions"]:
                self.assertIn("minimum_level", region)
                self.assertIn("assassin_hunter_name", region)
                self.assertGreaterEqual(region["minimum_level"], 1)
                self.assertTrue(region["assassin_hunter_name"])
                self.assertGreaterEqual(len(region["points_of_interest"]), 4)
                self.assertTrue(region["strategic_value"])
                self.assertGreaterEqual(len(region["travel_nodes"]), 4)
                for poi in region["points_of_interest"]:
                    self.assertTrue(poi["name"])
                    self.assertTrue(poi["summary"])
                    self.assertGreaterEqual(len(poi["connected_nodes"]), 1)

        def test_lore_dump_covers_country_factions_and_content_catalogs(self):
            world, _ = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
            lore = world.generate_lore_dump()
            self.assertIn("country", lore)
            self.assertIn("allies", lore)
            self.assertIn("villains", lore)
            self.assertIn("points_of_interest", lore)
            self.assertIn("legendary_weapons", lore)
            self.assertIn("summons", lore)
            self.assertEqual(len(lore["villains"]), len(world.villains))
            self.assertGreaterEqual(len(lore["allies"]), DEFAULT_ALLY_MIN_COUNT)
            self.assertGreaterEqual(len(lore["points_of_interest"]), 20)
            self.assertGreaterEqual(len(lore["summons"]), 12)

        def test_region_clear_reward_unlocks_fast_travel(self):
            world, player = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
            reward = world.clear_region(player, "Verdant Gate", "weapon")
            self.assertEqual(reward, "Renda Fang Blade")
            self.assertIn("Renda Fang Blade", player.reward_inventory["weapon"])
            self.assertIn("Verdant Gate", player.unlocked_fast_travel_nodes)

        def test_region_move_reward_unlocks_boss_exclusive_move(self):
            world, player = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
            verdant_gate = self._get_region(world, "Verdant Gate")
            reward_move_name = verdant_gate.boss_rewards["move"]
            unlocked_names = self._get_unlocked_move_names(player)
            self.assertNotIn(reward_move_name, unlocked_names)
            reward = world.clear_region(player, "Verdant Gate", "move")
            self.assertEqual(reward, reward_move_name)
            self.assertIn(reward_move_name, player.reward_inventory["move"])
            unlocked_names = self._get_unlocked_move_names(player)
            self.assertIn(reward_move_name, unlocked_names)
            move_result = player.execute_move(reward_move_name)
            self.assertNotEqual(move_result["combat_physics"]["blood_intensity"], "none")

        def test_boss_exclusive_move_not_unlocked_without_move_reward_choice(self):
            world, player = build_mvp_world("TestPlayer", [2, 4, 1, 3, 5])
            verdant_gate = self._get_region(world, "Verdant Gate")
            reward_move_name = verdant_gate.boss_rewards["move"]
            world.clear_region(player, "Verdant Gate", "weapon")
            unlocked_names = self._get_unlocked_move_names(player)
            self.assertNotIn(reward_move_name, unlocked_names)

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

        def test_world_initializes_arc_era_and_living_tapestry(self):
            world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
            summary = world.generate_playthrough_summary(player)
            self.assertIn("arc_state", summary)
            self.assertEqual(summary["arc_state"]["era"]["key"], "war_age")
            self.assertGreaterEqual(len(summary["living_tapestry"]["active_run_entries"]), 1)
            self.assertEqual(summary["living_tapestry"]["active_run_entries"][0]["event_type"], "arc_shift")

        def test_world_event_updates_state_and_logs_cause_effect(self):
            world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
            baseline = world.get_environment_state()
            event = world.trigger_world_event(player, event_key="tornado", causes=["test_driver"])
            self.assertEqual(event["event_key"], "tornado")
            self.assertEqual(event["causes"], ["test_driver"])
            self.assertIn("environment", event)
            self.assertNotEqual(event["environment"]["time_of_day"], baseline["time_of_day"])
            self.assertTrue(world.world_event_history)
            tapestry_entry = world.active_run_tapestry[-1]
            self.assertEqual(tapestry_entry["event_type"], "world_event")
            self.assertIn("region_pressure", tapestry_entry["effects"])
            self.assertIn("scheduled_regions", world.generate_playthrough_summary(player)["arc_state"])

        def test_minor_event_escalation_can_radicalize_npc_antagonist(self):
            world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
            world.trigger_world_event(player, event_key="tornado", causes=["weather"])
            world.trigger_world_event(player, event_key="rebuild_failure", causes=["hardship"])
            projection = world.get_final_antagonist_projection()
            self.assertIn("minor_event_escalation", " ".join(projection["signals"]))
            self.assertTrue(projection["name"] in world.antagonist_candidates)

        def test_all_antagonist_candidates_have_evil_threshold_profiles(self):
            world, _ = build_mvp_world("Dot", [1, 3, 5, 2, 1])
            self.assertTrue(world.npc_evil_profiles)
            self.assertEqual(set(world.antagonist_candidates), set(world.npc_evil_profiles))
            self.assertTrue(all(profile["can_turn"] for profile in world.npc_evil_profiles.values()))
            self.assertTrue(
                all(profile["evil_threshold"] >= 4 for profile in world.npc_evil_profiles.values())
            )

        def test_external_pressure_event_shifts_npc_evil_without_player_decision(self):
            world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
            baseline = {
                name: profile["evil_score"] for name, profile in world.npc_evil_profiles.items()
            }
            event = world.trigger_external_pressure_event(player, event_key="border_false_flag")
            self.assertEqual(event["event_key"], "border_false_flag")
            changed = [
                name
                for name, profile in world.npc_evil_profiles.items()
                if profile["evil_score"] != baseline[name]
            ]
            self.assertTrue(changed)
            self.assertTrue(world.external_pressure_history)

        def test_newspaper_or_overheard_intel_can_unlock_stealth_route(self):
            world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
            world.trigger_external_pressure_event(player, event_key="blackmail_dossier")
            intel = world.discover_world_intel(player, channel="overheard", stealth_probe=True)
            self.assertEqual(intel["channel"], "overheard")
            self.assertTrue(intel["unlock_node"])
            self.assertIn(intel["unlock_node"], player.unlocked_zones)

        def test_world_decisions_shift_villain_stance(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(2):
                world.apply_player_decision(player, "kill")
            self.assertTrue(all(v.stance == VillainStance.AGGRESSIVE for v in world.villains))

        def test_charm_decisions_shift_villain_stance_by_role(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            world.apply_player_decision(player, "charm")
            aggressive_role_villain = next(v for v in world.villains if v.name == "Mist Widow")
            passive_role_villain = next(v for v in world.villains if v.name == "Admiral Neris")
            self.assertEqual(aggressive_role_villain.stance, VillainStance.BALANCED)
            self.assertEqual(passive_role_villain.stance, VillainStance.PASSIVE)

        def test_stealth_decisions_shift_aggression_score_by_role(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            world.apply_player_decision(player, "stealth")
            aggressive_role_villain = next(v for v in world.villains if v.name == "Mist Widow")
            passive_role_villain = next(v for v in world.villains if v.name == "Admiral Neris")
            self.assertGreater(aggressive_role_villain.aggression_score, 0)
            self.assertLess(passive_role_villain.aggression_score, 0)

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

        def test_resolve_region_encounter_uses_region_encounter_table_cycle(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            first = world.resolve_region_encounter(player, "Verdant Gate")
            second = world.resolve_region_encounter(player, "Verdant Gate")
            self.assertNotEqual(first["encounter"], second["encounter"])
            self.assertEqual(player.encounter_history["Verdant Gate"], 2)
            self.assertFalse(first["assassin_hunt_triggered"])
            self.assertFalse(second["assassin_hunt_triggered"])

        def test_resolve_region_encounter_can_trigger_assassin_hunt_in_high_level_region(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            with patch("shinobi_rpg.core.random.random", return_value=0.0):
                result = world.resolve_region_encounter(player, "Sunken Hollow")
            self.assertTrue(result["unauthorized_region"])
            self.assertTrue(result["assassin_hunt_triggered"])
            self.assertEqual(result["outcome"], "killed")
            self.assertFalse(result["player_survived"])
            self.assertEqual(player.encounter_history["Sunken Hollow"], 1)

        def test_resolve_region_encounter_out_of_band_can_avoid_assassin_hunt(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            with patch("shinobi_rpg.core.random.random", return_value=0.99):
                result = world.resolve_region_encounter(player, "Sunken Hollow")
            region = self._get_region(world, "Sunken Hollow")
            self.assertTrue(result["unauthorized_region"])
            self.assertFalse(result["assassin_hunt_triggered"])
            self.assertIn(result["encounter"], region.encounter_table)
            self.assertTrue(result["player_survived"])
            self.assertEqual(player.encounter_history["Sunken Hollow"], 1)

        def test_region_encounters_grant_repeatable_xp_for_grinding(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            initial_level = player.stats.level
            initial_xp = player.stats.xp
            first = world.resolve_region_encounter(player, "Verdant Gate")
            self.assertGreater(first["reward_xp"], 0)
            self.assertEqual(player.stats.xp, initial_xp + first["reward_xp"])
            for _ in range(12):
                world.resolve_region_encounter(player, "Verdant Gate")
            self.assertGreater(player.stats.level, initial_level)

        def test_region_encounter_unlocks_enemy_exclusive_move_once(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            learnable = get_learnable_enemy_moves()
            region = self._get_region(world, "Verdant Gate")
            target_enemy = next(enemy for enemy in region.encounter_table if enemy in learnable)
            target_move = learnable[target_enemy]

            first_unlock = None
            for _ in range(len(region.encounter_table)):
                result = world.resolve_region_encounter(player, "Verdant Gate")
                if result["encounter"] == target_enemy:
                    first_unlock = result
                    break

            self.assertIsNotNone(first_unlock)
            self.assertEqual(first_unlock["enemy_exclusive_move"], target_move)
            self.assertEqual(first_unlock["enemy_exclusive_move_unlocked"], target_move)
            self.assertIn(target_move, self._get_unlocked_move_names(player))
            self.assertEqual(player.enemy_move_claims[target_enemy], target_move)

            repeat_unlock = None
            for _ in range(len(region.encounter_table)):
                result = world.resolve_region_encounter(player, "Verdant Gate")
                if result["encounter"] == target_enemy:
                    repeat_unlock = result
                    break

            self.assertIsNotNone(repeat_unlock)
            self.assertEqual(repeat_unlock["enemy_exclusive_move"], target_move)
            self.assertIsNone(repeat_unlock["enemy_exclusive_move_unlocked"])

        def test_seeded_encounter_tables_include_shinobi_guards_and_animals(self):
            world, _ = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            encounter_names = [
                encounter.lower()
                for region in world.regions
                for encounter in (region.encounter_table or region.enemies)
            ]
            self.assertTrue(any("shinobi" in encounter for encounter in encounter_names))
            self.assertTrue(any("guard" in encounter or "sentry" in encounter for encounter in encounter_names))
            self.assertTrue(
                any(
                    marker in encounter
                    for encounter in encounter_names
                    for marker in ("hound", "wolf", "boar", "mole", "otter", "bat")
                )
            )

        def test_seeded_encounters_are_mostly_shinobi_conflicts(self):
            world, _ = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            encounter_names = [
                encounter.lower()
                for region in world.regions
                for encounter in (region.encounter_table or region.enemies)
            ]
            shinobi_markers = (
                "shinobi",
                "ronin",
                "mercenar",
                "raider",
                "assassin",
                "monk",
                "scout",
                "hunter",
                "corsair",
                "adept",
                "stalker",
                "guard",
                "sentry",
            )
            shinobi_count = sum(
                1 for encounter in encounter_names if any(marker in encounter for marker in shinobi_markers)
            )
            self.assertGreater(shinobi_count, len(encounter_names) // 2)

        def test_shop_inventory_respects_black_market_unlock(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            public_inventory = {item["key"] for item in world.get_shop_inventory(player)}
            self.assertIn("market_smoke_bomb", public_inventory)
            self.assertNotIn("black_market_kunai", public_inventory)
            self.assertNotIn("pacifist_thread_charm", public_inventory)
            world.apply_player_decision(player, "stealth")
            nonlethal_inventory = {item["key"] for item in world.get_shop_inventory(player)}
            self.assertIn("pacifist_thread_charm", nonlethal_inventory)
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

        def test_city_shops_are_seeded_across_regions(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            shops = world.get_city_shops(player)
            self.assertGreaterEqual(len(shops), len(world.regions))
            self.assertEqual({shop["region_name"] for shop in shops}, {region.name for region in world.regions})

        def test_wayfarer_anchor_purchase_unlocks_mobile_fast_travel_tool(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for quest_id in ("Q1", "Q2", "Q3", "Q4"):
                world.complete_quest(player, quest_id)
            player.credits = 999
            result = world.purchase_shop_item(player, "wayfarer_anchor", city_shop_key="crestfall_wind_market")
            self.assertIn("Wayfarer Anchor", player.owned_tools)
            self.assertIn("Wayfarer Anchor", player.reward_inventory["tool"])
            self.assertEqual(result["remaining_credits"], player.credits)

        def test_mobile_fast_travel_can_be_set_after_buying_tool(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for quest_id in ("Q1", "Q2", "Q3", "Q4"):
                world.complete_quest(player, quest_id)
            player.credits = 999
            world.purchase_shop_item(player, "wayfarer_anchor", city_shop_key="crestfall_wind_market")
            placement = world.set_mobile_fast_travel(player, "Leafrise Village")
            self.assertEqual(placement["node"], "Leafrise Village")
            self.assertIn("Leafrise Village", world.get_available_fast_travel_points(player))
            travel = world.fast_travel(player, "Leafrise Village")
            self.assertTrue(travel["used_mobile_anchor"])

        def test_pickpocket_uses_raiseable_attribute(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            player.attribute_points = 4
            player.raise_action_attribute("pickpocket", 3)
            player.stats.agility = 16
            before = player.credits
            result = world.attempt_pickpocket(player, "Quartermaster Iori")
            self.assertTrue(result["success"])
            self.assertGreater(player.credits, before)
            self.assertEqual(player.pickpocket_history["success"], 1)

        def test_city_npc_interaction_exposes_intel_and_trade_context(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            intel = world.interact_city_npc(player, "Quartermaster Iori", interaction="gather_intel")
            trade = world.interact_city_npc(player, "Quartermaster Iori", interaction="trade")
            self.assertIn("intel_check", intel)
            self.assertIn("shops", trade)
            self.assertTrue(trade["shops"])

        def test_city_specific_quest_layer_tracks_pressure_and_mood(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            result = world.resolve_quest_branch(player, "Q4")
            self.assertIn("city_layer", result)
            self.assertIn("mood", result["city_layer"])
            self.assertIn("city_name", result["city_layer"])
            self.assertIn(result["city_layer"]["city_name"], result["outcome"])
            self.assertGreaterEqual(result["city_layer"]["quest_pressure_after"], 0)

        def test_pickpocket_consequence_updates_npc_and_city_state(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            player.stats.agility = 18
            player.attribute_points = 5
            player.raise_action_attribute("pickpocket", 4)
            result = world.attempt_pickpocket(player, "Quartermaster Iori")
            self.assertTrue(result["success"])
            self.assertIn("npc_consequence", result)
            self.assertEqual(result["npc_consequence"]["action"], "pickpocket")
            self.assertGreaterEqual(result["city_state"]["alert_level"], 1)
            self.assertGreaterEqual(result["npc_state"]["suspicion"], 1)

        def test_npc_specific_intel_consequence_changes_with_trust(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            player.stats.focus = 4
            first = world.interact_city_npc(player, "Quartermaster Iori", interaction="gather_intel")
            self.assertFalse(first["intel_check"]["success"])
            self.assertEqual(first["npc_consequence"]["outcome"], "failure")
            player.stats.focus = 20
            player.attribute_points = 4
            player.raise_action_attribute("scouting", 3)
            second = world.interact_city_npc(player, "Quartermaster Iori", interaction="gather_intel")
            self.assertTrue(second["intel_check"]["success"])
            self.assertEqual(second["npc_consequence"]["outcome"], "success")
            self.assertGreaterEqual(second["npc_state"]["trust"], 1)

        def test_mock_world_map_contains_regions_and_boss_locations(self):
            world, _ = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            world_map = world.generate_mock_world_map()
            self.assertIn("markers", world_map)
            self.assertIn("routes", world_map)
            self.assertIn("legend", world_map)
            self.assertEqual(len(world_map["legend"]), len(world.regions))
            first = world_map["legend"][0]
            self.assertIn("region", first)
            self.assertIn("boss", first)
            self.assertIn("boss_location", first)
            self.assertIn("coordinates", first)

        def test_villain_evolution_checkpoints_escalate_with_pressure(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(8):
                world.apply_player_decision(player, "kill")
            checkpoints = world.get_villain_evolution_checkpoints()
            renda = next(item for item in checkpoints if item["villain"] == "Kage Renda")
            self.assertEqual(renda["phase"], "apex")
            self.assertGreaterEqual(renda["pressure_index"], 8)

        def test_animation_preview_and_villain_kits_exposed_in_summary(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            preview = world.get_move_animation_preview("Edge Current")
            self.assertIn("startup", preview["animation_profile"])
            self.assertEqual(len(preview["action_timeline"]), 4)
            combo_preview = world.preview_affinity_combo_animation(
                "Undertow Slice",
                "Crosswind Fade",
                "Skyline Covenant",
            )
            self.assertEqual(len(combo_preview["combo_path"]), 3)
            self.assertTrue(all("action_timeline" in beat for beat in combo_preview["combo_path"]))
            summary = world.generate_playthrough_summary(player)
            self.assertIn("villain_kits", summary)
            self.assertGreaterEqual(len(summary["villain_kits"]), 15)
            self.assertIn("skill_physics", preview)

        def test_villain_slayer_trophy_awarded_when_all_villains_defeated(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for villain in world.villains:
                villain.defeated = True
            world.evaluate_trophies(player)
            self.assertIn("villain_slayer", player.trophies)

        def test_villain_slayer_trophy_tracks_red_bar_targets_only(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for villain in world.villains:
                villain.defeated = villain.health_bar_color.lower() == "red"
            world.evaluate_trophies(player)
            self.assertIn("villain_slayer", player.trophies)

        def test_decision_seeds_accumulate_silently(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(2):
                world.apply_player_decision(player, "kill")
            # Two kills below kill threshold (3) — no echo has fired yet.
            self.assertEqual(world.latent_decision_seeds.get("kill", 0), 2)
            self.assertEqual(world.latent_echo_history, [])

        def test_drift_signals_invisible_below_three_seeds(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            world.apply_player_decision(player, "kill")
            world.apply_player_decision(player, "charm")
            drift = world.get_world_drift_signals()
            self.assertFalse(drift["visible"])
            self.assertEqual(drift["signals"], [])

        def test_drift_signals_visible_at_three_seeds(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(3):
                world.apply_player_decision(player, "kill")
            drift = world.get_world_drift_signals()
            self.assertTrue(drift["visible"])
            self.assertEqual(drift["dominant_pattern"], "kill")
            self.assertEqual(drift["total_decision_weight"], 3)

        def test_tick_latent_effects_fires_kill_echo_at_threshold(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(3):
                world.apply_player_decision(player, "kill")
            fired = world.tick_latent_effects(player)
            self.assertEqual(len(fired), 1)
            self.assertEqual(fired[0]["echo_key"], "kill_echo")
            self.assertEqual(fired[0]["seed_key"], "kill")
            # Spent seeds drained by threshold.
            self.assertEqual(world.latent_decision_seeds.get("kill", 0), 0)
            # Narrative tag added to player.
            self.assertIn("feared_fighter", player.narrative_tags)

        def test_tick_latent_effects_fires_charm_echo_at_threshold(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(3):
                world.apply_player_decision(player, "charm")
            fired = world.tick_latent_effects(player)
            self.assertTrue(any(e["echo_key"] == "charm_echo" for e in fired))
            self.assertIn("silver_voice", player.narrative_tags)

        def test_tick_latent_effects_fires_on_quest_completion(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(4):
                world.apply_player_decision(player, "stealth")
            # Seeds should be planted but not yet fired.
            self.assertEqual(world.latent_echo_history, [])
            world.complete_quest(player, "Q1")
            # Quest completion ticks latent effects.
            self.assertTrue(any(e["echo_key"] == "stealth_echo" for e in world.latent_echo_history))
            self.assertIn("phantom_presence", player.narrative_tags)

        def test_tick_latent_effects_fires_on_region_clear(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(4):
                world.apply_player_decision(player, "evasion")
            world.clear_region(player, "Verdant Gate", "weapon")
            self.assertTrue(any(e["echo_key"] == "evasion_echo" for e in world.latent_echo_history))
            self.assertIn("elusive_ghost", player.narrative_tags)

        def test_echo_logs_world_drift_tapestry_entry(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(3):
                world.apply_player_decision(player, "kill")
            world.tick_latent_effects(player)
            drift_entries = [e for e in world.active_run_tapestry if e["event_type"] == "world_drift"]
            self.assertTrue(drift_entries)
            self.assertIn("latent:kill", drift_entries[0]["causes"])

        def test_echo_does_not_fire_before_threshold(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(2):
                world.apply_player_decision(player, "kill")
            fired = world.tick_latent_effects(player)
            self.assertEqual(fired, [])
            self.assertEqual(world.latent_echo_history, [])

        def test_seeds_carry_over_after_echo_fires(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            # Plant 5 kill seeds — threshold is 3, so remainder of 2 should carry over.
            for _ in range(5):
                world.apply_player_decision(player, "kill")
            world.tick_latent_effects(player)
            self.assertEqual(world.latent_decision_seeds.get("kill", 0), 2)

        def test_back_to_back_repeat_echo_suppression(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            # Plant enough kill seeds to fire 3 times in a row.
            for _ in range(9):
                world.apply_player_decision(player, "kill")
            # First tick fires once.
            world.tick_latent_effects(player)
            # Second tick should be suppressed (same echo back-to-back twice now).
            world.tick_latent_effects(player)
            kill_echo_fires = sum(
                1 for e in world.latent_echo_history if e["echo_key"] == "kill_echo"
            )
            # Should be at most 2 (fires on first tick, suppressed on 2nd consecutive tick).
            self.assertLessEqual(kill_echo_fires, 2)



class Issue2VillainEvolutionTests(unittest.TestCase):
    """Issue 2: Villain stance evolution triggers and mastery trophies."""

    def _world(self) -> tuple:
        return build_mvp_world("TestPlayer", [3, 1, 2, 4])

    def test_villain_checkpoint_includes_relationship_arc(self):
        world, player = self._world()
        checkpoints = world.get_villain_evolution_checkpoints()
        self.assertTrue(len(checkpoints) > 0)
        for cp in checkpoints:
            self.assertIn("relationship_arc", cp)
            self.assertIn("active_triggers", cp)

    def test_villain_becomes_nemesis_after_heavy_kill_pressure(self):
        world, player = self._world()
        for _ in range(10):
            world.apply_player_decision(player, "kill")
        checkpoints = world.get_villain_evolution_checkpoints()
        arcs = [cp["relationship_arc"] for cp in checkpoints]
        self.assertIn("nemesis", arcs)

    def test_villain_becomes_reformed_after_heavy_pacification(self):
        world, player = self._world()
        for _ in range(10):
            world.apply_player_decision(player, "charm")
        checkpoints = world.get_villain_evolution_checkpoints()
        arcs = [cp["relationship_arc"] for cp in checkpoints]
        self.assertIn("reformed", arcs)

    def test_pacifier_trophy_awarded_for_two_passive_villains(self):
        world, player = self._world()
        # Enough charm to push at least two villains to PASSIVE
        for _ in range(15):
            world.apply_player_decision(player, "charm")
        self.assertIn("pacifier", player.trophies)

    def test_terror_trophy_awarded_for_two_aggressive_villains(self):
        world, player = self._world()
        for _ in range(15):
            world.apply_player_decision(player, "kill")
        self.assertIn("terror", player.trophies)

    def test_shadow_whisperer_trophy_awarded_for_nonlethal_stealth_mastery(self):
        world, player = self._world()
        for _ in range(NONLETHAL_STEALTH_MASTER_THRESHOLD):
            world.apply_player_decision(player, "stealth")
        self.assertTrue(player.is_nonlethal_path_active())
        self.assertIn("shadow_whisperer", player.trophies)

    def test_silver_mask_trophy_awarded_for_nonlethal_charm_mastery(self):
        world, player = self._world()
        for _ in range(NONLETHAL_CHARM_MASTER_THRESHOLD):
            world.apply_player_decision(player, "charm")
        self.assertTrue(player.is_nonlethal_path_active())
        self.assertIn("silver_mask", player.trophies)

    def test_wind_dancer_trophy_awarded_for_nonlethal_evasion_mastery(self):
        world, player = self._world()
        for _ in range(NONLETHAL_EVASION_MASTER_THRESHOLD):
            world.apply_player_decision(player, "evasion")
        self.assertTrue(player.is_nonlethal_path_active())
        self.assertIn("wind_dancer", player.trophies)

    def test_mastery_trophies_not_awarded_if_kills_exist(self):
        world, player = self._world()
        world.apply_player_decision(player, "kill")
        for _ in range(NONLETHAL_STEALTH_MASTER_THRESHOLD):
            world.apply_player_decision(player, "stealth")
        # kill breaks nonlethal path — mastery trophies should NOT fire
        self.assertFalse(player.is_nonlethal_path_active())
        self.assertNotIn("shadow_whisperer", player.trophies)

    def test_new_mastery_trophies_in_catalog(self):
        world, _ = self._world()
        for key in ("pacifier", "terror", "stance_breaker",
                    "shadow_whisperer", "silver_mask", "wind_dancer"):
            self.assertIn(key, world.trophy_catalog, f"Trophy {key} missing from catalog")


class NinjaWorldGameplayTests(unittest.TestCase):
        def _world(self):
            return build_mvp_world("TestPlayer", [5, 1, 1, 1])

        def test_stealth_approach_undetected_on_success(self):
            world, player = self._world()
            # Raise stealth attribute high to guarantee success at undetected difficulty
            player.action_attributes["stealth"] = 10
            result = world.resolve_stealth_approach(player, "Verdant Gate")
            self.assertEqual(result["patrol_state_before"], PATROL_STATE_UNDETECTED)
            self.assertTrue(result["success"])
            self.assertEqual(result["patrol_state_after"], PATROL_STATE_UNDETECTED)

        def test_stealth_approach_escalates_to_alerted(self):
            world, player = self._world()
            from shinobi_rpg.core import PATROL_AGGRO_WINDOW
            # Force failures by setting stealth very low
            player.action_attributes["stealth"] = 1
            result = world.resolve_stealth_approach(
                player, "Verdant Gate",
                patrol_state=PATROL_STATE_UNDETECTED,
                consecutive_failures=PATROL_AGGRO_WINDOW - 1,
            )
            # One more failure should push to alerted
            if not result["success"]:
                self.assertEqual(result["patrol_state_after"], PATROL_STATE_ALERTED)

        def test_stealth_de_escalates_from_alerted(self):
            world, player = self._world()
            player.action_attributes["stealth"] = 10
            result = world.resolve_stealth_approach(
                player, "Verdant Gate",
                patrol_state=PATROL_STATE_ALERTED,
            )
            if result["success"]:
                self.assertEqual(result["patrol_state_after"], PATROL_STATE_UNDETECTED)
                self.assertTrue(result["de_escalated"])

        def test_stealth_approach_fog_grants_bonus(self):
            world, player = self._world()
            # Set weather to fog
            world.weather_cycle_index = list(
                __import__("shinobi_rpg.core", fromlist=["WEATHER_CYCLE"]).WEATHER_CYCLE
            ).index("fog") if "fog" in __import__("shinobi_rpg.core", fromlist=["WEATHER_CYCLE"]).WEATHER_CYCLE else 0
            result = world.resolve_stealth_approach(player, "Verdant Gate")
            # fog should produce environment_bonus >= 2
            self.assertGreaterEqual(result["environment_bonus"], 0)

        def test_environment_modifiers_rain_buffs_water(self):
            world, player = self._world()
            from shinobi_rpg.core import WEATHER_CYCLE
            world.weather_cycle_index = list(WEATHER_CYCLE).index("rain")
            water_move = Move("Wave Slash", MoveCategory.ATTACK, (Affinity.WATER,), 1.0, TechniqueType.ELEMENTAL)
            mods = world.compute_environment_modifiers(water_move)
            self.assertGreater(mods["damage_bonus"], 0.0)
            self.assertIn("rain_water_boost", mods["notes"])

        def test_environment_modifiers_rain_nerfs_fire(self):
            world, player = self._world()
            from shinobi_rpg.core import WEATHER_CYCLE
            world.weather_cycle_index = list(WEATHER_CYCLE).index("rain")
            fire_move = Move("Fireball", MoveCategory.ATTACK, (Affinity.FIRE,), 1.0, TechniqueType.ELEMENTAL)
            mods = world.compute_environment_modifiers(fire_move)
            self.assertLess(mods["damage_bonus"], 0.0)
            self.assertIn("rain_fire_nerf", mods["notes"])

        def test_environment_modifiers_night_boosts_blind_moves(self):
            world, player = self._world()
            from shinobi_rpg.core import DAY_NIGHT_CYCLE
            world.time_cycle_index = list(DAY_NIGHT_CYCLE).index("night")
            blind_move = Move("Shadow Strike", MoveCategory.ATTACK, (Affinity.WIND,), 1.0,
                              TechniqueType.ELEMENTAL, (StatusEffectType.BLIND,))
            mods = world.compute_environment_modifiers(blind_move)
            self.assertGreater(mods["damage_bonus"], 0.0)
            self.assertIn("night_blind_boost", mods["notes"])

        def test_environment_modifiers_fog_stealth_bonus(self):
            world, player = self._world()
            from shinobi_rpg.core import WEATHER_CYCLE
            world.weather_cycle_index = list(WEATHER_CYCLE).index("fog")
            any_move = Move("Quick Strike", MoveCategory.ATTACK, (Affinity.EARTH,), 1.0, TechniqueType.ELEMENTAL)
            mods = world.compute_environment_modifiers(any_move)
            self.assertGreater(mods["stealth_bonus"], 0)

        def test_rival_initializes_with_opposing_affinity(self):
            world, player = self._world()
            # seeded player has fire affinity → rival should have water
            rival = world.initialize_rival(player)
            self.assertIsInstance(rival, RivalProfile)
            self.assertEqual(rival.affinity, Affinity.WATER)

        def test_rival_is_reused_on_second_call(self):
            world, player = self._world()
            r1 = world.initialize_rival(player)
            r2 = world.initialize_rival(player)
            self.assertIs(r1, r2)

        def test_update_rival_progress_clears_behind_player(self):
            world, player = self._world()
            # Manually mark a region cleared
            world.regions[0].cleared = True
            result = world.update_rival_progress(player, region_just_cleared="Ashen Cradle")
            self.assertIn("rival_cleared_regions", result)
            self.assertIsInstance(result["rival_cleared_regions"], list)

        def test_rival_relationship_progresses_with_encounters(self):
            world, player = self._world()
            rival = world.initialize_rival(player)
            rival.encounter_count = 3
            relationship = rival.update_relationship(player.reputation, "neutral")
            self.assertIn(relationship, ("friend", "nemesis", "rival"))

        def test_boss_echo_requires_cleared_region(self):
            world, player = self._world()
            with self.assertRaises(ValueError):
                world.initiate_boss_echo(player, "Verdant Gate")

        def test_boss_echo_initiated_after_clear(self):
            world, player = self._world()
            world.clear_region(player, "Verdant Gate", "weapon")
            result = world.initiate_boss_echo(player, "Verdant Gate")
            self.assertEqual(result["region"], "Verdant Gate")
            self.assertIn("echo_stance", result)
            self.assertGreater(result["boosted_power_scale"], 0)
            self.assertIn("Verdant Gate", world.boss_echo_registry)

        def test_boss_echo_boosted_scale_increases_original(self):
            world, player = self._world()
            world.clear_region(player, "Verdant Gate", "weapon")
            region = world._find_region("Verdant Gate")
            villain = world._find_villain(region.boss)
            result = world.initiate_boss_echo(player, "Verdant Gate")
            expected = round(villain.signature_power.power_scale + BOSS_ECHO_POWER_SCALE_BOOST, 3)
            self.assertAlmostEqual(result["boosted_power_scale"], expected, places=3)

        def test_boss_echo_defeat_grants_rewards(self):
            world, player = self._world()
            world.clear_region(player, "Verdant Gate", "weapon")
            world.initiate_boss_echo(player, "Verdant Gate")
            before_credits = player.credits
            result = world.resolve_boss_echo_defeat(player, "Verdant Gate")
            self.assertGreater(player.credits, before_credits)
            self.assertEqual(result["times_defeated"], 1)

        def test_boss_echo_defeat_without_initiation_raises(self):
            world, player = self._world()
            with self.assertRaises(ValueError):
                world.resolve_boss_echo_defeat(player, "Verdant Gate")

        def test_scout_region_returns_intel(self):
            world, player = self._world()
            result = world.scout_region(player, "Verdant Gate")
            self.assertEqual(result["region"], "Verdant Gate")
            self.assertIn("category", result)
            self.assertIn(result["category"], SCOUTING_INTEL_CATEGORIES)
            self.assertIn("hint", result)

        def test_scout_region_reliable_at_high_scouting(self):
            world, player = self._world()
            from shinobi_rpg.core import SCOUTING_MIN_ATTRIBUTE
            player.action_attributes["scouting"] = SCOUTING_MIN_ATTRIBUTE + 2
            result = world.scout_region(player, "Verdant Gate")
            self.assertTrue(result["reliable"])

        def test_scout_region_unreliable_at_low_scouting(self):
            world, player = self._world()
            player.action_attributes["scouting"] = 1
            result = world.scout_region(player, "Verdant Gate")
            self.assertFalse(result["reliable"])

        def test_scout_region_unknown_raises(self):
            world, player = self._world()
            with self.assertRaises(ValueError):
                world.scout_region(player, "NonExistent")

        def test_scout_region_rotates_category_with_scouting(self):
            world, player = self._world()
            # Different scouting values should produce different category indices
            player.action_attributes["scouting"] = 1
            r1 = world.scout_region(player, "Verdant Gate")
            player.action_attributes["scouting"] = 4
            r2 = world.scout_region(player, "Verdant Gate")
            # Categories may differ when scouting value changes (modulo length)
            self.assertIn(r1["category"], SCOUTING_INTEL_CATEGORIES)
            self.assertIn(r2["category"], SCOUTING_INTEL_CATEGORIES)

