"""Preprocessing pipelines for NSL-KDD intrusion detection."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data_loading import (
    get_categorical_columns,
    get_feature_columns,
    get_numeric_columns,
)
from src.utils import RANDOM_STATE


def build_preprocessor() -> ColumnTransformer:
    """Build a leakage-safe preprocessing transformer."""
    numeric_cols = get_numeric_columns()
    categorical_cols = get_categorical_columns()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            )
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ]
    )


def apply_smote(
    x_train: np.ndarray,
    y_train: Iterable[int],
    random_state: int = RANDOM_STATE,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply SMOTE on the training set only."""
    smote = SMOTE(random_state=random_state)
    return smote.fit_resample(x_train, y_train)


def build_logistic_regression_pipeline() -> ImbPipeline:
    """Baseline model with preprocessing and SMOTE."""
    return ImbPipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("smote", SMOTE(random_state=RANDOM_STATE)),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def build_random_forest_pipeline():
    """Author-style Random Forest pipeline without SMOTE inside sklearn Pipeline.

    SMOTE is applied manually after preprocessing in the training notebook/script
    because the original tutorial resamples encoded features separately.
    """
    from sklearn.ensemble import RandomForestClassifier

    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    max_depth=20,
                    min_samples_split=5,
                    class_weight="balanced",
                    n_jobs=-1,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Extract feature matrix and binary target from a dataframe."""
    feature_cols = get_feature_columns()
    x = df[feature_cols].copy()
    y = df["binary_label"].copy()
    return x, y


def detect_redundant_features(df: pd.DataFrame, correlation_threshold: float = 0.95) -> dict:
    """Detect constant, duplicated, and highly correlated numeric columns."""
    numeric_df = df[get_numeric_columns()].copy()
    constant_cols = [col for col in numeric_df.columns if numeric_df[col].nunique(dropna=False) <= 1]
    duplicated_cols = [
        col
        for col in numeric_df.columns
        if numeric_df[col].duplicated(keep=False).all()
        and numeric_df[col].equals(numeric_df.iloc[:, 0])
    ]

    corr_matrix = numeric_df.corr(method="spearman").abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    highly_correlated = [
        f"{column} ~ {row}"
        for column in upper.columns
        for row in upper.index
        if pd.notna(upper.loc[row, column]) and upper.loc[row, column] >= correlation_threshold
    ]

    return {
        "constant_columns": constant_cols,
        "duplicated_columns": duplicated_cols,
        "highly_correlated_pairs": highly_correlated[:25],
    }
