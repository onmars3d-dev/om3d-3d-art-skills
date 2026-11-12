"""Run with: python run_tests.py (needs `pip install bpy`), or blender --background --python run_tests.py"""
import importlib.util, bpy, bmesh
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills")
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
mr = load("mr", f"{ROOT}/om3d-topology/scripts/mesh_report.py")
ur = load("ur", f"{ROOT}/om3d-uv/scripts/uv_report.py")
sc = load("sc", f"{ROOT}/om3d-asset-prep/scripts/scene_check.py")
import contextlib, io
def quiet(f):
    with contextlib.redirect_stdout(io.StringIO()): return f()
ok = []
def check(label, cond, val=None):
    ok.append(cond); print(("PASS " if cond else "FAIL ") + label, "" if cond else val)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=2)
cube = bpy.context.active_object
r = quiet(mr.main)["meshes"][0]
check("cube quads 6", r["quads"] == 6, r); check("cube poles 3x8", r["poles_by_valence"] == {"3": 8}, r)
u = quiet(ur.main)["meshes"][0]
check("cube islands 1", u["islands"] == 1, u["islands"])
check("cube hard 12", u["hard_edges"] == 12, u["hard_edges"])
check("cube hard no split 5", u["hard_edges_without_uv_split"] == 5, u["hard_edges_without_uv_split"])
check("cube no overlap", u["overlapping_faces"] == 0, u)
check("cube no flip", u["flipped_faces"] == 0, u)
check("cube density 2.56 px/cm", abs(u["texel_density_px_per_cm"]["overall"] - 2.56) < 0.01, u["texel_density_px_per_cm"])
check("cube padding 8 at 2K", u["padding_px_for_texture_size"] == 8, u)
check("cube verdict below min", u["texel_density_px_per_cm"]["verdict"].startswith("below"), u)
r = quiet(mr.main)["meshes"][0]; check("flat cube planar", r["non_planar_faces"] == 0, r)
# smooth all -> 0 hard
bpy.ops.object.shade_smooth()
u = quiet(ur.main)["meshes"][0]; check("smooth cube hard 0", u["hard_edges"] == 0, u["hard_edges"])
# scale object 2x -> density halves
cube.scale = (2,2,2); bpy.context.view_layer.update()
u = quiet(ur.main)["meshes"][0]; check("scaled density 1.28", abs(u["texel_density_px_per_cm"]["overall"] - 1.28) < 0.01, u["texel_density_px_per_cm"])
cube.scale = (1,1,1)
# overlap: stack all faces onto same uv square
me = cube.data
for poly in me.polygons:
    for i, li in enumerate(poly.loop_indices):
        me.uv_layers.active.uv[li].vector = [(0,0),(1,0),(1,1),(0,1)][i]
u = quiet(ur.main)["meshes"][0]
check("stacked overlap 6", u["overlapping_faces"] == 6, u["overlapping_faces"]); check("stacked islands 6", u["islands"] == 6, u["islands"])
# flip one face
poly = me.polygons[0]
for i, li in enumerate(poly.loop_indices):
    me.uv_layers.active.uv[li].vector = [(0,0),(0,1),(1,1),(1,0)][i]
u = quiet(ur.main)["meshes"][0]; check("flipped 1", u["flipped_faces"] == 1, u["flipped_faces"])
# separate materials -> no overlap counted across materials
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=2); cube = bpy.context.active_object; me = cube.data
for n in range(6):
    me.materials.append(bpy.data.materials.new(f"M{n}"))
for i, poly in enumerate(me.polygons):
    poly.material_index = i
    for k, li in enumerate(poly.loop_indices):
        me.uv_layers.active.uv[li].vector = [(0,0),(1,0),(1,1),(0,1)][k]
u = quiet(ur.main)["meshes"][0]; check("per-material no overlap", u["overlapping_faces"] == 0, u["overlapping_faces"])
# Edit mode works
bpy.ops.object.mode_set(mode='EDIT'); r = quiet(mr.main)["meshes"][0]; bpy.ops.object.mode_set(mode='OBJECT')
check("edit mode report", r["faces"] == 6, r)
# grid ngon + sphere
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8)
r = quiet(mr.main)["meshes"][0]
check("sphere poles 16 x2", r["poles_by_valence"] == {"16": 2}, r["poles_by_valence"])
check("sphere tris 32", r["tris"] == 32, r["tris"])
u = quiet(ur.main)["meshes"][0]; check("sphere overlap 0", u["overlapping_faces"] == 0, u["overlapping_faces"])
bpy.ops.mesh.primitive_circle_add(fill_type='NGON', location=(5,0,0))
r = quiet(mr.main)["meshes"][0]; check("circle ngon 1", r["ngons"] == 1, r)
# non-planar: grid with one vert pushed up
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=4, y_subdivisions=4, size=2)
g = bpy.context.active_object
r = quiet(mr.main)["meshes"][0]; check("grid planar", r["non_planar_faces"] == 0, r)
center = min(g.data.vertices, key=lambda v: v.co.length)
center.co.z += 0.1
r = quiet(mr.main)["meshes"][0]; check("pushed vert -> 4 non-planar", r["non_planar_faces"] == 4, r["non_planar_faces"])
# hero density: 4K on 2 m plane = 20.48
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_plane_add(size=2)
ur.TEXTURE_SIZE = 4096
u = quiet(ur.main)["meshes"][0]
check("4K on 2 m = 20.48", abs(u["texel_density_px_per_cm"]["overall"] - 20.48) < 0.01, u["texel_density_px_per_cm"])
check("hero verdict", u["texel_density_px_per_cm"]["verdict"] == "hero density", u["texel_density_px_per_cm"])
check("4K padding 8", u["padding_px_for_texture_size"] == 8, u)
ur.TEXTURE_SIZE = 1024
u = quiet(ur.main)["meshes"][0]; check("1K padding 4", u["padding_px_for_texture_size"] == 4, u)
ur.TEXTURE_SIZE = 2048
# scene_check
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(); a = bpy.context.active_object
bpy.ops.mesh.primitive_cube_add(location=(4,0,0)); b = bpy.context.active_object
b.name = "SM_Crate_Lid_low"; b.data.name = b.name
bpy.ops.mesh.primitive_cube_add(location=(4,0,0)); c = bpy.context.active_object
c.name = "SM_Crate_Lid_high_Bolts"; c.data.name = c.name
bpy.ops.mesh.primitive_cube_add(location=(8,0,0)); d = bpy.context.active_object
d.name = "SM_Barrel_low"; d.data.name = d.name; d.scale = (-1,1,1)
# add duplicate vert to d
bm = bmesh.new(); bm.from_mesh(d.data)
bm.verts.ensure_lookup_table(); bm.verts.new(bm.verts[0].co); bm.to_mesh(d.data); bm.free()
bpy.ops.object.select_all(action='DESELECT')
s = quiet(sc.main)
rows = {r["object"]: r for r in s["objects"]}
check("scene checked 4", s["checked"] == 4, s["checked"])
check("Cube default name", "default_name" in rows["Cube"]["warnings"] and "not_convention" in rows["Cube"]["warnings"], rows["Cube"])
check("lid clean", not rows["SM_Crate_Lid_low"]["errors"] and not rows["SM_Crate_Lid_low"]["warnings"], rows["SM_Crate_Lid_low"])
check("barrel negative", "negative_scale" in rows["SM_Barrel_low"]["errors"], rows["SM_Barrel_low"])
check("barrel loose + dup", rows["SM_Barrel_low"]["details"]["loose_verts"] == 1 and rows["SM_Barrel_low"]["details"]["duplicate_verts"] >= 1, rows["SM_Barrel_low"]["details"])
check("pairs", "Crate_Lid" in s["bake"]["pairs"] and s["bake"]["lows_without_high"] == ["SM_Barrel_low"], s["bake"])
print(f"{sum(ok)}/{len(ok)} passed")
