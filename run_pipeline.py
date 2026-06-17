"""Run the full reproduction pipeline and save all artifacts."""

from __future__ import annotations

import json

import pandas as pd

from src.data_loading import load_train_test
from src.eda import (
    plot_class_distribution,
    plot_correlation_heatmap,
    plot_missing_values,
    plot_numeric_distributions,
    plot_outlier_boxplots,
    plot_service_attack_crosstab,
    save_data_overview,
)
from src.error_analysis import extract_error_examples, summarize_error_patterns
from src.evaluation import build_comparison_table, evaluate_model_bundle
from src.models import train_models
from src.preprocessing import detect_redundant_features
from src.utils import METRICS_DIR, TABLES_DIR, ensure_output_dirs


def main() -> None:
    ensure_output_dirs()
    train_df, test_df = load_train_test()

    save_data_overview(train_df, prefix="train")
    save_data_overview(test_df, prefix="test")
    plot_class_distribution(train_df, prefix="train")
    plot_class_distribution(test_df, prefix="test")
    plot_missing_values(train_df, prefix="train")
    plot_numeric_distributions(train_df, prefix="train")
    plot_outlier_boxplots(train_df, prefix="train")
    plot_service_attack_crosstab(train_df, prefix="train")
    plot_correlation_heatmap(train_df, prefix="train")

    redundancy = detect_redundant_features(train_df)
    with (TABLES_DIR / "redundant_feature_report.json").open("w", encoding="utf-8") as handle:
        json.dump(redundancy, handle, indent=2)

    trained_official = train_models(train_df, test_df, use_official_test=True)
    trained_author = train_models(train_df, test_df, use_official_test=False)

    def evaluate_bundle(trained, prefix: str) -> dict[str, dict]:
        lr = evaluate_model_bundle(
            trained,
            f"{prefix}_logistic_regression",
            trained.logistic_regression,
            trained.x_test_processed,
            trained.y_test.values,
        )
        rf = evaluate_model_bundle(
            trained,
            f"{prefix}_random_forest",
            trained.random_forest,
            trained.x_test_processed,
            trained.y_test.values,
        )
        iso_pred = (trained.isolation_forest.predict(trained.x_test_processed) == -1).astype(int)

        class IsoWrapper:
            def predict(self, x):
                return iso_pred

        iso = evaluate_model_bundle(
            trained,
            f"{prefix}_isolation_forest",
            IsoWrapper(),
            trained.x_test_processed,
            trained.y_test.values,
            use_proba=False,
        )
        return {
            "logistic_regression": lr,
            "random_forest": rf,
            "isolation_forest": iso,
        }

    official_results = evaluate_bundle(trained_official, "official")
    author_results = evaluate_bundle(trained_author, "author_split")

    comparison = build_comparison_table(official_results)
    author_comparison = build_comparison_table(author_results)
    author_comparison.to_csv(TABLES_DIR / "author_split_model_comparison.csv")

    rf_pred = trained_official.random_forest.predict(trained_official.x_test_processed)
    extract_error_examples(
        trained_official.x_test,
        trained_official.y_test,
        rf_pred,
        original_labels=test_df.loc[trained_official.x_test.index, "label"],
    )
    summarize_error_patterns(trained_official.x_test, trained_official.y_test, rf_pred)

    summary = {
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "official_test_best_supervised_model": "random_forest",
        "official_test_metrics": official_results,
        "author_split_random_forest_metrics": author_results["random_forest"],
        "author_split_comparison": author_results,
    }
    with (METRICS_DIR / "run_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print("Pipeline completed.")
    print(comparison)


if __name__ == "__main__":
    main()
