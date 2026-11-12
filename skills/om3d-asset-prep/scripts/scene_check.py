"""OM3D scene_check: read-only prep report for game assets.

Run in Blender (Scripting tab, or through Blender MCP). Prints JSON.
Checks the selected meshes, or every visible mesh when nothing is selected.
Does not change anything. Edit the naming rules below to match your studio.
"""
import json
import re

import bmesh
import bpy
from mathutils import kdtree

PREFIX = "SM"
LOW, HIGH = "low", "high"
# SM_<Asset>[_<Part>]_low   or   SM_<Asset>[_<Part>]_high[_<Tag>]
NAME_RE = re.compile(
    rf"^{PREFIX}_(?P<asset>[A-Za-z0-9]+)(?:_(?P<part>[A-Za-z0-9]+))?_(?P<kind>{LOW}|{HIGH})(?:_(?P<tag>[A-Za-z0-9]+))?$"
)
COLLISION_RE = re.compile(r"^(UCX|UBX|USP|UCP)_")
DUPLICATE_RE = re.compile(r"\.\d{3}$")
JUNK_RE = re.compile(r"^(Cube|Cylinder|Sphere|Plane|Circle|Cone|Torus|Icosphere|Suzanne|Mesh|Object|pCube|pCylinder|polySurface)\b", re.I)
MERGE_TOL_FRACTION = 1e-5  # duplicate-vert distance as a fraction of the mesh's size


def target_objects():
    objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    if not objs:
        objs = [o for o in bpy.context.view_layer.objects if o.type == 'MESH' and o.visible_get()]
    return objs


def name_issues(obj):
    n = obj.name
    issues = []
    if COLLISION_RE.match(n):
        return issues
    if DUPLICATE_RE.search(n):
        issues.append("duplicate_suffix")
    if JUNK_RE.match(n):
        issues.append("default_name")
    if not NAME_RE.match(DUPLICATE_RE.sub("", n)):
        issues.append("not_convention")
    if obj.data.name != n and obj.data.users == 1:
        issues.append("mesh_data_name_differs")
    return issues


def transform_issues(obj):
    s = obj.scale
    issues = []
    if s.x * s.y * s.z < 0:
        issues.append("negative_scale")
    elif any(abs(c - 1.0) > 1e-5 for c in s):
        issues.append("unapplied_scale")
    if any(abs(c) > 1e-5 for c in obj.rotation_euler) and obj.rotation_mode not in {'QUATERNION', 'AXIS_ANGLE'}:
        issues.append("unapplied_rotation")
    return issues


def mesh_issues(obj):
    if obj.mode == 'EDIT':
        obj.update_from_editmode()
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    try:
        ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
        diag = max(obj.dimensions.length / max(max(obj.scale), 1e-9), 1e-9)
        zero_area = sum(1 for f in bm.faces if f.calc_area() < (diag * 1e-6) ** 2)
        non_manifold = sum(1 for e in bm.edges if len(e.link_faces) > 2) + \
            sum(1 for v in bm.verts if v.link_faces and not v.is_manifold and not v.is_boundary)
        loose_verts = sum(1 for v in bm.verts if not v.link_edges)
        loose_edges = sum(1 for e in bm.edges if not e.link_faces)

        tol = diag * MERGE_TOL_FRACTION
        tree = kdtree.KDTree(len(bm.verts))
        for v in bm.verts:
            tree.insert(v.co, v.index)
        tree.balance()
        bm.verts.ensure_lookup_table()
        dup = 0
        for v in bm.verts:
            neighbors = {e.other_vert(v).index for e in v.link_edges}
            for _co, idx, _d in tree.find_range(v.co, tol):
                if idx != v.index and idx not in neighbors:
                    dup += 1
                    break
        return {
            "ngons": ngons,
            "zero_area_faces": zero_area,
            "non_manifold": non_manifold,
            "loose_verts": loose_verts,
            "loose_edges": loose_edges,
            "duplicate_verts": dup,
            "uv_maps": len(me.uv_layers),
            "empty_material_slots": sum(1 for s in obj.material_slots if s.material is None),
            "triangles": sum(len(f.verts) - 2 for f in bm.faces),
        }
    finally:
        bm.free()


def severity(issues, mesh):
    errors, warnings = [], []
    for i in issues:
        (errors if i == "negative_scale" else warnings).append(i)
    if mesh["uv_maps"] == 0:
        errors.append("no_uv_map")
    elif mesh["uv_maps"] > 1:
        warnings.append("more_than_one_uv_map")
    for key in ("non_manifold", "zero_area_faces"):
        if mesh[key]:
            errors.append(key)
    for key in ("ngons", "loose_verts", "loose_edges", "duplicate_verts", "empty_material_slots"):
        if mesh[key]:
            warnings.append(key)
    return errors, warnings


def bake_pairs(objs):
    pairs = {}
    for o in objs:
        m = NAME_RE.match(o.name)
        if not m:
            continue
        key = f"{m['asset']}_{m['part']}" if m["part"] else m["asset"]
        p = pairs.setdefault(key, {"low": [], "high": []})
        p[m["kind"]].append(o.name)
    return {
        "pairs": {k: v for k, v in pairs.items() if v["low"] and v["high"]},
        "lows_without_high": [n for v in pairs.values() if not v["high"] for n in v["low"]],
        "highs_without_low": [n for v in pairs.values() if not v["low"] for n in v["high"]],
    }


def main():
    objs = target_objects()
    rows = []
    for o in objs:
        names = name_issues(o)
        trans = transform_issues(o)
        mesh = mesh_issues(o)
        errors, warnings = severity(names + trans, mesh)
        rows.append({"object": o.name, "errors": errors, "warnings": warnings, "details": mesh})
    out = {
        "checked": len(rows),
        "with_errors": sum(1 for r in rows if r["errors"]),
        "with_warnings": sum(1 for r in rows if r["warnings"]),
        "objects": rows,
        "bake": bake_pairs(objs),
    }
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
