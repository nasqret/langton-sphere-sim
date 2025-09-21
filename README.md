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

## Example Commands

Run the CLI in headless mode (`MPLBACKEND=Agg` + `--no-show`) to crunch 100 000 steps quickly, saving only every 100th frame.

```bash
MPLBACKEND=Agg ant-sim --backend mpl --width 200 --height 200 \
      --steps 100000 --steps-per-frame 100 --interval 0 --topology projective \
      --trail-lifetime 5 --no-show \
      --ant 60,60,north,green \
      --ant 120,60,north,red \
      --ant 60,120,north,blue \
      --ant 120,120,north,cyan \
      --save-path runs/ants_proj.gif --save-format gif --save-fps 30
```
Projective plane GIF—edges glue with reversed orientation, so ants “jump” and mirror as they cross seams.

```bash
MPLBACKEND=Agg ant-sim --backend mpl --width 200 --height 200 \
      --steps 100000 --steps-per-frame 100 --interval 0 --topology sphere_diag \
      --trail-lifetime 5 --no-show \
      --ant 60,60,north,green \
      --ant 120,60,north,red \
      --ant 60,120,north,blue \
      --ant 120,120,north,cyan \
      --save-path runs/ants_spher.gif --save-format gif --save-fps 30
```
Folded-sphere digon GIF—adjacent edges funnel ants toward the two poles while the overlay tracks step counts.

```bash
MPLBACKEND=Agg ant-sim --backend mpl --width 200 --height 200 \
      --steps 100000 --steps-per-frame 100 --interval 0 --topology torus \
      --trail-lifetime 5 --no-show \
      --ant 60,60,north,green \
      --ant 120,60,north,red \
      --ant 60,120,north,blue \
      --ant 120,120,north,cyan \
      --save-path runs/ants_tor.gif --save-format gif --save-fps 10
```
Classic torus GIF, slowed to 10 fps so highway structures are easy to inspect.

```bash
MPLBACKEND=Agg ant-sim --backend mpl --width 200 --height 200 \
      --steps 100000 --steps-per-frame 100 --interval 0 --topology torus \
      --trail-lifetime 5 --no-show \
      --ant 60,60,north,green \
      --ant 120,60,north,red \
      --ant 60,120,north,blue \
      --ant 120,120,north,cyan \
      --save-path runs/ants_tor.mp4 --save-format mp4 --save-fps 30
```
Same torus scenario, exported to MP4—requires FFmpeg and yields a smoother video.

```bash
MPLBACKEND=Agg ant-sim --backend mpl --width 200 --height 200 \
      --steps 100000 --steps-per-frame 100 --interval 0 --topology klein \
      --trail-lifetime 5 --no-show \
      --ant 60,60,north,green \
      --ant 120,60,north,red \
      --ant 60,120,north,blue \
      --ant 120,120,north,cyan \
      --save-path runs/ants_klein.mp4 --save-format mp4 --save-fps 30
```
Klein bottle MP4—one axis mirrors, so ants flip orientation at every seam crossing.

```bash
MPLBACKEND=Agg ant-sim --backend mpl --width 200 --height 200 \
      --steps 100000 --steps-per-frame 100 --interval 0 --topology projective \
      --trail-lifetime 5 --no-show \
      --ant 60,60,north,green \
      --ant 120,60,north,red \
      --ant 60,120,north,blue \
      --ant 120,120,north,cyan \
      --save-path runs/ants_proj.mp4 --save-format mp4 --save-fps 30
```
Projective plane, now rendered at 30 fps for sharing or longer experiments.

```bash
MPLBACKEND=Agg ant-sim --backend mpl --width 200 --height 200 \
      --steps 100000 --steps-per-frame 100 --interval 0 --topology sphere_diag \
      --trail-lifetime 5 --no-show \
      --ant 60,60,north,green \
      --ant 120,60,north,red \
      --ant 60,120,north,blue \
      --ant 120,120,north,cyan \
      --save-path runs/ants_spher.mp4 --save-format mp4 --save-fps 30
```
Folded-sphere digon MP4—adjacent seams act as a double cone while the annotation tracks progress.

### Smaller set-ups and ASCII runs

```bash
ant-sim --width 60 --height 60 --steps 5000 --interval 0.02 --topology torus \
        --ant 30,30,north,magenta
```
Terminal-only (ASCII) run with a single ant; great for quick sanity checks.

```bash
ant-sim --width 80 --height 40 --steps 8000 --interval 0 --topology klein \
        --ant 20,10,north,yellow --ant 60,30,east,cyan --no-clear
```
Three ants on a rectangular Klein bottle in the terminal; `--no-clear` lets you watch the path build up.

```bash
MPLBACKEND=Agg ant-sim --backend mpl --width 120 --height 120 \
      --steps 20000 --steps-per-frame 20 --interval 0 --topology projective \
      --trail-lifetime 10 --no-show \
      --ant 40,40,north,orange --ant 80,80,west,purple \
      --save-path runs/projective_small.gif --save-format gif --save-fps 24
```
Smaller projective-plane GIF with just two ants; the higher trail lifetime keeps crossings visible.

## Development

Lint and tests:

```bash
ruff check src tests
pytest --maxfail=1
```

Refer to `AGENTS.md` for contributor workflow, coding standards, and testing expectations.
