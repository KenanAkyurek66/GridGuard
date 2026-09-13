from __future__ import annotations

import json

from backend.app.ai_service import (
    analyze_gridguard_intelligence,
)
from backend.app.database import SessionLocal
from backend.app.models import (
    RiskAssessment,
    Telemetry,
)


# ============================================================
# GRIDGUARD AI - LIVE DATABASE INTEGRATION TEST
# ============================================================
#
# Purpose
# -------
# Read real GridGuard runtime telemetry from SQLite and send it
# through the complete AI intelligence service:
#
#   Telemetry History
#        ↓
#   XGBoost Predictor
#        ↓
#   Quality / Persistence Guard
#        ↓
#   Isolation Forest
#        ↓
#   Explainability
#        ↓
#   AI Consensus
#
# No database records are changed by this test.
#
# ============================================================


PANEL_ID = "LV-050"
HISTORY_LIMIT = 20


def main() -> None:

    db = SessionLocal()

    try:

        # ====================================================
        # LOAD TELEMETRY HISTORY
        # ====================================================

        telemetry_records = (
            db.query(Telemetry)
            .filter(
                Telemetry.panel_id
                == PANEL_ID
            )
            .order_by(
                Telemetry.timestamp.desc()
            )
            .limit(
                HISTORY_LIMIT
            )
            .all()
        )

        if not telemetry_records:

            raise RuntimeError(
                f"No telemetry found for {PANEL_ID}."
            )

        # Database returns newest → oldest.
        telemetry_records.reverse()

        telemetry_rows = [
            {
                "current_a":
                    record.current_a,

                "cable_temperature_c":
                    record.cable_temperature_c,

                "ambient_temperature_c":
                    record.ambient_temperature_c,

                "humidity_pct":
                    record.humidity_pct,

                "pd_index":
                    record.pd_index,

                "arc_detected":
                    record.arc_detected,

                "data_quality":
                    record.data_quality,
            }
            for record in telemetry_records
        ]

        # ====================================================
        # LOAD LATEST DETERMINISTIC RISK RESULT
        # ====================================================

        latest_risk = (
            db.query(RiskAssessment)
            .filter(
                RiskAssessment.panel_id
                == PANEL_ID
            )
            .order_by(
                RiskAssessment.timestamp.desc()
            )
            .first()
        )

        if latest_risk is None:

            raise RuntimeError(
                f"No risk assessment found for {PANEL_ID}."
            )

        risk_result = {
            "risk_score":
                latest_risk.risk_score,

            "status":
                latest_risk.status,

            "primary_risk":
                latest_risk.primary_risk,

            "causes":
                latest_risk.causes,

            "component_scores":
                latest_risk.component_scores,

            "metrics":
                latest_risk.metrics,
        }

        # ====================================================
        # RUN GRIDGUARD INTELLIGENCE
        # ====================================================

        intelligence = (
            analyze_gridguard_intelligence(
                telemetry_rows=telemetry_rows,
                risk_result=risk_result,
            )
        )

        # ====================================================
        # OUTPUT
        # ====================================================

        print(
            "=" * 72
        )

        print(
            "GRIDGUARD AI - LIVE DATABASE TEST"
        )

        print(
            "=" * 72
        )

        print()

        print(
            f"Panel          : {PANEL_ID}"
        )

        print(
            f"History points : {len(telemetry_rows)}"
        )

        print()

        print(
            "DETERMINISTIC RISK"
        )

        print(
            f"Status         : "
            f"{risk_result['status']}"
        )

        print(
            f"Risk Score     : "
            f"{risk_result['risk_score']}"
        )

        print(
            f"Primary Risk   : "
            f"{risk_result['primary_risk']}"
        )

        print()

        if not intelligence.get(
            "available"
        ):

            print(
                "AI AVAILABLE   : False"
            )

            print(
                json.dumps(
                    intelligence,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            return

        predictive = (
            intelligence[
                "predictive"
            ]
        )

        anomaly = (
            intelligence[
                "anomaly"
            ]
        )

        consensus = (
            intelligence[
                "consensus"
            ]
        )

        explainability = (
            intelligence[
                "explainability"
            ]
        )

        print(
            "PREDICTIVE AI"
        )

        print(
            f"Probability    : "
            f"{predictive['probability_pct']}%"
        )

        print(
            f"Decision       : "
            f"{predictive['decision']}"
        )

        print(
            f"Data Reliable  : "
            f"{predictive['data_reliable']}"
        )

        print(
            f"Recent Scores  : "
            f"{predictive['recent_probabilities']}"
        )

        print()

        print(
            "ANOMALY DETECTOR"
        )

        print(
            f"Detected       : "
            f"{anomaly['detected']}"
        )

        print(
            f"Level          : "
            f"{anomaly['level']}"
        )

        print(
            f"Normality      : "
            f"{anomaly['normality_score']}"
        )

        print(
            f"Strength       : "
            f"{anomaly['strength']}"
        )

        print()

        print(
            "AI CONSENSUS"
        )

        print(
            f"Status         : "
            f"{consensus['status']}"
        )

        print(
            f"Confidence     : "
            f"{consensus['confidence']}"
        )

        print(
            f"Agreement      : "
            f"{consensus['agreement_text']}"
        )

        print(
            f"Summary        : "
            f"{consensus['summary']}"
        )

        print()

        print(
            "TOP AI DRIVERS"
        )

        for (
            index,
            driver,
        ) in enumerate(
            explainability[
                "top_drivers"
            ],
            start=1,
        ):

            print(
                f"{index}. "
                f"{driver['label']}"
            )

            print(
                f"   Contribution : "
                f"{driver['contribution']}"
            )

            print(
                f"   Direction    : "
                f"{driver['direction']}"
            )

        print()

        print(
            "=" * 72
        )

        print(
            "LIVE GRIDGUARD AI DATABASE TEST COMPLETE"
        )

        print(
            "=" * 72
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()