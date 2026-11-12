---
name: om3d-asset-prep
description: Prepare game props in Blender for baking and export, covering naming, scene checks, low and high poly bake pairs, and FBX export presets for Substance Painter, Marmoset and Unreal. Use when the user asks to clean up a scene, check names, set up a bake, match lows to highs, or batch export assets.
---

# OM3D Asset Prep

Get a game prop from "modeling is done" to "ready to bake and export" without the tedious clicking. Check the scene, fix what is safe to fix, set up bake pairs, and export with the right settings for each target app.

## Naming convention

The default convention. Ask the artist if their studio uses a different one, then follow theirs.

- Low poly: `SM_<Asset>_<Part>_low`
- High poly: `SM_<Asset>_<Part>_high`, with an optional tag for extra highs: `SM_<Asset>_<Part>_high_Bolts`
- `<Part>` is one token in PascalCase (`Lens`, `ScaleViewfinder`, `Part01`). It is optional for single-part assets.
- Unreal collision (`UCX_`, `UBX_`, `USP_`, `UCP_`) keeps Unreal's own names.
- No Blender duplicate suffixes (`.001`) and no default names (`Cube`, `Cylinder.012`) in anything that gets exported.

Bakers pair meshes by these names, so naming comes first and everything else keys off it.

## Scene checks

Run `scripts/scene_check.py` (read only) through Blender MCP. It reports, per object:

| Check | Severity | Safe automatic fix |
|---|---|---|
| Negative or unapplied scale, unapplied rotation | Error / warning | Apply rotation and scale |
| No UV map, more than one UV map | Error / warning | None, ask |
| Non-manifold edges | Error | None, ask |
| Collapsed (zero area) faces | Error | Delete them |
| N-gons | Warning | Triangulate them |
| Loose verts and edges | Warning | Delete them |
| Duplicate verts | Warning | Merge by distance (tolerance scaled to mesh size) |
| Name doesn't match the convention, `.001` suffix | Warning | Rename, after the artist approves the list |
| Empty material slots | Warning | Remove them |

Show the report first. Fix only what the artist agrees to, all in one go, and say what changed.

## Bake setup

1. **Find pairs.** Group lows and highs by `<Asset>_<Part>`. List lows with no high, highs with no low, and meshes not named for baking.
2. **If the highs have default names**, match each high to the low its surface sits closest to (sample the high's verts, measure distance to each low). Flag close calls where the runner-up is nearly as close, and show the full rename list before renaming anything.
3. **Check each pair:** the low has UVs, no unintended overlapping UVs inside one material, the high covers the low, and transforms match.
4. **Explode** if the baker doesn't support name matching: move each pair apart along one axis with clear gaps so rays can't hit a neighbor. Keep the offsets so the layout can be put back.
5. **Hard edges need UV seams** on the low (see the om3d-uv skill). This is the most common cause of bake seams.
6. **The low has to match the high's silhouette.** If the low was optimized too far, the bake breaks (see the om3d-topology skill).
7. **Texture sets come from materials.** Substance Painter makes one texture set per material, so check every low has the material for its set (`M_tex_set_<name>`), and that each set's objects sit in their own numbered collection (`1_tex_set_<name>`).

## Export presets

Export copies, never the artist's objects. Apply modifiers on the copy, bake in the transform, and leave the scene exactly as it was.

| Target | Axes | Files | Notes |
|---|---|---|---|
| Unreal | -Y forward, Z up | `SM_<Asset>.fbx` | Drop `_low` from names, keep `UCX_` collision matched, LODs as `SM_<Asset>_LODn` |
| Substance Painter | Y forward, Z up | `SM_<Asset>_low.fbx`, `SM_<Asset>_high.fbx` | Triangulate the low so the bake matches the engine |
| Marmoset Toolbag | Y forward, Z up | Same as Painter | Same |

Pivot defaults to bottom center of each asset. Put each asset in its own folder, and do a dry run first that lists every file, mesh and triangle count.

## Rules when driving Blender

- Save before any fix. Scripted edits through MCP do not always make an undo step.
- Do heavy or risky tests in a separate Blender instance (`blender --background file.blend --python script.py`), never in the artist's open session.
- Scale tolerances with mesh size. A fixed 0.0001 merge distance will weld tiny screws together.

## Files

- `scripts/scene_check.py`: read-only scene report for selected (or all visible) meshes, printed as JSON. The naming rules are at the top of the script.
