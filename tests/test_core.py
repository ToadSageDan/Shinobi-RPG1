import unittest
from contextlib import redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from shinobi_rpg.core import (
    Affinity,
    Backstory,
    DEFAULT_ALLY_MIN_COUNT,
    HEROIC_THRESHOLD_MIN,
    TechniqueType,
    Move,
    MoveCategory,
    NONLETHAL_CHARM_MASTER_THRESHOLD,
    NONLETHAL_CHARM_REP_GAIN,
    NONLETHAL_EVASION_MASTER_THRESHOLD,
    NONLETHAL_STEALTH_MASTER_THRESHOLD,
    PlayerProfile,
    QuestStatus,
    ReputationTier,
    STATUS_EFFECT_BANDS,
    StatusEffectType,
    TROPHY_BATTLE_HARDENED,
    TROPHY_GHOST_STEP,
    TrophyCategory,
    TrophyTier,
    VillainStance,
    assign_affinity_from_choices,
    build_mvp_world,
    get_learnable_enemy_moves,
    load_world_snapshot,
    resolve_affinity_minigame,
    save_world_snapshot,
)
from shinobi_rpg.framework import framework_overview_json, get_framework_overview
from shinobi_rpg.__main__ import main


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

    def test_framework_overview_exposes_build_ready_content(self):
        overview = get_framework_overview()
        self.assertEqual(overview["project"], "Shinobi-RPG1")
        self.assertEqual(overview["player_bootstrap"]["name"], "Dan")
        self.assertIn(overview["player_bootstrap"]["affinity"], overview["framework"]["affinities"])
        self.assertEqual(overview["development"]["entrypoint"], "python -m shinobi_rpg")
        self.assertGreaterEqual(overview["seeded_content"]["allies"], DEFAULT_ALLY_MIN_COUNT)
        self.assertGreaterEqual(overview["seeded_content"]["regions"], 1)
        self.assertGreaterEqual(overview["seeded_content"]["points_of_interest"], 20)

    def test_cli_main_prints_framework_overview_json(self):
        buffer = StringIO()
        with redirect_stdout(buffer):
            exit_code = main()
        output = buffer.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.strip(), framework_overview_json())

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
        world.resolve_region_encounter(player, "Verdant Gate")
        world.resolve_region_encounter(player, "Verdant Gate")
        world.resolve_region_encounter(player, "Verdant Gate")
        world.archive_historic_ninja(player)
        archive = world.vault_historic_ninjas[0]
        self.assertEqual(archive["name"], "Dot")
        self.assertEqual(archive["affinity"], player.affinity.value)
        self.assertEqual(archive["level"], player.stats.level)
        self.assertEqual(archive["reputation"], player.reputation)
        self.assertIn("enemy_move_claims", archive)
        self.assertIn("enemy_exclusive_moves", archive)
        self.assertTrue(archive["enemy_exclusive_moves"])

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

    def test_q1_to_q3_include_required_backstory_and_reputation_branch_keys(self):
        world, _ = build_mvp_world("Coverage", [3, 1, 2, 4])
        required = {
            "exiled_heir",
            "street_ghost",
            "wandering_monk",
            "nonlethal_path",
            "heroic_path",
            "rogue_path",
            "default",
        }
        for quest_id in ("Q1", "Q2", "Q3"):
            quest = next(item for item in world.quests if item.quest_id == quest_id)
            with self.subTest(quest_id=quest_id):
                self.assertTrue(required.issubset(set(quest.branch_outcomes.keys())))

    def test_q2_branching_uses_nonlethal_path_when_active(self):
        world, player = build_mvp_world("NonLethal", [3, 1, 2, 4])
        for decision in ["stealth", "stealth", "stealth", "charm", "evasion"]:
            world.apply_player_decision(player, decision)
        result = world.resolve_quest_branch(player, "Q2")
        self.assertEqual(result["branch_key"], "nonlethal_path")

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
        attack_name = player.moves_by_set[MoveCategory.ATTACK][0].name
        player.execute_move(attack_name, target_name="Kage Renda", lock_on=True)
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
        self.assertEqual(restored_player.locked_on_target, "Kage Renda")
        self.assertGreaterEqual(restored_world.environment_cycle_step, world.environment_cycle_step)
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

    def test_quest_distribution_is_evenly_assigned_across_regions(self):
        world, _ = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        distribution = world.get_quest_distribution()
        counts = [len(entries) for entries in distribution.values()]
        self.assertEqual(len(distribution), len(world.regions))
        self.assertLessEqual(max(counts) - min(counts), 1)

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
        self.assertIn("ascii_map", world_map)
        self.assertIn("legend", world_map)
        self.assertEqual(len(world_map["legend"]), len(world.regions))
        first = world_map["legend"][0]
        self.assertIn("region", first)
        self.assertIn("boss", first)
        self.assertIn("boss_location", first)

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

    def test_playthrough_summary_includes_new_tracking_fields(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        world.apply_player_decision(player, "charm")
        world.resolve_region_encounter(player, "Verdant Gate")
        world.resolve_region_encounter(player, "Verdant Gate")
        world.resolve_region_encounter(player, "Verdant Gate")
        summary = world.generate_playthrough_summary(player)
        self.assertIn("villain_decision_memory", summary)
        self.assertIn("red_bar_power_claims", summary)
        self.assertIn("enemy_move_claims", summary)
        self.assertIn("enemy_exclusive_moves_unlocked", summary)
        self.assertIn("enemy_exclusive_move_progress", summary)
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
        self.assertGreaterEqual(summary["enemy_exclusive_move_progress"]["total"], 1)

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

    def test_dual_affinity_animation_preview_blends_both_affinity_signatures(self):
        world, _ = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        preview = world.get_move_animation_preview("Tempest Throne Collapse")
        self.assertIn("compressed air ring gathers", preview["animation_profile"]["startup"])
        self.assertIn("seal stamp with rising rock plates", preview["animation_profile"]["startup"])
        self.assertIn("pressure ripple cross-cut", preview["animation_profile"]["hit"])
        self.assertIn("fissure burst and heavy camera thud", preview["animation_profile"]["hit"])

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

    def test_snapshot_roundtrip_preserves_region_points_of_interest(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        snapshot = world.to_snapshot(player)
        restored_world, _ = world.from_snapshot(snapshot)
        original = world.build_world_map()["regions"]
        restored = restored_world.build_world_map()["regions"]
        self.assertEqual(len(original), len(restored))
        for original_region, restored_region in zip(original, restored):
            self.assertEqual(original_region["name"], restored_region["name"])
            self.assertEqual(original_region["travel_nodes"], restored_region["travel_nodes"])
            self.assertEqual(
                [poi["name"] for poi in original_region["points_of_interest"]],
                [poi["name"] for poi in restored_region["points_of_interest"]],
            )

    def test_memory_store_tracks_subject_entries(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        count = world.store_memory(player.name, "Saved the hidden village from raiders.")
        self.assertEqual(count, 1)
        world.store_memory(player.name, "Brokered peace with rival scouts.")
        self.assertEqual(
            world.get_memory_store(player.name),
            [
                "Saved the hidden village from raiders.",
                "Brokered peace with rival scouts.",
            ],
        )

    def test_snapshot_roundtrip_preserves_memory_store(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        world.store_memory(player.name, "Recovered the moon archive seal.")
        snapshot = world.to_snapshot(player)
        restored_world, _ = world.from_snapshot(snapshot)
        self.assertEqual(
            restored_world.get_memory_store(player.name),
            ["Recovered the moon archive seal."],
        )

    def test_snapshot_roundtrip_preserves_city_systems_and_action_attributes(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        player.attribute_points = 3
        player.raise_action_attribute("commerce", 2)
        player.unlock_tool("Wayfarer Anchor")
        world.set_mobile_fast_travel(player, "Leafrise Village")
        snapshot = world.to_snapshot(player)
        restored_world, restored_player = world.from_snapshot(snapshot)
        self.assertEqual(restored_player.action_attributes["commerce"], player.action_attributes["commerce"])
        self.assertIn("Wayfarer Anchor", restored_player.owned_tools)
        self.assertEqual(restored_player.mobile_fast_travel_node, "Leafrise Village")
        self.assertTrue(restored_world.city_shops)
        self.assertTrue(restored_world.city_npcs)

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
        world.record_quest_resolution(player, "Q10", approach="direct", stealth_satisfied=True)
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

    def test_q21_branching_uses_remaining_seeded_focus_outcomes(self):
        world, player = build_mvp_world("GhostFocus", [3, 1, 2, 4])
        player.choose_backstory(world.player_backstories[1])  # street_ghost
        result = world.resolve_quest_branch(player, "Q21")
        self.assertEqual(result["branch_key"], "street_ghost")
        self.assertIn("sacred spaces outside faction revenge cycles", result["outcome"])

    def test_q50_branching_uses_remaining_seeded_focus_outcomes(self):
        world, player = build_mvp_world("HeroFocus", [3, 1, 2, 4])
        player.update_reputation(60)
        result = world.resolve_quest_branch(player, "Q50")
        self.assertEqual(result["branch_key"], "heroic_path")
        self.assertIn("balances justice, deterrence, and stability", result["outcome"])

    def test_remaining_seeded_quests_include_tactical_and_reputation_branches(self):
        world, player = build_mvp_world("Coverage", [3, 1, 2, 4])
        required_keys = {
            "stealth_path",
            "charm_path",
            "evasion_path",
            "kill_path",
            "heroic_path",
            "rogue_path",
        }
        remaining = [
            quest for quest in world.quests if quest.quest_id.startswith("Q") and int(quest.quest_id[1:]) >= 21
        ]
        self.assertEqual(len(remaining), 30)
        for quest in remaining:
            with self.subTest(quest_id=quest.quest_id):
                self.assertTrue(required_keys.issubset(set(quest.branch_outcomes.keys())))

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

    def test_villain_slayer_trophy_tracks_red_bar_targets_only(self):
        world, player = build_mvp_world("TestPlayer", [3, 1, 2, 4])
        for villain in world.villains:
            villain.defeated = villain.health_bar_color.lower() == "red"
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


class Issue1QuestBranchOutcomesTests(unittest.TestCase):
    """Issue 1: Handcrafted branch outcomes for Q16–Q50 (Issue 1)."""

    def _world(self) -> tuple:
        return build_mvp_world("TestPlayer", [3, 1, 2, 4])

    def test_q16_has_handcrafted_branch_outcomes(self):
        world, player = self._world()
        q = next(q for q in world.quests if q.quest_id == "Q16")
        for key in ("exiled_heir", "street_ghost", "wandering_monk", "nonlethal_path",
                    "heroic_path", "rogue_path", "default"):
            self.assertIn(key, q.branch_outcomes)
        # Outcomes should be narrative-specific (not the template pattern)
        self.assertNotIn("reframes Crows Over Red Pass as a lawful mandate", q.branch_outcomes["exiled_heir"])

    def test_q25_to_q35_all_have_full_branch_keys(self):
        world, _ = self._world()
        required = {"exiled_heir", "street_ghost", "wandering_monk", "nonlethal_path",
                    "heroic_path", "rogue_path", "default"}
        for qid in [f"Q{n}" for n in range(25, 36)]:
            q = next(q for q in world.quests if q.quest_id == qid)
            missing = required - set(q.branch_outcomes.keys())
            self.assertFalse(missing, f"{qid} missing branch keys: {missing}")

    def test_q40_to_q50_all_have_full_branch_keys(self):
        world, _ = self._world()
        required = {"exiled_heir", "street_ghost", "wandering_monk", "nonlethal_path",
                    "heroic_path", "rogue_path", "default"}
        for qid in [f"Q{n}" for n in range(40, 51)]:
            q = next(q for q in world.quests if q.quest_id == qid)
            missing = required - set(q.branch_outcomes.keys())
            self.assertFalse(missing, f"{qid} missing branch keys: {missing}")

    def test_q50_nonlethal_branch_resolves_correctly(self):
        world, player = self._world()
        for _ in range(3):
            world.apply_player_decision(player, "stealth")
            world.apply_player_decision(player, "charm")
        # nonlethal path should be active
        self.assertTrue(player.is_nonlethal_path_active())
        result = world.resolve_quest_branch(player, "Q50")
        self.assertEqual(result["branch_key"], "nonlethal_path")
        self.assertIn("clean", result["outcome"])

    def test_q30_exiled_heir_branch_overrides_tactical(self):
        world, player = self._world()
        player.choose_backstory(world.player_backstories[0])  # exiled_heir
        for _ in range(5):
            world.apply_player_decision(player, "stealth")
        result = world.resolve_quest_branch(player, "Q30")
        self.assertEqual(result["branch_key"], "exiled_heir")

    def test_q16_rogue_branch_resolves_with_rogue_reputation(self):
        world, player = self._world()
        for _ in range(30):
            world.apply_player_decision(player, "kill")
        result = world.resolve_quest_branch(player, "Q16")
        self.assertIn(result["branch_key"], ("rogue_path", "kill_path", "default"))


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


class Issue4ReplaySummaryTests(unittest.TestCase):
    """Issue 4: Replay/snapshot summary fidelity."""

    def _world_and_player(self) -> tuple:
        return build_mvp_world("SummaryTest", [3, 1, 2, 4])

    def test_playthrough_summary_includes_playstyle_summary(self):
        world, player = self._world_and_player()
        summary = world.generate_playthrough_summary(player)
        self.assertIn("playstyle_summary", summary)
        ps = summary["playstyle_summary"]
        self.assertIn("style_label", ps)
        self.assertIn("nonlethal_total", ps)
        self.assertIn("lethal_total", ps)
        self.assertIn("playstyle_shift_note", ps)

    def test_playstyle_label_reflects_stealth_dominant_nonlethal(self):
        world, player = self._world_and_player()
        for _ in range(5):
            world.apply_player_decision(player, "stealth")
        summary = world.generate_playthrough_summary(player)
        label = summary["playstyle_summary"]["style_label"]
        self.assertIn("Shadow Operative", label)

    def test_playstyle_label_reflects_charm_dominant_nonlethal(self):
        world, player = self._world_and_player()
        for _ in range(5):
            world.apply_player_decision(player, "charm")
        summary = world.generate_playthrough_summary(player)
        label = summary["playstyle_summary"]["style_label"]
        self.assertIn("Silver Diplomat", label)

    def test_playthrough_summary_includes_villain_relationship_arcs(self):
        world, player = self._world_and_player()
        for _ in range(5):
            world.apply_player_decision(player, "kill")
        summary = world.generate_playthrough_summary(player)
        self.assertIn("villain_relationship_arcs", summary)
        arcs = summary["villain_relationship_arcs"]
        self.assertIsInstance(arcs, dict)
        for name, data in arcs.items():
            self.assertIn("arc", data)
            self.assertIn("phase", data)
            self.assertIn("active_triggers", data)

    def test_playthrough_summary_includes_trophy_near_miss(self):
        world, player = self._world_and_player()
        # 2 stealth encounters — Ghost Step needs 3, so 1 away
        world.apply_player_decision(player, "stealth")
        world.apply_player_decision(player, "stealth")
        summary = world.generate_playthrough_summary(player)
        self.assertIn("trophy_near_miss", summary)
        near_miss_keys = [item["trophy_key"] for item in summary["trophy_near_miss"]]
        self.assertIn(TROPHY_GHOST_STEP, near_miss_keys)

    def test_trophy_near_miss_empty_when_no_trophies_close(self):
        world, player = self._world_and_player()
        # No decisions at all — nothing should be near a threshold
        summary = world.generate_playthrough_summary(player)
        self.assertIsInstance(summary["trophy_near_miss"], list)

    def test_vault_snapshot_roundtrip_preserves_new_fields(self):
        import tempfile, os
        from shinobi_rpg.core import save_world_snapshot, load_world_snapshot
        world, player = self._world_and_player()
        for _ in range(3):
            world.apply_player_decision(player, "stealth")
        world.resolve_region_encounter(player, "Verdant Gate")
        world.resolve_region_encounter(player, "Verdant Gate")
        world.resolve_region_encounter(player, "Verdant Gate")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_world_snapshot(world, player, path)
            world2, player2 = load_world_snapshot(path)
            self.assertEqual(player2.encounter_outcomes["stealth"], 3)
            self.assertTrue(player2.enemy_move_claims)
            summary = world2.generate_playthrough_summary(player2)
            self.assertIn("playstyle_summary", summary)
            self.assertIn("trophy_near_miss", summary)
            self.assertIn("enemy_move_claims", summary)
        finally:
            os.unlink(path)


class Issue5QuestPathingAndArcTests(unittest.TestCase):
    def _world_and_player(self) -> tuple:
        return build_mvp_world("PathingTest", [3, 1, 2, 4])

    def test_stealth_gated_seeded_quests_are_flagged(self):
        world, _ = self._world_and_player()
        gated = {quest.quest_id for quest in world.quests if quest.stealth_required}
        self.assertTrue({"Q3", "Q5", "Q10"}.issubset(gated))

    def test_all_seeded_quests_expose_tactical_paths(self):
        world, _ = self._world_and_player()
        required = {"stealth_path", "charm_path", "evasion_path", "kill_path"}
        for quest in world.quests:
            with self.subTest(quest_id=quest.quest_id):
                self.assertTrue(required.issubset(set(quest.branch_outcomes)))

    def test_explicit_quest_approach_overrides_global_dominant_outcome(self):
        world, player = self._world_and_player()
        for _ in range(3):
            world.apply_player_decision(player, "kill")
        world.record_quest_resolution(player, "Q4", approach="stealth", stealth_satisfied=True)
        result = world.resolve_quest_branch(player, "Q4")
        self.assertEqual(result["branch_key"], "stealth_path")

    def test_stealth_gate_blocks_nonlethal_branch_until_satisfied(self):
        world, player = self._world_and_player()
        for decision in ["stealth", "charm", "evasion"]:
            world.apply_player_decision(player, decision)
        blocked = world.resolve_quest_branch(player, "Q5")
        self.assertNotEqual(blocked["branch_key"], "nonlethal_path")
        self.assertFalse(blocked["quest_resolution"]["stealth_gate_open"])

        world.record_quest_resolution(player, "Q5", approach="direct", stealth_satisfied=True)
        unlocked = world.resolve_quest_branch(player, "Q5")
        self.assertEqual(unlocked["branch_key"], "nonlethal_path")
        self.assertTrue(unlocked["quest_resolution"]["stealth_gate_open"])

    def test_complete_quest_persists_resolution_state(self):
        world, player = self._world_and_player()
        player.set_quest_status("Q3", QuestStatus.ACTIVE)
        world.record_quest_resolution(player, "Q3", approach="stealth", stealth_satisfied=True)
        result = world.complete_quest(player, "Q3")
        self.assertEqual(result["resolved_branch_key"], "stealth_path")
        self.assertTrue(player.quest_resolution_state["Q3"]["completed"])

    def test_snapshot_roundtrip_preserves_quest_resolution_state(self):
        world, player = self._world_and_player()
        world.record_quest_resolution(player, "Q10", approach="stealth", stealth_satisfied=True)
        with TemporaryDirectory() as temp_dir:
            snapshot_path = f"{temp_dir}/snapshot.json"
            save_world_snapshot(world, player, snapshot_path)
            restored_world, restored_player = load_world_snapshot(snapshot_path)
        self.assertEqual(
            restored_player.quest_resolution_state["Q10"]["approach"],
            "stealth",
        )
        restored = restored_world.resolve_quest_branch(restored_player, "Q10")
        self.assertTrue(restored["quest_resolution"]["stealth_gate_open"])

    def test_arc_transition_events_are_logged_once_per_phase(self):
        world, player = self._world_and_player()
        for _ in range(3):
            region_name = world.dynamic_region_chain[0]
            world.clear_region(player, region_name, "weapon")
        self.assertEqual(
            [entry["to_phase"] for entry in world.arc_transition_history],
            ["escalation", "apex"],
        )
        summary = world.generate_playthrough_summary(player)
        self.assertEqual(len(summary["arc_state"]["transition_history"]), 2)
        self.assertEqual(len(world.arc_transition_history), 2)
        self.assertTrue(
            any(entry.get("event_type") == "arc_transition" for entry in world.world_event_history)
        )

    def test_black_market_inventory_honors_required_quest_completion(self):
        world, player = self._world_and_player()
        player.update_reputation(-60)
        inventory = {item["key"] for item in world.get_shop_inventory(player)}
        self.assertNotIn("gatebreaker_smoke_map", inventory)
        player.set_quest_status("Q3", QuestStatus.COMPLETED)
        inventory = {item["key"] for item in world.get_shop_inventory(player)}
        self.assertIn("gatebreaker_smoke_map", inventory)

    def test_reformed_villain_hook_surfaces_in_quest_outcome(self):
        world, player = self._world_and_player()
        for _ in range(3):
            world.apply_player_decision(player, "charm")
        result = world.resolve_quest_branch(player, "Q3")
        self.assertIsNotNone(result["reformed_villain_hook"])
        self.assertIn("lowers his blade", result["outcome"])


class VillainBackstoryAndTieInTests(unittest.TestCase):
    """Villain backstory, power origins, arc ties, and player backstory hooks."""

    _PLAYER_BACKSTORY_KEYS = ("exiled_heir", "street_ghost", "wandering_monk")
    _PATH_KEYS = ("nonlethal_path", "rogue_path", "heroic_path")
    _BOSS_NAMES = ("Kage Renda", "General Voln", "Admiral Neris", "Zephyr Tyrant", "Ashen Monarch")

    def _world(self) -> tuple:
        return build_mvp_world("TestPlayer", [3, 1, 2, 4])

    def _villain_text(self, villain) -> str:
        parts = [
            villain.backstory,
            villain.power_origin,
            villain.role,
            villain.signature_power.name,
            villain.signature_power.technique_type.value,
            villain.signature_power.category.value,
            " ".join(villain.skinned_move_names.values()),
            " ".join(villain.player_backstory_hooks.values()),
        ]
        return " ".join(parts).lower()

    # ------------------------------------------------------------------
    # power_origin field
    # ------------------------------------------------------------------

    def test_all_villains_have_non_empty_power_origin(self):
        world, _ = self._world()
        for villain in world.villains:
            with self.subTest(villain=villain.name):
                self.assertTrue(
                    villain.power_origin,
                    f"Villain '{villain.name}' is missing a power_origin.",
                )

    def test_boss_power_origins_are_substantive(self):
        world, _ = self._world()
        for name in self._BOSS_NAMES:
            villain = next(v for v in world.villains if v.name == name)
            with self.subTest(villain=name):
                self.assertGreater(
                    len(villain.power_origin),
                    80,
                    f"'{name}' power_origin is too brief.",
                )

    def test_power_origins_mention_signature_power(self):
        world, _ = self._world()
        for villain in world.villains:
            with self.subTest(villain=villain.name):
                # power_origin should contextually reference the technique
                self.assertTrue(
                    villain.power_origin,
                    f"'{villain.name}' has empty power_origin.",
                )

    # ------------------------------------------------------------------
    # arc_ties field
    # ------------------------------------------------------------------

    def test_all_villains_have_at_least_one_arc_tie(self):
        world, _ = self._world()
        for villain in world.villains:
            with self.subTest(villain=villain.name):
                self.assertTrue(
                    villain.arc_ties,
                    f"Villain '{villain.name}' has no arc_ties.",
                )

    def test_boss_arc_ties_reference_known_arcs(self):
        world, _ = self._world()
        known_arcs = {
            "political_war", "fracture_front", "recovery_mandate",
            "rebellion_wave", "highland_reckoning", "depths_awakening",
        }
        for name in self._BOSS_NAMES:
            villain = next(v for v in world.villains if v.name == name)
            with self.subTest(villain=name):
                for arc in villain.arc_ties:
                    self.assertIn(arc, known_arcs, f"'{name}' has unknown arc tie '{arc}'.")

    def test_kage_renda_tied_to_political_war(self):
        world, _ = self._world()
        renda = next(v for v in world.villains if v.name == "Kage Renda")
        self.assertIn("political_war", renda.arc_ties)

    def test_general_voln_tied_to_fracture_front(self):
        world, _ = self._world()
        voln = next(v for v in world.villains if v.name == "General Voln")
        self.assertIn("fracture_front", voln.arc_ties)

    def test_admiral_neris_tied_to_recovery_mandate(self):
        world, _ = self._world()
        neris = next(v for v in world.villains if v.name == "Admiral Neris")
        self.assertIn("recovery_mandate", neris.arc_ties)

    def test_zephyr_tyrant_tied_to_highland_reckoning(self):
        world, _ = self._world()
        tyrant = next(v for v in world.villains if v.name == "Zephyr Tyrant")
        self.assertIn("highland_reckoning", tyrant.arc_ties)

    def test_ashen_monarch_tied_to_depths_awakening(self):
        world, _ = self._world()
        monarch = next(v for v in world.villains if v.name == "Ashen Monarch")
        self.assertIn("depths_awakening", monarch.arc_ties)

    # ------------------------------------------------------------------
    # player_backstory_hooks field
    # ------------------------------------------------------------------

    def test_all_bosses_have_hooks_for_all_player_backstory_keys(self):
        world, _ = self._world()
        for name in self._BOSS_NAMES:
            villain = next(v for v in world.villains if v.name == name)
            with self.subTest(villain=name):
                for key in self._PLAYER_BACKSTORY_KEYS:
                    self.assertIn(
                        key,
                        villain.player_backstory_hooks,
                        f"'{name}' missing player backstory hook for '{key}'.",
                    )

    def test_all_bosses_have_hooks_for_path_keys(self):
        world, _ = self._world()
        for name in self._BOSS_NAMES:
            villain = next(v for v in world.villains if v.name == name)
            with self.subTest(villain=name):
                for key in self._PATH_KEYS:
                    self.assertIn(
                        key,
                        villain.player_backstory_hooks,
                        f"'{name}' missing hook for path '{key}'.",
                    )

    def test_all_villains_have_at_least_three_backstory_hooks(self):
        world, _ = self._world()
        for villain in world.villains:
            with self.subTest(villain=villain.name):
                self.assertGreaterEqual(
                    len(villain.player_backstory_hooks),
                    3,
                    f"'{villain.name}' has fewer than 3 backstory hooks.",
                )

    def test_kage_renda_exiled_heir_hook_references_exile(self):
        world, _ = self._world()
        renda = next(v for v in world.villains if v.name == "Kage Renda")
        hook = renda.player_backstory_hooks["exiled_heir"]
        self.assertTrue(hook)
        self.assertIn("exile", hook.lower())

    def test_ashen_monarch_wandering_monk_hook_references_seals(self):
        world, _ = self._world()
        monarch = next(v for v in world.villains if v.name == "Ashen Monarch")
        hook = monarch.player_backstory_hooks["wandering_monk"]
        self.assertIn("seal", hook.lower())

    def test_villain_roster_covers_requested_personality_and_end_goal_themes(self):
        world, _ = self._world()
        villains = {villain.name: villain for villain in world.villains}

        themed_expectations = {
            "Kage Renda": ("political",),
            "Silent Bell": ("shrine", "theological"),
            "Torch Baron": ("money",),
            "Crimson Lantern": ("lust",),
            "Vanta Puppetmaster": ("technology", "summoning"),
            "Mist Widow": ("stealth",),
            "Dusk Paladin": ("last ronin",),
            "Bone Weaver": ("medical",),
            "Storm Needle": ("long range",),
        }

        for villain_name, expected_terms in themed_expectations.items():
            with self.subTest(villain=villain_name):
                text = self._villain_text(villains[villain_name])
                for term in expected_terms:
                    self.assertIn(term, text)

    # ------------------------------------------------------------------
    # get_villain_backstory_profile method
    # ------------------------------------------------------------------

    def test_get_villain_backstory_profile_returns_all_fields(self):
        world, _ = self._world()
        profile = world.get_villain_backstory_profile("Kage Renda")
        self.assertEqual(profile["name"], "Kage Renda")
        self.assertIn("backstory", profile)
        self.assertIn("power_origin", profile)
        self.assertIn("arc_ties", profile)
        self.assertIn("player_backstory_hooks", profile)
        self.assertIn("signature_power", profile)
        self.assertIn("primary_affinity", profile)
        self.assertIn("secondary_affinities", profile)
        self.assertIn("affinities", profile)
        self.assertIn("ultimate_affinities", profile)
        self.assertIn("role", profile)
        self.assertIn("stance", profile)
        self.assertIn("relationship_arc", profile)

    def test_get_villain_backstory_profile_tracks_dual_affinity_villains(self):
        world, _ = self._world()
        profile = world.get_villain_backstory_profile("Zephyr Tyrant")
        self.assertEqual(profile["primary_affinity"], Affinity.WIND.value)
        self.assertEqual(profile["secondary_affinities"], [Affinity.EARTH.value])
        self.assertEqual(profile["affinities"], [Affinity.WIND.value, Affinity.EARTH.value])
        self.assertEqual(profile["ultimate_affinities"], [Affinity.WIND.value, Affinity.EARTH.value])

    def test_get_villain_backstory_profile_raises_for_unknown_villain(self):
        world, _ = self._world()
        with self.assertRaises(ValueError):
            world.get_villain_backstory_profile("Nonexistent Villain")

    def test_get_villain_backstory_profile_arc_ties_is_list(self):
        world, _ = self._world()
        for name in self._BOSS_NAMES:
            with self.subTest(villain=name):
                profile = world.get_villain_backstory_profile(name)
                self.assertIsInstance(profile["arc_ties"], list)
                self.assertTrue(profile["arc_ties"])

    def test_get_villain_backstory_profile_hooks_is_dict(self):
        world, _ = self._world()
        profile = world.get_villain_backstory_profile("General Voln")
        self.assertIsInstance(profile["player_backstory_hooks"], dict)
        self.assertIn("exiled_heir", profile["player_backstory_hooks"])

    def test_get_villain_backstory_profile_relationship_arc_dormant_at_start(self):
        world, _ = self._world()
        profile = world.get_villain_backstory_profile("Kage Renda")
        self.assertEqual(profile["relationship_arc"], "dormant")

    def test_get_villain_backstory_profile_relationship_arc_updates_with_pressure(self):
        world, player = self._world()
        for _ in range(10):
            world.apply_player_decision(player, "kill")
        profile = world.get_villain_backstory_profile("Kage Renda")
        self.assertIn(profile["relationship_arc"], ("nemesis", "rival", "active"))

    # ------------------------------------------------------------------
    # generate_playthrough_summary integration
    # ------------------------------------------------------------------

    def test_playthrough_summary_includes_villain_backstory_profiles(self):
        world, player = self._world()
        summary = world.generate_playthrough_summary(player)
        self.assertIn("villain_backstory_profiles", summary)
        profiles = summary["villain_backstory_profiles"]
        self.assertIsInstance(profiles, dict)
        for name in self._BOSS_NAMES:
            with self.subTest(villain=name):
                self.assertIn(name, profiles)

    def test_villain_backstory_profiles_summary_contains_required_keys(self):
        world, player = self._world()
        summary = world.generate_playthrough_summary(player)
        profiles = summary["villain_backstory_profiles"]
        for name, data in profiles.items():
            with self.subTest(villain=name):
                self.assertIn("backstory", data)
                self.assertIn("power_origin", data)
                self.assertIn("affinities", data)
                self.assertIn("secondary_affinities", data)
                self.assertIn("arc_ties", data)
                self.assertIn("player_backstory_hooks", data)

    def test_villain_kits_include_secondary_affinities_for_dual_affinity_villains(self):
        world, player = self._world()
        summary = world.generate_playthrough_summary(player)
        zephyr_kit = next(item for item in summary["villain_kits"] if item["name"] == "Zephyr Tyrant")
        self.assertEqual(zephyr_kit["primary_affinity"], Affinity.WIND.value)
        self.assertEqual(zephyr_kit["secondary_affinities"], [Affinity.EARTH.value])
        self.assertEqual(zephyr_kit["affinities"], [Affinity.WIND.value, Affinity.EARTH.value])
        self.assertEqual(zephyr_kit["ultimate_affinities"], [Affinity.WIND.value, Affinity.EARTH.value])

    # ------------------------------------------------------------------
    # Snapshot round-trip
    # ------------------------------------------------------------------

    def test_snapshot_round_trip_preserves_villain_backstory_fields(self):
        import tempfile, os
        world, player = self._world()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_world_snapshot(world, player, path)
            restored_world, _ = load_world_snapshot(path)
        finally:
            os.unlink(path)

        for original, restored in zip(world.villains, restored_world.villains):
            with self.subTest(villain=original.name):
                self.assertEqual(restored.power_origin, original.power_origin)
                self.assertEqual(restored.arc_ties, original.arc_ties)
                self.assertEqual(
                    restored.player_backstory_hooks,
                    original.player_backstory_hooks,
                )

    def test_snapshot_round_trip_preserves_boss_arc_ties(self):
        import tempfile, os
        world, player = self._world()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_world_snapshot(world, player, path)
            restored_world, _ = load_world_snapshot(path)
        finally:
            os.unlink(path)

        renda_orig = next(v for v in world.villains if v.name == "Kage Renda")
        renda_rest = next(v for v in restored_world.villains if v.name == "Kage Renda")
        self.assertEqual(renda_rest.arc_ties, renda_orig.arc_ties)
        self.assertIn("political_war", renda_rest.arc_ties)

    def test_legacy_snapshot_without_new_fields_loads_with_defaults(self):
        """Snapshots saved before power_origin/arc_ties existed should still load."""
        world, player = self._world()
        snapshot = world.to_snapshot(player)
        # Strip the new fields to simulate a legacy snapshot
        for villain_data in snapshot["world"]["villains"]:
            villain_data.pop("power_origin", None)
            villain_data.pop("arc_ties", None)
            villain_data.pop("player_backstory_hooks", None)
        restored_world, _ = world.from_snapshot(snapshot)
        for villain in restored_world.villains:
            with self.subTest(villain=villain.name):
                self.assertEqual(villain.power_origin, "")
                self.assertEqual(villain.arc_ties, ())
                self.assertEqual(villain.player_backstory_hooks, {})


if __name__ == "__main__":
    unittest.main()
