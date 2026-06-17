"""Model training helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from src.data_loading import get_feature_columns
from src.preprocessing import apply_smote, build_preprocessor, split_features_target
from src.utils import RANDOM_STATE


@dataclass
class TrainedModels:
    """Container for trained models and data splits."""

    logistic_regression: LogisticRegression
    random_forest: RandomForestClassifier
    isolation_forest: IsolationForest
    preprocessor: object
    x_train: pd.DataFrame
    x_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    x_train_processed: np.ndarray
    x_test_processed: np.ndarray


def prepare_author_style_split(
    train_df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Reproduce the tutorial's random train/test split on the training file."""
    x, y = split_features_target(train_df)
    return train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )


def train_models(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame | None = None,
    use_official_test: bool = True,
) -> TrainedModels:
    """Train baseline, author-style Random Forest, and Isolation Forest."""
    if use_official_test and test_df is not None:
        x_train, y_train = split_features_target(train_df)
        x_test, y_test = split_features_target(test_df)
    else:
        x_train, x_test, y_train, y_test = prepare_author_style_split(train_df)

    preprocessor = build_preprocessor()
    x_train_processed = preprocessor.fit_transform(x_train)
    x_test_processed = preprocessor.transform(x_test)

    x_resampled, y_resampled = apply_smote(x_train_processed, y_train)

    logistic = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    logistic.fit(x_resampled, y_resampled)

    random_forest = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        class_weight="balanced",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    random_forest.fit(x_resampled, y_resampled)

    x_normal = x_train_processed[y_train.values == 0]
    isolation_forest = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        max_samples="auto",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    isolation_forest.fit(x_normal)

    return TrainedModels(
        logistic_regression=logistic,
        random_forest=random_forest,
        isolation_forest=isolation_forest,
        preprocessor=preprocessor,
        x_train=x_train,
        x_test=x_test,
        y_train=y_train,
        y_test=y_test,
        x_train_processed=x_train_processed,
        x_test_processed=x_test_processed,
    )
