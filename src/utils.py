"""Shared utilities for paths, seeds, and I/O helpers."""

from pathlib import Path

RANDOM_STATE = 42

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"
METRICS_DIR = RESULTS_DIR / "metrics"


def ensure_output_dirs() -> None:
    """Create standard output directories if they do not exist."""
    for directory in (FIGURES_DIR, TABLES_DIR, METRICS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def resolve_data_path(filename: str) -> Path:
    """Return path to a file inside the data directory."""
    return DATA_DIR / filename
