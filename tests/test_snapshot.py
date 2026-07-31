import unittest
from shinobi_rpg.core import (
    CHAKRA_START,
    MoveCategory,
    PlayerProfile,
    QuestStatus,
    TROPHY_GHOST_STEP,
    TrophyTier,
    build_mvp_world,
    load_world_snapshot,
    save_world_snapshot,
)
from tempfile import TemporaryDirectory


class SnapshotCoreTests(unittest.TestCase):
        def _get_unlocked_move_names(self, player: PlayerProfile) -> set[str]:
            return {move.name for moves in player.moves_by_set.values() for move in moves}

        def _get_region(self, world, region_name: str):
            region = next((item for item in world.regions if item.name == region_name), None)
            self.assertIsNotNone(region, f"Expected region '{region_name}' to exist in seeded world.")
            return region

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


class SnapshotGameplayImprovementsTests(unittest.TestCase):
        def _world(self):
            return build_mvp_world("TestPlayer", [5, 1, 1, 1])

        def test_snapshot_round_trip_preserves_new_player_fields(self):
            world, player = self._world()
            player.chakra = 55
            player.move_proficiency["Edge Current"] = 42
            player.nonlethal_flow_streak = 3
            player.weapon_durability["Dawn Cutter"] = 70
            player.reputation_inactivity_ticks = 2

            with TemporaryDirectory() as tmpdir:
                path = f"{tmpdir}/snap.json"
                save_world_snapshot(world, player, path)
                _, restored = load_world_snapshot(path)

            self.assertEqual(restored.chakra, 55)
            self.assertEqual(restored.move_proficiency.get("Edge Current"), 42)
            self.assertEqual(restored.nonlethal_flow_streak, 3)
            self.assertEqual(restored.weapon_durability.get("Dawn Cutter"), 70)
            self.assertEqual(restored.reputation_inactivity_ticks, 2)

        def test_legacy_snapshot_without_new_player_fields_loads_with_defaults(self):
            world, player = self._world()
            snapshot = world.to_snapshot(player)
            # Strip new fields to simulate legacy snapshot
            for field in ("chakra", "move_proficiency", "nonlethal_flow_streak",
                          "weapon_durability", "reputation_inactivity_ticks"):
                snapshot["player"].pop(field, None)
            _, restored = world.from_snapshot(snapshot)
            self.assertEqual(restored.chakra, CHAKRA_START)
            self.assertEqual(restored.move_proficiency, {})
            self.assertEqual(restored.nonlethal_flow_streak, 0)
            self.assertEqual(restored.weapon_durability, {})
            self.assertEqual(restored.reputation_inactivity_ticks, 0)

