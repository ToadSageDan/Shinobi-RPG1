"""Lightweight foundation systems for Shinobi RPG MVP."""

from .core import (
    Affinity,
    Move,
    MoveCategory,
    NinjaWorld,
    PlayerProfile,
    Quest,
    Region,
    ReputationTier,
    Weapon,
    WeaponType,
    build_mvp_world,
    resolve_affinity_minigame,
)

__all__ = [
    "Affinity",
    "Move",
    "MoveCategory",
    "NinjaWorld",
    "PlayerProfile",
    "Quest",
    "Region",
    "ReputationTier",
    "Weapon",
    "WeaponType",
    "build_mvp_world",
    "resolve_affinity_minigame",
]
