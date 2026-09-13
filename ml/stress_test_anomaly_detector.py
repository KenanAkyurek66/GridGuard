from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from ml.stress_test_predictive_model import (
    OBSERVED_STEPS,
    create_noisy_safe_scenario,
    create_sensor_spike_scenario,
    create_stress_scenarios,
)

from ml.train_anomaly_detector import (
    ANOMALY_FEATURE_COLUMNS,
)

from ml.train_predictive_model import (
    engineer_features,
)


# ============================================================
# GRIDGUARD AI - ANOMALY DETECTOR OOD PROFILE
# ============================================================
#
# Purpose
# -------
# Observe how the Isolation Forest reacts to manually designed
# out-of-distribution scenarios.
#
# IMPORTANT
# ---------
# "ANOMALY" does NOT mean "electrical fault".
#
# It means:
#
#   "This telemetry pattern differs from the healthy behavior
#    learned by the unsupervised model."
#
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

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
    / "anomaly_ood_profile.json"
)


# ============================================================
# LOAD CONFIG
# ============================================================


def load_threshold() -> float:

    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        config = json.load(
            file
        )

    return float(
        config[
            "threshold"
        ]
    )


# ============================================================
# ANOMALY LEVEL
# ============================================================


def anomaly_level(
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
# MAIN
# ============================================================


def main() -> None:

    print(
        "=" * 76
    )

    print(
        "GRIDGUARD AI - ANOMALY DETECTOR OOD PROFILE"
    )

    print(
        "=" * 76
    )

    print()

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            (
                "Isolation Forest model not found:\n"
                f"{MODEL_PATH}"
            )
        )

    if not CONFIG_PATH.exists():

        raise FileNotFoundError(
            (
                "Anomaly detector configuration not found:\n"
                f"{CONFIG_PATH}"
            )
        )

    model = joblib.load(
        MODEL_PATH
    )

    threshold = load_threshold()

    print(
        f"Normality threshold : "
        f"{threshold:.6f}"
    )

    print()

    # ========================================================
    # BUILD OOD SCENARIOS
    # ========================================================

    scenarios = (
        create_stress_scenarios()
    )

    scenarios.append(
        create_sensor_spike_scenario()
    )

    scenarios.append(
        create_noisy_safe_scenario()
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

    results = []

    # ========================================================
    # SCORE EACH SCENARIO
    # ========================================================

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
                ANOMALY_FEATURE_COLUMNS
            ]
            .astype(float)
        )

        normality_score = float(
            model.score_samples(
                X
            )[0]
        )

        strength = float(
            threshold
            - normality_score
        )

        is_anomaly = (
            normality_score
            < threshold
        )

        level = anomaly_level(
            strength
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
            f"Expected escalation : "
            f"{scenario.expected_escalation}"
        )

        print(
            f"Normality score     : "
            f"{normality_score:.6f}"
        )

        print(
            f"Threshold           : "
            f"{threshold:.6f}"
        )

        print(
            f"Anomaly strength    : "
            f"{strength:+.6f}"
        )

        print(
            f"Anomaly detected    : "
            f"{is_anomaly}"
        )

        print(
            f"Anomaly level       : "
            f"{level}"
        )

        print()

        results.append(
            {
                "scenario":
                    scenario.name,

                "description":
                    scenario.description,

                "expected_escalation":
                    scenario.expected_escalation,

                "normality_score":
                    round(
                        normality_score,
                        6,
                    ),

                "threshold":
                    round(
                        threshold,
                        6,
                    ),

                "anomaly_strength":
                    round(
                        strength,
                        6,
                    ),

                "anomaly_detected":
                    bool(
                        is_anomaly
                    ),

                "anomaly_level":
                    level,
            }
        )

    # ========================================================
    # SORT BY ANOMALY STRENGTH
    # ========================================================

    ranked = sorted(
        results,
        key=lambda item:
            item[
                "anomaly_strength"
            ],
        reverse=True,
    )

    print(
        "=" * 76
    )

    print(
        "ANOMALY RANKING"
    )

    print(
        "=" * 76
    )

    print()

    for (
        index,
        item,
    ) in enumerate(
        ranked,
        start=1,
    ):

        print(
            f"{index:>2}. "
            f"{item['scenario']:<32} "
            f"{item['anomaly_strength']:+.6f} "
            f"{item['anomaly_level']}"
        )

    print()

    # ========================================================
    # GROUP SUMMARY
    # ========================================================

    escalation_results = [
        item
        for item in results
        if item[
            "expected_escalation"
        ]
        == 1
    ]

    non_escalation_results = [
        item
        for item in results
        if item[
            "expected_escalation"
        ]
        == 0
    ]

    escalation_anomalies = sum(
        1
        for item in escalation_results
        if item[
            "anomaly_detected"
        ]
    )

    non_escalation_anomalies = sum(
        1
        for item in non_escalation_results
        if item[
            "anomaly_detected"
        ]
    )

    print(
        "=" * 76
    )

    print(
        "OOD PROFILE SUMMARY"
    )

    print(
        "=" * 76
    )

    print()

    print(
        f"Escalation scenarios      : "
        f"{len(escalation_results)}"
    )

    print(
        f"Escalation also anomalous : "
        f"{escalation_anomalies}"
    )

    print()

    print(
        f"Non-escalation scenarios  : "
        f"{len(non_escalation_results)}"
    )

    print(
        f"Non-escalation anomalous  : "
        f"{non_escalation_anomalies}"
    )

    print()

    print(
        (
            "NOTE: A non-escalation scenario may still be "
            "correctly classified as anomalous because "
            "unusual behavior is not equivalent to danger."
        )
    )

    print()

    # ========================================================
    # SAVE REPORT
    # ========================================================

    report = {
        "important_note":
            (
                "OOD anomaly profiling on manually designed "
                "synthetic scenarios. Anomaly detection does "
                "not represent fault classification and is "
                "not field validation."
            ),

        "threshold":
            threshold,

        "scenarios":
            results,

        "ranking":
            ranked,

        "summary": {
            "escalation_scenarios":
                len(
                    escalation_results
                ),

            "escalation_also_anomalous":
                escalation_anomalies,

            "non_escalation_scenarios":
                len(
                    non_escalation_results
                ),

            "non_escalation_anomalous":
                non_escalation_anomalies,
        },
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
        "Report saved to:"
    )

    print(
        f"  {REPORT_PATH}"
    )

    print()

    print(
        "=" * 76
    )

    print(
        "GRIDGUARD ANOMALY OOD PROFILE COMPLETE"
    )

    print(
        "=" * 76
    )


if __name__ == "__main__":
    main()