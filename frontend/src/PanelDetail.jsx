import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import AiTimeline from "./AiTimeline";


const API_BASE_URL =
  "http://127.0.0.1:8000";


function formatNumber(
  value,
  digits = 1
) {
  if (
    value === null ||
    value === undefined
  ) {
    return "--";
  }

  return Number(value).toFixed(digits);
}


function formatPercent(
  value,
  digits = 1
) {
  if (
    value === null ||
    value === undefined
  ) {
    return "--";
  }

  return `${Number(value).toFixed(digits)}%`;
}


function humanize(value) {
  if (!value) {
    return "UNKNOWN";
  }

  return String(value)
    .replaceAll("_", " ");
}


function statusClass(value) {
  return String(
    value ?? "unknown"
  )
    .toLowerCase()
    .replaceAll("_", "-");
}


function formatTime(value) {
  if (!value) {
    return "--";
  }

  return new Date(
    value
  ).toLocaleTimeString(
    "tr-TR",
    {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }
  );
}


function prepareTelemetryChart(
  history = []
) {
  return history.map(
    (item) => ({
      time: formatTime(
        item.timestamp
      ),

      current:
        item.current_a,

      cableTemperature:
        item.cable_temperature_c,

      ambientTemperature:
        item.ambient_temperature_c,

      pd:
        item.pd_index,
    })
  );
}


function prepareRiskChart(
  history = []
) {
  return history.map(
    (item) => ({
      time: formatTime(
        item.timestamp
      ),

      risk:
        item.risk_score,
    })
  );
}


export async function fetchPanelDetail(
  panelId
) {
  const response = await fetch(
    `${API_BASE_URL}/dashboard/panels/${panelId}/detail?history_limit=30`
  );

  if (!response.ok) {
    throw new Error(
      "Panel detail could not be loaded."
    );
  }

  return response.json();
}


function PanelDetail({
  detail,
  loading,
  error,
  onClose,
}) {
  const panel =
    detail?.panel;

  const risk =
    detail?.risk;

  const activeAlarm =
    detail?.active_alarm;

  const intelligence =
    detail?.intelligence;

  const predictive =
    intelligence?.predictive;

  const anomaly =
    intelligence?.anomaly;

  const consensus =
    intelligence?.consensus;

  const explainability =
    intelligence?.explainability;

  const telemetryChart =
    prepareTelemetryChart(
      detail?.telemetry_history
    );

  const riskChart =
    prepareRiskChart(
      detail?.risk_history
    );


  return (
    <>

      <div
        className="detail-backdrop"
        onClick={onClose}
      />


      <aside className="detail-drawer">

        <div className="detail-header">

          <div>

            <p className="eyebrow">
              PANEL INSPECTION
            </p>

            <h2>
              {panel?.panel_id ??
                "Loading..."}
            </h2>

          </div>


          <button
            className="detail-close"
            onClick={onClose}
            type="button"
            aria-label="Close panel details"
          >
            ×
          </button>

        </div>


        {loading ? (

          <div className="detail-loading">
            Loading panel data...
          </div>

        ) : error ? (

          <div className="detail-error">
            {error}
          </div>

        ) : !detail ? (

          <div className="detail-error">
            Panel data is unavailable.
          </div>

        ) : (

          <div className="detail-content">

            <section className="detail-summary">

              <div className="detail-risk-main">

                <span>
                  Risk Score
                </span>

                <strong>
                  {risk?.risk_score ?? 0}
                </strong>

                <span
                  className={`detail-status ${
                    (
                      risk?.status ??
                      "unknown"
                    ).toLowerCase()
                  }`}
                >
                  {risk?.status ??
                    "UNKNOWN"}
                </span>

              </div>


              <div className="detail-summary-meta">

                <div>

                  <span>
                    Primary Risk
                  </span>

                  <strong>
                    {risk?.primary_risk ??
                      "NO_DATA"}
                  </strong>

                </div>


                <div>

                  <span>
                    Data Quality
                  </span>

                  <strong>
                    {panel?.data_quality ??
                      "UNKNOWN"}
                  </strong>

                </div>


                <div>

                  <span>
                    Last Seen
                  </span>

                  <strong>
                    {formatTime(
                      panel?.last_seen
                    )}
                  </strong>

                </div>

              </div>

            </section>


            <section className="detail-section intelligence-section">

              <div className="detail-section-title intelligence-title-row">

                <div>

                  <p className="eyebrow">
                    GRIDGUARD INTELLIGENCE
                  </p>

                  <h3>
                    Predictive & Anomaly Analysis
                  </h3>

                </div>

                {intelligence?.available && (

                  <span
                    className={`intelligence-status ${statusClass(
                      consensus?.status
                    )}`}
                  >
                    {humanize(
                      consensus?.status
                    )}
                  </span>

                )}

              </div>


              {!intelligence?.available ? (

                <div className="intelligence-unavailable">

                  <strong>
                    AI analysis unavailable
                  </strong>

                  <p>
                    {intelligence?.reason ??
                      "Not enough telemetry history is available for AI analysis."}
                  </p>

                </div>

              ) : (

                <>

                  <div className="intelligence-hero">

                    <div className="intelligence-consensus">

                      <span>
                        Consensus
                      </span>

                      <strong>
                        {humanize(
                          consensus?.status
                        )}
                      </strong>

                      <p>
                        {consensus?.summary ??
                          "No consensus summary available."}
                      </p>

                    </div>


                    <div className="intelligence-confidence">

                      <span>
                        Confidence
                      </span>

                      <strong>
                        {humanize(
                          consensus?.confidence
                        )}
                      </strong>

                      <small>
                        {consensus?.agreement_text ??
                          "Agreement unavailable"}
                      </small>

                    </div>

                  </div>


                  <div className="intelligence-metrics">

                    <article>

                      <span>
                        Predictive Risk
                      </span>

                      <strong>
                        {formatPercent(
                          predictive?.probability_pct,
                          2
                        )}
                      </strong>

                      <small>
                        {humanize(
                          predictive?.decision
                        )}
                      </small>

                      <div className="probability-track">

                        <div
                          className="probability-fill"
                          style={{
                            width: `${Math.min(
                              Math.max(
                                Number(
                                  predictive?.probability_pct ?? 0
                                ),
                                0
                              ),
                              100
                            )}%`,
                          }}
                        />

                      </div>

                    </article>


                    <article>

                      <span>
                        Prediction Horizon
                      </span>

                      <strong>
                        {predictive?.prediction_horizon_cycles ??
                          "--"}
                      </strong>

                      <small>
                        telemetry cycles
                      </small>

                    </article>


                    <article>

                      <span>
                        Behavioral Anomaly
                      </span>

                      <strong
                        className={
                          anomaly?.detected
                            ? "ai-alert-text"
                            : "safe-text"
                        }
                      >
                        {humanize(
                          anomaly?.level
                        )}
                      </strong>

                      <small>
                        {anomaly?.detected
                          ? "Unusual behavior detected"
                          : "Healthy pattern"}
                      </small>

                    </article>


                    <article>

                      <span>
                        AI Data Quality
                      </span>

                      <strong
                        className={
                          predictive?.data_reliable
                            ? "safe-text"
                            : "ai-hold-text"
                        }
                      >
                        {predictive?.data_reliable
                          ? "RELIABLE"
                          : "WITHHELD"}
                      </strong>

                      <small>
                        {predictive?.data_reliable
                          ? "Prediction enabled"
                          : "Awaiting trustworthy samples"}
                      </small>

                    </article>

                  </div>


                  <div className="intelligence-agreement">

                    <div>

                      <span>
                        Layer Agreement
                      </span>

                      <strong>
                        {consensus?.strong_signal_count ?? 0}/3
                      </strong>

                    </div>

                    <p>
                      {predictive?.reason ??
                        consensus?.summary}
                    </p>

                  </div>


                  <AiTimeline
                    key={panel?.panel_id}
                    panel={panel}
                    risk={risk}
                    intelligence={intelligence}
                  />


                  <div className="ai-driver-list">

                    <div className="ai-driver-heading">

                      <span>
                        TOP AI DRIVERS
                      </span>

                      <small>
                        XGBoost feature contributions
                      </small>

                    </div>

                    {(explainability?.top_drivers ?? []).length > 0 ? (

                      (explainability?.top_drivers ?? []).map(
                        (driver, index) => (

                          <div
                            className="ai-driver-row"
                            key={`${driver.feature}-${index}`}
                          >

                            <div className="ai-driver-rank">
                              {index + 1}
                            </div>

                            <div className="ai-driver-copy">

                              <strong>
                                {driver.label}
                              </strong>

                              <span>
                                Value: {formatNumber(
                                  driver.value,
                                  2
                                )}
                              </span>

                            </div>

                            <div
                              className={`ai-driver-direction ${
                                driver.direction ===
                                "INCREASES_RISK"
                                  ? "increase"
                                  : driver.direction ===
                                    "DECREASES_RISK"
                                  ? "decrease"
                                  : "neutral"
                              }`}
                            >

                              <strong>
                                {driver.contribution > 0
                                  ? "+"
                                  : ""}
                                {formatNumber(
                                  driver.contribution,
                                  3
                                )}
                              </strong>

                              <span>
                                {driver.direction ===
                                "INCREASES_RISK"
                                  ? "INCREASES RISK"
                                  : driver.direction ===
                                    "DECREASES_RISK"
                                  ? "DECREASES RISK"
                                  : "NEUTRAL"}
                              </span>

                            </div>

                          </div>

                        )
                      )

                    ) : (

                      <div className="intelligence-unavailable compact">
                        No feature-contribution data available.
                      </div>

                    )}

                  </div>


                  <div className="ai-prototype-note">

                    <strong>
                      Prototype AI Advisory
                    </strong>

                    <span>
                      {intelligence?.prototype_notice ??
                        "AI output is advisory and does not replace deterministic protection logic."}
                    </span>

                  </div>

                </>

              )}

            </section>


            <section className="detail-section">

              <div className="detail-section-title">

                <p className="eyebrow">
                  LIVE TELEMETRY
                </p>

                <h3>
                  Current Measurements
                </h3>

              </div>


              <div className="sensor-grid">

                <article>

                  <span>
                    Current
                  </span>

                  <strong>
                    {formatNumber(
                      panel?.current_a,
                      1
                    )} A
                  </strong>

                </article>


                <article>

                  <span>
                    Cable Temperature
                  </span>

                  <strong>
                    {formatNumber(
                      panel?.cable_temperature_c,
                      1
                    )} °C
                  </strong>

                </article>


                <article>

                  <span>
                    Ambient Temperature
                  </span>

                  <strong>
                    {formatNumber(
                      panel?.ambient_temperature_c,
                      1
                    )} °C
                  </strong>

                </article>


                <article>

                  <span>
                    Humidity
                  </span>

                  <strong>
                    {formatNumber(
                      panel?.humidity_pct,
                      1
                    )} %
                  </strong>

                </article>


                <article>

                  <span>
                    PD Index
                  </span>

                  <strong>
                    {formatNumber(
                      panel?.pd_index,
                      1
                    )}
                  </strong>

                </article>


                <article>

                  <span>
                    Arc Detection
                  </span>

                  <strong
                    className={
                      panel?.arc_detected
                        ? "danger-text"
                        : "safe-text"
                    }
                  >
                    {panel?.arc_detected
                      ? "DETECTED"
                      : "CLEAR"}
                  </strong>

                </article>

              </div>

            </section>


            <section className="detail-section">

              <div className="detail-section-title">

                <p className="eyebrow">
                  EXPLAINABLE RISK
                </p>

                <h3>
                  Why is this panel rated this way?
                </h3>

              </div>


              <div className="cause-list">

                {(risk?.causes ?? []).length > 0 ? (

                  (risk?.causes ?? []).map(
                    (cause, index) => (

                      <div
                        className="cause-item"
                        key={`${cause}-${index}`}
                      >

                        <span>
                          {index + 1}
                        </span>

                        <p>
                          {cause}
                        </p>

                      </div>

                    )
                  )

                ) : (

                  <div className="cause-item">

                    <span>
                      1
                    </span>

                    <p>
                      No explanation data available.
                    </p>

                  </div>

                )}

              </div>


              <div className="component-score-grid">

                <div>

                  <span>
                    Current
                  </span>

                  <strong>
                    {risk?.component_scores
                      ?.current ?? 0}
                  </strong>

                </div>


                <div>

                  <span>
                    Thermal
                  </span>

                  <strong>
                    {risk?.component_scores
                      ?.thermal ?? 0}
                  </strong>

                </div>


                <div>

                  <span>
                    Environment
                  </span>

                  <strong>
                    {risk?.component_scores
                      ?.environment ?? 0}
                  </strong>

                </div>


                <div>

                  <span>
                    Partial Discharge
                  </span>

                  <strong>
                    {risk?.component_scores
                      ?.partial_discharge ?? 0}
                  </strong>

                </div>

              </div>

            </section>


            <section className="detail-section">

              <div className="detail-section-title">

                <p className="eyebrow">
                  ALARM STATE
                </p>

                <h3>
                  Active Alarm
                </h3>

              </div>


              {activeAlarm ? (

                <div className="active-alarm-box">

                  <div className="alarm-heading">

                    <span
                      className={`detail-status ${
                        (
                          activeAlarm.severity ??
                          "unknown"
                        ).toLowerCase()
                      }`}
                    >
                      {activeAlarm.severity}
                    </span>

                    <strong>
                      Alarm #{activeAlarm.id}
                    </strong>

                  </div>


                  <p>
                    {activeAlarm.message}
                  </p>


                  <div className="alarm-meta">

                    <span>

                      Risk:{" "}

                      <strong>
                        {activeAlarm.risk_score}
                      </strong>

                    </span>


                    <span>

                      Opened:{" "}

                      <strong>
                        {formatTime(
                          activeAlarm.opened_at
                        )}
                      </strong>

                    </span>

                  </div>

                </div>

              ) : (

                <div className="no-alarm-box">

                  <span>
                    ✓
                  </span>

                  No active alarm for this panel.

                </div>

              )}

            </section>


            <section className="detail-section">

              <div className="detail-section-title">

                <p className="eyebrow">
                  TREND ANALYSIS
                </p>

                <h3>
                  Current History
                </h3>

              </div>


              <div className="detail-chart">

                {telemetryChart.length > 0 ? (

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <LineChart
                      data={telemetryChart}
                    >

                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#17303d"
                      />

                      <XAxis
                        dataKey="time"
                        stroke="#60798b"
                        tick={{
                          fontSize: 9,
                        }}
                      />

                      <YAxis
                        stroke="#60798b"
                        tick={{
                          fontSize: 9,
                        }}
                      />

                      <Tooltip />

                      <Line
                        type="monotone"
                        dataKey="current"
                        name="Current (A)"
                        stroke="#55bedf"
                        strokeWidth={2}
                        dot={false}
                      />

                    </LineChart>

                  </ResponsiveContainer>

                ) : (

                  <div className="detail-chart-empty">
                    No telemetry history available.
                  </div>

                )}

              </div>

            </section>


            <section className="detail-section">

              <div className="detail-section-title">

                <p className="eyebrow">
                  THERMAL TREND
                </p>

                <h3>
                  Temperature History
                </h3>

              </div>


              <div className="detail-chart">

                {telemetryChart.length > 0 ? (

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <LineChart
                      data={telemetryChart}
                    >

                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#17303d"
                      />

                      <XAxis
                        dataKey="time"
                        stroke="#60798b"
                        tick={{
                          fontSize: 9,
                        }}
                      />

                      <YAxis
                        stroke="#60798b"
                        tick={{
                          fontSize: 9,
                        }}
                      />

                      <Tooltip />

                      <Legend />

                      <Line
                        type="monotone"
                        dataKey="cableTemperature"
                        name="Cable °C"
                        stroke="#ff8a4c"
                        strokeWidth={2}
                        dot={false}
                      />

                      <Line
                        type="monotone"
                        dataKey="ambientTemperature"
                        name="Ambient °C"
                        stroke="#55bedf"
                        strokeWidth={2}
                        dot={false}
                      />

                    </LineChart>

                  </ResponsiveContainer>

                ) : (

                  <div className="detail-chart-empty">
                    No temperature history available.
                  </div>

                )}

              </div>

            </section>


            <section className="detail-section">

              <div className="detail-section-title">

                <p className="eyebrow">
                  RISK TREND
                </p>

                <h3>
                  Risk Score History
                </h3>

              </div>


              <div className="detail-chart">

                {riskChart.length > 0 ? (

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <LineChart
                      data={riskChart}
                    >

                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#17303d"
                      />

                      <XAxis
                        dataKey="time"
                        stroke="#60798b"
                        tick={{
                          fontSize: 9,
                        }}
                      />

                      <YAxis
                        domain={[0, 100]}
                        stroke="#60798b"
                        tick={{
                          fontSize: 9,
                        }}
                      />

                      <Tooltip />

                      <Line
                        type="monotone"
                        dataKey="risk"
                        name="Risk Score"
                        stroke="#ff5d6c"
                        strokeWidth={2}
                        dot={false}
                      />

                    </LineChart>

                  </ResponsiveContainer>

                ) : (

                  <div className="detail-chart-empty">
                    No risk history available.
                  </div>

                )}

              </div>

            </section>

          </div>

        )}

      </aside>

    </>
  );
}


export default PanelDetail;