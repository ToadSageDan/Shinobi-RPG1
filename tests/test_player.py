import unittest
from shinobi_rpg.core import (
    AFFINITY_RESONANCE_PAIRS,
    Affinity,
    Backstory,
    CHAKRA_MAX,
    CHAKRA_START,
    CHAKRA_REGEN_ESCAPE,
    CHAKRA_COST,
    HEROIC_THRESHOLD_MIN,
    KARMIC_INHERITANCE_REP_BONUS,
    MOVE_PROFICIENCY_DEFAULT,
    MOVE_PROFICIENCY_MAX,
    MOVE_PROFICIENCY_LOW_THRESHOLD,
    MOVE_PROFICIENCY_SCALE_FLOOR,
    NONLETHAL_FLOW_CHAIN_THRESHOLD,
    REPUTATION_DECAY_INACTIVITY_TICKS,
    REPUTATION_DECAY_AMOUNT,
    ROGUE_THRESHOLD_MIN,
    TechniqueType,
    Move,
    MoveCategory,
    NONLETHAL_CHARM_REP_GAIN,
    PlayerProfile,
    ReputationTier,
    STATUS_EFFECT_BANDS,
    StatusEffectType,
    TROPHY_GHOST_STEP,
    TrophyCategory,
    TrophyTier,
    WEAPON_DURABILITY_LOW_THRESHOLD,
    WEAPON_DURABILITY_MAX,
    WEAPON_DURABILITY_SCALE_FLOOR,
    WEAPON_DURABILITY_START,
    assign_affinity_from_choices,
    build_mvp_world,
    resolve_affinity_minigame,
)


class PlayerCoreTests(unittest.TestCase):
        def _get_unlocked_move_names(self, player: PlayerProfile) -> set[str]:
            return {move.name for moves in player.moves_by_set.values() for move in moves}

        def _get_region(self, world, region_name: str):
            region = next((item for item in world.regions if item.name == region_name), None)
            self.assertIsNotNone(region, f"Expected region '{region_name}' to exist in seeded world.")
            return region

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
            self.assertIn("combat_physics", result)
            self.assertIn("combat_targeting", result)
            self.assertEqual(result["combat_targeting"]["mode"], "straight_line")
            self.assertFalse(result["combat_targeting"]["tracking_required"])
            self.assertEqual(result["combat_physics"]["blood_intensity"], "none")

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

        def test_move_power_scales_stay_within_balance_bands(self):
            world, _ = build_mvp_world("TestPlayer", [5, 1, 1, 1])
            balance_bands = {
                MoveCategory.ESCAPE: (0.6, 0.8),
                MoveCategory.ATTACK: (1.0, 1.15),
                MoveCategory.DEFENSE: (0.7, 1.0),
                MoveCategory.SUMMON: (1.0, 1.15),
                MoveCategory.ULTIMATE: (2.2, 2.6),
            }
            for move in world.technique_library:
                with self.subTest(move=move.name, category=move.category.value):
                    lower, upper = balance_bands[move.category]
                    self.assertGreaterEqual(move.power_scale, lower)
                    self.assertLessEqual(move.power_scale, upper)

        def test_ultimate_damage_is_impactful_but_not_broken(self):
            world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
            strongest_attack = max(
                player.execute_move(move.name)["damage"] for move in player.moves_by_set[MoveCategory.ATTACK]
            )
            for move in player.moves_by_set[MoveCategory.ULTIMATE]:
                with self.subTest(ultimate=move.name):
                    damage = player.execute_move(move.name)["damage"]
                    self.assertGreaterEqual(damage, strongest_attack * 4)
                    self.assertLessEqual(damage, strongest_attack * 5)

        def test_execute_summon_move_uses_focus_and_defense(self):
            world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
            summon_name = player.moves_by_set[MoveCategory.SUMMON][0].name
            result = player.execute_move(summon_name)
            self.assertEqual(result["category"], "summon")
            self.assertEqual(result["summon_type"], TechniqueType.SUMMONING.value)
            self.assertEqual(result["summon_power"], 20)

        def test_lock_on_enables_tracking_for_targeted_attacks(self):
            world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
            result = player.execute_move("Ash Fang Drive", target_name="Kage Renda", lock_on=True)
            self.assertEqual(player.locked_on_target, "Kage Renda")
            self.assertEqual(result["combat_targeting"]["mode"], "tracking")
            self.assertTrue(result["combat_targeting"]["tracking_required"])
            self.assertTrue(result["combat_targeting"]["tracking_applied"])
            self.assertEqual(result["combat_targeting"]["target"], "Kage Renda")

        def test_lock_on_requires_target_when_unset(self):
            world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
            with self.assertRaisesRegex(ValueError, "Lock-on requires a target name"):
                player.execute_move("Ash Fang Drive", lock_on=True)

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

        def test_nonlethal_path_and_trophy_unlock(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for decision in ["stealth", "stealth", "stealth", "charm", "evasion"]:
                world.apply_player_decision(player, decision)
            self.assertTrue(player.is_nonlethal_path_active())
            self.assertIn("ghost_step", player.trophies)
            self.assertIn("pacifist_shadow", player.trophies)

        def test_trophy_catalog_uses_categories_and_progression_unlocks(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            world.clear_region(player, "Verdant Gate", "weapon")
            self.assertIn("first_bloodline_victory", player.trophies)
            self.assertEqual(
                world.trophy_catalog["first_bloodline_victory"].category,
                TrophyCategory.PROGRESSION,
            )

        def test_trophy_progress_contains_near_miss(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(2):
                world.apply_player_decision(player, "stealth")
            progress = world.get_trophy_progress(player)
            ghost_step = next(item for item in progress if item["key"] == "ghost_step")
            self.assertEqual(ghost_step["remaining"], 1)
            self.assertTrue(ghost_step["near_miss"])

        def test_next_five_trophies_are_seeded(self):
            world, _ = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for trophy_key in [
                "silent_legend",
                "phantom_veil",
                "harmony_voice",
                "untouchable_ghost",
                "trinity_operator",
            ]:
                self.assertIn(trophy_key, world.trophy_catalog)

        def test_high_mastery_nonlethal_trophies_unlock(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(8):
                world.apply_player_decision(player, "stealth")
                world.apply_player_decision(player, "charm")
            for _ in range(5):
                world.apply_player_decision(player, "evasion")
            self.assertIn("phantom_veil", player.trophies)
            self.assertIn("harmony_voice", player.trophies)
            self.assertIn("untouchable_ghost", player.trophies)

        def test_trinity_operator_requires_balanced_nonlethal_choices(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for decision in ["stealth", "stealth", "charm", "charm", "evasion", "evasion"]:
                world.apply_player_decision(player, decision)
            self.assertIn("trinity_operator", player.trophies)

        def test_silent_legend_unlocks_on_full_nonlethal_world_clear(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for decision in ["stealth", "charm", "evasion"]:
                world.apply_player_decision(player, decision)
            for region in world.regions:
                world.clear_region(player, region.name, "weapon")
            self.assertIn("silent_legend", player.trophies)

        def test_silent_legend_blocked_if_kill_occurs(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            world.apply_player_decision(player, "kill")
            world.apply_player_decision(player, "stealth")
            for region in world.regions:
                world.clear_region(player, region.name, "weapon")
            self.assertNotIn("silent_legend", player.trophies)

        def test_ninjutsu_catalog_offers_diverse_affinity_and_summon_paths(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            self.assertGreaterEqual(len(world.technique_library), 20)
            summon_catalog = world.get_technique_catalog(technique_type=TechniqueType.SUMMONING)
            self.assertTrue(summon_catalog)
            self.assertTrue(any(item["category"] == MoveCategory.SUMMON.value for item in summon_catalog))

        def test_shared_move_pool_is_evenly_represented(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            counts = {category: 0 for category in MoveCategory}
            for move in world.technique_library:
                counts[move.category] += 1
            # Each base category has at least 12 moves; enemy-exclusive moves add to attack/defense/escape
            self.assertTrue(all(count >= 12 for count in counts.values()))

        def test_execute_move_applies_status_effects(self):
            world, player = build_mvp_world("TestPlayer", [5, 1, 1, 1])
            result = player.execute_move("Cinder Lance")
            self.assertIn(StatusEffectType.BURN.value, result["applied_statuses"])
            self.assertIn(StatusEffectType.BURN.value, player.active_status_effects)
            self.assertEqual(player.active_status_effects[StatusEffectType.BURN.value]["duration"], 2)
            self.assertEqual(player.active_status_effects[StatusEffectType.BURN.value]["stacks"], 1)

        def test_combo_resolution_applies_status_synergy_bonus(self):
            world, player = build_mvp_world("TestPlayer", [1, 5, 1, 1])
            skyline = next(move for move in world.technique_library if move.name == "Skyline Covenant")
            player.add_move(skyline, allow_cross_affinity=True)
            combo = player.resolve_combo("Undertow Slice", "Tidal Blink", "Skyline Covenant")
            self.assertEqual(combo["combo_bonus"], "storm_burst")
            self.assertGreater(combo["total_damage"], combo["base_damage"])

        def test_dual_affinity_animation_preview_blends_both_affinity_signatures(self):
            world, _ = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            preview = world.get_move_animation_preview("Tempest Throne Collapse")
            self.assertIn("compressed air ring gathers", preview["animation_profile"]["startup"])
            self.assertIn("seal stamp with rising rock plates", preview["animation_profile"]["startup"])
            self.assertIn("pressure ripple cross-cut", preview["animation_profile"]["hit"])
            self.assertIn("fissure burst and heavy camera thud", preview["animation_profile"]["hit"])

        def test_battle_hardened_trophy_awarded_at_five_kills(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(5):
                world.apply_player_decision(player, "kill")
            self.assertIn("battle_hardened", player.trophies)
            self.assertNotIn("war_veteran", player.trophies)

        def test_war_veteran_trophy_awarded_at_twenty_kills(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(20):
                world.apply_player_decision(player, "kill")
            self.assertIn("war_veteran", player.trophies)

        def test_crimson_reaper_trophy_awarded_at_thirty_five_kills(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(35):
                world.apply_player_decision(player, "kill")
            self.assertIn("crimson_reaper", player.trophies)
            self.assertNotIn("apex_predator", player.trophies)

        def test_apex_predator_trophy_awarded_at_fifty_kills(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for _ in range(50):
                world.apply_player_decision(player, "kill")
            self.assertIn("apex_predator", player.trophies)

        def test_rising_ninja_trophy_awarded_at_level_5(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            # Levels 1→2: 100, 2→3: 200, 3→4: 300, 4→5: 400 = 1000 XP total
            player.stats.gain_xp(1000)
            world.evaluate_trophies(player)
            self.assertIn("rising_ninja", player.trophies)

        def test_seasoned_ninja_trophy_awarded_at_level_10(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            # 100+200+300+400+500+600+700+800+900 = 4500 XP to reach level 10
            player.stats.gain_xp(4500)
            world.evaluate_trophies(player)
            self.assertIn("seasoned_ninja", player.trophies)

        def test_loyal_bonds_trophy_awarded_with_three_high_loyalty_allies(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for ally in ["Dan", "Moon", "Sleep"]:
                for _ in range(5):
                    player.adjust_ally_loyalty(ally, 1)
            world.evaluate_trophies(player)
            self.assertIn("loyal_bonds", player.trophies)

        def test_loyal_bonds_not_awarded_with_only_two_high_loyalty_allies(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            for ally in ["Dan", "Moon"]:
                for _ in range(5):
                    player.adjust_ally_loyalty(ally, 1)
            world.evaluate_trophies(player)
            self.assertNotIn("loyal_bonds", player.trophies)

        def test_new_trophy_keys_registered_in_catalog(self):
            world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            expected_keys = {
                "battle_hardened",
                "war_veteran",
                "crimson_reaper",
                "apex_predator",
                "rising_ninja",
                "seasoned_ninja",
                "loyal_bonds",
                "villain_slayer",
                "questmaster",
                "shadow_heir",
                "ghost_sovereign",
                "monk_ascendant",
            }
            for key in expected_keys:
                self.assertIn(key, world.trophy_catalog, f"Trophy '{key}' missing from catalog")

        def test_new_trophy_tiers_are_correct(self):
            world, _ = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            self.assertEqual(world.trophy_catalog["battle_hardened"].tier, TrophyTier.EARLY)
            self.assertEqual(world.trophy_catalog["war_veteran"].tier, TrophyTier.MID)
            self.assertEqual(world.trophy_catalog["crimson_reaper"].tier, TrophyTier.LATE)
            self.assertEqual(world.trophy_catalog["apex_predator"].tier, TrophyTier.LATE)
            self.assertEqual(world.trophy_catalog["rising_ninja"].tier, TrophyTier.EARLY)
            self.assertEqual(world.trophy_catalog["seasoned_ninja"].tier, TrophyTier.MID)
            self.assertEqual(world.trophy_catalog["villain_slayer"].tier, TrophyTier.LATE)
            self.assertEqual(world.trophy_catalog["questmaster"].tier, TrophyTier.LATE)
            self.assertEqual(world.trophy_catalog["shadow_heir"].tier, TrophyTier.LATE)



class PlayerGameplayImprovementsTests(unittest.TestCase):
        def _world(self):
            return build_mvp_world("TestPlayer", [5, 1, 1, 1])

        def test_resonance_returns_none_when_only_one_affinity(self):
            world, player = self._world()
            # seeded player starts with fire-only non-ultimate moves; no resonance expected
            result = player.get_affinity_resonance()
            self.assertEqual(result["label"], "none")
            self.assertEqual(result["damage_bonus"], 0.0)

        def test_resonance_activates_when_two_complementary_affinities_present(self):
            _, player = self._world()
            wind_move = Move("Wind Slash", MoveCategory.ATTACK, (Affinity.WIND,), 1.0, TechniqueType.ELEMENTAL)
            player.add_move(wind_move, allow_cross_affinity=True)
            water_move = Move("Water Blade", MoveCategory.ATTACK, (Affinity.WATER,), 1.0, TechniqueType.ELEMENTAL)
            player.add_move(water_move, allow_cross_affinity=True)
            result = player.get_affinity_resonance()
            # wind + water = Storm Doctrine
            self.assertEqual(result["label"], "Storm Doctrine")
            self.assertGreater(result["damage_bonus"], 0.0)
            self.assertIn("wind", result["affinities"])
            self.assertIn("water", result["affinities"])

        def test_resonance_selects_highest_bonus_pair(self):
            _, player = self._world()
            # Add all four affinities so multiple pairs are active
            for affinity in (Affinity.WIND, Affinity.WATER, Affinity.EARTH):
                m = Move(f"Test {affinity.value}", MoveCategory.ATTACK, (affinity,), 1.0, TechniqueType.ELEMENTAL)
                player.add_move(m, allow_cross_affinity=True)
            result = player.get_affinity_resonance()
            # The result should have the highest damage_bonus available
            max_bonus = max(spec["damage_bonus"] for spec in AFFINITY_RESONANCE_PAIRS.values())
            self.assertLessEqual(result["damage_bonus"], max_bonus)
            self.assertGreater(result["damage_bonus"], 0.0)

        def test_invoke_ally_ability_requires_loyalty(self):
            world, player = self._world()
            # Loyalty starts at 0 — should fail
            with self.assertRaises(ValueError):
                world.invoke_ally_ability(player, "Dan")

        def test_invoke_ally_ability_applies_stat_bonus(self):
            world, player = self._world()
            player.adjust_ally_loyalty("Dan", 5)
            before_defense = player.stats.defense
            result = world.invoke_ally_ability(player, "Dan")
            self.assertEqual(result["ally"], "Dan")
            self.assertIn("stat_bonus", result)
            self.assertGreater(player.stats.defense, before_defense)

        def test_invoke_ally_ability_sleep_applies_status_effects(self):
            world, player = self._world()
            player.adjust_ally_loyalty("Sleep", 5)
            result = world.invoke_ally_ability(player, "Sleep")
            self.assertIn("applied_statuses", result)
            self.assertIn("bleed", result["applied_statuses"])

        def test_invoke_ally_ability_porter_restores_chakra(self):
            world, player = self._world()
            player.adjust_ally_loyalty("Porter", 5)
            player.chakra = 20  # deplete chakra first
            result = world.invoke_ally_ability(player, "Porter")
            self.assertIn("chakra_restored", result)
            self.assertGreater(player.chakra, 20)

        def test_invoke_ally_ability_unknown_ally_raises(self):
            world, player = self._world()
            with self.assertRaises(ValueError):
                world.invoke_ally_ability(player, "NonExistentAlly")

        def test_player_starts_with_default_chakra(self):
            _, player = self._world()
            self.assertEqual(player.chakra, CHAKRA_START)

        def test_consume_chakra_deducts_correct_amount(self):
            _, player = self._world()
            before = player.chakra
            success = player.consume_chakra("attack")
            self.assertTrue(success)
            self.assertEqual(player.chakra, before - CHAKRA_COST["attack"])

        def test_consume_chakra_escape_restores(self):
            _, player = self._world()
            player.chakra = 50
            player.consume_chakra("escape")
            self.assertEqual(player.chakra, 50 + CHAKRA_REGEN_ESCAPE)

        def test_consume_chakra_escape_does_not_exceed_max(self):
            _, player = self._world()
            player.chakra = CHAKRA_MAX - 5
            player.consume_chakra("escape")
            self.assertEqual(player.chakra, CHAKRA_MAX)

        def test_consume_chakra_fails_when_insufficient(self):
            _, player = self._world()
            player.chakra = 0
            result = player.consume_chakra("ultimate")
            self.assertFalse(result)
            self.assertEqual(player.chakra, 0)

        def test_restore_chakra_capped_at_max(self):
            _, player = self._world()
            player.chakra = CHAKRA_MAX
            new_val = player.restore_chakra(50)
            self.assertEqual(new_val, CHAKRA_MAX)

        def test_restore_chakra_negative_raises(self):
            _, player = self._world()
            with self.assertRaises(ValueError):
                player.restore_chakra(-1)

        def test_reputation_decay_moves_positive_rep_toward_zero(self):
            world, player = self._world()
            player.reputation = 10
            player.reputation_inactivity_ticks = REPUTATION_DECAY_INACTIVITY_TICKS - 1
            result = world.tick_reputation_decay(player)
            self.assertEqual(result["decayed_units"], 1)
            self.assertEqual(player.reputation, 10 - REPUTATION_DECAY_AMOUNT)

        def test_reputation_decay_moves_negative_rep_toward_zero(self):
            world, player = self._world()
            player.reputation = -10
            player.reputation_inactivity_ticks = REPUTATION_DECAY_INACTIVITY_TICKS - 1
            result = world.tick_reputation_decay(player)
            self.assertEqual(result["decayed_units"], 1)
            self.assertEqual(player.reputation, -10 + REPUTATION_DECAY_AMOUNT)

        def test_reputation_no_decay_when_inactivity_not_reached(self):
            world, player = self._world()
            player.reputation = 20
            player.reputation_inactivity_ticks = 0
            result = world.tick_reputation_decay(player, ticks=1)
            self.assertEqual(result["decayed_units"], 0)
            self.assertEqual(player.reputation, 20)

        def test_reputation_decay_zero_reputation_no_change(self):
            world, player = self._world()
            player.reputation = 0
            player.reputation_inactivity_ticks = REPUTATION_DECAY_INACTIVITY_TICKS - 1
            result = world.tick_reputation_decay(player)
            self.assertEqual(result["decayed_units"], 0)
            self.assertEqual(player.reputation, 0)

        def test_tick_reputation_decay_invalid_ticks_raises(self):
            world, player = self._world()
            with self.assertRaises(ValueError):
                world.tick_reputation_decay(player, ticks=0)

        def test_use_move_proficiency_raises_degraded(self):
            _, player = self._world()
            move_name = "Edge Current"
            player.move_proficiency[move_name] = 10
            result = player.use_move_proficiency(move_name)
            self.assertGreater(result["proficiency"], 10)
            self.assertEqual(result["move"], move_name)

        def test_proficiency_scale_modifier_full_at_cap(self):
            self.assertEqual(PlayerProfile._proficiency_scale_modifier(MOVE_PROFICIENCY_MAX), 1.0)

        def test_proficiency_scale_modifier_floor_at_zero(self):
            modifier = PlayerProfile._proficiency_scale_modifier(0)
            self.assertAlmostEqual(modifier, MOVE_PROFICIENCY_SCALE_FLOOR, places=5)

        def test_proficiency_scale_modifier_one_at_threshold(self):
            self.assertEqual(PlayerProfile._proficiency_scale_modifier(MOVE_PROFICIENCY_LOW_THRESHOLD), 1.0)

        def test_decay_unused_moves_reduces_proficiency(self):
            _, player = self._world()
            move_name = "Edge Current"
            player.move_proficiency[move_name] = MOVE_PROFICIENCY_DEFAULT
            decayed = player.decay_unused_move_proficiency([])
            self.assertIn(move_name, decayed)
            self.assertLess(decayed[move_name], MOVE_PROFICIENCY_DEFAULT)

        def test_train_move_restores_proficiency(self):
            world, player = self._world()
            move_name = "Edge Current"
            player.move_proficiency[move_name] = 20
            player.credits = 1000
            result = world.train_move(player, move_name)
            self.assertEqual(result["proficiency_after"], MOVE_PROFICIENCY_MAX)
            self.assertGreater(result["credits_spent"], 0)

        def test_train_move_unlocked_only(self):
            world, player = self._world()
            with self.assertRaises(ValueError):
                world.train_move(player, "UnknownMove")

        def test_nonlethal_flow_streak_increments_on_nonlethal(self):
            _, player = self._world()
            result = player.record_nonlethal_chain("stealth")
            self.assertEqual(result["streak"], 1)
            self.assertFalse(result["flow_active"])

        def test_nonlethal_flow_activates_at_threshold(self):
            _, player = self._world()
            for _ in range(NONLETHAL_FLOW_CHAIN_THRESHOLD):
                result = player.record_nonlethal_chain("charm")
            self.assertTrue(result["flow_active"])
            self.assertTrue(result["free_evasion_available"])

        def test_nonlethal_flow_resets_on_kill(self):
            _, player = self._world()
            player.nonlethal_flow_streak = NONLETHAL_FLOW_CHAIN_THRESHOLD
            result = player.record_nonlethal_chain("kill")
            self.assertEqual(result["streak"], 0)
            self.assertFalse(result["flow_active"])

        def test_nonlethal_flow_stealth_buff_duration(self):
            _, player = self._world()
            player.nonlethal_flow_streak = NONLETHAL_FLOW_CHAIN_THRESHOLD - 1
            result = player.record_nonlethal_chain("evasion")
            if result["flow_active"]:
                self.assertGreater(result["stealth_buff_duration"], 0)

        def test_trophy_near_miss_live_returns_list(self):
            world, player = self._world()
            result = world.get_trophy_near_miss_live(player)
            self.assertIsInstance(result, list)

        def test_trophy_near_miss_live_shows_close_trophies(self):
            world, player = self._world()
            # Set stealth just one short of the ghost_step threshold
            from shinobi_rpg.core import STEALTH_TROPHY_BASE_THRESHOLD
            player.encounter_outcomes["stealth"] = STEALTH_TROPHY_BASE_THRESHOLD - 1
            result = world.get_trophy_near_miss_live(player)
            keys = [item["trophy_key"] for item in result]
            self.assertIn(TROPHY_GHOST_STEP, keys)

        def test_trophy_near_miss_live_excludes_already_unlocked(self):
            world, player = self._world()
            # Force enough stealth to earn ghost_step
            player.encounter_outcomes["stealth"] = 100
            world.evaluate_trophies(player)
            result = world.get_trophy_near_miss_live(player)
            keys = [item["trophy_key"] for item in result]
            self.assertNotIn(TROPHY_GHOST_STEP, keys)

        def test_weapon_durability_starts_at_full(self):
            _, player = self._world()
            d = player.weapon_durability.get("Dawn Cutter", WEAPON_DURABILITY_START)
            self.assertEqual(d, WEAPON_DURABILITY_START)

        def test_degrade_weapon_reduces_durability(self):
            _, player = self._world()
            from shinobi_rpg.core import WEAPON_DURABILITY_LOSS_PER_USE
            result = player.degrade_weapon("Dawn Cutter")
            expected = WEAPON_DURABILITY_START - WEAPON_DURABILITY_LOSS_PER_USE
            self.assertEqual(result["durability"], expected)

        def test_durability_power_ratio_full_above_threshold(self):
            ratio = PlayerProfile._durability_power_ratio(WEAPON_DURABILITY_LOW_THRESHOLD)
            self.assertEqual(ratio, 1.0)

        def test_durability_power_ratio_floor_at_zero(self):
            ratio = PlayerProfile._durability_power_ratio(0)
            self.assertAlmostEqual(ratio, WEAPON_DURABILITY_SCALE_FLOOR, places=5)

        def test_repair_weapon_restores_to_full(self):
            world, player = self._world()
            player.weapon_durability["Dawn Cutter"] = 10
            player.credits = 5000
            result = world.repair_weapon(player, "Dawn Cutter")
            self.assertEqual(result["durability_after"], WEAPON_DURABILITY_MAX)
            self.assertGreater(result["credits_spent"], 0)

        def test_repair_weapon_unknown_raises(self):
            world, player = self._world()
            with self.assertRaises(ValueError):
                world.repair_weapon(player, "FakeWeapon")

        def test_repair_weapon_insufficient_credits_raises(self):
            world, player = self._world()
            player.weapon_durability["Dawn Cutter"] = 0
            player.credits = 0
            with self.assertRaises(ValueError):
                world.repair_weapon(player, "Dawn Cutter")

        def test_karmic_inheritance_ineligible_with_fewer_than_two_runs(self):
            world, player = self._world()
            result = world.compute_karmic_inheritance()
            self.assertFalse(result["eligible"])

        def test_karmic_inheritance_returns_dominant_heroic_style(self):
            world, player = self._world()
            # Seed vault with two heroic runs
            for _ in range(2):
                world.vault_historic_ninjas.append({
                    "name": "Hero",
                    "reputation": HEROIC_THRESHOLD_MIN,
                    "nonlethal_path": False,
                    "trophies": [],
                    "affinity": "fire",
                    "level": 5,
                    "backstory": None,
                    "credits": 100,
                    "run_signature": {},
                    "living_tapestry": [],
                    "enemy_move_claims": {},
                    "enemy_exclusive_moves": [],
                })
            result = world.compute_karmic_inheritance()
            self.assertTrue(result["eligible"])
            self.assertEqual(result["style"], "heroic")
            self.assertEqual(result["reputation_bonus"], KARMIC_INHERITANCE_REP_BONUS)

        def test_karmic_inheritance_returns_dominant_rogue_style(self):
            world, player = self._world()
            for _ in range(3):
                world.vault_historic_ninjas.append({
                    "name": "Rogue",
                    "reputation": ROGUE_THRESHOLD_MIN,
                    "nonlethal_path": False,
                    "trophies": [],
                    "affinity": "wind",
                    "level": 3,
                    "backstory": None,
                    "credits": 50,
                    "run_signature": {},
                    "living_tapestry": [],
                    "enemy_move_claims": {},
                    "enemy_exclusive_moves": [],
                })
            result = world.compute_karmic_inheritance()
            self.assertTrue(result["eligible"])
            self.assertEqual(result["style"], "rogue")
            self.assertLess(result["reputation_bonus"], 0)

        def test_apply_karmic_inheritance_modifies_player_reputation(self):
            world, player = self._world()
            for _ in range(2):
                world.vault_historic_ninjas.append({
                    "name": "Hero",
                    "reputation": HEROIC_THRESHOLD_MIN,
                    "nonlethal_path": False,
                    "trophies": [],
                    "affinity": "fire",
                    "level": 5,
                    "backstory": None,
                    "credits": 100,
                    "run_signature": {},
                    "living_tapestry": [],
                    "enemy_move_claims": {},
                    "enemy_exclusive_moves": [],
                })
            before = player.reputation
            result = world.apply_karmic_inheritance(player)
            self.assertTrue(result["applied"])
            self.assertNotEqual(player.reputation, before)



class Issue3BalancePassTests(unittest.TestCase):
    """Issue 3: Status-effect stacking, nonlethal reputation viability."""

    def _player(self) -> PlayerProfile:
        _, player = build_mvp_world("BalanceTest", [3, 1, 2, 4])
        return player

    def test_status_effect_stacks_accumulate_not_replace(self):
        player = self._player()
        player.apply_status_effects([StatusEffectType.BLEED], duration=2, stacks=1)
        player.apply_status_effects([StatusEffectType.BLEED], duration=2, stacks=1)
        bleed = player.active_status_effects[StatusEffectType.BLEED.value]
        self.assertEqual(bleed["stacks"], 2)

    def test_status_effect_stacks_respect_band_cap(self):
        player = self._player()
        band_max = STATUS_EFFECT_BANDS[StatusEffectType.BLEED]["max_stacks"]
        for _ in range(band_max + 2):
            player.apply_status_effects([StatusEffectType.BLEED], duration=3, stacks=1)
        bleed = player.active_status_effects[StatusEffectType.BLEED.value]
        self.assertEqual(bleed["stacks"], band_max)

    def test_status_effect_duration_refreshes_to_higher_value(self):
        player = self._player()
        player.apply_status_effects([StatusEffectType.BURN], duration=2, stacks=1)
        player.apply_status_effects([StatusEffectType.BURN], duration=4, stacks=1)
        burn = player.active_status_effects[StatusEffectType.BURN.value]
        self.assertEqual(burn["duration"], 4)

    def test_charm_decision_grants_reputation_gain(self):
        world, player = build_mvp_world("RepTest", [3, 1, 2, 4])
        start_rep = player.reputation
        world.apply_player_decision(player, "charm")
        self.assertGreater(player.reputation, start_rep)

    def test_stealth_decision_grants_reputation_gain(self):
        world, player = build_mvp_world("RepTest", [3, 1, 2, 4])
        start_rep = player.reputation
        world.apply_player_decision(player, "stealth")
        self.assertGreater(player.reputation, start_rep)

    def test_evasion_decision_grants_reputation_gain(self):
        world, player = build_mvp_world("RepTest", [3, 1, 2, 4])
        start_rep = player.reputation
        world.apply_player_decision(player, "evasion")
        self.assertGreater(player.reputation, start_rep)

    def test_kill_decision_reduces_reputation(self):
        world, player = build_mvp_world("RepTest", [3, 1, 2, 4])
        start_rep = player.reputation
        world.apply_player_decision(player, "kill")
        self.assertLess(player.reputation, start_rep)

    def test_nonlethal_path_can_reach_heroic_tier_without_kills(self):
        world, player = build_mvp_world("PacifistTier", [3, 1, 2, 4])
        needed = HEROIC_THRESHOLD_MIN // NONLETHAL_CHARM_REP_GAIN + 1
        for _ in range(needed):
            world.apply_player_decision(player, "charm")
        self.assertEqual(player.current_reputation_tier().value, "heroic")
