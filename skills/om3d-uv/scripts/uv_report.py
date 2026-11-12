"""OM3D uv_report: read-only UV report for the selected meshes.

Run in Blender (Scripting tab, or through Blender MCP). Prints JSON.
Uses the active UV map. Does not change the mesh.

Reports per object:
- islands, UV fill (UV area / 0-1 square; above 1 means overlaps or tiles)
- overlapping faces per material (each material is its own texture set)
- flipped faces
- hard edges with no UV split (bakes show a seam line there)
- texel density in px/cm (median, 10th and 90th percentile across faces),
  checked against the OnMars3D guideline: 20.48 px/cm for hero assets,
  10.24 px/cm minimum for everything around them
- the island padding to use for the texture size (for mip mapping)
"""
import json
import math
from collections import defaultdict

import bmesh
import bpy

TEXTURE_SIZE = 2048        # px, the texture set this object will use
HERO_PX_PER_CM = 20.48     # hero assets (4K on a 2 m plane, or 2K on 1 m)
MIN_PX_PER_CM = 10.24      # minimum for everything around the hero
# Island padding: use 4 to 8 px, 16 px max. 8 px at 2K and up, 4 px at 1K and below.
# Go up toward 16 px only if islands bleed at a distance.
PADDING_MAX_PX = 8
PADDING_MIN_PX = 4
PADDING_CEILING_PX = 16
HARD_DOT = 0.999           # corner normals closer than this count as smooth
UV_EPS = 1e-6
OVERLAP_EPS = 1e-7


def target_objects():
    objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    if not objs and bpy.context.active_object and bpy.context.active_object.type == 'MESH':
        objs = [bpy.context.active_object]
    return objs


def percentile(vals, p):
    if not vals:
        return None
    vals = sorted(vals)
    k = (len(vals) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def tri_area2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])


def tris_overlap(t1, t2):
    """2D triangle overlap by separating axes. Touching edges don't count."""
    for tri in (t1, t2):
        for i in range(3):
            p, q = tri[i], tri[(i + 1) % 3]
            ax, ay = q[1] - p[1], p[0] - q[0]
            n = math.hypot(ax, ay)
            if n < 1e-12:
                continue
            ax, ay = ax / n, ay / n
            a = [ax * x + ay * y for x, y in t1]
            b = [ax * x + ay * y for x, y in t2]
            if min(a) >= max(b) - OVERLAP_EPS or min(b) >= max(a) - OVERLAP_EPS:
                return False
    return True


def overlapping_faces(tris_by_mat):
    """tris_by_mat: {mat: [(face_index, ((u,v),(u,v),(u,v)))]}. Returns set of face indices."""
    hits = set()
    for tris in tris_by_mat.values():
        if len(tris) < 2:
            continue
        # Grid sized so each cell holds a few triangles.
        cells = max(4, int(math.sqrt(len(tris))))
        grid = defaultdict(list)
        boxes = []
        for idx, (fi, t) in enumerate(tris):
            xs = [p[0] for p in t]
            ys = [p[1] for p in t]
            box = (min(xs), min(ys), max(xs), max(ys))
            boxes.append(box)
            for gx in range(int(math.floor(box[0] * cells)), int(math.floor(box[2] * cells)) + 1):
                for gy in range(int(math.floor(box[1] * cells)), int(math.floor(box[3] * cells)) + 1):
                    grid[(gx, gy)].append(idx)
        seen = set()
        for members in grid.values():
            for i in range(len(members)):
                a = members[i]
                fa, ta = tris[a]
                for j in range(i + 1, len(members)):
                    b = members[j]
                    fb, tb = tris[b]
                    if fa == fb:
                        continue
                    if fa in hits and fb in hits:
                        continue
                    key = (a, b) if a < b else (b, a)
                    if key in seen:
                        continue
                    seen.add(key)
                    ba, bb = boxes[a], boxes[b]
                    if ba[0] >= bb[2] or bb[0] >= ba[2] or ba[1] >= bb[3] or bb[1] >= ba[3]:
                        continue
                    if tris_overlap(ta, tb):
                        hits.add(fa)
                        hits.add(fb)
    return hits


def hard_edges_without_split(mesh, uv_layer):
    """Hard = shading actually splits (corner normals differ). Split = UVs differ."""
    normals = [c.vector.copy() for c in mesh.corner_normals]
    uvs = uv_layer.uv
    loops = mesh.loops
    edge_corners = defaultdict(list)  # (va, vb) -> [(loop at va, loop at vb)]
    for poly in mesh.polygons:
        start, total = poly.loop_start, poly.loop_total
        for k in range(total):
            la = start + k
            lb = start + (k + 1) % total
            va, vb = loops[la].vertex_index, loops[lb].vertex_index
            if va < vb:
                edge_corners[(va, vb)].append((la, lb))
            else:
                edge_corners[(vb, va)].append((lb, la))
    hard = 0
    flagged = []
    for key, pairs in edge_corners.items():
        if len(pairs) != 2:
            continue
        (a1, b1), (a2, b2) = pairs
        is_hard = normals[a1].dot(normals[a2]) < HARD_DOT or normals[b1].dot(normals[b2]) < HARD_DOT
        if not is_hard:
            continue
        hard += 1
        split = (uvs[a1].vector - uvs[a2].vector).length > UV_EPS or \
                (uvs[b1].vector - uvs[b2].vector).length > UV_EPS
        if not split:
            flagged.append(key)
    return hard, flagged


def island_count(bm, uv):
    parent = list(range(len(bm.faces)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        f1, f2 = e.link_faces
        l1 = [l for l in e.link_loops if l.face == f1][0]
        l2 = [l for l in e.link_loops if l.face == f2][0]
        # l1 runs v->w in f1, l2 runs w->v in f2 on a consistently wound mesh.
        same = True
        for lp in (l1, l1.link_loop_next):
            other = l2 if lp.vert == l2.vert else l2.link_loop_next
            if other.vert != lp.vert:
                same = False
                break
            if (lp[uv].uv - other[uv].uv).length > UV_EPS:
                same = False
                break
        if same:
            ra, rb = find(f1.index), find(f2.index)
            if ra != rb:
                parent[ra] = rb
    return len({find(i) for i in range(len(bm.faces))})


def report(obj):
    if obj.mode == 'EDIT':
        obj.update_from_editmode()
    mesh = obj.data
    out = {"object": obj.name, "uv_maps": [u.name for u in mesh.uv_layers]}
    if not mesh.uv_layers:
        out["error"] = "No UV map."
        return out
    uv_layer = mesh.uv_layers.active
    out["active_uv_map"] = uv_layer.name

    bm = bmesh.new()
    bm.from_mesh(mesh)
    try:
        bm.faces.ensure_lookup_table()
        uv = bm.loops.layers.uv.get(uv_layer.name)
        bm_world = bm.copy()
        bm_world.transform(obj.matrix_world)
        bm_world.faces.ensure_lookup_table()

        uv_area_total = 0.0
        flipped = []
        densities = []
        tris_by_mat = defaultdict(list)
        world_area_total = 0.0
        for f in bm.faces:
            pts = [tuple(l[uv].uv) for l in f.loops]
            a = 0.0
            for k in range(1, len(pts) - 1):
                a += tri_area2(pts[0], pts[k], pts[k + 1]) * 0.5
            uv_area_total += abs(a)
            if a < -1e-12:
                flipped.append(f.index)
            wa = bm_world.faces[f.index].calc_area()
            world_area_total += wa
            if wa > 1e-12 and abs(a) > 1e-14:
                densities.append(math.sqrt(abs(a) / wa) * TEXTURE_SIZE / 100.0)
        for tri in bm.calc_loop_triangles():
            f = tri[0].face
            tris_by_mat[f.material_index].append((f.index, tuple(tuple(l[uv].uv) for l in tri)))

        overlaps = overlapping_faces(tris_by_mat)
        hard, flagged = hard_edges_without_split(mesh, uv_layer)
        islands = island_count(bm, uv)
        bm_world.free()

        overall = math.sqrt(uv_area_total / world_area_total) * TEXTURE_SIZE / 100.0 if world_area_total > 0 else None
        out.update({
            "faces": len(bm.faces),
            "islands": islands,
            "uv_fill_percent": round(100.0 * uv_area_total, 1),
            "overlapping_faces": len(overlaps),
            "overlapping_sample": sorted(overlaps)[:50],
            "flipped_faces": len(flipped),
            "flipped_sample": flipped[:50],
            "hard_edges": hard,
            "hard_edges_without_uv_split": len(flagged),
            "hard_no_split_sample_vert_pairs": [list(k) for k in flagged[:50]],
            "texel_density_px_per_cm": {
                "texture_size": TEXTURE_SIZE,
                "overall": round(overall, 2) if overall else None,
                "p10": round(percentile(densities, 0.1), 2) if densities else None,
                "median": round(percentile(densities, 0.5), 2) if densities else None,
                "p90": round(percentile(densities, 0.9), 2) if densities else None,
            },
            "padding_px_for_texture_size": PADDING_MAX_PX if TEXTURE_SIZE >= 2048 else PADDING_MIN_PX,
            "padding_px_max_if_bleeding": PADDING_CEILING_PX,
        })
        if overall:
            td = out["texel_density_px_per_cm"]
            if overall >= HERO_PX_PER_CM * 2:
                td["verdict"] = "far above hero density: likely wasting texture space"
            elif overall >= HERO_PX_PER_CM * 0.9:
                td["verdict"] = "hero density"
            elif overall >= MIN_PX_PER_CM * 0.9:
                td["verdict"] = "above the minimum, below hero"
            else:
                td["verdict"] = "below the minimum: needs more resolution, more UV space, or its own texture set"
        return out
    finally:
        bm.free()


def main():
    objs = target_objects()
    out = {"meshes": [report(o) for o in objs]}
    if not objs:
        out["error"] = "Select at least one mesh object."
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
