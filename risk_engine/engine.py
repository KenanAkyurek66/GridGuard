from statistics import mean


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def evaluate_risk(history: list[dict]) -> dict:
    """
    Evaluate recent telemetry history for one panel.

    History must be ordered from oldest -> newest.
    """

    if not history:
        return {
            "risk_score": 0,
            "status": "UNKNOWN",
            "primary_risk": "NO_DATA",
            "causes": ["No telemetry data available."],
            "metrics": {}
        }

    latest = history[-1]

    current = latest.get("current_a")
    cable_temp = latest.get("cable_temperature_c")
    ambient_temp = latest.get("ambient_temperature_c")
    humidity = latest.get("humidity_pct")
    pd_index = latest.get("pd_index")
    arc_detected = latest.get("arc_detected", False)

    # ---------------------------------------------------------
    # ARC FLASH
    # Safety-critical event: immediate critical alarm.
    # ---------------------------------------------------------

    if arc_detected:
        return {
            "risk_score": 100,
            "status": "CRITICAL",
            "primary_risk": "ARC_FLASH",
            "causes": [
                "Arc flash event detected.",
                "Immediate operator attention required."
            ],
            "metrics": {
                "arc_detected": True
            }
        }

    current_score = 0
    thermal_score = 0
    humidity_score = 0
    pd_score = 0

    causes = []

    # ---------------------------------------------------------
    # CURRENT ANALYSIS
    # ---------------------------------------------------------

    valid_currents = [
        item.get("current_a")
        for item in history[:-1]
        if item.get("current_a") is not None
    ]

    current_change_pct = 0.0

    if current is not None and valid_currents:
        baseline_current = mean(valid_currents[-5:])

        if baseline_current > 0:
            current_change_pct = (
                (current - baseline_current)
                / baseline_current
            ) * 100

            if current_change_pct >= 35:
                current_score = 20
                causes.append(
                    "Current increased more than 35% above recent baseline."
                )

            elif current_change_pct >= 20:
                current_score = 15
                causes.append(
                    "Current increased more than 20% above recent baseline."
                )

            elif current_change_pct >= 10:
                current_score = 8
                causes.append(
                    "Current is rising above recent baseline."
                )

    # ---------------------------------------------------------
    # THERMAL ANALYSIS
    # ---------------------------------------------------------

    thermal_delta = None

    if cable_temp is not None and ambient_temp is not None:
        thermal_delta = cable_temp - ambient_temp

        # Absolute cable temperature component
        if cable_temp >= 80:
            thermal_score += 15
            causes.append(
                "Cable temperature is extremely high."
            )

        elif cable_temp >= 70:
            thermal_score += 12
            causes.append(
                "Cable temperature is critically elevated."
            )

        elif cable_temp >= 60:
            thermal_score += 8
            causes.append(
                "Cable temperature is elevated."
            )

        elif cable_temp >= 50:
            thermal_score += 4

        # Cable vs ambient difference
        if thermal_delta >= 40:
            thermal_score += 10
            causes.append(
                "Cable-to-ambient thermal delta is very high."
            )

        elif thermal_delta >= 30:
            thermal_score += 7
            causes.append(
                "Abnormal cable-to-ambient thermal delta detected."
            )

        elif thermal_delta >= 20:
            thermal_score += 4

    # Temperature trend
    valid_cable_temps = [
        item.get("cable_temperature_c")
        for item in history
        if item.get("cable_temperature_c") is not None
    ]

    valid_ambient_temps = [
        item.get("ambient_temperature_c")
        for item in history
        if item.get("ambient_temperature_c") is not None
    ]

    cable_temp_rise = 0.0
    ambient_temp_rise = 0.0

    if len(valid_cable_temps) >= 2:
        cable_temp_rise = (
            valid_cable_temps[-1] - valid_cable_temps[0]
        )

    if len(valid_ambient_temps) >= 2:
        ambient_temp_rise = (
            valid_ambient_temps[-1] - valid_ambient_temps[0]
        )

    if (
        cable_temp_rise >= 15
        and ambient_temp_rise < 5
    ):
        thermal_score += 10
        causes.append(
            "Cable temperature is rising rapidly while ambient "
            "temperature remains relatively stable."
        )

    thermal_score = int(
        _clamp(thermal_score, 0, 30)
    )

    # ---------------------------------------------------------
    # HUMIDITY / ENVIRONMENT
    # ---------------------------------------------------------

    if humidity is not None:
        if humidity >= 85:
            humidity_score = 10
            causes.append(
                "Very high humidity detected."
            )

        elif humidity >= 75:
            humidity_score = 7
            causes.append(
                "High humidity detected."
            )

        elif humidity >= 65:
            humidity_score = 4

    # ---------------------------------------------------------
    # PARTIAL DISCHARGE
    # pd_index is a normalized demonstration metric (0-100).
    # ---------------------------------------------------------

    if pd_index is not None:
        if pd_index >= 70:
            pd_score = 20
            causes.append(
                "Partial discharge activity is very high."
            )

        elif pd_index >= 50:
            pd_score = 15
            causes.append(
                "Elevated partial discharge activity detected."
            )

        elif pd_index >= 30:
            pd_score = 8
            causes.append(
                "Partial discharge activity is above normal range."
            )

        elif pd_index >= 20:
            pd_score = 4

    valid_pd_values = [
        item.get("pd_index")
        for item in history
        if item.get("pd_index") is not None
    ]

    pd_change = 0.0

    if len(valid_pd_values) >= 3:
        pd_change = (
            valid_pd_values[-1] - valid_pd_values[0]
        )

        if pd_change >= 25:
            pd_score += 8
            causes.append(
                "Partial discharge activity shows a strong rising trend."
            )

        elif pd_change >= 15:
            pd_score += 5
            causes.append(
                "Partial discharge activity is increasing over time."
            )

    pd_score = int(
        _clamp(pd_score, 0, 20)
    )

    # ---------------------------------------------------------
    # FINAL SCORE
    # ---------------------------------------------------------

    risk_score = (
        current_score
        + thermal_score
        + humidity_score
        + pd_score
    )

    risk_score = int(
        _clamp(risk_score, 0, 100)
    )

    # ---------------------------------------------------------
    # SAFETY OVERRIDES
    # ---------------------------------------------------------
    # These thresholds are prototype/demo configuration values.
    # In production they must be calibrated per asset and site.

    severe_thermal_event = (
        cable_temp is not None
        and thermal_delta is not None
        and cable_temp >= 80
        and thermal_delta >= 40
        and cable_temp_rise >= 20
    )

    if severe_thermal_event:
        risk_score = max(risk_score, 75)

        if "Severe thermal escalation pattern detected." not in causes:
            causes.append(
                "Severe thermal escalation pattern detected."
            )

    if risk_score >= 75:
        status = "CRITICAL"

    elif risk_score >= 45:
        status = "HIGH"

    elif risk_score >= 20:
        status = "WARNING"

    else:
        status = "NORMAL"

    component_scores = {
        "current": current_score,
        "thermal": thermal_score,
        "environment": humidity_score,
        "partial_discharge": pd_score
    }

    if risk_score == 0:
        primary_risk = "NONE"
    else:
        primary_risk = max(
            component_scores,
            key=component_scores.get
        )

    if not causes:
        causes.append(
            "No significant anomaly detected."
        )

    return {
        "risk_score": risk_score,
        "status": status,
        "primary_risk": primary_risk.upper(),
        "causes": causes,
        "component_scores": component_scores,
        "metrics": {
            "current_change_pct": round(
                current_change_pct, 2
            ),
            "thermal_delta_c": (
                round(thermal_delta, 2)
                if thermal_delta is not None
                else None
            ),
            "cable_temperature_rise_c": round(
                cable_temp_rise, 2
            ),
            "ambient_temperature_rise_c": round(
                ambient_temp_rise, 2
            ),
            "pd_change": round(
                pd_change, 2
            )
        }
    }