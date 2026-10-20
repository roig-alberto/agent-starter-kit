# Exporting a claude.ai Design canvas to plain HTML and PNG

Use this to hand a claude.ai Design canvas to a builder. A `.dc.html` artboard is plain HTML plus editor
wrappers, so a static frame renders in any browser after four edits. The recipe was proven on 77 frames,
first try, in agent-factory (2026-10-12).

1. `Artifact read` the canvas files to a local folder (or use the folder you published from).
2. For each artboard, drop the `<script src="./support.js"></script>` line and the
   `<script type="text/x-dc" ...>...</script>` block; strip the `<x-dc>` / `<helmet>` tags (keep their
   contents); rewrite `href="X.dc.html"` to `href="X.html"`; and replace any `{{holes}}` with literal
   text.
3. Serve the folder (`python3 -m http.server`) and shoot each frame at its canvas size:
   `ui-check http://127.0.0.1:PORT/html/X.html --width W --height H --shot png/X.png`.
4. Ship `source/` (the original `.dc.html` + `canvas.json`), `html/`, `png/`, a `manifest.json`, and an
   `index.html` gallery grouped by the canvas `title1` notes. Reference implementation:
   `~/projects/agent-factory/ui/wireframes/`.

Interactive frames (handlers, `<sc-for>`) need the editor runtime; this recipe is for static frames only.
