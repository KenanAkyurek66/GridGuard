from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from ml.consensus import evaluate_consensus
from ml.quality_guard import evaluate_quality_guard
from ml.train_anomaly_detector import ANOMALY_FEATURE_COLUMNS
from ml.train_predictive_model import (
    FEATURE_COLUMNS,
    add_group_features,
)


# ============================================================
# GRIDGUARD AI - LIVE INTELLIGENCE SERVICE
# ============================================================
#
# Purpose
# -------
# Connect the trained GridGuard AI prototype models with the
# live backend telemetry pipeline.
#
# Intelligence layers:
#
#   1. Deterministic Risk Engine
#   2. Predictive XGBoost Early Warning
#   3. Data Quality / Persistence Guard
#   4. Isolation Forest Anomaly Detection
#   5. XGBoost Feature Contributions
#   6. GridGuard AI Consensus
#
# IMPORTANT
# ---------
# The ML models were trained on synthetic prototype data.
#
# AI output is advisory only.
# It does not replace protection logic, switching logic,
# qualified engineering judgment or field validation.
#
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ML_MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
)

ML_REPORT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "reports"
)


PREDICTIVE_MODEL_PATH = (
    ML_MODEL_DIR
    / "xgboost_early_warning.joblib"
)

PREDICTIVE_REPORT_PATH = (
    ML_REPORT_DIR
    / "predictive_model_report.json"
)

ANOMALY_MODEL_PATH = (
    ML_MODEL_DIR
    / "isolation_forest.joblib"
)

ANOMALY_CONFIG_PATH = (
    ML_MODEL_DIR
    / "anomaly_detector_config.json"
)


MIN_HISTORY_POINTS = 5
RECENT_PREDICTION_WINDOW = 3
PREDICTION_HORIZON = 5
TOP_DRIVER_COUNT = 6


RAW_SENSOR_COLUMNS = [
    "current_a",
    "cable_temperature_c",
    "ambient_temperature_c",
    "humidity_pct",
    "pd_index",
]


FEATURE_LABELS = {
    "current_a":
        "Current",

    "cable_temperature_c":
        "Cable temperature",

    "ambient_temperature_c":
        "Ambient temperature",

    "humidity_pct":
        "Humidity",

    "pd_index":
        "Partial-discharge index",

    "thermal_delta_c":
        "Cable-to-ambient thermal delta",

    "data_quality_suspect":
        "Telemetry quality",

    "current_a_delta_1":
        "Current one-step change",

    "current_a_mean_5":
        "Recent mean current",

    "current_a_std_5":
        "Current variability",

    "current_a_slope_5":
        "Current trend",

    "current_change_pct":
        "Current change vs recent baseline",

    "cable_temperature_c_delta_1":
        "Cable temperature one-step change",

    "cable_temperature_c_mean_5":
        "Recent mean cable temperature",

    "cable_temperature_c_std_5":
        "Cable temperature variability",

    "cable_temperature_c_slope_5":
        "Cable temperature trend",

    "ambient_temperature_c_delta_1":
        "Ambient temperature one-step change",

    "ambient_temperature_c_mean_5":
        "Recent mean ambient temperature",

    "ambient_temperature_c_std_5":
        "Ambient temperature variability",

    "ambient_temperature_c_slope_5":
        "Ambient temperature trend",

    "humidity_pct_delta_1":
        "Humidity one-step change",

    "humidity_pct_mean_5":
        "Recent mean humidity",

    "humidity_pct_std_5":
        "Humidity variability",

    "humidity_pct_slope_5":
        "Humidity trend",

    "pd_index_delta_1":
        "PD one-step change",

    "pd_index_mean_5":
        "Recent mean PD index",

    "pd_index_std_5":
        "PD variability",

    "pd_index_slope_5":
        "PD trend",

    "thermal_delta_c_delta_1":
        "Thermal-delta one-step change",

    "thermal_delta_c_mean_5":
        "Recent mean thermal delta",

    "thermal_delta_c_std_5":
        "Thermal-delta variability",

    "thermal_delta_c_slope_5":
        "Thermal-delta trend",
}


# ============================================================
# FILE HELPERS
# ============================================================


def _load_json(
    path: Path,
) -> dict:

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


def _require_file(
    path: Path,
) -> None:

    if not path.exists():

        raise FileNotFoundError(
            f"Required GridGuard AI artifact not found: {path}"
        )


# ============================================================
# MODEL LOADING
# ============================================================


@lru_cache(maxsize=1)
def load_ai_assets() -> dict:

    required_paths = [
        PREDICTIVE_MODEL_PATH,
        PREDICTIVE_REPORT_PATH,
        ANOMALY_MODEL_PATH,
        ANOMALY_CONFIG_PATH,
    ]

    for path in required_paths:
        _require_file(
            path
        )

    predictive_model = joblib.load(
        PREDICTIVE_MODEL_PATH
    )

    predictive_report = _load_json(
        PREDICTIVE_REPORT_PATH
    )

    anomaly_model = joblib.load(
        ANOMALY_MODEL_PATH
    )

    anomaly_config = _load_json(
        ANOMALY_CONFIG_PATH
    )

    predictive_threshold = float(
        predictive_report[
            "xgboost"
        ][
            "validation_f2_threshold"
        ]
    )

    anomaly_threshold = float(
        anomaly_config[
            "threshold"
        ]
    )

    return {
        "predictive_model":
            predictive_model,

        "predictive_threshold":
            predictive_threshold,

        "anomaly_model":
            anomaly_model,

        "anomaly_threshold":
            anomaly_threshold,
    }


# ============================================================
# RUNTIME STATUS
# ============================================================


def get_ai_runtime_status() -> dict:

    try:

        assets = load_ai_assets()

        return {
            "available": True,

            "predictive_model":
                "XGBoost",

            "anomaly_model":
                "IsolationForest",

            "predictive_threshold":
                round(
                    assets[
                        "predictive_threshold"
                    ],
                    6,
                ),

            "anomaly_threshold":
                round(
                    assets[
                        "anomaly_threshold"
                    ],
                    6,
                ),

            "prediction_horizon_cycles":
                PREDICTION_HORIZON,

            "minimum_history_points":
                MIN_HISTORY_POINTS,

            "training_data":
                "SYNTHETIC_PROTOTYPE",

            "advisory_only":
                True,
        }

    except Exception as exc:

        return {
            "available": False,
            "error": str(exc),
        }


# ============================================================
# DATA QUALITY
# ============================================================


def _normalize_quality(
    value,
) -> str:

    if value is None:
        return "BAD"

    if hasattr(
        value,
        "value",
    ):
        value = value.value

    return str(
        value
    ).strip().upper()


# ============================================================
# LIVE DATAFRAME
# ============================================================


def _build_live_dataframe(
    telemetry_rows: list[dict],
) -> pd.DataFrame:

    rows = []

    for (
        timestep,
        telemetry,
    ) in enumerate(
        telemetry_rows
    ):

        rows.append(
            {
                "scenario_id":
                    "LIVE_PANEL",

                "scenario_type":
                    "LIVE",

                "timestep":
                    timestep,

                "current_a":
                    telemetry.get(
                        "current_a"
                    ),

                "cable_temperature_c":
                    telemetry.get(
                        "cable_temperature_c"
                    ),

                "ambient_temperature_c":
                    telemetry.get(
                        "ambient_temperature_c"
                    ),

                "humidity_pct":
                    telemetry.get(
                        "humidity_pct"
                    ),

                "pd_index":
                    telemetry.get(
                        "pd_index"
                    ),

                "arc_detected":
                    int(
                        bool(
                            telemetry.get(
                                "arc_detected",
                                False,
                            )
                        )
                    ),

                "data_quality":
                    _normalize_quality(
                        telemetry.get(
                            "data_quality",
                            "GOOD",
                        )
                    ),

                # These columns are required by the common
                # ML dataframe structure but are NOT used as
                # live predictive features.
                "latent_severity":
                    0,

                "future_escalation":
                    0,
            }
        )

    dataframe = pd.DataFrame(
        rows
    )

    return dataframe


# ============================================================
# LIVE DATA VALIDATION
# ============================================================


def _validate_live_dataframe(
    dataframe: pd.DataFrame,
) -> tuple[
    bool,
    str | None,
]:

    if len(
        dataframe
    ) < MIN_HISTORY_POINTS:

        return (
            False,
            (
                "At least "
                f"{MIN_HISTORY_POINTS} telemetry points "
                "are required for GridGuard AI analysis."
            ),
        )

    for column in RAW_SENSOR_COLUMNS:

        if column not in dataframe.columns:

            return (
                False,
                (
                    "Required telemetry field missing: "
                    f"{column}"
                ),
            )

        dataframe[
            column
        ] = pd.to_numeric(
            dataframe[
                column
            ],
            errors="coerce",
        )

    # The prototype ML models were trained on complete sensor
    # vectors. Do not silently invent sensor measurements.
    recent_required = (
        dataframe[
            RAW_SENSOR_COLUMNS
        ]
        .tail(
            MIN_HISTORY_POINTS
        )
    )

    if (
        recent_required
        .isna()
        .any()
        .any()
    ):

        missing_columns = [
            column
            for column in RAW_SENSOR_COLUMNS
            if (
                recent_required[
                    column
                ]
                .isna()
                .any()
            )
        ]

        return (
            False,
            (
                "Recent telemetry is incomplete for ML "
                "analysis. Missing values in: "
                + ", ".join(
                    missing_columns
                )
            ),
        )

    return (
        True,
        None,
    )


# ============================================================
# ANOMALY LEVEL
# ============================================================


def _anomaly_level(
    strength: float,
) -> str:

    if strength <= 0:
        return "NORMAL"

    if strength < 0.03:
        return "ELEVATED"

    if strength < 0.08:
        return "HIGH"

    return "SEVERE"


# ============================================================
# EXPLAINABILITY
# ============================================================


def _explain_latest_prediction(
    predictive_model,
    X_latest: pd.DataFrame,
) -> dict:

    booster = (
        predictive_model
        .get_booster()
    )

    matrix = xgb.DMatrix(
        X_latest,
        feature_names=FEATURE_COLUMNS,
    )

    contributions = (
        booster.predict(
            matrix,
            pred_contribs=True,
        )[0]
    )

    feature_contributions = (
        contributions[:-1]
    )

    bias = float(
        contributions[-1]
    )

    ranked = []

    for (
        feature,
        contribution,
    ) in zip(
        FEATURE_COLUMNS,
        feature_contributions,
    ):

        contribution = float(
            contribution
        )

        ranked.append(
            {
                "feature":
                    feature,

                "label":
                    FEATURE_LABELS.get(
                        feature,
                        feature,
                    ),

                "value":
                    round(
                        float(
                            X_latest.iloc[
                                0
                            ][
                                feature
                            ]
                        ),
                        6,
                    ),

                "contribution":
                    round(
                        contribution,
                        6,
                    ),

                "direction":
                    (
                        "INCREASES_RISK"
                        if contribution > 0
                        else (
                            "DECREASES_RISK"
                            if contribution < 0
                            else "NEUTRAL"
                        )
                    ),

                "absolute_contribution":
                    abs(
                        contribution
                    ),
            }
        )

    ranked.sort(
        key=lambda item:
            item[
                "absolute_contribution"
            ],
        reverse=True,
    )

    top_drivers = []

    for item in ranked[
        :TOP_DRIVER_COUNT
    ]:

        clean_item = dict(
            item
        )

        clean_item.pop(
            "absolute_contribution",
            None,
        )

        top_drivers.append(
            clean_item
        )

    return {
        "method":
            (
                "XGBoost native SHAP-style "
                "feature contributions"
            ),

        "bias":
            round(
                bias,
                6,
            ),

        "top_drivers":
            top_drivers,

        "important_note":
            (
                "Feature contributions explain model "
                "behavior. They do not establish "
                "electrical causality."
            ),
    }


# ============================================================
# MAIN LIVE INTELLIGENCE PIPELINE
# ============================================================


def analyze_gridguard_intelligence(
    *,
    telemetry_rows: list[dict],
    risk_result: dict,
) -> dict:

    # ========================================================
    # ASSETS
    # ========================================================

    try:

        assets = load_ai_assets()

    except Exception as exc:

        return {
            "available":
                False,

            "reason":
                "AI model artifacts unavailable.",

            "error":
                str(exc),
        }

    # ========================================================
    # LIVE DATA
    # ========================================================

    dataframe = (
        _build_live_dataframe(
            telemetry_rows
        )
    )

    (
        data_valid,
        validation_error,
    ) = _validate_live_dataframe(
        dataframe
    )

    if not data_valid:

        return {
            "available":
                False,

            "reason":
                validation_error,

            "history_points":
                len(
                    dataframe
                ),
        }

    # One live panel = one temporal group.
    engineered = (
        add_group_features(
            dataframe
        )
    )

    engineered[
        FEATURE_COLUMNS
    ] = (
        engineered[
            FEATURE_COLUMNS
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

    # ========================================================
    # PREDICTIVE XGBOOST
    # ========================================================

    predictive_model = (
        assets[
            "predictive_model"
        ]
    )

    predictive_threshold = float(
        assets[
            "predictive_threshold"
        ]
    )

    recent_frame = (
        engineered
        .tail(
            RECENT_PREDICTION_WINDOW
        )
    )

    X_recent = (
        recent_frame[
            FEATURE_COLUMNS
        ]
        .astype(float)
    )

    recent_probabilities = (
        predictive_model
        .predict_proba(
            X_recent
        )[:, 1]
        .astype(float)
        .tolist()
    )

    latest_probability = float(
        recent_probabilities[-1]
    )

    recent_quality = (
        recent_frame[
            "data_quality"
        ]
        .astype(str)
        .tolist()
    )

    quality_guard = (
        evaluate_quality_guard(
            recent_probabilities=(
                recent_probabilities
            ),

            recent_data_quality=(
                recent_quality
            ),

            threshold=(
                predictive_threshold
            ),

            consecutive_required=2,

            strong_confidence_margin=0.20,
        )
    )

    # ========================================================
    # ISOLATION FOREST
    # ========================================================

    anomaly_model = (
        assets[
            "anomaly_model"
        ]
    )

    anomaly_threshold = float(
        assets[
            "anomaly_threshold"
        ]
    )

    latest_row = (
        engineered
        .tail(1)
    )

    X_anomaly = (
        latest_row[
            ANOMALY_FEATURE_COLUMNS
        ]
        .astype(float)
    )

    normality_score = float(
        anomaly_model
        .score_samples(
            X_anomaly
        )[0]
    )

    anomaly_strength = float(
        anomaly_threshold
        - normality_score
    )

    anomaly_detected = bool(
        normality_score
        < anomaly_threshold
    )

    anomaly_level = (
        _anomaly_level(
            anomaly_strength
        )
    )

    # ========================================================
    # EXPLAINABILITY
    # ========================================================

    X_latest_predictive = (
        latest_row[
            FEATURE_COLUMNS
        ]
        .astype(float)
    )

    explainability = (
        _explain_latest_prediction(
            predictive_model,
            X_latest_predictive,
        )
    )

    # ========================================================
    # CONSENSUS
    # ========================================================

    rule_status = str(
        risk_result.get(
            "status",
            "NORMAL",
        )
    )

    rule_score = float(
        risk_result.get(
            "risk_score",
            0,
        )
    )

    consensus = (
        evaluate_consensus(
            rule_status=(
                rule_status
            ),

            rule_score=(
                rule_score
            ),

            predictive_decision=(
                quality_guard.decision
            ),

            predictive_probability=(
                latest_probability
            ),

            anomaly_detected=(
                anomaly_detected
            ),

            anomaly_level=(
                anomaly_level
            ),

            data_quality_reliable=(
                quality_guard.data_reliable
            ),
        )
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "available":
            True,

        "history_points":
            len(
                engineered
            ),

        "prototype_notice":
            (
                "ML models are trained on synthetic "
                "prototype telemetry and require field "
                "calibration before production use."
            ),

        "predictive": {
            "model":
                "XGBoost",

            "task":
                (
                    "HIGH/CRITICAL escalation "
                    "early warning"
                ),

            "probability":
                round(
                    latest_probability,
                    6,
                ),

            "probability_pct":
                round(
                    latest_probability
                    * 100.0,
                    2,
                ),

            "threshold":
                round(
                    predictive_threshold,
                    6,
                ),

            "prediction_horizon_cycles":
                PREDICTION_HORIZON,

            "recent_probabilities":
                [
                    round(
                        probability,
                        6,
                    )
                    for probability
                    in recent_probabilities
                ],

            "decision":
                quality_guard.decision,

            "data_reliable":
                quality_guard.data_reliable,

            "consecutive_high_predictions":
                (
                    quality_guard
                    .consecutive_high_predictions
                ),

            "reason":
                quality_guard.reason,
        },

        "anomaly": {
            "model":
                "IsolationForest",

            "detected":
                anomaly_detected,

            "level":
                anomaly_level,

            "normality_score":
                round(
                    normality_score,
                    6,
                ),

            "threshold":
                round(
                    anomaly_threshold,
                    6,
                ),

            "strength":
                round(
                    anomaly_strength,
                    6,
                ),

            "interpretation":
                (
                    "Anomaly indicates deviation from "
                    "learned healthy behavior. It does "
                    "not by itself indicate an "
                    "electrical fault."
                ),
        },

        "consensus":
            consensus.to_dict(),

        "explainability":
            explainability,

        "safety": {
            "advisory_only":
                True,

            "autonomous_switching":
                False,

            "deterministic_critical_override":
                True,
        },
    }