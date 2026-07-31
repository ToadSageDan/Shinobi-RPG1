"""Command-line entry point for launching the Shinobi RPG runtime client.

Usage:
    python -m shinobi_rpg         # print runtime package JSON
    python -m shinobi_rpg play    # launch the interactive CLI game loop
"""

from __future__ import annotations

import sys

from .client import runtime_package_json

__all__ = ["main"]


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        from .cli import main as play_main  # noqa: PLC0415
        return play_main()
    print(runtime_package_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
