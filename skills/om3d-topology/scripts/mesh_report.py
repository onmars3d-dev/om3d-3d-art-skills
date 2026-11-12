"""OM3D mesh_report: read-only topology report for the selected meshes.

Run in Blender (Scripting tab, or through Blender MCP). Prints JSON.
Does not change the mesh. Works in Object Mode and Edit Mode.
Measures the base mesh (before modifiers), which is what the artist edits.
"""
import json
import math

import bmesh
import bpy

# A face counts as non-planar when any corner bends more than this many
# degrees away from the face normal. Raise it to ignore tiny deviations.
NON_PLANAR_DEGREES = 1.0


def face_bend_degrees(f):
    """Largest angle between the face normal and any corner's own normal."""
    n = f.normal
    if n.length < 1e-12 or len(f.verts) < 4:
        return 0.0
    worst = 0.0
    for loop in f.loops:
        a = loop.link_loop_prev.vert.co - loop.vert.co
        b = loop.link_loop_next.vert.co - loop.vert.co
        c = b.cross(a)
        if c.length < 1e-12:
            continue
        d = max(-1.0, min(1.0, c.normalized().dot(n)))
        worst = max(worst, math.degrees(math.acos(d)))
    return worst


def target_objects():
    objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    if not objs and bpy.context.active_object and bpy.context.active_object.type == 'MESH':
        objs = [bpy.context.active_object]
    return objs


def report(obj):
    if obj.mode == 'EDIT':
        obj.update_from_editmode()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    try:
        quads = tris = ngons = 0
        tri_count = 0
        ngon_faces = []
        non_planar = []
        worst_bend = 0.0
        for f in bm.faces:
            n = len(f.verts)
            tri_count += n - 2
            bend = face_bend_degrees(f)
            if bend > NON_PLANAR_DEGREES:
                non_planar.append((bend, f.index))
                worst_bend = max(worst_bend, bend)
            if n == 4:
                quads += 1
            elif n == 3:
                tris += 1
            else:
                ngons += 1
                if len(ngon_faces) < 50:
                    ngon_faces.append(f.index)

        # Poles: interior verts whose edge count isn't 4. Boundary verts are
        # reported separately because 3 edges is normal on an open border.
        poles = {}
        pole_verts = {}
        loose_verts = 0
        for v in bm.verts:
            if not v.link_edges:
                loose_verts += 1
                continue
            if v.is_boundary or not v.link_faces:
                continue
            valence = len(v.link_edges)
            if valence != 4:
                key = str(valence)
                poles[key] = poles.get(key, 0) + 1
                lst = pole_verts.setdefault(key, [])
                if len(lst) < 50:
                    lst.append(v.index)

        non_manifold = []
        boundary = 0
        loose_edges = 0
        for e in bm.edges:
            nf = len(e.link_faces)
            if nf == 0:
                loose_edges += 1
            elif nf == 1:
                boundary += 1
            elif nf > 2 and len(non_manifold) < 200:
                non_manifold.append(e.index)
        non_manifold_count = sum(1 for e in bm.edges if len(e.link_faces) > 2)

        total = max(len(bm.faces), 1)
        return {
            "object": obj.name,
            "verts": len(bm.verts),
            "faces": len(bm.faces),
            "triangles_when_triangulated": tri_count,
            "quads": quads,
            "tris": tris,
            "ngons": ngons,
            "quad_percent": round(100.0 * quads / total, 1),
            "poles_by_valence": dict(sorted(poles.items(), key=lambda kv: int(kv[0]))),
            "non_planar_faces": len(non_planar),
            "non_planar_threshold_degrees": NON_PLANAR_DEGREES,
            "worst_bend_degrees": round(worst_bend, 2),
            "boundary_edges": boundary,
            "non_manifold_edges": non_manifold_count,
            "loose_verts": loose_verts,
            "loose_edges": loose_edges,
            "sample_indices": {
                "ngon_faces": ngon_faces,
                "non_planar_faces_worst_first": [i for _b, i in sorted(non_planar, reverse=True)[:50]],
                "pole_verts": pole_verts,
                "non_manifold_edges": non_manifold,
            },
        }
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
