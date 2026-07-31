"""Command-line entry point for launching the Shinobi RPG runtime client."""

from __future__ import annotations

from .client import runtime_package_json

__all__ = ["main"]


def main() -> int:
    print(runtime_package_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
