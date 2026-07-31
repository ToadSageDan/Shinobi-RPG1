import unittest
from shinobi_rpg.core import (
    Affinity,
    PlayerProfile,
    QuestStatus,
    build_mvp_world,
    load_world_snapshot,
    save_world_snapshot,
)
from tempfile import TemporaryDirectory


class QuestArcCoreTests(unittest.TestCase):
        def _get_unlocked_move_names(self, player: PlayerProfile) -> set[str]:
            return {move.name for moves in player.moves_by_set.values() for move in moves}

        def _get_region(self, world, region_name: str):
            region = next((item for item in world.regions if item.name == region_name), None)
            self.assertIsNotNone(region, f"Expected region '{region_name}' to exist in seeded world.")
            return region

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

        def test_quest_distribution_is_evenly_assigned_across_regions(self):
            world, _ = build_mvp_world("TestPlayer", [3, 1, 2, 4])
            distribution = world.get_quest_distribution()
            counts = [len(entries) for entries in distribution.values()]
            self.assertEqual(len(distribution), len(world.regions))
            self.assertLessEqual(max(counts) - min(counts), 1)

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
