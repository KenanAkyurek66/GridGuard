from __future__ import annotations

import time
from datetime import datetime, timezone

import requests


API_BASE = "http://127.0.0.1:8000"
PANEL_ID = "LV-050"

STEPS = [
    {
        "current_a": 320.0,
        "cable_temperature_c": 45.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 340.0,
        "cable_temperature_c": 48.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 370.0,
        "cable_temperature_c": 54.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 400.0,
        "cable_temperature_c": 60.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 435.0,
        "cable_temperature_c": 68.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 470.0,
        "cable_temperature_c": 76.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 500.0,
        "cable_temperature_c": 82.0,
        "ambient_temperature_c": 32.0,
    },
]


def post_telemetry(step: dict) -> None:

    payload = {
        "panel_id": PANEL_ID,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "current_a": step["current_a"],
        "cable_temperature_c": (
            step["cable_temperature_c"]
        ),
        "ambient_temperature_c": (
            step["ambient_temperature_c"]
        ),
        "humidity_pct": 44.0,
        "pd_index": 12.0,
        "arc_detected": False,
        "data_quality": "GOOD",
    }

    response = requests.post(
        f"{API_BASE}/telemetry",
        json=payload,
        timeout=10,
    )

    response.raise_for_status()


def get_rule_risk() -> dict:

    response = requests.get(
        f"{API_BASE}/panels/{PANEL_ID}/risk",
        timeout=10,
    )

    response.raise_for_status()

    payload = response.json()

    # Support either a direct risk object or a nested one.
    if (
        isinstance(payload, dict)
        and isinstance(
            payload.get("risk"),
            dict,
        )
    ):
        payload = payload["risk"]

    return payload


def get_intelligence() -> dict:

    response = requests.get(
        (
            f"{API_BASE}/panels/"
            f"{PANEL_ID}/intelligence"
        ),
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def main() -> None:

    print("=" * 88)
    print(
        "GRIDGUARD - OVERHEATING AI EARLY-WARNING TRACE"
    )
    print("=" * 88)
    print()

    first_predictive_warning_step = None
    first_rule_warning_step = None

    trace_rows = []

    for index, step in enumerate(
        STEPS,
        start=1,
    ):

        post_telemetry(
            step
        )

        # Give the backend a short moment to persist and
        # calculate the latest deterministic assessment.
        time.sleep(0.4)

        rule_result = get_rule_risk()

        intelligence = get_intelligence()

        predictive = intelligence[
            "predictive"
        ]

        anomaly = intelligence[
            "anomaly"
        ]

        consensus = intelligence[
            "consensus"
        ]

        rule_status = str(
            rule_result.get(
                "status",
                "UNKNOWN",
            )
        ).upper()

        rule_score = rule_result.get(
            "risk_score",
            "UNKNOWN",
        )

        primary_risk = rule_result.get(
            "primary_risk",
            "UNKNOWN",
        )

        predictive_decision = predictive[
            "decision"
        ]

        probability = predictive[
            "probability_pct"
        ]

        if (
            first_predictive_warning_step is None
            and predictive_decision
            == "ESCALATION"
        ):
            first_predictive_warning_step = index

        if (
            first_rule_warning_step is None
            and rule_status
            in {
                "WARNING",
                "HIGH",
                "CRITICAL",
            }
        ):
            first_rule_warning_step = index

        trace_rows.append(
            {
                "step": index,
                "rule_status": rule_status,
                "rule_score": rule_score,
                "predictive_decision": (
                    predictive_decision
                ),
                "predictive_probability": (
                    probability
                ),
                "consensus": (
                    consensus["status"]
                ),
            }
        )

        print("-" * 88)

        print(
            f"STEP {index}"
        )

        print(
            f"Current / Cable Temp : "
            f"{step['current_a']} A / "
            f"{step['cable_temperature_c']} °C"
        )

        print()

        print(
            f"Rule Engine           : "
            f"{rule_status} "
            f"({rule_score}/100)"
        )

        print(
            f"Primary Risk          : "
            f"{primary_risk}"
        )

        print(
            f"Predictive AI         : "
            f"{predictive_decision} "
            f"({probability}%)"
        )

        print(
            f"Anomaly Detector      : "
            f"{anomaly['level']}"
        )

        print(
            f"Consensus             : "
            f"{consensus['status']}"
        )

        print(
            f"Confidence            : "
            f"{consensus['confidence']}"
        )

        print(
            f"Agreement             : "
            f"{consensus['agreement_text']}"
        )

        print()

        time.sleep(0.8)

    print("=" * 88)
    print(
        "EARLY-WARNING TIMING SUMMARY"
    )
    print("=" * 88)

    print(
        f"First predictive ESCALATION : "
        f"{first_predictive_warning_step}"
    )

    print(
        f"First deterministic warning : "
        f"{first_rule_warning_step}"
    )

    print()

    if (
        first_predictive_warning_step is not None
        and first_rule_warning_step is not None
        and first_predictive_warning_step
        < first_rule_warning_step
    ):

        lead = (
            first_rule_warning_step
            - first_predictive_warning_step
        )

        print(
            "RESULT: AI EARLY WARNING CONFIRMED"
        )

        print(
            f"Predictive AI reacted "
            f"{lead} telemetry cycle(s) before "
            f"the deterministic warning."
        )

    elif (
        first_predictive_warning_step is not None
        and first_rule_warning_step is not None
        and first_predictive_warning_step
        == first_rule_warning_step
    ):

        print(
            "RESULT: AI and deterministic warning "
            "appeared at the same telemetry cycle."
        )

    elif (
        first_predictive_warning_step is not None
        and first_rule_warning_step is None
    ):

        print(
            "RESULT: Predictive escalation was detected, "
            "but no deterministic warning occurred "
            "during the observed trace."
        )

    else:

        print(
            "RESULT: No earlier predictive warning "
            "was demonstrated in this scenario."
        )

    print()

    print("-" * 88)
    print(
        "TRACE SUMMARY"
    )
    print("-" * 88)

    for row in trace_rows:

        print(
            f"Step {row['step']} | "
            f"Rule={row['rule_status']} "
            f"{row['rule_score']}/100 | "
            f"AI={row['predictive_decision']} "
            f"{row['predictive_probability']}% | "
            f"Consensus={row['consensus']}"
        )

    print("=" * 88)


if __name__ == "__main__":
    main()