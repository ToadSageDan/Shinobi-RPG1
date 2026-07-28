import unittest

from shinobi_rpg.core import (
    Affinity,
    Move,
    MoveCategory,
    PlayerProfile,
    build_mvp_world,
    resolve_affinity_minigame,
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

    def test_affinity_minigame_resolves_top_score(self):
        affinity = resolve_affinity_minigame([5, 1, 1, 1, 2])
        self.assertEqual(affinity, Affinity.FIRE)

    def test_rogue_reputation_unlocks_black_market(self):
        player = PlayerProfile(name="Tester", affinity=Affinity.WIND)
        tier = player.update_reputation(-60)
        self.assertEqual(tier.value, "rogue")
        self.assertIn("black_market", player.unlocked_zones)

    def test_world_seed_meets_mvp_size_and_region_clear_reward(self):
        world, player = build_mvp_world("Dan", [2, 4, 1, 3, 5])
        self.assertGreaterEqual(len(world.allies), 10)
        reward = world.clear_region(player, "Verdant Gate", "weapon")
        self.assertEqual(reward, "Renda Fang Blade")
        self.assertIn("Verdant Gate", player.unlocked_fast_travel_nodes)

    def test_leveling_progression_increases_stats(self):
        world, player = build_mvp_world("Dan", [1, 1, 1, 1, 1])
        before_level = player.stats.level
        before_power = player.stats.power
        player.stats.gain_xp(500)
        self.assertGreater(player.stats.level, before_level)
        self.assertGreater(player.stats.power, before_power)

    def test_vault_archives_historic_ninja(self):
        world, player = build_mvp_world("Dot", [1, 3, 5, 2, 1])
        world.archive_historic_ninja(player)
        self.assertEqual(world.vault_historic_ninjas[0]["name"], "Dot")


if __name__ == "__main__":
    unittest.main()
