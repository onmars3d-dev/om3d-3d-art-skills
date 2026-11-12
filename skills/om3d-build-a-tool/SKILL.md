---
name: om3d-build-a-tool
description: Turn a 3D artist's idea for a tool into a working Blender add-on, by interviewing them one question at a time, writing a one-page spec, then building, testing and versioning it. Use when the user wants to build a custom tool, add-on, script or automation for Blender (or another 3D app) and may not know how to code.
---

# OM3D Build a Tool

Most artists know exactly what tool they want and have no idea how to turn it into code. This skill is the path from "I wish Blender did X" to a working add-on they can install, test and keep improving.

## Step 1: Interview

Ask one question at a time. With each question, give your recommended answer and why, so the artist can reply "agree" and move on. Many artists answer from their phone, so keep questions short.

Cover, in roughly this order:

1. What the tool does in one sentence, and the moment in their workflow where they'd reach for it.
2. What they do by hand today, step by step. If they can, have them do it once by hand on a real asset while you take notes. The by-hand pass finds the rules the tool needs.
3. Inputs and outputs: what is selected when they run it, and what should be different afterwards.
4. What must never happen (moving verts they didn't select, deleting materials, overwriting files).
5. Where it lives in the UI: sidebar tab, menu, pie menu, or hotkey.
6. What "done" looks like for version 0.1. Keep it small.

Stop when you have enough for 0.1. Everything else goes on a "later" list.

## Step 2: One-page spec

Write a short spec: purpose, the by-hand steps it replaces, inputs, outputs, UI, safety rules, the 0.1 scope, and the later list. Ask the artist to read it and push back before you write code.

## Step 3: Build

- A Blender extension: `blender_manifest.toml` holds the version (the only place it lives), plus `__init__.py` and modules split by job (core logic with no UI, operators, panels).
- Keep the core logic free of UI code so it can be tested on its own.
- Every operator that changes data supports undo (`bl_options = {'REGISTER', 'UNDO'}`), and a preview or dry run comes before anything destructive.
- Tooltips on every button, written in the artist's words.

## Step 4: Test

- Write a test script that builds a small synthetic scene, runs the tool, and checks the result. Run it in a separate Blender instance in the background, never in the artist's open file:
  `blender --background --factory-startup --python run_tests.py`
- If Blender MCP is connected, install the add-on into the artist's Blender, run it on a copy of a real asset, and capture a viewport screenshot to show them.
- Then the artist tries to break it by hand. Their bug reports drive the next version.

## Step 5: Version and ship

- Bump the version on every change the artist will test. Keep a changelog with one line per version: what it added and what feedback drove it.
- Release as a zip with the files at the zip root, named `<tool>_v0.2.0.zip`.
- Install: Edit > Preferences > Get Extensions > Install from Disk.
- After installing from a script, save user preferences, or the add-on is off after the next restart.

## Lessons from building real tools this way

- Run a linter like `pyflakes` before installing. A syntax check misses undefined names, and one undefined constant stops the whole add-on from enabling.
- Read the evaluated mesh (`obj.evaluated_get(depsgraph)`) when a check depends on modifiers or Geometry Nodes. `obj.data` is the mesh before modifiers.
- Absolute tolerances break on small parts. Scale them with the mesh size.
- Never register a subclass of a panel that is already registered.
- Keep result lists in the sidebar short. It is narrow at default width.
