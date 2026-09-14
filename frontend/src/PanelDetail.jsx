import { useState } from "react";

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
import "./PanelDetail.css";


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
  const [trendTab, setTrendTab] =
    useState("current");

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

  const predictiveProbability =
    predictive?.probability_pct;

  const predictiveDecision =
    predictive?.decision;

  const anomalyLabel =
    intelligence?.available
      ? humanize(
          anomaly?.level
        )
      : "UNAVAILABLE";

  const consensusLabel =
    intelligence?.available
      ? humanize(
          consensus?.status
        )
      : "UNAVAILABLE";


  function renderTrendChart() {
    if (trendTab === "current") {
      return telemetryChart.length > 0 ? (
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
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="detail-chart-empty">
          No current history available.
        </div>
      );
    }

    if (trendTab === "temperature") {
      return telemetryChart.length > 0 ? (
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
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />

            <Line
              type="monotone"
              dataKey="ambientTemperature"
              name="Ambient °C"
              stroke="#55bedf"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="detail-chart-empty">
          No temperature history available.
        </div>
      );
    }

    return riskChart.length > 0 ? (
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
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    ) : (
      <div className="detail-chart-empty">
        No risk history available.
      </div>
    );
  }


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

          <div className="detail-content pd-detail-content">

            <section className="pd-hero">

              <article className="pd-hero-card risk">

                <span>
                  Risk
                </span>

                <div className="pd-hero-value-row">

                  <strong>
                    {risk?.risk_score ?? 0}
                  </strong>

                  <span
                    className={`detail-status ${(
                      risk?.status ??
                      "unknown"
                    ).toLowerCase()}`}
                  >
                    {risk?.status ??
                      "UNKNOWN"}
                  </span>

                </div>

                <small>
                  {humanize(
                    risk?.primary_risk ??
                      "NO_DATA"
                  )}
                </small>

              </article>


              <article className="pd-hero-card consensus">

                <span>
                  Consensus
                </span>

                <strong
                  className={`pd-consensus-value ${statusClass(
                    consensus?.status
                  )}`}
                >
                  {consensusLabel}
                </strong>

                <small>
                  {intelligence?.available
                    ? humanize(
                        consensus?.confidence
                      )
                    : "AI unavailable"}
                </small>

              </article>


              <article className="pd-hero-card predictive">

                <span>
                  Predictive Risk
                </span>

                <strong>
                  {intelligence?.available
                    ? formatPercent(
                        predictiveProbability,
                        1
                      )
                    : "--"}
                </strong>

                <small>
                  {intelligence?.available
                    ? humanize(
                        predictiveDecision
                      )
                    : "AI unavailable"}
                </small>

                {intelligence?.available && (
                  <div className="pd-probability-track">
                    <div
                      className="pd-probability-fill"
                      style={{
                        width: `${Math.min(
                          Math.max(
                            Number(
                              predictiveProbability ??
                                0
                            ),
                            0
                          ),
                          100
                        )}%`,
                      }}
                    />
                  </div>
                )}

              </article>


              <article className="pd-hero-card anomaly">

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
                  {anomalyLabel}
                </strong>

                <small>
                  {intelligence?.available
                    ? anomaly?.detected
                      ? "Unusual behavior"
                      : "Healthy pattern"
                    : "AI unavailable"}
                </small>

              </article>

            </section>


            <section className="pd-context-strip">

              <div>
                <span>
                  Data Quality
                </span>

                <strong
                  className={`pd-quality ${statusClass(
                    panel?.data_quality
                  )}`}
                >
                  {panel?.data_quality ??
                    "UNKNOWN"}
                </strong>
              </div>

              <div>
                <span>
                  Primary Risk
                </span>

                <strong>
                  {humanize(
                    risk?.primary_risk ??
                      "NO_DATA"
                  )}
                </strong>
              </div>

              <div>
                <span>
                  Confidence
                </span>

                <strong>
                  {intelligence?.available
                    ? humanize(
                        consensus?.confidence
                      )
                    : "--"}
                </strong>
              </div>

              <div>
                <span>
                  Layer Agreement
                </span>

                <strong>
                  {intelligence?.available
                    ? `${consensus?.strong_signal_count ?? 0}/3`
                    : "--"}
                </strong>
              </div>

              <div>
                <span>
                  Horizon
                </span>

                <strong>
                  {intelligence?.available
                    ? `${predictive?.prediction_horizon_cycles ?? "--"} cycles`
                    : "--"}
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

            </section>


            <section className="detail-section pd-timeline-section">

              <div className="detail-section-title pd-section-heading">

                <div>
                  <p className="eyebrow">
                    GRIDGUARD INTELLIGENCE
                  </p>

                  <h3>
                    Early-Warning Timeline
                  </h3>
                </div>

                {intelligence?.available && (
                  <span
                    className={`intelligence-status ${statusClass(
                      consensus?.status
                    )}`}
                  >
                    {consensusLabel}
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
                  <AiTimeline
                    key={panel?.panel_id}
                    panel={panel}
                    risk={risk}
                    intelligence={intelligence}
                  />

                  <div className="pd-intelligence-note">

                    <div>
                      <span>
                        Current interpretation
                      </span>

                      <strong>
                        {consensus?.summary ??
                          predictive?.reason ??
                          "No interpretation available."}
                      </strong>
                    </div>

                    <p>
                      {intelligence?.prototype_notice ??
                        "AI output is advisory and does not replace deterministic protection logic."}
                    </p>

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

              <div className="sensor-grid pd-sensor-grid">

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


            <details className="detail-section pd-disclosure">

              <summary>

                <div>
                  <p className="eyebrow">
                    EXPLAINABILITY
                  </p>

                  <h3>
                    Why is the panel rated this way?
                  </h3>
                </div>

                <span className="pd-disclosure-hint">
                  Open details
                </span>

              </summary>


              <div className="pd-disclosure-body">

                <div className="pd-explanation-column">

                  <div className="pd-subheading">

                    <strong>
                      Deterministic Explanation
                    </strong>

                    <span>
                      Rule-based evidence
                    </span>

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

                </div>


                <div className="pd-explanation-column">

                  <div className="pd-subheading">

                    <strong>
                      AI Drivers
                    </strong>

                    <span>
                      XGBoost feature contributions
                    </span>

                  </div>


                  {(explainability?.top_drivers ?? []).length > 0 ? (

                    <div className="ai-driver-list pd-driver-list">

                      {(explainability?.top_drivers ?? []).map(
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
                      )}

                    </div>

                  ) : (

                    <div className="intelligence-unavailable compact">
                      No feature-contribution data available.
                    </div>

                  )}

                </div>

              </div>

            </details>


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
                      className={`detail-status ${(
                        activeAlarm.severity ??
                        "unknown"
                      ).toLowerCase()}`}
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


            <section className="detail-section pd-trends">

              <div className="pd-trend-heading">

                <div>
                  <p className="eyebrow">
                    TREND ANALYSIS
                  </p>

                  <h3>
                    Historical Signals
                  </h3>
                </div>


                <div
                  className="pd-trend-tabs"
                  role="tablist"
                  aria-label="Trend chart selection"
                >

                  <button
                    type="button"
                    className={
                      trendTab === "current"
                        ? "active"
                        : ""
                    }
                    onClick={() =>
                      setTrendTab("current")
                    }
                  >
                    Current
                  </button>

                  <button
                    type="button"
                    className={
                      trendTab === "temperature"
                        ? "active"
                        : ""
                    }
                    onClick={() =>
                      setTrendTab(
                        "temperature"
                      )
                    }
                  >
                    Temperature
                  </button>

                  <button
                    type="button"
                    className={
                      trendTab === "risk"
                        ? "active"
                        : ""
                    }
                    onClick={() =>
                      setTrendTab("risk")
                    }
                  >
                    Risk
                  </button>

                </div>

              </div>


              <div className="detail-chart pd-trend-chart">
                {renderTrendChart()}
              </div>

            </section>

          </div>

        )}

      </aside>
    </>
  );
}


export default PanelDetail;
