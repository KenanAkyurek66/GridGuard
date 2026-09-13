from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from ml.train_predictive_model import (
    FEATURE_COLUMNS,
    engineer_features,
)


# ============================================================
# GRIDGUARD AI - PREDICTIVE MODEL STRESS / OOD TEST
# ============================================================
#
# Purpose
# -------
# Evaluate the trained predictive model on manually designed
# scenarios that are intentionally different from the synthetic
# training generator.
#
# IMPORTANT
# ---------
# These tests are NOT field validation.
#
# They are robustness / sanity tests for the prototype model.
#
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "xgboost_early_warning.joblib"
)

TRAINING_REPORT_PATH = (
    PROJECT_ROOT
    / "ml"
    / "reports"
    / "predictive_model_report.json"
)

STRESS_REPORT_PATH = (
    PROJECT_ROOT
    / "ml"
    / "reports"
    / "predictive_stress_test_report.json"
)


OBSERVED_STEPS = 15
FUTURE_STEPS = 5


# ============================================================
# DATA STRUCTURE
# ============================================================


@dataclass
class StressScenario:
    name: str
    description: str
    expected_escalation: int
    rows: list[dict]


# ============================================================
# HELPERS
# ============================================================


def interpolate(
    start: float,
    end: float,
    step: int,
    total_steps: int,
) -> float:

    if total_steps <= 1:
        return end

    ratio = (
        step
        / (
            total_steps
            - 1
        )
    )

    return (
        start
        + (
            end
            - start
        )
        * ratio
    )


def make_row(
    scenario_id: str,
    scenario_type: str,
    timestep: int,
    current: float,
    cable_temp: float,
    ambient_temp: float,
    humidity: float,
    pd_index: float,
    data_quality: str = "GOOD",
) -> dict:

    return {
        "scenario_id":
            scenario_id,

        "scenario_type":
            scenario_type,

        "timestep":
            timestep,

        "current_a":
            round(
                current,
                3,
            ),

        "cable_temperature_c":
            round(
                cable_temp,
                3,
            ),

        "ambient_temperature_c":
            round(
                ambient_temp,
                3,
            ),

        "humidity_pct":
            round(
                humidity,
                3,
            ),

        "pd_index":
            round(
                pd_index,
                3,
            ),

        "arc_detected":
            0,

        "data_quality":
            data_quality,

        "latent_severity":
            0,

        "future_escalation":
            0,
    }


def build_linear_scenario(
    scenario_id: str,
    scenario_type: str,
    observed_start: dict,
    observed_end: dict,
    future_end: dict,
    expected_escalation: int,
    description: str,
) -> StressScenario:

    rows: list[dict] = []

    for timestep in range(
        OBSERVED_STEPS
    ):

        rows.append(
            make_row(
                scenario_id=scenario_id,
                scenario_type=scenario_type,
                timestep=timestep,

                current=interpolate(
                    observed_start["current"],
                    observed_end["current"],
                    timestep,
                    OBSERVED_STEPS,
                ),

                cable_temp=interpolate(
                    observed_start["cable"],
                    observed_end["cable"],
                    timestep,
                    OBSERVED_STEPS,
                ),

                ambient_temp=interpolate(
                    observed_start["ambient"],
                    observed_end["ambient"],
                    timestep,
                    OBSERVED_STEPS,
                ),

                humidity=interpolate(
                    observed_start["humidity"],
                    observed_end["humidity"],
                    timestep,
                    OBSERVED_STEPS,
                ),

                pd_index=interpolate(
                    observed_start["pd"],
                    observed_end["pd"],
                    timestep,
                    OBSERVED_STEPS,
                ),
            )
        )

    for future_offset in range(
        1,
        FUTURE_STEPS + 1,
    ):

        timestep = (
            OBSERVED_STEPS
            - 1
            + future_offset
        )

        rows.append(
            make_row(
                scenario_id=scenario_id,
                scenario_type=scenario_type,
                timestep=timestep,

                current=interpolate(
                    observed_end["current"],
                    future_end["current"],
                    future_offset,
                    FUTURE_STEPS,
                ),

                cable_temp=interpolate(
                    observed_end["cable"],
                    future_end["cable"],
                    future_offset,
                    FUTURE_STEPS,
                ),

                ambient_temp=interpolate(
                    observed_end["ambient"],
                    future_end["ambient"],
                    future_offset,
                    FUTURE_STEPS,
                ),

                humidity=interpolate(
                    observed_end["humidity"],
                    future_end["humidity"],
                    future_offset,
                    FUTURE_STEPS,
                ),

                pd_index=interpolate(
                    observed_end["pd"],
                    future_end["pd"],
                    future_offset,
                    FUTURE_STEPS,
                ),
            )
        )

    return StressScenario(
        name=scenario_type,
        description=description,
        expected_escalation=expected_escalation,
        rows=rows,
    )


# ============================================================
# MANUALLY DESIGNED OOD / STRESS SCENARIOS
# ============================================================


def create_stress_scenarios() -> list[StressScenario]:

    scenarios: list[
        StressScenario
    ] = []

    # --------------------------------------------------------
    # NEGATIVE 1
    # High ambient temperature, but cable remains reasonably
    # close to ambient and no dangerous trend develops.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-001",
            scenario_type="HOT_AMBIENT_SAFE_DELTA",

            observed_start={
                "current": 290,
                "cable": 46,
                "ambient": 32,
                "humidity": 42,
                "pd": 10,
            },

            observed_end={
                "current": 305,
                "cable": 55,
                "ambient": 44,
                "humidity": 44,
                "pd": 11,
            },

            future_end={
                "current": 310,
                "cable": 57,
                "ambient": 46,
                "humidity": 45,
                "pd": 11,
            },

            expected_escalation=0,

            description=(
                "High ambient temperature with a relatively "
                "healthy cable-to-ambient thermal delta."
            ),
        )
    )

    # --------------------------------------------------------
    # NEGATIVE 2
    # Current increases, but temperature remains stable.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-002",
            scenario_type="CURRENT_RISE_NO_HEAT",

            observed_start={
                "current": 270,
                "cable": 43,
                "ambient": 30,
                "humidity": 45,
                "pd": 12,
            },

            observed_end={
                "current": 405,
                "cable": 48,
                "ambient": 31,
                "humidity": 45,
                "pd": 12,
            },

            future_end={
                "current": 420,
                "cable": 49,
                "ambient": 31,
                "humidity": 46,
                "pd": 13,
            },

            expected_escalation=0,

            description=(
                "Current rises significantly but without "
                "corresponding thermal deterioration."
            ),
        )
    )

    # --------------------------------------------------------
    # NEGATIVE 3
    # High humidity only.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-003",
            scenario_type="HIGH_HUMIDITY_ONLY",

            observed_start={
                "current": 285,
                "cable": 44,
                "ambient": 30,
                "humidity": 55,
                "pd": 10,
            },

            observed_end={
                "current": 290,
                "cable": 45,
                "ambient": 30,
                "humidity": 88,
                "pd": 12,
            },

            future_end={
                "current": 292,
                "cable": 45,
                "ambient": 30,
                "humidity": 91,
                "pd": 13,
            },

            expected_escalation=0,

            description=(
                "Very high humidity without thermal, current "
                "or partial-discharge escalation."
            ),
        )
    )

    # --------------------------------------------------------
    # NEGATIVE 4
    # Shifted but internally healthy baseline.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-004",
            scenario_type="SHIFTED_BASELINE_SAFE",

            observed_start={
                "current": 345,
                "cable": 49,
                "ambient": 36,
                "humidity": 48,
                "pd": 15,
            },

            observed_end={
                "current": 365,
                "cable": 52,
                "ambient": 38,
                "humidity": 50,
                "pd": 17,
            },

            future_end={
                "current": 370,
                "cable": 53,
                "ambient": 39,
                "humidity": 50,
                "pd": 18,
            },

            expected_escalation=0,

            description=(
                "A higher-than-usual operating baseline that "
                "remains stable and internally consistent."
            ),
        )
    )

    # --------------------------------------------------------
    # NEGATIVE 5
    # Recovery trend.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-005",
            scenario_type="RECOVERY_TREND",

            observed_start={
                "current": 430,
                "cable": 64,
                "ambient": 31,
                "humidity": 50,
                "pd": 35,
            },

            observed_end={
                "current": 350,
                "cable": 53,
                "ambient": 31,
                "humidity": 48,
                "pd": 22,
            },

            future_end={
                "current": 310,
                "cable": 47,
                "ambient": 30,
                "humidity": 47,
                "pd": 15,
            },

            expected_escalation=0,

            description=(
                "Previously elevated measurements are actively "
                "recovering instead of deteriorating."
            ),
        )
    )

    # --------------------------------------------------------
    # POSITIVE 1
    # Slow thermal escalation.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-006",
            scenario_type="SLOW_THERMAL_ESCALATION",

            observed_start={
                "current": 300,
                "cable": 43,
                "ambient": 30,
                "humidity": 44,
                "pd": 12,
            },

            observed_end={
                "current": 395,
                "cable": 64,
                "ambient": 31,
                "humidity": 45,
                "pd": 14,
            },

            future_end={
                "current": 445,
                "cable": 74,
                "ambient": 32,
                "humidity": 46,
                "pd": 15,
            },

            expected_escalation=1,

            description=(
                "Slow but persistent cable heating with rising "
                "load and a widening thermal delta."
            ),
        )
    )

    # --------------------------------------------------------
    # POSITIVE 2
    # Load-driven thermal escalation.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-007",
            scenario_type="LOAD_THERMAL_ESCALATION",

            observed_start={
                "current": 305,
                "cable": 45,
                "ambient": 30,
                "humidity": 43,
                "pd": 10,
            },

            observed_end={
                "current": 430,
                "cable": 65,
                "ambient": 31,
                "humidity": 44,
                "pd": 12,
            },

            future_end={
                "current": 495,
                "cable": 78,
                "ambient": 32,
                "humidity": 44,
                "pd": 13,
            },

            expected_escalation=1,

            description=(
                "Current and cable temperature rise together "
                "toward a severe thermal condition."
            ),
        )
    )

    # --------------------------------------------------------
    # POSITIVE 3
    # PD escalation.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-008",
            scenario_type="PD_ESCALATION",

            observed_start={
                "current": 285,
                "cable": 44,
                "ambient": 30,
                "humidity": 45,
                "pd": 12,
            },

            observed_end={
                "current": 290,
                "cable": 45,
                "ambient": 30,
                "humidity": 46,
                "pd": 60,
            },

            future_end={
                "current": 292,
                "cable": 45,
                "ambient": 30,
                "humidity": 47,
                "pd": 82,
            },

            expected_escalation=1,

            description=(
                "Partial-discharge activity rises strongly "
                "while other measurements remain stable."
            ),
        )
    )

    # --------------------------------------------------------
    # POSITIVE 4
    # Humidity + PD combined deterioration.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-009",
            scenario_type="HUMIDITY_PD_ESCALATION",

            observed_start={
                "current": 280,
                "cable": 43,
                "ambient": 29,
                "humidity": 50,
                "pd": 15,
            },

            observed_end={
                "current": 285,
                "cable": 46,
                "ambient": 30,
                "humidity": 79,
                "pd": 52,
            },

            future_end={
                "current": 290,
                "cable": 47,
                "ambient": 30,
                "humidity": 88,
                "pd": 76,
            },

            expected_escalation=1,

            description=(
                "Humidity and partial-discharge indicators "
                "deteriorate together."
            ),
        )
    )

    # --------------------------------------------------------
    # POSITIVE 5
    # Subtle combined deterioration.
    # --------------------------------------------------------

    scenarios.append(
        build_linear_scenario(
            scenario_id="OOD-010",
            scenario_type="SUBTLE_COMBINED_ESCALATION",

            observed_start={
                "current": 295,
                "cable": 44,
                "ambient": 31,
                "humidity": 50,
                "pd": 14,
            },

            observed_end={
                "current": 385,
                "cable": 59,
                "ambient": 32,
                "humidity": 66,
                "pd": 42,
            },

            future_end={
                "current": 465,
                "cable": 71,
                "ambient": 33,
                "humidity": 72,
                "pd": 62,
            },

            expected_escalation=1,

            description=(
                "Several moderate signals deteriorate together "
                "before any single measurement becomes extreme."
            ),
        )
    )

    return scenarios


# ============================================================
# SINGLE SENSOR SPIKE SPECIAL CASE
# ============================================================


def create_sensor_spike_scenario() -> StressScenario:

    rows: list[dict] = []

    for timestep in range(
        OBSERVED_STEPS
        + FUTURE_STEPS
    ):

        current = 300.0
        cable_temp = 45.0
        ambient_temp = 30.0
        humidity = 45.0
        pd_index = 12.0
        data_quality = "GOOD"

        # Spike occurs exactly at the evaluation point.
        if timestep == (
            OBSERVED_STEPS
            - 1
        ):

            current = 455.0
            cable_temp = 67.0
            pd_index = 50.0
            data_quality = "SUSPECT"

        rows.append(
            make_row(
                scenario_id="OOD-011",
                scenario_type="SINGLE_SENSOR_SPIKE",

                timestep=timestep,

                current=current,
                cable_temp=cable_temp,
                ambient_temp=ambient_temp,
                humidity=humidity,
                pd_index=pd_index,
                data_quality=data_quality,
            )
        )

    return StressScenario(
        name="SINGLE_SENSOR_SPIKE",

        description=(
            "A one-cycle multi-sensor spike marked as SUSPECT "
            "that immediately returns to normal."
        ),

        expected_escalation=0,

        rows=rows,
    )


# ============================================================
# NOISY SAFE SPECIAL CASE
# ============================================================


def create_noisy_safe_scenario() -> StressScenario:

    current_values = [
        302,
        294,
        311,
        287,
        318,
        299,
        306,
        291,
        315,
        296,
        309,
        301,
        313,
        292,
        305,
        300,
        303,
        297,
        304,
        301,
    ]

    cable_values = [
        45,
        46,
        44,
        47,
        45,
        46,
        44,
        45,
        47,
        45,
        46,
        45,
        44,
        46,
        45,
        45,
        46,
        45,
        45,
        46,
    ]

    pd_values = [
        12,
        15,
        10,
        17,
        11,
        14,
        9,
        16,
        12,
        13,
        11,
        15,
        10,
        14,
        12,
        13,
        12,
        11,
        13,
        12,
    ]

    rows: list[dict] = []

    for timestep in range(
        OBSERVED_STEPS
        + FUTURE_STEPS
    ):

        rows.append(
            make_row(
                scenario_id="OOD-012",
                scenario_type="NOISY_SAFE",

                timestep=timestep,

                current=current_values[
                    timestep
                ],

                cable_temp=cable_values[
                    timestep
                ],

                ambient_temp=30.0,

                humidity=46.0,

                pd_index=pd_values[
                    timestep
                ],
            )
        )

    return StressScenario(
        name="NOISY_SAFE",

        description=(
            "Noisy but bounded healthy telemetry with no "
            "persistent trend."
        ),

        expected_escalation=0,

        rows=rows,
    )


# ============================================================
# LOAD MODEL / THRESHOLD
# ============================================================


def load_threshold() -> float:

    with TRAINING_REPORT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        report = json.load(
            file
        )

    return float(
        report[
            "xgboost"
        ][
            "validation_f2_threshold"
        ]
    )


# ============================================================
# MAIN EVALUATION
# ============================================================


def main() -> None:

    print(
        "=" * 74
    )

    print(
        "GRIDGUARD AI - PREDICTIVE MODEL STRESS / OOD TEST"
    )

    print(
        "=" * 74
    )

    print()

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            (
                "Predictive model not found:\n"
                f"{MODEL_PATH}\n\n"
                "Train the model first."
            )
        )

    if not TRAINING_REPORT_PATH.exists():

        raise FileNotFoundError(
            (
                "Training report not found:\n"
                f"{TRAINING_REPORT_PATH}"
            )
        )

    model = joblib.load(
        MODEL_PATH
    )

    threshold = load_threshold()

    print(
        f"Model threshold: {threshold:.4f}"
    )

    print()

    scenarios = (
        create_stress_scenarios()
    )

    scenarios.append(
        create_sensor_spike_scenario()
    )

    scenarios.append(
        create_noisy_safe_scenario()
    )

    all_rows: list[dict] = []

    for scenario in scenarios:

        all_rows.extend(
            scenario.rows
        )

    dataframe = pd.DataFrame(
        all_rows
    )

    # Feature engineering is causal:
    # rolling windows use only current / previous rows.
    engineered = engineer_features(
        dataframe
    )

    results = []

    passed = 0

    positive_total = 0
    negative_total = 0

    positive_detected = 0
    negative_correct = 0

    for scenario in scenarios:

        scenario_frame = engineered[
            engineered[
                "scenario_id"
            ]
            == scenario.rows[0][
                "scenario_id"
            ]
        ].sort_values(
            "timestep"
        )

        # Evaluate at the final observed point.
        #
        # The following five rows represent the future and are
        # intentionally NOT passed into the prediction feature
        # vector.
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

        probability = float(
            model.predict_proba(
                X
            )[0, 1]
        )

        prediction = int(
            probability
            >= threshold
        )

        is_pass = (
            prediction
            == scenario.expected_escalation
        )

        if is_pass:
            passed += 1

        if (
            scenario.expected_escalation
            == 1
        ):

            positive_total += 1

            if prediction == 1:
                positive_detected += 1

        else:

            negative_total += 1

            if prediction == 0:
                negative_correct += 1

        status = (
            "PASS"
            if is_pass
            else "MISS"
        )

        print(
            "-" * 74
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
            f"Model probability   : "
            f"{probability:.4f}"
        )

        print(
            f"Model prediction    : "
            f"{prediction}"
        )

        print(
            f"Result              : "
            f"[{status}]"
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

                "probability":
                    round(
                        probability,
                        6,
                    ),

                "threshold":
                    round(
                        threshold,
                        6,
                    ),

                "prediction":
                    prediction,

                "result":
                    status,
            }
        )

    total = len(
        scenarios
    )

    pass_rate = (
        passed
        / total
        * 100
    )

    positive_recall = (
        positive_detected
        / positive_total
        if positive_total
        else 0.0
    )

    negative_specificity = (
        negative_correct
        / negative_total
        if negative_total
        else 0.0
    )

    print(
        "=" * 74
    )

    print(
        "STRESS TEST SUMMARY"
    )

    print(
        "=" * 74
    )

    print(
        f"Total scenarios      : "
        f"{total}"
    )

    print(
        f"Passed               : "
        f"{passed}"
    )

    print(
        f"Missed               : "
        f"{total - passed}"
    )

    print(
        f"Pass rate            : "
        f"{pass_rate:.2f}%"
    )

    print()

    print(
        f"Positive cases       : "
        f"{positive_total}"
    )

    print(
        f"Positive detected    : "
        f"{positive_detected}"
    )

    print(
        f"Stress recall        : "
        f"{positive_recall:.2%}"
    )

    print()

    print(
        f"Negative cases       : "
        f"{negative_total}"
    )

    print(
        f"Negative correct     : "
        f"{negative_correct}"
    )

    print(
        f"Stress specificity   : "
        f"{negative_specificity:.2%}"
    )

    print()

    report = {
        "important_note":
            (
                "Prototype robustness test using manually "
                "designed synthetic OOD scenarios. "
                "This is not field validation."
            ),

        "model":
            str(
                MODEL_PATH
            ),

        "threshold":
            threshold,

        "total_scenarios":
            total,

        "passed":
            passed,

        "missed":
            total - passed,

        "pass_rate_pct":
            round(
                pass_rate,
                2,
            ),

        "positive_cases":
            positive_total,

        "positive_detected":
            positive_detected,

        "stress_recall":
            round(
                positive_recall,
                6,
            ),

        "negative_cases":
            negative_total,

        "negative_correct":
            negative_correct,

        "stress_specificity":
            round(
                negative_specificity,
                6,
            ),

        "scenarios":
            results,
    }

    STRESS_REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with STRESS_REPORT_PATH.open(
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
        f"Report saved to:"
    )

    print(
        f"  {STRESS_REPORT_PATH}"
    )

    print()

    print(
        "Interpretation:"
    )

    print(
        (
            "This test measures prototype robustness "
            "against unusual synthetic scenarios."
        )
    )

    print(
        (
            "It must not be interpreted as real-world "
            "utility field accuracy."
        )
    )

    print(
        "=" * 74
    )


if __name__ == "__main__":
    main()