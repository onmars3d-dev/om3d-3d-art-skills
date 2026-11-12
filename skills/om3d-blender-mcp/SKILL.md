---
name: om3d-blender-mcp
description: Set up and safely use Blender MCP so Claude can run Python in Blender, read the scene and see the viewport. Use when the user wants to connect Claude to Blender, troubleshoot the Blender connection, or asks Claude to work directly in their Blender scene.
---

# OM3D Blender MCP

Blender MCP lets Claude work inside the artist's real Blender scene instead of guessing. This skill covers setup, a first connection check, and the rules that keep the artist's files safe.

## How the pieces connect

There are three parts, and all three need to be in place:

1. **The Blender connector in Claude.** In the Claude desktop app: Customize > Connectors, search "Blender", Add. This installs the MCP server program Claude launches.
2. **The MCP extension inside Blender** (Blender 5.1 or newer). It listens on port 9876 on the local machine only.
3. **Online Access** turned on in Blender: Edit > Preferences > System > Online Access.

Installing the Blender extension alone does nothing. The server Claude talks to is a separate program that comes with the connector.

## Setup steps

1. Install Blender 5.1+ and the Claude desktop app, and sign in.
2. Add the Blender connector in Claude (above).
3. In Blender, turn on Online Access, then Edit > Preferences > Get Extensions > Repositories > add `https://lab.blender.org/`. Search for "MCP", install it and enable it.
4. In Blender, Edit > Preferences > Add-ons > MCP: start the server, or turn on auto start.
5. Quit Claude fully (tray icon > Quit) and reopen it. Start a new chat or task. Chats that were already open don't pick up new connections.

Start order: open Blender first, then Claude.

## First check

Ask the artist to open a scene, then check the connection by reading the Blender version, the open file, and the list of objects in the scene. Report what you see in one or two lines. Take a viewport screenshot if the tool offers it.

## Troubleshooting

| Symptom | Fix |
|---|---|
| No Blender tools in Claude | Claude wasn't fully restarted, or the chat started before the connector was added. Quit from the tray and start a new chat. |
| "Online access must be enabled" | Edit > Preferences > System > Online Access. |
| Connection refused | Blender isn't open, or the MCP server in the add-on is stopped. Start it from the add-on preferences. |
| Port 9876 already in use | A second Blender is holding it. Close the other instance. |

## Safety rules

- **Save first.** Scripts run through MCP do not always create an undo step, so Ctrl+Z may not bring things back. Before any scripted change, save or ask the artist to.
- **Read before you write.** Inspect the scene and report what you found before changing anything.
- **Ask before deleting** objects, materials, images or files, and list exactly what will go.
- **Use a separate Blender instance for heavy tests**, run in the background, so the artist's session never crashes or gets changed by a test.
- **Keep it local.** The MCP server has no password. It only listens on the local machine, which is fine for a workstation. Never expose port 9876 to a network.
- **Show, don't describe.** After a visible change, grab a viewport screenshot so the artist can confirm it.

## Good first requests to try

- "List every object in my scene with its triangle count and material count."
- "Select every mesh that still has a default name like Cube or Cylinder.001."
- "Check my selected mesh for n-gons and non-manifold edges, and select them so I can see them."
- "Make a turntable camera around my selected object and render a preview."
