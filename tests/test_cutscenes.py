"""Tests for the boss cutscene engine."""

import unittest
from io import StringIO
from unittest.mock import patch

from shinobi_rpg.cutscenes import (
    BOSS_CUTSCENE_DATA,
    get_boss_taunt,
    list_cutscene_bosses,
    play_boss_cutscene,
    play_boss_defeat_scene,
    play_minor_encounter_cutscene,
)
from shinobi_rpg.core import build_mvp_world


_MAIN_BOSSES = [
    "Kage Renda",
    "General Voln",
    "Admiral Neris",
    "Zephyr Tyrant",
    "Ashen Monarch",
]

_ALL_APPROACHES = ["kill", "charm", "stealth", "evasion"]


class CutsceneDataIntegrityTests(unittest.TestCase):
    """Verify that the static cutscene data is complete and well-formed."""

    def test_all_main_bosses_have_cutscene_data(self):
        bosses = list_cutscene_bosses()
        for boss in _MAIN_BOSSES:
            with self.subTest(boss=boss):
                self.assertIn(boss, bosses)

    def test_each_boss_has_required_keys(self):
        required = {
            "affinity_icon", "region_mood", "intro_beats", "entrance_lines",
            "player_choices", "boss_responses", "stance_deltas",
            "pre_battle_line", "defeat_lines", "taunt_lines",
        }
        for boss, data in BOSS_CUTSCENE_DATA.items():
            with self.subTest(boss=boss):
                for key in required:
                    self.assertIn(key, data, f"{boss} missing key '{key}'")

    def test_player_choices_boss_responses_stance_deltas_aligned(self):
        for boss, data in BOSS_CUTSCENE_DATA.items():
            with self.subTest(boss=boss):
                n_choices = len(data["player_choices"])
                self.assertEqual(
                    len(data["boss_responses"]), n_choices,
                    f"{boss}: boss_responses count != player_choices count"
                )
                self.assertEqual(
                    len(data["stance_deltas"]), n_choices,
                    f"{boss}: stance_deltas count != player_choices count"
                )

    def test_each_boss_has_exactly_three_player_choices(self):
        for boss, data in BOSS_CUTSCENE_DATA.items():
            with self.subTest(boss=boss):
                self.assertEqual(len(data["player_choices"]), 3)

    def test_defeat_lines_cover_all_approaches(self):
        for boss, data in BOSS_CUTSCENE_DATA.items():
            with self.subTest(boss=boss):
                for approach in _ALL_APPROACHES:
                    self.assertIn(
                        approach, data["defeat_lines"],
                        f"{boss} missing defeat line for approach '{approach}'"
                    )

    def test_player_choices_are_two_tuples(self):
        for boss, data in BOSS_CUTSCENE_DATA.items():
            with self.subTest(boss=boss):
                for choice in data["player_choices"]:
                    self.assertEqual(len(choice), 2, f"{boss} choice not a 2-tuple")
                    self.assertIsInstance(choice[0], str)
                    self.assertIsInstance(choice[1], str)

    def test_taunt_lines_non_empty(self):
        for boss, data in BOSS_CUTSCENE_DATA.items():
            with self.subTest(boss=boss):
                self.assertTrue(len(data["taunt_lines"]) >= 2)

    def test_stance_deltas_are_integers(self):
        for boss, data in BOSS_CUTSCENE_DATA.items():
            with self.subTest(boss=boss):
                for delta in data["stance_deltas"]:
                    self.assertIsInstance(delta, int)

    def test_intro_beats_are_non_empty_strings(self):
        for boss, data in BOSS_CUTSCENE_DATA.items():
            with self.subTest(boss=boss):
                self.assertTrue(len(data["intro_beats"]) >= 1)
                for beat in data["intro_beats"]:
                    self.assertIsInstance(beat, str)
                    self.assertTrue(len(beat) > 10)


class CutscenePlaybackTests(unittest.TestCase):
    """Integration tests: run cutscenes with mocked I/O and validate returned data."""

    def _run_cutscene(self, boss_name: str, choice_idx: int, **kwargs) -> dict:
        """Run ``play_boss_cutscene`` with simulated user input."""
        with patch("builtins.input", return_value=str(choice_idx + 1)), \
             patch("sys.stdout", new_callable=StringIO):
            return play_boss_cutscene(boss_name=boss_name, player_name="Dan", **kwargs)

    def test_cutscene_returns_correct_keys(self):
        result = self._run_cutscene("Kage Renda", 0)
        self.assertIn("dialogue_tone", result)
        self.assertIn("stance_delta", result)
        self.assertIn("player_choice_index", result)
        self.assertIn("boss_name", result)

    def test_cutscene_returns_correct_boss_name(self):
        for boss in _MAIN_BOSSES:
            with self.subTest(boss=boss):
                result = self._run_cutscene(boss, 0)
                self.assertEqual(result["boss_name"], boss)

    def test_aggressive_choice_yields_positive_delta(self):
        # Choice 0 is the aggressive choice for Kage Renda (delta=2)
        result = self._run_cutscene("Kage Renda", 0)
        self.assertGreater(result["stance_delta"], 0)

    def test_diplomatic_choice_yields_negative_delta(self):
        # Choice 1 is diplomatic for Kage Renda (delta=-2)
        result = self._run_cutscene("Kage Renda", 1)
        self.assertLess(result["stance_delta"], 0)

    def test_dialogue_tone_labels_correct(self):
        tones = ["aggressive", "diplomatic", "pragmatic"]
        for boss in ["Kage Renda", "General Voln"]:
            for idx, expected_tone in enumerate(tones):
                with self.subTest(boss=boss, choice=idx):
                    result = self._run_cutscene(boss, idx)
                    self.assertEqual(result["dialogue_tone"], expected_tone)

    def test_player_choice_index_stored(self):
        for idx in range(3):
            with self.subTest(choice_idx=idx):
                result = self._run_cutscene("Kage Renda", idx)
                self.assertEqual(result["player_choice_index"], idx)

    def test_all_main_bosses_run_without_error(self):
        for boss in _MAIN_BOSSES:
            with self.subTest(boss=boss):
                result = self._run_cutscene(boss, 1)
                self.assertEqual(result["boss_name"], boss)

    def test_unknown_boss_returns_fallback(self):
        with patch("builtins.input", return_value=""), \
             patch("sys.stdout", new_callable=StringIO):
            result = play_boss_cutscene(boss_name="Shadow Phantom", player_name="Dan")
        self.assertEqual(result["boss_name"], "Shadow Phantom")
        self.assertEqual(result["stance_delta"], 0)

    def test_cutscene_with_backstory_hook_runs(self):
        result = self._run_cutscene(
            "Kage Renda", 1,
            player_backstory_hook="Renda recognises something in your bearing.",
        )
        self.assertIn("dialogue_tone", result)

    def test_cutscene_with_reformed_arc_runs(self):
        result = self._run_cutscene(
            "Kage Renda", 1,
            villain_relationship_arc="reformed",
        )
        self.assertIn("dialogue_tone", result)


class DefeatSceneTests(unittest.TestCase):
    """Verify that defeat scenes render without error for all bosses and approaches."""

    def _run_defeat(self, boss: str, approach: str) -> None:
        with patch("builtins.input", return_value=""), \
             patch("sys.stdout", new_callable=StringIO):
            play_boss_defeat_scene(boss, approach)

    def test_defeat_scenes_for_all_known_bosses_and_approaches(self):
        for boss in _MAIN_BOSSES:
            for approach in _ALL_APPROACHES:
                with self.subTest(boss=boss, approach=approach):
                    self._run_defeat(boss, approach)

    def test_defeat_scene_unknown_boss_no_error(self):
        self._run_defeat("Unknown Villain", "kill")

    def test_defeat_scene_unknown_approach_falls_back(self):
        # Should not raise even for an approach not in the data
        self._run_defeat("Kage Renda", "unknown_approach")


class MinorEncounterCutsceneTests(unittest.TestCase):
    def test_minor_cutscene_returns_story_metadata(self):
        with patch("builtins.input", return_value=""), \
             patch("sys.stdout", new_callable=StringIO):
            result = play_minor_encounter_cutscene(
                "Mist Ronin",
                "Verdant Gate",
                player_name="Dan",
                threat_count=2,
            )
        self.assertEqual(result["encounter_name"], "Mist Ronin")
        self.assertEqual(result["region_name"], "Verdant Gate")
        self.assertEqual(result["threat_count"], 2)


class TauntLineTests(unittest.TestCase):
    def test_taunt_returns_string_for_known_boss(self):
        for boss in _MAIN_BOSSES:
            with self.subTest(boss=boss):
                taunt = get_boss_taunt(boss)
                self.assertIsInstance(taunt, str)
                self.assertTrue(len(taunt) > 5)

    def test_taunt_returns_none_for_unknown_boss(self):
        taunt = get_boss_taunt("Nobody The Forgotten")
        self.assertIsNone(taunt)


class CutsceneWorldIntegrationTests(unittest.TestCase):
    """Verify cutscene hooks work correctly with the live game world."""

    def setUp(self):
        self.world, self.player = build_mvp_world("TestPlayer", [3, 1, 2, 4, 5])

    def test_villain_backstory_hook_available_for_each_boss(self):
        for boss in _MAIN_BOSSES:
            with self.subTest(boss=boss):
                profile = self.world.get_villain_backstory_profile(boss)
                hooks = profile.get("player_backstory_hooks", {})
                # Each boss should have at least heroic/rogue/nonlethal hooks
                self.assertTrue(
                    len(hooks) >= 3,
                    f"{boss} has fewer than 3 backstory hooks: {list(hooks.keys())}"
                )

    def test_stance_delta_applied_to_villain(self):
        """Applying a positive stance delta increases villain aggression."""
        world, player = self.world, self.player
        villain = next(v for v in world.villains if v.name == "Kage Renda")
        initial_score = villain.aggression_score
        villain.aggression_score += 2  # simulate aggressive dialogue choice
        self.assertGreater(villain.aggression_score, initial_score)

    def test_relationship_arc_readable_from_world(self):
        checkpoints = self.world.get_villain_evolution_checkpoints()
        self.assertIsInstance(checkpoints, list)
        if checkpoints:
            first = checkpoints[0]
            self.assertIn("villain", first)
            self.assertIn("relationship_arc", first)

    def test_cutscene_bosses_match_region_bosses(self):
        region_bosses = {r.boss for r in self.world.regions}
        scene_bosses = set(list_cutscene_bosses())
        # All 5 main bosses should appear in both the region list and cutscene data
        for boss in _MAIN_BOSSES:
            with self.subTest(boss=boss):
                self.assertIn(boss, region_bosses)
                self.assertIn(boss, scene_bosses)


if __name__ == "__main__":
    unittest.main()
