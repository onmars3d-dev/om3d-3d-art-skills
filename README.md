# OM3D 3D Art Skills

Agent skills for 3D artists, from OnMars3D. They teach Claude the topology, UV and game asset rules from my courses (the Modeling and Topology Masterclass, the UV Mapping Masterclass and the Game Art Program), so it can handle the tedious parts of game art in Blender with you: topology checks, low poly optimization, UVs, bake prep, export, and building your own tools.

You asked for this. When I put out the AI workflows video, over 140 of you signed up, and the top answers to "what would you most want to automate?" were retopology and UVs, then baking, naming and cleanup, and building your own tools. So that's what's in the first pack.

## What's in here

| Skill | What it does |
|---|---|
| `om3d-topology` | Finds the stuff that causes shading artifacts on Sub-D models (non-planar faces, poles), walks you through optimizing a high poly down to a game-ready low poly, and covers retopo. Counts tris, n-gons, poles and non-planar faces. |
| `om3d-uv` | The UV Mapping Masterclass workflow: seam planning, unwrap methods, straightening, copied and mirrored parts, texel density (20.48 px/cm for heroes, 10.24 minimum), texture sets, packing and padding, trims, atlases and UDIMs, lightmaps and bake checks. Flags hard edges with no UV seam, overlaps inside a texture set and flipped islands. |
| `om3d-asset-prep` | Naming, scene checks, low/high bake pairs, and export settings for Substance Painter, Marmoset and Unreal. |
| `om3d-build-a-tool` | Turns your tool idea into a Blender add-on. Claude interviews you one question at a time, writes a short spec, then builds and tests it. |
| `om3d-blender-mcp` | Connects Claude to Blender so it can work in your actual scene, with the safety rules I use. |

The topology, UV and asset prep skills come with small Blender scripts that only read your scene and print a report. They never change your mesh.

## Install

**Claude Code**

```
/plugin marketplace add onmars3d-dev/om3d-3d-art-skills
/plugin install om3d-3d-art-skills@om3d-3d-art-skills
```

Or copy any folder from `skills/` into `~/.claude/skills/`.

**Claude app (desktop or web)**

Zip one skill folder (for example `skills/om3d-uv`) so the folder sits at the root of the zip, then upload it in Settings > Capabilities > Skills.

## Getting the most out of them

Most of these work best with Claude connected to Blender. Start with `om3d-blender-mcp` if you haven't set that up. Without it, the skills still work as a guide: Claude walks you through the steps and you run the scripts yourself from Blender's Scripting tab.

Some prompts to try:

- "Check my Sub-D model for non-planar faces and poles that could cause artifacts."
- "Help me optimize this high poly into a low poly under 1,500 tris without losing the silhouette."
- "Check the texel density of everything in this texture set at 4K and tell me what falls below 10.24 px/cm."
- "Find my bake pairs and tell me which lows don't have a high."
- "I want a tool that renames all my highs to match the nearest low. Interview me."

Save your file before you let Claude change anything. Scripts run through MCP don't always make an undo step.

## Tested on

Blender 5.2. The report scripts have a test suite that runs on Blender's Python module (`bpy`).

## Feedback

Tell me what broke and what you want next. Reply to the email this came from, or find me on YouTube at @onmars3d.

## License

MIT. Use them, change them, share them.
