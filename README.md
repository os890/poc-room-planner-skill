# room-planner skill

A Claude skill for planning and furnishing any room as an interactive, true-to-scale 3D model in a single local HTML file (three.js), refined step by step in conversation.

## Install

Copy this folder into your skills directory and name it after the skill:

```bash
cp -r room-planner-skill ~/.claude/skills/room-planner
```

(or into a project's `.claude/skills/room-planner/`). Then start a session with something like:

> Plan my bedroom: 3.5 × 4 m, ceiling 2.5 m, window on the short wall, door in the corner opposite. I need a 160 cm bed, a wardrobe and a small desk.

## Contents

- `SKILL.md` – workflow: gather facts, build from the reference engine, iterate, verify.
- `references/architecture.md` – section map of the reference file, key patterns, how to adapt to other rooms, pitfalls.
- `references/clearances.md` – ergonomic distances and typical sizes per room type.
- `assets/example-living-room.html` – complete reference implementation (4 × 5 m living room). Open it in a browser to see all features.
- `scripts/check_syntax.py` – extracts the module script from the HTML and runs `node --check`.

The page loads three.js from cdn.jsdelivr.net in the browser; everything else is local.

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
