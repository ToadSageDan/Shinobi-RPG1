# Assets Guide — Sourcing Art for Shinobi RPG

All code, shaders, scenes, and game logic are complete.
This guide covers how to fill in the placeholder art assets.

---

## Characters

### Free Option — Mixamo (recommended starting point)
1. Go to [mixamo.com](https://www.mixamo.com/) (free with Adobe account)
2. Download a ninja/character base mesh in **FBX for Unity** format (works in Godot too)
3. Download animations: idle, run, jump, attack (light/heavy), dodge, death, hurt
4. Import into Godot via **Import > Scenes** — use the FBX importer
5. Attach the imported `AnimationPlayer` to `scenes/characters/Player.tscn`

Animation names to map (Player.gd `_play_anim` calls):
- `idle`, `run`, `jump`, `fall`, `land`
- `dash`, `dodge`
- `wall_run_left`, `wall_run_right`, `wall_jump`, `double_jump`
- `attack_1`, `attack_2`, `attack_3`, `attack_heavy`, `attack_air`
- `hurt`, `death`
- `jutsu_charge`, `jutsu_fire`, `jutsu_fail`, `chakra_charge`
- **Boss only:** `boss_signature`, `boss_defeat_kill`, `boss_defeat_charm`,
  `boss_defeat_stealth`, `boss_defeat_evasion`

### Paid Options
- **Godot Asset Library**: search "ninja", "shinobi", "character pack"
- **Itch.io**: many free/paid CC0 character asset packs
- **KayKit** (kaylousberg.com): clean stylized packs, CC0 license

---

## Environments (Arena Terrain)

### Free Options
| Arena            | Suggested Pack                                      |
|------------------|-----------------------------------------------------|
| Verdant Gate     | [Nature Starter Kit 2](https://assetstore.unity.com) / Kenney.nl Nature Pack |
| Ashen Cradle     | Kenney.nl Dungeon Pack (recolored) / Stylized Lava tiles |
| Tideglass        | Godot Asset Library "Ocean" / Kenney.nl Pirate Pack  |
| Stormwall Ridge  | Kenney.nl Castle Pack + mountain heightmap terrain   |
| Sunken Hollow    | Dungeon/cave tile packs from itch.io (many CC0)     |

### Arena Floor Setup (Godot)
1. Import your terrain mesh as a `MeshInstance3D`
2. Add a `StaticBody3D` + `CollisionShape3D` for physics
3. Replace the placeholder flat `GroundMesh` in each `.tscn` arena scene

---

## VFX Particles

The jutsu projectile (`JutsuProjectile.gd`) uses `GPUParticles3D` nodes.
Set the `ParticlesMaterial` on the `VFX` child node with:
- **Fire jutsu**: `OrbitVelocityMin/Max` + orange `Color` gradient + `ExplosionShape`
- **Water jutsu**: blue gradient, slow `Gravity` upward, `SphereShape` emitter
- **Earth jutsu**: brown/grey `BoxShape`, heavy gravity, short lifetime
- **Wind jutsu**: white/cyan gradient, high `LinearVelocity`, zero gravity

---

## Audio

Required audio keys (referenced in `AudioManager.gd`):

### Music (looping .ogg)
| Key                    | Description                        |
|------------------------|------------------------------------|
| `music_menu`           | Title screen ambient               |
| `music_forest`         | Verdant Gate exploration            |
| `music_volcanic`       | Ashen Cradle battle                |
| `music_coastal`        | Tideglass exploration              |
| `music_alpine`         | Stormwall Ridge battle             |
| `music_cave`           | Sunken Hollow ambient              |
| `music_boss_phase2_*`  | Intensity layer for each boss      |

### SFX (.ogg or .wav)
| Key              | Description                     |
|------------------|---------------------------------|
| `hit_fire`       | Fire-affinity attack hit        |
| `hit_water`      | Water-affinity attack hit       |
| `hit_earth`      | Earth-affinity attack hit       |
| `hit_wind`       | Wind-affinity attack hit        |
| `hit_generic`    | Default hit sound               |
| `sfx_death`      | Player death sting              |
| `sfx_dodge`      | Dodge whoosh                    |
| `sfx_dash`       | Dash burst                      |
| `sfx_jutsu_fire` | Jutsu launch sound              |
| `sfx_level_up`   | Level-up fanfare                |

### Free Audio Sources
- [freesound.org](https://freesound.org) — CC0 licensed game SFX
- [opengameart.org](https://opengameart.org) — free game music
- [zapsplat.com](https://zapsplat.com) — SFX library (free tier)

---

## Registering Audio in Godot

After adding your audio files to `res://assets/audio/`, register them in your
arena's `_ready()` or in an `AudioManifest.gd` autoload:

```gdscript
AudioManager.register_streams(
    {
        "music_forest": "res://assets/audio/music/forest_theme.ogg",
        "music_boss_phase2_kage_renda": "res://assets/audio/music/boss_intense.ogg",
    },
    {
        "hit_fire": "res://assets/audio/sfx/hit_fire.wav",
        "sfx_death": "res://assets/audio/sfx/death.wav",
        # ...
    }
)
```

---

## Applying the Cel-Shading Material

1. Select a character mesh in the Godot editor
2. In the `Surface Material Override` slot, create a new `ShaderMaterial`
3. Set shader to `res://resources/shaders/cel_shading.gdshader`
4. Tune `albedo_color`, `affinity_tint`, and `affinity_tint_strength`
   to match each character's elemental theme

---

## Minimum Viable Art Pass (to get running first)

You can launch and play the game **without any art assets** using Godot's built-in
primitive meshes. The game logic, combat, and all systems are fully functional.
Replace meshes gradually as you source art.
