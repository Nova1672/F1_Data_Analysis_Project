# F1 Race Intelligence

F1 Race Intelligence is a Python project for exploring Formula 1 session data
from OpenF1 and developing reusable race-analysis tools.

## Current status

Phase 1 data exploration is complete. The repository includes sample raw CSV
datasets, a discovery notebook, a local CSV loader, timestamp synchronization
helpers, and an initial driver snapshot implementation. This is a foundation
for further development, not a finished replay application.

Dynamic session selection, live race replay, and a FastAPI backend are not
implemented.

## Existing structure

- `data/raw/`: sample race datasets; keep these source files unchanged.
- `notebooks/01_data_discovery.ipynb`: exploratory API and data analysis.
- `src/data/loader.py`: reads the configured local CSV datasets.
- `src/race_engine/synchronization.py`: timestamp row-selection helpers.
- `src/race_engine/snapshot.py`: preliminary driver snapshot builder.
- `test_snapshot.py`: manually runnable snapshot example.
- `tests/`: automated tests for the existing behavior.

The loader currently loads all configured CSV files from `data/raw/`; it does
not select a session dynamically.

## Environment setup

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project and test dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the snapshot example

```powershell
python test_snapshot.py
```

The example uses the local raw CSVs and requests the existing sample snapshot
for driver 44 at lap 28.

## Run tests

```powershell
python -m pytest --import-mode=importlib
```

The import mode avoids a module-name collision between the preserved root
example (`test_snapshot.py`) and the automated test (`tests/test_snapshot.py`).