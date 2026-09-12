# GridGuard Demo Guide

This guide describes a recommended demonstration flow for the GridGuard prototype.

The goal is to demonstrate the complete path from telemetry generation to explainable risk detection, alarm creation, live dashboard visualization, external notification, and recovery.

---

# 1. Demo Goals

A successful GridGuard demonstration should show:

- A healthy 100-panel baseline
- Live telemetry ingestion
- Explainable risk scoring
- Progressive overheating detection
- Partial discharge degradation
- Immediate arc-flash detection
- Automatic alarm creation
- Live dashboard updates
- Panel-level trend inspection
- Alarm resolution after recovery
- MQTT ingestion
- Modbus TCP ingestion
- Critical-event webhook notification

The recommended order starts with the core GridGuard workflow before optional industrial integrations.

---

# 2. Recommended Terminal Layout

For the basic demo, use three terminals.

## Terminal 1 — Backend

Runs the FastAPI application.

## Terminal 2 — Frontend

Runs the React dashboard.

## Terminal 3 — Scenario / Development

Used for simulators, tests, and scenario commands.

Additional terminals can be opened when demonstrating MQTT, Modbus, or notifications.

---

# 3. Start the Backend

From the GridGuard project root:

```powershell
.venv\Scripts\Activate.ps1
```

Then:

```powershell
uvicorn backend.app.main:app --reload --no-access-log
```

Expected endpoint:

```text
http://127.0.0.1:8000
```

Optional health check:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
```

Expected system state:

```text
status: healthy
```

---

# 4. Start the Frontend

Open another terminal:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

The dashboard should report:

```text
SYSTEM ONLINE
```

---

# 5. Establish the 100-Panel Baseline

In Terminal 3:

```powershell
python simulator\multi_panel.py
```

Allow several cycles to run.

Expected output:

```text
Sent: 100/100
Errors: 0
```

Stop the simulator with:

```text
Ctrl + C
```

The dashboard should show approximately:

```text
Connected Panels: 100
Active Alarms: 0
Normal: 100
Warning: 0
High: 0
Critical: 0
```

This establishes the normal operating baseline.

---

# 6. Demonstrate the Panel Monitor

Open the `Panels` section of the dashboard.

Demonstrate:

- Panel search
- Status filtering
- Live telemetry
- Risk score
- Current
- Cable temperature
- Ambient temperature
- Humidity
- Partial discharge index
- Data quality

Search for a specific panel such as:

```text
LV-050
```

Click the panel to open its detail view.

The panel detail view should include:

- Current telemetry
- Risk score
- Status
- Primary risk
- Explainable causes
- Component scores
- Current history
- Temperature history
- Risk-score history

---

# 7. Overheating Scenario

Keep the dashboard visible.

In Terminal 3:

```powershell
python simulator\scenario_overheating.py
```

The target panel is:

```text
LV-050
```

Expected progression:

```text
NORMAL
↓
WARNING
↓
HIGH
↓
CRITICAL
```

The final stage should produce approximately:

```text
Current      : 500 A
Cable Temp   : 82 °C
Risk Score   : 75
Status       : CRITICAL
Primary Risk : THERMAL
```

The exact explainable causes may include:

```text
Current increased above recent baseline.
Cable temperature is extremely high.
Cable-to-ambient thermal delta is very high.
Severe thermal escalation pattern detected.
```

During the scenario, demonstrate that the dashboard updates automatically.

---

# 8. Verify Automatic Alarm Creation

After the overheating scenario:

```powershell
$open = Invoke-RestMethod "http://127.0.0.1:8000/alarms?status=OPEN"

$open.alarms |
    Where-Object { $_.panel_id -eq "LV-050" } |
    Select-Object id, panel_id, status, severity, risk_score, primary_risk |
    Format-Table
```

Expected result:

```text
panel_id      LV-050
status        OPEN
severity      CRITICAL
risk_score    75
primary_risk  THERMAL
```

The dashboard should also show one active alarm.

---

# 9. Recovery Scenario

Run:

```powershell
python simulator\scenario_recovery.py
```

Expected recovery:

```text
Risk Score : 0
Status     : NORMAL
```

The first recovery step should resolve the open alarm.

Example:

```text
Alarm action: RESOLVED
```

Verify:

```powershell
$summary = Invoke-RestMethod "http://127.0.0.1:8000/dashboard/summary"

Write-Host "Active alarms:" $summary.active_alarms
Write-Host "Critical panels:" $summary.risk_distribution.critical
```

Expected:

```text
Active alarms: 0
Critical panels: 0
```

This demonstrates the complete alarm lifecycle:

```text
NORMAL
↓
ABNORMAL CONDITION
↓
OPEN ALARM
↓
RECOVERY
↓
RESOLVED ALARM
```

---

# 10. Partial Discharge Scenario

Run:

```powershell
python simulator\scenario_pd.py
```

Target panel:

```text
LV-041
```

Expected progression includes increasing partial discharge activity.

Typical final state:

```text
PD Index     : 72
Risk Score   : 50
Status       : HIGH
Primary Risk : PARTIAL_DISCHARGE
```

This demonstrates that GridGuard can detect degradation patterns even when current and temperature remain relatively stable.

---

# 11. Arc-Flash Scenario

Run:

```powershell
python simulator\scenario_arc.py
```

Target panel:

```text
LV-042
```

Before the arc event:

```text
Status: NORMAL
```

When the arc signal changes to:

```text
ARC: True
```

GridGuard should immediately produce:

```text
Risk Score   : 100
Status       : CRITICAL
Primary Risk : ARC_FLASH
```

This demonstrates the direct safety-critical override behavior.

---

# 12. Core Regression Test

The complete core risk-engine regression suite can be shown with:

```powershell
python -m risk_engine.test_engine
```

Expected ending:

```text
ALL CORE RISK ENGINE TESTS PASSED
```

The suite verifies:

- Normal condition
- Moderate overheating
- Severe overheating
- Partial discharge degradation
- Severe partial discharge escalation
- Arc flash

---

# 13. MQTT Integration Demo

Eclipse Mosquitto must be installed and running.

The development broker configuration is:

```text
Host: 127.0.0.1
Port: 1883
```

Open an additional terminal and run:

```powershell
python integrations\mqtt_consumer.py
```

Expected output:

```text
[MQTT CONNECTED]
[MQTT SUBSCRIBED]
Waiting for GridGuard telemetry...
```

The subscribed topic is:

```text
gridguard/telemetry/#
```

Telemetry received through MQTT is forwarded into the standard GridGuard processing pipeline.

---

# 14. MQTT Reliability Demo

With the MQTT consumer running, temporarily stop the broker.

The consumer should report a disconnection.

Restart the broker.

The consumer should automatically reconnect and display:

```text
[MQTT CONNECTED]
[MQTT SUBSCRIBED]
```

This demonstrates broker recovery handling.

---

# 15. Modbus TCP Demo

Open an additional terminal.

Start the simulated Modbus device:

```powershell
python integrations\modbus_server.py
```

Expected:

```text
Simulated asset: LV-060
[MODBUS SERVER READY]
Listening on 127.0.0.1:5020
```

The register map represents:

```text
HR0 Current
HR1 Cable Temperature
HR2 Ambient Temperature
HR3 Humidity
HR4 PD Index
HR5 Arc Detection
HR6 Data Quality
```

In another terminal run:

```powershell
python integrations\modbus_adapter.py
```

Expected flow:

```text
[CONNECTING TO PLC]
↓
Modbus values read
↓
[FORWARDING TO GRIDGUARD]
↓
POST http://127.0.0.1:8000/telemetry
↓
[GRIDGUARD ACCEPTED]
```

The panel:

```text
LV-060
```

should be visible in the dashboard.

---

# 16. Modbus Reliability Demo

Stop the simulated Modbus server.

Run or observe the adapter.

Expected behavior:

```text
[MODBUS CONNECTION FAILED]
```

Restart:

```powershell
python integrations\modbus_server.py
```

Run the adapter again.

The telemetry request should succeed.

This demonstrates failure detection and recovery of the industrial adapter.

---

# 17. Critical Notification Demo

Start the local notification receiver:

```powershell
python integrations\notification_receiver.py
```

Expected:

```text
Waiting for GridGuard critical alerts...
```

In another terminal run:

```powershell
python integrations\critical_notifier.py
```

The default webhook endpoint is:

```text
http://127.0.0.1:9001/notify
```

Now run a critical scenario such as:

```powershell
python simulator\scenario_overheating.py
```

or:

```powershell
python simulator\scenario_arc.py
```

The notifier should detect the new critical alarm.

Expected notifier output:

```text
[NOTIFICATION SENT]
Event      : CRITICAL_OPEN
Panel      : ...
Severity   : CRITICAL
Risk Score : ...
```

The notification receiver should display the external event payload.

After recovery, the notifier can also produce:

```text
CRITICAL_RESOLVED
```

---

# 18. Database Persistence Demo

GridGuard stores runtime information in:

```text
data/gridguard.db
```

To demonstrate persistence:

1. Record the telemetry count of a panel.
2. Stop the FastAPI backend.
3. Restart the backend.
4. Query the same telemetry endpoint again.

Example:

```powershell
$before = Invoke-RestMethod "http://127.0.0.1:8000/panels/LV-050/telemetry?limit=100"

Write-Host "Telemetry count:" $before.count
```

After restart, the count should remain available.

This demonstrates persistence across backend restarts.

---

# 19. Validation Demo

GridGuard rejects invalid telemetry through Pydantic validation.

For example, a humidity value outside the accepted range should produce:

```text
HTTP 422
```

This demonstrates validation before invalid measurements enter the main processing pipeline.

---

# 20. Recommended Short Presentation Flow

For a short live demonstration, use the following sequence:

```text
1. Open dashboard
2. Show 100 healthy panels
3. Open LV-050 panel detail
4. Run overheating scenario
5. Watch NORMAL → WARNING → HIGH → CRITICAL
6. Show explainable causes and trend charts
7. Show OPEN critical alarm
8. Run recovery
9. Show alarm becoming RESOLVED
10. Run arc scenario
11. Show immediate 100/100 CRITICAL result
```

This is the most effective sequence for demonstrating GridGuard's core value without spending too much time on setup.

---

# 21. Extended Demonstration Flow

For a longer technical presentation:

```text
1. Architecture overview
2. Backend health
3. 100-panel baseline
4. Panel monitoring
5. Overheating scenario
6. Alarm lifecycle
7. Recovery
8. Partial discharge scenario
9. Arc-flash scenario
10. Regression tests
11. MQTT integration
12. MQTT reconnection
13. Modbus integration
14. Modbus failure/recovery
15. Critical webhook notification
16. Database persistence
17. Production build / repository structure
```

---

# 22. Final Healthy State

After all abnormal scenarios, restore affected panels before a final presentation or screenshot.

The preferred final dashboard state is:

```text
Panels: 100
Active alarms: 0
System: ONLINE

Normal: 100
Warning: 0
High: 0
Critical: 0
```

This provides a clean starting point for the next demo.

---

# 23. Important Prototype Disclaimer

The project uses demonstration thresholds for:

- Current deviation
- Temperature
- Thermal delta
- Humidity
- Partial discharge
- Risk escalation

These values must not be interpreted as universal electrical protection settings.

GridGuard is a software architecture and monitoring prototype.

Real deployment would require qualified electrical engineering assessment, sensor calibration, cybersecurity controls, hardware validation, protection-system coordination, and compliance with applicable standards.