import unittest
from tempfile import TemporaryDirectory

from shinobi_rpg.core import (
    Affinity,
    Backstory,
    DEFAULT_ALLY_MIN_COUNT,
    JutsuType,
    Move,
    MoveCategory,
    PlayerProfile,
    QuestStatus,
    ReputationTier,
    StatusEffectType,
    TrophyCategory,
    TrophyTier,
    VillainStance,
    assign_affinity_from_choices,
    build_mvp_world,
    load_world_snapshot,
    resolve_affinity_minigame,
    save_world_snapshot,
)


class CoreSystemTests(unittest.TestCase):
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
        self.assertGreaterEqual(len(world.allies), DEFAULT_ALLY_MIN_COUNT)
        self.assertFalse(
            any(name.startswith("AutoNinja-") for name in world.allies[:DEFAULT_ALLY_MIN_COUNT])
        )

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

    def test_vault_replay_summary_defaults_when_no_runs(self):
        world, _ = build_mvp_world("Dot", [1, 3, 5, 2, 1])
        summary = world.get_vault_replay_summary()
        self.assertEqual(summary["total_runs"], 0)
        self.assertEqual(summary["unique_ninjas"], [])
        self.assertEqual(summary["nonlethal_runs"], 0)
        self.assertEqual(summary["heroic_runs"], 0)
        self.assertEqual(summary["rogue_runs"], 0)
        self.assertIsNone(summary["highest_level_run"])
        self.assertEqual(summary["most_collected_trophies"], [])

    def test_vault_replay_summary_tracks_history_and_trophies(self):
        world, first_player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
        for decision in ["stealth", "stealth", "charm", "charm", "evasion", "evasion"]:
            world.apply_player_decision(first_player, decision)
        first_player.stats.gain_xp(1500)
        first_player.update_reputation(-80)
        world.archive_historic_ninja(first_player)

        _, second_player = build_mvp_world("Moon", [5, 1, 1, 1])
        second_player.update_reputation(80)
        world.archive_historic_ninja(second_player)

        summary = world.get_vault_replay_summary()
        self.assertEqual(summary["total_runs"], 2)
        self.assertEqual(summary["unique_ninjas"], ["Dot", "Moon"])
        self.assertEqual(summary["nonlethal_runs"], 1)
        self.assertEqual(summary["heroic_runs"], 1)
        self.assertEqual(summary["rogue_runs"], 1)
        self.assertEqual(summary["highest_level_run"]["name"], "Dot")
        self.assertIn("trinity_operator", {item["key"] for item in summary["most_collected_trophies"]})

        dot_history = world.get_player_vault_history("Dot")
        self.assertEqual(len(dot_history), 1)
        self.assertEqual(dot_history[0]["name"], "Dot")
        with self.assertRaisesRegex(ValueError, "Player name cannot be empty."):
            world.get_player_vault_history("   ")

    def test_replay_hub_report_combines_active_and_archive_state(self):
        world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
        world.apply_player_decision(player, "stealth")
        world.archive_historic_ninja(player)
        report = world.generate_replay_hub_report(player)
        self.assertIn("active_run", report)
        self.assertIn("vault_overview", report)
        self.assertIn("player_archive_history", report)
        self.assertEqual(report["vault_overview"]["total_runs"], 1)
        self.assertEqual(len(report["player_archive_history"]), 1)

    def test_world_initializes_arc_era_and_living_tapestry(self):
        world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
        summary = world.generate_playthrough_summary(player)
        self.assertIn("arc_state", summary)
        self.assertEqual(summary["arc_state"]["era"]["key"], "war_age")
        self.assertGreaterEqual(len(summary["living_tapestry"]["active_run_entries"]), 1)
        self.assertEqual(summary["living_tapestry"]["active_run_entries"][0]["event_type"], "arc_shift")

    def test_world_event_updates_state_and_logs_cause_effect(self):
        world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
        event = world.trigger_world_event(player, event_key="tornado", causes=["test_driver"])
        self.assertEqual(event["event_key"], "tornado")
        self.assertEqual(event["causes"], ["test_driver"])
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

    def test_archive_captures_run_signature_and_vault_meta_tapestry(self):
        world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
        world.apply_player_decision(player, "charm")
        world.archive_historic_ninja(player)
        archived = world.vault_historic_ninjas[0]
        self.assertIn("run_signature", archived)
        self.assertIn("dominant_arc_path", archived["run_signature"])
        self.assertIn("living_tapestry", archived)
        self.assertGreater(len(world.vault_meta_tapestry), 0)

    def test_replay_hub_report_surfaces_tapestry_delta(self):
        world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
        world.apply_player_decision(player, "stealth")
        world.archive_historic_ninja(player)
        world.apply_player_decision(player, "kill")
        report = world.generate_replay_hub_report(player)
        self.assertIn("living_tapestry_delta", report)
        self.assertIn("event_differences", report["living_tapestry_delta"])

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

    def test_quest_branching_expands_backstory_specific_outcome_for_q2(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        monk = next(backstory for backstory in world.player_backstories if backstory.key == "wandering_monk")
        player.choose_backstory(monk)
        result = world.resolve_quest_branch(player, "Q2")
        self.assertEqual(result["branch_key"], "wandering_monk")
        self.assertIn("de-escalates the ambush", result["outcome"])

    def test_quest_branching_prefers_backstory_key_over_narrative_tag(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        ghost = next(backstory for backstory in world.player_backstories if backstory.key == "street_ghost")
        player.choose_backstory(ghost)
        result = world.resolve_quest_branch(player, "Q1")
        self.assertEqual(result["branch_key"], "street_ghost")
        self.assertIn("underworld contacts", result["outcome"])

    def test_q4_branching_uses_nonlethal_and_reputation_paths(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        for decision in ["stealth", "charm", "evasion"]:
            world.apply_player_decision(player, decision)
        nonlethal = world.resolve_quest_branch(player, "Q4")
        self.assertEqual(nonlethal["branch_key"], "nonlethal_path")

        rogue_world, rogue_player = build_mvp_world("Rogue", [3, 1, 2, 4])
        rogue_player.update_reputation(-60)
        rogue = rogue_world.resolve_quest_branch(rogue_player, "Q4")
        self.assertEqual(rogue["branch_key"], "rogue_path")

        heroic_world, heroic_player = build_mvp_world("Hero", [3, 1, 2, 4])
        heroic_player.update_reputation(60)
        heroic = heroic_world.resolve_quest_branch(heroic_player, "Q4")
        self.assertEqual(heroic["branch_key"], "heroic_path")

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
        world.trigger_external_pressure_event(player, event_key="forbidden_scroll_auction")
        world.discover_world_intel(player, channel="newspaper", stealth_probe=True)
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
        self.assertTrue(restored_world.npc_evil_profiles)
        self.assertTrue(restored_world.external_pressure_history)
        self.assertTrue(restored_world.intel_discovery_log)

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
        world.clear_region(player, "Verdant Gate", "weapon")
        world.clear_region(player, "Ashen Cradle", "weapon")
        world.clear_region(player, "Tideglass Basin", "weapon")
        self.assertIn("silent_legend", player.trophies)

    def test_silent_legend_blocked_if_kill_occurs(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        world.apply_player_decision(player, "kill")
        world.apply_player_decision(player, "stealth")
        world.clear_region(player, "Verdant Gate", "weapon")
        world.clear_region(player, "Ashen Cradle", "weapon")
        world.clear_region(player, "Tideglass Basin", "weapon")
        self.assertNotIn("silent_legend", player.trophies)

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
        self.assertIn("kill_counter", summary)
        self.assertIn("trophy_progress", summary)
        self.assertIn("villain_evolution", summary)
        self.assertIn("npc_evil_profiles", summary)
        self.assertIn("external_pressure_history", summary)
        self.assertIn("intel_discovery_log", summary)
        self.assertEqual(summary["kill_counter"]["total_kills"], 0)

    def test_villain_evolution_checkpoints_escalate_with_pressure(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        for _ in range(8):
            world.apply_player_decision(player, "kill")
        checkpoints = world.get_villain_evolution_checkpoints()
        renda = next(item for item in checkpoints if item["villain"] == "Kage Renda")
        self.assertEqual(renda["phase"], "apex")
        self.assertGreaterEqual(renda["pressure_index"], 8)

    def test_trophy_progress_and_summary_include_tiers(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        for _ in range(3):
            world.apply_player_decision(player, "stealth")
        summary = world.generate_playthrough_summary(player)
        ghost = next(item for item in summary["trophies"] if item["key"] == "ghost_step")
        self.assertEqual(ghost["tier"], TrophyTier.EARLY.value)
        progress = world.get_trophy_progress(player)
        ghost_progress = next(item for item in progress if item["key"] == "ghost_step")
        self.assertEqual(ghost_progress["tier"], TrophyTier.EARLY.value)

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
        self.assertIn("skill_physics", preview)

    def test_snapshot_load_supports_legacy_trophies_without_tier(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        snapshot = world.to_snapshot(player)
        for trophy in snapshot["world"]["trophy_catalog"].values():
            trophy.pop("tier", None)
        restored_world, restored_player = world.from_snapshot(snapshot)
        self.assertEqual(restored_player.name, player.name)
        self.assertEqual(
            restored_world.trophy_catalog["ghost_step"].tier,
            TrophyTier.EARLY,
        )

    # ------------------------------------------------------------------
    # Q6-Q15 quest branching tests
    # ------------------------------------------------------------------

    def test_q6_exists_in_seeded_world(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        quest_ids = [q.quest_id for q in world.quests]
        self.assertIn("Q6", quest_ids)
        self.assertIn("Q7", quest_ids)
        self.assertIn("Q8", quest_ids)
        self.assertIn("Q9", quest_ids)
        self.assertIn("Q10", quest_ids)

    def test_q6_branching_uses_exiled_heir_backstory(self):
        world, player = build_mvp_world("Heir", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[0])  # exiled_heir
        result = world.resolve_quest_branch(player, "Q6")
        self.assertEqual(result["branch_key"], "exiled_heir")
        self.assertIn("bloodline covenant", result["outcome"])

    def test_q6_branching_uses_street_ghost_backstory(self):
        world, player = build_mvp_world("Ghost", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[1])  # street_ghost
        result = world.resolve_quest_branch(player, "Q6")
        self.assertEqual(result["branch_key"], "street_ghost")
        self.assertIn("stolen council sigils", result["outcome"])

    def test_q6_branching_uses_wandering_monk_backstory(self):
        world, player = build_mvp_world("Monk", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[2])  # wandering_monk
        result = world.resolve_quest_branch(player, "Q6")
        self.assertEqual(result["branch_key"], "wandering_monk")
        self.assertIn("unarmed", result["outcome"])

    def test_q6_branching_uses_nonlethal_path(self):
        world, player = build_mvp_world("Pacifist", [3, 1, 2, 4])
        for decision in ["stealth", "charm", "evasion"]:
            world.apply_player_decision(player, decision)
        result = world.resolve_quest_branch(player, "Q6")
        self.assertEqual(result["branch_key"], "nonlethal_path")

    def test_q6_branching_uses_rogue_path(self):
        world, player = build_mvp_world("Rogue", [3, 1, 2, 4])
        player.update_reputation(-60)
        result = world.resolve_quest_branch(player, "Q6")
        self.assertEqual(result["branch_key"], "rogue_path")

    def test_q6_branching_uses_heroic_path(self):
        world, player = build_mvp_world("Hero", [3, 1, 2, 4])
        player.update_reputation(60)
        result = world.resolve_quest_branch(player, "Q6")
        self.assertEqual(result["branch_key"], "heroic_path")

    def test_q6_default_branch_fires_with_no_special_conditions(self):
        world, player = build_mvp_world("Blank", [3, 1, 2, 4])
        result = world.resolve_quest_branch(player, "Q6")
        self.assertEqual(result["branch_key"], "default")

    def test_q7_branching_uses_nonlethal_path(self):
        world, player = build_mvp_world("Pacifist", [3, 1, 2, 4])
        for decision in ["stealth", "charm", "evasion"]:
            world.apply_player_decision(player, decision)
        result = world.resolve_quest_branch(player, "Q7")
        self.assertEqual(result["branch_key"], "nonlethal_path")
        self.assertIn("without a single execution", result["outcome"])

    def test_q8_branching_uses_heroic_path(self):
        world, player = build_mvp_world("Hero", [3, 1, 2, 4])
        player.update_reputation(60)
        result = world.resolve_quest_branch(player, "Q8")
        self.assertEqual(result["branch_key"], "heroic_path")
        self.assertIn("first guardian of the new age", result["outcome"])

    def test_q9_branching_uses_street_ghost_backstory(self):
        world, player = build_mvp_world("Ghost", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[1])  # street_ghost
        result = world.resolve_quest_branch(player, "Q9")
        self.assertEqual(result["branch_key"], "street_ghost")
        self.assertIn("safehouses", result["outcome"])

    def test_q10_branching_uses_nonlethal_path(self):
        world, player = build_mvp_world("Pacifist", [3, 1, 2, 4])
        for decision in ["stealth", "charm", "evasion"]:
            world.apply_player_decision(player, decision)
        result = world.resolve_quest_branch(player, "Q10")
        self.assertEqual(result["branch_key"], "nonlethal_path")
        self.assertIn("without blood debt", result["outcome"].lower())

    def test_q11_branching_uses_exiled_heir_backstory(self):
        world, player = build_mvp_world("Heir", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[0])  # exiled_heir
        result = world.resolve_quest_branch(player, "Q11")
        self.assertEqual(result["branch_key"], "exiled_heir")
        self.assertIn("bloodline", result["outcome"].lower())

    def test_q12_branching_uses_street_ghost_backstory(self):
        world, player = build_mvp_world("Ghost", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[1])  # street_ghost
        result = world.resolve_quest_branch(player, "Q12")
        self.assertEqual(result["branch_key"], "street_ghost")
        self.assertIn("underworld", result["outcome"].lower())

    def test_q13_branching_uses_wandering_monk_backstory(self):
        world, player = build_mvp_world("Monk", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[2])  # wandering_monk
        result = world.resolve_quest_branch(player, "Q13")
        self.assertEqual(result["branch_key"], "wandering_monk")
        self.assertIn("restraint", result["outcome"].lower())

    def test_q14_branching_uses_heroic_path(self):
        world, player = build_mvp_world("Hero", [3, 1, 2, 4])
        player.update_reputation(60)
        result = world.resolve_quest_branch(player, "Q14")
        self.assertEqual(result["branch_key"], "heroic_path")
        self.assertIn("trust", result["outcome"].lower())

    def test_q15_branching_uses_rogue_path(self):
        world, player = build_mvp_world("Rogue", [3, 1, 2, 4])
        player.update_reputation(-60)
        result = world.resolve_quest_branch(player, "Q15")
        self.assertEqual(result["branch_key"], "rogue_path")
        self.assertIn("leverage", result["outcome"].lower())

    def test_q20_branching_uses_stealth_path_when_dominant_outcome(self):
        world, player = build_mvp_world("StealthMain", [3, 1, 2, 4])
        for _ in range(3):
            world.apply_player_decision(player, "stealth")
        world.apply_player_decision(player, "kill")
        world.apply_player_decision(player, "charm")
        result = world.resolve_quest_branch(player, "Q20")
        self.assertEqual(result["branch_key"], "stealth_path")
        self.assertIn("stealth-first tactics", result["outcome"])

    def test_q20_branching_uses_kill_path_when_kill_is_dominant(self):
        world, player = build_mvp_world("AggroMain", [3, 1, 2, 4])
        for _ in range(3):
            world.apply_player_decision(player, "kill")
        result = world.resolve_quest_branch(player, "Q20")
        self.assertEqual(result["branch_key"], "kill_path")
        self.assertIn("brutal conclusion", result["outcome"])

    def test_q16_branching_uses_nonlethal_path(self):
        world, player = build_mvp_world("PacifistMain", [3, 1, 2, 4])
        for decision in ["stealth", "charm", "evasion"]:
            world.apply_player_decision(player, decision)
        result = world.resolve_quest_branch(player, "Q16")
        self.assertEqual(result["branch_key"], "nonlethal_path")
        self.assertIn("without executions", result["outcome"])

    def test_q18_branching_uses_heroic_path(self):
        world, player = build_mvp_world("HeroMain", [3, 1, 2, 4])
        player.update_reputation(60)
        result = world.resolve_quest_branch(player, "Q18")
        self.assertEqual(result["branch_key"], "heroic_path")
        self.assertIn("public support", result["outcome"])

    def test_q19_branching_uses_wandering_monk_backstory(self):
        world, player = build_mvp_world("MonkMain", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[2])  # wandering_monk
        result = world.resolve_quest_branch(player, "Q19")
        self.assertEqual(result["branch_key"], "wandering_monk")
        self.assertIn("restraint", result["outcome"])

    def test_backstory_branching_still_overrides_tactical_path(self):
        world, player = build_mvp_world("GhostMain", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[1])  # street_ghost
        for _ in range(3):
            world.apply_player_decision(player, "stealth")
        result = world.resolve_quest_branch(player, "Q20")
        self.assertEqual(result["branch_key"], "street_ghost")

    def test_seeded_world_extends_quest_chain_to_q50(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        quest_ids = [q.quest_id for q in world.quests]
        self.assertIn("Q40", quest_ids)
        self.assertIn("Q50", quest_ids)
        self.assertEqual(len(quest_ids), 50)

    def test_extended_quests_include_structured_metadata(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        quest = next(q for q in world.quests if q.quest_id == "Q40")
        self.assertTrue(quest.premise)
        self.assertTrue(quest.choices)
        self.assertTrue(quest.rewards)
        self.assertTrue(quest.follow_up_hook)
        self.assertIn("exiled_heir", quest.branch_outcomes)
        self.assertIn("street_ghost", quest.branch_outcomes)
        self.assertIn("wandering_monk", quest.branch_outcomes)
        self.assertIn("default", quest.branch_outcomes)

    def test_resolve_quest_branch_returns_structured_fields(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        result = world.resolve_quest_branch(player, "Q20")
        self.assertIn("premise", result)
        self.assertIn("objective", result)
        self.assertIn("choices", result)
        self.assertIn("rewards", result)
        self.assertIn("follow_up_hook", result)
        self.assertIn("villain_stance_impacts", result)
        self.assertIn("reputation_impacts", result)
        self.assertIn("trophy_hooks", result)

    # ------------------------------------------------------------------
    # New trophy evaluation tests
    # ------------------------------------------------------------------

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

    def test_villain_slayer_trophy_awarded_when_all_villains_defeated(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        for villain in world.villains:
            villain.defeated = True
        world.evaluate_trophies(player)
        self.assertIn("villain_slayer", player.trophies)

    def test_questmaster_trophy_awarded_on_all_quest_completion(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        player.initialize_quest_log([q.quest_id for q in world.quests])
        for quest in world.quests:
            player.set_quest_status(quest.quest_id, QuestStatus.COMPLETED)
        world.evaluate_trophies(player)
        self.assertIn("questmaster", player.trophies)

    def test_shadow_heir_trophy_awarded_for_exiled_heir_world_clear(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[0])  # exiled_heir
        for region in world.regions:
            region.cleared = True
        world.evaluate_trophies(player)
        self.assertIn("shadow_heir", player.trophies)
        self.assertNotIn("ghost_sovereign", player.trophies)
        self.assertNotIn("monk_ascendant", player.trophies)

    def test_ghost_sovereign_trophy_awarded_for_street_ghost_world_clear(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[1])  # street_ghost
        for region in world.regions:
            region.cleared = True
        world.evaluate_trophies(player)
        self.assertIn("ghost_sovereign", player.trophies)
        self.assertNotIn("shadow_heir", player.trophies)

    def test_monk_ascendant_trophy_awarded_for_wandering_monk_world_clear(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[2])  # wandering_monk
        for region in world.regions:
            region.cleared = True
        world.evaluate_trophies(player)
        self.assertIn("monk_ascendant", player.trophies)

    def test_backstory_world_clear_trophies_not_awarded_without_world_clear(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[0])  # exiled_heir, no regions cleared
        world.evaluate_trophies(player)
        self.assertNotIn("shadow_heir", player.trophies)

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

    # ------------------------------------------------------------------
    # Latent decision network tests
    # ------------------------------------------------------------------

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

    def test_latent_fields_persist_in_snapshot_round_trip(self):
        import tempfile, os
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        for _ in range(3):
            world.apply_player_decision(player, "charm")
        world.tick_latent_effects(player)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "snap.json")
            save_world_snapshot(world, player, path)
            restored_world, restored_player = load_world_snapshot(path)
        self.assertEqual(
            restored_world.latent_decision_seeds,
            world.latent_decision_seeds,
        )
        self.assertEqual(len(restored_world.latent_echo_history), len(world.latent_echo_history))
        self.assertIn("silver_voice", restored_player.narrative_tags)

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


if __name__ == "__main__":
    unittest.main()
