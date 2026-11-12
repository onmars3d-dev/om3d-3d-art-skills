---
name: om3d-topology
description: Check and fix topology for game and real-time assets in Blender, covering Sub-D surface artifacts (non-planar faces, poles), low poly optimization from a high poly, retopology, and triangle budgets. Use when the user asks about topology, retopo, edge flow, poles, shading artifacts, optimizing or reducing a mesh, low poly, LODs, or polycount.
---

# OM3D Topology

These rules come from the OnMars3D Modeling and Topology Masterclass and the Game Art Program. Help the artist find topology problems early, measure instead of guessing, and do the tedious cleanup, while they stay in charge of the form.

## Sub-D: why a clean-looking mesh still shows artifacts

**Non-planar faces** are one of the main reasons smooth Sub-D models get surface artifacts. A mesh can be all quads with even edge distribution and still break up a highlight.

- A face is planar when all its verts sit on one plane, however the face is rotated. A smoothly curved surface can still be made of planar faces.
- They usually come from moving verts by hand or adding geometry with the knife tool.
- They show most on glossy and reflective surfaces. Check with a contrasty highlight matcap.
- To find them by eye, grab some faces, zoom in and look almost parallel down the surface from odd angles. `scripts/mesh_report.py` measures it for you.
- Fix: select the run of faces (the loop and the faces connected to it, not just one face), then LoopTools > Flatten. Flattening one set can push its neighbors out of plane, so expect a couple of passes. Aligning verts with scale-to-zero (`S Z 0`, `S Y 0`) also works. Toggle smooth preview to check.

**Poles** cause distortion too.

- Sometimes there is no way around a pole because the form needs it. Then the job is to keep the pole and its spread as small as possible.
- Add a loop close to the pole (`Ctrl+R`) so its impact stays inside a small set of faces. Supporting loops contain the geometry, the poles and the deformation, and the mesh subdivides predictably.
- A uniform bevel only works when the curvature is uniform. Where a harder edge meets a softer curve, a bevel changes the profile. Bevel the silhouette edge and add the other edge by hand, so Blender's bevel doesn't leave an n-gon.

None of this is a catch-all. Explain the fix for the model in front of you.

## Low poly: optimizing from the high poly

The priority is preserving the **silhouette and shading quality**. The silhouette is king.

1. **Set the budget first.** Ask for the max triangle count per object and for the whole scene, the target hardware (high-end PC, current console, handheld, mobile, VR) and where the cameras sit. Always work in triangles, because the engine converts everything to triangles.
2. **Duplicate the high poly** (`Shift+D`, move it along X) so the two can be compared side by side.
3. **Strip the modifiers.** Drop Subdivision Surface. For a Bevel modifier, keep it (shape 0.5 keeps a flat chamfer) or remove it on small corners that don't read.
4. **Remove the support loops.** A high poly built with powers of four and even bevel segments reduces cleanly: Checker Deselect plus Select Edge Loops, then Dissolve Edges. Never dissolve an edge that holds the silhouette.
5. **Use triangles to control edge flow.** End a loop by merging its verts, or split it with a triangle on each side, then dissolve the part that adds nothing to the silhouette. Triangles are completely fine on a game mesh.
6. **Check the silhouette** with Matcap > Flat. It shows exactly which edges contribute to the form. Dissolve the ones that don't, and delete hidden inside faces.
7. **Compare low and high** in Solid view with the standard scene light and a plain material. The low has to match the high's form and silhouette, or the bake will have problems.
8. **Set shading.** Shade Auto Smooth and raise the angle until the shading looks right (around 30 to 35 degrees is a good start), then Mark Sharp by hand where a part needs a hard edge. Every hard edge will need a UV seam (see om3d-uv).

Don't reach for Decimate on hero or mid-distance assets. It wrecks the silhouette quickly and belongs to far-off LODs that take up a percent or two of the screen.

You'll hit a point where any more reduction breaks the silhouette. Stop there for the agreed target. Good optimization should be barely noticeable.

## Retopology of sculpts and scans

The same rules apply: silhouette first, triangle budget, loops where the mesh deforms. On characters that means loops around the eyes, mouth and joints, and poles kept out of the joint creases. An automatic remesher can give a starting base. Tell the artist which areas it usually gets wrong (the loops around eyes and mouth) and let them place those.

## Working with the artist

- Ask one question at a time, with a suggested answer each time, so they can just agree.
- Measure before and after with `scripts/mesh_report.py`. Report plain numbers: "1,400 tris, down from 1,700. 0 n-gons. 3 non-planar faces, all on the cap."
- Select problem faces or verts in Blender so they can see them, and lead with what will show in the bake or the shading.
- Save before scripted edits. Scripts run through Blender MCP don't always make an undo step.
- Change the mesh only after the artist agrees. Work on a duplicate when trying something risky.

## Files

- `scripts/mesh_report.py`: read-only topology report for the selected meshes, printed as JSON: quads, tris, n-gons, triangle count, poles by valence, non-planar faces, non-manifold and loose geometry, with sample indices to select.
