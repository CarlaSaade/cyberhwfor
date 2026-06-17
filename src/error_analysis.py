"""False positive / false negative analysis."""

from __future__ import annotations

import pandas as pd

from src.utils import TABLES_DIR, ensure_output_dirs


def extract_error_examples(
    x_test: pd.DataFrame,
    y_test: pd.Series,
    y_pred: pd.Series | list,
    original_labels: pd.Series | None = None,
    max_examples: int = 10,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return false positive and false negative examples."""
    ensure_output_dirs()
    analysis = x_test.copy()
    analysis["actual"] = y_test.values
    analysis["predicted"] = list(y_pred)
    if original_labels is not None:
        analysis["attack_type"] = original_labels.values

    false_positives = analysis[(analysis["actual"] == 0) & (analysis["predicted"] == 1)].head(max_examples)
    false_negatives = analysis[(analysis["actual"] == 1) & (analysis["predicted"] == 0)].head(max_examples)

    false_positives.to_csv(TABLES_DIR / "false_positive_examples.csv", index=False)
    false_negatives.to_csv(TABLES_DIR / "false_negative_examples.csv", index=False)

    combined = pd.concat(
        [
            false_positives.assign(error_type="false_positive"),
            false_negatives.assign(error_type="false_negative"),
        ],
        ignore_index=True,
    )
    combined.to_csv(TABLES_DIR / "error_examples.csv", index=False)
    return false_positives, false_negatives


def summarize_error_patterns(
    x_test: pd.DataFrame,
    y_test: pd.Series,
    y_pred: pd.Series | list,
) -> pd.DataFrame:
    """Summarize common patterns among misclassified samples."""
    ensure_output_dirs()
    errors = x_test.copy()
    errors["actual"] = y_test.values
    errors["predicted"] = list(y_pred)
    errors = errors[errors["actual"] != errors["predicted"]]

    summary_rows = []
    for column in ["protocol_type", "service", "flag"]:
        grouped = (
            errors.groupby(column)["actual"]
            .count()
            .rename("error_count")
            .reset_index()
            .sort_values("error_count", ascending=False)
            .head(5)
        )
        grouped["feature"] = column
        summary_rows.append(grouped)

    summary = pd.concat(summary_rows, ignore_index=True)
    summary.to_csv(TABLES_DIR / "error_pattern_summary.csv", index=False)
    return summary
