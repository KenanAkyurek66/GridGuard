import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import axios from "axios";

import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import "./App.css";

import AlarmCenter from "./AlarmCenter";

import PanelDetail, {
  fetchPanelDetail,
} from "./PanelDetail";


const API_BASE_URL =
  "http://127.0.0.1:8000";


const RISK_COLORS = {
  normal: "#55d6a4",
  warning: "#f2c94c",
  high: "#ff8a4c",
  critical: "#ff5d6c",
  unknown: "#60798b",
};


function App() {
  const [summary, setSummary] =
    useState(null);

  const [panels, setPanels] =
    useState([]);

  const [alarms, setAlarms] =
    useState([]);

  const [
    backendOnline,
    setBackendOnline,
  ] = useState(false);

  const [loading, setLoading] =
    useState(true);

  const [
    lastUpdate,
    setLastUpdate,
  ] = useState(null);

  const [
    panelSearch,
    setPanelSearch,
  ] = useState("");

  const [
    statusFilter,
    setStatusFilter,
  ] = useState("ALL");

  const [
    selectedPanelId,
    setSelectedPanelId,
  ] = useState(null);

  const [
    selectedPanelDetail,
    setSelectedPanelDetail,
  ] = useState(null);

  const [
    panelDetailLoading,
    setPanelDetailLoading,
  ] = useState(false);

  const [
    panelDetailError,
    setPanelDetailError,
  ] = useState(null);


  const loadDashboard =
    useCallback(async () => {
      try {
        const [
          summaryResponse,
          panelsResponse,
          alarmsResponse,
        ] = await Promise.all([
          axios.get(
            `${API_BASE_URL}/dashboard/summary`
          ),

          axios.get(
            `${API_BASE_URL}/dashboard/panels`
          ),

          axios.get(
            `${API_BASE_URL}/alarms`
          ),
        ]);

        setSummary(
          summaryResponse.data
        );

        setPanels(
          panelsResponse.data.panels ??
            []
        );

        setAlarms(
          alarmsResponse.data.alarms ??
            []
        );

        setBackendOnline(true);

        if (
          summaryResponse.data
            .generated_at
        ) {
          setLastUpdate(
            new Date(
              summaryResponse.data
                .generated_at
            )
          );
        }
      } catch (error) {
        console.error(
          "GridGuard dashboard request failed:",
          error
        );

        setBackendOnline(false);
      } finally {
        setLoading(false);
      }
    }, []);


  const openPanelDetail =
    useCallback(
      async (panelId) => {
        setSelectedPanelId(
          panelId
        );

        setSelectedPanelDetail(
          null
        );

        setPanelDetailError(
          null
        );

        setPanelDetailLoading(
          true
        );

        try {
          const data =
            await fetchPanelDetail(
              panelId
            );

          setSelectedPanelDetail(
            data
          );
        } catch (error) {
          console.error(
            "Panel detail request failed:",
            error
          );

          setPanelDetailError(
            "Panel detail could not be loaded."
          );
        } finally {
          setPanelDetailLoading(
            false
          );
        }
      },
      []
    );


  const closePanelDetail =
    useCallback(() => {
      setSelectedPanelId(null);

      setSelectedPanelDetail(
        null
      );

      setPanelDetailError(null);

      setPanelDetailLoading(
        false
      );
    }, []);


  useEffect(() => {
    loadDashboard();

    const interval =
      setInterval(
        loadDashboard,
        5000
      );

    return () =>
      clearInterval(interval);
  }, [loadDashboard]);


  useEffect(() => {
    if (!selectedPanelId) {
      return undefined;
    }

    const interval =
      setInterval(
        async () => {
          try {
            const data =
              await fetchPanelDetail(
                selectedPanelId
              );

            setSelectedPanelDetail(
              data
            );

            setPanelDetailError(
              null
            );
          } catch (error) {
            console.error(
              "Panel detail refresh failed:",
              error
            );
          }
        },
        5000
      );

    return () =>
      clearInterval(interval);
  }, [selectedPanelId]);


  useEffect(() => {
    function handleEscape(
      event
    ) {
      if (
        event.key === "Escape" &&
        selectedPanelId
      ) {
        closePanelDetail();
      }
    }

    window.addEventListener(
      "keydown",
      handleEscape
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleEscape
      );
    };
  }, [
    selectedPanelId,
    closePanelDetail,
  ]);


  const distribution =
    summary?.risk_distribution ?? {
      normal: 0,
      warning: 0,
      high: 0,
      critical: 0,
      unknown: 0,
    };


  const riskChartData =
    useMemo(
      () =>
        [
          {
            name: "Normal",
            key: "normal",
            value:
              distribution.normal,
          },
          {
            name: "Warning",
            key: "warning",
            value:
              distribution.warning,
          },
          {
            name: "High",
            key: "high",
            value:
              distribution.high,
          },
          {
            name: "Critical",
            key: "critical",
            value:
              distribution.critical,
          },
          {
            name: "Unknown",
            key: "unknown",
            value:
              distribution.unknown,
          },
        ].filter(
          (item) =>
            item.value > 0
        ),
      [distribution]
    );


  const elevatedRiskPanels =
    useMemo(
      () =>
        (
          summary
            ?.highest_risk_panels ??
          []
        ).filter(
          (panel) =>
            panel.risk_score > 0 &&
            panel.status !==
              "NORMAL" &&
            panel.status !==
              "UNKNOWN"
        ),
      [summary]
    );


  const filteredPanels =
    useMemo(() => {
      const searchValue =
        panelSearch
          .trim()
          .toLowerCase();

      return panels.filter(
        (panel) => {
          const matchesSearch =
            !searchValue ||
            panel.panel_id
              .toLowerCase()
              .includes(
                searchValue
              );

          const matchesStatus =
            statusFilter ===
              "ALL" ||
            panel.status ===
              statusFilter;

          return (
            matchesSearch &&
            matchesStatus
          );
        }
      );
    }, [
      panels,
      panelSearch,
      statusFilter,
    ]);


  const connectedPanels =
    summary?.connected_panels ?? 0;

  const activeAlarms =
    summary?.active_alarms ?? 0;


  function formatUpdateTime() {
    if (!lastUpdate) {
      return "--";
    }

    return lastUpdate
      .toLocaleTimeString(
        "tr-TR",
        {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }
      );
  }


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

    return Number(
      value
    ).toFixed(digits);
  }


  function formatLastSeen(
    value
  ) {
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


  return (
    <div className="app-shell">

      <header className="topbar">

        <div className="brand-row">

          <div className="brand-mark">
            G
          </div>

          <div>

            <h1>
              GridGuard
            </h1>

            <p>
              Operations Center
            </p>

          </div>

        </div>


        <div className="topbar-right">

          <div className="update-info">

            Last update

            <strong>
              {formatUpdateTime()}
            </strong>

          </div>


          <div
            className={`system-badge ${
              backendOnline
                ? "online"
                : "offline"
            }`}
          >

            <span className="status-dot" />

            {backendOnline
              ? "SYSTEM ONLINE"
              : "SYSTEM OFFLINE"}

          </div>

        </div>

      </header>


      <main className="dashboard">

        <section className="intro">

          <div>

            <p className="eyebrow">
              LOW VOLTAGE DISTRIBUTION MONITORING
            </p>

            <h2>
              Grid Overview
            </h2>

            <p className="subtitle">
              Real-time telemetry,
              explainable risk analysis
              and early-warning monitoring.
            </p>

          </div>


          <button
            className="refresh-button"
            onClick={loadDashboard}
            type="button"
          >
            Refresh Data
          </button>

        </section>


        <section className="primary-grid">

          <article className="metric-card">

            <div className="metric-header">

              <span>
                Connected Panels
              </span>

              <span
                className="
                  metric-indicator
                  online-dot
                "
              />

            </div>

            <strong>
              {loading
                ? "--"
                : connectedPanels}
            </strong>

            <p>
              Registered monitoring modules
            </p>

          </article>


          <article className="metric-card">

            <div className="metric-header">

              <span>
                Active Alarms
              </span>

              <span
                className={`metric-indicator ${
                  activeAlarms > 0
                    ? "alarm-dot"
                    : "online-dot"
                }`}
              />

            </div>

            <strong>
              {loading
                ? "--"
                : activeAlarms}
            </strong>

            <p>
              Open operational incidents
            </p>

          </article>


          <article className="metric-card">

            <div className="metric-header">

              <span>
                System Health
              </span>

            </div>

            <strong
              className={
                backendOnline
                  ? "health-online"
                  : "health-offline"
              }
            >
              {loading
                ? "CHECKING"
                : backendOnline
                  ? "ONLINE"
                  : "OFFLINE"}
            </strong>

            <p>
              GridGuard API and
              monitoring core
            </p>

          </article>

        </section>


        <section className="risk-grid">

          <article
            className="
              risk-card
              normal-card
            "
          >

            <span>
              NORMAL
            </span>

            <strong>
              {distribution.normal}
            </strong>

          </article>


          <article
            className="
              risk-card
              warning-card
            "
          >

            <span>
              WARNING
            </span>

            <strong>
              {distribution.warning}
            </strong>

          </article>


          <article
            className="
              risk-card
              high-card
            "
          >

            <span>
              HIGH
            </span>

            <strong>
              {distribution.high}
            </strong>

          </article>


          <article
            className="
              risk-card
              critical-card
            "
          >

            <span>
              CRITICAL
            </span>

            <strong>
              {distribution.critical}
            </strong>

          </article>

        </section>


        <section className="content-grid">

          <article className="panel-card">

            <div className="section-header">

              <div>

                <p className="eyebrow">
                  LIVE STATUS
                </p>

                <h3>
                  Risk Distribution
                </h3>

              </div>

            </div>


            <div className="risk-chart-layout">

              <div className="chart-container">

                {riskChartData.length >
                0 ? (

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <PieChart>

                      <Pie
                        data={
                          riskChartData
                        }
                        dataKey="value"
                        nameKey="name"
                        innerRadius="63%"
                        outerRadius="86%"
                        paddingAngle={2}
                      >

                        {riskChartData.map(
                          (entry) => (

                            <Cell
                              key={
                                entry.key
                              }
                              fill={
                                RISK_COLORS[
                                  entry.key
                                ]
                              }
                            />

                          )
                        )}

                      </Pie>

                      <Tooltip />

                    </PieChart>

                  </ResponsiveContainer>

                ) : (

                  <div className="empty-state">
                    No risk data available.
                  </div>

                )}


                <div className="chart-center">

                  <strong>
                    {connectedPanels}
                  </strong>

                  <span>
                    Panels
                  </span>

                </div>

              </div>


              <div className="legend">

                {[
                  [
                    "normal",
                    "Normal",
                  ],
                  [
                    "warning",
                    "Warning",
                  ],
                  [
                    "high",
                    "High",
                  ],
                  [
                    "critical",
                    "Critical",
                  ],
                  [
                    "unknown",
                    "Unknown",
                  ],
                ].map(
                  ([
                    key,
                    label,
                  ]) => (

                    <div
                      className="legend-row"
                      key={key}
                    >

                      <div>

                        <span
                          className="legend-dot"
                          style={{
                            background:
                              RISK_COLORS[
                                key
                              ],
                          }}
                        />

                        {label}

                      </div>

                      <strong>
                        {
                          distribution[
                            key
                          ]
                        }
                      </strong>

                    </div>

                  )
                )}

              </div>

            </div>

          </article>


          <article className="panel-card">

            <div className="section-header">

              <div>

                <p className="eyebrow">
                  PRIORITY MONITORING
                </p>

                <h3>
                  Highest Risk Panels
                </h3>

              </div>

            </div>


            {elevatedRiskPanels.length ===
            0 ? (

              <div className="healthy-state">

                <div className="healthy-icon">
                  ✓
                </div>

                <h4>
                  No elevated-risk panels
                </h4>

                <p>
                  All currently evaluated
                  panels are operating
                  within normal conditions.
                </p>

              </div>

            ) : (

              <div className="risk-list">

                {elevatedRiskPanels.map(
                  (panel) => (

                    <button
                      className="risk-row risk-row-button"
                      key={
                        panel.panel_id
                      }
                      onClick={() =>
                        openPanelDetail(
                          panel.panel_id
                        )
                      }
                      type="button"
                    >

                      <div>

                        <strong>
                          {
                            panel.panel_id
                          }
                        </strong>

                        <span>
                          {
                            panel.primary_risk
                          }
                        </span>

                      </div>


                      <div className="risk-row-right">

                        <span
                          className={`risk-pill ${
                            panel.status
                              .toLowerCase()
                          }`}
                        >
                          {
                            panel.status
                          }
                        </span>

                        <strong>
                          {
                            panel.risk_score
                          }
                        </strong>

                      </div>

                    </button>

                  )
                )}

              </div>

            )}

          </article>

        </section>


        <AlarmCenter
          alarms={alarms}
          onOpenPanel={
            openPanelDetail
          }
        />


        <section className="panel-monitor">

          <div className="monitor-heading">

            <div>

              <p className="eyebrow">
                ASSET MONITORING
              </p>

              <h3>
                Panel Monitor
              </h3>

              <p>
                Live operational state
                of registered panels.
              </p>

            </div>


            <div className="panel-count">

              Showing

              <strong>
                {
                  filteredPanels.length
                }
              </strong>

              panels

            </div>

          </div>


          <div className="monitor-controls">

            <input
              type="text"
              placeholder="Search panel ID..."
              value={panelSearch}
              onChange={(event) =>
                setPanelSearch(
                  event.target.value
                )
              }
            />


            <select
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(
                  event.target.value
                )
              }
            >

              <option value="ALL">
                All Statuses
              </option>

              <option value="NORMAL">
                Normal
              </option>

              <option value="WARNING">
                Warning
              </option>

              <option value="HIGH">
                High
              </option>

              <option value="CRITICAL">
                Critical
              </option>

              <option value="UNKNOWN">
                Unknown
              </option>

            </select>

          </div>


          <div className="table-wrapper">

            <table className="panel-table">

              <thead>

                <tr>
                  <th>Panel</th>
                  <th>Status</th>
                  <th>Risk</th>
                  <th>Current</th>
                  <th>Cable Temp</th>
                  <th>Ambient</th>
                  <th>Humidity</th>
                  <th>PD</th>
                  <th>Quality</th>
                  <th>Last Seen</th>
                </tr>

              </thead>


              <tbody>

                {filteredPanels.length ===
                0 ? (

                  <tr>

                    <td
                      colSpan="10"
                      className="no-panel-results"
                    >
                      No matching panels found.
                    </td>

                  </tr>

                ) : (

                  filteredPanels.map(
                    (panel) => (

                      <tr
                        key={
                          panel.panel_id
                        }
                        className={`clickable-panel-row ${
                          panel.has_open_alarm
                            ? "alarm-row"
                            : ""
                        }`}
                        onClick={() =>
                          openPanelDetail(
                            panel.panel_id
                          )
                        }
                      >

                        <td>

                          <div className="panel-id-cell">

                            <span
                              className={`panel-state-dot ${
                                panel.status
                                  .toLowerCase()
                              }`}
                            />

                            <strong>
                              {
                                panel.panel_id
                              }
                            </strong>

                          </div>

                        </td>


                        <td>

                          <span
                            className={`table-status ${
                              panel.status
                                .toLowerCase()
                            }`}
                          >
                            {
                              panel.status
                            }
                          </span>

                        </td>


                        <td className="risk-score-cell">
                          {
                            panel.risk_score
                          }
                        </td>


                        <td>
                          {formatNumber(
                            panel.current_a,
                            1
                          )} A
                        </td>


                        <td>
                          {formatNumber(
                            panel.cable_temperature_c,
                            1
                          )} °C
                        </td>


                        <td>
                          {formatNumber(
                            panel.ambient_temperature_c,
                            1
                          )} °C
                        </td>


                        <td>
                          {formatNumber(
                            panel.humidity_pct,
                            1
                          )} %
                        </td>


                        <td>
                          {formatNumber(
                            panel.pd_index,
                            1
                          )}
                        </td>


                        <td>

                          <span
                            className={`quality-pill ${
                              (
                                panel.data_quality ??
                                "unknown"
                              ).toLowerCase()
                            }`}
                          >
                            {
                              panel.data_quality ??
                              "UNKNOWN"
                            }
                          </span>

                        </td>


                        <td className="last-seen-cell">
                          {formatLastSeen(
                            panel.last_seen
                          )}
                        </td>

                      </tr>

                    )
                  )

                )}

              </tbody>

            </table>

          </div>

        </section>


        <footer className="dashboard-footer">

          <span>
            GridGuard Edge Monitoring
            & Early Warning System
          </span>

          <span>
            Auto-refresh: 5 seconds
          </span>

        </footer>

      </main>


      {selectedPanelId && (

        <PanelDetail
          detail={
            selectedPanelDetail
          }
          loading={
            panelDetailLoading
          }
          error={
            panelDetailError
          }
          onClose={
            closePanelDetail
          }
        />

      )}

    </div>
  );
}


export default App;