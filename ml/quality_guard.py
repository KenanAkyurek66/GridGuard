from __future__ import annotations

from dataclasses import asdict, dataclass


# ============================================================
# GRIDGUARD AI - DATA QUALITY & PERSISTENCE GUARD
# ============================================================
#
# Purpose
# -------
# Prevent the predictive ML layer from blindly acting on a
# single unreliable or transient telemetry sample.
#
# This guard does NOT replace the deterministic GridGuard
# safety / risk engine.
#
# Safety-critical signals such as confirmed arc detection are
# handled outside this predictive ML advisory layer.
#
# ============================================================


DECISION_SAFE = "SAFE"
DECISION_HOLD = "HOLD"
DECISION_ESCALATION = "ESCALATION"


@dataclass
class GuardDecision:
    decision: str

    latest_probability: float
    threshold: float

    consecutive_high_predictions: int

    data_reliable: bool

    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


def _normalize_quality(
    value: str | None,
) -> str:

    if value is None:
        return "UNKNOWN"

    return str(
        value
    ).strip().upper()


def _count_consecutive_high(
    probabilities: list[float],
    threshold: float,
) -> int:

    count = 0

    for probability in reversed(
        probabilities
    ):

        if probability >= threshold:
            count += 1

        else:
            break

    return count


def evaluate_quality_guard(
    recent_probabilities: list[float],
    recent_data_quality: list[str],
    threshold: float,
    consecutive_required: int = 2,
    strong_confidence_margin: float = 0.20,
) -> GuardDecision:
    """
    Convert raw predictive probabilities into a safer
    operational advisory decision.

    Decision rules
    --------------

    1. Latest / recent telemetry quality is unreliable:
       HOLD

    2. Latest probability is below threshold:
       SAFE

    3. At least N consecutive predictions exceed threshold:
       ESCALATION

    4. Very strong prediction exceeds threshold by a
       confidence margin:
       ESCALATION

    5. Otherwise:
       HOLD and wait for confirmation.

    Notes
    -----
    HOLD means:

        "The model sees something concerning, but GridGuard
        wants more trustworthy / persistent evidence before
        presenting an escalation advisory."

    It does NOT mean that the electrical system is safe.
    """

    if not recent_probabilities:

        raise ValueError(
            "recent_probabilities cannot be empty."
        )

    if not recent_data_quality:

        raise ValueError(
            "recent_data_quality cannot be empty."
        )

    if (
        len(recent_probabilities)
        != len(recent_data_quality)
    ):

        raise ValueError(
            (
                "recent_probabilities and "
                "recent_data_quality must have "
                "the same length."
            )
        )

    latest_probability = float(
        recent_probabilities[-1]
    )

    normalized_quality = [
        _normalize_quality(
            value
        )
        for value
        in recent_data_quality
    ]

    # ========================================================
    # DATA QUALITY CHECK
    # ========================================================
    #
    # Inspect the two most recent samples.
    #
    # A recent suspect sample should not immediately generate
    # an ML escalation advisory.
    #
    # ========================================================

    quality_window = (
        normalized_quality[-2:]
    )

    data_reliable = all(
        quality == "GOOD"
        for quality
        in quality_window
    )

    if not data_reliable:

        return GuardDecision(
            decision=DECISION_HOLD,

            latest_probability=latest_probability,

            threshold=threshold,

            consecutive_high_predictions=0,

            data_reliable=False,

            reason=(
                "Recent telemetry quality is not fully "
                "reliable. Predictive escalation is withheld "
                "until trustworthy samples confirm the trend."
            ),
        )

    # ========================================================
    # BELOW THRESHOLD
    # ========================================================

    if latest_probability < threshold:

        return GuardDecision(
            decision=DECISION_SAFE,

            latest_probability=latest_probability,

            threshold=threshold,

            consecutive_high_predictions=0,

            data_reliable=True,

            reason=(
                "Predictive escalation probability is below "
                "the configured advisory threshold."
            ),
        )

    # ========================================================
    # PERSISTENCE CHECK
    # ========================================================

    consecutive_high = (
        _count_consecutive_high(
            probabilities=recent_probabilities,
            threshold=threshold,
        )
    )

    if (
        consecutive_high
        >= consecutive_required
    ):

        return GuardDecision(
            decision=DECISION_ESCALATION,

            latest_probability=latest_probability,

            threshold=threshold,

            consecutive_high_predictions=consecutive_high,

            data_reliable=True,

            reason=(
                "Predictive risk remained above threshold "
                "across consecutive trustworthy telemetry "
                "samples."
            ),
        )

    # ========================================================
    # STRONG CONFIDENCE OVERRIDE
    # ========================================================
    #
    # A rapidly developing real event should not always need
    # multiple cycles before an advisory appears.
    #
    # This override only applies to GOOD telemetry.
    #
    # ========================================================

    strong_threshold = min(
        1.0,
        threshold
        + strong_confidence_margin,
    )

    if (
        latest_probability
        >= strong_threshold
    ):

        return GuardDecision(
            decision=DECISION_ESCALATION,

            latest_probability=latest_probability,

            threshold=threshold,

            consecutive_high_predictions=consecutive_high,

            data_reliable=True,

            reason=(
                "Predictive escalation probability is "
                "strongly above threshold on trustworthy "
                "telemetry."
            ),
        )

    # ========================================================
    # WAIT FOR CONFIRMATION
    # ========================================================

    return GuardDecision(
        decision=DECISION_HOLD,

        latest_probability=latest_probability,

        threshold=threshold,

        consecutive_high_predictions=consecutive_high,

        data_reliable=True,

        reason=(
            "Predictive probability exceeded threshold, "
            "but persistence has not yet been confirmed."
        ),
    )