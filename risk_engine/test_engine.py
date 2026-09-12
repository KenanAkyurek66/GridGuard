from risk_engine.engine import evaluate_risk


def point(
    current: float = 300.0,
    cable_temp: float = 44.0,
    ambient_temp: float = 30.0,
    humidity: float = 44.0,
    pd_index: float = 12.0,
    arc_detected: bool = False,
) -> dict:
    return {
        "current_a": current,
        "cable_temperature_c": cable_temp,
        "ambient_temperature_c": ambient_temp,
        "humidity_pct": humidity,
        "pd_index": pd_index,
        "arc_detected": arc_detected,
    }


def run_case(
    name: str,
    history: list[dict],
    expected_score: int,
    expected_status: str,
    expected_primary: str,
) -> None:
    result = evaluate_risk(history)

    print()
    print("=" * 72)
    print(name)
    print("=" * 72)

    print(
        f"Risk Score   : {result['risk_score']}"
    )
    print(
        f"Status       : {result['status']}"
    )
    print(
        f"Primary Risk : {result['primary_risk']}"
    )
    print(
        f"Causes       : {result['causes']}"
    )
    print(
        f"Metrics      : {result['metrics']}"
    )

    assert (
        result["risk_score"]
        == expected_score
    ), (
        f"{name}: expected risk score "
        f"{expected_score}, "
        f"got {result['risk_score']}"
    )

    assert (
        result["status"]
        == expected_status
    ), (
        f"{name}: expected status "
        f"{expected_status}, "
        f"got {result['status']}"
    )

    assert (
        result["primary_risk"]
        == expected_primary
    ), (
        f"{name}: expected primary risk "
        f"{expected_primary}, "
        f"got {result['primary_risk']}"
    )

    print()
    print("[PASS]")


def test_normal() -> None:
    history = [
        point(
            current=300,
            cable_temp=44,
            ambient_temp=30,
            pd_index=12,
        ),
        point(
            current=302,
            cable_temp=44,
            ambient_temp=30,
            pd_index=12,
        ),
        point(
            current=300,
            cable_temp=44,
            ambient_temp=30,
            pd_index=12,
        ),
    ]

    run_case(
        name="NORMAL",
        history=history,
        expected_score=0,
        expected_status="NORMAL",
        expected_primary="NONE",
    )


def test_moderate_overheating() -> None:
    history = [
        point(
            current=300,
            cable_temp=46,
            ambient_temp=32,
        ),
        point(
            current=300,
            cable_temp=50,
            ambient_temp=32,
        ),
        point(
            current=300,
            cable_temp=56,
            ambient_temp=32,
        ),
        point(
            current=300,
            cable_temp=64,
            ambient_temp=32,
        ),
        point(
            current=300,
            cable_temp=70,
            ambient_temp=32,
        ),
        point(
            current=412,
            cable_temp=78,
            ambient_temp=33,
        ),
    ]

    run_case(
        name="MODERATE OVERHEATING",
        history=history,
        expected_score=50,
        expected_status="HIGH",
        expected_primary="THERMAL",
    )


def test_severe_overheating() -> None:
    history = [
        point(
            current=300,
            cable_temp=44,
            ambient_temp=30,
        ),
        point(
            current=320,
            cable_temp=45,
            ambient_temp=31,
        ),
        point(
            current=340,
            cable_temp=48,
            ambient_temp=31,
        ),
        point(
            current=370,
            cable_temp=54,
            ambient_temp=31,
        ),
        point(
            current=400,
            cable_temp=60,
            ambient_temp=31,
        ),
        point(
            current=435,
            cable_temp=68,
            ambient_temp=31,
        ),
        point(
            current=470,
            cable_temp=76,
            ambient_temp=31,
        ),
        point(
            current=500,
            cable_temp=82,
            ambient_temp=32,
        ),
    ]

    run_case(
        name="SEVERE OVERHEATING",
        history=history,
        expected_score=75,
        expected_status="CRITICAL",
        expected_primary="THERMAL",
    )


def test_pd_degradation() -> None:
    history = [
        point(
            pd_index=11,
        ),
        point(
            pd_index=20,
        ),
        point(
            pd_index=31,
        ),
        point(
            pd_index=45,
        ),
        point(
            pd_index=60,
        ),
    ]

    run_case(
        name="PD DEGRADATION",
        history=history,
        expected_score=20,
        expected_status="WARNING",
        expected_primary="PARTIAL_DISCHARGE",
    )


def test_severe_pd() -> None:
    history = [
        point(
            pd_index=10,
        ),
        point(
            pd_index=24,
        ),
        point(
            pd_index=38,
        ),
        point(
            pd_index=55,
        ),
        point(
            pd_index=72,
        ),
    ]

    run_case(
        name="SEVERE PD ESCALATION",
        history=history,
        expected_score=50,
        expected_status="HIGH",
        expected_primary="PARTIAL_DISCHARGE",
    )


def test_arc_flash() -> None:
    history = [
        point(),
        point(
            arc_detected=True,
        ),
    ]

    run_case(
        name="ARC FLASH",
        history=history,
        expected_score=100,
        expected_status="CRITICAL",
        expected_primary="ARC_FLASH",
    )


def main() -> None:
    print()
    print("=" * 72)
    print(" GRIDGUARD CORE RISK ENGINE REGRESSION TESTS")
    print("=" * 72)

    test_normal()
    test_moderate_overheating()
    test_severe_overheating()
    test_pd_degradation()
    test_severe_pd()
    test_arc_flash()

    print()
    print("=" * 72)
    print(" ALL CORE RISK ENGINE TESTS PASSED")
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()