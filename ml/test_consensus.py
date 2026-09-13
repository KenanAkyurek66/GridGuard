from __future__ import annotations

from ml.consensus import (
    CONSENSUS_ACTION_REQUIRED,
    CONSENSUS_CRITICAL,
    CONSENSUS_EARLY_WARNING,
    CONSENSUS_HOLD,
    CONSENSUS_NORMAL,
    CONSENSUS_OBSERVE,
    evaluate_consensus,
)


# ============================================================
# GRIDGUARD AI - CONSENSUS ENGINE TESTS
# ============================================================


def run_case(
    *,
    name: str,
    expected_status: str,

    rule_status: str,
    rule_score: float,

    predictive_decision: str,
    predictive_probability: float,

    anomaly_detected: bool,
    anomaly_level: str,

    data_quality_reliable: bool,
) -> None:

    print(
        "=" * 72
    )

    print(
        name
    )

    print(
        "=" * 72
    )

    result = evaluate_consensus(
        rule_status=rule_status,
        rule_score=rule_score,

        predictive_decision=(
            predictive_decision
        ),

        predictive_probability=(
            predictive_probability
        ),

        anomaly_detected=(
            anomaly_detected
        ),

        anomaly_level=(
            anomaly_level
        ),

        data_quality_reliable=(
            data_quality_reliable
        ),
    )

    print(
        f"Expected status : "
        f"{expected_status}"
    )

    print(
        f"Actual status   : "
        f"{result.status}"
    )

    print(
        f"Confidence      : "
        f"{result.confidence}"
    )

    print(
        f"Agreement       : "
        f"{result.agreement_text}"
    )

    print(
        f"Summary         : "
        f"{result.summary}"
    )

    print()

    for reason in result.reasons:

        print(
            f"- {reason}"
        )

    print()

    assert (
        result.status
        == expected_status
    )

    print(
        "[PASS]"
    )

    print()


def main() -> None:

    # --------------------------------------------------------
    # 1. Fully healthy system
    # --------------------------------------------------------

    run_case(
        name="ALL LAYERS HEALTHY",

        expected_status=(
            CONSENSUS_NORMAL
        ),

        rule_status="NORMAL",
        rule_score=0,

        predictive_decision="SAFE",
        predictive_probability=0.02,

        anomaly_detected=False,
        anomaly_level="NORMAL",

        data_quality_reliable=True,
    )

    # --------------------------------------------------------
    # 2. Predictive early warning only
    # --------------------------------------------------------

    run_case(
        name="PREDICTIVE EARLY WARNING",

        expected_status=(
            CONSENSUS_EARLY_WARNING
        ),

        rule_status="NORMAL",
        rule_score=8,

        predictive_decision=(
            "ESCALATION"
        ),

        predictive_probability=0.82,

        anomaly_detected=False,
        anomaly_level="NORMAL",

        data_quality_reliable=True,
    )

    # --------------------------------------------------------
    # 3. Strong multi-layer agreement
    # --------------------------------------------------------

    run_case(
        name="MULTI-LAYER DETERIORATION",

        expected_status=(
            CONSENSUS_EARLY_WARNING
        ),

        rule_status="WARNING",
        rule_score=34,

        predictive_decision=(
            "ESCALATION"
        ),

        predictive_probability=0.91,

        anomaly_detected=True,
        anomaly_level="HIGH",

        data_quality_reliable=True,
    )

    # --------------------------------------------------------
    # 4. Anomaly only
    # --------------------------------------------------------

    run_case(
        name="UNKNOWN ANOMALOUS BEHAVIOR",

        expected_status=(
            CONSENSUS_OBSERVE
        ),

        rule_status="NORMAL",
        rule_score=5,

        predictive_decision="SAFE",
        predictive_probability=0.17,

        anomaly_detected=True,
        anomaly_level="HIGH",

        data_quality_reliable=True,
    )

    # --------------------------------------------------------
    # 5. Suspect sensor spike
    # --------------------------------------------------------

    run_case(
        name="SUSPECT SENSOR SPIKE",

        expected_status=(
            CONSENSUS_HOLD
        ),

        rule_status="NORMAL",
        rule_score=8,

        predictive_decision="HOLD",
        predictive_probability=0.85,

        anomaly_detected=True,
        anomaly_level="SEVERE",

        data_quality_reliable=False,
    )

    # --------------------------------------------------------
    # 6. Recovery remains unusual
    # --------------------------------------------------------

    run_case(
        name="RECOVERY ANOMALY",

        expected_status=(
            CONSENSUS_OBSERVE
        ),

        rule_status="NORMAL",
        rule_score=4,

        predictive_decision="SAFE",
        predictive_probability=0.01,

        anomaly_detected=True,
        anomaly_level="ELEVATED",

        data_quality_reliable=True,
    )

    # --------------------------------------------------------
    # 7. Deterministic HIGH
    # --------------------------------------------------------

    run_case(
        name="DETERMINISTIC HIGH",

        expected_status=(
            CONSENSUS_ACTION_REQUIRED
        ),

        rule_status="HIGH",
        rule_score=58,

        predictive_decision=(
            "ESCALATION"
        ),

        predictive_probability=0.88,

        anomaly_detected=True,
        anomaly_level="HIGH",

        data_quality_reliable=True,
    )

    # --------------------------------------------------------
    # 8. Deterministic CRITICAL safety override
    # --------------------------------------------------------

    run_case(
        name="CRITICAL SAFETY OVERRIDE",

        expected_status=(
            CONSENSUS_CRITICAL
        ),

        rule_status="CRITICAL",
        rule_score=100,

        predictive_decision="SAFE",
        predictive_probability=0.08,

        anomaly_detected=False,
        anomaly_level="NORMAL",

        data_quality_reliable=True,
    )

    print(
        "=" * 72
    )

    print(
        "ALL GRIDGUARD AI CONSENSUS TESTS PASSED"
    )

    print(
        "=" * 72
    )


if __name__ == "__main__":
    main()