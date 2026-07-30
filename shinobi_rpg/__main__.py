"""Command-line entry point for bootstrapping the Shinobi RPG MVP."""

from __future__ import annotations

from .framework import framework_overview_json


def main() -> int:
    print(framework_overview_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
