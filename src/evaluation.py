"""Evaluation metrics and visualizations."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    fbeta_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from src.utils import FIGURES_DIR, METRICS_DIR, TABLES_DIR, ensure_output_dirs


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
    beta: float = 2.0,
) -> dict[str, float]:
    """Compute standard cybersecurity classification metrics."""
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(fbeta_score(y_true, y_pred, beta=1.0, zero_division=0)),
        f"f{int(beta)}": float(fbeta_score(y_true, y_pred, beta=beta, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
    }
    if y_proba is not None and len(np.unique(y_true)) > 1:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba))
    return metrics


def evaluate_model_bundle(
    models,
    model_name: str,
    estimator,
    x_test_processed: np.ndarray,
    y_test: np.ndarray,
    use_proba: bool = True,
) -> dict:
    """Evaluate one classifier and persist artifacts."""
    ensure_output_dirs()
    y_pred = estimator.predict(x_test_processed)
    y_proba = estimator.predict_proba(x_test_processed)[:, 1] if use_proba else None
    metrics = compute_classification_metrics(y_test, y_pred, y_proba)

    report = classification_report(
        y_test,
        y_pred,
        target_names=["normal", "attack"],
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(
        cm,
        index=["actual_normal", "actual_attack"],
        columns=["pred_normal", "pred_attack"],
    )
    cm_df.to_csv(TABLES_DIR / f"confusion_matrix_{model_name}.csv")

    metrics_path = METRICS_DIR / f"{model_name}_metrics.json"
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump({"metrics": metrics, "classification_report": report}, handle, indent=2)

    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
    ax.set_title(f"Confusion Matrix - {model_name}")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_xticklabels(["normal", "attack"])
    ax.set_yticklabels(["normal", "attack"])
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"confusion_matrix_{model_name}.png", dpi=150)
    plt.close(fig)

    if y_proba is not None:
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.plot(fpr, tpr, label=f"AUC={metrics.get('roc_auc', 0):.4f}")
        ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
        ax.set_title(f"ROC Curve - {model_name}")
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / f"roc_curve_{model_name}.png", dpi=150)
        plt.close(fig)

    return metrics


def build_comparison_table(results: dict[str, dict[str, float]]) -> pd.DataFrame:
    """Create and save a model comparison table."""
    ensure_output_dirs()
    comparison = pd.DataFrame(results).T.sort_values("f1", ascending=False)
    comparison.to_csv(TABLES_DIR / "model_comparison.csv")
    return comparison
