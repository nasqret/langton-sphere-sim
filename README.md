# Langton Ant Simulator

A multi-agent Langton ant playground that supports torus, Klein bottle, and projective plane surfaces. The engine powers both a terminal-based renderer and an optional Matplotlib animation backend.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]        # tooling + tests (pytest, ruff)
pip install -e .[viz]        # optional Matplotlib backend
```

Matplotlib exports rely on external writers:
- GIF: Pillow support ships with Matplotlib; for smoother results install ImageMagick (`brew install imagemagick`).
- MP4: Requires FFmpeg (`brew install ffmpeg` or your package manager of choice).

## Running the Simulator

1. **Activate the virtual environment** each session: `source .venv/bin/activate`.
2. **Run the terminal renderer (default backend)**:
   ```bash
   ant-sim --steps 500 --interval 0.05 --topology torus
   ```
   - `--steps` controls how many simulation ticks execute after the initial frame.
   - `--interval` is the delay between frames in seconds (`0` runs as fast as possible).
   - `--topology {torus,klein,projective,sphere_diag}` selects the wrapping surface (the sphere variant pairs adjacent edges into a double-cone seam and only supports square grids).
   - `--no-clear` prevents the terminal from clearing between frames so you can scroll back.
3. **Spawn additional ants** by repeating `--ant x,y,heading,color` (headings: `north|east|south|west`). Example:
   ```bash
   ant-sim --ant 20,10,north,red --ant 21,10,west,blue
   ```
4. **Switch to the Matplotlib backend** when you need a graphical window or video export:
   ```bash
   ant-sim --backend mpl --steps 400 --interval 0.05 --topology sphere_diag
   ```
   - Add `--no-show` for headless environments (CI, servers).
   - Use `--save-path out.gif` to export an animation. Combine with `--save-format {gif,mp4}`, `--save-fps 24`, or `--save-writer pillow|imagemagick|ffmpeg` to control encoding.
   - Render less frequently with `--steps-per-frame 50` to skip drawing 50 computed steps between frames.
   - Adjust `--trail-lifetime 30` (default 20) to control how long trails remain visible.
   - Saved frames automatically include the current step count and topology label in the overlay.
5. **Headless batch export** example:
   ```bash
   ant-sim --backend mpl --steps 1200 --interval 0.02 \
       --save-path runs/projective.mp4 --save-format mp4 --save-fps 30 \
       --no-show
   ```

Tips:
- The origin `(0,0)` is the top-left cell; ants wrap according to the chosen topology.
- Trail colors accept Matplotlib names or hex codes (e.g., `#ff8800`).
- Trails fade after the configured lifetime; set `--trail-lifetime 0` to disable trails entirely.
- Combine `--steps-per-frame` with a small `--interval` (or `0`) to process thousands of steps while sampling only key frames.
- Keep one terminal on the ASCII backend while another renders exports for faster iteration.

## Development

Lint and tests:

```bash
ruff check src tests
pytest --maxfail=1
```

Refer to `AGENTS.md` for contributor workflow, coding standards, and testing expectations.
