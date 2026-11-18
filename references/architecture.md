# Architecture of the reference planner

`assets/example-living-room.html` is one self-contained file: CSS + control panel markup + one `<script type="module">`. three.js r160 is loaded through an import map from jsDelivr (`three` and `three/addons/`). Section headers in the script look like `// ---------------------------------------------------------------- name` or `// ---- name`.

## Contents
1. Coordinate system and conventions
2. Section map (engine vs. room-specific)
3. Key patterns
4. Adapting to other rooms
5. Pitfalls we hit (and how to avoid them)

## 1. Coordinate system and conventions

- 1 scene unit = 1 metre. `y` is up. Floor at `y = 0`, ceiling at `y = H`.
- Room interior spans `x ∈ [X0, X1]` (width `W`, west → east) and `z ∈ [Z0, Z1]` (depth `D`, north → south), centred on the origin. Walls (thickness `T`) sit **outside** these bounds, so all furniture distances are measured to the inner wall faces.
- In the example: north wall (`z = Z0`) = window wall, west wall (`x = X0`) = door + storage, east wall (`x = X1`) = sofa, south wall (`z = Z1`) = back wall. In the plan view north is at the top.
- **Furniture builders** create a `THREE.Group` in **local** coordinates: origin on the floor at the footprint centre, length along local `x`, depth along local `z`, **front facing local +z**. Placement then uses `rotY`:
  - `rotY = 0` → front faces +z (south), `π` → north, `π/2` → front faces +x (east), `−π/2` → front faces −x (west).
  - With `rotY = π/2`, local `x` maps to world `−z`; with `−π/2`, local `x` maps to world `+z`.
- `THREE.BoxGeometry(w, h, d)` = sizes along **x, y, z** of the parent frame. A strip that runs "along the west wall" in world space needs its long side on **z**, not x.

## 2. Section map

| Section (header in the file) | Reusable? | Notes |
|---|---|---|
| CSS + `#ui` panel markup, `#card`, `#scalebar`, `#hint` | engine | Panel is collapsible (`#uiToggle`, state in `localStorage` wrapped in try/catch). Add/remove buttons per room. |
| Import map + imports (`OrbitControls`, `RoundedBoxGeometry`, `RectAreaLightUniformsLib`) | engine | Keep versions pinned. |
| Room definition (`W, D, H, T, SILL, WIN_TOP, DOOR`) | **room config** | First thing to change. |
| renderer / cameras / controls (`perspCam`, `planCam` orthographic, `PLAN_HALF`) | engine | Adjust `PLAN_HALF` so the whole room + scale bar fits the plan view. |
| helpers (`mat`, `mesh`, `box`, `rbox`, `cyl`, `canvasTex`) | engine | `RoundedBoxGeometry` radius must be < half the smallest side. |
| procedural textures (wood planks, rug palettes, fabric, art, sky gradients) | engine (+ palettes are config) | No external images needed. |
| shared materials `M` | engine | |
| item registry `item(name, group, opts)` | engine | Measures the group's **local** bounding box before placing it; opts: `pos`, `rotY`, `parent`, `extra` (info lines), `round` (shows Ø), `box` (override size), `clearance`. |
| floor, slab, ceiling | engine | Ceiling is a plane facing down (see patterns). |
| walls: `makeWall`, `setCut`, wall segments, baseboards | engine + **config** | Segments describe solid parts around openings. |
| windows, door | **room config** | Window frames/glass/sill, door leaf/casing/jambs. |
| radiators, curtains | **room config** | |
| furniture builders + placements | **room-specific** | Replace with what the room needs. |
| `cabinet()` + `fillSlot()` | engine | Board-built cabinets with closed (optionally fluted), **open** or **glass** sections; `fillSlot` fills open/glass compartments with books, glasses, decor, baskets. |
| storage wall block (`MEDIA`), TV, sockets, indirect light | room-specific, good template for any built-in storage | Shows wall-mounted storage, symmetric layout, swivel TV, socket + cable, LED strips. |
| lights: ceiling disc, wall lamp, floor lamp, small lamp, indirect | template | Each light = real light + emissive material; registered in `lightState`. |
| outside (ground, hedge, trees) | engine | Gives the windows something to show. |
| annotations: `makeLabel`, `dimLine`, room dims, door swing, scale bar, grid | engine | All label sprites obey the global `showNumbers`. |
| lighting: hemisphere + sun (shadows), `lightState`, `applyLights`, `setMode` | engine + config | Day/evening presets set `lightState`, users toggle individual lights. |
| views (`VIEWS`, `setView`) | engine + config | Eye-level presets reference furniture positions. |
| toggles (dims, grid, numbers, gaps), colour options, panel collapse | engine | |
| double-click selection: `select`, `computeGaps`, `drawGaps`, card | engine | |
| loop: cut-away update, plan scale bar, camera animation | engine | |

## 3. Key patterns

**Item registry & measurements.** Every selectable object goes through `item()`. The orange overlay is added as a child of the item, so it uses the item's local frame (width/depth/height lines follow the rotation). The card shows width = larger horizontal extent, depth = smaller, `Ø` for `round` items, "bottom edge above floor" for wall-mounted items, then the gap list.

**Gaps to neighbours (`computeGaps`).** For each of the four floor directions, take the item's world AABB face and find the nearest obstacle: other items whose height range overlaps (> 1 cm) and whose perpendicular range overlaps (3 cm tolerance), or the wall plane if the item is inside the room on that axis. Skip flat/soft things (`GAP_SKIP`: rug, curtains, the room itself) and ancestors/descendants. Gaps < 1 cm count as "touching". Lines are drawn in world space (`gapOverlay`), blue, with labels like `52.5 cm → Door`.

**Wall cut-away.** Each wall has an outward normal and a point. When the camera is outside a wall, `setCut` sets `colorWrite = false` / `depthWrite = false` on that wall's (cloned) materials – it disappears visually but **still casts shadows** (sunlight through windows stays right) – shows a low "stub" footprint and hides objects in `wall.attached` (wall-mounted things). Not done in plan view.

**Ceiling.** A plane rotated to face down with `FrontSide`: invisible from above (overview/plan) but visible from inside and still casting shadows. To make it read white, give it a little emissive and keep the hemisphere light's ground colour neutral – a brownish ground colour makes downward-facing surfaces look beige.

**Plan view.** `OrthographicCamera` with `up = (0,0,−1)` (north up), its own `OrbitControls` with rotation disabled (pan + zoom). Pixels per metre = `innerHeight / ((top − bottom) / zoom)`; the HTML scale bar picks 25 cm / 50 cm / 1 m / 2 m / 5 m. Hide ceiling-mounted fixtures in plan view so tables stay visible (lights stay on: lights are re-parented to the scene with `scene.attach`).

**Lights.** `lightState = {indirect, ceiling, wall, floor, small, …}`, `applyLights()` sets light intensities and emissive intensities from it, buttons toggle single keys, "All off" clears all, `setMode('day'|'evening')` assigns a preset then calls `applyLights()`. If a light is a child of a group that may be hidden (wall cut-away, plan view), move it to the scene with `scene.attach(light)` after placing the group.

**Indirect light.** LED strips (thin emissive boxes **along the wall**) on top of the storage + a `RectAreaLight` pointing up (`rotation.x = π/2`) + a soft glow plane on the wall strip above + an `AmbientLight` "bounce fill" for the room. Avoid big down-facing area lights or ceiling glow planes – they produce visible bands/edges that users find strange.

**Colour options.** Keep colour on shared materials (`boucle`, `pillowMats`, `rugTopMat` …) and swap `.color` / `.map` in a `setXxx(key)` function driven by a button row. Generate pattern textures per palette lazily and cache them.

**Numbers / gaps toggles.** `makeLabel` marks sprites with `userData.isLabel` and sets `visible = showNumbers`; the toggle traverses the scene. Gap overlay visibility follows `showGaps`.

**Cabinets.** `cabinet(w, h, d, sections, {fluted, body, open: [i], glass: [i]})` builds boards (top, bottom, sides, back, dividers) so open/glass sections are really hollow; closed sections get (fluted) doors. `g.userData.slots` lists open compartments for `fillSlot(g, slot, depth, kind)` with `kind` ∈ `books | decor | basket | device | glasses | wine | tumblers`.

## 4. Adapting to other rooms

- **Openings on other walls.** Wall segments are plain boxes: for a wall with an opening, split it into the parts left/right of the opening plus a part above (and below for windows). Mirror the door code (casing, jambs, leaf, handle, swing arc in `dims`) for the wall you need; the door's item `box` override should be the wall opening.
- **Sloped ceilings / alcoves.** Add extra wall or ceiling segments as boxes; keep the cut-away logic per wall plane.
- **Bedroom.** Bed (mattress height ~50–55 cm, headboard), bedside tables, wardrobe (60 cm deep, doors need ~60–90 cm in front, sliding doors less), optional desk. Keep 60–70 cm beside the bed.
- **Kitchen.** Base cabinets 60 cm deep with 90 cm worktop height, wall cabinets 35 cm deep starting ~50–60 cm above the worktop, tall units; sink / hob / fridge as items so gaps (work triangle, landing space) can be checked; aisle 100–120 cm.
- **Home office.** Desk 72–75 cm high, 70–80 cm deep, chair clearance 90–100 cm behind the desk edge, shelving, task light, sockets.
- **Bathroom.** Fixtures as items with their required free areas (in front of WC/basin ~70 cm), wall-hung units, mirror cabinet.
- Reuse `cabinet()` for wardrobes, kitchen units and shelving; reuse lights, sockets and textiles patterns; add a colour-option row for whatever the user cares about (bed linen, kitchen fronts, desk top).

## 5. Pitfalls we hit (and how to avoid them)

- **Box orientation**: an LED strip meant to run along the west wall was built with its long side on x and stuck out of the room as a "white line". Check which axis a long thin box should run on.
- **Use before declare**: a `const` (e.g. `tvZ`) used by code placed earlier in the file throws at runtime (TDZ) even though `node --check` passes. Define configuration constants before everything that uses them; when moving blocks, re-check order.
- **Children of hidden groups**: lights inside a group that gets hidden (cut-away wall, plan view) switch off with it – re-parent lights to the scene.
- **Raycasting hidden things**: three.js raycasts invisible objects too; filter by walking up `visible` and skip materials with `colorWrite === false`.
- **Sprites in raycasts** need `raycaster.camera` (set by `setFromCamera`).
- **Overlapping coplanar wall boxes** z-fight at the corners: let one pair of walls span the full outer length and the other pair only the inner length.
- **Ceiling looks beige**: see the ceiling pattern above.
- **Things that wouldn't stand in reality**: books in an open niche need a box or bookends; a TV standing on a sideboard needs a foot and a socket behind it; swivelling a TV needs depth and width clearance – compute the rotated corners.
- **Moving one thing collides with others**: after any move, compute extents of the neighbours (chaise vs. shelf, coffee table vs. sofa, door swing vs. shelf) and adjust.
- **Light tuning is invisible to you**: intensities are educated guesses; expose a brightness slider and ask the user to judge.
