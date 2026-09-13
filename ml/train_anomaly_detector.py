from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest

from ml.train_predictive_model import (
    FEATURE_COLUMNS,
    engineer_features,
)


# ============================================================
# GRIDGUARD AI - UNSUPERVISED ANOMALY DETECTOR
# ============================================================
#
# Goal
# ----
# Learn the distribution of healthy / normal telemetry.
#
# The model is NOT taught explicit fault labels during
# training.
#
# It answers:
#
#   "How unusual is this telemetry pattern compared with
#    healthy operating behavior?"
#
# IMPORTANT
# ---------
# This detector is trained and evaluated on synthetic
# prototype telemetry.
#
# It is NOT validated field-performance evidence.
#
# ============================================================


RANDOM_SEED = 42

ROLLING_WARMUP = 4

TARGET_NORMAL_FALSE_POSITIVE_RATE = 0.05


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "gridguard_synthetic_telemetry.csv"
)

SCENARIO_SPLIT_PATH = (
    PROJECT_ROOT
    / "ml"
    / "reports"
    / "scenario_split.json"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "isolation_forest.joblib"
)

CONFIG_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "anomaly_detector_config.json"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "ml"
    / "reports"
    / "anomaly_detector_report.json"
)


# ============================================================
# FEATURES
# ============================================================
#
# We intentionally exclude data_quality_suspect.
#
# Data quality is handled by GridGuard's separate Quality
# Guard rather than being mixed into anomaly scoring.
#
# ============================================================


ANOMALY_FEATURE_COLUMNS = [
    feature
    for feature in FEATURE_COLUMNS
    if feature != "data_quality_suspect"
]


# ============================================================
# LOAD SCENARIO SPLIT
# ============================================================


def load_scenario_split() -> tuple[
    set[str],
    set[str],
    set[str],
]:

    if not SCENARIO_SPLIT_PATH.exists():

        raise FileNotFoundError(
            (
                "Scenario split file not found:\n"
                f"{SCENARIO_SPLIT_PATH}\n\n"
                "Run predictive model training first."
            )
        )

    with SCENARIO_SPLIT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        payload = json.load(
            file
        )

    return (
        set(
            payload[
                "train_scenarios"
            ]
        ),
        set(
            payload[
                "validation_scenarios"
            ]
        ),
        set(
            payload[
                "test_scenarios"
            ]
        ),
    )


# ============================================================
# PREPARE DATA
# ============================================================


def prepare_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    dataframe = engineer_features(
        dataframe
    )

    # Remove early rolling-window warmup rows.
    dataframe = dataframe[
        dataframe[
            "timestep"
        ]
        >= ROLLING_WARMUP
    ].copy()

    dataframe[
        ANOMALY_FEATURE_COLUMNS
    ] = (
        dataframe[
            ANOMALY_FEATURE_COLUMNS
        ]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .fillna(0.0)
    )

    return dataframe


# ============================================================
# HEALTHY TRAINING DATA
# ============================================================


def select_healthy_training_rows(
    dataframe: pd.DataFrame,
    train_ids: set[str],
) -> pd.DataFrame:
    """
    Isolation Forest sees ONLY healthy behavior.

    NORMAL and NORMAL_WITH_NOISE scenarios are allowed.

    We also require:
        latent_severity == 0
        data_quality == GOOD
    """

    healthy_types = {
        "NORMAL",
        "NORMAL_WITH_NOISE",
    }

    result = dataframe[
        dataframe[
            "scenario_id"
        ].isin(
            train_ids
        )
        & dataframe[
            "scenario_type"
        ].isin(
            healthy_types
        )
        & (
            dataframe[
                "latent_severity"
            ]
            == 0
        )
        & (
            dataframe[
                "data_quality"
            ]
            == "GOOD"
        )
    ].copy()

    return result


# ============================================================
# SCORE HELPERS
# ============================================================


def raw_normality_score(
    model: IsolationForest,
    X: pd.DataFrame,
) -> np.ndarray:
    """
    sklearn IsolationForest score_samples:

    Higher value:
        more normal

    Lower value:
        more anomalous
    """

    return model.score_samples(
        X
    )


def anomaly_strength(
    normality_scores: np.ndarray,
    threshold: float,
) -> np.ndarray:
    """
    Positive values indicate increasingly anomalous behavior.

    0:
        at threshold

    > 0:
        anomaly side

    < 0:
        healthy side
    """

    return (
        threshold
        - normality_scores
    )


# ============================================================
# THRESHOLD CALIBRATION
# ============================================================


def calibrate_threshold(
    model: IsolationForest,
    validation_normal: pd.DataFrame,
) -> float:
    """
    Set the anomaly threshold using ONLY held-out healthy
    validation telemetry.

    Target:
        approximately 5% false-positive rate on healthy
        synthetic validation data.
    """

    X_validation_normal = (
        validation_normal[
            ANOMALY_FEATURE_COLUMNS
        ]
        .astype(float)
    )

    scores = raw_normality_score(
        model,
        X_validation_normal,
    )

    threshold = float(
        np.quantile(
            scores,
            TARGET_NORMAL_FALSE_POSITIVE_RATE,
        )
    )

    return threshold


# ============================================================
# EVALUATION
# ============================================================


def evaluate_detector(
    model: IsolationForest,
    threshold: float,
    test_dataframe: pd.DataFrame,
) -> dict:

    # --------------------------------------------------------
    # Healthy test rows
    # --------------------------------------------------------

    normal_rows = test_dataframe[
        (
            test_dataframe[
                "latent_severity"
            ]
            == 0
        )
        & (
            test_dataframe[
                "scenario_type"
            ].isin(
                [
                    "NORMAL",
                    "NORMAL_WITH_NOISE",
                ]
            )
        )
        & (
            test_dataframe[
                "data_quality"
            ]
            == "GOOD"
        )
    ].copy()

    # --------------------------------------------------------
    # Known deteriorated test rows
    #
    # latent_severity >= 1 is used ONLY for evaluation.
    #
    # The Isolation Forest never sees these labels while
    # training.
    # --------------------------------------------------------

    abnormal_rows = test_dataframe[
        test_dataframe[
            "latent_severity"
        ]
        >= 1
    ].copy()

    X_normal = (
        normal_rows[
            ANOMALY_FEATURE_COLUMNS
        ]
        .astype(float)
    )

    X_abnormal = (
        abnormal_rows[
            ANOMALY_FEATURE_COLUMNS
        ]
        .astype(float)
    )

    normal_scores = raw_normality_score(
        model,
        X_normal,
    )

    abnormal_scores = raw_normality_score(
        model,
        X_abnormal,
    )

    normal_predictions = (
        normal_scores
        < threshold
    )

    abnormal_predictions = (
        abnormal_scores
        < threshold
    )

    normal_false_positive_rate = float(
        np.mean(
            normal_predictions
        )
    )

    abnormal_detection_rate = float(
        np.mean(
            abnormal_predictions
        )
    )

    return {
        "normal_rows":
            int(
                len(
                    normal_rows
                )
            ),

        "abnormal_rows":
            int(
                len(
                    abnormal_rows
                )
            ),

        "normal_false_positive_rate":
            round(
                normal_false_positive_rate,
                6,
            ),

        "normal_specificity":
            round(
                1.0
                - normal_false_positive_rate,
                6,
            ),

        "abnormal_detection_rate":
            round(
                abnormal_detection_rate,
                6,
            ),

        "normal_score_mean":
            round(
                float(
                    np.mean(
                        normal_scores
                    )
                ),
                6,
            ),

        "abnormal_score_mean":
            round(
                float(
                    np.mean(
                        abnormal_scores
                    )
                ),
                6,
            ),

        "normal_score_median":
            round(
                float(
                    np.median(
                        normal_scores
                    )
                ),
                6,
            ),

        "abnormal_score_median":
            round(
                float(
                    np.median(
                        abnormal_scores
                    )
                ),
                6,
            ),
    }


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    print(
        "=" * 74
    )

    print(
        "GRIDGUARD AI - ISOLATION FOREST ANOMALY DETECTOR"
    )

    print(
        "=" * 74
    )

    print()

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            (
                "Synthetic dataset not found:\n"
                f"{DATASET_PATH}"
            )
        )

    print(
        "Loading synthetic telemetry..."
    )

    dataframe = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Raw telemetry rows : "
        f"{len(dataframe)}"
    )

    print()

    (
        train_ids,
        validation_ids,
        test_ids,
    ) = load_scenario_split()

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

    dataframe = prepare_dataframe(
        dataframe
    )

    print(
        f"Anomaly feature count : "
        f"{len(ANOMALY_FEATURE_COLUMNS)}"
    )

    print()

    # ========================================================
    # TRAINING DATA
    # ========================================================

    healthy_train = (
        select_healthy_training_rows(
            dataframe,
            train_ids,
        )
    )

    if healthy_train.empty:

        raise RuntimeError(
            "No healthy training rows found."
        )

    print(
        f"Healthy training rows : "
        f"{len(healthy_train)}"
    )

    print(
        "Training scenario types:"
    )

    for (
        scenario_type,
        count,
    ) in (
        healthy_train[
            "scenario_type"
        ]
        .value_counts()
        .sort_index()
        .items()
    ):

        print(
            f"  {scenario_type:<24} "
            f"{count}"
        )

    print()

    X_train = (
        healthy_train[
            ANOMALY_FEATURE_COLUMNS
        ]
        .astype(float)
    )

    # ========================================================
    # TRAIN ISOLATION FOREST
    # ========================================================

    print(
        "Training Isolation Forest..."
    )

    model = IsolationForest(
        n_estimators=400,
        max_samples="auto",
        contamination="auto",
        max_features=1.0,
        bootstrap=False,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )

    model.fit(
        X_train
    )

    print(
        "Isolation Forest training complete."
    )

    print()

    # ========================================================
    # VALIDATION NORMAL DATA FOR THRESHOLD
    # ========================================================

    validation_normal = dataframe[
        dataframe[
            "scenario_id"
        ].isin(
            validation_ids
        )
        & dataframe[
            "scenario_type"
        ].isin(
            [
                "NORMAL",
                "NORMAL_WITH_NOISE",
            ]
        )
        & (
            dataframe[
                "latent_severity"
            ]
            == 0
        )
        & (
            dataframe[
                "data_quality"
            ]
            == "GOOD"
        )
    ].copy()

    if validation_normal.empty:

        raise RuntimeError(
            (
                "No healthy validation rows available "
                "for anomaly threshold calibration."
            )
        )

    threshold = calibrate_threshold(
        model,
        validation_normal,
    )

    print(
        f"Validation healthy rows : "
        f"{len(validation_normal)}"
    )

    print(
        f"Target healthy FPR      : "
        f"{TARGET_NORMAL_FALSE_POSITIVE_RATE:.2%}"
    )

    print(
        f"Calibrated threshold    : "
        f"{threshold:.6f}"
    )

    print()

    # ========================================================
    # TEST
    # ========================================================

    test_dataframe = dataframe[
        dataframe[
            "scenario_id"
        ].isin(
            test_ids
        )
    ].copy()

    metrics = evaluate_detector(
        model,
        threshold,
        test_dataframe,
    )

    print(
        "-" * 74
    )

    print(
        "HELD-OUT TEST RESULTS"
    )

    print(
        "-" * 74
    )

    print(
        f"Healthy test rows       : "
        f"{metrics['normal_rows']}"
    )

    print(
        f"Deteriorated test rows  : "
        f"{metrics['abnormal_rows']}"
    )

    print()

    print(
        f"Healthy false positive  : "
        f"{metrics['normal_false_positive_rate']:.2%}"
    )

    print(
        f"Healthy specificity     : "
        f"{metrics['normal_specificity']:.2%}"
    )

    print(
        f"Abnormal detection rate : "
        f"{metrics['abnormal_detection_rate']:.2%}"
    )

    print()

    print(
        f"Mean healthy score      : "
        f"{metrics['normal_score_mean']:.6f}"
    )

    print(
        f"Mean abnormal score     : "
        f"{metrics['abnormal_score_mean']:.6f}"
    )

    print()

    # ========================================================
    # SAVE ARTIFACTS
    # ========================================================

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    config = {
        "model_type":
            "IsolationForest",

        "random_seed":
            RANDOM_SEED,

        "threshold":
            threshold,

        "threshold_strategy":
            (
                "5th percentile of held-out healthy "
                "validation normality scores."
            ),

        "target_healthy_false_positive_rate":
            TARGET_NORMAL_FALSE_POSITIVE_RATE,

        "rolling_warmup":
            ROLLING_WARMUP,

        "feature_count":
            len(
                ANOMALY_FEATURE_COLUMNS
            ),

        "features":
            ANOMALY_FEATURE_COLUMNS,

        "important_note":
            (
                "Synthetic prototype anomaly detector. "
                "Production threshold requires field "
                "calibration."
            ),
    }

    with CONFIG_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            config,
            file,
            indent=2,
            ensure_ascii=False,
        )

    report = {
        "important_note":
            (
                "Unsupervised anomaly detector trained only "
                "on healthy synthetic prototype telemetry. "
                "Metrics do not represent validated field "
                "performance."
            ),

        "training": {
            "healthy_training_rows":
                int(
                    len(
                        healthy_train
                    )
                ),

            "training_scenarios":
                int(
                    healthy_train[
                        "scenario_id"
                    ].nunique()
                ),
        },

        "calibration": {
            "healthy_validation_rows":
                int(
                    len(
                        validation_normal
                    )
                ),

            "target_false_positive_rate":
                TARGET_NORMAL_FALSE_POSITIVE_RATE,

            "threshold":
                threshold,
        },

        "test":
            metrics,
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
        "-" * 74
    )

    print(
        "MODEL ARTIFACTS"
    )

    print(
        "-" * 74
    )

    print(
        "Isolation Forest:"
    )

    print(
        f"  {MODEL_PATH}"
    )

    print()

    print(
        "Configuration:"
    )

    print(
        f"  {CONFIG_PATH}"
    )

    print()

    print(
        "Evaluation report:"
    )

    print(
        f"  {REPORT_PATH}"
    )

    print()

    print(
        "=" * 74
    )

    print(
        "GRIDGUARD ANOMALY DETECTOR TRAINING COMPLETE"
    )

    print(
        "=" * 74
    )


if __name__ == "__main__":
    main()