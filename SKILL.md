---
name: room-planner
description: Plan and furnish any room as an interactive, true-to-scale 3D model in a single local HTML file (three.js) and refine it with the user step by step. Use this whenever someone wants to lay out, furnish, redesign or visualise a room or small space – living room, bedroom, kids' room, kitchen, dining room, home office, studio, hallway, guest room, bathroom, shop or office corner – especially when they give room dimensions, window/door/radiator positions, or ask things like "where should the sofa/bed/desk go", "show me my room in 3D", "does a table for 4 fit", "how much storage can I fit", or want a floor plan with measurements, even if they don't say "3D" or "planner".
---

# Room planner

Build a **local, single-file HTML + three.js scene** of the user's room in **real metric scale** and iterate on it with them until the layout feels right. The user previews the file locally; the value is in fast, concrete iterations ("move the couch 15 cm", "the storage looks bulky", "make the ceiling white") on a model whose numbers they can trust.

A complete, working reference implementation – a 4 × 5 m living room that went through ~50 rounds of feedback – is in `assets/example-living-room.html`. Reuse its engine instead of starting from scratch (see *Building the scene*).

## 1. Gather the facts before drawing

Ask only what you cannot reasonably assume, but get these right – they drive everything else:

- **Room type and use** (living, bedroom, kitchen, office, …) and who uses it.
- **Inner dimensions** (width × depth) and **ceiling height**. Ask for the height explicitly – people forget it, and it matters for windows, wall cabinets and indirect light.
- **Openings**: every window and door – which wall, position from a corner, width, height/sill, which way the door swings and on which side it is hinged.
- **Fixed points** that are expensive to move: radiators/heating (keep them free), existing ceiling or wall light outlets, sockets, built-ins, pillars, sloped ceilings. If the user mentions an existing outlet ("there is already a lamp on that wall"), keep the fixture there.
- **Must-haves** (e.g. a table for 4, a desk, max storage, a bed of 160 cm) and **no-gos** (e.g. "the couch not in front of the window").
- **Style** in the user's words ("modern but not too modern"), plus colours they like or dislike.

State your interpretation of anything ambiguous in one line and proceed; don't block on questions you can answer with a sensible default. Use **they/them** for people whose pronouns you don't know.

Read `references/clearances.md` for ergonomic distances per room type (walkways, chair pull-out, bed sides, kitchen aisles, TV distance …) and use them when placing things.

## 2. Building the scene

1. Copy `assets/example-living-room.html` to the user's working directory (e.g. `index.html`), then **keep the engine sections and replace the room-specific ones**. `references/architecture.md` maps every section of the file, says which parts are reusable as-is, which are room configuration, and explains the patterns (coordinate system, item registry, wall cut-away, measurements, lights …). Read it before editing.
2. Set the room constants (`W`, `D`, `H`, wall thickness, windows, doors) first, then walls/openings, then fixed points (radiators, sockets, outlets), then furniture.
3. Model furniture with **real dimensions** (cm accuracy) and register every object through `item(name, group, {...})` so double-click shows its size and gaps. Give each item a helpful `extra` text (material, why it is placed there).
4. Keep it local: one HTML file, three.js via an import map from a CDN (pinned version). Do **not** publish/upload the page unless the user explicitly asks – they preview locally (`open index.html` or `python3 -m http.server`).

### Features users expect (all present in the example – keep them)

- True scale (1 unit = 1 m), **orthographic floor plan** view with an on-screen scale bar, a 3D **scale bar** on the ground, room dimension lines, optional 50 cm grid.
- **Double-click any item** → orange outline with width/depth/height, an info card, and **blue gap lines to the nearest neighbour** (other item, door, radiator or wall) in all four directions.
- Walls facing the camera are **cut away** automatically (still casting shadows); camera presets (overview, plan, eye-level views from door/seat/window).
- **Day / evening** presets and **individually switchable lights**; brightness slider.
- Toggles for room dimensions, grid, **all numbers**, **gap distances**; colour options for key textiles (sofa, rug …); a **collapsible control panel**.

## 3. Iterating with the user

- Make **small, targeted edits** to the existing file (Edit tool / small scripted replacements) rather than regenerating it – the user is reloading the same file and expects everything else to stay put.
- When something moves, **re-check its neighbours** and move them too if they would collide (coffee table vs. sofa, cabinets vs. door swing, chairs vs. walkway). Verify numerically – a few lines of `node -e` computing extents is enough – and tell the user what else you moved and why.
- Say what changed in user terms (cm, positions relative to walls/door/windows), mention trade-offs you made (e.g. "TV is now 55 cm off-centre from the sofa"), and offer the one or two most relevant alternatives instead of a long menu.
- Read instructions literally and from the user's viewpoint: "left of the TV" is as seen from the seat; "not the whole bookshelf, only the middle row"; "the *other* water stone". If you misread something, say so plainly and fix it.
- Respect earlier decisions (e.g. heating stays free, no green, storage wall-mounted) when making later changes.

## 4. Verifying every change

You usually cannot see the rendered page, so check what you can and be honest about the rest:

- Run `python3 scripts/check_syntax.py <file.html>` after each edit – it extracts the module script and runs `node --check`.
- Watch for runtime traps a syntax check misses (listed in `references/architecture.md` → *Pitfalls*), especially use-before-declare of `const`s and wrong box orientation.
- In the reply, say that the code was syntax-checked but not visually verified, and ask the user to look at the specific thing that could be off (e.g. light brightness).

## Design defaults that worked well

- Keep heating and door swings free; leave ~30 cm or more between a door frame and furniture; keep main walkways ≥ 60–90 cm.
- Wall-mounted storage ~20 cm above the floor (easy cleaning), closed at the bottom, mix of closed / open / glass fronts, symmetric composition, a common top line with a gap below the ceiling for indirect light.
- Things on open shelves need support (book box, bookends); free-standing items need power (add sockets and cable).
- Warm, calm palettes: light wood, white ceiling, softly coloured walls; offer colour options rather than guessing one.
