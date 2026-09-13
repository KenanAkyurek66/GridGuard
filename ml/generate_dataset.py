from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


# ============================================================
# GRIDGUARD AI - SYNTHETIC TELEMETRY DATASET GENERATOR
# ============================================================
#
# Purpose
# -------
# Generate many independent synthetic panel-operation scenarios
# for training and validating GridGuard predictive ML models.
#
# IMPORTANT
# ---------
# This dataset is synthetic prototype data.
#
# It must NOT be presented as real utility field data.
# Production deployment requires calibration / retraining using
# validated historical operational data.
#
# ============================================================


RANDOM_SEED = 42

SCENARIO_COUNT = 3000

MIN_STEPS = 36
MAX_STEPS = 50

PREDICTION_HORIZON = 5


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "ml" / "data"
REPORT_DIR = PROJECT_ROOT / "ml" / "reports"

DATASET_PATH = DATA_DIR / "gridguard_synthetic_telemetry.csv"
SUMMARY_PATH = REPORT_DIR / "dataset_summary.json"


SCENARIO_TYPES = [
    "NORMAL",
    "NORMAL_WITH_NOISE",
    "GRADUAL_OVERLOAD",
    "RAPID_OVERLOAD",
    "THERMAL_DEGRADATION",
    "LOAD_DRIVEN_OVERHEATING",
    "AMBIENT_HEATING",
    "HIGH_HUMIDITY",
    "GRADUAL_PD",
    "RAPID_PD",
    "THERMAL_PD",
    "CURRENT_THERMAL",
    "HUMIDITY_PD",
    "SENSOR_OUTLIER",
    "RECOVERY",
]


# Higher weight means that scenario is generated more often.
SCENARIO_WEIGHTS = {
    "NORMAL": 18,
    "NORMAL_WITH_NOISE": 12,
    "GRADUAL_OVERLOAD": 8,
    "RAPID_OVERLOAD": 6,
    "THERMAL_DEGRADATION": 8,
    "LOAD_DRIVEN_OVERHEATING": 9,
    "AMBIENT_HEATING": 6,
    "HIGH_HUMIDITY": 5,
    "GRADUAL_PD": 7,
    "RAPID_PD": 6,
    "THERMAL_PD": 5,
    "CURRENT_THERMAL": 6,
    "HUMIDITY_PD": 4,
    "SENSOR_OUTLIER": 4,
    "RECOVERY": 6,
}


# ============================================================
# DATA STRUCTURE
# ============================================================


@dataclass
class TelemetryPoint:
    scenario_id: str
    scenario_type: str
    timestep: int

    current_a: float
    cable_temperature_c: float
    ambient_temperature_c: float
    humidity_pct: float
    pd_index: float

    arc_detected: bool
    data_quality: str

    # Internal synthetic ground-truth severity.
    #
    # 0 = NORMAL
    # 1 = EARLY DETERIORATION
    # 2 = HIGH
    # 3 = CRITICAL
    #
    # This value is used only for generating the future target.
    # It will NOT later be used as an ML feature.
    latent_severity: int

    future_escalation: int = 0


# ============================================================
# HELPERS
# ============================================================


def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    return max(
        minimum,
        min(value, maximum),
    )


def noisy(
    value: float,
    sigma: float,
) -> float:
    return value + random.gauss(0, sigma)


def smooth_progress(
    timestep: int,
    start_step: int,
    end_step: int,
) -> float:
    """
    Return a smooth 0..1 progression between start and end.
    """

    if timestep <= start_step:
        return 0.0

    if timestep >= end_step:
        return 1.0

    x = (
        (timestep - start_step)
        / (end_step - start_step)
    )

    # Smoothstep:
    # 3x^2 - 2x^3
    return (
        3 * x * x
        - 2 * x * x * x
    )


def severity_from_conditions(
    current_a: float,
    cable_temp: float,
    ambient_temp: float,
    humidity: float,
    pd_index: float,
    arc_detected: bool,
) -> int:
    """
    Synthetic ground-truth severity function.

    This is NOT an electrical protection standard.

    It is only used to build prototype training labels.
    """

    if arc_detected:
        return 3

    thermal_delta = (
        cable_temp
        - ambient_temp
    )

    # CRITICAL synthetic state
    if (
        cable_temp >= 80
        and thermal_delta >= 38
    ):
        return 3

    if (
        current_a >= 500
        and cable_temp >= 75
    ):
        return 3

    if (
        pd_index >= 85
    ):
        return 3

    # HIGH synthetic state
    if (
        cable_temp >= 70
        and thermal_delta >= 30
    ):
        return 2

    if (
        current_a >= 460
        and cable_temp >= 65
    ):
        return 2

    if (
        pd_index >= 70
    ):
        return 2

    # EARLY deterioration
    if (
        cable_temp >= 55
        or current_a >= 390
        or pd_index >= 45
        or humidity >= 82
    ):
        return 1

    return 0


# ============================================================
# BASELINE GENERATOR
# ============================================================


def make_baseline() -> dict:
    """
    Generate a slightly different healthy operating baseline
    for every scenario.
    """

    ambient = random.uniform(
        24.0,
        34.0,
    )

    return {
        "current": random.uniform(
            230.0,
            340.0,
        ),
        "ambient": ambient,
        "cable": ambient
        + random.uniform(
            8.0,
            17.0,
        ),
        "humidity": random.uniform(
            32.0,
            58.0,
        ),
        "pd": random.uniform(
            4.0,
            18.0,
        ),
    }


# ============================================================
# SCENARIO GENERATOR
# ============================================================


def generate_scenario(
    scenario_id: str,
    scenario_type: str,
    step_count: int,
) -> list[TelemetryPoint]:

    baseline = make_baseline()

    event_start = random.randint(
        9,
        max(
            10,
            int(step_count * 0.40),
        ),
    )

    event_end = random.randint(
        max(
            event_start + 8,
            int(step_count * 0.72),
        ),
        step_count - 1,
    )

    points: list[TelemetryPoint] = []

    for timestep in range(step_count):

        progress = smooth_progress(
            timestep,
            event_start,
            event_end,
        )

        current = baseline["current"]
        cable_temp = baseline["cable"]
        ambient_temp = baseline["ambient"]
        humidity = baseline["humidity"]
        pd_index = baseline["pd"]

        arc_detected = False
        data_quality = "GOOD"

        # ====================================================
        # NORMAL
        # ====================================================

        if scenario_type == "NORMAL":

            current += random.gauss(
                0,
                7,
            )

            cable_temp += random.gauss(
                0,
                0.7,
            )

            ambient_temp += random.gauss(
                0,
                0.4,
            )

            humidity += random.gauss(
                0,
                1.2,
            )

            pd_index += random.gauss(
                0,
                1.2,
            )

        # ====================================================
        # NORMAL WITH NOISE
        # ====================================================

        elif (
            scenario_type
            == "NORMAL_WITH_NOISE"
        ):

            current += random.gauss(
                0,
                18,
            )

            cable_temp += random.gauss(
                0,
                1.7,
            )

            ambient_temp += random.gauss(
                0,
                1.0,
            )

            humidity += random.gauss(
                0,
                3.0,
            )

            pd_index += random.gauss(
                0,
                3.5,
            )

        # ====================================================
        # GRADUAL OVERLOAD
        # ====================================================

        elif (
            scenario_type
            == "GRADUAL_OVERLOAD"
        ):

            target_current = random.uniform(
                430,
                490,
            )

            current += (
                target_current
                - baseline["current"]
            ) * progress

            cable_temp += (
                random.uniform(
                    10,
                    22,
                )
                * progress
            )

        # ====================================================
        # RAPID OVERLOAD
        # ====================================================

        elif (
            scenario_type
            == "RAPID_OVERLOAD"
        ):

            rapid_progress = smooth_progress(
                timestep,
                event_start,
                min(
                    event_start + 8,
                    step_count - 1,
                ),
            )

            target_current = random.uniform(
                480,
                550,
            )

            current += (
                target_current
                - baseline["current"]
            ) * rapid_progress

            cable_temp += (
                random.uniform(
                    15,
                    28,
                )
                * rapid_progress
            )

        # ====================================================
        # THERMAL DEGRADATION
        # ====================================================

        elif (
            scenario_type
            == "THERMAL_DEGRADATION"
        ):

            cable_temp += (
                random.uniform(
                    28,
                    48,
                )
                * progress
            )

            current += (
                random.uniform(
                    15,
                    45,
                )
                * progress
            )

        # ====================================================
        # LOAD DRIVEN OVERHEATING
        # ====================================================

        elif (
            scenario_type
            == "LOAD_DRIVEN_OVERHEATING"
        ):

            target_current = random.uniform(
                470,
                535,
            )

            current += (
                target_current
                - baseline["current"]
            ) * progress

            cable_temp += (
                random.uniform(
                    32,
                    48,
                )
                * progress
            )

            ambient_temp += (
                random.uniform(
                    0,
                    3,
                )
                * progress
            )

        # ====================================================
        # AMBIENT HEATING
        # ====================================================

        elif (
            scenario_type
            == "AMBIENT_HEATING"
        ):

            ambient_rise = (
                random.uniform(
                    12,
                    22,
                )
                * progress
            )

            ambient_temp += ambient_rise

            cable_temp += (
                ambient_rise
                + random.uniform(
                    1,
                    6,
                )
                * progress
            )

        # ====================================================
        # HIGH HUMIDITY
        # ====================================================

        elif (
            scenario_type
            == "HIGH_HUMIDITY"
        ):

            target_humidity = random.uniform(
                82,
                96,
            )

            humidity += (
                target_humidity
                - baseline["humidity"]
            ) * progress

        # ====================================================
        # GRADUAL PD
        # ====================================================

        elif (
            scenario_type
            == "GRADUAL_PD"
        ):

            target_pd = random.uniform(
                55,
                78,
            )

            pd_index += (
                target_pd
                - baseline["pd"]
            ) * progress

        # ====================================================
        # RAPID PD
        # ====================================================

        elif (
            scenario_type
            == "RAPID_PD"
        ):

            pd_progress = smooth_progress(
                timestep,
                event_start,
                min(
                    event_start + 9,
                    step_count - 1,
                ),
            )

            target_pd = random.uniform(
                75,
                96,
            )

            pd_index += (
                target_pd
                - baseline["pd"]
            ) * pd_progress

        # ====================================================
        # THERMAL + PD
        # ====================================================

        elif (
            scenario_type
            == "THERMAL_PD"
        ):

            cable_temp += (
                random.uniform(
                    25,
                    43,
                )
                * progress
            )

            pd_index += (
                random.uniform(
                    45,
                    78,
                )
                * progress
            )

            current += (
                random.uniform(
                    20,
                    65,
                )
                * progress
            )

        # ====================================================
        # CURRENT + THERMAL
        # ====================================================

        elif (
            scenario_type
            == "CURRENT_THERMAL"
        ):

            target_current = random.uniform(
                450,
                525,
            )

            current += (
                target_current
                - baseline["current"]
            ) * progress

            cable_temp += (
                random.uniform(
                    25,
                    45,
                )
                * progress
            )

        # ====================================================
        # HUMIDITY + PD
        # ====================================================

        elif (
            scenario_type
            == "HUMIDITY_PD"
        ):

            humidity += (
                random.uniform(
                    28,
                    48,
                )
                * progress
            )

            pd_index += (
                random.uniform(
                    38,
                    72,
                )
                * progress
            )

        # ====================================================
        # SENSOR OUTLIER
        # ====================================================

        elif (
            scenario_type
            == "SENSOR_OUTLIER"
        ):

            if (
                event_start
                <= timestep
                <= event_start + 1
            ):

                outlier_type = random.choice(
                    [
                        "CURRENT",
                        "TEMPERATURE",
                        "PD",
                    ]
                )

                if (
                    outlier_type
                    == "CURRENT"
                ):
                    current += random.uniform(
                        100,
                        180,
                    )

                elif (
                    outlier_type
                    == "TEMPERATURE"
                ):
                    cable_temp += random.uniform(
                        15,
                        30,
                    )

                else:
                    pd_index += random.uniform(
                        30,
                        55,
                    )

                data_quality = "SUSPECT"

        # ====================================================
        # RECOVERY
        # ====================================================

        elif (
            scenario_type
            == "RECOVERY"
        ):

            peak_step = int(
                step_count * 0.55
            )

            if timestep <= peak_step:

                rise_progress = smooth_progress(
                    timestep,
                    event_start,
                    peak_step,
                )

                current += (
                    random.uniform(
                        130,
                        200,
                    )
                    * rise_progress
                )

                cable_temp += (
                    random.uniform(
                        28,
                        42,
                    )
                    * rise_progress
                )

                pd_index += (
                    random.uniform(
                        15,
                        35,
                    )
                    * rise_progress
                )

            else:

                recovery_progress = (
                    (
                        timestep
                        - peak_step
                    )
                    /
                    max(
                        1,
                        step_count
                        - peak_step
                        - 1,
                    )
                )

                remaining = (
                    1.0
                    - recovery_progress
                )

                current += (
                    random.uniform(
                        130,
                        200,
                    )
                    * remaining
                )

                cable_temp += (
                    random.uniform(
                        28,
                        42,
                    )
                    * remaining
                )

                pd_index += (
                    random.uniform(
                        15,
                        35,
                    )
                    * remaining
                )

        # ====================================================
        # SMALL MEASUREMENT NOISE FOR ALL SCENARIOS
        # ====================================================

        current = noisy(
            current,
            3.5,
        )

        cable_temp = noisy(
            cable_temp,
            0.45,
        )

        ambient_temp = noisy(
            ambient_temp,
            0.25,
        )

        humidity = noisy(
            humidity,
            0.8,
        )

        pd_index = noisy(
            pd_index,
            1.0,
        )

        # ====================================================
        # LIMITS
        # ====================================================

        current = clamp(
            current,
            0,
            650,
        )

        cable_temp = clamp(
            cable_temp,
            -20,
            120,
        )

        ambient_temp = clamp(
            ambient_temp,
            -20,
            70,
        )

        humidity = clamp(
            humidity,
            0,
            100,
        )

        pd_index = clamp(
            pd_index,
            0,
            100,
        )

        # ====================================================
        # LATENT SEVERITY
        # ====================================================

        severity = severity_from_conditions(
            current_a=current,
            cable_temp=cable_temp,
            ambient_temp=ambient_temp,
            humidity=humidity,
            pd_index=pd_index,
            arc_detected=arc_detected,
        )

        point = TelemetryPoint(
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            timestep=timestep,
            current_a=round(
                current,
                3,
            ),
            cable_temperature_c=round(
                cable_temp,
                3,
            ),
            ambient_temperature_c=round(
                ambient_temp,
                3,
            ),
            humidity_pct=round(
                humidity,
                3,
            ),
            pd_index=round(
                pd_index,
                3,
            ),
            arc_detected=arc_detected,
            data_quality=data_quality,
            latent_severity=severity,
        )

        points.append(point)

    assign_future_escalation_labels(
        points
    )

    return points


# ============================================================
# FUTURE TARGET
# ============================================================


def assign_future_escalation_labels(
    points: list[TelemetryPoint],
) -> None:
    """
    future_escalation = 1

    when the panel is not already HIGH/CRITICAL,
    but becomes HIGH/CRITICAL within the next
    PREDICTION_HORIZON telemetry points.
    """

    for index, point in enumerate(points):

        # Already severe:
        # not useful as an early-warning training row.
        if point.latent_severity >= 2:
            point.future_escalation = 0
            continue

        future_end = min(
            len(points),
            index
            + PREDICTION_HORIZON
            + 1,
        )

        future_window = points[
            index + 1:
            future_end
        ]

        point.future_escalation = int(
            any(
                future_point.latent_severity
                >= 2
                for future_point
                in future_window
            )
        )


# ============================================================
# DATASET CREATION
# ============================================================


def choose_scenario_type() -> str:

    types = list(
        SCENARIO_WEIGHTS.keys()
    )

    weights = [
        SCENARIO_WEIGHTS[
            scenario_type
        ]
        for scenario_type
        in types
    ]

    return random.choices(
        types,
        weights=weights,
        k=1,
    )[0]


def generate_dataset() -> list[TelemetryPoint]:

    all_points: list[
        TelemetryPoint
    ] = []

    for scenario_number in range(
        1,
        SCENARIO_COUNT + 1,
    ):

        scenario_type = (
            choose_scenario_type()
        )

        step_count = random.randint(
            MIN_STEPS,
            MAX_STEPS,
        )

        scenario_id = (
            f"SCN-{scenario_number:05d}"
        )

        points = generate_scenario(
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            step_count=step_count,
        )

        all_points.extend(
            points
        )

    return all_points


# ============================================================
# CSV
# ============================================================


def write_dataset(
    points: list[TelemetryPoint],
) -> None:

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "scenario_id",
        "scenario_type",
        "timestep",
        "current_a",
        "cable_temperature_c",
        "ambient_temperature_c",
        "humidity_pct",
        "pd_index",
        "arc_detected",
        "data_quality",
        "latent_severity",
        "future_escalation",
    ]

    with DATASET_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for point in points:

            writer.writerow(
                {
                    "scenario_id":
                        point.scenario_id,

                    "scenario_type":
                        point.scenario_type,

                    "timestep":
                        point.timestep,

                    "current_a":
                        point.current_a,

                    "cable_temperature_c":
                        point.cable_temperature_c,

                    "ambient_temperature_c":
                        point.ambient_temperature_c,

                    "humidity_pct":
                        point.humidity_pct,

                    "pd_index":
                        point.pd_index,

                    "arc_detected":
                        int(
                            point.arc_detected
                        ),

                    "data_quality":
                        point.data_quality,

                    "latent_severity":
                        point.latent_severity,

                    "future_escalation":
                        point.future_escalation,
                }
            )


# ============================================================
# SUMMARY
# ============================================================


def write_summary(
    points: list[TelemetryPoint],
) -> dict:

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    scenario_ids = {
        point.scenario_id
        for point in points
    }

    scenario_types = Counter()

    seen_scenarios = set()

    for point in points:

        if (
            point.scenario_id
            not in seen_scenarios
        ):

            scenario_types[
                point.scenario_type
            ] += 1

            seen_scenarios.add(
                point.scenario_id
            )

    escalation_rows = sum(
        point.future_escalation
        for point in points
    )

    eligible_rows = sum(
        1
        for point in points
        if point.latent_severity < 2
    )

    high_critical_rows = sum(
        1
        for point in points
        if point.latent_severity >= 2
    )

    summary = {
        "random_seed":
            RANDOM_SEED,

        "scenario_count":
            len(scenario_ids),

        "telemetry_rows":
            len(points),

        "prediction_horizon":
            PREDICTION_HORIZON,

        "early_warning_eligible_rows":
            eligible_rows,

        "positive_future_escalation_rows":
            escalation_rows,

        "positive_rate_pct":
            round(
                (
                    escalation_rows
                    / eligible_rows
                    * 100
                )
                if eligible_rows
                else 0,
                2,
            ),

        "high_or_critical_rows":
            high_critical_rows,

        "scenario_distribution":
            dict(
                sorted(
                    scenario_types.items()
                )
            ),

        "dataset_path":
            str(
                DATASET_PATH
            ),

        "important_note":
            (
                "Synthetic prototype dataset. "
                "Not validated utility field data."
            ),
    }

    with SUMMARY_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return summary


# ============================================================
# MAIN
# ============================================================


def main() -> None:

    random.seed(
        RANDOM_SEED
    )

    print(
        "=" * 70
    )

    print(
        "GRIDGUARD AI - SYNTHETIC DATASET GENERATOR"
    )

    print(
        "=" * 70
    )

    print(
        f"Scenarios to generate : {SCENARIO_COUNT}"
    )

    print(
        f"Prediction horizon     : {PREDICTION_HORIZON}"
    )

    print()

    points = generate_dataset()

    write_dataset(
        points
    )

    summary = write_summary(
        points
    )

    print(
        f"Telemetry rows         : "
        f"{summary['telemetry_rows']}"
    )

    print(
        f"Eligible warning rows  : "
        f"{summary['early_warning_eligible_rows']}"
    )

    print(
        f"Future escalation rows : "
        f"{summary['positive_future_escalation_rows']}"
    )

    print(
        f"Positive rate          : "
        f"{summary['positive_rate_pct']}%"
    )

    print()

    print(
        "Scenario distribution:"
    )

    for (
        scenario_type,
        count,
    ) in summary[
        "scenario_distribution"
    ].items():

        print(
            f"  {scenario_type:<28} "
            f"{count}"
        )

    print()

    print(
        f"Dataset saved to:"
    )

    print(
        f"  {DATASET_PATH}"
    )

    print()

    print(
        f"Summary saved to:"
    )

    print(
        f"  {SUMMARY_PATH}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "This dataset is synthetic prototype data."
    )

    print(
        "It is not real utility field data."
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()