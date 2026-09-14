# GridGuard Demo Guide

This guide defines the recommended demonstration procedure for the current GridGuard prototype.

The primary goal is to demonstrate a complete monitoring and early-warning workflow:

```text
Telemetry
    ↓
Deterministic Risk Analysis
    +
AI Advisory Intelligence
    ↓
Consensus
    ↓
Operations Center
    ↓
Alarm / Early Warning
    ↓
Recovery
```

GridGuard is an educational and engineering prototype.

The current AI validation uses synthetic telemetry, and the physical hardware architecture remains conceptual.

---

# 1. Primary Demonstration Goals

The recommended jury demonstration should show:

- a healthy multi-panel operating baseline,
- live telemetry ingestion,
- explainable deterministic risk analysis,
- predictive AI early warning,
- behavioral anomaly information,
- telemetry quality awareness,
- GridGuard Consensus,
- the AI Early-Warning Timeline,
- the Digital Panel Twin,
- progressive thermal deterioration,
- automatic alarm creation,
- CRITICAL escalation,
- recovery,
- and automatic alarm resolution.

Optional technical demonstrations can additionally show:

- MQTT ingestion,
- MQTT reconnection,
- Modbus TCP integration,
- Modbus failure recovery,
- critical-event webhook notification,
- API inspection,
- and deterministic regression tests.

---

# 2. Demo Positioning

The project should be introduced as:

> A functional software prototype for intelligent low-voltage electrical-panel monitoring and early warning, supported by synthetic AI validation, industrial-style communication integrations, a conceptual edge-hardware architecture, and a virtual panel representation.

Do not describe GridGuard as:

- certified electrical protection equipment,
- an autonomous switching controller,
- a field-proven fault predictor,
- or validated production hardware.

The AI layer is advisory.

Deterministic critical evidence always takes priority.

---

# 3. Recommended Terminal Layout

Use three main terminals.

## Terminal 1 — BACKEND

Runs the FastAPI application.

## Terminal 2 — FRONTEND

Runs the React Operations Center.

## Terminal 3 — DEVELOPMENT / TEST

Used for:

- scenario simulators,
- health checks,
- validation commands,
- recovery,
- and tests.

Additional terminals are only required for optional MQTT, Modbus, or webhook demonstrations.

---

# 4. Pre-Demo Checklist

Before the jury session, verify:

```text
Backend starts successfully
Frontend starts successfully
AI runtime is available
100-panel baseline is healthy
LV-050 is NORMAL
No unwanted active alarms remain
Browser is already open
Panel View works
LV-050 Panel Detail works
```

Also verify the repository is clean:

```powershell
git status
```

Preferred result:

```text
nothing to commit, working tree clean
```

---

# 5. Start the Backend

## Terminal 1 — BACKEND

From the project root:

```powershell
.venv\Scripts\Activate.ps1
```

Then:

```powershell
uvicorn backend.app.main:app --reload --no-access-log
```

Backend address:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 6. Verify Backend Health

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
```

Expected general result:

```text
status = healthy
```

The response also reports the current number of connected panels.

---

# 7. Verify AI Runtime

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/ai/status" | ConvertTo-Json -Depth 10
```

The AI runtime should report the availability of the GridGuard intelligence components.

Do not begin the predictive AI demonstration until the expected models are available.

---

# 8. Start the Frontend

## Terminal 2 — FRONTEND

Run:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

Main navigation:

```text
Overview
Panel View
Alarms
Panels
```

---

# 9. Establish the Healthy Baseline

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
python simulator\multi_panel.py
```

Allow multiple cycles to complete.

The simulator should successfully send telemetry for the virtual panel fleet.

Stop with:

```text
Ctrl + C
```

The preferred baseline for the presentation is:

```text
Panels        : 100
Active Alarms : 0

NORMAL   : 100
WARNING  : 0
HIGH     : 0
CRITICAL : 0
```

If the database already contains previous demonstration state, restore abnormal panels before presenting the baseline.

---

# 10. Show the Overview

In the browser, open:

```text
Overview
```

Show:

- system status,
- connected panels,
- active alarms,
- risk distribution,
- highest-risk panels,
- and fleet-level monitoring.

The purpose of this step is to establish that GridGuard is not only monitoring one demonstration panel.

The software architecture supports a multi-panel environment.

---

# 11. Show the Panels View

Open:

```text
Panels
```

Demonstrate:

- panel listing,
- search,
- status filtering,
- risk score,
- electrical current,
- cable temperature,
- and operational state.

Search for:

```text
LV-050
```

Open the panel detail interface.

---

# 12. Prepare LV-050 for the AI Demonstration

Keep:

```text
LV-050
```

open in Panel Detail.

This is important because the AI Early-Warning Timeline records recent telemetry transitions during the current panel session.

Before starting the scenario, verify that LV-050 is in a healthy state.

Preferred starting state:

```text
Risk Score : 0
Status     : NORMAL
```

---

# 13. Explain GridGuard Intelligence Before Running the Scenario

Before sending abnormal telemetry, briefly point out the AI section.

Relevant information includes:

- predictive risk,
- predictive decision,
- behavioral anomaly,
- data quality,
- consensus,
- confidence,
- layer agreement,
- and AI drivers.

Explain that GridGuard uses multiple intelligence layers rather than treating one ML probability as absolute truth.

Conceptually:

```text
Deterministic Risk
        +
Predictive XGBoost
        +
Isolation Forest
        +
Quality Guard
        ↓
GridGuard Consensus
```

---

# 14. Primary Jury Scenario — Predictive Overheating Demo

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
python simulator\scenario_overheating_demo.py
```

Target panel:

```text
LV-050
```

This is the recommended primary jury scenario.

Do not use the older deterministic-only overheating scenario as the main AI demonstration.

---

# 15. Expected Thermal Sequence

The demonstration sequence is:

| Step | Current | Cable Temperature | Deterministic State |
|---|---:|---:|---|
| 1 | 320 A | 45°C | NORMAL |
| 2 | 340 A | 48°C | NORMAL |
| 3 | 370 A | 54°C | NORMAL |
| 4 | 400 A | 60°C | WARNING |
| 5 | 435 A | 68°C | WARNING |
| 6 | 470 A | 76°C | HIGH |
| 7 | 500 A | 82°C | CRITICAL |

The important transition is between Step 3 and Step 4.

---

# 16. The Key AI Moment

At the demonstrated Step 3:

```text
Current      : 370 A
Cable Temp   : 54 °C

Deterministic Risk:
Status       : NORMAL

Predictive AI:
Early-Warning Advisory
```

At the next telemetry cycle:

```text
Current      : 400 A
Cable Temp   : 60 °C

Deterministic Risk:
Status       : WARNING
```

This is the central GridGuard AI demonstration.

---

# 17. Jury-Safe Early-Warning Claim

Use this wording:

> In our synthetic overheating demonstration, GridGuard's predictive model issued an early-warning advisory one telemetry cycle before the deterministic risk engine crossed its WARNING threshold.

Important qualifiers:

```text
synthetic
advisory
one telemetry cycle
```

Do not say:

```text
GridGuard always predicts failures five cycles early.
```

The model's prediction target examines escalation within the next five telemetry cycles.

That is different from demonstrated lead time.

---

# 18. AI Early-Warning Timeline

While the overheating scenario runs, show the:

```text
AI EARLY-WARNING TIMELINE
```

The graph compares:

```text
Predictive AI %
vs.
Rule Risk Score
```

During the demonstrated early-warning sequence, the interface should be able to show:

```text
EARLY WARNING CONFIRMED
AI led by 1 telemetry cycle
```

Explain that the timeline provides visual evidence that AI escalation occurred before the deterministic WARNING transition in this synthetic sequence.

---

# 19. Show AI Drivers

During deterioration, show the AI driver information.

Possible influential information includes:

- current,
- cable temperature,
- thermal delta,
- recent trends,
- PD behavior,
- humidity,
- and temporal features.

Use wording such as:

> These values explain which model features contributed strongly to the advisory.

Do not say:

> The AI proved that this physical component caused the fault.

Model contribution is not the same as physical causality.

---

# 20. Show the Digital Panel Twin

Open:

```text
Panel View
```

Select or observe:

```text
LV-050
```

The conceptual monitored path is:

```text
Main Busbar
    ↓
Circuit Breaker
    ↓
Outgoing Feeder
    ↓
Cable / Load Area
```

The Digital Panel Twin also visualizes:

- current condition,
- cable temperature,
- partial discharge,
- arc status,
- ambient condition,
- GridGuard Edge,
- data quality,
- AI analysis,
- prediction,
- and consensus.

---

# 21. Digital Panel Twin Early-Warning State

During the synthetic Step 3 condition:

```text
370 A / 54°C
```

the deterministic state can remain NORMAL while the predictive layer identifies early deterioration.

The Digital Panel Twin can visually represent the AI advisory before deterministic WARNING.

Explain:

> The cyan AI state represents predictive advisory information. It does not mean the circuit breaker itself has been proven faulty.

The Digital Panel Twin represents a conceptual monitored electrical path.

It is not a validated physical twin of a real industrial panel.

---

# 22. WARNING State

At approximately:

```text
400 A / 60°C
```

the deterministic engine reaches:

```text
WARNING
```

This demonstrates that the predictive AI advisory appeared before the deterministic threshold crossing in the selected synthetic scenario.

---

# 23. HIGH State

At approximately:

```text
470 A / 76°C
```

the deterministic state reaches:

```text
HIGH
```

Show that:

- the panel status changes,
- the risk score increases,
- alarm state remains active,
- and the visual interface reflects deterioration.

---

# 24. CRITICAL Thermal State

At approximately:

```text
500 A / 82°C
```

the expected deterministic result is:

```text
Risk Score   : 75
Status       : CRITICAL
Primary Risk : THERMAL
```

Show:

- risk state,
- primary risk,
- deterministic explanation,
- telemetry,
- Digital Panel Twin,
- and alarm information.

---

# 25. Verify Alarm Creation

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
$open = Invoke-RestMethod "http://127.0.0.1:8000/alarms?status=OPEN"

$open.alarms |
    Where-Object { $_.panel_id -eq "LV-050" } |
    Select-Object id, panel_id, status, severity, risk_score, primary_risk |
    Format-Table
```

The LV-050 alarm should be OPEN during the abnormal condition.

At the final thermal stage, the alarm should reflect the CRITICAL thermal condition.

---

# 26. Explain the Alarm Lifecycle

The lifecycle is:

```text
NORMAL
   ↓
WARNING
   ↓
OPEN ALARM
   ↓
HIGH / CRITICAL
   ↓
Same alarm updated
   ↓
Recovery
   ↓
RESOLVED
```

GridGuard does not create a separate new alarm for every telemetry sample belonging to the same ongoing event.

---

# 27. Recovery Scenario

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
python simulator\scenario_recovery.py
```

The recovery sequence returns LV-050 toward normal values.

Representative recovery values include:

```text
315 A / 46°C
305 A / 45°C
300 A / 44°C
```

Expected final deterministic state:

```text
Risk Score : 0
Status     : NORMAL
```

The associated OPEN alarm should become:

```text
RESOLVED
```

---

# 28. Verify Recovery

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
$summary = Invoke-RestMethod "http://127.0.0.1:8000/dashboard/summary"

Write-Host "Active alarms:" $summary.active_alarms
Write-Host "Critical panels:" $summary.risk_distribution.critical
```

For a clean restored system, the preferred result is:

```text
Active alarms: 0
Critical panels: 0
```

---

# 29. Arc Detection Demonstration

After completing the primary AI demo, the deterministic arc path can be shown separately.

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
python simulator\scenario_arc.py
```

Target panel:

```text
LV-042
```

When:

```text
arc_detected = True
```

the deterministic system should immediately produce:

```text
Risk Score   : 100
Status       : CRITICAL
Primary Risk : ARC_FLASH
```

Explain:

> GridGuard does not wait for AI confirmation when strong deterministic arc evidence exists.

This demonstrates the deterministic safety priority.

---

# 30. Partial-Discharge Demonstration

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
python simulator\scenario_pd.py
```

Target panel:

```text
LV-041
```

The scenario demonstrates progressively increasing normalized partial-discharge activity.

The PD index used by GridGuard is a prototype normalized value.

It is not a calibrated physical partial-discharge measurement unit.

---

# 31. AI Trace Utility

For technical inspection of the predictive sequence:

```powershell
python simulator\scenario_overheating_ai_trace.py
```

This is useful when discussing AI behavior in more detail.

It is not necessary for the main jury presentation unless technical questions arise.

---

# 32. Deterministic Regression Test

## Terminal 3 — DEVELOPMENT / TEST

Run:

```powershell
python -m risk_engine.test_engine
```

Successful completion should end with:

```text
ALL CORE RISK ENGINE TESTS PASSED
```

This provides a concise technical demonstration of deterministic regression coverage.

Do not run the test module using its direct file path if package imports require module execution.

---

# 33. Swagger / API Demonstration

If the jury asks about the backend API, open:

```text
http://127.0.0.1:8000/docs
```

Important endpoints include:

```text
GET  /health
GET  /ai/status
POST /telemetry

GET /panels
GET /panels/{panel_id}
GET /panels/{panel_id}/telemetry
GET /panels/{panel_id}/risk
GET /panels/{panel_id}/risks
GET /panels/{panel_id}/intelligence

GET /alarms

GET /dashboard/summary
GET /dashboard/panels
GET /dashboard/panels/{panel_id}/detail
```

---

# 34. AI Validation Talking Points

If asked about model validation, use the following summary.

Dataset:

```text
3,000 synthetic scenarios
128,598 telemetry rows
Prediction horizon: 5 telemetry cycles
```

Selected XGBoost held-out synthetic results:

```text
Accuracy  : 95.33%
Precision : 68.77%
Recall    : 94.92%
F1        : 79.76%
ROC-AUC   : 0.9868
PR-AUC    : 0.8955
```

Always add:

> These metrics are based on synthetic prototype telemetry and do not represent validated field performance.

Detailed documentation:

```text
docs/AI_VALIDATION.md
```

---

# 35. Behavioral Anomaly Talking Points

GridGuard also uses Isolation Forest.

Its role is different from the predictive model.

Predictive AI asks:

```text
Is the panel likely to escalate soon?
```

Isolation Forest asks:

```text
Does current behavior look unusual compared with learned healthy behavior?
```

Synthetic test results include approximately:

```text
Healthy specificity     : 95.08%
Abnormal detection rate : 73.22%
```

Again, these are synthetic prototype results.

---

# 36. Quality Guard Talking Points

If asked about false alarms or unreliable telemetry, explain the Quality Guard.

Conceptual behavior:

```text
High AI probability
        +
Unreliable telemetry
        ↓
HOLD
```

instead of automatically generating a strong escalation advisory.

The current synthetic stress suite contains:

```text
12 scenarios
12 passed
```

This includes an unreliable single-cycle spike scenario.

---

# 37. Hardware Question

A likely jury question is:

> How would GridGuard connect to a real electrical panel?

Answer with the proposed architecture:

```text
Field Sensors
      ↓
GridGuard Edge Module
      ↓
MQTT / Modbus / Ethernet
      ↓
GridGuard Server
      ↓
Deterministic Risk + AI
      ↓
Operations Center
```

Potential future sensing concepts include:

- current measurement,
- cable temperature,
- ambient temperature,
- humidity,
- HFCT-style partial-discharge sensing,
- and optical arc sensing.

Immediately clarify:

> The physical Edge Module and sensor installation are currently conceptual and require qualified electrical-engineering validation.

Detailed document:

```text
docs/HARDWARE_CONCEPT.md
```

---

# 38. Optional MQTT Demonstration

MQTT is optional during the main jury session.

Use it only if time allows or the jury asks about industrial integration.

Start Eclipse Mosquitto.

Then in an additional terminal:

```powershell
python integrations\mqtt_consumer.py
```

Expected connection state includes:

```text
[MQTT CONNECTED]
[MQTT SUBSCRIBED]
```

Example telemetry publisher:

```powershell
python simulator\mqtt_single_panel.py
```

Flow:

```text
MQTT Publisher
      ↓
Mosquitto
      ↓
GridGuard MQTT Consumer
      ↓
FastAPI /telemetry
      ↓
Risk + AI
```

---

# 39. Optional MQTT Reconnection Demonstration

With the MQTT consumer running:

1. Stop the broker.
2. Observe the disconnect.
3. Restart the broker.
4. Observe reconnection.

This demonstrates communication recovery.

It is not necessary for the short jury demo.

---

# 40. Optional Modbus Demonstration

Start the simulated Modbus device:

```powershell
python integrations\modbus_server.py
```

Development endpoint:

```text
127.0.0.1:5020
```

In another terminal:

```powershell
python integrations\modbus_adapter.py
```

Conceptual flow:

```text
Simulated PLC
      ↓
Modbus TCP
      ↓
GridGuard Adapter
      ↓
POST /telemetry
      ↓
Risk + AI
```

---

# 41. Optional Critical Webhook Demonstration

Start the local receiver:

```powershell
python integrations\notification_receiver.py
```

Then run:

```powershell
python integrations\critical_notifier.py
```

Default local webhook:

```text
http://127.0.0.1:9001/notify
```

Preferred configuration variable:

```text
GRIDGUARD_WEBHOOK_URL
```

Example:

```powershell
$env:GRIDGUARD_WEBHOOK_URL="http://127.0.0.1:9001/notify"
python integrations\critical_notifier.py
```

The legacy variable:

```text
WEBHOOK_URL
```

is also accepted as a fallback.

---

# 42. Recommended Short Jury Flow

The strongest short demonstration is:

```text
1. Show the GridGuard architecture briefly
2. Open Overview
3. Show the healthy 100-panel baseline
4. Search LV-050
5. Open LV-050 Panel Detail
6. Point out GridGuard Intelligence
7. Keep LV-050 open
8. Run scenario_overheating_demo.py
9. Show AI advisory while deterministic state is still NORMAL
10. Show AI Early-Warning Timeline
11. Show deterministic WARNING
12. Open Panel View
13. Show Digital Panel Twin
14. Continue to HIGH
15. Continue to CRITICAL
16. Show OPEN alarm
17. Run recovery
18. Show NORMAL + RESOLVED alarm
19. Briefly explain deterministic arc override
20. End with limitations and future hardware path
```

This sequence should be preferred over attempting every integration live.

---

# 43. Recommended Presentation Emphasis

The most important GridGuard story is not:

```text
We built many separate features.
```

The story is:

```text
A panel begins in a healthy state.
        ↓
Telemetry gradually deteriorates.
        ↓
AI recognizes the developing pattern.
        ↓
Deterministic thresholds have not yet crossed WARNING.
        ↓
GridGuard issues an advisory.
        ↓
One telemetry cycle later the deterministic engine reaches WARNING.
        ↓
The condition continues to HIGH and CRITICAL.
        ↓
An alarm remains active.
        ↓
The panel recovers.
        ↓
The alarm resolves automatically.
```

This creates one coherent end-to-end story.

---

# 44. What Not to Demonstrate Unless Asked

Avoid spending main presentation time on:

- npm installation,
- Python package installation,
- database file inspection,
- long terminal setup,
- every REST endpoint,
- full MQTT outage testing,
- full Modbus outage testing,
- every ML report,
- or raw model-training scripts.

These are supporting technical evidence.

The main demo should focus on GridGuard's core value.

---

# 45. Statements to Avoid

Do not say:

```text
GridGuard predicts real electrical failures with 95% accuracy.
```

Instead say:

```text
The XGBoost model achieved 95.33% accuracy on our held-out synthetic prototype test set.
```

Do not say:

```text
GridGuard predicts faults five cycles early.
```

Instead say:

```text
The model evaluates escalation within a five-cycle prediction horizon.
In our synthetic overheating demonstration, the advisory appeared one telemetry cycle before deterministic WARNING.
```

Do not say:

```text
This is a certified digital twin.
```

Instead say:

```text
This is a conceptual Digital Panel Twin visualization.
```

Do not say:

```text
GridGuard replaces electrical protection equipment.
```

Instead say:

```text
GridGuard is a monitoring and operator decision-support prototype.
```

---

# 46. Demo Failure Recovery Plan

If the frontend has a temporary issue:

```text
Keep the backend running
Refresh the browser
Reopen LV-050
Continue the scenario if state is still valid
```

If the backend stops:

```text
Restart Terminal 1
Wait for the API to become healthy
Refresh the frontend
```

If LV-050 is left in an abnormal state:

```powershell
python simulator\scenario_recovery.py
```

If the AI Timeline is empty:

```text
Open LV-050 first
Keep the panel open
Then send the next telemetry samples
```

The Timeline represents the current live panel session.

---

# 47. Clean Final State

After rehearsals or abnormal scenarios, restore the project to a clean baseline.

Preferred final dashboard:

```text
Panels        : 100
Active Alarms : 0
System        : ONLINE

NORMAL   : 100
WARNING  : 0
HIGH     : 0
CRITICAL : 0
```

This is the preferred state before beginning the jury presentation.

---

# 48. Final Jury Message

The presentation should end with a clear scope statement:

> GridGuard currently demonstrates an end-to-end software architecture for low-voltage panel monitoring and early warning. The system combines deterministic explainable risk analysis with synthetic-data-trained AI advisory intelligence, industrial-style integrations, alarm management, a Digital Panel Twin, and a conceptual edge-hardware path. Real industrial deployment would require physical sensor integration, engineering validation, field data, calibration, certification, and prospective field testing.

---

# 49. Supporting Documentation

For deeper technical questions:

```text
README.md
docs/ARCHITECTURE.md
docs/AI_VALIDATION.md
docs/HARDWARE_CONCEPT.md
docs/DEMO_GUIDE.MD
```

Conceptual diagrams:

```text
docs/diagrams1/01_system_architecture.png
docs/diagrams1/02_panel_instrumentation_concept.png
docs/diagrams1/03_panel_layout_overlay.png
docs/diagrams1/04_sensor_io_map.png
docs/diagrams1/05_end_to_end_flow.png
```

---

# 50. Final Safety Disclaimer

GridGuard is an educational and engineering prototype.

The current system uses:

- demonstration deterministic thresholds,
- synthetic AI training and validation data,
- conceptual physical hardware,
- and software-based panel visualization.

It must not be used directly as certified protection logic or autonomous electrical switching equipment.

Real deployment requires qualified engineering review and compliance with applicable electrical, industrial, cybersecurity, and safety requirements.