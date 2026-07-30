from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from .core import Affinity, Move, MoveCategory, _seed_ninjutsu_library, _seed_regions, _seed_villains

_AFFINITY_ROTATION: Tuple[Affinity, ...] = (
    Affinity.FIRE,
    Affinity.WATER,
    Affinity.EARTH,
    Affinity.WIND,
)

_SKILL_FRAMES: Dict[MoveCategory, Tuple[Tuple[str, str], ...]] = {
    MoveCategory.ESCAPE: (
        ("Lantern Skip", "Leaves a hovering paper lantern decoy that pulls ranged fire off your trail."),
        ("Rivulet Slide", "Turns puddles into a low-profile slide that lets the user pass under sweep attacks."),
        ("Stone Latch Drop", "Pins chakra to a wall so the user can fall straight down and reappear on a lower ledge."),
        ("Kite String Vanish", "Anchors chakra thread to rooftops and swings the user out of sight in a single arc."),
        ("Cinder Sleeve Shed", "Drops a burning cloak fragment that keeps moving like a false body double."),
        ("Mirror Brook Step", "Bounces the user through reflective water surfaces for a blindside exit."),
        ("Terrace Burrow", "Creates a shallow earth trench that protects the first step of a retreat."),
        ("Whistling Banner Roll", "Wraps the user in a snapping banner gust that masks footwork timing."),
        ("Ash Petal Reversal", "Bursts into harmless ash petals before reforming on the opposite side of pressure."),
        ("Undercurrent Coil", "Lets the user hook an ally or object and slingshot both out of a collapse zone."),
        ("Rootline Pivot", "Splits the ground into narrow rails so the user can pivot around charging enemies."),
        ("Skylark Exit", "Uses an updraft to convert a dodge into a brief aerial reposition."),
        ("Bonfire Hollow Trace", "Marks the user's last safe tile with embers, then snaps back to it once."),
    ),
    MoveCategory.ATTACK: (
        ("Scorch Reed Thrust", "Pierces guard gaps with a reed-thin flame lance that rewards precision spacing."),
        ("Harborline Cut", "Draws a crescent of pressurized water that keeps momentum after the initial hit."),
        ("Fault Pulse Knuckle", "Turns a short punch into a localized shock that rattles armor seams."),
        ("Zephyr Hookline", "Curves a wind slash around shields so the second half of the strike lands from the side."),
        ("Coalbrand Scatter", "Splits an ember volley into smaller follow-up needles after the first impact."),
        ("Floodglass Heel", "Kicks a slick water plane forward to juggle enemies who lose footing."),
        ("Bastion Break Palm", "Condenses earth chakra into the palm to rupture barriers without large knockback."),
        ("Mourning Kite Slice", "Throws a high singing blade of wind that reveals cloaked enemies in its wake."),
        ("Kiln Chain Jab", "Links short-range strikes so each confirmed hit reheats the next one."),
        ("Blue Current Drill", "Bores through a target line and leaves a wake that speeds ally follow-ups."),
        ("Quarry Tooth Rush", "Raises staggered stone teeth that herd enemies into a preferred lane."),
        ("Tempest Needle Choir", "Surrounds the target with thin wind needles that arrive a heartbeat apart."),
        ("Phoenix Ink Burst", "Brands the target with flaming calligraphy that pops when they cast."),
    ),
    MoveCategory.DEFENSE: (
        ("Ember Crest Ward", "Creates a warm crest that softens projectiles and powers up the next parry."),
        ("Breakwater Frame", "Stacks water panes into a flexible wall that absorbs multi-hit pressure."),
        ("Ancestor Cairn", "Raises a short earth shrine that blocks lanes and anchors nearby allies."),
        ("Hollow Gale Screen", "Spins crosswinds into a translucent curtain that bends arrows off angle."),
        ("Char Seal Mantle", "Burns incoming poison or curse effects off the user's cloak edge."),
        ("Tideglass Rebuttal", "Stores a portion of blocked force and releases it as a ripple on command."),
        ("Citadel Grip", "Roots the user's stance so displacement effects lose most of their push."),
        ("Songbird Aegis", "Turns defensive motions into soft wind notes that disrupt enemy casting rhythm."),
        ("Firefly Rampart", "Spawns a ring of ember motes that intercept chip damage one hit at a time."),
        ("Stillwater Latch", "Calms the area around the user and shortens hostile status durations."),
        ("Terracotta Relay", "Passes a fraction of blocked damage into the ground instead of the body."),
        ("Monsoon Halo", "Builds a rotating wind halo that makes the next dodge safer after guarding."),
        ("Kiln Mirror Plate", "Hardens heat into a glossy plate that flashes attackers with reflected light."),
    ),
    MoveCategory.SUMMON: (
        ("Ash Ferret Pact", "Summons a tunnel-running ferret that tags escape routes and steals pickups."),
        ("Lagoon Crane Pact", "Calls a crane that paints healing currents where it lands."),
        ("Boulder Ox Pact", "Brings in a heavy ox that can body-block choke points for the team."),
        ("Tempest Moth Pact", "Releases a luminous moth swarm that marks enemies for aerial combos."),
        ("Cinder Boar Pact", "Charges a boar avatar through traps so the player can follow safely."),
        ("Mirror Carp Pact", "Creates a koi familiar that duplicates the user's next support jutsu."),
        ("Moss Rhino Pact", "Plants a rhino guardian that grants cover while slowly pushing forward."),
        ("Needle Falcon Pact", "Summons a falcon that peels back fog, smoke, and invisibility."),
        ("Forge Hound Pact", "Conjures a furnace hound that heats allied weapons for bonus break power."),
        ("Abyss Lamprey Pact", "Latches onto a target to drain momentum and feed it to the summoner."),
        ("Granite Cicada Pact", "Creates a cicada shell that can be detonated into a brief stone stun."),
        ("Cloud Fox Pact", "Calls a fox spirit that misdirects enemy lock-on until struck."),
        ("Sunveil Lynx Pact", "Lets a lynx familiar scout ahead and pounce when the player enters combat."),
    ),
}

_ULTIMATE_FRAMES: Tuple[Tuple[str, str], ...] = (
    ("Starforge Cataclysm", "Turns stored heat into a descending meteor wheel that rewrites the center of the arena."),
    ("Moonwell Dominion", "Floods the stage with reflective water that duplicates every dash trail for a full combo string."),
    ("Worldspine Uprising", "Raises a ring of earth spires that trap the battlefield inside a shifting maze."),
    ("Heavenwire Judgment", "Braids storm lines between enemies so every movement triggers a cutting lightning wind lash."),
    ("Pyrewake Leviathan", "Summons a fire-serpent tide that surges forward, then crashes back for a second hit."),
    ("Monolith Tempest", "Spins mountain fragments inside a cyclone to create a roaming damage wall."),
    ("Abyss Bloom Reckoning", "Detonates a lotus of deep-water pressure that silences the impact zone."),
    ("Crown of the Four Veils", "Wraps the caster in rotating elemental layers that each answer a different threat."),
    ("Dawnbreak Ravine", "Splits the arena with a glowing trench that buffs allies and punishes pursuers."),
    ("Stormglass Burial", "Drops a prism rain that freezes targets in visible trajectories before shattering them free."),
    ("Furnace Choir Ascension", "Converts every active burn stack on the field into a synchronized blast wave."),
    ("Kingfisher Zero", "Collapses all nearby water markers into a single pierce line with instant reposition afterward."),
    ("Titan Root Verdict", "Judges the arena with chained roots that decide between pinning, lifting, or crushing based on target state."),
    ("Horizon Sever Anthem", "Sings a wide wind blade across the full map and leaves a glide path behind it."),
    ("Red Lantern Eclipse", "Darkens the arena under burning lanterns that reveal hidden enemies and explode in sequence."),
    ("Deep Current Tribunal", "Creates rotating courts of water that drag opponents through repeated sentencing hits."),
    ("Obsidian Mercy Collapse", "Slams a black glass dome down, then chooses to imprison, blast back, or spare survivors."),
    ("Skyrift Orchestra", "Commands layered air currents like instruments so each ally input spawns a matching follow-up strike."),
    ("Solar Torrent Mandate", "Rains heated water spears that stick in the field and erupt when crossed."),
    ("Gravebloom Citadel", "Builds a living fortress of stone and roots around the caster for a slow advancing siege."),
    ("Mirage Tyrant Procession", "Marches blazing afterimages across the lane until the real caster erupts from one."),
    ("Blue Abyss Coronation", "Crowns the target area with a pressure halo that amplifies every chill or drench effect."),
    ("Earthshaker Covenant", "Invokes ancient seals that crack armor, floors, and enemy confidence at once."),
    ("Thunderleaf Exodus", "Launches the team on windrails while detonating their abandoned positions in rapid sequence."),
    ("Sunken Throne Awakening", "Raises a drowned palace under foes and lets its pillars hit in custom order."),
    ("Ember Scripture Ruin", "Writes a field-wide fire seal whose final character ignites only after opponents commit."),
    ("Bastion of Falling Stars", "Calls down clustered star fragments that orbit a central stone anchor before exploding."),
    ("Cyclone Funeral Rite", "Carries enemies skyward in silence and returns them with brutal synchronized crash timing."),
    ("Tidal Glass Guillotine", "Forms giant water mirrors that close like blades from every side of the stage."),
    ("Volcanic Parish", "Builds a burning sanctum where allied summons become larger and hostile healing fails."),
    ("Pale Reef Omen", "Summons spectral reef towers that project zones of slow, fear, and delayed burst."),
    ("Rootstorm Inheritance", "Lets the caster pass their active buffs through a tree-network shockwave to the whole team."),
    ("Aurora Fang Deluge", "Fills the sky with luminous bite-shaped projectiles that home on status-marked targets."),
    ("Black Sand Testament", "Sifts the ground into razor sand, then engraves enemy positions for repeated eruptions."),
    ("Phoenix Tide Concord", "Merges revival fire with water momentum so a defeated ally can return inside the wave."),
    ("Sovereign Wind Labyrinth", "Redraws the battlefield into floating corridors only the caster can navigate cleanly."),
    ("Basalt Moon Catastrophe", "Drops a moonlike basalt mass that cracks into pursuit boulders on impact."),
    ("Celestial Undertow Archive", "Records every motion in the arena, then plays them back as drowning afterimages."),
)

_HERO_COSMETICS: Tuple[Dict[str, str], ...] = (
    {
        "concept": "Leaf Vanguard",
        "alignment": "heroic",
        "palette": "jade, cream, tempered steel",
        "silhouette": "split shoulder guards, travel scarf, wrapped forearms",
        "materials": "matte cloth, lacquered leather, brushed metal",
        "fx": "clean affinity glow along hems and seals",
    },
    {
        "concept": "River Envoy",
        "alignment": "heroic",
        "palette": "indigo, pearl, sea-glass cyan",
        "silhouette": "long coat panels, rope sash, soft shin guards",
        "materials": "layered silk, sharkskin trim, polished shell",
        "fx": "waterline refractions and drifting droplets",
    },
    {
        "concept": "Stone Warden",
        "alignment": "heroic",
        "palette": "ochre, slate, cedar brown",
        "silhouette": "broad chest wrap, shrine belt, plated boots",
        "materials": "woven canvas, carved stone beads, heavy hide",
        "fx": "dust puffs and seal-etched glow cracks",
    },
    {
        "concept": "Sky Courier",
        "alignment": "heroic",
        "palette": "white, cobalt, silver mist",
        "silhouette": "high collar cape, narrow greaves, feathered tailcloth",
        "materials": "ripstop cloth, corded silk, lightweight metal",
        "fx": "wind ribbons and luminous motion trails",
    },
)

_VILLAIN_COSMETICS: Tuple[Dict[str, str], ...] = (
    {
        "concept": "Ash Regent",
        "alignment": "villain",
        "palette": "charcoal, ember orange, antique brass",
        "silhouette": "torn royal coat, hooked pauldrons, mask crown",
        "materials": "burned velvet, chain lattice, scorched gold leaf",
        "fx": "smoke leaks from seam lines and cracked sigils",
    },
    {
        "concept": "Drowned Judge",
        "alignment": "villain",
        "palette": "midnight blue, algae green, pallid bone",
        "silhouette": "ceremonial robe with weighted hems and shell collar",
        "materials": "sodden silk, coral plating, pearl lacquer",
        "fx": "constant drip trails and pressure-ripple halos",
    },
    {
        "concept": "Grave Mason",
        "alignment": "villain",
        "palette": "black clay, rust red, granite gray",
        "silhouette": "heavy apron armor, tomb-ring belt, broad gauntlets",
        "materials": "stone tile plates, iron hooks, ash canvas",
        "fx": "falling grit, fault-line glow, seismic pulses",
    },
    {
        "concept": "Storm Widow",
        "alignment": "villain",
        "palette": "violet, smoke black, moonlit teal",
        "silhouette": "needle limbs, veil train, blade-fan sleeves",
        "materials": "oiled silk, mirror glass, razor wire trim",
        "fx": "flickering silhouettes and whispering gust echoes",
    },
)

_CHARACTER_RENDER_BRIEF: Dict[str, Any] = {
    "heroes": {
        "body_language": "Grounded stances, readable hand signs, and confident forward-lean silhouettes.",
        "face_direction": "Visible eyes, calm brows, and clan markings kept symmetrical for trustworthiness.",
        "material_language": "Natural fabrics, repaired armor, and polished metal accents that show discipline.",
    },
    "villains": {
        "body_language": "Asymmetrical silhouettes, off-axis posture, and delayed idle motions that feel predatory.",
        "face_direction": "Masks, veils, or shadowed brows that obscure intent until the final animation beat.",
        "material_language": "Gloss-black surfaces, damaged ceremony pieces, and aggressive trim that catches the light.",
    },
}

_REGION_RENDER_BRIEFS: Dict[str, Dict[str, Any]] = {
    "Verdant Gate": {
        "palette": "moss green, shrine red, weathered cedar",
        "landmarks": ["broken torii ridge", "wind-cut watchtowers", "lantern rice terraces"],
        "look": "A defensive woodland frontier where sacred architecture has been converted into tactical chokepoints.",
    },
    "Ashen Cradle": {
        "palette": "volcanic black, furnace orange, smoke gray",
        "landmarks": ["hanging slag bridges", "bellows docks", "ember shrine kilnfields"],
        "look": "An industrial fire basin where clan foundries and siege camps have fused into one red horizon.",
    },
    "Tideglass Basin": {
        "palette": "sea-glass blue, pearl white, storm teal",
        "landmarks": ["flooded causeways", "mirror marsh piers", "spiral lighthouse ruins"],
        "look": "A drowned trade basin built around reflective water shelves and storm-scarred naval ruins.",
    },
}


def _affinity_effect_text(affinity: Affinity, category: MoveCategory) -> str:
    effect_map = {
        MoveCategory.ESCAPE: {
            Affinity.FIRE: "heat haze concealment",
            Affinity.WATER: "slipstream repositioning",
            Affinity.EARTH: "terrain-assisted evasion",
            Affinity.WIND: "air-lift redirection",
        },
        MoveCategory.ATTACK: {
            Affinity.FIRE: "burst damage with burn pressure",
            Affinity.WATER: "flowing line damage with setup control",
            Affinity.EARTH: "guard break and heavy stagger",
            Affinity.WIND: "angle-changing cuts and reveal utility",
        },
        MoveCategory.DEFENSE: {
            Affinity.FIRE: "status cleansing guard frames",
            Affinity.WATER: "flexible barrier absorption",
            Affinity.EARTH: "anchored mitigation and cover",
            Affinity.WIND: "projectile deflection and parry support",
        },
        MoveCategory.SUMMON: {
            Affinity.FIRE: "aggressive pursuit support",
            Affinity.WATER: "healing or control support",
            Affinity.EARTH: "frontline body-block support",
            Affinity.WIND: "vision and tracking support",
        },
        MoveCategory.ULTIMATE: {},
    }
    return effect_map[category][affinity]



def _category_ability_text(category: MoveCategory) -> str:
    return {
        MoveCategory.ESCAPE: "Creates a disengage window while preserving combo tempo.",
        MoveCategory.ATTACK: "Starts or extends pressure strings with a category-specific payoff.",
        MoveCategory.DEFENSE: "Turns a guard beat into board control instead of pure damage denial.",
        MoveCategory.SUMMON: "Adds a second body or hazard that changes battlefield routing.",
        MoveCategory.ULTIMATE: "Delivers a finisher-level arena rewrite with strong identity.",
    }[category]



def _move_to_brainstorm_entry(move: Move) -> Dict[str, Any]:
    return {
        "name": move.name,
        "category": move.category.value,
        "affinity": [affinity.value for affinity in move.affinities],
        "effect": ", ".join(effect.value for effect in move.status_effects) or "raw utility",
        "ability": move.jutsu_type.value,
        "unique_hook": "seeded shared move pool",
        "origin": "seeded",
    }



def _build_new_skill_entries() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for category in (
        MoveCategory.ESCAPE,
        MoveCategory.ATTACK,
        MoveCategory.DEFENSE,
        MoveCategory.SUMMON,
    ):
        for index, (name, unique_hook) in enumerate(_SKILL_FRAMES[category]):
            affinity = _AFFINITY_ROTATION[index % len(_AFFINITY_ROTATION)]
            entries.append(
                {
                    "name": name,
                    "category": category.value,
                    "affinity": [affinity.value],
                    "effect": _affinity_effect_text(affinity, category),
                    "ability": _category_ability_text(category),
                    "unique_hook": unique_hook,
                    "origin": "brainstorm",
                }
            )
    return entries



def _build_new_ultimate_entries() -> List[Dict[str, Any]]:
    pair_cycle: Tuple[Tuple[Affinity, Affinity], ...] = (
        (Affinity.FIRE, Affinity.WIND),
        (Affinity.WATER, Affinity.EARTH),
        (Affinity.FIRE, Affinity.WATER),
        (Affinity.EARTH, Affinity.WIND),
        (Affinity.FIRE, Affinity.EARTH),
        (Affinity.WATER, Affinity.WIND),
    )
    entries: List[Dict[str, Any]] = []
    for index, (name, unique_hook) in enumerate(_ULTIMATE_FRAMES):
        affinities = pair_cycle[index % len(pair_cycle)]
        entries.append(
            {
                "name": name,
                "category": MoveCategory.ULTIMATE.value,
                "affinity": [affinity.value for affinity in affinities],
                "effect": f"dual-affinity arena finisher keyed to {affinities[0].value}/{affinities[1].value}",
                "ability": _category_ability_text(MoveCategory.ULTIMATE),
                "unique_hook": unique_hook,
                "origin": "brainstorm",
            }
        )
    return entries



def _build_map_rendering() -> Dict[str, Any]:
    regions = []
    for region in _seed_regions():
        render_brief = _REGION_RENDER_BRIEFS[region.name]
        regions.append(
            {
                "name": region.name,
                "village_hub": region.village_hub,
                "boss": region.boss,
                "palette": render_brief["palette"],
                "landmarks": list(render_brief["landmarks"]),
                "look": render_brief["look"],
            }
        )
    return {
        "overview": "A triangular frontier map: forest gate in the west, furnace coast to the south, and a drowned basin to the east, all feeding back into a shifting ninja war corridor.",
        "camera_language": "Top-down travel with dramatic low-angle boss arenas and strong silhouette reads from hub rooftops.",
        "regions": regions,
    }



def _build_villain_brainstorm() -> List[Dict[str, Any]]:
    visual_hooks = {
        Affinity.FIRE: "charred cloth edges and ember seal seams",
        Affinity.WATER: "wet lacquer, shell trim, and refractive highlights",
        Affinity.EARTH: "ceramic plates, rope belts, and fault-glow cracks",
        Affinity.WIND: "split capes, feather motifs, and drifting ribbon tails",
    }
    roster = []
    for villain in _seed_villains():
        roster.append(
            {
                "name": villain.name,
                "role": villain.role,
                "affinity": villain.primary_affinity.value,
                "backstory": villain.backstory,
                "power": villain.signature_power.name,
                "ultimate_look": villain.ultimate_skin_name,
                "visual_hook": visual_hooks[villain.primary_affinity],
            }
        )
    return roster



def build_creative_brainstorm() -> Dict[str, Any]:
    """Return a structured issue #6 design packet for cosmetics, moves, and render direction."""
    seeded_moves = _seed_ninjutsu_library()
    skills = [_move_to_brainstorm_entry(move) for move in seeded_moves if move.category != MoveCategory.ULTIMATE]
    skills.extend(_build_new_skill_entries())
    ultimates = [_move_to_brainstorm_entry(move) for move in seeded_moves if move.category == MoveCategory.ULTIMATE]
    ultimates.extend(_build_new_ultimate_entries())
    compiled_moves = [*skills, *ultimates]
    return {
        "cosmetics": {
            "heroic_characters": [dict(entry) for entry in _HERO_COSMETICS],
            "villain_characters": [dict(entry) for entry in _VILLAIN_COSMETICS],
        },
        "character_rendering": dict(_CHARACTER_RENDER_BRIEF),
        "map_rendering": _build_map_rendering(),
        "skills": skills,
        "ultimates": ultimates,
        "compiled_moves": compiled_moves,
        "villains": _build_villain_brainstorm(),
    }
