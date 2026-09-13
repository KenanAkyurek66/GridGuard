from __future__ import annotations

from dataclasses import asdict, dataclass


# ============================================================
# GRIDGUARD AI - CONSENSUS ENGINE
# ============================================================
#
# Purpose
# -------
# Combine independent evidence from:
#
#   1. Deterministic Rule Engine
#   2. Predictive ML + Quality Guard
#   3. Unsupervised Anomaly Detector
#
# This layer does NOT replace electrical protection logic.
#
# It produces an operator-facing advisory interpretation.
#
# ============================================================


CONSENSUS_NORMAL = "NORMAL"
CONSENSUS_OBSERVE = "OBSERVE"
CONSENSUS_EARLY_WARNING = "EARLY_WARNING"
CONSENSUS_ACTION_REQUIRED = "ACTION_REQUIRED"
CONSENSUS_CRITICAL = "CRITICAL"
CONSENSUS_HOLD = "HOLD_UNRELIABLE"


CONFIDENCE_LOW = "LOW"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_SAFETY_OVERRIDE = "SAFETY_OVERRIDE"


VALID_RULE_STATUSES = {
    "NORMAL",
    "WARNING",
    "HIGH",
    "CRITICAL",
}

VALID_PREDICTIVE_DECISIONS = {
    "SAFE",
    "HOLD",
    "ESCALATION",
}

VALID_ANOMALY_LEVELS = {
    "NORMAL",
    "ELEVATED",
    "HIGH",
    "SEVERE",
}


@dataclass
class ConsensusResult:
    status: str
    confidence: str

    rule_status: str
    rule_score: float

    predictive_decision: str
    predictive_probability: float

    anomaly_detected: bool
    anomaly_level: str

    data_quality_reliable: bool

    strong_signal_count: int
    agreement_text: str

    summary: str
    reasons: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# HELPERS
# ============================================================


def _normalize(
    value: str,
) -> str:

    return str(
        value
    ).strip().upper()


def _strong_signal_count(
    rule_status: str,
    predictive_decision: str,
    anomaly_detected: bool,
    anomaly_level: str,
) -> int:

    count = 0

    # Rule engine indicates known deterioration.
    if rule_status in {
        "WARNING",
        "HIGH",
        "CRITICAL",
    }:
        count += 1

    # Predictive model expects future escalation.
    if predictive_decision == "ESCALATION":
        count += 1

    # Only HIGH / SEVERE anomalies count as strong anomaly
    # evidence.
    #
    # ELEVATED remains weak observational evidence.
    if (
        anomaly_detected
        and anomaly_level in {
            "HIGH",
            "SEVERE",
        }
    ):
        count += 1

    return count


def _agreement_text(
    signal_count: int,
) -> str:

    return (
        f"{signal_count}/3 strong detection "
        f"layers indicate concern."
    )


# ============================================================
# CONSENSUS ENGINE
# ============================================================


def evaluate_consensus(
    *,
    rule_status: str,
    rule_score: float,

    predictive_decision: str,
    predictive_probability: float,

    anomaly_detected: bool,
    anomaly_level: str,

    data_quality_reliable: bool,
) -> ConsensusResult:

    rule_status = _normalize(
        rule_status
    )

    predictive_decision = _normalize(
        predictive_decision
    )

    anomaly_level = _normalize(
        anomaly_level
    )

    if rule_status not in VALID_RULE_STATUSES:
        raise ValueError(
            f"Invalid rule status: {rule_status}"
        )

    if (
        predictive_decision
        not in VALID_PREDICTIVE_DECISIONS
    ):
        raise ValueError(
            (
                "Invalid predictive decision: "
                f"{predictive_decision}"
            )
        )

    if (
        anomaly_level
        not in VALID_ANOMALY_LEVELS
    ):
        raise ValueError(
            (
                "Invalid anomaly level: "
                f"{anomaly_level}"
            )
        )

    reasons: list[str] = []

    signal_count = (
        _strong_signal_count(
            rule_status=rule_status,
            predictive_decision=(
                predictive_decision
            ),
            anomaly_detected=(
                anomaly_detected
            ),
            anomaly_level=(
                anomaly_level
            ),
        )
    )

    agreement = (
        _agreement_text(
            signal_count
        )
    )

    # ========================================================
    # 1. DETERMINISTIC CRITICAL SAFETY OVERRIDE
    # ========================================================
    #
    # AI cannot downgrade a deterministic CRITICAL event.
    #
    # Examples:
    #   confirmed arc detection
    #   severe rule-engine thermal condition
    #
    # ========================================================

    if rule_status == "CRITICAL":

        reasons.append(
            (
                "Deterministic GridGuard Risk Engine "
                "reports a CRITICAL condition."
            )
        )

        reasons.append(
            (
                "AI advisory layers are not permitted "
                "to downgrade deterministic critical "
                "safety evidence."
            )
        )

        return ConsensusResult(
            status=CONSENSUS_CRITICAL,

            confidence=(
                CONFIDENCE_SAFETY_OVERRIDE
            ),

            rule_status=rule_status,
            rule_score=float(rule_score),

            predictive_decision=(
                predictive_decision
            ),

            predictive_probability=float(
                predictive_probability
            ),

            anomaly_detected=bool(
                anomaly_detected
            ),

            anomaly_level=anomaly_level,

            data_quality_reliable=bool(
                data_quality_reliable
            ),

            strong_signal_count=(
                signal_count
            ),

            agreement_text=agreement,

            summary=(
                "Critical deterministic safety "
                "condition detected."
            ),

            reasons=reasons,
        )

    # ========================================================
    # 2. DETERMINISTIC HIGH CONDITION
    # ========================================================

    if rule_status == "HIGH":

        reasons.append(
            (
                "Deterministic Risk Engine already "
                "reports a HIGH condition."
            )
        )

        if (
            predictive_decision
            == "ESCALATION"
        ):

            reasons.append(
                (
                    "Predictive ML also indicates "
                    "continued escalation risk."
                )
            )

        if (
            anomaly_detected
            and anomaly_level in {
                "HIGH",
                "SEVERE",
            }
        ):

            reasons.append(
                (
                    "Anomaly detector also reports "
                    "strong deviation from healthy "
                    "behavior."
                )
            )

        return ConsensusResult(
            status=(
                CONSENSUS_ACTION_REQUIRED
            ),

            confidence=CONFIDENCE_HIGH,

            rule_status=rule_status,
            rule_score=float(rule_score),

            predictive_decision=(
                predictive_decision
            ),

            predictive_probability=float(
                predictive_probability
            ),

            anomaly_detected=bool(
                anomaly_detected
            ),

            anomaly_level=anomaly_level,

            data_quality_reliable=bool(
                data_quality_reliable
            ),

            strong_signal_count=(
                signal_count
            ),

            agreement_text=agreement,

            summary=(
                "Known high-risk condition requires "
                "operator attention."
            ),

            reasons=reasons,
        )

    # ========================================================
    # 3. UNRELIABLE TELEMETRY
    # ========================================================
    #
    # Rule Engine WARNING may still be shown elsewhere, but
    # the AI predictive interpretation is withheld.
    #
    # ========================================================

    if not data_quality_reliable:

        reasons.append(
            (
                "Recent telemetry quality is not "
                "reliable enough for predictive "
                "confirmation."
            )
        )

        if anomaly_detected:

            reasons.append(
                (
                    "The anomaly detector identified "
                    "unusual behavior, but anomalous "
                    "telemetry is not equivalent to "
                    "confirmed deterioration."
                )
            )

        return ConsensusResult(
            status=CONSENSUS_HOLD,

            confidence=CONFIDENCE_LOW,

            rule_status=rule_status,
            rule_score=float(rule_score),

            predictive_decision=(
                predictive_decision
            ),

            predictive_probability=float(
                predictive_probability
            ),

            anomaly_detected=bool(
                anomaly_detected
            ),

            anomaly_level=anomaly_level,

            data_quality_reliable=False,

            strong_signal_count=(
                signal_count
            ),

            agreement_text=agreement,

            summary=(
                "AI advisory withheld because recent "
                "telemetry is unreliable."
            ),

            reasons=reasons,
        )

    # ========================================================
    # 4. PREDICTIVE ESCALATION
    # ========================================================

    if (
        predictive_decision
        == "ESCALATION"
    ):

        reasons.append(
            (
                "Predictive model estimates future "
                "HIGH/CRITICAL escalation."
            )
        )

        if rule_status == "WARNING":

            reasons.append(
                (
                    "Deterministic Risk Engine also "
                    "reports current deterioration."
                )
            )

        if (
            anomaly_detected
            and anomaly_level in {
                "HIGH",
                "SEVERE",
            }
        ):

            reasons.append(
                (
                    "Anomaly detector independently "
                    "reports strong deviation from "
                    "healthy behavior."
                )
            )

        elif (
            anomaly_detected
            and anomaly_level
            == "ELEVATED"
        ):

            reasons.append(
                (
                    "Anomaly detector reports a mild "
                    "departure from healthy behavior."
                )
            )

        if (
            rule_status == "WARNING"
            or (
                anomaly_detected
                and anomaly_level in {
                    "HIGH",
                    "SEVERE",
                }
            )
        ):

            confidence = CONFIDENCE_HIGH

        else:

            confidence = CONFIDENCE_MEDIUM

        return ConsensusResult(
            status=(
                CONSENSUS_EARLY_WARNING
            ),

            confidence=confidence,

            rule_status=rule_status,
            rule_score=float(rule_score),

            predictive_decision=(
                predictive_decision
            ),

            predictive_probability=float(
                predictive_probability
            ),

            anomaly_detected=bool(
                anomaly_detected
            ),

            anomaly_level=anomaly_level,

            data_quality_reliable=True,

            strong_signal_count=(
                signal_count
            ),

            agreement_text=agreement,

            summary=(
                "Predictive deterioration detected "
                "before a confirmed severe condition."
            ),

            reasons=reasons,
        )

    # ========================================================
    # 5. CURRENT WARNING WITHOUT PREDICTIVE ESCALATION
    # ========================================================

    if rule_status == "WARNING":

        reasons.append(
            (
                "Deterministic Risk Engine reports a "
                "WARNING condition."
            )
        )

        if anomaly_detected:

            reasons.append(
                (
                    "Anomaly detector also reports "
                    "behavior outside the learned "
                    "healthy pattern."
                )
            )

            confidence = CONFIDENCE_MEDIUM

        else:

            confidence = CONFIDENCE_LOW

        return ConsensusResult(
            status=CONSENSUS_OBSERVE,

            confidence=confidence,

            rule_status=rule_status,
            rule_score=float(rule_score),

            predictive_decision=(
                predictive_decision
            ),

            predictive_probability=float(
                predictive_probability
            ),

            anomaly_detected=bool(
                anomaly_detected
            ),

            anomaly_level=anomaly_level,

            data_quality_reliable=True,

            strong_signal_count=(
                signal_count
            ),

            agreement_text=agreement,

            summary=(
                "Current warning condition should "
                "remain under observation."
            ),

            reasons=reasons,
        )

    # ========================================================
    # 6. PREDICTIVE HOLD
    # ========================================================

    if predictive_decision == "HOLD":

        reasons.append(
            (
                "Predictive evidence has not yet "
                "persisted enough for escalation."
            )
        )

        if anomaly_detected:

            reasons.append(
                (
                    "Anomaly detector reports unusual "
                    "behavior that should be monitored."
                )
            )

        return ConsensusResult(
            status=CONSENSUS_OBSERVE,

            confidence=CONFIDENCE_LOW,

            rule_status=rule_status,
            rule_score=float(rule_score),

            predictive_decision=(
                predictive_decision
            ),

            predictive_probability=float(
                predictive_probability
            ),

            anomaly_detected=bool(
                anomaly_detected
            ),

            anomaly_level=anomaly_level,

            data_quality_reliable=True,

            strong_signal_count=(
                signal_count
            ),

            agreement_text=agreement,

            summary=(
                "Insufficient persistent evidence; "
                "continue monitoring."
            ),

            reasons=reasons,
        )

    # ========================================================
    # 7. ANOMALY WITHOUT PREDICTED ESCALATION
    # ========================================================

    if anomaly_detected:

        if anomaly_level in {
            "HIGH",
            "SEVERE",
        }:

            confidence = CONFIDENCE_MEDIUM

        else:

            confidence = CONFIDENCE_LOW

        reasons.append(
            (
                "Unsupervised detector reports behavior "
                "outside the learned healthy operating "
                "pattern."
            )
        )

        reasons.append(
            (
                "Predictive model does not currently "
                "forecast severe escalation."
            )
        )

        return ConsensusResult(
            status=CONSENSUS_OBSERVE,

            confidence=confidence,

            rule_status=rule_status,
            rule_score=float(rule_score),

            predictive_decision=(
                predictive_decision
            ),

            predictive_probability=float(
                predictive_probability
            ),

            anomaly_detected=True,

            anomaly_level=anomaly_level,

            data_quality_reliable=True,

            strong_signal_count=(
                signal_count
            ),

            agreement_text=agreement,

            summary=(
                "Unusual behavior detected without "
                "confirmed future escalation."
            ),

            reasons=reasons,
        )

    # ========================================================
    # 8. ALL LAYERS NORMAL
    # ========================================================

    reasons.append(
        (
            "Rule Engine reports NORMAL."
        )
    )

    reasons.append(
        (
            "Predictive model does not forecast "
            "escalation."
        )
    )

    reasons.append(
        (
            "Anomaly detector considers the behavior "
            "consistent with healthy operation."
        )
    )

    return ConsensusResult(
        status=CONSENSUS_NORMAL,

        confidence=CONFIDENCE_HIGH,

        rule_status=rule_status,
        rule_score=float(rule_score),

        predictive_decision=(
            predictive_decision
        ),

        predictive_probability=float(
            predictive_probability
        ),

        anomaly_detected=False,

        anomaly_level=anomaly_level,

        data_quality_reliable=True,

        strong_signal_count=0,

        agreement_text=(
            "0/3 strong detection layers "
            "indicate concern."
        ),

        summary=(
            "All GridGuard intelligence layers "
            "currently indicate stable operation."
        ),

        reasons=reasons,
    )