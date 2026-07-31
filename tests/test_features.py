import unittest
from shinobi_rpg.core import (
    Affinity,
    CHAKRA_MAX,
    CHAKRA_REGEN_ESCAPE,
    CHAKRA_COST,
    RivalProfile,
    WEAPON_DURABILITY_SCALE_FLOOR,
    WEAPON_DURABILITY_START,
    build_mvp_world,
)


class ExecuteMoveIntegrationTests(unittest.TestCase):
    """Tests for the three features newly wired into execute_move:
    chakra consumption (Feature 3), move proficiency (Feature 8),
    and weapon durability (Feature 12).
    """

    def setUp(self) -> None:
        self.world, self.player = build_mvp_world("IntegrationTest", [5, 1, 1, 1])

    # ------------------------------------------------------------------
    # Chakra integration (Feature 3)
    # ------------------------------------------------------------------

    def test_execute_move_returns_chakra_remaining(self) -> None:
        result = self.player.execute_move("Edge Current")
        self.assertIn("chakra_remaining", result)
        self.assertIn("insufficient_chakra", result)
        self.assertIsInstance(result["chakra_remaining"], int)

    def test_execute_attack_consumes_chakra(self) -> None:
        before = self.player.chakra
        result = self.player.execute_move("Edge Current")
        expected_cost = CHAKRA_COST["attack"]
        self.assertEqual(result["chakra_remaining"], before - expected_cost)
        self.assertFalse(result["insufficient_chakra"])

    def test_execute_escape_move_restores_chakra(self) -> None:
        # Drain some chakra first, then use an escape move.
        self.player.chakra = 40
        result = self.player.execute_move("Smoke Step")
        self.assertEqual(result["chakra_remaining"], min(CHAKRA_MAX, 40 + CHAKRA_REGEN_ESCAPE))
        self.assertFalse(result["insufficient_chakra"])

    def test_execute_move_flags_insufficient_chakra(self) -> None:
        # Use up almost all chakra, then force an expensive ultimate.
        self.player.chakra = 5  # Less than CHAKRA_COST["ultimate"] (30)
        result = self.player.execute_move("Twin Dragon Convergence")
        self.assertTrue(result["insufficient_chakra"])
        # Chakra should not go negative.
        self.assertGreaterEqual(result["chakra_remaining"], 0)

    def test_execute_defense_move_consumes_correct_chakra(self) -> None:
        before = self.player.chakra
        result = self.player.execute_move("Guarding Veil")
        self.assertEqual(result["chakra_remaining"], before - CHAKRA_COST["defense"])

    def test_insufficient_chakra_does_not_prevent_execution(self) -> None:
        """The move still executes even with insufficient chakra (signal only)."""
        self.player.chakra = 0
        result = self.player.execute_move("Edge Current")
        self.assertIn("damage", result)
        self.assertTrue(result["insufficient_chakra"])

    # ------------------------------------------------------------------
    # Move proficiency integration (Feature 8)
    # ------------------------------------------------------------------

    def test_execute_move_returns_proficiency_fields(self) -> None:
        result = self.player.execute_move("Edge Current")
        self.assertIn("proficiency", result)
        self.assertIn("proficiency_modifier", result)

    def test_execute_move_restores_proficiency_on_use(self) -> None:
        move_name = "Edge Current"
        # Artificially drain proficiency below the default.
        self.player.move_proficiency[move_name] = 10
        result = self.player.execute_move(move_name)
        # After use, proficiency should be restored toward default.
        self.assertGreater(result["proficiency"], 10)
        self.assertEqual(self.player.move_proficiency[move_name], result["proficiency"])

    def test_execute_move_proficiency_modifier_is_one_at_default(self) -> None:
        # Starting proficiency (MOVE_PROFICIENCY_DEFAULT=80) is above the
        # low threshold (40), so the scale modifier must be exactly 1.0.
        result = self.player.execute_move("Edge Current")
        self.assertEqual(result["proficiency_modifier"], 1.0)
        # Damage is unchanged compared to the unmodified formula.
        self.assertEqual(result["damage"], int(self.player.stats.power * 1.0))

    def test_execute_move_reduced_proficiency_lowers_damage(self) -> None:
        move_name = "Edge Current"
        move = self.player.get_move(move_name)
        # Pin proficiency well below the low threshold to force a sub-1 modifier.
        self.player.move_proficiency[move_name] = 0
        result = self.player.execute_move(move_name)
        # use_move_proficiency restores by DECAY_ON_SKIP from 0, so proficiency
        # becomes DECAY_ON_SKIP (5), still below LOW_THRESHOLD (40).
        self.assertLess(result["proficiency_modifier"], 1.0)
        # Damage must equal the formula with the reported modifier.
        expected_damage = int(self.player.stats.power * move.power_scale * result["proficiency_modifier"])
        self.assertEqual(result["damage"], expected_damage)

    def test_execute_ultimate_proficiency_modifier_applied(self) -> None:
        move_name = "Twin Dragon Convergence"
        move = self.player.get_move(move_name)
        self.player.move_proficiency[move_name] = 0
        result = self.player.execute_move(move_name)
        self.assertLess(result["proficiency_modifier"], 1.0)
        expected_damage = int(
            (self.player.stats.power + self.player.stats.focus)
            * move.power_scale
            * result["proficiency_modifier"]
        )
        self.assertEqual(result["damage"], expected_damage)

    # ------------------------------------------------------------------
    # Weapon durability integration (Feature 12)
    # ------------------------------------------------------------------

    def test_execute_move_returns_durability_ratio_one_without_weapon(self) -> None:
        result = self.player.execute_move("Edge Current")
        self.assertEqual(result["durability_ratio"], 1.0)

    def test_execute_move_with_weapon_name_degrades_durability(self) -> None:
        weapon_name = "Renda Fang Blade"
        self.world.clear_region(self.player, "Verdant Gate", "weapon")
        self.assertIn(weapon_name, self.player.reward_inventory["weapon"])

        before = self.player.weapon_durability.get(weapon_name, WEAPON_DURABILITY_START)
        self.player.execute_move("Edge Current", weapon_name=weapon_name)
        after = self.player.weapon_durability[weapon_name]
        self.assertLess(after, before)

    def test_execute_move_durability_ratio_is_one_above_threshold(self) -> None:
        weapon_name = "Renda Fang Blade"
        self.world.clear_region(self.player, "Verdant Gate", "weapon")
        # Full durability is above the low threshold, so ratio must be 1.0.
        result = self.player.execute_move("Edge Current", weapon_name=weapon_name)
        self.assertEqual(result["durability_ratio"], 1.0)

    def test_execute_move_low_durability_reduces_damage(self) -> None:
        weapon_name = "Renda Fang Blade"
        self.world.clear_region(self.player, "Verdant Gate", "weapon")
        move = self.player.get_move("Edge Current")

        # Pin durability to zero to get the scale floor.
        self.player.weapon_durability[weapon_name] = 0
        result = self.player.execute_move("Edge Current", weapon_name=weapon_name)
        proficiency_modifier = result["proficiency_modifier"]
        expected_damage = int(
            self.player.stats.power
            * move.power_scale
            * proficiency_modifier
            * WEAPON_DURABILITY_SCALE_FLOOR
        )
        self.assertLess(result["durability_ratio"], 1.0)
        self.assertEqual(result["damage"], expected_damage)

    def test_execute_move_weapon_not_in_inventory_ignores_durability(self) -> None:
        # Passing a weapon name the player doesn't own should not degrade anything.
        result = self.player.execute_move("Edge Current", weapon_name="Nonexistent Blade")
        self.assertEqual(result["durability_ratio"], 1.0)
        self.assertNotIn("Nonexistent Blade", self.player.weapon_durability)

    # ------------------------------------------------------------------
    # All three systems interact correctly
    # ------------------------------------------------------------------

    def test_execute_move_combines_proficiency_and_durability_modifiers(self) -> None:
        weapon_name = "Renda Fang Blade"
        self.world.clear_region(self.player, "Verdant Gate", "weapon")
        move_name = "Edge Current"
        move = self.player.get_move(move_name)

        # Force both modifiers below 1.0.
        self.player.move_proficiency[move_name] = 0
        self.player.weapon_durability[weapon_name] = 0

        result = self.player.execute_move(move_name, weapon_name=weapon_name)
        # Both modifiers must be below 1.0.
        self.assertLess(result["proficiency_modifier"], 1.0)
        self.assertLess(result["durability_ratio"], 1.0)
        # Damage must equal the formula with both modifiers applied.
        expected_damage = int(
            self.player.stats.power
            * move.power_scale
            * result["proficiency_modifier"]
            * result["durability_ratio"]
        )
        self.assertEqual(result["damage"], expected_damage)
        self.assertFalse(result["insufficient_chakra"])


class RivalProfileReputationTests(unittest.TestCase):
    """Verify that update_relationship now incorporates player_reputation."""

    def _make_rival(self, alignment: str = "heroic") -> RivalProfile:
        rival = RivalProfile(name="Storm Hawk", affinity=Affinity.WIND, alignment=alignment)
        rival.encounter_count = 3
        return rival

    def test_heroic_reputation_resolves_to_friend_regardless_of_alignment(self) -> None:
        rival = self._make_rival(alignment="rogue")
        result = rival.update_relationship(player_reputation=60, player_alignment="rogue")
        self.assertEqual(result, "friend")

    def test_rogue_reputation_resolves_to_nemesis_regardless_of_alignment(self) -> None:
        rival = self._make_rival(alignment="heroic")
        result = rival.update_relationship(player_reputation=-60, player_alignment="heroic")
        self.assertEqual(result, "nemesis")

    def test_neutral_reputation_falls_back_to_alignment_match(self) -> None:
        rival = self._make_rival(alignment="neutral")
        result = rival.update_relationship(player_reputation=0, player_alignment="neutral")
        self.assertEqual(result, "friend")

    def test_neutral_reputation_alignment_mismatch_is_nemesis(self) -> None:
        rival = self._make_rival(alignment="heroic")
        result = rival.update_relationship(player_reputation=0, player_alignment="rogue")
        self.assertEqual(result, "nemesis")

    def test_low_encounter_count_stays_rival_regardless_of_reputation(self) -> None:
        rival = RivalProfile(name="Test", affinity=Affinity.FIRE)
        rival.encounter_count = 1
        result = rival.update_relationship(player_reputation=100, player_alignment="heroic")
        self.assertEqual(result, "rival")

    def test_zero_encounters_stays_stranger(self) -> None:
        rival = RivalProfile(name="Test", affinity=Affinity.EARTH)
        result = rival.update_relationship(player_reputation=100, player_alignment="heroic")
        self.assertEqual(result, "stranger")
