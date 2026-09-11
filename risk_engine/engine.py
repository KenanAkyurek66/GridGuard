from statistics import mean


def _clamp(
    value: float,
    minimum: float,
    maximum: float
) -> float:
    return max(minimum, min(value, maximum))


def _add_cause(
    causes: list[str],
    message: str
) -> None:
    if message not in causes:
        causes.append(message)


def evaluate_risk(history: list[dict]) -> dict:
    """
    GridGuard Explainable Risk Engine.

    Parameters
    ----------
    history:
        One panel's telemetry history ordered from
        oldest -> newest.

    Notes
    -----
    Thresholds in this engine are prototype/demo configuration
    values. They are NOT claimed to be universal electrical
    safety limits.

    In a production deployment, thresholds must be calibrated
    according to asset type, sensor characteristics and site
    engineering requirements.
    """

    # =========================================================
    # NO DATA
    # =========================================================

    if not history:
        return {
            "risk_score": 0,
            "status": "UNKNOWN",
            "primary_risk": "NO_DATA",
            "causes": [
                "No telemetry data available."
            ],
            "component_scores": {
                "current": 0,
                "thermal": 0,
                "environment": 0,
                "partial_discharge": 0
            },
            "metrics": {}
        }

    latest = history[-1]

    current = latest.get("current_a")
    cable_temp = latest.get(
        "cable_temperature_c"
    )
    ambient_temp = latest.get(
        "ambient_temperature_c"
    )
    humidity = latest.get(
        "humidity_pct"
    )
    pd_index = latest.get(
        "pd_index"
    )
    arc_detected = latest.get(
        "arc_detected",
        False
    )

    # =========================================================
    # ARC FLASH
    # =========================================================
    #
    # ARC is treated as a direct safety-critical signal.
    # We do not wait for trend analysis.
    #

    if arc_detected:
        return {
            "risk_score": 100,
            "status": "CRITICAL",
            "primary_risk": "ARC_FLASH",
            "causes": [
                "Arc flash event detected.",
                "Immediate operator attention required."
            ],
            "component_scores": {
                "current": 0,
                "thermal": 0,
                "environment": 0,
                "partial_discharge": 0
            },
            "metrics": {
                "arc_detected": True
            }
        }

    # =========================================================
    # INITIAL SCORES
    # =========================================================

    current_score = 0
    thermal_score = 0
    humidity_score = 0
    pd_score = 0

    causes: list[str] = []

    # Metrics
    current_change_pct = 0.0
    thermal_delta = None
    cable_temp_rise = 0.0
    ambient_temp_rise = 0.0
    pd_change = 0.0

    # =========================================================
    # CURRENT ANALYSIS
    # =========================================================

    valid_previous_currents = [
        item.get("current_a")
        for item in history[:-1]
        if item.get("current_a") is not None
    ]

    if (
        current is not None
        and valid_previous_currents
    ):
        baseline_values = (
            valid_previous_currents[-5:]
        )

        baseline_current = mean(
            baseline_values
        )

        if baseline_current > 0:
            current_change_pct = (
                (current - baseline_current)
                / baseline_current
            ) * 100

            if current_change_pct >= 35:
                current_score = 20

                _add_cause(
                    causes,
                    (
                        "Current increased more than "
                        "35% above recent baseline."
                    )
                )

            elif current_change_pct >= 20:
                current_score = 15

                _add_cause(
                    causes,
                    (
                        "Current increased more than "
                        "20% above recent baseline."
                    )
                )

            elif current_change_pct >= 10:
                current_score = 8

                _add_cause(
                    causes,
                    (
                        "Current is rising above "
                        "recent baseline."
                    )
                )

    # =========================================================
    # THERMAL ANALYSIS
    # =========================================================

    if (
        cable_temp is not None
        and ambient_temp is not None
    ):
        thermal_delta = (
            cable_temp - ambient_temp
        )

        # -----------------------------------------------------
        # Absolute cable temperature
        # -----------------------------------------------------

        if cable_temp >= 80:
            thermal_score += 15

            _add_cause(
                causes,
                "Cable temperature is extremely high."
            )

        elif cable_temp >= 70:
            thermal_score += 12

            _add_cause(
                causes,
                (
                    "Cable temperature is "
                    "critically elevated."
                )
            )

        elif cable_temp >= 60:
            thermal_score += 8

            _add_cause(
                causes,
                "Cable temperature is elevated."
            )

        elif cable_temp >= 50:
            thermal_score += 4

        # -----------------------------------------------------
        # Cable vs ambient temperature difference
        # -----------------------------------------------------

        if thermal_delta >= 40:
            thermal_score += 10

            _add_cause(
                causes,
                (
                    "Cable-to-ambient thermal delta "
                    "is very high."
                )
            )

        elif thermal_delta >= 30:
            thermal_score += 7

            _add_cause(
                causes,
                (
                    "Abnormal cable-to-ambient "
                    "thermal delta detected."
                )
            )

        elif thermal_delta >= 20:
            thermal_score += 4

    # ---------------------------------------------------------
    # Thermal trend
    # ---------------------------------------------------------

    valid_cable_temperatures = [
        item.get("cable_temperature_c")
        for item in history
        if item.get(
            "cable_temperature_c"
        ) is not None
    ]

    valid_ambient_temperatures = [
        item.get("ambient_temperature_c")
        for item in history
        if item.get(
            "ambient_temperature_c"
        ) is not None
    ]

    if len(valid_cable_temperatures) >= 2:
        cable_temp_rise = (
            valid_cable_temperatures[-1]
            - valid_cable_temperatures[0]
        )

    if len(valid_ambient_temperatures) >= 2:
        ambient_temp_rise = (
            valid_ambient_temperatures[-1]
            - valid_ambient_temperatures[0]
        )

    if (
        cable_temp_rise >= 15
        and ambient_temp_rise < 5
    ):
        thermal_score += 10

        _add_cause(
            causes,
            (
                "Cable temperature is rising rapidly "
                "while ambient temperature remains "
                "relatively stable."
            )
        )

    thermal_score = int(
        _clamp(
            thermal_score,
            0,
            30
        )
    )

    # =========================================================
    # HUMIDITY / ENVIRONMENT ANALYSIS
    # =========================================================

    if humidity is not None:

        if humidity >= 85:
            humidity_score = 10

            _add_cause(
                causes,
                "Very high humidity detected."
            )

        elif humidity >= 75:
            humidity_score = 7

            _add_cause(
                causes,
                "High humidity detected."
            )

        elif humidity >= 65:
            humidity_score = 4

    # =========================================================
    # PARTIAL DISCHARGE ANALYSIS
    # =========================================================
    #
    # pd_index is our normalized prototype metric:
    #
    # 0 ------------------------------ 100
    # low activity               high activity
    #
    # It is NOT presented as a calibrated physical PD unit.
    #

    if pd_index is not None:

        if pd_index >= 70:
            pd_score = 20

            _add_cause(
                causes,
                (
                    "Partial discharge activity "
                    "is very high."
                )
            )

        elif pd_index >= 50:
            pd_score = 15

            _add_cause(
                causes,
                (
                    "Elevated partial discharge "
                    "activity detected."
                )
            )

        elif pd_index >= 30:
            pd_score = 8

            _add_cause(
                causes,
                (
                    "Partial discharge activity "
                    "is above normal range."
                )
            )

        elif pd_index >= 20:
            pd_score = 4

    # ---------------------------------------------------------
    # Partial discharge trend
    # ---------------------------------------------------------

    valid_pd_values = [
        item.get("pd_index")
        for item in history
        if item.get("pd_index") is not None
    ]

    if len(valid_pd_values) >= 3:
        pd_change = (
            valid_pd_values[-1]
            - valid_pd_values[0]
        )

        if pd_change >= 25:
            pd_score += 8

            _add_cause(
                causes,
                (
                    "Partial discharge activity "
                    "shows a strong rising trend."
                )
            )

        elif pd_change >= 15:
            pd_score += 5

            _add_cause(
                causes,
                (
                    "Partial discharge activity "
                    "is increasing over time."
                )
            )

    pd_score = int(
        _clamp(
            pd_score,
            0,
            20
        )
    )

    # =========================================================
    # BASE RISK SCORE
    # =========================================================

    risk_score = (
        current_score
        + thermal_score
        + humidity_score
        + pd_score
    )

    risk_score = int(
        _clamp(
            risk_score,
            0,
            100
        )
    )

    # =========================================================
    # SAFETY OVERRIDES
    # =========================================================
    #
    # These values are prototype/demo configuration values.
    # Production thresholds must be calibrated per asset/site.
    #

    # ---------------------------------------------------------
    # Severe thermal escalation
    # ---------------------------------------------------------

    severe_thermal_event = (
        cable_temp is not None
        and thermal_delta is not None
        and cable_temp >= 80
        and thermal_delta >= 40
        and cable_temp_rise >= 20
    )

    if severe_thermal_event:
        risk_score = max(
            risk_score,
            75
        )

        _add_cause(
            causes,
            (
                "Severe thermal escalation "
                "pattern detected."
            )
        )

    # ---------------------------------------------------------
    # Moderate PD escalation
    # ---------------------------------------------------------

    moderate_pd_event = (
        pd_index is not None
        and pd_index >= 40
        and pd_change >= 20
    )

    if moderate_pd_event:
        risk_score = max(
            risk_score,
            20
        )

        _add_cause(
            causes,
            (
                "Rising partial discharge "
                "pattern detected."
            )
        )

    # ---------------------------------------------------------
    # Severe PD escalation
    # ---------------------------------------------------------

    severe_pd_event = (
        pd_index is not None
        and pd_index >= 70
        and pd_change >= 40
    )

    if severe_pd_event:
        risk_score = max(
            risk_score,
            50
        )

        _add_cause(
            causes,
            (
                "Severe partial discharge "
                "escalation pattern detected."
            )
        )

    # =========================================================
    # STATUS CLASSIFICATION
    # =========================================================

    if risk_score >= 75:
        status = "CRITICAL"

    elif risk_score >= 45:
        status = "HIGH"

    elif risk_score >= 20:
        status = "WARNING"

    else:
        status = "NORMAL"

    # =========================================================
    # COMPONENT SCORES
    # =========================================================

    component_scores = {
        "current": current_score,
        "thermal": thermal_score,
        "environment": humidity_score,
        "partial_discharge": pd_score
    }

    # =========================================================
    # PRIMARY RISK
    # =========================================================

    if risk_score == 0:
        primary_risk = "NONE"

    else:
        highest_component_score = max(
            component_scores.values()
        )

        if highest_component_score == 0:
            # A safety override may theoretically raise the
            # final score even when component scores are zero.
            if severe_thermal_event:
                primary_risk = "THERMAL"

            elif (
                moderate_pd_event
                or severe_pd_event
            ):
                primary_risk = "PARTIAL_DISCHARGE"

            else:
                primary_risk = "UNKNOWN"

        else:
            primary_risk = max(
                component_scores,
                key=component_scores.get
            ).upper()

    # =========================================================
    # NORMAL EXPLANATION
    # =========================================================

    if not causes:
        causes.append(
            "No significant anomaly detected."
        )

    # =========================================================
    # RESULT
    # =========================================================

    return {
        "risk_score": risk_score,
        "status": status,
        "primary_risk": primary_risk,
        "causes": causes,
        "component_scores": component_scores,
        "metrics": {
            "current_change_pct": round(
                current_change_pct,
                2
            ),
            "thermal_delta_c": (
                round(
                    thermal_delta,
                    2
                )
                if thermal_delta is not None
                else None
            ),
            "cable_temperature_rise_c": round(
                cable_temp_rise,
                2
            ),
            "ambient_temperature_rise_c": round(
                ambient_temp_rise,
                2
            ),
            "pd_change": round(
                pd_change,
                2
            )
        }
    }