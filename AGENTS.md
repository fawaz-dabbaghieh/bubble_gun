# Repository Guidelines

## Project Structure & Module Organization
- `BubbleGun/` holds the Python package and CLI implementation (entry point: `BubbleGun/main.py`).
- `BubbleGun/archiv/` contains older or experimental utilities; treat as legacy unless referenced.
- `example/` includes small sample inputs/outputs (e.g., `paper_example2.gfa`).
- `use_cases/` documents real datasets and workflows.
- `images/` stores figures used in documentation.
- `test/` currently only has sample GFA files, not automated tests.

## Build, Test, and Development Commands
- `pip install BubbleGun` installs from PyPI for end users.
- `python3 setup.py install` installs from the local source tree.
- If you build the C++ extension, run imports from outside the repo to avoid shadowing site-packages; or build locally with `python setup.py build_ext --inplace`.
- `BubbleGun -h` shows CLI help and available subcommands.
- `BubbleGun -g example/paper_example2.gfa bchains --bubble_json out.json` runs a basic bubble-chain extraction.

## Troubleshooting (C++ Extension)
- If `BubbleGun._graph_cpp` is missing, confirm `python -m pip install . -v` shows `build_ext` and that the extension lands in the installed package directory.
- If the extension builds but Python still uses the pure-Python class, run imports outside the repo root or build in place with `python setup.py build_ext --inplace`.
- In conda, ensure a compiler toolchain is available; use `--no-build-isolation` if build deps are already installed.

## Coding Style & Naming Conventions
- Use Python 3 syntax with 4-space indentation.
- Prefer `snake_case` for functions/variables and `CamelCase` for classes.
- Keep modules focused; core graph logic lives in `BubbleGun/` (e.g., `Graph.py`, `Bubble.py`).
- No formatter or linter is configured; keep changes consistent with surrounding style.

## Testing Guidelines
- There is no automated test suite or test runner configured.
- When adding tests, follow `test_*.py` naming and keep fixtures in `test/`.
- If you validate changes manually, document the CLI command you used in the PR.

## Commit & Pull Request Guidelines
- Recent commits use short, descriptive, present-tense messages (e.g., "adding citation", "fixing the issue with the overlaps").
- Keep commits focused on one change area.
- PRs should include: a brief summary, linked issues if any, and example commands or outputs for CLI changes.
- Add screenshots only when documentation images are updated.

## Security & Configuration Notes
- Inputs are typically GFA/VG graph files; avoid committing large or sensitive datasets.
- Example data should stay in `example/` or `use_cases/` with clear provenance.
