---
name: om3d-uv
description: Plan seams, unwrap, straighten, pack and validate UVs for game and real-time assets in Blender, including texel density in px/cm, padding, texture sets, stacking and mirroring, texture systems (trim, atlas, UDIM), lightmap channels and bake-ready UVs. Use when the user asks about UV mapping, unwrapping, seams, distortion, straightening, packing, overlapping or flipped UVs, texel density, texture sets, atlases, trim sheets, UDIMs, lightmaps, or UV problems in a bake.
---

# OM3D UV

These rules come from the OnMars3D UV Mapping Masterclass and the UV module of the Game Art Program. The aim is to make UV decisions on any asset: where to cut, how to control distortion, how much resolution to give it, and which texture system fits. Measure, flag problems and do the repetitive steps. Leave the choices that change how the texture reads to the artist.

## The five simple steps

1. **Apply Scale.** Every prep starts here. Also check normals and Face Orientation (one sided or thick), topology and modifier state. Save a backup copy before destructive steps like applying a bevel.
2. **Project from View** as a quick starting layout.
3. **Mark Seam.**
4. **Unwrap.**
5. **Pack.**

Then review: check distortion and add seams where it's high, straighten what benefits from it, and check every island with a directional checker. That's the whole workflow. Everything else builds on it.

Before packing, the layout needs a destination: which texture set, what resolution, and what the camera sees.

## Seams

- **Seams are unavoidable. Put them where they reduce distortion.**
- Start from natural seams on real-world reference: stitching and hems on clothing, parting lines where plastic shells meet, panel gaps on cars, and anywhere the material changes. A seam on a real join is one the viewer already expects. These are clues, not mandatory cuts.
- **Every sharp edge needs a UV seam.** A hard edge splits the normals, and if the UVs aren't split there too, the bake shows a line. Not every seam needs a hard edge.
- Cylinders always need a seam. Split the caps, then straighten the body.
- Characters still need seams, the face included, even with no natural seam there. Hands and gloves need the most help: the thumb and fingers need extra cuts.
- Directional textures (textile patterns, wood grain, labels) show seams far more than noise. Surfaces that get a noisy or triplanar procedural material hide seams easily, so don't spend time hiding them there.
- On deforming meshes, fewer edge segments mean more UV skewing when the mesh bends. A UV seam is not a tear in the mesh.

Fast seam selection:

- Select Sharp Edges (around 60 degrees, about 40 after a bevel), then fix the selection by hand. It depends on the threshold, so check every result.
- `Shift+G` > Select Similar (Sharpness, or Bevel) to grab matching edges.
- Select Coplanar faces, grow, Select Boundary Loop, Mark Seam. Fast on complex hard-surface pieces.
- Turn on UV Sync Selection, pick trouble edges in the UV editor, then mark the seam in the 3D view.
- Apply or remove a Solidify modifier before unwrapping. Apply bevels before unwrapping.

## Unwrap methods

Choose the result that supports the texture. Don't rely on one algorithm.

- **Angle Based (ABF, the default):** keeps face angles. Best for organic models, characters and curved surfaces. Can add some area stretching.
- **Conformal (LSCM):** best for simpler geometric and hard-surface parts. Can distort or scale parts unevenly on complex organic shapes.
- **Minimum Stretch (SLIM):** balances area against angle distortion. Best for tight curves and large organic surfaces where stretching shows (a mouse body, for example).

With a Subdivision Surface modifier: unwrap Angle Based with Use Subdivision Surface on, and set the modifier's UV Smooth to Keep Corners and Boundary Smooth to All. Applying the subdivision and unwrapping again is a last resort.

Pin and Relax aren't part of this workflow.

Automatic UVs (Smart UV Project, Painter or ZBrush auto unwrap, Cube Projection) are fine when the result meets the job, for example Cube Projection on lights and glass that get procedural materials. Portfolio pieces need clean UVs.

## Straightening and editing

- Straighten islands that hold labels, trim or directional detail. Straightening can add some distortion on purpose, so do it when the texture benefits.
- Follow Active Quads (Blender) or Straighten (UV Toolkit), which gives a much straighter result.
- UV Toolkit: Orient Islands, Orient to Edge, Stack Similar, Straighten, Seams from Islands, Split Faces. Blender's Stitch joins islands.
- Use the tool to remove repetition, then check what changed.

## Duplicates and mirrored parts

- **Copy UVs copies coordinates, not seams.** After copying, run Seams from Islands so the copies keep their cuts, or they fall apart the next time you unwrap or pack.
- When Copy UVs fails (common with imported duplicates): select the copies, then the source last so it's active, `Ctrl+L` > Transfer Mesh Data, Edge Data: UV Seam, Edge Mapping: Topology, Object Transform off. Needs matching topology. Doing a few by hand is often quicker.
- Mirrored parts: delete one side, add a Mirror modifier with Mirror U and V on, apply, then unwrap again so the UVs aren't flipped. If copying caused flipped UVs, use a Mirror modifier with Merge off, re-unwrap the mirrored meshes, then pack. `Ctrl+Shift+M` (Select Mirror) grabs the other side.
- Stack copies (screws, bolts, repeated straps) to save space. Reuse only saves space when the shared information is appropriate: decide which regions stay unique for baking. Set up properly, mirrored and stacked UVs don't cause baking issues.
- UV map one strap, chain link or emblem before duplicating it.

## Texel density

Texel density is texture pixels per surface area, measured in **pixels per centimeter**. 1024 px across 100 cm is 10.24 px/cm.

- The course works to **20.48 px/cm for hero assets** and **10.24 px/cm minimum** for everything around them. These are working guidelines, not industry-wide requirements. Use the project's numbers when it has them.
- Four things change density: texture resolution, object size, UV scale (scaling UVs up is how tiling textures look sharp), and distance from the camera, including render resolution.
- Aim for consistency. A crisp object next to a blurry one breaks immersion. It doesn't need to be perfect.
- Too low: go from 2K to 4K. Too high: drop 2K to 1K. If neither works, add or remove texture sets.
- Watch for waste: a small prop alone on a 4K map can hit 100+ px/cm.

Texel Density Checker (free) measures and sets it. `scripts/uv_report.py` reports it per object with a verdict against the two numbers.

## Texture sets and packing

- Substance Painter makes one texture set per material. **Pack by material set.** The more optimized the model, the fewer sets it needs.
- Group props by where they sit and how close the camera gets. Large or hero surfaces get their own set. Split an asset when it gives you control (a workbench top separate from its legs).
- Name sets clearly: collections `1_tex_set_<name>`, materials `M_tex_set_<name>`. Clone materials rather than overwrite them, and `Ctrl+L` > Link Materials from the active object.
- Know what the pack needs before you pack: orientation, rotation, density preservation, padding. A good pack keeps the decisions you already made. Don't chase occupancy at the expense of the texture.
- To keep island rotation, turn Pre-rotate off and set the angle to 0. It matters most for clothing and hair.
- Packers rescale and rotate islands. Pin islands you placed by hand, then pack around them. Packing to a custom region keeps props together, at a cost in space and density. A packer can't create more unique texels.
- Place large islands by hand when packing many objects into one set.
- On big assets, pack as you go, then do one clean final pass.
- UV-Packer (free; its successor is Unwrella) packs better than Blender's default. Repack a few times to remove dead space.

## Padding

Padding protects each island from its neighbors when the engine uses smaller mip levels at a distance. Without it, colors bleed across seams.

- **Use 4 to 8 px. 16 px is the max.** Start with 8 px at 2K and 4K, and 4 px at 1K and below.
- Go up toward 16 px only if you see bleeding at a distance. The right amount depends on the engine's filtering and how far the asset gets from the camera.
- Be clear whether a number means the gap between islands or the dilation around each island. Lightmaps follow their own rules.

## Texture systems

Context decides. Games, VFX and cinematics want different things.

- **Trim sheet:** design the reusable texture, then map geometry to its bands. Only repeat along the trim's supported direction.
- **Decals** add one-off detail on top of trims. Atlas them (OM3D Atlas) to cut materials: six decals with six materials and 15 textures became one material with three maps.
- **Individual prop** texture sets, or **atlas** them at the end, which also makes LODs easier.
- **UDIMs** give fidelity. They're common in VFX and cinematics, uncommon in games. Check renderer and engine support first. UDIM tiles are not the same thing as texture sets.
- Hybrids are normal. More tiles only help when more unique information is needed.

Extend (clamp) suits decals, sprites, UI, lightmaps and baked textures and prevents edge bleeding. Repeat is for tiling. There's no meaningful performance difference.

## Runtime cost

UV seams and hard edges split vertices on the GPU. Use enough seams to get the result, and understand the cost. A shared atlas only cuts draw calls when the props share the material.

## Lightmaps and UV channels

One mesh can carry different layouts. Baked lighting needs a unique, padded second channel. Stacked texture islands can't stay stacked there. Engines can auto-generate lightmap UVs, but that repacks the existing charts rather than cutting new ones. Not every asset needs a lightmap.

## Bake-ready UVs

- **Bake early. It finds problems the checker misses.** Self-bake the low poly, apply test materials, fix UV problems, repeat until clean. Do a Substance Painter test bake even if the final bake happens elsewhere.
- Check the UV editor's distortion overlay, not only the checker.
- **Triangulate before you bake and export.** The bake and the final mesh need the same triangulation.
- When a bake looks wrong, sort the problem first: UV, projection or shading. Check the cause before changing the UVs.

## Hair cards and stitching

For high-frequency detail like hair cards and stitching, plan the UVs first, then the geometry. A hair card is a plane, an Array modifier with a UV offset in V, then a curve. Keep island rotation when packing them.

## Diagnose before editing

UVs expose bad models. A similar symptom can have a different cause. Common ones:

| Symptom | Cause | Fix |
|---|---|---|
| Mirrored parts won't take seams | Mirrored or imported geometry | Rebuild with a Mirror modifier, Mirror U/V on |
| Density or unwrap off on part of a model | Scale on the parent, not the mesh | Select the whole hierarchy and apply scale |
| Odd overlaps | Duplicate geometry | Remove the duplicate faces |
| Unwrap or pack breaks | Floating vertex | Find it in UV Sync mode and delete it |
| Seam on the symmetry line | Unwelded vertex | Merge it |
| Flipped UVs after copying | Copying on a symmetrical model | Mirror modifier with Merge off, re-unwrap, pack |
| Distortion only visible up close | Too few seams | Add seams, check the checker and distortion overlay |

Run OM3D Asset Prep (or the om3d-asset-prep skill) before the UV stage and again at the end. It catches the small objects you miss.

## Final validation checklist

- **Geometry:** scale applied, topology and triangulation understood, normals and face orientation checked, modifier state evaluated, no floating or unwelded verts.
- **UVs:** correct channel, distortion acceptable (checker and distortion overlay), direction intentional, density measured at the right resolution, padding tested, overlap intentional, copied and mirrored parts still have seams.
- **Pipeline:** texture strategy matches the brief, bake assumptions consistent, test bake inspected, asset prep pass run.

Once the UVs are done, do one final pass on everything, then a clean final pack. Give it a night and look again with fresh eyes. And pace yourself: a full vehicle can take several nights.

## Add-ons used in the course

All free: UV Toolkit, Texel Density Checker, UV Packer (now Unwrella), TexTools (needs a patch for Blender 5.x), OM3D Atlas and OM3D Asset Prep. UV Squares also works for one-click straightening. Dedicated tools like RizomUV help on very large assets; the thinking is the same in any tool. Ask which add-ons the artist has before suggesting steps that need them.

## Working with the artist

- Get a short brief first, one question at a time with a suggested answer: the camera, the texture system, what needs unique detail, the working density, the overlap policy and where the asset is going.
- Run `scripts/uv_report.py` before and after, and report plain numbers.
- Save before scripted UV edits. Scripts run through Blender MCP don't always make an undo step.
- Reports never change the mesh. Seams, unwraps and packs happen only once the artist agrees.
- Know the issue, know the fix, then let Claude carry out the repetitive part.
- Blender 5.x keeps UV selection in mesh attributes, not on BMesh loop UVs. Use the `bpy.ops.uv` selection operators, or read the attributes in Object Mode.

## Files

- `scripts/uv_report.py`: read-only UV report for the selected meshes, printed as JSON: islands, UV fill, overlaps per material, flipped faces, hard edges with no UV split, texel density in px/cm with a verdict, and the padding for the texture size. Set `TEXTURE_SIZE` at the top to the texture set size.
