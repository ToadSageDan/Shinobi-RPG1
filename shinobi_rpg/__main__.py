"""Command-line entry point for bootstrapping the Shinobi RPG MVP.

Usage:
    python -m shinobi_rpg         # print framework JSON snapshot
    python -m shinobi_rpg play    # launch the interactive CLI game loop
"""

from __future__ import annotations

import sys

from .framework import framework_overview_json


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        from .cli import main as play_main  # noqa: PLC0415
        return play_main()
    print(framework_overview_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
