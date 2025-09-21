# Repository Guidelines

## Project Structure & Module Organization
- Keep production code in `src/ant/`, grouped by domain (`src/ant/simulation/`, `src/ant/visualization/`) with shared helpers in `src/ant/utils/`.
- Configuration files belong in `config/` (YAML or JSON); name per scenario (`config/foraging.yaml`) and load them through the CLI layer.
- Tests mirror the package inside `tests/`, data assets live under `data/` (`data/raw/`, `data/processed/`), and exploratory notebooks stay in `notebooks/` outside packaging.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — create and enter the local virtual environment.
- `pip install -e .[dev]` — install the package plus dev tooling once `pyproject.toml` lands; rerun whenever dependencies change.
- `pip install -e .[viz]` — pull in Matplotlib support for the graphical renderer; combine extras (`pip install -e .[dev,viz]`) when you need both stacks.
- `ruff check src tests` — lint and format; add `--fix` for safe rewrites.
- `pytest --maxfail=1 --disable-warnings` — run the suite quickly; append `--cov=ant --cov-report=term-missing` before submitting a PR.

## Coding Style & Naming Conventions
- Target Python 3.11; document this constraint in `pyproject.toml` when it is added.
- Use `snake_case` for functions and variables, `PascalCase` for classes, and `CAPS_WITH_UNDERSCORES` for shared constants in `config.py`.
- Keep functions focused (<50 lines), favor explicit imports, and open modules with a docstring describing the scenario.
- Run `ruff format` (or `black` if introduced) before committing to avoid whitespace churn.

## Testing Guidelines
- Unit tests sit in `tests/<module>/test_<feature>.py`; integration suites go in `tests/integration/`.
- Model fixtures with `pytest` factories stored in `tests/factories/` to keep setup repeatable.
- Preserve ≥90% coverage on new work and never reduce the global number without sign-off noted in the PR.
- Add regression tests for every bug fix and reference the issue in the test docstring.

## Commit & Pull Request Guidelines
- Use imperative, scope-prefixed messages (`feat: add pheromone decay model`) and squash trivial fixups locally.
- Link issues with `Fixes #123` when applicable and add design doc URLs for multi-module work.
- PR descriptions should cover intent, solution outline, validation steps, and follow-up tasks; attach screenshots or CLI traces for user-visible changes.
- Confirm lint (`ruff check`) and tests (`pytest --cov=ant`) succeed locally before requesting review and call out any known flakiness in the PR.

## Running Simulations
- ASCII backend (default): `ant-sim --steps 500 --interval 0.05` renders in the terminal; add `--no-clear` to inspect historic frames.
- Matplotlib backend: install extras via `pip install -e .[viz]`, then run `ant-sim --backend mpl --steps 500 --interval 0.05`. Use `--no-show` for headless runs (CI) and `--save-path out.gif --save-format gif --save-fps 15 --save-writer pillow` to export animations; omit `--save-format` when the file extension matches the desired format.
- Topology showcase: try `--topology projective`, `--topology klein`, or `--topology sphere_diag` (adjacent edges pair into a double-cone sphere; square grids only); chain `--ant x,y,heading,color` flags to preseed multiple agents.
- Trail tuning: `--trail-lifetime 30` extends how long colored trails remain; set it to `0` to disable trails entirely.
- Frame skipping: `--steps-per-frame 50` advances 50 simulation steps between renders, dramatically speeding up recordings.
