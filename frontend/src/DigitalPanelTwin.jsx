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


function statusClass(status) {
  return String(
    status ?? "NORMAL"
  ).toLowerCase();
}


function isPositiveScore(value) {
  return Number(value ?? 0) > 0;
}


function includesAny(text, terms) {
  const value = String(
    text ?? ""
  ).toLowerCase();

  return terms.some(
    (term) =>
      value.includes(term)
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

  for (const driver of positiveDrivers) {
    const label =
      String(
        driver.label ??
        driver.feature ??
        ""
      ).toLowerCase();


    if (
      includesAny(
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
      includesAny(
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
      includesAny(
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
      includesAny(
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
      includesAny(
        label,
        [
          "arc",
        ]
      )
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
    case "thermal":
      return "THERMAL / CABLE";

    case "current":
      return "CURRENT / FEEDER";

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


function StatusDot({ status }) {
  return (
    <span
      className={`twin-status-dot ${statusClass(
        status
      )}`}
    />
  );
}


function ZoneLabel({
  label,
  status,
  aiAdvisory = false,
}) {
  return (
    <div className="twin-zone-label">

      {aiAdvisory ? (
        <span className="twin-ai-dot" />
      ) : (
        <StatusDot
          status={status}
        />
      )}


      <span>
        {label}
      </span>


      {aiAdvisory ? (
        <strong className="twin-ai-tag">
          AI EARLY
        </strong>
      ) : (
        <strong>
          {status}
        </strong>
      )}

    </div>
  );
}


function SensorCard({
  label,
  value,
  status,
  description,
  aiAdvisory = false,
}) {
  return (
    <article
      className={[
        "twin-sensor-card",
        statusClass(status),
        aiAdvisory
          ? "ai-warning"
          : "",
      ].join(" ")}
    >

      <div className="twin-sensor-header">

        {aiAdvisory ? (
          <span className="twin-ai-dot" />
        ) : (
          <StatusDot
            status={status}
          />
        )}

        <span>
          {label}
        </span>

      </div>


      <strong>
        {value}
      </strong>


      <small>
        {description}
      </small>


      {aiAdvisory && (
        <span className="sensor-ai-advisory">
          AI EARLY WARNING
        </span>
      )}

    </article>
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


  const domainStatus =
    (involved) =>
      involved
        ? overallStatus
        : "NORMAL";


  const currentStatus =
    domainStatus(
      currentInvolved
    );


  const thermalStatus =
    domainStatus(
      thermalInvolved
    );


  const environmentStatus =
    domainStatus(
      environmentInvolved
    );


  const pdStatus =
    domainStatus(
      pdInvolved
    );


  const arcStatus =
    arcInvolved
      ? "CRITICAL"
      : "NORMAL";


  const busbarStatus =
    arcInvolved
      ? "CRITICAL"
      : "NORMAL";


  const breakerStatus =
    arcInvolved
      ? "CRITICAL"
      : currentInvolved
        ? overallStatus
        : "NORMAL";


  const feederStatus =
    currentInvolved ||
    thermalInvolved
      ? overallStatus
      : "NORMAL";


  const cableStatus =
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


  const aiBusbar =
    aiArc;


  const aiBreaker =
    aiArc ||
    aiCurrent;


  const aiFeeder =
    aiCurrent ||
    aiThermal;


  const aiCable =
    aiThermal ||
    aiPd;


  const dataQuality =
    panel?.data_quality ??
    "UNKNOWN";


  const telemetryPresent =
    Boolean(
      panel?.last_seen
    );


  return (
    <section className="digital-twin">

      <div className="digital-twin-header">

        <div>

          <p className="digital-twin-eyebrow">
            VIRTUAL INSTRUMENTATION LAYER
          </p>

          <h3>
            Digital Panel Twin
          </h3>

          <span className="digital-twin-subtitle">
            Conceptual live representation
            of panel instrumentation
          </span>

        </div>


        <div
          className={`digital-twin-overall ${statusClass(
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

        </div>

      </div>


      {aiEarlyWarning && (

        <div className="digital-twin-ai-warning">

          <div className="ai-pulse" />

          <div>

            <strong>
              AI EARLY WARNING
            </strong>

            <span>
              Predictive intelligence
              detected a developing{" "}
              {aiFocusLabel(
                aiFocus
              ).toLowerCase()}{" "}
              condition while the
              deterministic panel state
              remains NORMAL.
            </span>

          </div>


          <div className="ai-focus-chip">
            {aiFocusLabel(
              aiFocus
            )}
          </div>

        </div>

      )}


      <div className="digital-twin-layout">

        <div className="panel-cabinet">

          <div className="cabinet-label">
            {panel?.panel_id ??
              "PANEL"}
          </div>


          <div
            className={[
              "panel-zone",
              "busbar-zone",
              statusClass(
                busbarStatus
              ),
              aiBusbar
                ? "ai-warning"
                : "",
            ].join(" ")}
          >

            <ZoneLabel
              label="BUSBAR"
              status={
                busbarStatus
              }
              aiAdvisory={
                aiBusbar
              }
            />


            <div className="busbar-lines">
              <span />
              <span />
              <span />
            </div>


            <div
              className={[
                "virtual-sensor",
                "arc-sensor",
                statusClass(
                  arcStatus
                ),
                aiArc
                  ? "ai-warning"
                  : "",
              ].join(" ")}
            >
              ARC
            </div>

          </div>


          <div className="panel-connection">
            <span />
            <span />
            <span />
          </div>


          <div
            className={[
              "panel-zone",
              "breaker-zone",
              statusClass(
                breakerStatus
              ),
              aiBreaker
                ? "ai-warning"
                : "",
            ].join(" ")}
          >

            <ZoneLabel
              label="BREAKER"
              status={
                breakerStatus
              }
              aiAdvisory={
                aiBreaker
              }
            />


            <div className="breaker-body">

              <div className="breaker-handle" />

              <span>
                CB
              </span>

            </div>

          </div>


          <div className="panel-connection">
            <span />
            <span />
            <span />
          </div>


          <div
            className={[
              "panel-zone",
              "feeder-zone",
              statusClass(
                feederStatus
              ),
              aiFeeder
                ? "ai-warning"
                : "",
            ].join(" ")}
          >

            <ZoneLabel
              label="FEEDER"
              status={
                feederStatus
              }
              aiAdvisory={
                aiFeeder
              }
            />


            <div className="feeder-lines">
              <span />
              <span />
              <span />
            </div>


            <div
              className={[
                "virtual-sensor",
                "current-sensor",
                statusClass(
                  currentStatus
                ),
                aiCurrent
                  ? "ai-warning"
                  : "",
              ].join(" ")}
            >
              I
            </div>

          </div>


          <div
            className={[
              "panel-zone",
              "cable-zone",
              statusClass(
                cableStatus
              ),
              aiCable
                ? "ai-warning"
                : "",
            ].join(" ")}
          >

            <ZoneLabel
              label="CABLE / LOAD"
              status={
                cableStatus
              }
              aiAdvisory={
                aiCable
              }
            />


            <div className="cable-lines">
              <span />
              <span />
              <span />
            </div>


            <div
              className={[
                "virtual-sensor",
                "temperature-sensor",
                statusClass(
                  thermalStatus
                ),
                aiThermal
                  ? "ai-warning"
                  : "",
              ].join(" ")}
            >
              °C
            </div>


            <div
              className={[
                "virtual-sensor",
                "pd-sensor",
                statusClass(
                  pdStatus
                ),
                aiPd
                  ? "ai-warning"
                  : "",
              ].join(" ")}
            >
              PD
            </div>

          </div>


          <div
            className={[
              "environment-sensor",
              statusClass(
                environmentStatus
              ),
              aiEnvironment
                ? "ai-warning"
                : "",
            ].join(" ")}
          >

            {aiEnvironment ? (
              <span className="twin-ai-dot" />
            ) : (
              <StatusDot
                status={
                  environmentStatus
                }
              />
            )}


            <span>
              AMBIENT
            </span>

            <strong>
              {formatNumber(
                panel?.ambient_temperature_c,
                1
              )} °C
            </strong>

          </div>

        </div>


        <div className="digital-twin-side">

          <div className="twin-sensor-grid">

            <SensorCard
              label="Current Measurement"
              value={`${formatNumber(
                panel?.current_a,
                1
              )} A`}
              status={
                currentStatus
              }
              aiAdvisory={
                aiCurrent
              }
              description="Electrical load measurement"
            />


            <SensorCard
              label="Cable Temperature"
              value={`${formatNumber(
                panel?.cable_temperature_c,
                1
              )} °C`}
              status={
                thermalStatus
              }
              aiAdvisory={
                aiThermal
              }
              description="Surface / cable thermal monitoring"
            />


            <SensorCard
              label="Ambient Environment"
              value={`${formatNumber(
                panel?.ambient_temperature_c,
                1
              )} °C · ${formatNumber(
                panel?.humidity_pct,
                1
              )}% RH`}
              status={
                environmentStatus
              }
              aiAdvisory={
                aiEnvironment
              }
              description="Ambient temperature and humidity"
            />


            <SensorCard
              label="Partial Discharge"
              value={formatNumber(
                panel?.pd_index,
                1
              )}
              status={
                pdStatus
              }
              aiAdvisory={
                aiPd
              }
              description="HFCT-style PD monitoring channel"
            />


            <SensorCard
              label="Arc Detection"
              value={
                panel?.arc_detected
                  ? "DETECTED"
                  : "CLEAR"
              }
              status={
                arcStatus
              }
              aiAdvisory={
                aiArc
              }
              description="Optical arc detection channel"
            />

          </div>


          <div className="edge-module">

            <div className="edge-module-header">

              <div>

                <p>
                  GRIDGUARD EDGE
                </p>

                <strong>
                  EDGE-01
                </strong>

              </div>


              <span className="edge-module-badge">
                VIRTUAL
              </span>

            </div>


            <div className="edge-module-status">

              <div>

                <span>
                  Telemetry Link
                </span>

                <strong
                  className={
                    telemetryPresent
                      ? "edge-good"
                      : "edge-bad"
                  }
                >
                  {telemetryPresent
                    ? "DATA PRESENT"
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
                      ? "edge-good"
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
                      ? "edge-good"
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
                  Predictive Decision
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


              <div>

                <span>
                  AI Focus
                </span>

                <strong
                  className={
                    aiEarlyWarning
                      ? "edge-ai"
                      : ""
                  }
                >
                  {aiEarlyWarning
                    ? aiFocusLabel(
                        aiFocus
                      )
                    : "--"}
                </strong>

              </div>

            </div>


            <div className="edge-flow">

              <span>
                SENSORS
              </span>

              <i>
                →
              </i>

              <span>
                EDGE
              </span>

              <i>
                →
              </i>

              <span>
                GRIDGUARD
              </span>

            </div>

          </div>

        </div>

      </div>


      <div className="digital-twin-footer">

        <div className="twin-legend">

          <span>
            <StatusDot status="NORMAL" />
            Normal
          </span>

          <span>
            <StatusDot status="WARNING" />
            Warning
          </span>

          <span>
            <StatusDot status="HIGH" />
            High
          </span>

          <span>
            <StatusDot status="CRITICAL" />
            Critical
          </span>

          <span className="twin-ai-legend">
            <i />
            AI Early Warning
          </span>

        </div>


        <p>
          Conceptual instrumentation view only.
          Sensor placement, isolation,
          protection, wiring and field
          installation require qualified
          electrical engineering validation.
        </p>

      </div>

    </section>
  );
}


export default DigitalPanelTwin;