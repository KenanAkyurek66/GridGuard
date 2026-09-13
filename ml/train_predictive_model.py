from __future__ import annotations

import json
import random
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from xgboost import XGBClassifier


# ============================================================
# GRIDGUARD AI - PREDICTIVE EARLY WARNING MODEL
# ============================================================
#
# Goal
# ----
# Predict whether a panel that is NOT currently HIGH/CRITICAL
# will escalate to HIGH/CRITICAL within the next 5 telemetry
# cycles.
#
# IMPORTANT
# ---------
# This model is trained on synthetic prototype data.
#
# It must NOT be presented as a validated utility field model.
# Production deployment requires retraining / calibration using
# validated historical operational data.
#
# ============================================================


RANDOM_SEED = 42

ROLLING_WINDOW = 5

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "gridguard_synthetic_telemetry.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "reports"
)

LOGISTIC_MODEL_PATH = (
    MODEL_DIR
    / "logistic_baseline.joblib"
)

XGBOOST_MODEL_PATH = (
    MODEL_DIR
    / "xgboost_early_warning.joblib"
)

FEATURE_LIST_PATH = (
    MODEL_DIR
    / "predictive_features.json"
)

SPLIT_PATH = (
    REPORT_DIR
    / "scenario_split.json"
)

REPORT_PATH = (
    REPORT_DIR
    / "predictive_model_report.json"
)


# ============================================================
# FEATURE ENGINEERING
# ============================================================


RAW_SENSOR_COLUMNS = [
    "current_a",
    "cable_temperature_c",
    "ambient_temperature_c",
    "humidity_pct",
    "pd_index",
]


def rolling_slope(
    values: np.ndarray,
) -> float:
    """
    Linear trend slope over the rolling window.

    Positive:
        increasing

    Negative:
        decreasing
    """

    if len(values) < 3:
        return 0.0

    x = np.arange(
        len(values),
        dtype=float,
    )

    y = np.asarray(
        values,
        dtype=float,
    )

    if np.allclose(
        y,
        y[0],
    ):
        return 0.0

    slope = np.polyfit(
        x,
        y,
        1,
    )[0]

    return float(slope)


def add_group_features(
    group: pd.DataFrame,
) -> pd.DataFrame:

    group = (
        group
        .sort_values("timestep")
        .copy()
    )

    # --------------------------------------------------------
    # Direct engineered features
    # --------------------------------------------------------

    group[
        "thermal_delta_c"
    ] = (
        group["cable_temperature_c"]
        - group["ambient_temperature_c"]
    )

    group[
        "data_quality_suspect"
    ] = (
        group["data_quality"]
        != "GOOD"
    ).astype(int)

    # --------------------------------------------------------
    # Rolling telemetry features
    # --------------------------------------------------------

    feature_sources = (
        RAW_SENSOR_COLUMNS
        + [
            "thermal_delta_c",
        ]
    )

    for column in feature_sources:

        group[
            f"{column}_delta_1"
        ] = (
            group[column]
            .diff()
            .fillna(0.0)
        )

        group[
            f"{column}_mean_{ROLLING_WINDOW}"
        ] = (
            group[column]
            .rolling(
                window=ROLLING_WINDOW,
                min_periods=1,
            )
            .mean()
        )

        group[
            f"{column}_std_{ROLLING_WINDOW}"
        ] = (
            group[column]
            .rolling(
                window=ROLLING_WINDOW,
                min_periods=2,
            )
            .std()
            .fillna(0.0)
        )

        group[
            f"{column}_slope_{ROLLING_WINDOW}"
        ] = (
            group[column]
            .rolling(
                window=ROLLING_WINDOW,
                min_periods=3,
            )
            .apply(
                rolling_slope,
                raw=True,
            )
            .fillna(0.0)
        )

    # --------------------------------------------------------
    # Current change percentage against recent history
    # --------------------------------------------------------

    recent_current_mean = (
        group["current_a"]
        .shift(1)
        .rolling(
            window=ROLLING_WINDOW,
            min_periods=1,
        )
        .mean()
    )

    group[
        "current_change_pct"
    ] = np.where(
        recent_current_mean > 0,
        (
            (
                group["current_a"]
                - recent_current_mean
            )
            / recent_current_mean
        )
        * 100.0,
        0.0,
    )

    group[
        "current_change_pct"
    ] = (
        group[
            "current_change_pct"
        ]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            0.0,
        )
        .fillna(0.0)
    )

    return group


def engineer_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    print(
        "Engineering temporal features..."
    )

    groups = []

    for (
        _scenario_id,
        scenario_group,
    ) in dataframe.groupby(
        "scenario_id",
        sort=False,
    ):

        groups.append(
            add_group_features(
                scenario_group
            )
        )

    result = pd.concat(
        groups,
        ignore_index=True,
    )

    return result


# ============================================================
# MODEL FEATURES
# ============================================================


FEATURE_COLUMNS = [
    # Raw current state
    "current_a",
    "cable_temperature_c",
    "ambient_temperature_c",
    "humidity_pct",
    "pd_index",
    "thermal_delta_c",
    "data_quality_suspect",

    # Current
    "current_a_delta_1",
    "current_a_mean_5",
    "current_a_std_5",
    "current_a_slope_5",
    "current_change_pct",

    # Cable temperature
    "cable_temperature_c_delta_1",
    "cable_temperature_c_mean_5",
    "cable_temperature_c_std_5",
    "cable_temperature_c_slope_5",

    # Ambient temperature
    "ambient_temperature_c_delta_1",
    "ambient_temperature_c_mean_5",
    "ambient_temperature_c_std_5",
    "ambient_temperature_c_slope_5",

    # Humidity
    "humidity_pct_delta_1",
    "humidity_pct_mean_5",
    "humidity_pct_std_5",
    "humidity_pct_slope_5",

    # Partial discharge
    "pd_index_delta_1",
    "pd_index_mean_5",
    "pd_index_std_5",
    "pd_index_slope_5",

    # Thermal delta
    "thermal_delta_c_delta_1",
    "thermal_delta_c_mean_5",
    "thermal_delta_c_std_5",
    "thermal_delta_c_slope_5",
]


# ============================================================
# SCENARIO-LEVEL SPLIT
# ============================================================


def split_scenarios(
    dataframe: pd.DataFrame,
) -> tuple[
    set[str],
    set[str],
    set[str],
]:
    """
    Split complete scenarios.

    Rows from the same scenario can NEVER appear in multiple
    dataset partitions.

    Scenario types are distributed independently so that each
    split receives examples from every scenario family.
    """

    random.seed(
        RANDOM_SEED
    )

    scenario_metadata = (
        dataframe[
            [
                "scenario_id",
                "scenario_type",
            ]
        ]
        .drop_duplicates()
    )

    train_ids: set[str] = set()
    validation_ids: set[str] = set()
    test_ids: set[str] = set()

    for (
        scenario_type,
        group,
    ) in scenario_metadata.groupby(
        "scenario_type"
    ):

        ids = (
            group[
                "scenario_id"
            ]
            .tolist()
        )

        random.shuffle(
            ids
        )

        count = len(
            ids
        )

        train_end = int(
            count
            * TRAIN_RATIO
        )

        validation_end = (
            train_end
            + int(
                count
                * VALIDATION_RATIO
            )
        )

        train_ids.update(
            ids[
                :train_end
            ]
        )

        validation_ids.update(
            ids[
                train_end:
                validation_end
            ]
        )

        test_ids.update(
            ids[
                validation_end:
            ]
        )

    return (
        train_ids,
        validation_ids,
        test_ids,
    )


# ============================================================
# THRESHOLD SELECTION
# ============================================================


def choose_f2_threshold(
    y_true: np.ndarray,
    probabilities: np.ndarray,
) -> tuple[
    float,
    float,
]:
    """
    Choose the threshold maximizing F2.

    F2 gives recall more importance than precision.

    For an early-warning system, missing a real future
    escalation is more costly than producing some additional
    warnings.
    """

    precision, recall, thresholds = (
        precision_recall_curve(
            y_true,
            probabilities,
        )
    )

    if len(thresholds) == 0:
        return (
            0.5,
            0.0,
        )

    precision = precision[:-1]
    recall = recall[:-1]

    beta_squared = 4.0

    denominator = (
        beta_squared
        * precision
        + recall
    )

    f2_scores = np.where(
        denominator > 0,
        (
            (
                1
                + beta_squared
            )
            * precision
            * recall
            / denominator
        ),
        0.0,
    )

    best_index = int(
        np.argmax(
            f2_scores
        )
    )

    return (
        float(
            thresholds[
                best_index
            ]
        ),
        float(
            f2_scores[
                best_index
            ]
        ),
    )


# ============================================================
# EVALUATION
# ============================================================


def evaluate_predictions(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold: float,
) -> dict:

    predictions = (
        probabilities
        >= threshold
    ).astype(int)

    matrix = confusion_matrix(
        y_true,
        predictions,
        labels=[
            0,
            1,
        ],
    )

    tn, fp, fn, tp = (
        matrix.ravel()
    )

    if len(
        np.unique(
            y_true
        )
    ) > 1:

        roc_auc = (
            roc_auc_score(
                y_true,
                probabilities,
            )
        )

        pr_auc = (
            average_precision_score(
                y_true,
                probabilities,
            )
        )

    else:
        roc_auc = None
        pr_auc = None

    return {
        "threshold":
            round(
                float(
                    threshold
                ),
                6,
            ),

        "rows":
            int(
                len(
                    y_true
                )
            ),

        "positive_rows":
            int(
                np.sum(
                    y_true
                )
            ),

        "positive_rate_pct":
            round(
                float(
                    np.mean(
                        y_true
                    )
                    * 100
                ),
                3,
            ),

        "accuracy":
            round(
                float(
                    accuracy_score(
                        y_true,
                        predictions,
                    )
                ),
                6,
            ),

        "precision":
            round(
                float(
                    precision_score(
                        y_true,
                        predictions,
                        zero_division=0,
                    )
                ),
                6,
            ),

        "recall":
            round(
                float(
                    recall_score(
                        y_true,
                        predictions,
                        zero_division=0,
                    )
                ),
                6,
            ),

        "f1":
            round(
                float(
                    f1_score(
                        y_true,
                        predictions,
                        zero_division=0,
                    )
                ),
                6,
            ),

        "roc_auc":
            (
                round(
                    float(
                        roc_auc
                    ),
                    6,
                )
                if roc_auc
                is not None
                else None
            ),

        "pr_auc":
            (
                round(
                    float(
                        pr_auc
                    ),
                    6,
                )
                if pr_auc
                is not None
                else None
            ),

        "confusion_matrix": {
            "true_negative":
                int(tn),

            "false_positive":
                int(fp),

            "false_negative":
                int(fn),

            "true_positive":
                int(tp),
        },
    }


# ============================================================
# DATASET PREPARATION
# ============================================================


def prepare_training_rows(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep only rows where the system is not already HIGH or
    CRITICAL.

    This ensures the ML task remains genuine early warning,
    rather than simply recognizing an already severe event.
    """

    eligible = dataframe[
        dataframe[
            "latent_severity"
        ]
        < 2
    ].copy()

    eligible = (
        eligible
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
    )

    eligible[
        FEATURE_COLUMNS
    ] = (
        eligible[
            FEATURE_COLUMNS
        ]
        .fillna(0.0)
    )

    return eligible


# ============================================================
# OUTPUT HELPERS
# ============================================================


def save_feature_list() -> None:

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "rolling_window":
            ROLLING_WINDOW,

        "feature_count":
            len(
                FEATURE_COLUMNS
            ),

        "features":
            FEATURE_COLUMNS,

        "target":
            "future_escalation",

        "task":
            (
                "Predict HIGH/CRITICAL "
                "escalation within the "
                "next 5 telemetry cycles."
            ),
    }

    with FEATURE_LIST_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )


def save_split(
    train_ids: set[str],
    validation_ids: set[str],
    test_ids: set[str],
) -> None:

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "random_seed":
            RANDOM_SEED,

        "strategy":
            (
                "Scenario-level split. "
                "No scenario appears in "
                "multiple partitions."
            ),

        "train_scenarios":
            sorted(
                train_ids
            ),

        "validation_scenarios":
            sorted(
                validation_ids
            ),

        "test_scenarios":
            sorted(
                test_ids
            ),
    }

    with SPLIT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    np.random.seed(
        RANDOM_SEED
    )

    random.seed(
        RANDOM_SEED
    )

    print(
        "=" * 72
    )

    print(
        "GRIDGUARD AI - PREDICTIVE EARLY WARNING TRAINING"
    )

    print(
        "=" * 72
    )

    print()

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            (
                "Synthetic dataset not found:\n"
                f"{DATASET_PATH}\n\n"
                "Run first:\n"
                "python -m ml.generate_dataset"
            )
        )

    print(
        "Loading dataset..."
    )

    dataframe = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Raw telemetry rows       : "
        f"{len(dataframe)}"
    )

    print(
        f"Scenarios                : "
        f"{dataframe['scenario_id'].nunique()}"
    )

    print()

    # --------------------------------------------------------
    # Temporal feature engineering
    # --------------------------------------------------------

    dataframe = engineer_features(
        dataframe
    )

    print(
        f"Engineered feature count : "
        f"{len(FEATURE_COLUMNS)}"
    )

    print()

    # --------------------------------------------------------
    # Scenario split
    # --------------------------------------------------------

    (
        train_ids,
        validation_ids,
        test_ids,
    ) = split_scenarios(
        dataframe
    )

    assert (
        train_ids
        .isdisjoint(
            validation_ids
        )
    )

    assert (
        train_ids
        .isdisjoint(
            test_ids
        )
    )

    assert (
        validation_ids
        .isdisjoint(
            test_ids
        )
    )

    save_split(
        train_ids,
        validation_ids,
        test_ids,
    )

    save_feature_list()

    print(
        "Scenario split:"
    )

    print(
        f"  Train      : "
        f"{len(train_ids)}"
    )

    print(
        f"  Validation : "
        f"{len(validation_ids)}"
    )

    print(
        f"  Test       : "
        f"{len(test_ids)}"
    )

    print()

    # --------------------------------------------------------
    # Eligible early-warning rows
    # --------------------------------------------------------

    eligible = (
        prepare_training_rows(
            dataframe
        )
    )

    train_df = eligible[
        eligible[
            "scenario_id"
        ].isin(
            train_ids
        )
    ].copy()

    validation_df = eligible[
        eligible[
            "scenario_id"
        ].isin(
            validation_ids
        )
    ].copy()

    test_df = eligible[
        eligible[
            "scenario_id"
        ].isin(
            test_ids
        )
    ].copy()

    X_train = (
        train_df[
            FEATURE_COLUMNS
        ]
        .astype(float)
    )

    y_train = (
        train_df[
            "future_escalation"
        ]
        .astype(int)
        .to_numpy()
    )

    X_validation = (
        validation_df[
            FEATURE_COLUMNS
        ]
        .astype(float)
    )

    y_validation = (
        validation_df[
            "future_escalation"
        ]
        .astype(int)
        .to_numpy()
    )

    X_test = (
        test_df[
            FEATURE_COLUMNS
        ]
        .astype(float)
    )

    y_test = (
        test_df[
            "future_escalation"
        ]
        .astype(int)
        .to_numpy()
    )

    print(
        "Training rows:"
    )

    print(
        f"  Train      : "
        f"{len(X_train)} "
        f"({np.mean(y_train) * 100:.2f}% positive)"
    )

    print(
        f"  Validation : "
        f"{len(X_validation)} "
        f"({np.mean(y_validation) * 100:.2f}% positive)"
    )

    print(
        f"  Test       : "
        f"{len(X_test)} "
        f"({np.mean(y_test) * 100:.2f}% positive)"
    )

    print()

    # ========================================================
    # MODEL 1 - LOGISTIC REGRESSION BASELINE
    # ========================================================

    print(
        "-" * 72
    )

    print(
        "TRAINING LOGISTIC REGRESSION BASELINE"
    )

    print(
        "-" * 72
    )

    logistic_model = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=RANDOM_SEED,
                ),
            ),
        ]
    )

    logistic_model.fit(
        X_train,
        y_train,
    )

    logistic_validation_probability = (
        logistic_model
        .predict_proba(
            X_validation
        )[:, 1]
    )

    (
        logistic_threshold,
        logistic_validation_f2,
    ) = choose_f2_threshold(
        y_validation,
        logistic_validation_probability,
    )

    logistic_test_probability = (
        logistic_model
        .predict_proba(
            X_test
        )[:, 1]
    )

    logistic_test_metrics = (
        evaluate_predictions(
            y_test,
            logistic_test_probability,
            logistic_threshold,
        )
    )

    print(
        f"Validation F2 threshold : "
        f"{logistic_threshold:.4f}"
    )

    print(
        f"Validation F2           : "
        f"{logistic_validation_f2:.4f}"
    )

    print(
        f"Test precision          : "
        f"{logistic_test_metrics['precision']:.4f}"
    )

    print(
        f"Test recall             : "
        f"{logistic_test_metrics['recall']:.4f}"
    )

    print(
        f"Test F1                 : "
        f"{logistic_test_metrics['f1']:.4f}"
    )

    print(
        f"Test PR-AUC             : "
        f"{logistic_test_metrics['pr_auc']:.4f}"
    )

    print()

    # ========================================================
    # MODEL 2 - XGBOOST
    # ========================================================

    print(
        "-" * 72
    )

    print(
        "TRAINING XGBOOST EARLY WARNING MODEL"
    )

    print(
        "-" * 72
    )

    positive_count = int(
        np.sum(
            y_train
        )
    )

    negative_count = int(
        len(y_train)
        - positive_count
    )

    if positive_count == 0:

        raise RuntimeError(
            "Training set has zero positive examples."
        )

    scale_pos_weight = (
        negative_count
        / positive_count
    )

    print(
        f"scale_pos_weight         : "
        f"{scale_pos_weight:.3f}"
    )

    xgboost_model = XGBClassifier(
        n_estimators=450,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=3,
        reg_lambda=1.5,
        objective="binary:logistic",
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        tree_method="hist",
    )

    xgboost_model.fit(
        X_train,
        y_train,
        eval_set=[
            (
                X_validation,
                y_validation,
            )
        ],
        verbose=False,
    )

    xgb_validation_probability = (
        xgboost_model
        .predict_proba(
            X_validation
        )[:, 1]
    )

    (
        xgb_threshold,
        xgb_validation_f2,
    ) = choose_f2_threshold(
        y_validation,
        xgb_validation_probability,
    )

    xgb_test_probability = (
        xgboost_model
        .predict_proba(
            X_test
        )[:, 1]
    )

    xgb_test_metrics = (
        evaluate_predictions(
            y_test,
            xgb_test_probability,
            xgb_threshold,
        )
    )

    print(
        f"Validation F2 threshold : "
        f"{xgb_threshold:.4f}"
    )

    print(
        f"Validation F2           : "
        f"{xgb_validation_f2:.4f}"
    )

    print(
        f"Test accuracy           : "
        f"{xgb_test_metrics['accuracy']:.4f}"
    )

    print(
        f"Test precision          : "
        f"{xgb_test_metrics['precision']:.4f}"
    )

    print(
        f"Test recall             : "
        f"{xgb_test_metrics['recall']:.4f}"
    )

    print(
        f"Test F1                 : "
        f"{xgb_test_metrics['f1']:.4f}"
    )

    print(
        f"Test ROC-AUC            : "
        f"{xgb_test_metrics['roc_auc']:.4f}"
    )

    print(
        f"Test PR-AUC             : "
        f"{xgb_test_metrics['pr_auc']:.4f}"
    )

    print()

    print(
        "Confusion matrix:"
    )

    for (
        key,
        value,
    ) in xgb_test_metrics[
        "confusion_matrix"
    ].items():

        print(
            f"  {key:<18} : {value}"
        )

    print()

    # ========================================================
    # SAVE MODELS
    # ========================================================

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        logistic_model,
        LOGISTIC_MODEL_PATH,
    )

    joblib.dump(
        xgboost_model,
        XGBOOST_MODEL_PATH,
    )

    # ========================================================
    # REPORT
    # ========================================================

    report = {
        "important_note":
            (
                "Models trained on synthetic prototype data. "
                "Metrics do not represent validated field "
                "performance."
            ),

        "task":
            (
                "Predict HIGH/CRITICAL escalation within the "
                "next five telemetry cycles while the panel is "
                "not already HIGH/CRITICAL."
            ),

        "random_seed":
            RANDOM_SEED,

        "rolling_window":
            ROLLING_WINDOW,

        "feature_count":
            len(
                FEATURE_COLUMNS
            ),

        "scenario_split": {
            "train":
                len(
                    train_ids
                ),

            "validation":
                len(
                    validation_ids
                ),

            "test":
                len(
                    test_ids
                ),
        },

        "row_split": {
            "train":
                len(
                    X_train
                ),

            "validation":
                len(
                    X_validation
                ),

            "test":
                len(
                    X_test
                ),
        },

        "positive_rate_pct": {
            "train":
                round(
                    float(
                        np.mean(
                            y_train
                        )
                        * 100
                    ),
                    3,
                ),

            "validation":
                round(
                    float(
                        np.mean(
                            y_validation
                        )
                        * 100
                    ),
                    3,
                ),

            "test":
                round(
                    float(
                        np.mean(
                            y_test
                        )
                        * 100
                    ),
                    3,
                ),
        },

        "logistic_regression": {
            "validation_f2_threshold":
                round(
                    float(
                        logistic_threshold
                    ),
                    6,
                ),

            "validation_f2":
                round(
                    float(
                        logistic_validation_f2
                    ),
                    6,
                ),

            "test":
                logistic_test_metrics,
        },

        "xgboost": {
            "scale_pos_weight":
                round(
                    float(
                        scale_pos_weight
                    ),
                    6,
                ),

            "validation_f2_threshold":
                round(
                    float(
                        xgb_threshold
                    ),
                    6,
                ),

            "validation_f2":
                round(
                    float(
                        xgb_validation_f2
                    ),
                    6,
                ),

            "test":
                xgb_test_metrics,
        },
    }

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "-" * 72
    )

    print(
        "MODEL ARTIFACTS"
    )

    print(
        "-" * 72
    )

    print(
        f"Logistic baseline:"
    )

    print(
        f"  {LOGISTIC_MODEL_PATH}"
    )

    print()

    print(
        f"XGBoost model:"
    )

    print(
        f"  {XGBOOST_MODEL_PATH}"
    )

    print()

    print(
        f"Evaluation report:"
    )

    print(
        f"  {REPORT_PATH}"
    )

    print()

    print(
        "=" * 72
    )

    print(
        "GRIDGUARD PREDICTIVE MODEL TRAINING COMPLETE"
    )

    print(
        "=" * 72
    )


if __name__ == "__main__":
    main()