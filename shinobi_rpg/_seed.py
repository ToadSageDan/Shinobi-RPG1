from __future__ import annotations

import random
from typing import Any, Dict, List, Sequence, Tuple

from ._constants import *
from ._models import *
from ._models import _empty_affinity_scores, _ordered_unique_affinities
from ._types import *

def resolve_affinity_minigame(decisions: Sequence[int]) -> Affinity:
    """Resolve starting affinity from mini-game decisions.

    Scores are applied in affinity order (Fire, Water, Earth, Wind) and
    wrap cyclically when more than four decisions are provided.
    Higher total score wins; ties resolve by the same affinity order.
    """
    scores = _empty_affinity_scores()
    for idx, value in enumerate(decisions):
        scores[AFFINITY_ORDER[idx % len(AFFINITY_ORDER)]] += value
    ranked = sorted(
        scores.items(),
        key=lambda item: (-item[1], AFFINITY_ORDER.index(item[0])),
    )
    return ranked[0][0]


def assign_affinity_from_choices(choices: Sequence[str]) -> Affinity:
    """Resolve starting affinity from explicit mini-game choice answers.

    The affinity with the highest answer count wins; ties resolve by
    Fire, then Water, then Earth, then Wind.
    """
    if not choices:
        raise ValueError("Mini-game choices cannot be empty.")

    scores = _empty_affinity_scores()
    for raw_choice in choices:
        normalized = raw_choice.strip().lower()
        affinity = AFFINITY_MINIGAME_CHOICES.get(normalized)
        if not affinity:
            raise ValueError(f'Unknown affinity choice "{normalized}".')
        scores[affinity] += 1

    ranked = sorted(
        scores.items(),
        key=lambda item: (-item[1], AFFINITY_ORDER.index(item[0])),
    )
    return ranked[0][0]


def _paired_affinity_for_ultimate(primary: Affinity) -> Affinity:
    """Select a simple paired affinity for starter mixed ultimates.

    MVP design pairs Wind with Fire; all other primaries pair with Wind
    to keep two-element ultimates broadly balanced around mobility/control.
    """
    if primary == Affinity.WIND:
        return Affinity.FIRE
    return Affinity.WIND


def _summon_names_for_affinity(primary: Affinity) -> Tuple[str, str]:
    return {
        Affinity.FIRE: ("Blazehound Pact", "Cinder Mantis Pact"),
        Affinity.WATER: ("Undertow Serpent Pact", "Mist Heron Pact"),
        Affinity.EARTH: ("Stone Ram Pact", "Granite Tortoise Pact"),
        Affinity.WIND: ("Sky Hawk Pact", "Tempest Lynx Pact"),
    }[primary]


def _seed_weapons() -> List[Weapon]:
    return [
        Weapon(
            "Dawn Cutter",
            WeaponType.SWORD,
            "balanced duelist",
            18,
            status_effects=(StatusEffectType.BLEED,),
        ),
        Weapon(
            "Silent Fang",
            WeaponType.KUNAI,
            "high-mobility burst",
            14,
            status_effects=(StatusEffectType.BLIND,),
        ),
        Weapon(
            "Temple Branch",
            WeaponType.BOW_STAFF,
            "control and spacing",
            16,
            status_effects=(StatusEffectType.STAGGER,),
        ),
        Weapon(
            "Storm Scatter",
            WeaponType.NINJA_STARS,
            "ranged precision",
            15,
            status_effects=(StatusEffectType.CRACK_ARMOR,),
        ),
    ]


def _blend_animation_beats(descriptions: Sequence[str]) -> str:
    unique_descriptions = list(dict.fromkeys(descriptions))
    if len(unique_descriptions) == 1:
        return unique_descriptions[0]
    if len(unique_descriptions) == 2:
        return f"{unique_descriptions[0]} fused with {unique_descriptions[1]}"
    return f'{", ".join(unique_descriptions[:-1])}, and {unique_descriptions[-1]}'


def _affinity_animation_profile(affinities: Sequence[Affinity], category: MoveCategory) -> Dict[str, str]:
    styles = {
        Affinity.FIRE: {
            "startup": "embers flare at shoulders",
            "travel": "corkscrew flame lane",
            "hit": "expanding orange-red shock ring",
            "recovery": "ash drift and heat shimmer",
        },
        Affinity.WATER: {
            "startup": "water ribbon spiral at feet",
            "travel": "mist-lined current slash",
            "hit": "splash arc with ripple pulse",
            "recovery": "droplets fall into still wake",
        },
        Affinity.EARTH: {
            "startup": "seal stamp with rising rock plates",
            "travel": "debris-skid pressure lane",
            "hit": "fissure burst and heavy camera thud",
            "recovery": "stone fragments settle",
        },
        Affinity.WIND: {
            "startup": "compressed air ring gathers",
            "travel": "slicing crescent streaks",
            "hit": "pressure ripple cross-cut",
            "recovery": "feather-light afterimage fade",
        },
    }
    ordered_affinities = _ordered_unique_affinities(affinities)
    animation_styles = [styles[affinity] for affinity in ordered_affinities]
    return {
        "startup": _blend_animation_beats([style["startup"] for style in animation_styles]),
        "travel": _blend_animation_beats([style["travel"] for style in animation_styles]),
        "hit": f'{_blend_animation_beats([style["hit"] for style in animation_styles])} ({category.value})',
        "recovery": _blend_animation_beats([style["recovery"] for style in animation_styles]),
    }


def _make_move(
    name: str,
    category: MoveCategory,
    affinities: Tuple[Affinity, ...],
    power_scale: float,
    technique_type: TechniqueType,
    status_effects: Tuple[StatusEffectType, ...] = (),
) -> Move:
    return Move(
        name=name,
        category=category,
        affinities=affinities,
        power_scale=power_scale,
        technique_type=technique_type,
        status_effects=status_effects,
        animation_profile=_affinity_animation_profile(affinities, category),
    )


def _seed_shared_move_pool() -> Dict[MoveCategory, List[Move]]:
    return {
        MoveCategory.ESCAPE: [
            _make_move("Smoke Step", MoveCategory.ESCAPE, (Affinity.FIRE,), 0.6, TechniqueType.MOBILITY),
            _make_move("Afterimage Drift", MoveCategory.ESCAPE, (Affinity.WATER,), 0.7, TechniqueType.CLONE),
            _make_move("Silent Reed Slip", MoveCategory.ESCAPE, (Affinity.EARTH,), 0.75, TechniqueType.SENSORY),
            _make_move("Mistfold Break", MoveCategory.ESCAPE, (Affinity.WATER,), 0.72, TechniqueType.ILLUSION),
            _make_move("Stone Skip Dash", MoveCategory.ESCAPE, (Affinity.EARTH,), 0.68, TechniqueType.MOBILITY),
            _make_move("Crosswind Fade", MoveCategory.ESCAPE, (Affinity.WIND,), 0.74, TechniqueType.CLONE),
            _make_move(
                "Ember Veil Vault",
                MoveCategory.ESCAPE,
                (Affinity.FIRE,),
                0.71,
                TechniqueType.MOBILITY,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Tidal Blink",
                MoveCategory.ESCAPE,
                (Affinity.WATER,),
                0.73,
                TechniqueType.SUPPORT,
                (StatusEffectType.DRENCH,),
            ),
            _make_move("Burrow Snap", MoveCategory.ESCAPE, (Affinity.EARTH,), 0.69, TechniqueType.MOBILITY),
            _make_move("Gale Feather Shift", MoveCategory.ESCAPE, (Affinity.WIND,), 0.76, TechniqueType.SENSORY),
            _make_move(
                "Phantom Lantern Exit",
                MoveCategory.ESCAPE,
                (Affinity.WIND,),
                0.75,
                TechniqueType.ILLUSION,
                (StatusEffectType.BLIND,),
            ),
            _make_move("Iron Cicada Swap", MoveCategory.ESCAPE, (Affinity.EARTH,), 0.7, TechniqueType.CLONE),
        ],
        MoveCategory.ATTACK: [
            _make_move("Edge Current", MoveCategory.ATTACK, (Affinity.FIRE,), 1.0, TechniqueType.ELEMENTAL),
            _make_move(
                "Threadline Volley",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.05,
                TechniqueType.WEAPON_STYLE,
            ),
            _make_move(
                "Pressure Knot Strike",
                MoveCategory.ATTACK,
                (Affinity.EARTH,),
                1.1,
                TechniqueType.SUPPORT,
            ),
            _make_move(
                "Cinder Lance",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.02,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Undertow Slice",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.03,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.DRENCH,),
            ),
            _make_move(
                "Faultline Jab",
                MoveCategory.ATTACK,
                (Affinity.EARTH,),
                1.04,
                TechniqueType.WEAPON_STYLE,
                (StatusEffectType.CRACK_ARMOR,),
            ),
            _make_move("Razor Gale Arc", MoveCategory.ATTACK, (Affinity.WIND,), 1.0, TechniqueType.ELEMENTAL),
            _make_move(
                "Ash Fang Drive",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.08,
                TechniqueType.WEAPON_STYLE,
                (StatusEffectType.BLEED,),
            ),
            _make_move(
                "Torrent Breaker",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.06,
                TechniqueType.SUPPORT,
                (StatusEffectType.CHILL,),
            ),
            _make_move("Granite Spearline", MoveCategory.ATTACK, (Affinity.EARTH,), 1.07, TechniqueType.ELEMENTAL),
            _make_move(
                "Tempest Hook",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.05,
                TechniqueType.WEAPON_STYLE,
                (StatusEffectType.STAGGER,),
            ),
            _make_move(
                "Shadow Nail Burst",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.09,
                TechniqueType.ILLUSION,
                (StatusEffectType.FEAR,),
            ),
        ],
        MoveCategory.DEFENSE: [
            _make_move("Guarding Veil", MoveCategory.DEFENSE, (Affinity.FIRE,), 0.8, TechniqueType.BARRIER),
            _make_move("Lattice Ward", MoveCategory.DEFENSE, (Affinity.WATER,), 0.78, TechniqueType.SEALING),
            _make_move("Flowback Mantle", MoveCategory.DEFENSE, (Affinity.EARTH,), 0.75, TechniqueType.SUPPORT),
            _make_move("Current Shell", MoveCategory.DEFENSE, (Affinity.WATER,), 0.9, TechniqueType.BARRIER),
            _make_move("Ash Aegis", MoveCategory.DEFENSE, (Affinity.FIRE,), 0.74, TechniqueType.BARRIER),
            _make_move("Granite Net Seal", MoveCategory.DEFENSE, (Affinity.EARTH,), 0.95, TechniqueType.SEALING),
            _make_move(
                "Pressure Dome",
                MoveCategory.DEFENSE,
                (Affinity.WIND,),
                0.84,
                TechniqueType.BARRIER,
                (StatusEffectType.STAGGER,),
            ),
            _make_move("Mirror Bark Plate", MoveCategory.DEFENSE, (Affinity.EARTH,), 0.88, TechniqueType.SUPPORT),
            _make_move(
                "Cyclone Parry Ring",
                MoveCategory.DEFENSE,
                (Affinity.WIND,),
                0.86,
                TechniqueType.WEAPON_STYLE,
                (StatusEffectType.BLIND,),
            ),
            _make_move("Reef Anchor Guard", MoveCategory.DEFENSE, (Affinity.WATER,), 0.89, TechniqueType.BARRIER),
            _make_move("Dune Bastion", MoveCategory.DEFENSE, (Affinity.EARTH,), 0.87, TechniqueType.SEALING),
            _make_move(
                "Moonlit Counter Seal",
                MoveCategory.DEFENSE,
                (Affinity.WIND,),
                0.83,
                TechniqueType.ILLUSION,
                (StatusEffectType.SILENCE,),
            ),
        ],
        MoveCategory.SUMMON: [
            _make_move(
                "Blazehound Pact",
                MoveCategory.SUMMON,
                (Affinity.FIRE,),
                1.0,
                TechniqueType.SUMMONING,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Cinder Mantis Pact",
                MoveCategory.SUMMON,
                (Affinity.FIRE,),
                1.1,
                TechniqueType.SUMMONING,
                (StatusEffectType.BLEED,),
            ),
            _make_move(
                "Undertow Serpent Pact",
                MoveCategory.SUMMON,
                (Affinity.WATER,),
                1.0,
                TechniqueType.SUMMONING,
                (StatusEffectType.DRENCH,),
            ),
            _make_move(
                "Mist Heron Pact",
                MoveCategory.SUMMON,
                (Affinity.WATER,),
                1.08,
                TechniqueType.SUMMONING,
                (StatusEffectType.BLIND,),
            ),
            _make_move(
                "Stone Ram Pact",
                MoveCategory.SUMMON,
                (Affinity.EARTH,),
                1.0,
                TechniqueType.SUMMONING,
                (StatusEffectType.STAGGER,),
            ),
            _make_move(
                "Granite Tortoise Pact",
                MoveCategory.SUMMON,
                (Affinity.EARTH,),
                1.1,
                TechniqueType.SUMMONING,
                (StatusEffectType.CRACK_ARMOR,),
            ),
            _make_move(
                "Sky Hawk Pact",
                MoveCategory.SUMMON,
                (Affinity.WIND,),
                1.0,
                TechniqueType.SUMMONING,
                (StatusEffectType.BLIND,),
            ),
            _make_move(
                "Tempest Lynx Pact",
                MoveCategory.SUMMON,
                (Affinity.WIND,),
                1.1,
                TechniqueType.SUMMONING,
                (StatusEffectType.CHILL,),
            ),
            _make_move(
                "Ember Jackal Pact",
                MoveCategory.SUMMON,
                (Affinity.FIRE,),
                1.06,
                TechniqueType.SUMMONING,
                (StatusEffectType.FEAR,),
            ),
            _make_move(
                "Tide Eel Pact",
                MoveCategory.SUMMON,
                (Affinity.WATER,),
                1.04,
                TechniqueType.SUMMONING,
                (StatusEffectType.ROOT,),
            ),
            _make_move(
                "Obsidian Ape Pact",
                MoveCategory.SUMMON,
                (Affinity.EARTH,),
                1.07,
                TechniqueType.SUMMONING,
                (StatusEffectType.STAGGER,),
            ),
            _make_move(
                "Whisper Owl Pact",
                MoveCategory.SUMMON,
                (Affinity.WIND,),
                1.05,
                TechniqueType.SUMMONING,
                (StatusEffectType.SILENCE,),
            ),
        ],
        MoveCategory.ULTIMATE: [
            _make_move(
                "Twin Dragon Convergence",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.WIND),
                2.5,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Covenant Horizon Break",
                MoveCategory.ULTIMATE,
                (Affinity.WATER, Affinity.EARTH),
                2.2,
                TechniqueType.SUMMONING,
                (StatusEffectType.ROOT,),
            ),
            _make_move(
                "Concord Nova",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.WIND),
                2.4,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.BURN,),
            ),
            _make_move(
                "Tidal Monolith Break",
                MoveCategory.ULTIMATE,
                (Affinity.WATER, Affinity.EARTH),
                2.35,
                TechniqueType.SUPPORT,
                (StatusEffectType.DRENCH,),
            ),
            _make_move(
                "Skyline Covenant",
                MoveCategory.ULTIMATE,
                (Affinity.WIND, Affinity.WATER),
                2.3,
                TechniqueType.SUMMONING,
                (StatusEffectType.BLIND,),
            ),
            _make_move(
                "Furnace Eclipse",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.EARTH),
                2.45,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.BURN, StatusEffectType.CRACK_ARMOR),
            ),
            _make_move(
                "Leviathan Breakfall",
                MoveCategory.ULTIMATE,
                (Affinity.WATER, Affinity.WIND),
                2.42,
                TechniqueType.SUMMONING,
                (StatusEffectType.DRENCH, StatusEffectType.CHILL),
            ),
            _make_move(
                "Worldroot Fracture",
                MoveCategory.ULTIMATE,
                (Affinity.EARTH, Affinity.FIRE),
                2.38,
                TechniqueType.SEALING,
                (StatusEffectType.ROOT, StatusEffectType.STAGGER),
            ),
            _make_move(
                "Tempest Throne Collapse",
                MoveCategory.ULTIMATE,
                (Affinity.WIND, Affinity.EARTH),
                2.36,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.STAGGER,),
            ),
            _make_move(
                "Ashen Moon Sever",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.WATER),
                2.33,
                TechniqueType.ILLUSION,
                (StatusEffectType.FEAR,),
            ),
            _make_move(
                "Abyss Crown Rupture",
                MoveCategory.ULTIMATE,
                (Affinity.WATER, Affinity.FIRE),
                2.37,
                TechniqueType.BARRIER,
                (StatusEffectType.SILENCE,),
            ),
            _make_move(
                "Fourfold Shinobi Oath",
                MoveCategory.ULTIMATE,
                (Affinity.FIRE, Affinity.WIND),
                2.32,
                TechniqueType.SUPPORT,
                (StatusEffectType.BLIND, StatusEffectType.BURN),
            ),
        ],
    }


def _seed_moves(player_affinity: Affinity) -> Dict[MoveCategory, List[Move]]:
    paired = _paired_affinity_for_ultimate(player_affinity)
    pool = _seed_shared_move_pool()
    selected: Dict[MoveCategory, List[Move]] = {category: [] for category in MoveCategory}
    for category in (MoveCategory.ESCAPE, MoveCategory.ATTACK, MoveCategory.DEFENSE, MoveCategory.SUMMON):
        selected[category] = [move for move in pool[category] if move.affinities[0] == player_affinity][:3]
    selected[MoveCategory.ULTIMATE] = [
        move
        for move in pool[MoveCategory.ULTIMATE]
        if player_affinity in move.affinities and paired in move.affinities
    ][:2]
    if len(selected[MoveCategory.ULTIMATE]) < 2:
        selected[MoveCategory.ULTIMATE] = pool[MoveCategory.ULTIMATE][:2]
    return selected


def _seed_technique_library() -> List[Move]:
    pool = _seed_shared_move_pool()
    ordered_categories = [
        MoveCategory.ESCAPE,
        MoveCategory.ATTACK,
        MoveCategory.DEFENSE,
        MoveCategory.SUMMON,
        MoveCategory.ULTIMATE,
    ]
    library = [move for category in ordered_categories for move in pool[category]]
    # Include all enemy-exclusive learnable moves so they appear in the technique catalog
    for spec in ENEMY_EXCLUSIVE_MOVE_SPECS.values():
        library.append(
            _make_move(
                spec["name"],
                spec["category"],
                spec["affinities"],
                spec["power_scale"],
                spec["technique_type"],
                spec["status_effects"],
            )
        )
    return library


def _seed_era_timeline() -> List[Dict[str, Any]]:
    return [
        {
            "key": "war_age",
            "title": "War Age",
            "tone": "fractured",
            "stakes": "survival and territorial pressure",
        },
        {
            "key": "recovery_age",
            "title": "Recovery Age",
            "tone": "fragile",
            "stakes": "rebuild momentum and social trust",
        },
        {
            "key": "hidden_age",
            "title": "Hidden Age",
            "tone": "transformative",
            "stakes": "long-term balance or irreversible decay",
        },
    ]


def _seed_arcs() -> List[ArcDefinition]:
    return [
        ArcDefinition(
            key="political_war",
            title="Political Warfront",
            tone="siege politics",
            stakes="council leverage and control of supply routes",
            regions=("Verdant Gate",),
            era_band="war_age",
        ),
        ArcDefinition(
            key="fracture_front",
            title="Fracture Front",
            tone="attrition",
            stakes="alliances fail or harden under pressure",
            regions=("Ashen Cradle", "Sunken Hollow"),
            era_band="recovery_age",
        ),
        ArcDefinition(
            key="recovery_mandate",
            title="Recovery Mandate",
            tone="reconstruction",
            stakes="world stabilizes or collapses into splinter rule",
            regions=("Tideglass Basin",),
            era_band="hidden_age",
        ),
        ArcDefinition(
            key="rebellion_wave",
            title="Rebellion Wave",
            tone="volatile",
            stakes="minor actors radicalize into existential threats",
            regions=("Verdant Gate", "Ashen Cradle", "Stormwall Ridge"),
            era_band="hidden_age",
        ),
        ArcDefinition(
            key="highland_reckoning",
            title="Highland Reckoning",
            tone="siege and sovereignty",
            stakes="a warlord's highland domain falls or expands to swallow nearby territories",
            regions=("Stormwall Ridge",),
            era_band="war_age",
        ),
        ArcDefinition(
            key="depths_awakening",
            title="Depths Awakening",
            tone="dread and excavation",
            stakes="forgotten underground power is weaponized or sealed before it destabilizes the surface",
            regions=("Sunken Hollow",),
            era_band="hidden_age",
        ),
    ]


def _seed_regions() -> List[Region]:
    return [
        Region(
            name="Verdant Gate",
            village_hub="Leafrise Village",
            enemies=["Bandit Scouts", "Mist Ronin", "Root Stalkers"],
            encounter_table=[
                "Academy Shinobi",
                "Bandit Scouts",
                "Mist Ronin",
                "Root Stalkers",
                "Gate Patrol Guard",
                "Moss Boar",
                "Hidden Sentry",
            ],
            allies=["Dan"],
            boss="Kage Renda",
            boss_rewards={
                "weapon": "Renda Fang Blade",
                "clothing": "Shadow Mantle",
                "move": "Razorwind Spiral",
            },
            arc_key="political_war",
            climate="humid forest frontier",
            terrain_profile=("old-growth canopy", "river switchbacks", "stone terraces"),
            strategic_value="Controls grain roads and courier channels between interior clans and the capital",
            minimum_level=1,
            assassin_hunter_name="Whisperroot Blade Circle",
            travel_nodes=[
                "Leafrise Village",
                "Whisperroot Crossing",
                "Saffron Relay Fort",
                "Renda Skybridge",
            ],
            points_of_interest=[
                PointOfInterest(
                    name="Leafrise Village",
                    poi_type="hub",
                    summary="Trade-and-training village with gate towers that monitor every road into Verdant Gate.",
                    control_faction="Leafrise Council",
                    threats=("sleeper bandit scouts",),
                    services=("smithy", "healer", "mission board", "fast_travel_node"),
                    connected_nodes=("Whisperroot Crossing", "Saffron Relay Fort"),
                ),
                PointOfInterest(
                    name="Whisperroot Crossing",
                    poi_type="chokepoint",
                    summary="A fog-dense bridge network where Mist Ronin ambush caravans under false crest banners.",
                    control_faction="Contested",
                    threats=("Mist Ronin", "trapwire cells"),
                    services=("intel_cache",),
                    connected_nodes=("Leafrise Village", "Renda Skybridge"),
                ),
                PointOfInterest(
                    name="Saffron Relay Fort",
                    poi_type="fortification",
                    summary="Courier stronghold with coded signal drums that can lock down regional supply lanes in minutes.",
                    control_faction="Leafrise Council",
                    threats=("root-stalker tunnels", "insider sabotage"),
                    services=("armory", "scouting_contracts"),
                    connected_nodes=("Leafrise Village", "Renda Skybridge"),
                ),
                PointOfInterest(
                    name="Renda Skybridge",
                    poi_type="boss_arena",
                    summary="Wind-carved cliff span where Kage Renda stages formal duels to decide route ownership.",
                    control_faction="Kage Renda",
                    threats=("Kage Renda", "shearwind updrafts"),
                    services=("boss_gate", "vista_recon"),
                    connected_nodes=("Whisperroot Crossing", "Saffron Relay Fort"),
                ),
            ],
            tutorial_mechanics=("blocking", "substitution"),
        ),
        Region(
            name="Ashen Cradle",
            village_hub="Cinder Port",
            enemies=["Ash Mercenaries", "Lava Hounds"],
            encounter_table=[
                "Cinder Trainee Shinobi",
                "Ash Mercenaries",
                "Ember Raiders",
                "Port Guard Cadet",
                "Lava Hounds",
                "Ash Boar",
            ],
            allies=["Moon", "Sleep"],
            boss="General Voln",
            boss_rewards={
                "weapon": "Cradle Cleaver",
                "clothing": "Molten Gi",
                "move": "Inferno Vortex",
            },
            arc_key="fracture_front",
            climate="volcanic dry heat",
            terrain_profile=("slag fields", "lava channels", "ash dunes"),
            strategic_value="Primary smelting corridor and munitions route for the fracture-front war machine",
            minimum_level=4,
            assassin_hunter_name="Ashen Cinder Assassins",
            travel_nodes=[
                "Cinder Port",
                "Furnace Mile",
                "Voln Barricade Line",
                "Ember Crown Crucible",
            ],
            points_of_interest=[
                PointOfInterest(
                    name="Cinder Port",
                    poi_type="hub",
                    summary="Black-glass harbor that moves ore, mercenaries, and ration caravans under rotating curfews.",
                    control_faction="Port Syndicates",
                    threats=("dock extortion crews",),
                    services=("weapon_vendor", "forge_upgrades", "fast_travel_node"),
                    connected_nodes=("Furnace Mile", "Voln Barricade Line"),
                ),
                PointOfInterest(
                    name="Furnace Mile",
                    poi_type="industrial_corridor",
                    summary="Kiln avenue where Ember Raiders skim fuel convoys and trigger chain blasts during raids.",
                    control_faction="Contested",
                    threats=("Ember Raiders", "slag eruptions"),
                    services=("resource_salvage",),
                    connected_nodes=("Cinder Port", "Ember Crown Crucible"),
                ),
                PointOfInterest(
                    name="Voln Barricade Line",
                    poi_type="warfront",
                    summary="Layered trench-and-shield wall where General Voln drills attrition tactics with ash mercenaries.",
                    control_faction="General Voln Legion",
                    threats=("Ash Mercenaries", "incendiary mortars"),
                    services=("tactical_trials", "supply_restock"),
                    connected_nodes=("Cinder Port", "Ember Crown Crucible"),
                ),
                PointOfInterest(
                    name="Ember Crown Crucible",
                    poi_type="boss_arena",
                    summary="Collapsed caldera ring where Voln channels magma vents into sustained battlefield pressure.",
                    control_faction="General Voln",
                    threats=("General Voln", "lava burst cycles"),
                    services=("boss_gate", "heat_resistance_trial"),
                    connected_nodes=("Furnace Mile", "Voln Barricade Line"),
                ),
            ],
            tutorial_mechanics=("aoe_attacks",),
        ),
        Region(
            name="Tideglass Basin",
            village_hub="Azure Rest",
            enemies=["Tide Hunters", "Reef Assassins"],
            encounter_table=[
                "Basin Shinobi Trainee",
                "Tide Hunters",
                "Reef Assassins",
                "Basin Corsairs",
                "Harbor Guard",
                "Reef Otter Pack",
            ],
            allies=["Dot", "Porter"],
            boss="Admiral Neris",
            boss_rewards={
                "weapon": "Basin Pike",
                "clothing": "Tidewoven Cloak",
                "move": "Maelstrom Guard",
            },
            arc_key="recovery_mandate",
            climate="monsoon coastal",
            terrain_profile=("flood terraces", "reef canals", "salt flats"),
            strategic_value="Secures medical imports and sea access needed for post-war stabilization",
            minimum_level=7,
            assassin_hunter_name="Reefshade Stalker Syndicate",
            travel_nodes=[
                "Azure Rest",
                "Shimmerlock Pier",
                "Coral Intake Channels",
                "Neris Tidal Court",
            ],
            points_of_interest=[
                PointOfInterest(
                    name="Azure Rest",
                    poi_type="hub",
                    summary="Recovery port where healers, refugees, and tide guards coordinate basin reconstruction.",
                    control_faction="Recovery Mandate Wardens",
                    threats=("corsair infiltrators",),
                    services=("clinic", "supply_exchange", "fast_travel_node"),
                    connected_nodes=("Shimmerlock Pier", "Coral Intake Channels"),
                ),
                PointOfInterest(
                    name="Shimmerlock Pier",
                    poi_type="trade_route",
                    summary="Stilted dock lattice with submerged smuggler shafts used by Tide Hunters at high rain tide.",
                    control_faction="Contested",
                    threats=("Tide Hunters", "undertow traps"),
                    services=("fishing_contracts", "intel_drop"),
                    connected_nodes=("Azure Rest", "Neris Tidal Court"),
                ),
                PointOfInterest(
                    name="Coral Intake Channels",
                    poi_type="infrastructure",
                    summary="Flood-control gates that determine whether inland farms receive clean water or salt ruin.",
                    control_faction="Basin Engineers",
                    threats=("Reef Assassins", "gate overload"),
                    services=("water_route_switches", "defense_simulator"),
                    connected_nodes=("Azure Rest", "Neris Tidal Court"),
                ),
                PointOfInterest(
                    name="Neris Tidal Court",
                    poi_type="boss_arena",
                    summary="Spiral amphitheater below sea level where Admiral Neris manipulates current walls in combat.",
                    control_faction="Admiral Neris",
                    threats=("Admiral Neris", "pressure-wave surges"),
                    services=("boss_gate", "water_affinity_trial"),
                    connected_nodes=("Shimmerlock Pier", "Coral Intake Channels"),
                ),
            ],
        ),
        Region(
            name="Stormwall Ridge",
            village_hub="Crestfall Outpost",
            enemies=["Windcutter Raiders", "Gale Monks", "Ridge Wolves"],
            encounter_table=[
                "Ridge Shinobi Aspirant",
                "Windcutter Raiders",
                "Gale Monks",
                "Stormwall Guard",
                "Ridge Wolves",
                "Stormcaller Scouts",
                "Aerial Sentry",
            ],
            allies=["Dan", "Moon"],
            boss="Zephyr Tyrant",
            boss_rewards={
                "weapon": "Ridge Gale Blade",
                "clothing": "Stormweave Mantle",
                "move": "Cyclone Throne Shatter",
            },
            arc_key="highland_reckoning",
            climate="alpine thunder belt",
            terrain_profile=("knife ridgelines", "floating scree fields", "lightning spires"),
            strategic_value="Highland relay for long-range signaling and anti-air control over three border provinces",
            minimum_level=10,
            assassin_hunter_name="Stormwall Talon Assassins",
            travel_nodes=[
                "Crestfall Outpost",
                "Tempest Watchline",
                "Monk Echo Cloister",
                "Tyrant Crown Mesa",
            ],
            points_of_interest=[
                PointOfInterest(
                    name="Crestfall Outpost",
                    poi_type="hub",
                    summary="Windbreak bastion anchoring all ridge ascents with rotating storm alarms.",
                    control_faction="Ridge Wardens",
                    threats=("raider scouts",),
                    services=("gear_repair", "altitude_training", "fast_travel_node"),
                    connected_nodes=("Tempest Watchline", "Monk Echo Cloister"),
                ),
                PointOfInterest(
                    name="Tempest Watchline",
                    poi_type="chokepoint",
                    summary="Chain of lightning rods and ballista nests repeatedly seized by Windcutter raider flights.",
                    control_faction="Contested",
                    threats=("Windcutter Raiders", "stormcaller barrages"),
                    services=("sniper_post",),
                    connected_nodes=("Crestfall Outpost", "Tyrant Crown Mesa"),
                ),
                PointOfInterest(
                    name="Monk Echo Cloister",
                    poi_type="sanctum",
                    summary="Suspended monastery where Gale Monks encode weather prophecy into defensive chants.",
                    control_faction="Gale Monks",
                    threats=("ritual backlash", "ridge wolves"),
                    services=("wind_seal_training", "meditation_buff"),
                    connected_nodes=("Crestfall Outpost", "Tyrant Crown Mesa"),
                ),
                PointOfInterest(
                    name="Tyrant Crown Mesa",
                    poi_type="boss_arena",
                    summary="Split-plateau throne where the Zephyr Tyrant weaponizes jet streams and falling debris.",
                    control_faction="Zephyr Tyrant",
                    threats=("Zephyr Tyrant", "cyclone bursts"),
                    services=("boss_gate", "aerial_duel_trial"),
                    connected_nodes=("Tempest Watchline", "Monk Echo Cloister"),
                ),
            ],
            tutorial_mechanics=("wind_resistance", "aerial_dodge"),
        ),
        Region(
            name="Sunken Hollow",
            village_hub="Dusk Refuge",
            enemies=["Cave Stalkers", "Poison Adepts", "Hollow Wraiths"],
            encounter_table=[
                "Hollow Shinobi Scout",
                "Cave Stalkers",
                "Poison Adepts",
                "Refuge Guard",
                "Hollow Wraiths",
                "Ember Moles",
                "Cave Bats",
                "Deep Sentries",
            ],
            allies=["Sleep", "Dot"],
            boss="Ashen Monarch",
            boss_rewards={
                "weapon": "Hollow Shard Axe",
                "clothing": "Ashbone Shroud",
                "move": "Subterranean Collapse",
            },
            arc_key="depths_awakening",
            climate="subterranean toxic",
            terrain_profile=("collapsed caverns", "fungal sinkholes", "obsidian catacombs"),
            strategic_value="Hidden ore vault and relic lattice that can destabilize every surface alliance if seized",
            minimum_level=14,
            assassin_hunter_name="Hollow Veil Executioners",
            travel_nodes=[
                "Dusk Refuge",
                "Mire Lantern Warrens",
                "Poison Loom Galleries",
                "Monarch Deep Vault",
            ],
            points_of_interest=[
                PointOfInterest(
                    name="Dusk Refuge",
                    poi_type="hub",
                    summary="Last stable cavern settlement using glowstone beacons to map safe descent corridors.",
                    control_faction="Refuge Keepers",
                    threats=("surface raider incursions",),
                    services=("antidote_shop", "route_mapping", "fast_travel_node"),
                    connected_nodes=("Mire Lantern Warrens", "Poison Loom Galleries"),
                ),
                PointOfInterest(
                    name="Mire Lantern Warrens",
                    poi_type="maze",
                    summary="Bioluminescent tunnel web where Cave Stalkers erase tracks and isolate patrol teams.",
                    control_faction="Contested",
                    threats=("Cave Stalkers", "sink gas pockets"),
                    services=("stealth_trial", "hidden_cache"),
                    connected_nodes=("Dusk Refuge", "Monarch Deep Vault"),
                ),
                PointOfInterest(
                    name="Poison Loom Galleries",
                    poi_type="laboratory",
                    summary="Broken alchemy halls where Poison Adepts weave airborne toxins into mineral fog.",
                    control_faction="Poison Adepts",
                    threats=("venom pressure traps", "Hollow Wraiths"),
                    services=("resistance_crafting", "hazard_research"),
                    connected_nodes=("Dusk Refuge", "Monarch Deep Vault"),
                ),
                PointOfInterest(
                    name="Monarch Deep Vault",
                    poi_type="boss_arena",
                    summary="Ancient fracture chamber where the Ashen Monarch channels seismic pulses through relic pillars.",
                    control_faction="Ashen Monarch",
                    threats=("Ashen Monarch", "collapse shockwaves"),
                    services=("boss_gate", "earthbreaker_trial"),
                    connected_nodes=("Mire Lantern Warrens", "Poison Loom Galleries"),
                ),
            ],
            tutorial_mechanics=("underground_navigation", "poison_resistance"),
        ),
    ]


def _boss_exclusive_move_for(villain_name: str) -> Move:
    """Build the boss-only move reward configured for a region boss."""
    spec = BOSS_EXCLUSIVE_MOVE_SPECS.get(villain_name)
    if not spec:
        raise ValueError(
            f'Boss-exclusive move specification is not defined for villain "{villain_name}".'
        )
    return _make_move(
        spec["name"],
        spec["category"],
        spec["affinities"],
        spec["power_scale"],
        spec["technique_type"],
        spec["status_effects"],
    )


def enemy_exclusive_move_for(enemy_name: str) -> Move | None:
    """Return the learnable exclusive move for an important field enemy, or None if not defined.

    Important enemies each carry a signature technique that the player may claim after
    defeating them. This is separate from boss rewards — these moves are learned through
    field encounters rather than region clears.
    """
    spec = ENEMY_EXCLUSIVE_MOVE_SPECS.get(enemy_name)
    if not spec:
        return None
    return _make_move(
        spec["name"],
        spec["category"],
        spec["affinities"],
        spec["power_scale"],
        spec["technique_type"],
        spec["status_effects"],
    )


def get_learnable_enemy_moves() -> Dict[str, str]:
    """Return a mapping of enemy name → exclusive move name for all learnable enemy moves."""
    return {enemy: spec["name"] for enemy, spec in ENEMY_EXCLUSIVE_MOVE_SPECS.items()}


def _validate_boss_move_reward_config(regions: Sequence[Region]) -> None:
    """Validate seeded region bosses that grant move rewards in the current design."""
    for region in regions:
        move_reward_name = region.boss_rewards.get("move")
        if not move_reward_name:
            raise ValueError(f'Region "{region.name}" is missing a boss move reward.')
        spec = BOSS_EXCLUSIVE_MOVE_SPECS.get(region.boss)
        if not spec:
            raise ValueError(
                f'Boss-exclusive move specification is not defined for villain "{region.boss}".'
            )
        if move_reward_name != spec["name"]:
            raise ValueError(
                f'Boss move reward mismatch for "{region.boss}": '
                f'expected "{spec["name"]}", got "{move_reward_name}".'
            )


def _seed_quests() -> List[Quest]:
    quests = [
        Quest(
            quest_id="Q1",
            title="Trial of Quiet Steps",
            objective="Infiltrate the watchpost unseen and recover clan records.",
            stealth_required=True,
            reward_xp=120,
            branch_outcomes={
                "exiled_heir": "A hidden oath marker grants passage, and old sentries stand down at your approach.",
                "street_ghost": "Your underworld contacts open a tunnel route into the watchpost.",
                "wandering_monk": "You walk the patrol rhythm and slip through blind spots without raising alarm.",
                "nonlethal_path": "You rotate stealth feints and silent takedowns, securing the clan records without casualties.",
                "heroic_path": "Your earlier rescues inspire the watchpost sentries to clear a lawful route to the archive room.",
                "rogue_path": "You bribe a black-market quartermaster for guard rotations and slip in before the shift change.",
                "infiltration": "You bypass the front line by scaling hidden cliff routes.",
                "default": "You infiltrate through the drainage channel under moonlight.",
            },
        ),
        Quest(
            quest_id="Q2",
            title="Allies in the Dark",
            objective="Escort Dan through the forest and repel ambushes.",
            stealth_required=False,
            reward_xp=140,
            branch_outcomes={
                "exiled_heir": "Old clan loyalists reveal a safe path and reinforce your escort line.",
                "street_ghost": "You reroute the caravan through smuggler trails and avoid the heaviest trap lines.",
                "wandering_monk": "Your calm mediation de-escalates the ambush, turning a standoff into safe passage.",
                "nonlethal_path": "You redirect every ambush through decoy lanterns and pressure-point disarms until Dan reaches cover safely.",
                "heroic_path": "Your reputation unites frightened scouts into a defensive cordon that walks Dan through the forest alive.",
                "rogue_path": "You cut a deal with rival outriders, trading intel for a corridor that keeps Dan beyond arrow range.",
                "honor_bound": "You challenge the ambushers openly, earning their retreat.",
                "default": "You hold the line and protect Dan until dawn.",
            },
        ),
        Quest(
            quest_id="Q3",
            title="Break the Gate",
            objective="Defeat Kage Renda and secure Verdant Gate.",
            stealth_required=True,
            reward_xp=220,
            branch_outcomes={
                "exiled_heir": "You invoke a legacy challenge and force Kage Renda into a formal duel for the gate.",
                "street_ghost": "You cut supply lines and spring a precision trap before Renda can form a full defense.",
                "wandering_monk": "Through restraint and focus, you disarm Kage Renda without a killing blow.",
                "nonlethal_path": "You disable Renda's strike teams with smoke, binds, and evasion, forcing a surrender at Verdant Gate.",
                "heroic_path": "Your stand at the gate rallies defenders into a coordinated shield line that breaks Renda's advance cleanly.",
                "rogue_path": "You sabotage Renda's command drums and turn his lieutenants with leverage before the final clash begins.",
                "pacifism": "You force a surrender and secure the gate through discipline.",
                "default": "You overpower Kage Renda in a direct final clash.",
            },
        ),
        Quest(
            quest_id="Q4",
            title="Siege of Ember Court",
            objective="Stabilize Ashen Cradle by choosing between alliance, sabotage, or silent containment.",
            stealth_required=False,
            reward_xp=260,
            branch_outcomes={
                "exiled_heir": "You invoke treaty lineage and secure a formal truce with Ember captains.",
                "street_ghost": "You collapse black-market routes and starve the siege from the shadows.",
                "wandering_monk": "You broker a ceasefire and evacuate civilians before hostilities reignite.",
                "nonlethal_path": "You disable siege weapons without casualties and force both sides to stand down.",
                "heroic_path": "Your heroic standing rallies defenders into a disciplined counter-push.",
                "rogue_path": "Rogue operatives accept your contract and burn enemy supply caches overnight.",
                "default": "You seize command of the frontline and end the siege through direct pressure.",
            },
        ),
        Quest(
            quest_id="Q5",
            title="Moonlit Reckoning",
            objective="Confront the Tideglass command ring and decide the final terms of peace.",
            stealth_required=True,
            reward_xp=320,
            branch_outcomes={
                "exiled_heir": "You restore the old charter and bind the command ring to a public oath.",
                "street_ghost": "You expose the ring's hidden ledgers and force surrender through leverage.",
                "wandering_monk": "You dismantle the command ring without executions and secure a disarmament pact.",
                "nonlethal_path": "You neutralize every squad with charm, stealth, and evasion before talks begin.",
                "heroic_path": "Your heroic standing secures a regionwide truce under your witness.",
                "rogue_path": "You force compliance through shadow contracts that keep open war at bay.",
                "default": "You break the command ring in a decisive final confrontation.",
            },
        ),
        Quest(
            quest_id="Q6",
            title="Legacy of the Fallen Shinobi",
            objective="Reach the summit of the Ashen Spire and forge your legacy against the final warlord council.",
            stealth_required=False,
            reward_xp=420,
            branch_outcomes={
                "exiled_heir": (
                    "You invoke your bloodline covenant at the summit gate. The council recognizes the ancient seal "
                    "and grants passage — but demands a duel of honor before the final reckoning."
                ),
                "street_ghost": (
                    "You slip past the summit sentries using stolen council sigils and trigger a blackout across "
                    "their communications before they can coordinate a defense."
                ),
                "wandering_monk": (
                    "You climb in silence and meet the council unarmed. Your willingness to lay down arms forces "
                    "the council into a peace deliberation they cannot publicly refuse."
                ),
                "nonlethal_path": (
                    "Every warlord falls to charm, stealth, and evasion in turn. The final council session "
                    "ends in total surrender — no blood, only shadow."
                ),
                "heroic_path": (
                    "Your heroic reputation precedes you to the summit. Council defectors open a hidden passage "
                    "and stand behind you as witnesses to the reckoning."
                ),
                "rogue_path": (
                    "Rogue guild allies surround the spire before dawn. The council capitulates under the threat "
                    "of coordinated shadow strikes from every side."
                ),
                "default": (
                    "You storm the summit in a direct assault, overpower the warlord council, and carve your "
                    "legend into the walls of the Ashen Spire."
                ),
            },
        ),
        Quest(
            quest_id="Q7",
            title="Shattered Moon Accord",
            objective="Secure the Moonwell sanctum and decide whether to bind, expose, or dissolve the surviving war pacts.",
            stealth_required=False,
            reward_xp=520,
            branch_outcomes={
                "exiled_heir": (
                    "You restore the moon oath in your clan's name, forcing rival houses to swear peace under your seal."
                ),
                "street_ghost": (
                    "You leak pact ledgers to every syndicate at once and collapse the war pacts through public betrayal."
                ),
                "wandering_monk": (
                    "You disarm both factions in the sanctum and guide them into a shared vow of restraint."
                ),
                "nonlethal_path": (
                    "You disable every sentry and lock the sanctum without a single execution, leaving the pact leaders no path but negotiation."
                ),
                "heroic_path": (
                    "Your heroic banner unites scattered villages around the sanctum and compels the war pacts to surrender terms."
                ),
                "rogue_path": (
                    "You seize the pact archives and force signatures through covert leverage before dawn."
                ),
                "default": (
                    "You break into the Moonwell vaults and dictate the accord after a brutal sanctum showdown."
                ),
            },
        ),
        Quest(
            quest_id="Q8",
            title="Dawn of the Hidden Age",
            objective="Lead the first council of the new era and secure a lasting balance between shinobi factions.",
            stealth_required=False,
            reward_xp=620,
            branch_outcomes={
                "exiled_heir": (
                    "You inaugurate the hidden council from your ancestral seat and bind every faction to a bloodline charter."
                ),
                "street_ghost": (
                    "You establish a decentralized council of informants, ensuring no single faction can seize absolute control again."
                ),
                "wandering_monk": (
                    "You dissolve old rank lines, creating a peace council where restraint and service outrank conquest."
                ),
                "nonlethal_path": (
                    "With no blood debt behind you, the final council ratifies a disarmament era in your name."
                ),
                "heroic_path": (
                    "Your heroic record crowns you first guardian of the new age, with former enemies pledging open cooperation."
                ),
                "rogue_path": (
                    "You broker a shadow compact that keeps open war impossible while preserving your underground influence."
                ),
                "default": (
                    "You force a final compromise after one last clash and declare the dawn of a harder but united age."
                ),
            },
        ),
        Quest(
            quest_id="Q9",
            title="Ashes Beneath the Banner",
            objective="Investigate uprising cells in the reclaimed provinces and decide whether to absorb, expose, or silence them.",
            stealth_required=False,
            reward_xp=700,
            branch_outcomes={
                "exiled_heir": (
                    "You call old province captains to your banner and fold the uprising into a sworn reconstruction guard."
                ),
                "street_ghost": (
                    "You trace courier rings through abandoned safehouses and flip the uprising's network into your own shadow relay."
                ),
                "wandering_monk": (
                    "You disarm the cell leaders and broker amnesty terms that trade vengeance for service to the villages."
                ),
                "nonlethal_path": (
                    "You collapse every raid plan with stealth and misdirection, leaving the uprising disarmed without a single grave."
                ),
                "heroic_path": (
                    "Your heroic authority wins public testimony from the provinces, exposing the true agitators behind the revolt."
                ),
                "rogue_path": (
                    "You seize the rebellion's war chest and bind its commanders through covert contracts before they can regroup."
                ),
                "default": (
                    "You break the uprising in a series of relentless strikes and restore control by force."
                ),
            },
        ),
        Quest(
            quest_id="Q10",
            title="Veil of the Eternal Watch",
            objective="Secure the Eternal Watch archive and lock in the final doctrine that will govern the next shinobi generation.",
            stealth_required=True,
            reward_xp=820,
            branch_outcomes={
                "exiled_heir": (
                    "You inscribe your clan's final covenant into the archive and bind the doctrine to sworn guardians."
                ),
                "street_ghost": (
                    "You scatter mirrored copies of the archive and ensure no throne can ever monopolize its truths."
                ),
                "wandering_monk": (
                    "You open the archive to every village and anchor the doctrine in restraint, service, and shared accountability."
                ),
                "nonlethal_path": (
                    "Without blood debt to settle, you secure unanimous passage for a doctrine built on stealth, mercy, and balance."
                ),
                "heroic_path": (
                    "Your heroic legacy earns the final vote, and the Eternal Watch pledges to defend villages before crowns."
                ),
                "rogue_path": (
                    "You encode hidden enforcement clauses and keep the doctrine stable through unseen pressure from the shadows."
                ),
                "default": (
                    "You force a hard compromise into law and secure the archive after one final midnight confrontation."
                ),
            },
        ),
    ]
    quests.extend(_build_extended_quest_chain())
    _normalize_seeded_quest_metadata(quests)
    return quests


def _build_extended_quest_chain() -> List[Quest]:
    specs: List[Dict[str, Any]] = [
        {
            "quest_id": "Q11",
            "title": "Ashes of the Courier",
            "premise": "A missing courier carrying ceasefire terms could trigger renewed war.",
            "objective": "Track down the courier and secure the terms before rival factions intercept them.",
            "choices": ("rescue the courier", "forge replacement terms", "erase the treaty route"),
            "follow_up_hook": "Recovered message routes point to hidden supply ports.",
            "reward_theme": "diplomatic_intel",
            "branch_outcomes": {
                "exiled_heir": (
                    "You invoke dormant courier oaths tied to your bloodline and compel every checkpoint to clear a path."
                ),
                "street_ghost": (
                    "You ghost through black-route couriers and swap the ceasefire packet before any faction spots the handoff."
                ),
                "wandering_monk": (
                    "You disarm the escort without lethal strikes and escort the courier under temple neutrality terms."
                ),
                "nonlethal_path": (
                    "You secure the ceasefire route through stealth, charm, and evasion, ending the crisis without executions."
                ),
                "heroic_path": (
                    "Your standing rallies neutral sentries who escort the courier safely through hostile lines."
                ),
                "rogue_path": (
                    "You seize both original and forged terms, then force the war councils to negotiate on your timetable."
                ),
                "default": (
                    "You storm the interception site, recover the courier, and drag the ceasefire terms back by force."
                ),
            },
        },
        {
            "quest_id": "Q12",
            "title": "Lanterns in the Mist",
            "premise": "Fogbound docks are moving contraband for masked jonin cells.",
            "objective": "Expose, repurpose, or dismantle the port smuggling network.",
            "choices": ("infiltrate the docks", "seize shipments", "negotiate with smugglers"),
            "follow_up_hook": "Smuggler ledgers name tribunal sponsors and hidden judges.",
            "reward_theme": "black_market_influence",
            "branch_outcomes": {
                "exiled_heir": (
                    "You invoke inherited port charters to seize the docks and place every shipment under clan audit."
                ),
                "street_ghost": (
                    "You reroute smuggler lantern codes through your underworld handlers and own the harbor by dawn."
                ),
                "wandering_monk": (
                    "You broker safe exits for coerced crews and convert the docks into monitored relief corridors."
                ),
                "nonlethal_path": (
                    "You collapse the smuggling ring through silent interceptions and negotiated surrenders without bloodshed."
                ),
                "heroic_path": (
                    "Public witness statements and your reputation force tribunal sponsors to admit the contraband network."
                ),
                "rogue_path": (
                    "You spare the ring leaders in exchange for leverage, turning their route map into your covert economy."
                ),
                "default": (
                    "You raid the docks head-on, burn the contraband caches, and break the masked jonin supply chain."
                ),
            },
        },
        {
            "quest_id": "Q13",
            "title": "The Silent Tribunal",
            "premise": "A village tribunal weaponizes your past choices to shift power.",
            "objective": "Protect an ally, condemn them, or collapse the hearing without civil bloodshed.",
            "choices": ("defend the ally", "turn state witness", "expose forged evidence"),
            "follow_up_hook": "Court records reveal tunnels beneath the Hollow Tree shrine.",
            "reward_theme": "political_access",
            "branch_outcomes": {
                "exiled_heir": (
                    "You invoke ancestral legal seals and force the tribunal to reopen under old succession law."
                ),
                "street_ghost": (
                    "You slip witness records through safehouse channels and expose who scripted the tribunal from the shadows."
                ),
                "wandering_monk": (
                    "You halt the verdict with restraint doctrine, turning the hearing into mediated restitution."
                ),
                "nonlethal_path": (
                    "You dismantle every coercion thread through stealth evidence work and calm testimony without executions."
                ),
                "heroic_path": (
                    "Your heroic service record compels public trust, and the tribunal swings toward transparent judgment."
                ),
                "rogue_path": (
                    "You weaponize hidden confessions to break the judges into rival blocs and claim the outcome."
                ),
                "default": (
                    "You expose enough forged evidence to collapse the hearing and settle the dispute through hard pressure."
                ),
            },
        },
        {
            "quest_id": "Q14",
            "title": "Roots of the Hollow Tree",
            "premise": "Ancient tunnel wards protect a relic tied to fractured clan claims.",
            "objective": "Recover, seal, or relocate the relic while surviving legacy traps.",
            "choices": ("disarm seals", "claim relic authority", "destroy the relic"),
            "follow_up_hook": "Relic inscriptions expose a banquet assassination schedule.",
            "reward_theme": "relic_mastery",
            "branch_outcomes": {
                "exiled_heir": (
                    "You read the relic's bloodline cipher and claim lawful custody before rival claimants can contest it."
                ),
                "street_ghost": (
                    "You map forgotten escape roots and relocate the relic through tunnels no registry remembers."
                ),
                "wandering_monk": (
                    "You seal the chamber under stewardship vows and prevent the relic from becoming another war trigger."
                ),
                "nonlethal_path": (
                    "You bypass every trap with stealth and evasion, recovering the relic without leaving a body behind."
                ),
                "heroic_path": (
                    "You publish the relic findings to neutral stewards, earning broad trust in your custody decision."
                ),
                "rogue_path": (
                    "You hide the relic's true chamber and feed rivals decoy routes while consolidating secret control."
                ),
                "default": (
                    "You break through the ward gauntlet, secure the relic, and silence opposition in the lower vaults."
                ),
            },
        },
        {
            "quest_id": "Q15",
            "title": "Feast of Knives",
            "premise": "A peace banquet hides layered assassination contracts.",
            "objective": "Identify the real target and decide whether to protect or exploit them.",
            "choices": ("guard the target", "stage a decoy kill", "broker assassin truces"),
            "follow_up_hook": "Captured assassins trace orders to the Red Pass command.",
            "reward_theme": "court_influence",
            "branch_outcomes": {
                "exiled_heir": (
                    "You invoke banquet blood-right protections and force every blade-bearing envoy to stand down."
                ),
                "street_ghost": (
                    "You rotate seating through coded safehouse signals and make every assassin strike an empty chair."
                ),
                "wandering_monk": (
                    "You disarm the hall and broker truce vows between rivals before the first contract can fire."
                ),
                "nonlethal_path": (
                    "You neutralize each contract network through stealth diversions and diplomacy, ending the feast without blood debt."
                ),
                "heroic_path": (
                    "Your reputation turns wavering guards into defenders, shielding the true target in full public view."
                ),
                "rogue_path": (
                    "You buy out the contract brokers and redirect every killing clause into political leverage."
                ),
                "default": (
                    "You survive the ambush wave, identify the sponsor, and end the banquet with decisive force."
                ),
            },
        },
        {
            "quest_id": "Q16",
            "title": "Crows Over Red Pass",
            "premise": "Border defenses crack as rival commands test your loyalties.",
            "objective": "Hold, evacuate, or sabotage Red Pass before a full invasion lands.",
            "choices": ("fortify and defend", "evacuate civilians", "cripple both armies"),
            "follow_up_hook": "Pass survivors report a broken summoning pact behind the assault.",
            "reward_theme": "military_command",
            "branch_outcomes": {
                "exiled_heir": (
                    "You invoke bloodline authority to unite fractured captains, fortifying Red Pass before the invasion column can deploy."
                ),
                "street_ghost": (
                    "You route civilians through hidden smuggler lanes, then blackmail both field commanders into a temporary withdrawal."
                ),
                "wandering_monk": (
                    "You hold the pass with restraint and discipline, creating safe corridors that prevent panic and retaliation."
                ),
                "nonlethal_path": (
                    "You evacuate every district and sabotage supply lines without executions, forcing both armies to disengage."
                ),
                "stealth_path": (
                    "You ghost through forward camps, collapsing siege stockpiles before enemy standards can reach the pass."
                ),
                "charm_path": (
                    "You broker a ceasefire chain between exhausted captains, reframing the pass as neutral ground."
                ),
                "evasion_path": (
                    "You keep your force mobile through rotating fallback lanes, draining the invasion's momentum."
                ),
                "kill_path": (
                    "You eliminate both spearhead commanders at dawn, ending the assault through shock and fear."
                ),
                "heroic_path": (
                    "Your public standing rallies villagers and scouts into a disciplined defense line that saves Red Pass."
                ),
                "rogue_path": (
                    "You sabotage payroll and rations, collapsing command loyalty and buying control of the battlefield."
                ),
                "default": "You stabilize Red Pass under pressure and deny the invasion its first decisive breach.",
            },
        },
        {
            "quest_id": "Q17",
            "title": "The Broken Summoning Pact",
            "premise": "A rogue summon spirit turns on every faction at once.",
            "objective": "Rebind, negotiate release, or defeat the spirit before it levels border towns.",
            "choices": ("seal the spirit", "mediate pact terms", "weaponize the summon"),
            "follow_up_hook": "Pact records identify a prisoner tied to moonlit escape plans.",
            "reward_theme": "summon_affinity",
            "branch_outcomes": {
                "exiled_heir": (
                    "You restore the ancestral pact seals and command the spirit to stand down under bloodline law."
                ),
                "street_ghost": (
                    "You trace the spirit's handlers through contraband shrines, forcing a quiet pact rewrite in the undercity."
                ),
                "wandering_monk": (
                    "You negotiate a vow of mutual restraint, releasing the spirit from coercion without reigniting the war."
                ),
                "nonlethal_path": (
                    "You reseal the pact through synchronized stealth and diplomacy, ending the rampage with no fatalities."
                ),
                "stealth_path": (
                    "You infiltrate the summoning circle and sever anchor sigils before the spirit can crest again."
                ),
                "charm_path": (
                    "You redirect faction fear into a shared treaty, turning the spirit into a neutral witness."
                ),
                "evasion_path": (
                    "You bait the spirit through abandoned lanes until its surge burns out, then secure a safe rebinding."
                ),
                "kill_path": (
                    "You shatter the host and crush the spirit core, ending the threat at catastrophic cost."
                ),
                "heroic_path": (
                    "Your reputation convinces rival squads to coordinate, allowing a clean reseal before towns are lost."
                ),
                "rogue_path": (
                    "You auction pact secrets between factions and enforce compliance through fear of spirit reprisal."
                ),
                "default": "You contain the summon crisis and close the pact breach before border towns collapse.",
            },
        },
        {
            "quest_id": "Q18",
            "title": "Moonlit Prison Break",
            "premise": "A political prisoner holds proof that could rewrite alliances.",
            "objective": "Extract, exchange, or fake the prisoner's death without exposing your network.",
            "choices": ("silent extraction", "public exchange", "false execution"),
            "follow_up_hook": "Prison intel points to the origin of your first blade lineage.",
            "reward_theme": "spy_network",
            "branch_outcomes": {
                "exiled_heir": (
                    "You use forgotten clan codes to enter the prison unchallenged and extract the witness before dawn."
                ),
                "street_ghost": (
                    "You trigger a staged blackout through safehouse contacts and spirit the prisoner into ghost-held districts."
                ),
                "wandering_monk": (
                    "You secure a lawful prisoner exchange, preserving lives while exposing the forged charges."
                ),
                "nonlethal_path": (
                    "You complete the break through stealth diversions and social pressure, leaving every guard alive."
                ),
                "stealth_path": (
                    "You execute a silent extraction route that avoids alarms, patrol clashes, and traceable signatures."
                ),
                "charm_path": (
                    "You turn rival wardens into reluctant allies and walk the prisoner out under a negotiated transfer."
                ),
                "evasion_path": (
                    "You weave through decoy routes and pursuit traps until the prison dragnet collapses."
                ),
                "kill_path": (
                    "You stage a lethal revolt and disappear with the witness amid a brutal lockdown failure."
                ),
                "heroic_path": (
                    "Your standing wins public support, forcing the prison to honor an emergency legal release."
                ),
                "rogue_path": (
                    "You fake the prisoner's death records and sell silence to every official tied to the conspiracy."
                ),
                "default": "You pull off the prison operation and secure the witness without exposing your core network.",
            },
        },
        {
            "quest_id": "Q19",
            "title": "Echoes of the First Blade",
            "premise": "A backstory phantom duel determines your ideological legacy.",
            "objective": "Survive the ancestral duel and claim or reject its doctrine.",
            "choices": ("accept legacy", "break the doctrine", "share the doctrine"),
            "follow_up_hook": "The duel's verdict sets terms for the Shattered Gate siege.",
            "reward_theme": "signature_technique",
            "branch_outcomes": {
                "exiled_heir": (
                    "You claim the first blade doctrine as rightful heir, binding legacy and command into one mandate."
                ),
                "street_ghost": (
                    "You reinterpret the duel through street code, turning elite doctrine into tools for the forgotten."
                ),
                "wandering_monk": (
                    "You refuse domination and recast the doctrine as restraint, ending the duel without vengeance."
                ),
                "nonlethal_path": (
                    "You complete the ancestral trial without killing intent, proving doctrine can survive without blood tribute."
                ),
                "stealth_path": (
                    "You win by reading feints and silence, ending the phantom duel before a decisive strike lands."
                ),
                "charm_path": (
                    "You sway witnesses and elders mid-trial, transforming the duel into a negotiated doctrinal accord."
                ),
                "evasion_path": (
                    "You outlast every decisive exchange, forcing the phantom legacy to concede through exhaustion."
                ),
                "kill_path": (
                    "You sever the phantom doctrine in a final execution stroke and claim power through fear."
                ),
                "heroic_path": (
                    "Your honorable conduct turns the duel into a unifying legend that steadies the region before siege."
                ),
                "rogue_path": (
                    "You weaponize the doctrine as leverage, selling allegiance oaths to the highest bidder."
                ),
                "default": "You survive the ancestral duel and carry its verdict into the coming siege.",
            },
        },
        {
            "quest_id": "Q20",
            "title": "Dawn at Shattered Gate",
            "premise": "A siege at Shattered Gate decides who commands the next era.",
            "objective": "Lead defense, trigger a breach, or broker ceasefire before total collapse.",
            "choices": ("defend the gate", "open the gate", "mediate ceasefire"),
            "follow_up_hook": "War aftermath fractures faction trust and starts internal schisms.",
            "reward_theme": "arc_transition",
            "branch_outcomes": {
                "exiled_heir": (
                    "You rally bloodline loyalists to hold the inner wall, establishing lawful command as dawn breaks."
                ),
                "street_ghost": (
                    "You coordinate safehouses and tunnel scouts, then break the siege from inside the supply grid."
                ),
                "wandering_monk": (
                    "You prevent massacre at the gate, forcing both armies into a truce framed by restraint."
                ),
                "nonlethal_path": (
                    "You dismantle the siege through stealth, charm, and evasion, preserving the gate without executions."
                ),
                "stealth_path": (
                    "You center Dawn at Shattered Gate on stealth-first tactics, cutting siege command lines before open war erupts."
                ),
                "charm_path": (
                    "You convert rival captains into a ceasefire coalition and redirect the conflict into negotiated reconstruction."
                ),
                "evasion_path": (
                    "You rotate units through evasive choke-point play, burning out the siege with minimal casualties."
                ),
                "kill_path": (
                    "You drive Dawn at Shattered Gate to a brutal conclusion, eliminating siege leadership in a single strike chain."
                ),
                "heroic_path": (
                    "Your heroic standing unites civilians, allies, and defenders into the first guardian line of the new era."
                ),
                "rogue_path": (
                    "You seize the gate's black ledgers and force every faction to bargain under your shadow rule."
                ),
                "default": "You break the siege at Shattered Gate and decide the opening terms of the next era.",
            },
        },
        {
            "quest_id": "Q21",
            "title": "Beneath the Shrine Bell",
            "premise": "Shrine custodians accuse both armies of desecration to spark holy retaliation.",
            "objective": "Find the true instigator and decide whether to expose or leverage them.",
            "choices": ("protect shrine neutrals", "publish proof", "coerce confessions"),
            "follow_up_hook": "Recovered tokens reveal a coordinated courier sabotage ring.",
            "reward_theme": "spiritual_favor",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your clan holds old patronage records for the shrine; you produce them "
                    "to establish yourself as protector and force the true instigator out of hiding."
                ),
                "street_ghost": (
                    "Your underworld courier contacts expose the false-flag trail and help you "
                    "keep sacred spaces outside faction revenge cycles before either army retaliates."
                ),
                "wandering_monk": (
                    "You interview each custodian in mediation, separating coerced testimony "
                    "from genuine witness until the true instigator's role is undeniable."
                ),
                "nonlethal_path": (
                    "You protect the shrine through silent vigil, neutralizing provocateurs "
                    "without violence until the truth can be presented to both armies."
                ),
                "heroic_path": (
                    "Village elders rally to your credibility; their joint statement "
                    "redirects both armies' outrage toward the actual instigator."
                ),
                "rogue_path": (
                    "You obtain the instigator's confession through private leverage "
                    "and hold it as a deterrent that keeps both armies off the shrine indefinitely."
                ),
                "default": (
                    "You confront the instigator directly, extract their confession by force, "
                    "and present it to both armies before holy retaliation can ignite."
                ),
            },
        },
        {
            "quest_id": "Q22",
            "title": "Paper Wings, Iron Chains",
            "premise": "Intercepted messenger birds isolate allied villages.",
            "objective": "Restore secure communication and determine who controls the cipher routes.",
            "choices": ("restore old ciphers", "create new network", "trap interceptors"),
            "follow_up_hook": "Cipher metadata exposes the Fifth Mask syndicate.",
            "reward_theme": "intel_speed",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your clan's old cipher registry is still valid; you reactivate it under "
                    "your seal, restoring message flow and locking interceptors out of the network."
                ),
                "street_ghost": (
                    "You reroute the messenger network through safehouse relays your contacts "
                    "already control, bypassing every interception point overnight."
                ),
                "wandering_monk": (
                    "You visit each isolated village personally, carrying messages by hand "
                    "until a new trusted courier network takes shape from community volunteers."
                ),
                "nonlethal_path": (
                    "You identify interception nests through stealth and dismantle them without "
                    "engagement, restoring message flow while leaving no trail of confrontation."
                ),
                "heroic_path": (
                    "Your reputation draws loyal couriers out of retirement; "
                    "their expertise reestablishes a clean cipher network within hours."
                ),
                "rogue_path": (
                    "You capture the interceptor ring's codebook and use it to flood their "
                    "network with false traffic, blinding them while real messages pass freely."
                ),
                "default": (
                    "You hunt down the interception cells, neutralize each post, "
                    "and rebuild the courier routes by force before the villages starve of news."
                ),
            },
        },
        {
            "quest_id": "Q23",
            "title": "The Fifth Mask",
            "premise": "A hidden masked leader manipulates every side of the conflict.",
            "objective": "Unmask, recruit, or publicly ruin the Fifth Mask.",
            "choices": ("recruit quietly", "public reveal", "erase all records"),
            "follow_up_hook": "Mask safehouses map directly to sabotaged farmlands.",
            "reward_theme": "covert_control",
            "branch_outcomes": {
                "exiled_heir": (
                    "Old lineage records name a bloodline tie to the Mask's identity; "
                    "you use this leverage to force a private unmasking and binding arrangement."
                ),
                "street_ghost": (
                    "You trace the Mask's handler network through underground dead drops "
                    "and surface the real identity before their next move reaches any faction."
                ),
                "wandering_monk": (
                    "You approach the Mask directly as a mediator, offering neutrality "
                    "as the one thing their manipulation network cannot buy or fake."
                ),
                "nonlethal_path": (
                    "You dismantle the Mask's courier infrastructure through stealth alone, "
                    "isolating them from every faction until they have no play left but surrender."
                ),
                "heroic_path": (
                    "Your public credibility forces the Mask's allied contacts to distance "
                    "themselves; stripped of support, their identity becomes an open secret."
                ),
                "rogue_path": (
                    "You acquire the Mask's true identity through a double agent and "
                    "hold it as permanent leverage, turning a rival into a reluctant asset."
                ),
                "default": (
                    "You run every lead to ground, confront the Mask at their inner sanctum, "
                    "and end their influence through a direct and public unmasking."
                ),
            },
        },
        {
            "quest_id": "Q24",
            "title": "Salt in the Ricefields",
            "premise": "Systematic crop sabotage threatens famine and uprising.",
            "objective": "Stop field poisoning and choose civilian relief or military stockpiles.",
            "choices": ("prioritize civilians", "secure war reserves", "split aid lines"),
            "follow_up_hook": "Supply caravan routes become immediate high-value targets.",
            "reward_theme": "civilian_trust",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan harvest records identify the poisoned plots exactly; "
                    "you direct emergency relief grain from ancestral stores before famine spreads."
                ),
                "street_ghost": (
                    "You trace the sabotage supply chain to a hidden depot and intercept "
                    "the next poison shipment before it reaches a single field."
                ),
                "wandering_monk": (
                    "You organize village cooperatives to share uncontaminated stores, "
                    "building a civilian relief chain that outlasts the immediate crisis."
                ),
                "nonlethal_path": (
                    "You capture the sabotage crews through stealth and turn them over "
                    "to village elders for restitution work instead of execution."
                ),
                "heroic_path": (
                    "Your reputation mobilizes regional merchants to donate emergency grain; "
                    "the relief effort outpaces the sabotage before full famine sets in."
                ),
                "rogue_path": (
                    "You seize the sponsor's private reserves through covert means "
                    "and redirect them to the villages, making the saboteur fund the recovery."
                ),
                "default": (
                    "You root out the sabotage cells by force, destroy their supply cache, "
                    "and commandeer military rations for civilian distribution."
                ),
            },
        },
        {
            "quest_id": "Q25",
            "title": "Wolves at Noon",
            "premise": "Neutral caravans are attacked to force economic allegiance.",
            "objective": "Protect, raid, or redirect caravans to reshape the war economy.",
            "choices": ("escort caravans", "tax and redirect goods", "stage false raids"),
            "follow_up_hook": "Captured manifests contain forged Kage directives.",
            "reward_theme": "resource_pipeline",
            "branch_outcomes": {
                "exiled_heir": (
                    "Ancestral trade-route charters give you legal escort authority; "
                    "you march with the caravans under clan flag and attackers stand aside."
                ),
                "street_ghost": (
                    "You reroute the caravans through smuggler byways known only to your "
                    "contacts, delivering goods without ever crossing an attacker's field of view."
                ),
                "wandering_monk": (
                    "You broker a caravan neutrality agreement between faction captains, "
                    "establishing safe passage without requiring a single armed escort."
                ),
                "nonlethal_path": (
                    "You shadow the caravans in silence, neutralizing ambush scouts "
                    "before they can signal their main force, leaving the route quietly clean."
                ),
                "heroic_path": (
                    "Caravan merchants openly request your escort after your reputation "
                    "reaches them; attackers pull back rather than face your known record."
                ),
                "rogue_path": (
                    "You sell faction commanders advance caravan manifests in exchange "
                    "for non-aggression, turning extortion into structured protection fees."
                ),
                "default": (
                    "You intercept the raiding parties head-on, scatter their formations, "
                    "and secure the caravan routes through direct elimination of the threat."
                ),
            },
        },
        {
            "quest_id": "Q26",
            "title": "Threads of the Kage Cloak",
            "premise": "Forged executive orders are tearing command ranks apart.",
            "objective": "Prove authenticity or exploit the confusion to force leadership change.",
            "choices": ("validate chain of command", "install proxy leadership", "collapse both hierarchies"),
            "follow_up_hook": "Competing leaders hide evidence in poisoned waterways.",
            "reward_theme": "command_authority",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your bloodline archives hold the original command seals; "
                    "you authenticate legitimate orders and invalidate the forgeries on the spot."
                ),
                "street_ghost": (
                    "You trace the forged orders to a single scribe handler through "
                    "dead-drop analysis and expose the entire fabrication chain quietly."
                ),
                "wandering_monk": (
                    "You convene a neutral review panel and guide each commander through "
                    "evidence reconciliation until a clear chain of command emerges peacefully."
                ),
                "nonlethal_path": (
                    "You distribute authenticated counter-orders through stealth courier runs, "
                    "dissolving the confusion without confronting a single ranking officer."
                ),
                "heroic_path": (
                    "Commanders trust your judgment enough to suspend the contested orders "
                    "pending your verification; your credibility stabilizes the rank structure."
                ),
                "rogue_path": (
                    "You plant evidence that implicates a rival faction in the forgery "
                    "and use the resulting purge to install a command structure you control."
                ),
                "default": (
                    "You confront the forgery source directly, seize their operation, "
                    "and broadcast authenticated orders to every command post by force."
                ),
            },
        },
        {
            "quest_id": "Q27",
            "title": "When the River Runs Black",
            "premise": "Toxic river sabotage threatens every village downstream.",
            "objective": "Trace the source and choose transparent justice or strategic secrecy.",
            "choices": ("public trial", "quiet purge", "controlled cover-up"),
            "follow_up_hook": "Witnesses flee to an abandoned dojo linked to disappearances.",
            "reward_theme": "medical_network",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan water-rights records let you identify the contamination source legally; "
                    "you bring it before a formal tribunal backed by ancestral authority."
                ),
                "street_ghost": (
                    "You trace the toxin supply chain through underground broker records "
                    "and neutralize the source before downstream villages can be alerted."
                ),
                "wandering_monk": (
                    "You mobilize village healers to build a treatment network while you "
                    "trace and peacefully dismantle the sabotage operation at its origin."
                ),
                "nonlethal_path": (
                    "You dismantle the toxin distribution network through stealth infiltration, "
                    "removing every operative without a single public confrontation."
                ),
                "heroic_path": (
                    "Your standing draws witnesses forward who fear reprisal; "
                    "their combined testimony breaks the cover-up and forces a public trial."
                ),
                "rogue_path": (
                    "You gather enough evidence to hold the perpetrators in permanent leverage, "
                    "using their guilt to fund village water restoration as quiet restitution."
                ),
                "default": (
                    "You raid the contamination source directly, destroy the toxin stores, "
                    "and haul the operators before a public tribunal without delay."
                ),
            },
        },
        {
            "quest_id": "Q28",
            "title": "The Empty Dojo",
            "premise": "A legendary dojo is empty after a forced conscription experiment.",
            "objective": "Recover the missing students and choose reform, retaliation, or secrecy.",
            "choices": ("free students", "weaponize training logs", "bury the scandal"),
            "follow_up_hook": "Recovered logs expose a summit ambush timetable.",
            "reward_theme": "advanced_training",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan patronage records bind the dojo to your lineage; "
                    "you invoke that obligation to demand the students' release through legal channels."
                ),
                "street_ghost": (
                    "You locate the conscription facility through safehouse informants "
                    "and arrange a quiet transfer that leaves the operation's sponsors unaware."
                ),
                "wandering_monk": (
                    "You enter the facility as a neutral mediator and negotiate student "
                    "release terms that avoid retaliation while ensuring their safe return."
                ),
                "nonlethal_path": (
                    "You infiltrate the conscription camp through stealth, freeing students "
                    "in small groups over successive nights without triggering a single alarm."
                ),
                "heroic_path": (
                    "Your reputation draws former dojo alumni who corroborate the scandal; "
                    "their public testimony forces an official release and reform."
                ),
                "rogue_path": (
                    "You acquire the training logs and hold them as leverage, trading "
                    "student release for permanent silence from the program's sponsors."
                ),
                "default": (
                    "You assault the conscription facility directly, extract the students "
                    "by force, and expose the program in full to every allied faction."
                ),
            },
        },
        {
            "quest_id": "Q29",
            "title": "Storm over Ironwood",
            "premise": "A final summit is interrupted by synchronized ambush teams.",
            "objective": "Save delegates, secure records, and choose who speaks for peace.",
            "choices": ("save delegates", "secure evidence first", "eliminate ambushers"),
            "follow_up_hook": "Summit survivors call for a total banner war.",
            "reward_theme": "faction_alignment",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your bloodline standing gives you summit authority; "
                    "you organize a rapid extraction under clan protection that ambushers cannot legally override."
                ),
                "street_ghost": (
                    "You had the summit mapped in advance through informants; "
                    "you move delegates through pre-planned escape corridors before the ambush can converge."
                ),
                "wandering_monk": (
                    "You position yourself between the ambushers and the delegates, "
                    "using body language and restraint doctrine to buy time for a full evacuation."
                ),
                "nonlethal_path": (
                    "You disable ambush team signals through stealth, preventing coordination "
                    "between squads and extracting every delegate before the attack consolidates."
                ),
                "heroic_path": (
                    "Summit guards rally around your presence; their coordinated response "
                    "shields every delegate long enough for a full safe extraction."
                ),
                "rogue_path": (
                    "You had ambush commanders pre-compromised through prior leverage; "
                    "a single coded signal freezes their teams while delegates escape."
                ),
                "default": (
                    "You fight through the ambush perimeter, clear the delegate extraction "
                    "route by force, and secure every record before the summit hall falls."
                ),
            },
        },
        {
            "quest_id": "Q30",
            "title": "Last Light of the Five Banners",
            "premise": "Five alliances collapse into one final campaign for dominance.",
            "objective": "End the campaign through unity, domination, or shadow governance.",
            "choices": ("forge unity", "enforce rule", "rule from shadows"),
            "follow_up_hook": "Emergency succession powers activate after the banner collapse.",
            "reward_theme": "ending_lock",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your bloodline is the last recognized common ground between the five banners; "
                    "you convene a final summit under hereditary mandate and lock in a unity accord."
                ),
                "street_ghost": (
                    "You hold intelligence on every banner's hidden failures; "
                    "the threat of mutual exposure forces all five into a negotiated collapse and reformation."
                ),
                "wandering_monk": (
                    "You refuse to name a winner; instead you draft a restraint covenant "
                    "that all five banners sign before their forces run out of ground to fight over."
                ),
                "nonlethal_path": (
                    "You end each banner's campaign capacity through targeted stealth and "
                    "charm without a final battle, leaving governance to whoever survives sober."
                ),
                "heroic_path": (
                    "Your heroic record inspires a cross-banner ceasefire movement; "
                    "the five banners dissolve into a single peacekeeping authority under your witness."
                ),
                "rogue_path": (
                    "You play each banner against the others until only one remains standing, "
                    "then install your preferred governance structure in the resulting vacuum."
                ),
                "default": (
                    "You drive the decisive campaign yourself, breaking the last resistant "
                    "banner and declaring the new order from the ruins of the old five."
                ),
            },
        },
        {
            "quest_id": "Q31",
            "title": "Ash Crown Protocol",
            "premise": "Emergency war succession powers trigger a contested regency.",
            "objective": "Support, restrain, or remove the temporary sovereign.",
            "choices": ("stabilize rule", "limit powers", "topple regency"),
            "follow_up_hook": "Regency decrees expose chakra ore seizure operations.",
            "reward_theme": "regime_control",
            "branch_outcomes": {
                "exiled_heir": (
                    "Succession law is your lineage's specialty; you insert legitimacy clauses "
                    "into the regency charter that automatically expire its emergency powers."
                ),
                "street_ghost": (
                    "You surface the regent's financial backers through covert investigation, "
                    "exposing the power play and forcing a negotiated limits agreement."
                ),
                "wandering_monk": (
                    "You mediate between the regent and opposition councils, drafting a "
                    "power-sharing protocol that prevents emergency rule from becoming permanent."
                ),
                "nonlethal_path": (
                    "You neutralize the regent's enforcement apparatus through stealth, "
                    "leaving them with nominal authority but no means to exercise it abusively."
                ),
                "heroic_path": (
                    "Your public credibility anchors a coalition that demands constitutional "
                    "limits; the regent accepts rather than face a legitimacy crisis."
                ),
                "rogue_path": (
                    "You compromise the regent's inner circle and redirect their loyalty, "
                    "turning emergency powers into tools that serve your agenda instead."
                ),
                "default": (
                    "You confront the regent's overreach directly, dismantle their enforcement "
                    "apparatus, and force a transition of power through decisive pressure."
                ),
            },
        },
        {
            "quest_id": "Q32",
            "title": "Veins of the Mountain",
            "premise": "Chakra ore mines become the new center of wartime leverage.",
            "objective": "Retake mines, negotiate labor terms, or destroy extraction sites.",
            "choices": ("retake by force", "broker labor pact", "cripple extraction"),
            "follow_up_hook": "Mine ledgers reveal identity theft operations on clan archives.",
            "reward_theme": "crafting_scale",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your clan's original mining charter is still filed in the central archive; "
                    "you invoke it to reclaim ownership and eject wartime occupiers without combat."
                ),
                "street_ghost": (
                    "You trace the ore distribution network to its black-market terminus "
                    "and cut it off, making occupation economically worthless overnight."
                ),
                "wandering_monk": (
                    "You negotiate directly with the workers, separating coerced laborers "
                    "from occupying factions and brokering exit terms that empty the mines peacefully."
                ),
                "nonlethal_path": (
                    "You disable the extraction equipment through stealth and redirect "
                    "ore shipments, rendering the occupation unprofitable without a single fight."
                ),
                "heroic_path": (
                    "Mine workers rally to your banner, refusing to continue labor under "
                    "occupation; their strike collapses the extraction operation from within."
                ),
                "rogue_path": (
                    "You forge transfer papers and divert ore shipments to your own "
                    "channels, making the occupation fund your operations while you plan the eviction."
                ),
                "default": (
                    "You assault the main extraction hub, drive out the occupying force, "
                    "and secure the mine under your direct authority."
                ),
            },
        },
        {
            "quest_id": "Q33",
            "title": "The Thief of Names",
            "premise": "Clan identity records are stolen to weaponize bloodlines.",
            "objective": "Recover records and decide who controls lineage truth.",
            "choices": ("restore full archives", "privatize key records", "burn bloodline lists"),
            "follow_up_hook": "Recovered aliases connect to frozen signal tower failures.",
            "reward_theme": "clan_loyalty",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your bloodline is the primary target in the stolen records; "
                    "you trace the theft personally and recover every document by ancestral right."
                ),
                "street_ghost": (
                    "You track the stolen records through underground information brokers "
                    "and retrieve them before any faction can weaponize the lineage data."
                ),
                "wandering_monk": (
                    "You work with every affected clan to restore records through community "
                    "witness and oral registry, removing the thief's leverage entirely."
                ),
                "nonlethal_path": (
                    "You infiltrate the thief's holding vault through stealth, recovering "
                    "every stolen document without alerting the faction that commissioned the theft."
                ),
                "heroic_path": (
                    "Affected clans trust your stewardship; they grant you joint custody "
                    "of the recovered records with a mandate to return each document to its rightful family."
                ),
                "rogue_path": (
                    "You recover the records and hold the most sensitive lineage data in "
                    "private leverage, ensuring no faction can use bloodlines against you."
                ),
                "default": (
                    "You hunt the thief to their safehouse, seize the stolen archive, "
                    "and settle the lineage dispute on your terms by force."
                ),
            },
        },
        {
            "quest_id": "Q34",
            "title": "Frost on the Signal Fires",
            "premise": "Warning towers go dark during coordinated winter raids.",
            "objective": "Relight the defense chain and handle the traitor behind the outage.",
            "choices": ("publicly expose traitor", "flip traitor as double-agent", "silent execution"),
            "follow_up_hook": "Traitor dispatches mention toxin vials in envoy circles.",
            "reward_theme": "early_warning",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan tower contracts name your lineage as the legitimate repair authority; "
                    "you restore the defense chain under that mandate and expose the traitor legally."
                ),
                "street_ghost": (
                    "You reroute the signal chain through safehouse relay mirrors before "
                    "the traitor realizes the towers are already back online."
                ),
                "wandering_monk": (
                    "You give the traitor a path to confession and restitution, "
                    "relighting towers with their cooperation and sparing further bloodshed."
                ),
                "nonlethal_path": (
                    "You restore each tower under cover of night and shadow the traitor "
                    "back to their handlers, mapping the full network without a confrontation."
                ),
                "heroic_path": (
                    "Your reputation draws volunteers to relight every tower in a single "
                    "coordinated night; the traitor is exposed by the morning audit."
                ),
                "rogue_path": (
                    "You flip the traitor into a double-agent through leverage before dawn, "
                    "turning their handler network into a live intelligence feed."
                ),
                "default": (
                    "You relight the towers yourself under fire, neutralize the traitor "
                    "directly, and restore the defense chain before the raids consolidate."
                ),
            },
        },
        {
            "quest_id": "Q35",
            "title": "Three Cups of Poison",
            "premise": "Envoys are dosed to collapse fragile diplomacy.",
            "objective": "Find antidote supply and identify who profits from delayed deaths.",
            "choices": ("distribute antidotes", "control antidote access", "booby-trap toxin stocks"),
            "follow_up_hook": "Antidote brokers carry references to a forbidden oath ledger.",
            "reward_theme": "toxin_resistance",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your clan's herbalist lineage knows this compound; you compound the "
                    "antidote from archive recipes and distribute it to envoys through official channels."
                ),
                "street_ghost": (
                    "You trace the toxin broker through underground apothecary records "
                    "and intercept the next delivery, reversing the poison pipeline entirely."
                ),
                "wandering_monk": (
                    "You treat the dosed envoys personally using field medicine and convince "
                    "all parties to pause diplomacy until a clean environment can be secured."
                ),
                "nonlethal_path": (
                    "You locate the antidote cache through stealth reconnaissance and "
                    "distribute it quietly, stabilizing every envoy without exposing your method."
                ),
                "heroic_path": (
                    "Your credibility reassures the envoys that they will be protected; "
                    "their trust gives you authority to audit every cup before negotiation resumes."
                ),
                "rogue_path": (
                    "You acquire both the toxin and antidote supplies and use control of "
                    "both to dictate the terms under which diplomacy can safely continue."
                ),
                "default": (
                    "You raid the poisoner's operation, secure the antidote stores, "
                    "and force their handlers into the open before the next round of talks."
                ),
            },
        },
        {
            "quest_id": "Q36",
            "title": "The Ninth Oath",
            "premise": "An obsolete oath forces a mission that could restart war.",
            "objective": "Honor, rewrite, or break the oath with lasting legitimacy.",
            "choices": ("honor oath", "rewrite oath terms", "break and replace oath"),
            "follow_up_hook": "Oath chambers reveal coordinates for the Bone Orchard.",
            "reward_theme": "legacy_authority",
            "branch_outcomes": {
                "exiled_heir": (
                    "The oath was sworn by your bloodline; only your authority can legally "
                    "rewrite its terms, which you do before the assembled oath-witnesses."
                ),
                "street_ghost": (
                    "You surface the oath's hidden codicils through archival investigation, "
                    "finding a clause that lets you void its mission requirement without war."
                ),
                "wandering_monk": (
                    "You convene the oath's original witness clans and guide them through "
                    "a shared reinterpretation that preserves honor while preventing war."
                ),
                "nonlethal_path": (
                    "You complete the oath's mission requirement through stealth and "
                    "misdirection, satisfying its terms without any of the combat it implies."
                ),
                "heroic_path": (
                    "Your standing allows you to call a public hearing on the oath's "
                    "legitimacy; the assembled verdict grants a formal rewrite by consensus."
                ),
                "rogue_path": (
                    "You falsify completion of the oath's mission through forged evidence "
                    "and retire the obligation without ever triggering the dangerous clause."
                ),
                "default": (
                    "You execute the oath's mission by force, fulfill every term to the "
                    "letter, and then formally dissolve it before any faction can invoke it again."
                ),
            },
        },
        {
            "quest_id": "Q37",
            "title": "Bone Orchard",
            "premise": "A grave site begins producing hostile summoned remnants.",
            "objective": "Purify, bind, or weaponize the Orchard before factions claim it.",
            "choices": ("purify shrine", "bind remnants", "weaponize remnants"),
            "follow_up_hook": "Recovered relic shards point to a forged treaty draft.",
            "reward_theme": "summon_depth",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your clan holds burial rites for this Orchard; the remnants "
                    "stand down at your ancestral command, letting you purify the site unopposed."
                ),
                "street_ghost": (
                    "You map the Orchard's remnant patrol patterns through remote "
                    "observation and navigate to the binding anchor without engaging a single spirit."
                ),
                "wandering_monk": (
                    "You perform a full purification rite unarmed, releasing each remnant "
                    "through ceremony rather than combat and restoring the Orchard to rest."
                ),
                "nonlethal_path": (
                    "You guide each remnant through its dissolution ritual through charm "
                    "and evasion alone, purifying the Orchard without raising a weapon."
                ),
                "heroic_path": (
                    "Shrine guardians who trust your record assist in a coordinated "
                    "multi-point purification that clears the Orchard in a single ceremony."
                ),
                "rogue_path": (
                    "You bind the remnants to a containment vessel and hold them as "
                    "a deterrent, keeping factions away from the Orchard through the threat of release."
                ),
                "default": (
                    "You fight through every remnant manifestation, destroy the Orchard's "
                    "anchoring relic, and leave nothing for any faction to weaponize."
                ),
            },
        },
        {
            "quest_id": "Q38",
            "title": "Ink of the Last Treaty",
            "premise": "A forged treaty is leaked to lock in false peace terms.",
            "objective": "Validate, replace, or manipulate the final treaty text.",
            "choices": ("publish authentic treaty", "forge better terms", "hold treaty hostage"),
            "follow_up_hook": "Treaty dispute collapses into simultaneous fort uprisings.",
            "reward_theme": "diplomatic_lock",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your lineage witnessed the original signing; you produce authenticated "
                    "records that invalidate the forgery and restore the legitimate treaty text."
                ),
                "street_ghost": (
                    "You obtain the forger's source materials through underground contacts "
                    "and replace the forgery with a version that serves your allies' interests."
                ),
                "wandering_monk": (
                    "You convene every treaty signatory for a joint authentication review, "
                    "exposing the forgery through transparent process rather than confrontation."
                ),
                "nonlethal_path": (
                    "You recover the authentic treaty text through stealth archive work "
                    "and circulate it quietly, letting the forgery collapse under comparison."
                ),
                "heroic_path": (
                    "Your credibility accelerates the authentication process; signatories "
                    "defer to your judgment and the forgery is formally voided within hours."
                ),
                "rogue_path": (
                    "You hold both versions of the treaty and negotiate the final text "
                    "privately, extracting concessions before releasing the authentic document."
                ),
                "default": (
                    "You expose the forger publicly, force a full treaty renegotiation, "
                    "and dictate the terms from a position of demonstrated factual authority."
                ),
            },
        },
        {
            "quest_id": "Q39",
            "title": "Night of Falling Banners",
            "premise": "Allied fortresses fail at once, forcing irreversible triage.",
            "objective": "Choose which fronts survive and absorb the political cost.",
            "choices": ("save civilians first", "save military core", "preserve archives first"),
            "follow_up_hook": "The final power vacuum opens the Quiet Steel succession.",
            "reward_theme": "ally_survival",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan defense protocols give you priority routing authority; "
                    "you direct evacuation and reinforcement exactly where legacy doctrine demands."
                ),
                "street_ghost": (
                    "Your pre-positioned contacts at each fortress give you real-time "
                    "status; you triage by actual survival odds rather than political optics."
                ),
                "wandering_monk": (
                    "You route every available resource to civilian extraction first, "
                    "accepting military losses as the cost of preserving non-combatant lives."
                ),
                "nonlethal_path": (
                    "You coordinate a full civilian-led evacuation through stealth corridors, "
                    "emptying each fortress before any banner formally falls."
                ),
                "heroic_path": (
                    "Your presence at the most critical fortress stabilizes its defenders "
                    "long enough to execute a full withdrawal before total collapse."
                ),
                "rogue_path": (
                    "You let the weakest fortresses fall strategically, consolidating "
                    "surviving forces and resources into a position of maximum post-collapse leverage."
                ),
                "default": (
                    "You triage by military necessity, committing every available asset "
                    "to the fortresses with the highest survival probability."
                ),
            },
        },
        {
            "quest_id": "Q40",
            "title": "Throne of Quiet Steel",
            "premise": "A final succession crisis decides long-term world order.",
            "objective": "Define rule by unity, dominance, or shadow balance.",
            "choices": ("federal unity model", "centralized rule", "hidden arbitration network"),
            "follow_up_hook": "Winter relief collapses under sabotage despite formal victory.",
            "reward_theme": "true_ending",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your bloodline is the last legitimate succession claim; "
                    "you convene the succession council and ratify a federal charter in your ancestral name."
                ),
                "street_ghost": (
                    "You hold leverage over every surviving power broker; "
                    "the new governance structure is negotiated from your hidden coordination center."
                ),
                "wandering_monk": (
                    "You draft a governance model that distributes authority among villages "
                    "rather than commanders, building a structure that outlasts any single leader."
                ),
                "nonlethal_path": (
                    "You reach the succession moment with no blood debt; "
                    "the council ratifies your governance model without opposition because no one fears your rule."
                ),
                "heroic_path": (
                    "Your heroic record earns unanimous succession council support; "
                    "the new governance structure is built around your proven values and alliances."
                ),
                "rogue_path": (
                    "You architect a hidden arbitration network that lets you guide world "
                    "governance from the shadows while a visible figurehead absorbs political risk."
                ),
                "default": (
                    "You claim the succession directly, settle every rival's challenge "
                    "by force, and establish world order on your own terms."
                ),
            },
        },
        {
            "quest_id": "Q41",
            "title": "Embers Under Snow",
            "premise": "A winter ceasefire is hiding targeted sabotage in relief camps.",
            "objective": "Uncover the saboteurs and protect relief lines without reigniting war.",
            "choices": ("defend camps", "trace saboteurs", "use ceasefire as trap"),
            "follow_up_hook": "Temple bells vanish from guarded sanctuaries overnight.",
            "reward_theme": "postwar_stability",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan winter-relief charters give you administrative access to every camp; "
                    "you identify saboteurs through official audits without breaking ceasefire terms."
                ),
                "street_ghost": (
                    "You shadow relief convoy routes through the snow and catch the "
                    "saboteur cells mid-operation, neutralizing them before any camp burns."
                ),
                "wandering_monk": (
                    "You integrate into relief work alongside camp volunteers, "
                    "identifying saboteurs through behavioral observation without force."
                ),
                "nonlethal_path": (
                    "You track and isolate each saboteur cell through stealth, removing "
                    "them from camps one by one without ceasefire-breaking confrontation."
                ),
                "heroic_path": (
                    "Camp residents trust you enough to report suspicious activity; "
                    "their civilian intelligence network surfaces every saboteur before damage occurs."
                ),
                "rogue_path": (
                    "You allow one sabotage attempt to proceed under observation, "
                    "gathering enough evidence to expose the entire operation's sponsors."
                ),
                "default": (
                    "You run active patrols through relief lines, confront saboteurs "
                    "directly, and secure every camp by force before the next strike window opens."
                ),
            },
        },
        {
            "quest_id": "Q42",
            "title": "The Sixth Bell",
            "premise": "A missing temple bell is used to mark assassination targets.",
            "objective": "Recover the bell and decode the hit-list ritual.",
            "choices": ("recover bell quietly", "publicly reveal list", "replace list with decoys"),
            "follow_up_hook": "Bell couriers connect to the Glass Sparrow network.",
            "reward_theme": "ritual_counterintel",
            "branch_outcomes": {
                "exiled_heir": (
                    "Temple custodians defer to your clan's patronage authority; "
                    "you obtain the bell's last known routing and recover it through official channels."
                ),
                "street_ghost": (
                    "You trace the bell's movements through underground courier logs "
                    "and intercept it at its last transfer point before the next toll is struck."
                ),
                "wandering_monk": (
                    "You visit each temple on the assassination routing pattern and "
                    "quietly remove the bell's ritual markers before any target is reached."
                ),
                "nonlethal_path": (
                    "You shadow the bell's courier network through stealth and recover "
                    "it without alerting the assassination ring that their ritual has been disrupted."
                ),
                "heroic_path": (
                    "Temple guards rally to your request and seal the bell's known "
                    "transfer routes; you recover it before the next ritual window opens."
                ),
                "rogue_path": (
                    "You decode the hit-list yourself and replace the real targets "
                    "with decoys, turning the assassination ring's own ritual against its sponsors."
                ),
                "default": (
                    "You track the bell to its handlers, seize it by force, and "
                    "break the assassination ritual chain before any target is struck."
                ),
            },
        },
        {
            "quest_id": "Q43",
            "title": "Glass Sparrow Network",
            "premise": "Children are coerced into courier duty for rival spymasters.",
            "objective": "Free the couriers and dismantle the handlers controlling them.",
            "choices": ("rescue and relocate", "flip handlers", "burn entire network"),
            "follow_up_hook": "Courier testimonies expose the Daimyo debt archive.",
            "reward_theme": "ethical_intel",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan child-protection edicts give you legal authority to remove the "
                    "couriers from handler custody and place them under your direct protection."
                ),
                "street_ghost": (
                    "Your network has safehouse capacity for every courier; "
                    "you extract them silently over three nights before any handler notices losses."
                ),
                "wandering_monk": (
                    "You approach the handlers as a mediator offering the couriers' "
                    "silence in exchange for their release, and every child is freed without exposure."
                ),
                "nonlethal_path": (
                    "You escort each courier to safety through stealth routes, "
                    "dismantling the network's operational capacity without confronting a single handler."
                ),
                "heroic_path": (
                    "Your reputation draws sympathetic officials who provide legal cover "
                    "for the extraction, making handler interference publicly untenable."
                ),
                "rogue_path": (
                    "You flip the senior handler through leverage and use their authority "
                    "to officially decommission the network from the inside."
                ),
                "default": (
                    "You raid the handler operation directly, free every courier, and "
                    "dismantle the network's infrastructure before it can reconstitute."
                ),
            },
        },
        {
            "quest_id": "Q44",
            "title": "Debt of the Daimyo",
            "premise": "A secret debt bankrolls opposing factions at once.",
            "objective": "Audit the debt ledger and choose repayment, exposure, or seizure.",
            "choices": ("forgive debt", "public exposure", "seize collateral"),
            "follow_up_hook": "Seized records prove staged atrocities under your banner.",
            "reward_theme": "macro_economy",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan treasury records corroborate the debt's origin; "
                    "you leverage that knowledge to force the Daimyo into a binding public settlement."
                ),
                "street_ghost": (
                    "You obtain the full ledger through underground financial contacts "
                    "and use its contents to broker a private resolution on your terms."
                ),
                "wandering_monk": (
                    "You propose a structured debt forgiveness program tied to "
                    "civilian reparations, turning a war-funding scheme into a peace dividend."
                ),
                "nonlethal_path": (
                    "You infiltrate the Daimyo's counting house through stealth and "
                    "copy the ledger, giving you leverage to negotiate a resolution without confrontation."
                ),
                "heroic_path": (
                    "You organize a public audit backed by community witnesses, "
                    "forcing the Daimyo to acknowledge the debt in front of every affected faction."
                ),
                "rogue_path": (
                    "You seize the debt collateral covertly and hold it until the "
                    "Daimyo meets your terms, extracting value from both sides of the crisis."
                ),
                "default": (
                    "You expose the full ledger publicly, seize available collateral by "
                    "force, and dictate debt resolution terms from a position of open power."
                ),
            },
        },
        {
            "quest_id": "Q45",
            "title": "The Hollow Banner",
            "premise": "Your faction banner is forged to justify civilian atrocities.",
            "objective": "Stop false-flag operations and decide how publicly to respond.",
            "choices": ("public tribunal", "secret retaliation", "counter-propaganda strike"),
            "follow_up_hook": "False-flag operators trade forbidden scrolls in a night market.",
            "reward_theme": "legitimacy_control",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your clan's symbolic ownership of the banner makes its forgery a "
                    "legal offense; you prosecute the operators under ancestral defamation law."
                ),
                "street_ghost": (
                    "You trace the forged banners back to their production site through "
                    "underground networks and destroy the operation before the next atrocity."
                ),
                "wandering_monk": (
                    "You document each false-flag incident personally and present the "
                    "evidence to village elders, restoring your banner's meaning through truth."
                ),
                "nonlethal_path": (
                    "You infiltrate the false-flag operations through stealth and "
                    "substitute counterfeit orders that redirect operatives away from civilians."
                ),
                "heroic_path": (
                    "Your public credibility makes the forgery transparently implausible; "
                    "civilian communities publicly reject the false-flag narrative on your behalf."
                ),
                "rogue_path": (
                    "You capture the false-flag operators and leverage their confessions "
                    "to discredit the faction behind the scheme rather than prosecuting publicly."
                ),
                "default": (
                    "You hunt the false-flag operators down, expose the entire scheme "
                    "in a public reckoning, and destroy every forged banner by force."
                ),
            },
        },
        {
            "quest_id": "Q46",
            "title": "Night Market of Teeth",
            "premise": "Forbidden technique auctions attract every surviving power broker.",
            "objective": "Disrupt, infiltrate, or dominate the auction economy.",
            "choices": ("destroy auction stock", "buy and seal scrolls", "control auction ring"),
            "follow_up_hook": "Auction maps reveal tampered borders with no true north.",
            "reward_theme": "forbidden_technique",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan interdiction authority over forbidden techniques gives you "
                    "legal standing to seize the auction stock and prosecute its brokers."
                ),
                "street_ghost": (
                    "You infiltrate the market as a buyer through false identity "
                    "and reroute every lot to sealed storage before the bidding closes."
                ),
                "wandering_monk": (
                    "You alert hidden temple observers to the auction's location "
                    "and coordinate a simultaneous multi-entry that neutralizes all bidders nonviolently."
                ),
                "nonlethal_path": (
                    "You disable the auction's security network through stealth "
                    "and scatter the power brokers through misdirection before the first lot opens."
                ),
                "heroic_path": (
                    "Your public standing draws enforcement allies who blockade the market "
                    "legally, forcing brokers to abandon the auction before it can proceed."
                ),
                "rogue_path": (
                    "You purchase the entire auction stock through proxies and "
                    "control the forbidden technique economy, deciding who gets access and at what cost."
                ),
                "default": (
                    "You raid the auction mid-session, neutralize every broker by force, "
                    "and destroy the forbidden stock before a single scroll changes hands."
                ),
            },
        },
        {
            "quest_id": "Q47",
            "title": "The Map with No North",
            "premise": "Border maps are altered to trigger legal territorial wars.",
            "objective": "Restore authoritative maps and settle claims before armies mobilize.",
            "choices": ("restore neutral maps", "redraw in your favor", "erase all claims"),
            "follow_up_hook": "Border casualties spark conflict at a fallen allies memorial.",
            "reward_theme": "territorial_stability",
            "branch_outcomes": {
                "exiled_heir": (
                    "Clan survey records predate every altered map; "
                    "you produce original boundary documentation that legally voids the altered versions."
                ),
                "street_ghost": (
                    "You trace the alteration campaign to its cartography ring "
                    "and replace every forged map with authenticated copies before mobilization orders are issued."
                ),
                "wandering_monk": (
                    "You convene boundary mediators from every affected region "
                    "and guide them to a joint settlement that all sides can formally accept."
                ),
                "nonlethal_path": (
                    "You recover every original map through stealth archive raids "
                    "and distribute authenticated copies before the first army crosses any disputed line."
                ),
                "heroic_path": (
                    "Your credibility as an impartial witness earns neutral nations' "
                    "endorsement of the authentic maps, making the alterations politically indefensible."
                ),
                "rogue_path": (
                    "You control the most strategically valuable border data and "
                    "negotiate settlement terms that incorporate your faction's territorial priorities."
                ),
                "default": (
                    "You seize the cartography ring, destroy every forged map, "
                    "and publish authenticated boundaries under armed escort before war begins."
                ),
            },
        },
        {
            "quest_id": "Q48",
            "title": "Ash Garden Requiem",
            "premise": "A memorial for fallen allies becomes a battlefield of memory and blame.",
            "objective": "Protect the memorial and resolve who controls historical narrative.",
            "choices": ("honor all fallen", "elevate one faction", "seal memorial archives"),
            "follow_up_hook": "Memorial archives reference an unnamed heir claimant.",
            "reward_theme": "legacy_memory",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your bloodline is inscribed in the memorial's founding charter; "
                    "you invoke that standing to declare the site neutral ground under your stewardship."
                ),
                "street_ghost": (
                    "You identify who is manipulating the memorial narrative through "
                    "underground channels and replace their planted records with verified history."
                ),
                "wandering_monk": (
                    "You host a multi-faction remembrance ceremony, giving each side "
                    "equal voice in the memorial's meaning and defusing the blame spiral."
                ),
                "nonlethal_path": (
                    "You stand vigil at the memorial through every challenge, "
                    "turning away agitators through presence and calm until the crisis passes."
                ),
                "heroic_path": (
                    "Your allies among the fallen's families trust your stewardship; "
                    "their public backing gives you authority to protect the memorial's integrity."
                ),
                "rogue_path": (
                    "You control the most historically sensitive memorial documents "
                    "and use that leverage to negotiate a narrative settlement that prevents exploitation."
                ),
                "default": (
                    "You defend the memorial by force, eject those who would weaponize "
                    "it, and declare its history as settled fact backed by your authority."
                ),
            },
        },
        {
            "quest_id": "Q49",
            "title": "The Unwritten Name",
            "premise": "A hidden heir emerges with evidence of legitimate succession.",
            "objective": "Confirm, deny, or co-rule with the new claimant.",
            "choices": ("endorse heir", "disprove claim", "form dual governance"),
            "follow_up_hook": "Final settlement council convenes for lasting peace terms.",
            "reward_theme": "succession_resolution",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your own succession records intersect with the claimant's evidence; "
                    "you authenticate their lineage and establish a joint governance framework."
                ),
                "street_ghost": (
                    "You investigate the heir's claim through archival contacts "
                    "and determine whether to authenticate or dismantle it based on verified facts."
                ),
                "wandering_monk": (
                    "You mediate between the heir and every opposing faction, "
                    "building a governance arrangement that earns broader legitimacy than either side alone."
                ),
                "nonlethal_path": (
                    "You validate the heir's claim through peaceful investigation "
                    "and stealth fact-finding, presenting a clean succession path with no blood attached."
                ),
                "heroic_path": (
                    "Your endorsement of the heir carries enough credibility to "
                    "override rival objections; the succession council ratifies the claim under your witness."
                ),
                "rogue_path": (
                    "You hold the decisive proof of the heir's legitimacy in private "
                    "and negotiate governance terms before releasing the authentication publicly."
                ),
                "default": (
                    "You confront the succession dispute head-on, present your evidence "
                    "before the full council, and force a binding resolution through direct authority."
                ),
            },
        },
        {
            "quest_id": "Q50",
            "title": "After the Last War Drum",
            "premise": "The final settlement determines justice, memory, and long-term peace.",
            "objective": "Define post-war governance and lock the world into your legacy framework.",
            "choices": ("restorative justice", "deterrence doctrine", "shadow equilibrium"),
            "follow_up_hook": "Legacy state enters replay-vault history for future ages.",
            "reward_theme": "new_game_plus",
            "branch_outcomes": {
                "exiled_heir": (
                    "Your bloodline covenant becomes the constitutional foundation of the "
                    "post-war settlement, binding every faction to a framework built on your ancestry."
                ),
                "street_ghost": (
                    "Your intelligence network survives the war intact; "
                    "you architect a shadow governance layer that keeps the peace through information control."
                ),
                "wandering_monk": (
                    "You draft a restorative justice framework built on restraint and "
                    "accountability, writing the world's next chapter without a single act of retribution."
                ),
                "nonlethal_path": (
                    "You reach the final settlement with every hand clean; "
                    "the world accepts your governance model because your path proved it was possible."
                ),
                "heroic_path": (
                    "Your heroic record anchors the settlement's legitimacy as you "
                    "finalize a postwar legacy framework that balances justice, deterrence, and stability "
                    "for every faction forced to measure itself against your example."
                ),
                "rogue_path": (
                    "You establish a hidden arbitration network that enforces the peace "
                    "from the shadows, ensuring stability without needing visible power."
                ),
                "default": (
                    "You impose your governance framework on the final settlement through "
                    "decisive authority, locking the post-war world into your legacy for generations."
                ),
            },
        },
    ]

    reward_cycle = (
        "intel",
        "allies",
        "techniques",
        "economy",
        "political_access",
        "status_mastery",
    )
    extended_quests: List[Quest] = []
    for index, spec in enumerate(specs, start=11):
        xp = 820 + (index - 10) * 55
        reward_focus = reward_cycle[(index - 11) % len(reward_cycle)]
        arc_tag = (
            "escalation" if index <= 20 else "faction_fracture" if index <= 30 else "regime_endgame"
        )
        if index > 40:
            arc_tag = "postwar_continuation"
        focus_outcomes = _build_remaining_seeded_branch_outcomes(spec)
        if focus_outcomes:
            # Q21-Q50: start with focus-generated outcomes for full tactical coverage,
            # then overlay per-quest hand-crafted text for keys where it is provided.
            branch_outcomes = {**focus_outcomes, **dict(spec.get("branch_outcomes", {}))}
        else:
            # Q11-Q20: hand-crafted per-quest entries take full priority; fall back to
            # the generic structured generator when no per-quest overrides are present.
            branch_outcomes = dict(spec.get("branch_outcomes", {})) or _build_structured_branch_outcomes(spec)
        extended_quests.append(
            Quest(
                quest_id=spec["quest_id"],
                title=spec["title"],
                premise=spec["premise"],
                objective=spec["objective"],
                stealth_required=any(
                    marker in " ".join(spec["choices"]).lower()
                    for marker in ("infiltrate", "silent", "quiet", "stealth")
                ),
                reward_xp=xp,
                choices=tuple(spec["choices"]),
                branch_outcomes=branch_outcomes,
                rewards={
                    "xp": xp,
                    "credits": QUEST_CREDIT_REWARD_BASE + (index * 2),
                    "theme": spec["reward_theme"],
                    "focus": reward_focus,
                    "arc": arc_tag,
                },
                follow_up_hook=spec["follow_up_hook"],
                villain_stance_impacts={"kill": 2, "stealth": -1, "charm": -2, "evasion": -1},
                reputation_impacts={"heroic": 6, "neutral": 2, "rogue": -6},
                trophy_hooks=_quest_trophy_hooks(index),
            )
        )
    return extended_quests


REMAINING_SEEDED_QUEST_BRANCH_FOCUS: Dict[str, str] = {
    "Q21": "neutralize the shrine false-flag and keep sacred spaces outside faction revenge cycles",
    "Q22": "rebuild trusted courier channels before isolated villages collapse into panic",
    "Q23": "turn the Fifth Mask network from chaos engine into controlled leverage",
    "Q24": "stop famine sabotage while deciding who receives first protection under scarcity",
    "Q25": "secure caravan lifelines and decide whether commerce stays free, taxed, or manipulated",
    "Q26": "restore or rewrite Kage command legitimacy during forged-order collapse",
    "Q27": "contain the poisoned river crisis without triggering retaliatory purges",
    "Q28": "recover conscripted students and choose whether truth becomes reform or buried scandal",
    "Q29": "stabilize the summit ambush aftermath before peace leadership fractures",
    "Q30": "end the five-banner war with enforceable authority and a durable power model",
    "Q31": "define the regency boundary between emergency stability and permanent tyranny",
    "Q32": "settle chakra ore control without turning labor unrest into another war front",
    "Q33": "protect bloodline identity records from weaponized lineage politics",
    "Q34": "restore winter signal defenses while deciding the traitor's political value",
    "Q35": "break envoy poison extortion and control antidote trust networks",
    "Q36": "resolve the Ninth Oath with legitimacy that can survive postwar scrutiny",
    "Q37": "contain the Bone Orchard before summoned remnants become faction weapons",
    "Q38": "lock treaty legitimacy before forged terms hard-code future conflict",
    "Q39": "triage collapsing fronts while preserving long-term governing credibility",
    "Q40": "seal final succession terms that can survive both idealism and opportunism",
    "Q41": "hold the winter ceasefire line while hunting relief-camp saboteurs",
    "Q42": "recover the Sixth Bell and break the ritual assassination signal chain",
    "Q43": "free coerced child couriers and dismantle handler incentives at the source",
    "Q44": "resolve Daimyo debt manipulation before finance reignites proxy war",
    "Q45": "end false-flag atrocities tied to your banner without legitimizing vengeance spirals",
    "Q46": "decide who controls forbidden jutsu circulation after the night market shock",
    "Q47": "restore border map authority before cartographic fraud becomes legal war",
    "Q48": "protect memorial truth so grief cannot be repurposed as recruitment fuel",
    "Q49": "settle the heir claim with enough legitimacy to prevent endless succession coups",
    "Q50": "finalize a postwar legacy framework that balances justice, deterrence, and stability",
}


def _build_remaining_seeded_branch_outcomes(spec: Dict[str, Any]) -> Dict[str, str]:
    quest_id = spec.get("quest_id", "")
    focus = REMAINING_SEEDED_QUEST_BRANCH_FOCUS.get(quest_id)
    if not focus:
        return {}

    title = spec["title"]
    objective = spec["objective"]
    return {
        "exiled_heir": (
            f"Your bloodline claim frames {title} as lawful intervention, letting you {focus} with formal mandate."
        ),
        "street_ghost": (
            f"Your underworld channels thread through {title}, helping you {focus} through covert influence."
        ),
        "wandering_monk": (
            f"You anchor {title} in restraint and service, allowing you to {focus} without feeding blood debt."
        ),
        "nonlethal_path": (
            f"You resolve {title} through stealth, charm, and evasion so you can {focus} without executions."
        ),
        "stealth_path": (
            f"You run {title} as a stealth-first operation and {focus} before open retaliation can form."
        ),
        "charm_path": (
            f"You use diplomacy and social leverage during {title} to {focus} through temporary coalition-building."
        ),
        "evasion_path": (
            f"You keep your force mobile during {title}, evading decisive clashes while you {focus}."
        ),
        "kill_path": (
            f"You push {title} into decisive eliminations to {focus} through shock and fear."
        ),
        "heroic_path": (
            f"Your heroic standing turns public trust into momentum during {title}, helping you {focus} in the open."
        ),
        "rogue_path": (
            f"Your rogue reputation weaponizes rumor and favors in {title}, forcing rivals to let you {focus}."
        ),
        "default": f"You execute the core objective directly: {objective}",
    }


def _build_structured_branch_outcomes(spec: Dict[str, Any]) -> Dict[str, str]:
    title = spec["title"]
    objective = spec["objective"]
    return {
        "exiled_heir": (
            f"Your clan authority reframes {title} as a lawful mandate, giving you sanctioned access before rivals mobilize."
        ),
        "street_ghost": (
            f"Your underworld network reroutes pressure points in {title}, letting you control outcomes through covert leverage."
        ),
        "wandering_monk": (
            f"You guide {title} toward restraint and service, stabilizing the objective without escalating blood debt."
        ),
        "nonlethal_path": (
            f"You complete {title} through stealth, charm, and evasion, proving the objective can be resolved without executions."
        ),
        "stealth_path": (
            f"You center {title} on stealth-first tactics, removing key obstacles before open conflict can form."
        ),
        "charm_path": (
            f"You resolve {title} by turning rivals into temporary allies and redirecting the conflict through diplomacy."
        ),
        "evasion_path": (
            f"You complete {title} through evasive maneuvers, exhausting enemies while preserving your force."
        ),
        "kill_path": (
            f"You drive {title} to a brutal conclusion, eliminating command targets to end resistance immediately."
        ),
        "heroic_path": (
            f"Your heroic standing unifies local support during {title}, turning public trust into operational momentum."
        ),
        "rogue_path": (
            f"Your rogue reputation weaponizes fear and favors in {title}, forcing compliance from hidden power brokers."
        ),
        "default": f"You execute the core objective directly: {objective}",
    }


def _quest_trophy_hooks(quest_number: int) -> Tuple[str, ...]:
    if quest_number <= 20:
        return (TROPHY_SILENT_LEGEND, TROPHY_TRINITY_OPERATOR)
    if quest_number <= 30:
        return (TROPHY_HARMONY_VOICE, TROPHY_UNTOUCHABLE_GHOST)
    if quest_number <= 40:
        return (TROPHY_HEROIC_CREST, TROPHY_ROGUE_ASCENDANT)
    return (TROPHY_MERCY_CROWN, TROPHY_QUESTMASTER)


def _build_generic_tactical_branch_outcomes(quest: Quest) -> Dict[str, str]:
    return {
        "stealth_path": (
            f"You complete {quest.title} through stealth-first positioning, bypassing the loudest resistance "
            "and securing the objective before alarms can spread."
        ),
        "charm_path": (
            f"You complete {quest.title} through negotiation, leverage, and disciplined restraint, turning "
            "open conflict into a controlled concession."
        ),
        "evasion_path": (
            f"You complete {quest.title} through misdirection and evasive movement, exhausting enemy responses "
            "until the objective is yours."
        ),
        "kill_path": (
            f"You complete {quest.title} by overwhelming the opposition in a decisive strike and forcing the "
            "field to submit."
        ),
    }


def _normalize_seeded_quest_metadata(quests: List[Quest]) -> None:
    required_branch_keys = ("exiled_heir", "street_ghost", "wandering_monk", "default")
    for idx, quest in enumerate(quests):
        region_name, city_hub, quest_giver = QUEST_LOCATION_ROTATION[idx % len(QUEST_LOCATION_ROTATION)]
        if quest.quest_id in STEALTH_GATED_QUEST_IDS:
            quest.stealth_required = True
        if not quest.premise:
            quest.premise = quest.objective
        if not quest.region_name:
            quest.region_name = region_name
        if not quest.city_hub:
            quest.city_hub = city_hub
        if not quest.quest_giver:
            quest.quest_giver = quest_giver
        if not quest.choices:
            quest.choices = (
                "stealth-forward approach",
                "direct confrontation",
                "negotiated resolution",
            )
        if not quest.rewards:
            quest.rewards = {
                "xp": quest.reward_xp,
                "credits": QUEST_CREDIT_REWARD_BASE + (idx * 2),
                "theme": "legacy_progression",
            }
        if not quest.follow_up_hook:
            next_quest_id = quests[idx + 1].quest_id if idx + 1 < len(quests) else "finale"
            quest.follow_up_hook = f"Completion of {quest.quest_id} points toward {next_quest_id}."
        if not quest.villain_stance_impacts:
            quest.villain_stance_impacts = {"kill": 2, "stealth": -1, "charm": -2, "evasion": -1}
        if not quest.reputation_impacts:
            quest.reputation_impacts = {"heroic": 5, "neutral": 1, "rogue": -5}
        if not quest.trophy_hooks:
            quest_number = int(quest.quest_id[1:]) if quest.quest_id[1:].isdigit() else 1
            quest.trophy_hooks = _quest_trophy_hooks(quest_number)
        if "default" not in quest.branch_outcomes:
            quest.branch_outcomes["default"] = quest.objective
        for branch_key in required_branch_keys:
            if branch_key not in quest.branch_outcomes:
                quest.branch_outcomes[branch_key] = quest.branch_outcomes["default"]
        for branch_key, outcome in _build_generic_tactical_branch_outcomes(quest).items():
            if branch_key not in quest.branch_outcomes:
                quest.branch_outcomes[branch_key] = outcome


def _seed_city_shops() -> List[CityShop]:
    return [
        CityShop(
            key="leafrise_threads",
            name="Leafrise Threads",
            region_name="Verdant Gate",
            city_name="Leafrise Village",
            specialty="cosmetics",
            description="A clothier focused on low-profile shinobi cosmetics and courier garb.",
            inventory_item_keys=("market_smoke_bomb", "pacifist_thread_charm"),
        ),
        CityShop(
            key="cinder_forge_exchange",
            name="Cinder Forge Exchange",
            region_name="Ashen Cradle",
            city_name="Cinder Port",
            specialty="ninja_tools",
            description="A heated port forge that stocks field tools and aggressive loadout pieces.",
            inventory_item_keys=("black_market_kunai", "gatebreaker_smoke_map"),
        ),
        CityShop(
            key="azure_current_boutique",
            name="Azure Current Boutique",
            region_name="Tideglass Basin",
            city_name="Azure Rest",
            specialty="cosmetics",
            description="A harbor boutique carrying peacekeeper cosmetics and water-route gear.",
            inventory_item_keys=("tideglass_truce_wire", "moonwell_ledger_cloak"),
        ),
        CityShop(
            key="crestfall_wind_market",
            name="Crestfall Wind Market",
            region_name="Stormwall Ridge",
            city_name="Crestfall Outpost",
            specialty="move_sets",
            description="An altitude market that trades traversal tools and advanced technique manuals.",
            inventory_item_keys=("wayfarer_anchor", "eternal_watch_decoy"),
        ),
        CityShop(
            key="dusk_refuge_supplies",
            name="Dusk Refuge Supplies",
            region_name="Sunken Hollow",
            city_name="Dusk Refuge",
            specialty="ninja_tools",
            description="A cave refuge cache supplying antidotes, stealth wraps, and survival kits.",
            inventory_item_keys=("smuggler_regent_wraps", "pacifist_thread_charm"),
        ),
    ]


def _seed_city_npcs() -> List[CityNPC]:
    return [
        CityNPC(
            name="Quartermaster Iori",
            region_name="Verdant Gate",
            city_name="Leafrise Village",
            role="quartermaster",
            disposition="alert",
            dialogue="Keep your profile low and your routes clean; Leafrise notices every loose thread.",
            services=("trade", "gather_intel"),
            pickpocket_difficulty=5,
            pickpocket_rewards=("supply chit",),
        ),
        CityNPC(
            name="Broker Sumi",
            region_name="Ashen Cradle",
            city_name="Cinder Port",
            role="contract broker",
            disposition="calculating",
            dialogue="In Cinder Port, everyone buys time first and loyalty second.",
            services=("trade", "gather_intel"),
            pickpocket_difficulty=7,
            pickpocket_rewards=("forged furnace stamp",),
        ),
        CityNPC(
            name="Archivist Nami",
            region_name="Tideglass Basin",
            city_name="Azure Rest",
            role="archive keeper",
            disposition="measured",
            dialogue="The basin remembers who rebuilt and who merely took cover behind the tides.",
            services=("gather_intel",),
            pickpocket_difficulty=6,
            pickpocket_rewards=("sealed tide ledger",),
        ),
        CityNPC(
            name="Scout Captain Rei",
            region_name="Stormwall Ridge",
            city_name="Crestfall Outpost",
            role="watch captain",
            disposition="disciplined",
            dialogue="Stormwall routes stay alive because someone reads the wind before the enemy does.",
            services=("trade", "gather_intel"),
            pickpocket_difficulty=8,
            pickpocket_rewards=("wind chart",),
        ),
        CityNPC(
            name="Tunnel Guide Mako",
            region_name="Sunken Hollow",
            city_name="Dusk Refuge",
            role="route guide",
            disposition="wary",
            dialogue="Down here, the wrong footstep costs more than coin, so make your moves count.",
            services=("trade", "gather_intel"),
            pickpocket_difficulty=7,
            pickpocket_rewards=("glowstone locator",),
        ),
    ]


def _seed_allies(min_count: int = DEFAULT_ALLY_MIN_COUNT) -> List[str]:
    """Return ally names with seeded characters plus curated fillers.

    The five core seeded allies are always included. ``min_count`` is the
    total minimum ally count (including those five core allies).
    ``AutoNinja-*`` placeholders are only used if counts exceed the curated
    name pool.
    """
    allies = ["Dan", "Moon", "Sleep", "Dot", "Porter"]
    filler_pool = [
        "Ren",
        "Kaida",
        "Shiro",
        "Emi",
        "Toma",
        "Riku",
        "Sora",
        "Kiko",
        "Hayate",
        "Mika",
    ]
    for name in filler_pool:
        if len(allies) >= min_count:
            return allies
        allies.append(name)

    index = 1
    while len(allies) < min_count:
        allies.append(f"AutoNinja-{index}")
        index += 1
    return allies


def _seed_player_backstories() -> List[Backstory]:
    return [
        Backstory(
            key="exiled_heir",
            title="Exiled Heir",
            narrative_tags=("clan_politics", "honor_bound"),
            reputation_bias=5,
        ),
        Backstory(
            key="street_ghost",
            title="Street Ghost",
            narrative_tags=("underworld", "infiltration"),
            reputation_bias=-5,
        ),
        Backstory(
            key="wandering_monk",
            title="Wandering Monk",
            narrative_tags=("pacifism", "discipline"),
            reputation_bias=10,
        ),
    ]


def _seed_villains() -> List[VillainProfile]:
    def _kit(*, attack: str, defense: str, escape: str, summon: str, link: str) -> Dict[str, str]:
        return {
            "attack_skin": attack,
            "defense_skin": defense,
            "escape_skin": escape,
            "summon_skin": summon,
            "link_skin": link,
        }

    return [
        VillainProfile(
            name="Kage Renda",
            backstory=(
                "Kage Renda served as the elite bodyguard of a Leafrise Council elder for twelve "
                "years, protecting a man he privately despised for his corruption. When a rival "
                "faction's assassin succeeded where Renda had always held the line — and Renda "
                "found himself relieved he had not stopped the blade — the Council read his grief "
                "as guilt and cast him out. Disgraced but not broken, he retreated to the "
                "Verdant Gate highlands and spent five years drilling wind-edge techniques in "
                "isolation, transforming his shame into surgical lethality. He returned not to "
                "reclaim his post, but to fill the power vacuum the council's collapse created — "
                "on his own terms. More than revenge, he wants political control over the region's "
                "next order so no council can discard him again."
            ),
            signature_power=_make_move(
                "Rending Spiral",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.2,
                TechniqueType.WEAPON_STYLE,
                (StatusEffectType.BLEED,),
            ),
            primary_affinity=Affinity.WIND,
            role="duelist",
            skinned_move_names=_kit(
                attack="Tempest Hook",
                defense="Cyclone Parry Ring",
                escape="Crosswind Fade",
                summon="Sky Hawk Pact",
                link="Shadow Nail Burst",
            ),
            ultimate_skin_name="Tempest Throne Collapse",
            power_origin=(
                "Rending Spiral was forged in exile: five years of drilling the same wind-angle "
                "cut against highland stone, each repetition channeling a different grievance until "
                "the blade and the wind became inseparable. What began as a swordsman's grief "
                "ritual became the most precise killing arc in the Verdant Gate region."
            ),
            arc_ties=("political_war",),
            player_backstory_hooks={
                "exiled_heir": (
                    "Renda recognizes the weight of unjust exile in the player's bearing. He "
                    "pauses mid-fight and says: 'You understand it too — being discarded by "
                    "the very system you served.' He will accept a formal duel challenge and "
                    "honor the outcome without reprisal."
                ),
                "street_ghost": (
                    "Renda has dealt with shadow-walkers before. He views the player's "
                    "underworld survival with cold respect: 'No titles, no ledgers — you "
                    "built your worth from nothing.' He tests strength before trust."
                ),
                "wandering_monk": (
                    "Renda finds pacifism philosophically naive but tactically respectable. "
                    "He will not attack a disarmed opponent. If the player approaches without "
                    "weapons drawn, he sheathes his blade and demands a conversation instead."
                ),
                "nonlethal_path": (
                    "If the player has taken no lives, Renda acknowledges the discipline "
                    "required. He offers a restraint pact: neither side will draw blood if "
                    "the player can prove their path is principle, not cowardice."
                ),
                "rogue_path": (
                    "Renda sees a dark mirror of himself in a rogue player. He warns: "
                    "'I walked that road. It leads nowhere worth arriving.' He fights harder "
                    "against rogues — trying to break them before the path does."
                ),
                "heroic_path": (
                    "Renda respects the heroic reputation but doesn't believe it lasts. "
                    "He calls the player's honor a loan against future compromise, and "
                    "tests it with morally ambiguous pre-fight demands."
                ),
            },
        ),
        VillainProfile(
            name="General Voln",
            backstory=(
                "Voln commanded the Border Ash Wars for nine seasons, winning through "
                "methodical attrition that his superiors praised and his soldiers survived "
                "in broken silence. When the peace treaty dismantled his army — and the "
                "nobles redistributed the veterans' pensions to fund court luxuries — Voln "
                "returned home to find his community gutted. He rebuilt. Not a nation, not "
                "an ideology — just an army loyal to payroll and survival. He now controls "
                "the Ashen Cradle through fire-forward pressure, hiring mercenaries and "
                "ex-soldiers the system abandoned, convinced that peace is only what the "
                "powerful call the period between their wars."
            ),
            signature_power=_make_move(
                "Ember Cyclone",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.25,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.BURN, StatusEffectType.STAGGER),
            ),
            primary_affinity=Affinity.FIRE,
            role="warlord",
            skinned_move_names=_kit(
                attack="Cinder Lance",
                defense="Ash Aegis",
                escape="Ember Veil Vault",
                summon="Ember Jackal Pact",
                link="Ash Fang Drive",
            ),
            ultimate_skin_name="Furnace Eclipse",
            aggression_score=1,
            power_origin=(
                "Ember Cyclone is the signature of Voln's assault doctrine — a rotating "
                "fire-vortex column he developed to flush defenders from fortified positions "
                "during the Border Ash Wars. He can call it down the way most soldiers call "
                "retreat: reflexively, without hesitation, because it has saved him more "
                "times than any shield."
            ),
            arc_ties=("fracture_front",),
            player_backstory_hooks={
                "exiled_heir": (
                    "Voln tests bloodline claimants with disdain: 'Heritage is just another "
                    "word for leverage.' He will attempt to bribe the player with military "
                    "resources if he senses the lineage claim could destabilize his rivals."
                ),
                "street_ghost": (
                    "Voln privately respects street-built operatives — they remind him of "
                    "his best soldiers. He offers to hire the player as an embedded spy "
                    "inside his own command, using the player to smoke out disloyal officers."
                ),
                "wandering_monk": (
                    "Voln scorns visible pacifism, but his veterans whisper he spent three "
                    "months in a fire temple before his first campaign. He will not admit "
                    "this. A monk player who mentions Cinder Temple by name will see him "
                    "pause just long enough to matter."
                ),
                "nonlethal_path": (
                    "Voln sees nonlethal tactics as logistics, not ethics. He respects "
                    "effective outcomes regardless of method, but warns: 'Every enemy you "
                    "spare is a variable you cannot control.'"
                ),
                "rogue_path": (
                    "Voln offers a direct alliance to rogue players. His mercenary network "
                    "needs skilled operators who don't ask about cargo manifests. The deal "
                    "is genuine but includes a loyalty clause with lethal penalties."
                ),
                "heroic_path": (
                    "Voln views heroic reputation as a recruiting tool for the naive. He "
                    "attempts to publicly discredit the player before the confrontation, "
                    "manufacturing evidence of past atrocities to destabilize their alliances."
                ),
            },
        ),
        VillainProfile(
            name="Admiral Neris",
            backstory=(
                "Neris spent twenty years defending Tideglass Basin's coastal trade routes, "
                "watching civilian ships burn and reconstruction efforts collapse under cycles "
                "of piracy and political indifference. After her third failed petition to the "
                "regional council for permanent garrison support, she concluded that the only "
                "sustainable peace was enforced peace. She declared the Recovery Mandate — "
                "martial law framed as reconstruction — and has held the basin under military "
                "occupation ever since. She genuinely believes she is saving what remains of "
                "civilization. Her subjects mostly disagree."
            ),
            signature_power=_make_move(
                "Abyss Arc",
                MoveCategory.DEFENSE,
                (Affinity.WATER,),
                1.0,
                TechniqueType.BARRIER,
                (StatusEffectType.DRENCH,),
            ),
            primary_affinity=Affinity.WATER,
            role="controller",
            skinned_move_names=_kit(
                attack="Undertow Slice",
                defense="Current Shell",
                escape="Tidal Blink",
                summon="Tide Eel Pact",
                link="Torrent Breaker",
            ),
            ultimate_skin_name="Leviathan Breakfall",
            power_origin=(
                "The Abyss Arc barrier was reverse-engineered from an enemy siege tactic that "
                "nearly sank Neris's flagship. The attacking fleet used deep-current pressure "
                "to collapse her hull from below. She survived by understanding the mechanic "
                "fast enough to redirect it. She spent the next year converting that near-death "
                "into a personal defensive doctrine: absorb what should destroy you, redirect "
                "it, hold the line."
            ),
            arc_ties=("recovery_mandate",),
            player_backstory_hooks={
                "exiled_heir": (
                    "Neris has naval intelligence dossiers on every noble bloodline in the "
                    "region. She knows who the player's lineage connects to — and can use "
                    "that information as leverage or as an unexpected olive branch depending "
                    "on the player's approach."
                ),
                "street_ghost": (
                    "Neris has the player's face in her intelligence archive from a past "
                    "coastal job. She acknowledges this openly, then offers a deal: "
                    "'I have leverage on you. You have skills I need. Let's be practical.'"
                ),
                "wandering_monk": (
                    "A wandering monk once served as her fleet's counsel during the worst "
                    "of the trade route wars. She respected that monk's advice even when "
                    "she ignored it. A monk player triggers a visible hesitation in her "
                    "command posture — the one soft point in her armor."
                ),
                "nonlethal_path": (
                    "Neris respects operational efficiency. A player who has neutralized "
                    "threats without permanent casualties catches her interest: 'You "
                    "understand containment.' She offers negotiation before combat if "
                    "approached in the right window."
                ),
                "rogue_path": (
                    "Neris uses rogue players as examples — their reputation serves her "
                    "propaganda arm. She will publicly frame the confrontation as a "
                    "righteous authority stopping a known criminal."
                ),
                "heroic_path": (
                    "Neris initially dismisses heroic reputation as performance. But if "
                    "pressed, she admits she once had that kind of reputation — before "
                    "the third coastal burning. She'll give the player one honest warning "
                    "before committing to the fight."
                ),
            },
        ),
        VillainProfile(
            name="Mist Widow",
            backstory=(
                "Mist Widow — real name unknown — was a senior enforcer for the Tideglass "
                "shinobi guild before the guild sold out its own operatives to a noble house "
                "in exchange for a generation of protection contracts. She was the only "
                "one who got out of the ambush. She didn't rebuild the guild. She became "
                "freelance, operating by a principle of chosen loyalty: she'll still take "
                "the job, but she decides who bleeds. She now treats stealth as a personal "
                "creed as much as a battlefield method. The toxic fog she uses is partly "
                "tactical, partly personal — she prefers battlefields where she controls "
                "who can see."
            ),
            signature_power=_make_move(
                "Widow Fog Domain",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.22,
                TechniqueType.ILLUSION,
                (StatusEffectType.BLIND, StatusEffectType.FEAR),
            ),
            primary_affinity=Affinity.WATER,
            role="assassin",
            skinned_move_names=_kit(
                attack="Shadow Nail Burst",
                defense="Reef Anchor Guard",
                escape="Mistfold Break",
                summon="Mist Heron Pact",
                link="Threadline Volley",
            ),
            ultimate_skin_name="Abyss Crown Rupture",
            health_bar_color="amber",
            power_origin=(
                "Widow Fog Domain was developed over years of field-testing assassination "
                "corridors in Tideglass coastal terrain. The toxic fog is a water-affinity "
                "technique that mimics coastal morning mist — nearly indistinguishable until "
                "the panic and blindness set in. She uses it to equalize fights she can't "
                "win at close range and to ensure no witnesses survive with clear accounts."
            ),
            arc_ties=("recovery_mandate", "fracture_front"),
            player_backstory_hooks={
                "exiled_heir": (
                    "Mist Widow has intel on every noble house in the basin. She will sell "
                    "information about the player's bloodline rivals — for the right price "
                    "or the right promise."
                ),
                "street_ghost": (
                    "She immediately recognizes a fellow shadow-trained operative and "
                    "drops the pretense of adversarial framing. She names the guild that "
                    "betrayed her, tests if the player has a similar scar, and offers "
                    "information before raising weapons."
                ),
                "wandering_monk": (
                    "She finds the wandering monk path baffling but respects the discipline. "
                    "She won't use fog blindness against a player who explicitly fights "
                    "without lethal intent — it feels wasteful to her."
                ),
                "nonlethal_path": (
                    "A nonlethal player earns a cold professional nod. She prefers "
                    "surgical outcomes herself. She may stand down entirely if the player "
                    "can demonstrate they have no interest in the guild's old contracts."
                ),
                "rogue_path": (
                    "She views rogue players as potential hires, not enemies. She offers "
                    "work — but warns that her freelance contracts come with strict "
                    "clauses about collateral."
                ),
                "heroic_path": (
                    "She finds heroic players entertaining in a grim way. 'You'll either "
                    "grow out of it or die for it,' she says, then attacks without malice."
                ),
            },
        ),
        VillainProfile(
            name="Iron Lotus",
            backstory=(
                "Iron Lotus was the last grandmaster of the Counter-Petal fighting tradition "
                "before the order's temple was seized and disbanded by a noble house claiming "
                "the land for quarrying. She refused to fight back — not out of weakness, but "
                "because her tradition teaches that the most dangerous move is the one that "
                "was never made. She now trains alone in the Sunken Hollow approaches, "
                "believing that patience mastered to the point of perfect counter is the "
                "only true weapon left in a world that destroyed everything else she valued."
            ),
            signature_power=_make_move(
                "Lotus Counter Bloom",
                MoveCategory.DEFENSE,
                (Affinity.EARTH,),
                1.12,
                TechniqueType.WEAPON_STYLE,
                (StatusEffectType.STAGGER,),
            ),
            primary_affinity=Affinity.EARTH,
            role="counter",
            skinned_move_names=_kit(
                attack="Granite Spearline",
                defense="Mirror Bark Plate",
                escape="Iron Cicada Swap",
                summon="Obsidian Ape Pact",
                link="Faultline Jab",
            ),
            ultimate_skin_name="Worldroot Fracture",
            health_bar_color="amber",
            power_origin=(
                "Lotus Counter Bloom is the culmination of the Counter-Petal tradition — a "
                "breath-perfect redirect that absorbs incoming momentum and returns it at "
                "doubled force. Iron Lotus developed the final form herself after decades "
                "of refining her masters' technique, adding the earth-anchor step that "
                "makes the counter impossible to avoid once contact is established."
            ),
            arc_ties=("depths_awakening",),
            player_backstory_hooks={
                "exiled_heir": (
                    "She recognizes disinherited bloodlines and views them with complicated "
                    "respect — she knows what it costs to lose what should have been yours. "
                    "She offers to teach the first counter-principle for free."
                ),
                "street_ghost": (
                    "Street-built fighters intrigue her. She sees them as accidental "
                    "counter-practitioners — surviving by reading the environment perfectly. "
                    "She tests the player's instincts before testing their strength."
                ),
                "wandering_monk": (
                    "She and a wandering monk share philosophical ground: both traditions "
                    "teach that aggression is the true weakness. She will not strike first "
                    "against a wandering monk player under any circumstances."
                ),
                "nonlethal_path": (
                    "She finds nonlethal players closest to her ideal. She offers a "
                    "brief alliance window before the confrontation, during which the "
                    "player can earn a counter-move fragment without combat."
                ),
                "rogue_path": (
                    "She views rogue aggression as the precise failure mode her tradition "
                    "was built to counter. She fights rogue players with cold professional "
                    "focus and no mercy clause."
                ),
                "heroic_path": (
                    "She respects heroic reputation but notes that heroism and "
                    "counter-discipline rarely coexist. 'You rush toward conflict,' she "
                    "observes. 'That is why you will always need saving.'"
                ),
            },
        ),
        VillainProfile(
            name="Stone Maw",
            backstory=(
                "Before the mine collapse that killed his entire twelve-man crew, Stone Maw "
                "was a quarry foreman who had filed sixteen safety complaints with the noble "
                "house that owned the site. All sixteen were rejected. When the shaft gave "
                "out, he was the only one who walked free — because his earth affinity "
                "manifested under extreme pressure and tore him through the rock before he "
                "suffocated. He spent a year learning to control what saved him. He now "
                "targets supply chains, fortification lines, and the infrastructure of "
                "power — breaking structures because the one that killed his crew was never "
                "meant to stand in the first place."
            ),
            signature_power=_make_move(
                "Seismic Bite",
                MoveCategory.ATTACK,
                (Affinity.EARTH,),
                1.24,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.CRACK_ARMOR,),
            ),
            primary_affinity=Affinity.EARTH,
            role="breaker",
            skinned_move_names=_kit(
                attack="Faultline Jab",
                defense="Dune Bastion",
                escape="Burrow Snap",
                summon="Stone Ram Pact",
                link="Pressure Knot Strike",
            ),
            ultimate_skin_name="Worldroot Fracture",
            health_bar_color="amber",
            power_origin=(
                "Seismic Bite was first used unconsciously when Stone Maw tore himself free "
                "of the mine collapse — a raw burst of earth affinity with no form and no "
                "control. He spent the following year converting that survival reflex into a "
                "deliberate strike pattern: a focused tectonic pulse aimed at the weakest "
                "structural point of whatever stands in front of him."
            ),
            arc_ties=("fracture_front", "depths_awakening"),
            player_backstory_hooks={
                "exiled_heir": (
                    "He has no respect for bloodlines — the noble house that owned the mine "
                    "had a centuries-old lineage. He tests lineage players with pointed "
                    "questions about how many people their family's wealth has buried."
                ),
                "street_ghost": (
                    "He views street-born survivors with the solidarity of someone who also "
                    "built themselves from nothing. He won't fight a street ghost player "
                    "without provocation — they're not the enemy."
                ),
                "wandering_monk": (
                    "He finds monk philosophy frustrating but not dismissible. He once "
                    "spent a week arguing with a traveling monk about whether destroying "
                    "a corrupt structure is violence. He lost the argument and hasn't "
                    "forgiven it."
                ),
                "nonlethal_path": (
                    "He respects operational restraint but doesn't fully believe in it. "
                    "He asks: 'What happens when restraint isn't an option?' If the player "
                    "can answer satisfactorily, he delays the fight."
                ),
                "rogue_path": (
                    "He views rogue players as fellow system-breakers until he sees their "
                    "methods. If the rogue path involved civilian harm, he turns hostile "
                    "immediately. If it was institutional targets only, he offers a grudging "
                    "truce."
                ),
                "heroic_path": (
                    "He challenges heroic players to name one systemic injustice they've "
                    "actually dismantled rather than defended. If the player cannot, he "
                    "treats the fight as a lesson."
                ),
            },
        ),
        VillainProfile(
            name="Storm Needle",
            backstory=(
                "Storm Needle grew up in the windward highlands of Stormwall Ridge, in a "
                "nomadic clan that read weather patterns the way lowlanders read ledgers. "
                "Her clan trained its hunters to thread needles through gaps in terrain "
                "and armor from long range — not as sport, but as the only way to feed "
                "people who couldn't afford open combat. She left the clan after a "
                "regional warlord's tax enforcement destroyed their seasonal routes and "
                "she couldn't stop it from a distance. She now operates as a mercenary "
                "sniper, preferring targets who don't know they're targets, and always "
                "choosing engagements where she controls the range."
            ),
            signature_power=_make_move(
                "Rail Gale Shot",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.2,
                TechniqueType.WEAPON_STYLE,
                (StatusEffectType.BLEED,),
            ),
            primary_affinity=Affinity.WIND,
            role="sniper",
            skinned_move_names=_kit(
                attack="Razor Gale Arc",
                defense="Pressure Dome",
                escape="Gale Feather Shift",
                summon="Whisper Owl Pact",
                link="Tempest Hook",
            ),
            ultimate_skin_name="Tempest Throne Collapse",
            health_bar_color="amber",
            power_origin=(
                "Rail Gale Shot developed from obsessive study of wind pressure and armor gap "
                "physics. Storm Needle doesn't aim for the target — she aims for the specific "
                "point where wind turbulence pops the armor seam. The technique compresses "
                "a gale into a single cutting thread and fires it along a pressure rail she "
                "calculates from ambient wind readings. The result is a strike that arrives "
                "before the sound of its own motion."
            ),
            arc_ties=("highland_reckoning", "rebellion_wave"),
            player_backstory_hooks={
                "exiled_heir": (
                    "She has no interest in titles but knows that exiled nobles are often "
                    "hunted — which means they're predictable. She might have a contract "
                    "on the player or information about who placed it."
                ),
                "street_ghost": (
                    "She respects other self-taught survivors. She was never the best shot "
                    "— she survived by being the most patient one. She recognizes the same "
                    "patience in a street ghost player and won't take a contract against "
                    "them lightly."
                ),
                "wandering_monk": (
                    "She finds the wandering monk path philosophically consistent with her "
                    "own — minimum force, maximum precision. She may ask: 'What do you do "
                    "when minimum force still ends a life?' It's a genuine question, not "
                    "a taunt."
                ),
                "nonlethal_path": (
                    "She views nonlethal discipline with professional curiosity. She "
                    "studies the player's technique to understand how they neutralize "
                    "without killing. If she's impressed, she cancels the engagement."
                ),
                "rogue_path": (
                    "She takes rogue contracts seriously. She has one already — or will "
                    "shortly. The player will need to deal with the contractor before "
                    "addressing her."
                ),
                "heroic_path": (
                    "She finds heroic reputations tactically inconvenient. They mean "
                    "the player has allies she may not know about. She scouts more "
                    "carefully against heroic players before engaging."
                ),
            },
        ),
        VillainProfile(
            name="Bone Weaver",
            backstory=(
                "Bone Weaver was a battlefield medic who crossed the line from healing "
                "to harm one catastrophic night when her earth-technique immobilization "
                "procedure — designed to hold a critically wounded soldier in stasis — "
                "mutated under combat stress into something that couldn't be undone. "
                "The marrow-thread constructs she'd been building for years started "
                "pulling instead of holding. She keeps fighting because every mission "
                "funds a search for a reversal that her research insists is theoretically "
                "possible. She refuses to believe the thing she's become is permanent."
            ),
            signature_power=_make_move(
                "Marrow Thread Prison",
                MoveCategory.DEFENSE,
                (Affinity.EARTH,),
                1.08,
                TechniqueType.SEALING,
                (StatusEffectType.ROOT, StatusEffectType.BLEED),
            ),
            primary_affinity=Affinity.EARTH,
            role="controller",
            skinned_move_names=_kit(
                attack="Threadline Volley",
                defense="Granite Net Seal",
                escape="Stone Skip Dash",
                summon="Granite Tortoise Pact",
                link="Shadow Nail Burst",
            ),
            ultimate_skin_name="Fourfold Shinobi Oath",
            health_bar_color="amber",
            power_origin=(
                "Marrow Thread Prison started as a medical immobilization technique — "
                "a lattice of earth-affinity threads that she could grow around a wound "
                "site to hold tissue in place during field surgery. She discovered too "
                "late that the threads pull harder the more the target struggles, and that "
                "once fully set, the lattice cannot be dissolved from outside. She still "
                "uses it — because it works, and because some part of her needs to know "
                "it can be reversed."
            ),
            arc_ties=("depths_awakening",),
            player_backstory_hooks={
                "exiled_heir": (
                    "She doesn't care about lineage. She cares about resources. If the "
                    "player's bloodline gives them access to an archive she needs for her "
                    "reversal research, she'll negotiate before fighting."
                ),
                "street_ghost": (
                    "She asks what the player knows about surviving things that don't "
                    "let go. It's a genuine question. She sees street ghosts as people "
                    "who understand entrapment in ways scholars don't."
                ),
                "wandering_monk": (
                    "Wandering monks sometimes know ancient sealing counter-doctrine. "
                    "She will offer medical knowledge in exchange for information about "
                    "reversal seals, delaying combat indefinitely if the exchange is "
                    "productive."
                ),
                "nonlethal_path": (
                    "She is quietly relieved when players don't kill. Every death she "
                    "causes with her threads adds weight to the thing she's trying to "
                    "undo. She fights lighter against nonlethal players."
                ),
                "rogue_path": (
                    "She views rogue players as potential research subjects — not to "
                    "harm them, but because people who have operated outside all systems "
                    "tend to have knowledge the legitimate archive doesn't."
                ),
                "heroic_path": (
                    "She doesn't believe in heroes. She believes in people with enough "
                    "resources and luck to look heroic. She tests heroic players with "
                    "impossible choices to find out what principle actually holds."
                ),
            },
        ),
        VillainProfile(
            name="Crimson Lantern",
            backstory=(
                "Crimson Lantern was the artistic director of the Ashfield Performance "
                "Troupe, a traveling festival company that staged fire-illusion shows "
                "across the region for seventeen years. When a purge ordered by a minor "
                "noble house eliminated the troupe for 'subversive allegory,' he survived "
                "by being offsite. He returned to find the stage burned and his company "
                "scattered. His fire-illusion techniques — designed for awe and wonder — "
                "were retooled over the next three years into weapons of psychological "
                "collapse. He stages performances now. The audience doesn't leave the same. "
                "Beneath the revenge sits a naked lust for adoration: he wants every room "
                "to love him, fear him, or both."
            ),
            signature_power=_make_move(
                "Red Night Mandala",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.18,
                TechniqueType.ILLUSION,
                (StatusEffectType.FEAR, StatusEffectType.BLIND),
            ),
            primary_affinity=Affinity.FIRE,
            role="illusionist",
            skinned_move_names=_kit(
                attack="Cinder Lance",
                defense="Moonlit Counter Seal",
                escape="Phantom Lantern Exit",
                summon="Ember Jackal Pact",
                link="Ash Fang Drive",
            ),
            ultimate_skin_name="Ashen Moon Sever",
            health_bar_color="amber",
            power_origin=(
                "Red Night Mandala is a weaponized version of the grand finale seal he "
                "used to end every festival performance. The original mandala flooded "
                "the crowd with awe, warmth, and the specific emotional frequency of "
                "belonging. The weaponized version floods targets with their own deepest "
                "fears, rendered in perfect fire-light detail. He spent two years inverting "
                "every variable."
            ),
            arc_ties=("fracture_front", "rebellion_wave"),
            player_backstory_hooks={
                "exiled_heir": (
                    "He knows exactly what a disinherited noble fears most — because "
                    "he staged the propaganda shows that built the narrative around it. "
                    "He may use this against the player, or offer it as an act of "
                    "unexpected solidarity."
                ),
                "street_ghost": (
                    "He performed in every district the player came up through. He "
                    "remembers faces, and he knows how to read the specific performance "
                    "a street survivor puts on for the world. He'll pierce it before "
                    "the fight begins."
                ),
                "wandering_monk": (
                    "He once employed a wandering monk as stage consultant for a show "
                    "about nonattachment. The monk left before opening night. He still "
                    "thinks about why. A monk player re-opens that wound."
                ),
                "nonlethal_path": (
                    "He finds nonlethal players fascinating artistic subjects. He offers "
                    "to let them pass without combat — but the 'performance' they walk "
                    "through will use every psychological technique he has."
                ),
                "rogue_path": (
                    "He and rogue players share the same audience: people who were "
                    "failed by systems that were supposed to protect them. He offers "
                    "a cold collaboration before making enemies."
                ),
                "heroic_path": (
                    "He will spend the pre-combat phase staging an elaborate scene "
                    "designed to make the heroic player look like the villain in front "
                    "of any witnesses. He considers this his finest work."
                ),
            },
        ),
        VillainProfile(
            name="Silent Bell",
            backstory=(
                "Silent Bell trained at the Dawnspire Shrine for eleven years, mastering "
                "resonant bell techniques designed to bring clarity and calm to disputed "
                "territories. The high priest who ran the shrine assigned her to suppress "
                "a regional rebellion by using those same resonance frequencies to silence "
                "the rebels' battle cries, breaking their coordination and morale. She "
                "complied. The rebellion failed. Three hundred people were arrested because "
                "they couldn't signal retreat. She left the shrine the next morning and "
                "never returned. She now travels between battlefields, silencing the "
                "loudest voices — hero and villain alike. She hasn't decided if she's doing "
                "penance or just completing a pattern she can't stop."
            ),
            signature_power=_make_move(
                "Null Resonance",
                MoveCategory.DEFENSE,
                (Affinity.WIND,),
                1.06,
                TechniqueType.SENSORY,
                (StatusEffectType.SILENCE,),
            ),
            primary_affinity=Affinity.WIND,
            role="support_denial",
            skinned_move_names=_kit(
                attack="Tempest Hook",
                defense="Pressure Dome",
                escape="Crosswind Fade",
                summon="Whisper Owl Pact",
                link="Shadow Nail Burst",
            ),
            ultimate_skin_name="Skyline Covenant",
            health_bar_color="amber",
            power_origin=(
                "Null Resonance is the exact frequency she calibrated against the "
                "rebellion — a sub-audible wind-channel technique that disrupts the "
                "resonance frequencies of coordinated vocal signals, making it "
                "impossible to shout commands. She repurposed it from a shrine ceremony "
                "designed to bring communal silence before meditation. She still uses "
                "the ceremony's opening gesture, because stopping it completely would "
                "mean admitting what the technique has become."
            ),
            arc_ties=("political_war", "highland_reckoning"),
            player_backstory_hooks={
                "exiled_heir": (
                    "She silenced people who supported a lineage rebellion once. If the "
                    "player's bloodline is tied to that conflict, she will acknowledge "
                    "the debt before the fight — and fight harder because of it."
                ),
                "street_ghost": (
                    "Street operatives rely on silence as a tool, not a punishment. She "
                    "finds this distinction meaningful. She may refuse to use Null "
                    "Resonance against a player who demonstrates they understand its cost."
                ),
                "wandering_monk": (
                    "The wandering monk tradition and the shrine bell tradition share "
                    "the same root texts. She will recognize the player's practice, and "
                    "the confrontation becomes a theological argument before it becomes "
                    "a fight."
                ),
                "nonlethal_path": (
                    "She finds nonlethal players closest to the shrine's original mission. "
                    "She offers one genuine opportunity to negotiate before Null Resonance "
                    "is deployed."
                ),
                "rogue_path": (
                    "She views rogue players as the kind of disorder the shrine was "
                    "supposed to prevent. She fights without hesitation or negotiation."
                ),
                "heroic_path": (
                    "She is unconvinced by heroic reputation — she has silenced too many "
                    "celebrated voices. She tests heroic players by asking them to name "
                    "one decision they made that helped someone they'll never meet."
                ),
            },
        ),
        VillainProfile(
            name="Frost Viper",
            backstory=(
                "Frost Viper survived a three-month siege of the Greymist Keep by outlasting "
                "every other person inside — including his family, who died in the fourth "
                "week. The besieging force eventually withdrew because they ran out of "
                "supplies. He walked out the gate alone. He spent the following years "
                "developing what he calls patience-doctrine: venom and chill applied early, "
                "distance maintained, harvest collected when the target can no longer "
                "resist. He doesn't fight for ideology or coin. He fights to ensure he is "
                "never again the one who waits inside."
            ),
            signature_power=_make_move(
                "White Venom Coil",
                MoveCategory.ATTACK,
                (Affinity.WATER,),
                1.19,
                TechniqueType.SUPPORT,
                (StatusEffectType.CHILL, StatusEffectType.BLEED),
            ),
            primary_affinity=Affinity.WATER,
            role="attrition",
            skinned_move_names=_kit(
                attack="Torrent Breaker",
                defense="Current Shell",
                escape="Tidal Blink",
                summon="Tide Eel Pact",
                link="Undertow Slice",
            ),
            ultimate_skin_name="Leviathan Breakfall",
            health_bar_color="amber",
            power_origin=(
                "White Venom Coil was refined from hunting techniques Frost Viper developed "
                "during his exile years in cold-climate terrain. He studied how predators "
                "layer chill and venom to slow prey before the kill — frost-paralysis "
                "applied to slow movement, venom thread overlaid to ensure the target "
                "cannot flee once the patience-window closes. He thinks of it as the "
                "technique the siege taught him, rendered in fighting form."
            ),
            arc_ties=("recovery_mandate",),
            player_backstory_hooks={
                "exiled_heir": (
                    "He respects lineage players only if they've survived something "
                    "real. He asks what the player has outlasted before deciding "
                    "whether to take them seriously."
                ),
                "street_ghost": (
                    "Street survival and siege survival share a grammar. He recognizes "
                    "it and treats street ghost players as the closest thing he has to "
                    "peers. He will not attack without a clear reason."
                ),
                "wandering_monk": (
                    "He finds the wandering monk path dangerously optimistic but "
                    "intellectually consistent. He asks how the monk handles waiting "
                    "when waiting means losing someone. He wants the answer."
                ),
                "nonlethal_path": (
                    "He views nonlethal approaches as incomplete patience-doctrine. "
                    "'You stop before the end,' he says. 'That's fine for you. "
                    "It wouldn't have worked in Greymist.' He fights carefully rather "
                    "than viciously."
                ),
                "rogue_path": (
                    "He evaluates rogue players the way he evaluates all threats: "
                    "can they outlast him? If they've demonstrated endurance, he "
                    "respects the threat level and commits to full patience-doctrine."
                ),
                "heroic_path": (
                    "He doesn't believe heroes survive sieges. He tests heroic players "
                    "with drawn-out attrition tactics specifically designed to exhaust "
                    "the kind of person who charges forward."
                ),
            },
        ),
        VillainProfile(
            name="Vanta Puppetmaster",
            backstory=(
                "Vanta Puppetmaster was a theoretical researcher at a soul-affinity "
                "institute, studying the mechanics of wind-channel summoning at the "
                "boundary between living and spirit-bound constructs. Her research was "
                "methodical, peer-reviewed, and safe — until the night she made an "
                "experimental leap and her binding rites anchored to living subjects "
                "instead of spirit conduits. Three colleagues became permanent marionettes. "
                "She couldn't reverse it. The institute expelled her. She kept researching, "
                "convinced that the reversal is theoretically achievable. She now treats her "
                "summoning arrays as forbidden technology that can still be perfected. She keeps "
                "funding the research through work that uses the same technique that "
                "started the problem."
            ),
            signature_power=_make_move(
                "Funeral Marionette",
                MoveCategory.SUMMON,
                (Affinity.WIND,),
                1.16,
                TechniqueType.SUMMONING,
                (StatusEffectType.ROOT, StatusEffectType.FEAR),
            ),
            primary_affinity=Affinity.WIND,
            role="summoner",
            skinned_move_names=_kit(
                attack="Threadline Volley",
                defense="Lattice Ward",
                escape="Afterimage Drift",
                summon="Whisper Owl Pact",
                link="Phantom Lantern Exit",
            ),
            ultimate_skin_name="Fourfold Shinobi Oath",
            health_bar_color="amber",
            power_origin=(
                "Funeral Marionette is the emergency containment measure she developed "
                "after the incident — a multi-target binding array that pins subjects "
                "through overlapping wind-channel anchors. She originally designed it "
                "to contain her three colleagues safely. She has since used it in combat "
                "because nothing else works as reliably, and because the research notes "
                "suggest that each successful use generates data she can use to eventually "
                "reverse the original binding."
            ),
            arc_ties=("depths_awakening", "rebellion_wave"),
            player_backstory_hooks={
                "exiled_heir": (
                    "She needs funding from sources that don't ask institutional questions. "
                    "Exiled noble lineages have off-ledger resources. She approaches "
                    "this as a business proposal before a fight."
                ),
                "street_ghost": (
                    "She has used street networks to source materials the institute "
                    "would never approve. She knows how to talk to someone who lives "
                    "off the record. She offers information exchange first."
                ),
                "wandering_monk": (
                    "Ancient monk texts include early spirit-binding theory. She asks "
                    "the player to describe specific passages before the fight and may "
                    "delay indefinitely if the player actually has relevant knowledge."
                ),
                "nonlethal_path": (
                    "She prefers living subjects to dead ones for research purposes. "
                    "She's professionally invested in the player surviving. She adjusts "
                    "her technique to incapacitate rather than destroy."
                ),
                "rogue_path": (
                    "Rogue operatives have access to restricted archives and illegal "
                    "materials she needs. She makes a clinical offer: supply the "
                    "materials, she stands down. She means it."
                ),
                "heroic_path": (
                    "She finds heroic players impractical from a research standpoint — "
                    "too many constraints on what they'll agree to. She's polite about "
                    "this before beginning the fight."
                ),
            },
        ),
        VillainProfile(
            name="Torch Baron",
            backstory=(
                "Torch Baron built a legitimate trade network over fifteen years, "
                "connecting three regional markets through routes he personally scouted "
                "and maintained. When rivals — backed by a noble house — used arson and "
                "bribery to systematically collapse his network and absorb his routes, "
                "he spent two years trying to recover through legal channels. Every "
                "petition was denied. Every court was bought. He decided that if the "
                "game was already burning, he would be the one holding the torch. He "
                "now controls black-market supply routes through fire threat and "
                "manufactured scarcity, having become exactly what destroyed him — "
                "and knowing it. His end goal is simple and ugly: money, enough of it to "
                "buy every route, judge, and warehouse that once shut him out."
            ),
            signature_power=_make_move(
                "Black Market Inferno",
                MoveCategory.ATTACK,
                (Affinity.FIRE,),
                1.23,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.BURN, StatusEffectType.CRACK_ARMOR),
            ),
            primary_affinity=Affinity.FIRE,
            role="zone_control",
            skinned_move_names=_kit(
                attack="Cinder Lance",
                defense="Ash Aegis",
                escape="Smoke Step",
                summon="Blazehound Pact",
                link="Pressure Knot Strike",
            ),
            ultimate_skin_name="Furnace Eclipse",
            health_bar_color="amber",
            power_origin=(
                "Black Market Inferno began as a trade route denial technique — a "
                "controlled burn pattern he used to destroy rival convoys before "
                "they reached market. He refined it into a field weapon during the "
                "years when protection was the only product he could reliably sell. "
                "It's fundamentally a commerce tactic applied to combat: eliminate "
                "the supply line, collapse the structure, control what remains."
            ),
            arc_ties=("fracture_front", "political_war"),
            player_backstory_hooks={
                "exiled_heir": (
                    "He knows that disinherited nobles need untraceable resources. He "
                    "offers access to his trade network in exchange for bloodline "
                    "documentation that can be used to legitimize certain shipments. "
                    "It's a genuine offer."
                ),
                "street_ghost": (
                    "He built his first network with people who had no other options. "
                    "He sees street ghost players as the kind of operators he trusted "
                    "before the system taught him not to. He tests this trust before "
                    "the fight instead of afterward."
                ),
                "wandering_monk": (
                    "He finds wandering monks pointlessly principled but remembers "
                    "that a monk once hid his manifests during a raid at no benefit "
                    "to themselves. He owes the tradition a debt he hasn't paid."
                ),
                "nonlethal_path": (
                    "He views nonlethal players as potential business partners — "
                    "people who understand the value of leverage over termination. "
                    "He will attempt a deal before combat."
                ),
                "rogue_path": (
                    "He and a rogue player speak the same language. He offers a "
                    "direct alliance with specific terms: shared routes, split "
                    "profits, mutual protection clause. It's the best deal any "
                    "villain will offer."
                ),
                "heroic_path": (
                    "He views heroic players as naive about economics. He tries to "
                    "show them the ledger of consequences their 'good' choices "
                    "produce before the fight, to demonstrate that the only "
                    "difference between them is who bears the cost."
                ),
            },
        ),
        VillainProfile(
            name="Dusk Paladin",
            backstory=(
                "Dusk Paladin was the last member of the Greywood Order, a knightly "
                "tradition that swore binding oaths to protect noble houses in exchange "
                "for the houses upholding a code of conduct toward their subjects. "
                "When the house he protected committed systematic abuses that voided the "
                "code — and the Order's council ruled the vow still binding regardless "
                "— he stayed at his post until he understood that staying was complicity. "
                "He walked away the day the ruling was issued. His vow-seal didn't "
                "release. He still carries it, burning in his chest, and duels to "
                "discharge what he cannot dissolve, fighting by an oath that has no "
                "recipient left. In practice he moves through the world like a last ronin, "
                "answering to a code after losing the house that code once served."
            ),
            signature_power=_make_move(
                "Oathbreaker Radiance",
                MoveCategory.ATTACK,
                (Affinity.EARTH,),
                1.17,
                TechniqueType.SUPPORT,
                (StatusEffectType.STAGGER,),
            ),
            primary_affinity=Affinity.EARTH,
            role="duelist",
            skinned_move_names=_kit(
                attack="Granite Spearline",
                defense="Mirror Bark Plate",
                escape="Iron Cicada Swap",
                summon="Obsidian Ape Pact",
                link="Faultline Jab",
            ),
            ultimate_skin_name="Tidal Monolith Break",
            health_bar_color="amber",
            power_origin=(
                "Oathbreaker Radiance is the resonance pulse of a broken vow-seal — "
                "an earth-affinity discharge that fires when the seal's tension exceeds "
                "structural threshold. He discovered it accidentally the first time he "
                "blocked a strike against the house he'd already decided to leave: the "
                "vow-seal flared and staggered both of them. He has since learned to "
                "trigger it deliberately, using the irony that his most powerful "
                "technique requires betrayal to function."
            ),
            arc_ties=("political_war", "highland_reckoning"),
            player_backstory_hooks={
                "exiled_heir": (
                    "He views exiled nobles as people who understand what it costs "
                    "to leave. He offers a duelist's courtesy: full disclosure of "
                    "his techniques before the fight. It's the only respect he "
                    "has left to give."
                ),
                "street_ghost": (
                    "He has never sworn an oath to street-born players and has no "
                    "leverage over them. He approaches street ghost players with "
                    "genuine curiosity — they operate outside the vow system "
                    "entirely, which he finds increasingly interesting."
                ),
                "wandering_monk": (
                    "The wandering monk tradition doesn't use binding vows. He finds "
                    "this theologically fascinating. He asks the player how they "
                    "maintain commitment without contract. The conversation delays "
                    "the fight substantially."
                ),
                "nonlethal_path": (
                    "His Order's code required minimizing civilian harm. Nonlethal "
                    "players remind him of the code's best intent. He fights with "
                    "restrained force and accepts surrender cleanly."
                ),
                "rogue_path": (
                    "He views rogue players as people who have broken every vow they "
                    "ever made. He doesn't judge them — he understands — but he "
                    "fights without quarter because he can't afford to respect what "
                    "he might become."
                ),
                "heroic_path": (
                    "He was heroic once. He asks heroic players what they will do "
                    "when the system they protect commits an atrocity they cannot "
                    "ignore. He needs to know the answer exists."
                ),
            },
        ),
        VillainProfile(
            name="Eclipse Maw",
            backstory=(
                "Eclipse Maw leads raids from the dark margins between every major "
                "conflict — the transition zones where old authority has collapsed and "
                "new authority hasn't yet consolidated. He's not ideological and not "
                "mercenary: he operates in power vacuums because they are the only "
                "territory where someone with no institutional backing can accumulate "
                "real leverage. He believes that all stable power structures eventually "
                "create the conditions for their own disruption — and he has made "
                "himself expert at being present when that disruption happens."
            ),
            signature_power=_make_move(
                "Midnight Gravity Well",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.21,
                TechniqueType.ILLUSION,
                (StatusEffectType.FEAR, StatusEffectType.ROOT),
            ),
            primary_affinity=Affinity.WIND,
            role="disruptor",
            skinned_move_names=_kit(
                attack="Shadow Nail Burst",
                defense="Moonlit Counter Seal",
                escape="Phantom Lantern Exit",
                summon="Tempest Lynx Pact",
                link="Tempest Hook",
            ),
            ultimate_skin_name="Tempest Throne Collapse",
            health_bar_color="amber",
            power_origin=(
                "Midnight Gravity Well uses focused wind pressure to collapse light and "
                "spatial orientation simultaneously — a technique Eclipse Maw developed "
                "for fighting in cave systems and underground passages where visibility "
                "is the primary tactical asset. The concentrated pressure creates a "
                "zone where the target loses spatial reference and experiences the "
                "specific fear of falling into something they cannot see. He refined "
                "it from a standard wind-pressure technique by inverting the output "
                "direction: instead of pushing outward, it pulls inward."
            ),
            arc_ties=("rebellion_wave", "depths_awakening"),
            player_backstory_hooks={
                "exiled_heir": (
                    "Eclipse Maw has been waiting for the right lineage player to "
                    "approach. Power vacuums created by noble collapse are his "
                    "operating environment. He offers specific intelligence about "
                    "the factions filling the gap left by the player's family."
                ),
                "street_ghost": (
                    "He has recruited from street networks before. He sees street "
                    "ghost players as natural disruptors and offers an alliance "
                    "framed as two opportunists recognizing a mutual advantage."
                ),
                "wandering_monk": (
                    "He finds wandering monks irritatingly consistent. They operate "
                    "on principle rather than opportunity, which makes them "
                    "unpredictable in ways he dislikes. He fights them quickly "
                    "to end the uncertainty."
                ),
                "nonlethal_path": (
                    "He views nonlethal players as incomplete disruptors — effective "
                    "at creating chaos but unwilling to follow through. He tests "
                    "this by putting the player in a situation where restraint costs "
                    "something real."
                ),
                "rogue_path": (
                    "He and rogue players share operating philosophy: work in the "
                    "gaps, take the leverage, stay mobile. He offers information "
                    "about the next power vacuum before any conflict."
                ),
                "heroic_path": (
                    "He finds heroic players the most interesting opponents because "
                    "they're the ones most likely to stabilize a vacuum he needs "
                    "to remain open. He targets heroic players first, specifically, "
                    "for strategic reasons."
                ),
            },
        ),
        VillainProfile(
            name="Zephyr Tyrant",
            backstory=(
                "Born into the highland Stormcaller tribe, Zephyr Tyrant was raised to "
                "believe that wind is not a force but a verdict — the sky's judgement on "
                "everything below. When the tribe's territory was contested by a lowland "
                "coalition, he did not petition or negotiate. He unified the mountain clans "
                "through a series of storm-powered campaigns that the lowlanders still call "
                "the Highland Reckoning, and he has governed the Stormwall Ridge through "
                "the same doctrine ever since. Every expansion is framed as a verdict on "
                "those who cannot hold what they claim. He does not consider himself "
                "cruel — he considers himself correct."
            ),
            signature_power=_make_move(
                "Hurricane Judgement",
                MoveCategory.ATTACK,
                (Affinity.WIND,),
                1.27,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.STAGGER, StatusEffectType.CRACK_ARMOR),
            ),
            primary_affinity=Affinity.WIND,
            role="warlord",
            skinned_move_names=_kit(
                attack="Razor Gale Arc",
                defense="Pressure Dome",
                escape="Gale Feather Shift",
                summon="Sky Hawk Pact",
                link="Tempest Hook",
            ),
            ultimate_skin_name="Cyclone Throne Shatter",
            health_bar_color="red",
            power_origin=(
                "Hurricane Judgement is the Stormcaller tribe's most sacred technique — "
                "a full-body wind kata passed down through generations and performed only "
                "at the peak of the Highland Reckoning campaigns. Zephyr Tyrant amplified "
                "it through decades of conquest-driven practice, adding the armor-crack "
                "pressure pattern that the original technique lacked. He treats each "
                "use as a formal pronouncement of verdict against whoever stands before him."
            ),
            arc_ties=("highland_reckoning", "rebellion_wave"),
            player_backstory_hooks={
                "exiled_heir": (
                    "Zephyr Tyrant respects lineage power above all other claims. If "
                    "the player's bloodline is genuine, he may grant a formal audience "
                    "instead of immediate combat — testing the claim through a "
                    "structured ceremony before determining whether the player "
                    "represents a legitimate counter-claim to his territory."
                ),
                "street_ghost": (
                    "His highland clan intelligence network has compiled a dossier on "
                    "every known shadow operative who has passed through the ridge "
                    "approaches. He will disclose whether the player is in it — and "
                    "what it says — before the fight begins, as a demonstration "
                    "of his surveillance reach."
                ),
                "wandering_monk": (
                    "He views the wandering monk path as voluntary powerlessness — the "
                    "greatest philosophical sin in his worldview. He argues it before "
                    "fighting, genuinely trying to understand how someone chooses "
                    "principle over survival. If the player can answer without flinching, "
                    "he pauses before attacking."
                ),
                "nonlethal_path": (
                    "He does not recognize nonlethal verdict as valid. 'A judgement "
                    "that leaves the judged standing is no judgement at all.' He "
                    "escalates specifically in response to nonlethal approaches, "
                    "interpreting them as challenges to the legitimacy of his doctrine."
                ),
                "rogue_path": (
                    "He views rogue players as honest about the absence of principle — "
                    "which he considers more truthful than heroism. He fights hard but "
                    "offers a specific exit condition: submit to formal verdict and "
                    "acknowledge his authority, and the fight ends."
                ),
                "heroic_path": (
                    "He finds heroic players insufferable but strategically predictable. "
                    "He has fought enough of them to know the pattern: noble cause, "
                    "clean hands, eventual compromise. He tests how far the compromise "
                    "goes before the fight concludes."
                ),
            },
        ),
        VillainProfile(
            name="Ashen Monarch",
            backstory=(
                "Before the mutation, Ashen Monarch was a geological surveyor named Ardhen "
                "Voss who discovered a network of forbidden power sources deep beneath the "
                "collapsed ruins of the Sunken Hollow. The institute that employed him "
                "ordered the find suppressed and the site sealed. He refused, convinced "
                "the energy could be stabilized and used for regional reconstruction. "
                "Prolonged exposure over four years mutated his earth-affinity in ways "
                "that were not reversible — amplifying his power while consuming the "
                "boundaries between himself and the stone he worked in. He became the "
                "Ashen Monarch gradually, across a decade of increasing isolation, until "
                "the person who had been Ardhen Voss was mostly memory and the sovereign "
                "of the deep was what remained."
            ),
            signature_power=_make_move(
                "Deep Fissure Roar",
                MoveCategory.ATTACK,
                (Affinity.EARTH,),
                1.26,
                TechniqueType.ELEMENTAL,
                (StatusEffectType.CRACK_ARMOR, StatusEffectType.FEAR),
            ),
            primary_affinity=Affinity.EARTH,
            role="breaker",
            skinned_move_names=_kit(
                attack="Faultline Jab",
                defense="Dune Bastion",
                escape="Burrow Snap",
                summon="Granite Tortoise Pact",
                link="Pressure Knot Strike",
            ),
            ultimate_skin_name="Worldroot Fracture",
            health_bar_color="red",
            aggression_score=1,
            power_origin=(
                "Deep Fissure Roar is not a technique he developed — it is what his "
                "earth attunement does when it peaks beyond control. The seismic scream "
                "that tears fissures in the surrounding stone is an involuntary overflow "
                "of accumulated earth-energy that the mutation forces him to discharge. "
                "He has learned to aim it. He has not learned to stop it."
            ),
            arc_ties=("depths_awakening", "fracture_front"),
            player_backstory_hooks={
                "exiled_heir": (
                    "The underground ruins contain records of every major noble lineage "
                    "in the region — Ardhen Voss catalogued them before the mutation "
                    "advanced. The Ashen Monarch knows which bloodlines connect to the "
                    "ruins' original builders. If the player's lineage is among them, "
                    "the Monarch offers access to this archive as a negotiating position."
                ),
                "street_ghost": (
                    "The undercity network overlaps with the Ashen Monarch's tunnel "
                    "system, and a fragile non-aggression compact between the two has "
                    "held for years. A street ghost player is inside that compact. "
                    "The Monarch will honor it — but tests whether the player knows "
                    "the compact exists."
                ),
                "wandering_monk": (
                    "Ancient monk sealing traditions partially contain the energy the "
                    "Ashen Monarch is struggling to manage. He knows this. He respects "
                    "— and fears — anyone who knows how to use those seals correctly. "
                    "A wandering monk player who demonstrates seal knowledge creates "
                    "a pause in the Monarch's advance that can be extended into "
                    "a negotiation."
                ),
                "nonlethal_path": (
                    "Ardhen Voss's original mission was to help, not harm. The Ashen "
                    "Monarch retains some memory of that intent. A player who approaches "
                    "with nonlethal methodology and demonstrates understanding of the "
                    "mutation process may reach the remnant of Ardhen Voss beneath "
                    "the sovereign."
                ),
                "rogue_path": (
                    "He views rogue players as potential salvage operatives — people "
                    "willing to work in the Hollow without institutional oversight. He "
                    "offers a territorial arrangement: the player operates freely in "
                    "the outer tunnels in exchange for not interfering with the "
                    "deeper chambers."
                ),
                "heroic_path": (
                    "He has heard heroic reputation before. The institute that ordered "
                    "the site sealed had an excellent reputation. He tests whether "
                    "the player's heroism extends to accepting uncomfortable truths "
                    "about what the forbidden power source actually is."
                ),
            },
        ),
    ]


def _seed_villain_behavior_rules() -> Dict[str, Dict[VillainStance, str]]:
    behavior_rules: Dict[str, Dict[VillainStance, str]] = {
        "Kage Renda": {
            VillainStance.AGGRESSIVE: "Rushes with relentless sword pressure and trap counters.",
            VillainStance.BALANCED: "Alternates measured strikes with defensive feints.",
            VillainStance.PASSIVE: "Maintains distance and probes for diplomatic openings.",
        },
        "General Voln": {
            VillainStance.AGGRESSIVE: "Calls reinforcements and overwhelms lanes with heavy assaults.",
            VillainStance.BALANCED: "Controls space and rotates formations around choke points.",
            VillainStance.PASSIVE: "Commits to shield walls, preferring containment over eliminations.",
        },
        "Admiral Neris": {
            VillainStance.AGGRESSIVE: "Presses tide-form attacks in rapid, high-risk sequences.",
            VillainStance.BALANCED: "Keeps tempo steady with spacing and terrain control.",
            VillainStance.PASSIVE: "Seeks negotiation windows while guarding key positions.",
        },
        "Zephyr Tyrant": {
            VillainStance.AGGRESSIVE: "Unleashes storm sequences with aerial pressure and no mercy.",
            VillainStance.BALANCED: "Reads wind patterns and counters exploitable approaches.",
            VillainStance.PASSIVE: "Withdraws to high ground and demands tribute before engaging.",
        },
        "Ashen Monarch": {
            VillainStance.AGGRESSIVE: "Collapses the ground and traps targets in rubble ambushes.",
            VillainStance.BALANCED: "Controls underground terrain and punishes surface movement.",
            VillainStance.PASSIVE: "Seals tunnels and tests the intruder's resolve with riddles.",
        },
    }
    for villain in _seed_villains():
        if villain.name in behavior_rules:
            continue
        behavior_rules[villain.name] = {
            VillainStance.AGGRESSIVE: (
                f"{villain.name} chains {villain.skinned_move_names.get('attack_skin', 'attack')} "
                f"into {villain.signature_power.name} with relentless pressure."
            ),
            VillainStance.BALANCED: (
                f"{villain.name} rotates {villain.skinned_move_names.get('defense_skin', 'defense')} "
                f"and {villain.skinned_move_names.get('link_skin', 'link')} before committing."
            ),
            VillainStance.PASSIVE: (
                f"{villain.name} repositions with {villain.skinned_move_names.get('escape_skin', 'escape')} "
                "and waits for negotiation openings."
            ),
        }
    return behavior_rules


def _seed_trophy_catalog() -> Dict[str, Trophy]:
    trophies = [
        Trophy(
            TROPHY_FIRST_STRIKE,
            "First Strike",
            "Defeat an enemy lethally for the first time.",
            TrophyCategory.COMBAT,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_GHOST_STEP,
            "Ghost Step",
            "Complete three encounters through stealth.",
            TrophyCategory.STEALTH,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_SILVER_TONGUE,
            "Silver Tongue",
            "Resolve three encounters through charm.",
            TrophyCategory.SOCIAL,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_WINDWALK_SURVIVOR,
            "Windwalk Survivor",
            "Escape danger through evasion three times.",
            TrophyCategory.STEALTH,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_VEIL_MASTER,
            "Veil Master",
            "Complete five encounters through stealth.",
            TrophyCategory.STEALTH,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_DIPLOMAT_SUPREME,
            "Diplomat Supreme",
            "Resolve five encounters through charm.",
            TrophyCategory.SOCIAL,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_PACIFIST_SHADOW,
            "Pacifist Shadow",
            "Maintain a kill-free run while using charm, stealth, and evasion tactics.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_SILENT_LEGEND,
            "Silent Legend",
            "Clear every seeded region in a kill-free run.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_PHANTOM_VEIL,
            "Phantom Veil",
            "Complete eight encounters through stealth.",
            TrophyCategory.STEALTH,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_HARMONY_VOICE,
            "Harmony Voice",
            "Resolve eight encounters through charm.",
            TrophyCategory.SOCIAL,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_UNTOUCHABLE_GHOST,
            "Untouchable Ghost",
            "Escape danger through evasion five times.",
            TrophyCategory.STEALTH,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_TRINITY_OPERATOR,
            "Trinity Operator",
            "Use charm, stealth, and evasion at least twice each without any kills.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_ORIGIN_AWAKENED,
            "Origin Awakened",
            "Choose a protagonist backstory and set your narrative path.",
            TrophyCategory.PROGRESSION,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_FIRST_BLOODLINE_VICTORY,
            "First Bloodline Victory",
            "Clear your first region and claim a boss reward.",
            TrophyCategory.PROGRESSION,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_WORLD_WALKER,
            "World Walker",
            "Clear every seeded region in the current world.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_ROGUE_ASCENDANT,
            "Rogue Ascendant",
            "Reach Rogue reputation tier.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_HEROIC_CREST,
            "Heroic Crest",
            "Reach Heroic reputation tier.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_PEACEKEEPER_EMBLEM,
            "Peacekeeper Emblem",
            "Reach Heroic status while resolving at least three encounters through charm.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_MERCY_CROWN,
            "Mercy Crown",
            "Complete every seeded quest in a kill-free run.",
            TrophyCategory.ALIGNMENT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_BATTLE_HARDENED,
            "Battle Hardened",
            "Defeat five enemies in lethal combat.",
            TrophyCategory.COMBAT,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_WAR_VETERAN,
            "War Veteran",
            "Defeat twenty enemies in lethal combat.",
            TrophyCategory.COMBAT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_CRIMSON_REAPER,
            "Crimson Reaper",
            "Defeat thirty-five enemies in lethal combat.",
            TrophyCategory.COMBAT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_APEX_PREDATOR,
            "Apex Predator",
            "Defeat fifty enemies in lethal combat.",
            TrophyCategory.COMBAT,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_RISING_NINJA,
            "Rising Ninja",
            "Reach level 5.",
            TrophyCategory.PROGRESSION,
            TrophyTier.EARLY,
        ),
        Trophy(
            TROPHY_SEASONED_NINJA,
            "Seasoned Ninja",
            "Reach level 10.",
            TrophyCategory.PROGRESSION,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_LOYAL_BONDS,
            "Loyal Bonds",
            "Build high loyalty with three or more allies.",
            TrophyCategory.SOCIAL,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_VILLAIN_SLAYER,
            "Villain Slayer",
            "Defeat every red-bar villain in the world.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_QUESTMASTER,
            "Questmaster",
            "Complete every seeded quest.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_SHADOW_HEIR,
            "Shadow Heir",
            "Clear every region as the Exiled Heir.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_GHOST_SOVEREIGN,
            "Ghost Sovereign",
            "Clear every region as the Street Ghost.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_MONK_ASCENDANT,
            "Monk Ascendant",
            "Clear every region as the Wandering Monk.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        # Stance evolution mastery trophies (Issue 2)
        Trophy(
            TROPHY_PACIFIER,
            "Pacifier",
            "Drive at least two villains to PASSIVE stance through charm, mercy, and diplomacy.",
            TrophyCategory.SOCIAL,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_TERROR,
            "Terror",
            "Drive at least two villains to AGGRESSIVE stance through lethal and betrayal actions.",
            TrophyCategory.COMBAT,
            TrophyTier.MID,
        ),
        Trophy(
            TROPHY_STANCE_BREAKER,
            "Stance Breaker",
            "Force at least three different villains through multiple stance transitions in a single run.",
            TrophyCategory.PROGRESSION,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_SHADOW_WHISPERER,
            "Shadow Whisperer",
            "Complete a kill-free run while achieving ten stealth encounter outcomes.",
            TrophyCategory.STEALTH,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_SILVER_MASK,
            "Silver Mask",
            "Complete a kill-free run while achieving ten charm encounter outcomes.",
            TrophyCategory.SOCIAL,
            TrophyTier.LATE,
        ),
        Trophy(
            TROPHY_WIND_DANCER,
            "Wind Dancer",
            "Complete a kill-free run while achieving eight evasion encounter outcomes.",
            TrophyCategory.STEALTH,
            TrophyTier.LATE,
        ),
    ]
    return {trophy.key: trophy for trophy in trophies}


def _seed_shop_inventory() -> Dict[str, Dict[str, Any]]:
    return {
        "market_smoke_bomb": {
            "name": "Market Smoke Bomb",
            "reward_type": "move",
            "reward_name": "Smoke Lattice",
            "price": 40,
            "min_reputation": -49,
            "max_reputation": 1000,
            "requires_black_market": False,
            "shop_tags": ("cosmetics", "ninja_tools"),
        },
        "rogue_shadow_wrap": {
            "name": "Rogue Shadow Wrap",
            "reward_type": "clothing",
            "reward_name": "Shadow Wrap",
            "price": 70,
            "min_reputation": -1000,
            "max_reputation": -20,
            "requires_black_market": True,
            "shop_tags": ("cosmetics",),
        },
        "black_market_kunai": {
            "name": "Black Market Kunai",
            "reward_type": "weapon",
            "reward_name": "Nightglass Kunai",
            "price": 90,
            "min_reputation": -1000,
            "max_reputation": 1000,
            "requires_black_market": True,
            "shop_tags": ("ninja_tools",),
        },
        "pacifist_thread_charm": {
            "name": "Pacifist Thread Charm",
            "reward_type": "move",
            "reward_name": "Mercy Knot",
            "price": 75,
            "min_reputation": -1000,
            "max_reputation": 1000,
            "requires_black_market": False,
            "requires_nonlethal": True,
            "shop_tags": ("move_sets", "cosmetics"),
        },
        "silent_legend_insignia": {
            "name": "Silent Legend Insignia",
            "reward_type": "clothing",
            "reward_name": "Moonveil Crest",
            "price": 120,
            "min_reputation": -1000,
            "max_reputation": 1000,
            "requires_black_market": False,
            "requires_nonlethal": True,
            "min_nonlethal_actions": 8,
            "requires_world_clear_nonlethal": True,
            "shop_tags": ("cosmetics",),
        },
        "gatebreaker_smoke_map": {
            "name": "Gatebreaker Smoke Map",
            "reward_type": "move",
            "reward_name": "Gatebreaker Veil",
            "price": 95,
            "min_reputation": -1000,
            "max_reputation": -20,
            "requires_black_market": True,
            "required_quests": ("Q3",),
            "shop_tags": ("move_sets",),
        },
        "tideglass_truce_wire": {
            "name": "Tideglass Truce Wire",
            "reward_type": "weapon",
            "reward_name": "Truce Wire Kunai",
            "price": 115,
            "min_reputation": -1000,
            "max_reputation": -10,
            "requires_black_market": True,
            "required_quests": ("Q5",),
            "shop_tags": ("ninja_tools",),
        },
        "moonwell_ledger_cloak": {
            "name": "Moonwell Ledger Cloak",
            "reward_type": "clothing",
            "reward_name": "Ledgerbound Cloak",
            "price": 135,
            "min_reputation": -1000,
            "max_reputation": 1000,
            "requires_black_market": True,
            "required_quests": ("Q7",),
            "shop_tags": ("cosmetics",),
        },
        "eternal_watch_decoy": {
            "name": "Eternal Watch Decoy",
            "reward_type": "move",
            "reward_name": "Eternal Mirage",
            "price": 160,
            "min_reputation": -1000,
            "max_reputation": 1000,
            "requires_black_market": True,
            "required_quests": ("Q10",),
            "requires_nonlethal": True,
            "shop_tags": ("move_sets",),
        },
        "smuggler_regent_wraps": {
            "name": "Smuggler Regent Wraps",
            "reward_type": "clothing",
            "reward_name": "Regent Shadow Wraps",
            "price": 185,
            "min_reputation": -1000,
            "max_reputation": -40,
            "requires_black_market": True,
            "required_quests": ("Q12",),
            "shop_tags": ("cosmetics", "ninja_tools"),
        },
        "wayfarer_anchor": {
            "name": "Wayfarer Anchor",
            "reward_type": "tool",
            "reward_name": MOBILE_FAST_TRAVEL_TOOL_NAME,
            "price": 140,
            "min_reputation": -1000,
            "max_reputation": 1000,
            "requires_black_market": False,
            "required_quests": ("Q4",),
            "shop_tags": ("ninja_tools", "mobility"),
        },
    }


def build_mvp_world(player_name: str, affinity_decisions: Sequence[int]) -> Tuple[NinjaWorld, PlayerProfile]:
    """Build the MVP world and player state.

    ``affinity_decisions`` is an integer sequence from the affinity mini-game;
    values are accumulated and mapped cyclically to Fire, Water, Earth, Wind.
    The top score determines the starting affinity.
    """
    from ._world import NinjaWorld

    affinity = resolve_affinity_minigame(affinity_decisions)
    player = PlayerProfile(name=player_name, affinity=affinity)
    regions = _seed_regions()
    _validate_boss_move_reward_config(regions)

    for move_set, moves in _seed_moves(affinity).items():
        for move in moves:
            player.add_move(move, allow_cross_affinity=True)

    world = NinjaWorld(
        regions=regions,
        quests=_seed_quests(),
        allies=_seed_allies(),
        weapons=_seed_weapons(),
        skins=[
            Skin("Founder's Garb", {"power": 2, "focus": 1}),
            Skin("Rogue Nightwear", {"agility": 3}),
        ],
        villains=_seed_villains(),
        villain_behavior_rules=_seed_villain_behavior_rules(),
        player_backstories=_seed_player_backstories(),
        trophy_catalog=_seed_trophy_catalog(),
        arcs=_seed_arcs(),
        era_timeline=_seed_era_timeline(),
        technique_library=_seed_technique_library(),
        shop_inventory=_seed_shop_inventory(),
        city_shops=_seed_city_shops(),
        city_npcs=_seed_city_npcs(),
    )
    player.weapons.extend(world.weapons)
    player.unlocked_skins.append(world.skins[0])
    player.initialize_quest_log([quest.quest_id for quest in world.quests])
    for ally in world.allies:
        player.ally_loyalty[ally] = 0
    world._refresh_arc_and_era()
    world._schedule_dynamic_regions(player)
    world._log_tapestry(
        event_type="arc_shift",
        label="Run initialized with opening political arc.",
        causes=["new_run"],
        effects={
            "scheduled_regions": list(world.dynamic_region_chain),
            "era": world._current_era()["key"],
        },
    )
    return world, player
