import "./DigitalPanelTwin.css";


const DETERMINISTIC_STATES = [
  "WARNING",
  "HIGH",
  "CRITICAL",
];


function humanize(value) {
  if (!value) {
    return "UNKNOWN";
  }

  return String(value).replaceAll("_", " ");
}


function formatNumber(value, digits = 1) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "--";
  }

  return Number(value).toFixed(digits);
}


function statusClass(value) {
  return String(
    value ?? "NORMAL"
  ).toLowerCase();
}


function isPositiveScore(value) {
  return Number(value ?? 0) > 0;
}


function containsAny(text, words) {
  const normalized =
    String(text ?? "").toLowerCase();

  return words.some(
    (word) =>
      normalized.includes(word)
  );
}


function detectAiFocus(
  intelligence,
  risk
) {
  const drivers =
    intelligence?.explainability
      ?.top_drivers ?? [];

  const positiveDrivers =
    drivers.filter(
      (driver) =>
        driver.direction ===
        "INCREASES_RISK"
    );


  for (
    const driver of positiveDrivers
  ) {
    const label =
      String(
        driver.label ??
        driver.feature ??
        ""
      ).toLowerCase();


    if (
      containsAny(
        label,
        [
          "cable temperature",
          "thermal",
          "temperature",
        ]
      )
    ) {
      return "thermal";
    }


    if (
      containsAny(
        label,
        [
          "current",
          "load",
          "amp",
        ]
      )
    ) {
      return "current";
    }


    if (
      containsAny(
        label,
        [
          "partial discharge",
          "pd index",
          "pd ",
        ]
      )
    ) {
      return "pd";
    }


    if (
      containsAny(
        label,
        [
          "humidity",
          "ambient",
          "environment",
        ]
      )
    ) {
      return "environment";
    }


    if (
      label.includes("arc")
    ) {
      return "arc";
    }
  }


  const primaryRisk =
    String(
      risk?.primary_risk ??
      ""
    ).toUpperCase();


  if (
    primaryRisk.includes(
      "THERMAL"
    )
  ) {
    return "thermal";
  }


  if (
    primaryRisk.includes(
      "CURRENT"
    )
  ) {
    return "current";
  }


  if (
    primaryRisk.includes(
      "PARTIAL"
    ) ||
    primaryRisk === "PD"
  ) {
    return "pd";
  }


  if (
    primaryRisk.includes(
      "ENVIRONMENT"
    )
  ) {
    return "environment";
  }


  if (
    primaryRisk.includes(
      "ARC"
    )
  ) {
    return "arc";
  }


  return "unknown";
}


function aiFocusLabel(focus) {
  switch (focus) {
    case "current":
      return "CURRENT / FEEDER";

    case "thermal":
      return "CABLE TEMPERATURE";

    case "pd":
      return "PARTIAL DISCHARGE";

    case "environment":
      return "ENVIRONMENT";

    case "arc":
      return "ARC";

    default:
      return "DEVELOPING CONDITION";
  }
}


function aiFocusDescription(focus) {
  switch (focus) {
    case "current":
      return "AI detected a developing load or current trend on the outgoing feeder.";

    case "thermal":
      return "AI detected a developing thermal condition around the monitored cable / load area.";

    case "pd":
      return "AI detected unusual partial-discharge behavior in the monitored outgoing circuit.";

    case "environment":
      return "AI detected an environmental pattern that may contribute to panel risk.";

    case "arc":
      return "AI detected features associated with the arc-monitoring path.";

    default:
      return "AI detected a developing condition before the deterministic warning threshold was reached.";
  }
}


function StatusDot({
  state = "NORMAL",
  ai = false,
}) {
  return (
    <span
      className={
        ai
          ? "simple-ai-dot"
          : `simple-status-dot ${statusClass(
              state
            )}`
      }
    />
  );
}


function StateBadge({
  state = "NORMAL",
  ai = false,
}) {
  if (ai) {
    return (
      <span className="simple-state-badge ai">
        AI EARLY
      </span>
    );
  }

  return (
    <span
      className={`simple-state-badge ${statusClass(
        state
      )}`}
    >
      {state}
    </span>
  );
}


function PowerStage({
  number,
  title,
  description,
  state = "NORMAL",
  ai = false,
  children,
}) {
  return (
    <article
      className={[
        "power-stage",
        statusClass(state),
        ai ? "ai-warning" : "",
      ].join(" ")}
    >
      <div className="power-stage-number">
        {number}
      </div>


      <div className="power-stage-main">

        <div className="power-stage-top">

          <div>

            <h4>
              {title}
            </h4>

            <p>
              {description}
            </p>

          </div>


          <StateBadge
            state={state}
            ai={ai}
          />

        </div>


        {children && (
          <div className="power-stage-info">
            {children}
          </div>
        )}

      </div>
    </article>
  );
}


function FlowArrow() {
  return (
    <div className="simple-flow-arrow">
      <span />
      <strong>
        ↓
      </strong>
    </div>
  );
}


function SensorRow({
  label,
  value,
  description,
  state = "NORMAL",
  ai = false,
}) {
  return (
    <div
      className={[
        "simple-sensor-row",
        statusClass(state),
        ai ? "ai-warning" : "",
      ].join(" ")}
    >

      <div className="simple-sensor-left">

        <StatusDot
          state={state}
          ai={ai}
        />

        <div>

          <strong>
            {label}
          </strong>

          <span>
            {description}
          </span>

        </div>

      </div>


      <div className="simple-sensor-right">

        <strong>
          {value}
        </strong>

        <StateBadge
          state={state}
          ai={ai}
        />

      </div>

    </div>
  );
}


function DigitalPanelTwin({
  detail,
}) {
  const panel =
    detail?.panel ?? {};

  const risk =
    detail?.risk ?? {};

  const intelligence =
    detail?.intelligence ?? {};

  const predictive =
    intelligence?.predictive ?? {};

  const consensus =
    intelligence?.consensus ?? {};

  const scores =
    risk?.component_scores ?? {};


  const overallStatus =
    String(
      risk?.status ??
      "NORMAL"
    ).toUpperCase();


  const deterministicActive =
    DETERMINISTIC_STATES.includes(
      overallStatus
    );


  const primaryRisk =
    String(
      risk?.primary_risk ??
      ""
    ).toUpperCase();


  const currentInvolved =
    deterministicActive &&
    (
      isPositiveScore(
        scores.current
      ) ||
      primaryRisk.includes(
        "CURRENT"
      )
    );


  const thermalInvolved =
    deterministicActive &&
    (
      isPositiveScore(
        scores.thermal
      ) ||
      primaryRisk.includes(
        "THERMAL"
      )
    );


  const environmentInvolved =
    deterministicActive &&
    (
      isPositiveScore(
        scores.environment
      ) ||
      primaryRisk.includes(
        "ENVIRONMENT"
      )
    );


  const pdInvolved =
    deterministicActive &&
    (
      isPositiveScore(
        scores.partial_discharge
      ) ||
      primaryRisk.includes(
        "PARTIAL"
      ) ||
      primaryRisk === "PD"
    );


  const arcInvolved =
    Boolean(
      panel?.arc_detected
    ) ||
    primaryRisk.includes(
      "ARC"
    );


  const currentState =
    currentInvolved
      ? overallStatus
      : "NORMAL";


  const thermalState =
    thermalInvolved
      ? overallStatus
      : "NORMAL";


  const environmentState =
    environmentInvolved
      ? overallStatus
      : "NORMAL";


  const pdState =
    pdInvolved
      ? overallStatus
      : "NORMAL";


  const arcState =
    arcInvolved
      ? "CRITICAL"
      : "NORMAL";


  const busbarState =
    arcInvolved
      ? "CRITICAL"
      : "NORMAL";


  const breakerPathState =
    arcInvolved
      ? "CRITICAL"
      : currentInvolved
        ? overallStatus
        : "NORMAL";


  const feederState =
    currentInvolved ||
    thermalInvolved
      ? overallStatus
      : "NORMAL";


  const cableState =
    thermalInvolved ||
    pdInvolved
      ? overallStatus
      : "NORMAL";


  const aiEarlyWarning =
    consensus?.status ===
      "EARLY_WARNING" &&
    overallStatus ===
      "NORMAL";


  const aiFocus =
    aiEarlyWarning
      ? detectAiFocus(
          intelligence,
          risk
        )
      : null;


  const aiCurrent =
    aiEarlyWarning &&
    aiFocus === "current";


  const aiThermal =
    aiEarlyWarning &&
    aiFocus === "thermal";


  const aiPd =
    aiEarlyWarning &&
    aiFocus === "pd";


  const aiEnvironment =
    aiEarlyWarning &&
    aiFocus ===
      "environment";


  const aiArc =
    aiEarlyWarning &&
    aiFocus === "arc";


  const aiBreaker =
    aiCurrent ||
    aiArc;


  const aiFeeder =
    aiCurrent ||
    aiThermal;


  const aiCable =
    aiThermal ||
    aiPd;


  const telemetryAvailable =
    Boolean(
      panel?.last_seen
    );


  const dataQuality =
    panel?.data_quality ??
    "UNKNOWN";


  return (
    <section className="simple-digital-twin">

      <div className="simple-twin-header">

        <div>

          <p className="simple-eyebrow">
            VIRTUAL HARDWARE MODEL
          </p>

          <h3>
            {panel?.panel_id ?? "PANEL"} Electrical Panel
          </h3>

          <p>
            Follow the electrical power
            path from the main distribution
            bus to the monitored outgoing
            cable.
          </p>

        </div>


        <div
          className={`simple-panel-state ${statusClass(
            overallStatus
          )}`}
        >

          <span>
            PANEL STATE
          </span>

          <strong>
            {humanize(
              overallStatus
            )}
          </strong>

          <small>
            Risk {risk?.risk_score ?? 0}/100
          </small>

        </div>

      </div>


      {aiEarlyWarning && (

        <div className="simple-ai-banner">

          <div className="simple-ai-pulse" />

          <div>

            <span>
              GRIDGUARD PREDICTIVE AI
            </span>

            <strong>
              Early warning before
              deterministic threshold
            </strong>

            <p>
              {aiFocusDescription(
                aiFocus
              )}
            </p>

          </div>


          <div className="simple-ai-focus">
            {aiFocusLabel(
              aiFocus
            )}
          </div>

        </div>

      )}


      <div className="simple-twin-grid">

        <div className="simple-power-flow">

          <div className="simple-section-heading">

            <div>

              <span>
                ELECTRICAL POWER FLOW
              </span>

              <strong>
                Electrical Path & Condition
              </strong>

            </div>

          </div>


          <PowerStage
            number="1"
            title="Main Busbar"
            description="Main conductor that distributes electrical power inside the panel."
            state={busbarState}
            ai={aiArc}
          >

            <div className="stage-reading">

              <span>
                Arc monitoring
              </span>

              <strong
                className={
                  panel?.arc_detected
                    ? "danger-reading"
                    : "safe-reading"
                }
              >
                {panel?.arc_detected
                  ? "DETECTED"
                  : "CLEAR"}
              </strong>

            </div>

          </PowerStage>


          <FlowArrow />


          <PowerStage
            number="2"
            title="Circuit Breaker"
            description="Protection and switching device for the outgoing electrical circuit."
            state={breakerPathState}
            ai={aiBreaker}
          >

            <div className="stage-reading">

              <span>
                Monitored path current
              </span>

              <strong>
                {formatNumber(
                  panel?.current_a,
                  1
                )} A
              </strong>

            </div>

            <small className="stage-note">
              Color represents the
              monitored electrical path,
              not a confirmed breaker fault.
            </small>

          </PowerStage>


          <FlowArrow />


          <PowerStage
            number="3"
            title="Outgoing Feeder"
            description="Electrical path carrying power from the breaker toward the connected load."
            state={feederState}
            ai={aiFeeder}
          >

            <div className="stage-reading">

              <span>
                Current measurement
              </span>

              <strong>
                {formatNumber(
                  panel?.current_a,
                  1
                )} A
              </strong>

            </div>

          </PowerStage>


          <FlowArrow />


          <PowerStage
            number="4"
            title="Cable / Load Area"
            description="Monitored outgoing cable and load area where thermal and PD conditions are observed."
            state={cableState}
            ai={aiCable}
          >

            <div className="stage-reading-grid">

              <div>

                <span>
                  Cable temperature
                </span>

                <strong>
                  {formatNumber(
                    panel
                      ?.cable_temperature_c,
                    1
                  )} °C
                </strong>

              </div>


              <div>

                <span>
                  Partial discharge
                </span>

                <strong>
                  {formatNumber(
                    panel?.pd_index,
                    1
                  )}
                </strong>

              </div>

            </div>

          </PowerStage>

        </div>


        <aside className="simple-sensor-panel">

          <div className="simple-section-heading">

            <div>

              <span>
                SENSOR STATUS
              </span>

              <strong>
                What is GridGuard seeing?
              </strong>

            </div>

          </div>


          <SensorRow
            label="Current"
            value={`${formatNumber(
              panel?.current_a,
              1
            )} A`}
            description="Electrical load measurement"
            state={currentState}
            ai={aiCurrent}
          />


          <SensorRow
            label="Cable Temperature"
            value={`${formatNumber(
              panel?.cable_temperature_c,
              1
            )} °C`}
            description="Cable / surface thermal monitoring"
            state={thermalState}
            ai={aiThermal}
          />


          <SensorRow
            label="Partial Discharge"
            value={formatNumber(
              panel?.pd_index,
              1
            )}
            description="PD monitoring channel"
            state={pdState}
            ai={aiPd}
          />


          <SensorRow
            label="Arc Detection"
            value={
              panel?.arc_detected
                ? "DETECTED"
                : "CLEAR"
            }
            description="Optical arc monitoring"
            state={arcState}
            ai={aiArc}
          />


          <SensorRow
            label="Ambient"
            value={`${formatNumber(
              panel
                ?.ambient_temperature_c,
              1
            )} °C · ${formatNumber(
              panel?.humidity_pct,
              1
            )}% RH`}
            description="Panel environment"
            state={environmentState}
            ai={aiEnvironment}
          />


          <div className="simple-edge-module">

            <div className="simple-edge-title">

              <div>

                <span>
                  GRIDGUARD EDGE
                </span>

                <strong>
                  EDGE-01
                </strong>

              </div>

              <span className="simple-virtual-tag">
                VIRTUAL
              </span>

            </div>


            <div className="simple-edge-status">

              <div>

                <span>
                  Telemetry
                </span>

                <strong
                  className={
                    telemetryAvailable
                      ? "edge-ok"
                      : "edge-problem"
                  }
                >
                  {telemetryAvailable
                    ? "CONNECTED"
                    : "NO DATA"}
                </strong>

              </div>


              <div>

                <span>
                  Data Quality
                </span>

                <strong
                  className={
                    dataQuality ===
                    "GOOD"
                      ? "edge-ok"
                      : "edge-warning"
                  }
                >
                  {dataQuality}
                </strong>

              </div>


              <div>

                <span>
                  AI Analysis
                </span>

                <strong
                  className={
                    intelligence?.available
                      ? "edge-ok"
                      : "edge-warning"
                  }
                >
                  {intelligence?.available
                    ? "AVAILABLE"
                    : "UNAVAILABLE"}
                </strong>

              </div>


              <div>

                <span>
                  Prediction
                </span>

                <strong>
                  {humanize(
                    predictive?.decision
                  )}
                </strong>

              </div>


              <div>

                <span>
                  Consensus
                </span>

                <strong>
                  {humanize(
                    consensus?.status
                  )}
                </strong>

              </div>

            </div>

          </div>

        </aside>

      </div>


      <div className="simple-data-flow">

        <div>

          <span className="data-flow-number">
            1
          </span>

          <strong>
            Field Sensors
          </strong>

          <small>
            Measure panel conditions
          </small>

        </div>


        <span className="data-flow-arrow">
          →
        </span>


        <div>

          <span className="data-flow-number">
            2
          </span>

          <strong>
            GridGuard Edge
          </strong>

          <small>
            Collects and validates data
          </small>

        </div>


        <span className="data-flow-arrow">
          →
        </span>


        <div>

          <span className="data-flow-number">
            3
          </span>

          <strong>
            MQTT / Modbus
          </strong>

          <small>
            Industrial communication
          </small>

        </div>


        <span className="data-flow-arrow">
          →
        </span>


        <div>

          <span className="data-flow-number">
            4
          </span>

          <strong>
            GridGuard Server
          </strong>

          <small>
            Risk Engine + AI
          </small>

        </div>

      </div>


      <div className="simple-twin-footer">

        <div className="simple-legend">

          <span>
            <StatusDot state="NORMAL" />
            Normal
          </span>

          <span>
            <StatusDot state="WARNING" />
            Warning
          </span>

          <span>
            <StatusDot state="HIGH" />
            High
          </span>

          <span>
            <StatusDot state="CRITICAL" />
            Critical
          </span>

          <span>
            <StatusDot ai />
            AI Early Warning
          </span>

        </div>


        <p>
          Conceptual visualization only.
          Final sensor placement,
          electrical isolation,
          protection and installation
          require qualified electrical
          engineering validation.
        </p>

      </div>

    </section>
  );
}


export default DigitalPanelTwin;