"""Exploratory data analysis helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.data_loading import get_numeric_columns
from src.utils import FIGURES_DIR, TABLES_DIR, ensure_output_dirs


def save_data_overview(df: pd.DataFrame, prefix: str = "train") -> None:
    """Save overview tables for loading/inspection section."""
    ensure_output_dirs()

    overview = pd.DataFrame(
        {
            "column": df.columns,
            "dtype": df.dtypes.astype(str).values,
            "missing_values": df.isna().sum().values,
            "n_unique": df.nunique(dropna=False).values,
        }
    )
    overview.to_csv(TABLES_DIR / f"{prefix}_column_overview.csv", index=False)

    class_distribution = df["binary_label"].value_counts().rename_axis("class").reset_index(name="count")
    class_distribution["class_name"] = class_distribution["class"].map({0: "normal", 1: "attack"})
    class_distribution.to_csv(TABLES_DIR / f"{prefix}_class_distribution.csv", index=False)

    attack_distribution = (
        df["label"].value_counts().rename_axis("attack_type").reset_index(name="count")
    )
    attack_distribution.to_csv(TABLES_DIR / f"{prefix}_attack_type_distribution.csv", index=False)


def plot_class_distribution(df: pd.DataFrame, prefix: str = "train") -> Path:
    """Plot binary class distribution."""
    ensure_output_dirs()
    fig, ax = plt.subplots(figsize=(6, 4))
    counts = df["binary_label"].value_counts().sort_index()
    labels = ["normal", "attack"]
    sns.barplot(x=labels, y=counts.values, ax=ax, hue=labels, legend=False, palette="Set2")
    ax.set_title(f"Binary Class Distribution ({prefix})")
    ax.set_ylabel("Count")
    output = FIGURES_DIR / f"{prefix}_class_distribution.png"
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output


def plot_missing_values(df: pd.DataFrame, prefix: str = "train") -> Path:
    """Plot missing values per column."""
    ensure_output_dirs()
    missing = df.isna().sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    missing.plot(kind="bar", ax=ax, color="#4C72B0")
    ax.set_title(f"Missing Values by Column ({prefix})")
    ax.set_ylabel("Missing count")
    output = FIGURES_DIR / f"{prefix}_missing_values.png"
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output


def plot_numeric_distributions(df: pd.DataFrame, prefix: str = "train", max_cols: int = 8) -> Path:
    """Plot histograms for selected numeric features."""
    ensure_output_dirs()
    numeric_cols = get_numeric_columns()[:max_cols]
    fig, axes = plt.subplots(2, 4, figsize=(14, 7))
    axes = axes.flatten()
    for ax, col in zip(axes, numeric_cols):
        sns.histplot(df[col], kde=False, ax=ax, bins=30)
        ax.set_title(col)
    fig.suptitle(f"Numeric Feature Distributions ({prefix})")
    output = FIGURES_DIR / f"{prefix}_numeric_distributions.png"
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output


def plot_correlation_heatmap(df: pd.DataFrame, prefix: str = "train") -> Path:
    """Plot Spearman correlation heatmap for numeric features."""
    ensure_output_dirs()
    corr = df[get_numeric_columns()].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax)
    ax.set_title(f"Spearman Correlation Heatmap ({prefix})")
    output = FIGURES_DIR / f"{prefix}_spearman_correlation.png"
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    corr.to_csv(TABLES_DIR / f"{prefix}_spearman_correlation.csv")
    return output


def plot_service_attack_crosstab(df: pd.DataFrame, prefix: str = "train") -> Path:
    """Plot crosstab between service and attack label."""
    ensure_output_dirs()
    crosstab = pd.crosstab(df["service"], df["binary_label"])
    crosstab.to_csv(TABLES_DIR / f"{prefix}_service_attack_crosstab.csv")
    top_services = df["service"].value_counts().head(10).index
    subset = crosstab.loc[top_services]
    fig, ax = plt.subplots(figsize=(10, 5))
    subset.plot(kind="bar", stacked=True, ax=ax, color=["#55A868", "#C44E52"])
    ax.set_title("Top Services vs Attack Label")
    ax.set_xlabel("service")
    ax.set_ylabel("count")
    output = FIGURES_DIR / f"{prefix}_service_attack_crosstab.png"
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output


def plot_outlier_boxplots(df: pd.DataFrame, prefix: str = "train") -> Path:
    """Plot boxplots for outlier inspection on selected numeric columns."""
    ensure_output_dirs()
    selected = ["duration", "src_bytes", "dst_bytes", "count", "srv_count", "serror_rate"]
    melted = df[selected].melt(var_name="feature", value_name="value")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(data=melted, x="feature", y="value", ax=ax)
    ax.set_title(f"Outlier Analysis ({prefix})")
    output = FIGURES_DIR / f"{prefix}_outlier_boxplots.png"
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output
