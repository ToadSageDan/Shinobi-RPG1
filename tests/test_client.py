import unittest
from shinobi_rpg.core import (
    DEFAULT_ALLY_MIN_COUNT,
)
from contextlib import redirect_stdout
from io import StringIO
from shinobi_rpg.client import ShinobiRuntimeClient, runtime_package_json
from shinobi_rpg.framework import get_framework_overview
from shinobi_rpg.__main__ import main


class RuntimeClientFrameworkTests(unittest.TestCase):
        def test_framework_overview_exposes_build_ready_content(self):
            overview = get_framework_overview()
            self.assertEqual(overview["project"], "Shinobi-RPG1")
            self.assertEqual(overview["player_bootstrap"]["name"], "Dan")
            self.assertIn(overview["player_bootstrap"]["affinity"], overview["framework"]["affinities"])
            self.assertEqual(overview["development"]["entrypoint"], "python -m shinobi_rpg")
            self.assertGreaterEqual(overview["seeded_content"]["allies"], DEFAULT_ALLY_MIN_COUNT)
            self.assertGreaterEqual(overview["seeded_content"]["regions"], 1)
            self.assertGreaterEqual(overview["seeded_content"]["points_of_interest"], 20)

        def test_cli_main_prints_runtime_package_json(self):
            buffer = StringIO()
            with redirect_stdout(buffer):
                exit_code = main()
            output = buffer.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertEqual(output.strip(), runtime_package_json())

        def test_runtime_client_builds_visual_vertical_slice_package(self):
            runtime = ShinobiRuntimeClient("TestPlayer")
            package = runtime.build_runtime_package()
            self.assertEqual(package["visual_target"]["style"], "2.5D_stylized")
            self.assertEqual(package["simulation_layer"], "shinobi_rpg.core")
            self.assertEqual(package["presentation_layer"], "shinobi_rpg.client")
            self.assertEqual(len(package["scenes"]), 4)
            scene_keys = {scene["key"] for scene in package["scenes"]}
            self.assertIn("title_menu", scene_keys)
            self.assertIn("interactive_world_map", scene_keys)
            self.assertIn("combat_timeline_preview", scene_keys)
            self.assertIn("vertical_slice_verdant_gate", scene_keys)

