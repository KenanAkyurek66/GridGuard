from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from ml.stress_test_predictive_model import (
    OBSERVED_STEPS,
    create_stress_scenarios,
)

from ml.train_predictive_model import (
    FEATURE_COLUMNS,
    engineer_features,
)


# ============================================================
# GRIDGUARD AI - PREDICTIVE MODEL EXPLAINABILITY
# ============================================================
#
# Uses XGBoost native SHAP-style feature contributions.
#
# Goal:
# Explain WHY the predictive model considers a telemetry state
# likely or unlikely to escalate.
#
# IMPORTANT:
# These explanations describe the behavior of a model trained
# on synthetic prototype data.
#
# They are NOT causal electrical-engineering conclusions.
#
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "xgboost_early_warning.joblib"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "ml"
    / "reports"
    / "predictive_explainability_report.json"
)


TOP_FEATURE_COUNT = 8


# ============================================================
# HUMAN-READABLE FEATURE NAMES
# ============================================================


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
        "Suspect data quality",

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
# EXPLANATION
# ============================================================


def explain_row(
    model,
    X: pd.DataFrame,
) -> dict:

    probability = float(
        model.predict_proba(
            X
        )[0, 1]
    )

    booster = (
        model.get_booster()
    )

    matrix = xgb.DMatrix(
        X,
        feature_names=FEATURE_COLUMNS,
    )

    contributions = (
        booster.predict(
            matrix,
            pred_contribs=True,
        )[0]
    )

    # Final value is the bias / base contribution.
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
                            X.iloc[0][feature]
                        ),
                        6,
                    ),

                "contribution":
                    round(
                        float(
                            contribution
                        ),
                        6,
                    ),

                "absolute_contribution":
                    round(
                        abs(
                            float(
                                contribution
                            )
                        ),
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
            }
        )

    ranked.sort(
        key=lambda item:
            item[
                "absolute_contribution"
            ],
        reverse=True,
    )

    return {
        "probability":
            round(
                probability,
                6,
            ),

        "bias":
            round(
                bias,
                6,
            ),

        "top_features":
            ranked[
                :TOP_FEATURE_COUNT
            ],
    }


# ============================================================
# SCENARIOS
# ============================================================


def get_demo_scenarios():

    scenarios = (
        create_stress_scenarios()
    )

    wanted = {
        "SLOW_THERMAL_ESCALATION",
        "LOAD_THERMAL_ESCALATION",
        "PD_ESCALATION",
        "HUMIDITY_PD_ESCALATION",
        "SUBTLE_COMBINED_ESCALATION",
        "HOT_AMBIENT_SAFE_DELTA",
        "RECOVERY_TREND",
    }

    return [
        scenario
        for scenario in scenarios
        if scenario.name in wanted
    ]


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    print(
        "=" * 76
    )

    print(
        "GRIDGUARD AI - PREDICTIVE MODEL EXPLAINABILITY"
    )

    print(
        "=" * 76
    )

    print()

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            (
                "Predictive model not found:\n"
                f"{MODEL_PATH}"
            )
        )

    model = joblib.load(
        MODEL_PATH
    )

    scenarios = (
        get_demo_scenarios()
    )

    all_rows = []

    for scenario in scenarios:

        all_rows.extend(
            scenario.rows
        )

    dataframe = pd.DataFrame(
        all_rows
    )

    engineered = engineer_features(
        dataframe
    )

    report_scenarios = []

    for scenario in scenarios:

        scenario_id = (
            scenario.rows[0][
                "scenario_id"
            ]
        )

        scenario_frame = (
            engineered[
                engineered[
                    "scenario_id"
                ]
                == scenario_id
            ]
            .sort_values(
                "timestep"
            )
        )

        evaluation_row = (
            scenario_frame[
                scenario_frame[
                    "timestep"
                ]
                == (
                    OBSERVED_STEPS
                    - 1
                )
            ]
        )

        X = (
            evaluation_row[
                FEATURE_COLUMNS
            ]
            .astype(float)
        )

        explanation = (
            explain_row(
                model,
                X,
            )
        )

        print(
            "-" * 76
        )

        print(
            scenario.name
        )

        print(
            scenario.description
        )

        print()

        print(
            f"Escalation probability : "
            f"{explanation['probability']:.4f}"
        )

        print()

        print(
            "TOP MODEL DRIVERS"
        )

        print()

        for (
            index,
            feature,
        ) in enumerate(
            explanation[
                "top_features"
            ],
            start=1,
        ):

            sign = (
                "+"
                if feature[
                    "contribution"
                ] >= 0
                else ""
            )

            print(
                f"{index}. "
                f"{feature['label']}"
            )

            print(
                f"   Value        : "
                f"{feature['value']}"
            )

            print(
                f"   Contribution : "
                f"{sign}"
                f"{feature['contribution']:.4f}"
            )

            print(
                f"   Direction    : "
                f"{feature['direction']}"
            )

            print()

        report_scenarios.append(
            {
                "scenario":
                    scenario.name,

                "description":
                    scenario.description,

                "expected_escalation":
                    scenario.expected_escalation,

                "explanation":
                    explanation,
            }
        )

    report = {
        "important_note":
            (
                "XGBoost feature contributions explain "
                "prototype model behavior on synthetic data. "
                "They do not establish physical causality."
            ),

        "method":
            (
                "XGBoost native SHAP-style "
                "feature contributions"
            ),

        "top_feature_count":
            TOP_FEATURE_COUNT,

        "scenarios":
            report_scenarios,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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
        "=" * 76
    )

    print(
        "EXPLAINABILITY REPORT COMPLETE"
    )

    print(
        "=" * 76
    )

    print()

    print(
        "Report saved to:"
    )

    print(
        f"  {REPORT_PATH}"
    )

    print()

    print(
        (
            "IMPORTANT: Feature contributions explain "
            "the model prediction. They do not prove "
            "electrical causality."
        )
    )


if __name__ == "__main__":
    main()