from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from ml.quality_guard import (
    DECISION_ESCALATION,
    DECISION_HOLD,
    DECISION_SAFE,
    evaluate_quality_guard,
)

from ml.stress_test_predictive_model import (
    OBSERVED_STEPS,
    create_noisy_safe_scenario,
    create_sensor_spike_scenario,
    create_stress_scenarios,
)

from ml.train_predictive_model import (
    FEATURE_COLUMNS,
    engineer_features,
)


# ============================================================
# GRIDGUARD AI - QUALITY GUARD STRESS TEST
# ============================================================
#
# Purpose
# -------
# Validate the combined:
#
#   Predictive Model
#        +
#   Data Quality Guard
#        +
#   Persistence Logic
#
# against the manually designed OOD / stress scenarios.
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

OUTPUT_REPORT_PATH = (
    PROJECT_ROOT
    / "ml"
    / "reports"
    / "quality_guard_stress_report.json"
)


RECENT_WINDOW = 3


# ============================================================
# THRESHOLD
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
# EXPECTED DECISION
# ============================================================


def expected_decision_for(
    scenario_name: str,
    expected_escalation: int,
) -> str:

    # --------------------------------------------------------
    # The model previously produced a false positive here.
    #
    # The correct operational behavior is neither:
    #
    # SAFE
    #
    # nor:
    #
    # ESCALATION
    #
    # because the telemetry itself is explicitly SUSPECT.
    #
    # GridGuard should abstain and request confirmation.
    # --------------------------------------------------------

    if (
        scenario_name
        == "SINGLE_SENSOR_SPIKE"
    ):

        return DECISION_HOLD

    if expected_escalation == 1:
        return DECISION_ESCALATION

    return DECISION_SAFE


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    print(
        "=" * 76
    )

    print(
        "GRIDGUARD AI - QUALITY GUARD STRESS TEST"
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

    if not TRAINING_REPORT_PATH.exists():

        raise FileNotFoundError(
            (
                "Predictive training report not found:\n"
                f"{TRAINING_REPORT_PATH}"
            )
        )

    model = joblib.load(
        MODEL_PATH
    )

    threshold = load_threshold()

    print(
        f"Predictive threshold : "
        f"{threshold:.4f}"
    )

    print(
        f"Recent window        : "
        f"{RECENT_WINDOW}"
    )

    print()

    # ========================================================
    # BUILD SCENARIOS
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

    all_rows: list[dict] = []

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

    # ========================================================
    # EVALUATION
    # ========================================================

    results = []

    passed = 0

    decision_counts = {
        DECISION_SAFE: 0,
        DECISION_HOLD: 0,
        DECISION_ESCALATION: 0,
    }

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

        # ----------------------------------------------------
        # Only use observed telemetry.
        #
        # Future rows exist exclusively to define the manually
        # designed stress scenario outcome.
        # ----------------------------------------------------

        observed_frame = (
            scenario_frame[
                scenario_frame[
                    "timestep"
                ]
                <= (
                    OBSERVED_STEPS
                    - 1
                )
            ]
        )

        recent_frame = (
            observed_frame
            .tail(
                RECENT_WINDOW
            )
        )

        X_recent = (
            recent_frame[
                FEATURE_COLUMNS
            ]
            .astype(float)
        )

        recent_probabilities = (
            model
            .predict_proba(
                X_recent
            )[:, 1]
            .astype(float)
            .tolist()
        )

        recent_quality = (
            recent_frame[
                "data_quality"
            ]
            .astype(str)
            .tolist()
        )

        decision = (
            evaluate_quality_guard(
                recent_probabilities=(
                    recent_probabilities
                ),

                recent_data_quality=(
                    recent_quality
                ),

                threshold=threshold,

                consecutive_required=2,

                strong_confidence_margin=0.20,
            )
        )

        expected = (
            expected_decision_for(
                scenario_name=(
                    scenario.name
                ),

                expected_escalation=(
                    scenario.expected_escalation
                ),
            )
        )

        is_pass = (
            decision.decision
            == expected
        )

        if is_pass:
            passed += 1

        decision_counts[
            decision.decision
        ] += 1

        status = (
            "PASS"
            if is_pass
            else "MISS"
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
            "Recent probabilities:"
        )

        for (
            index,
            probability,
        ) in enumerate(
            recent_probabilities,
            start=1,
        ):

            print(
                f"  t-{RECENT_WINDOW - index} "
                f": {probability:.4f}"
            )

        print()

        print(
            "Recent quality:"
        )

        for quality in recent_quality:

            print(
                f"  {quality}"
            )

        print()

        print(
            f"Expected decision : "
            f"{expected}"
        )

        print(
            f"Guard decision    : "
            f"{decision.decision}"
        )

        print(
            f"Latest probability: "
            f"{decision.latest_probability:.4f}"
        )

        print(
            f"Consecutive high  : "
            f"{decision.consecutive_high_predictions}"
        )

        print(
            f"Reliable data     : "
            f"{decision.data_reliable}"
        )

        print()

        print(
            f"Reason:"
        )

        print(
            f"  {decision.reason}"
        )

        print()

        print(
            f"Result            : "
            f"[{status}]"
        )

        print()

        results.append(
            {
                "scenario":
                    scenario.name,

                "description":
                    scenario.description,

                "expected_decision":
                    expected,

                "guard_decision":
                    decision.decision,

                "recent_probabilities":
                    [
                        round(
                            probability,
                            6,
                        )
                        for probability
                        in recent_probabilities
                    ],

                "recent_quality":
                    recent_quality,

                "decision_details":
                    decision.to_dict(),

                "result":
                    status,
            }
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    total = len(
        scenarios
    )

    missed = (
        total
        - passed
    )

    pass_rate = (
        passed
        / total
        * 100.0
    )

    print(
        "=" * 76
    )

    print(
        "QUALITY GUARD STRESS TEST SUMMARY"
    )

    print(
        "=" * 76
    )

    print(
        f"Total scenarios : "
        f"{total}"
    )

    print(
        f"Passed          : "
        f"{passed}"
    )

    print(
        f"Missed          : "
        f"{missed}"
    )

    print(
        f"Pass rate       : "
        f"{pass_rate:.2f}%"
    )

    print()

    print(
        "Decision distribution:"
    )

    print(
        f"  SAFE       : "
        f"{decision_counts[DECISION_SAFE]}"
    )

    print(
        f"  HOLD       : "
        f"{decision_counts[DECISION_HOLD]}"
    )

    print(
        f"  ESCALATION : "
        f"{decision_counts[DECISION_ESCALATION]}"
    )

    print()

    # ========================================================
    # SAVE REPORT
    # ========================================================

    report = {
        "important_note":
            (
                "Synthetic prototype robustness test. "
                "This is not real-world field validation."
            ),

        "predictive_threshold":
            threshold,

        "recent_window":
            RECENT_WINDOW,

        "guard_configuration": {
            "consecutive_required":
                2,

            "strong_confidence_margin":
                0.20,

            "suspect_recent_data":
                "HOLD",
        },

        "total_scenarios":
            total,

        "passed":
            passed,

        "missed":
            missed,

        "pass_rate_pct":
            round(
                pass_rate,
                2,
            ),

        "decision_distribution":
            decision_counts,

        "scenarios":
            results,
    }

    OUTPUT_REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_REPORT_PATH.open(
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
        f"  {OUTPUT_REPORT_PATH}"
    )

    print()

    print(
        "Interpretation:"
    )

    print(
        (
            "GridGuard's predictive ML layer may abstain "
            "instead of issuing an escalation advisory when "
            "telemetry quality is unreliable or evidence has "
            "not yet persisted."
        )
    )

    print()

    if missed == 0:

        print(
            "ALL QUALITY GUARD STRESS TESTS PASSED"
        )

    else:

        print(
            (
                "Some scenarios did not match the expected "
                "guard behavior. Review MISS cases before "
                "integration."
            )
        )

    print(
        "=" * 76
    )


if __name__ == "__main__":
    main()