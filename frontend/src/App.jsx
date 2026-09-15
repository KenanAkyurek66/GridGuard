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
import "./LanguageSwitch.css";

import AlarmCenter from "./AlarmCenter";
import EdgeLab from "./EdgeLab";

import PanelDetail, {
  fetchPanelDetail,
} from "./PanelDetail";

import PanelView from "./PanelView";


const API_BASE_URL =
  "http://127.0.0.1:8000";


const RISK_COLORS = {
  normal: "#55d6a4",
  warning: "#f2c94c",
  high: "#ff8a4c",
  critical: "#ff5d6c",
  unknown: "#60798b",
};


const TEXT = {
  tr: {
    operationsCenter:
      "Operasyon Merkezi",
    overview:
      "Genel Bakış",
    edgeLab:
      "Edge Lab",
    panelView:
      "Panel Görünümü",
    alarms:
      "Alarmlar",
    panels:
      "Panolar",
    lastUpdate:
      "Son Güncelleme",
    systemOnline:
      "SİSTEM ÇEVRİMİÇİ",
    systemOffline:
      "SİSTEM ÇEVRİMDIŞI",
    eyebrow:
      "ALÇAK GERİLİM DAĞITIM İZLEME",
    gridOverview:
      "Şebeke Genel Bakışı",
    subtitle:
      "Gerçek zamanlı telemetri, açıklanabilir risk analizi ve erken uyarı izleme.",
    refresh:
      "Verileri Yenile",
    connectedPanels:
      "Bağlı Panolar",
    connectedPanelsNote:
      "Kayıtlı izleme modülleri",
    activeAlarms:
      "Aktif Alarmlar",
    activeAlarmsNote:
      "Açık operasyon olayları",
    viewAlarmCenter:
      "Alarm Merkezini Gör →",
    systemHealth:
      "Sistem Sağlığı",
    checking:
      "KONTROL EDİLİYOR",
    online:
      "ÇEVRİMİÇİ",
    offline:
      "ÇEVRİMDIŞI",
    systemHealthNote:
      "GridGuard API ve izleme çekirdeği",
    normal:
      "Normal",
    warning:
      "Uyarı",
    high:
      "Yüksek",
    critical:
      "Kritik",
    unknown:
      "Bilinmiyor",
    liveStatus:
      "CANLI DURUM",
    riskDistribution:
      "Risk Dağılımı",
    noRiskData:
      "Risk verisi bulunmuyor.",
    priorityMonitoring:
      "ÖNCELİKLİ İZLEME",
    highestRiskPanels:
      "En Yüksek Riskli Panolar",
    noElevatedRisk:
      "Yükselmiş riskli pano yok",
    allNormal:
      "Değerlendirilen tüm panolar normal çalışma koşullarında.",
    assetMonitoring:
      "VARLIK İZLEME",
    panelMonitor:
      "Pano İzleme",
    panelMonitorNote:
      "Kayıtlı panoların canlı operasyon durumu.",
    showing:
      "Gösterilen",
    panelWord:
      "pano",
    clearFilters:
      "Filtreleri Temizle",
    searchPlaceholder:
      "Pano kimliği ara...",
    allStatuses:
      "Tüm Durumlar",
    tablePanel:
      "Pano",
    tableStatus:
      "Durum",
    tableRisk:
      "Risk",
    tableCurrent:
      "Akım",
    tableCableTemp:
      "Kablo Sıcaklığı",
    tableAmbient:
      "Ortam",
    tableHumidity:
      "Nem",
    tablePD:
      "PD",
    tableQuality:
      "Kalite",
    tableLastSeen:
      "Son Görülme",
    noMatchingPanels:
      "Eşleşen pano bulunamadı.",
    footer:
      "GridGuard Edge İzleme ve Erken Uyarı Sistemi",
    autoRefresh:
      "Otomatik yenileme: 5 saniye",
    panelsLabel:
      "Panolar",
  },

  en: {
    operationsCenter:
      "Operations Center",
    overview:
      "Overview",
    edgeLab:
      "Edge Lab",
    panelView:
      "Panel View",
    alarms:
      "Alarms",
    panels:
      "Panels",
    lastUpdate:
      "Last update",
    systemOnline:
      "SYSTEM ONLINE",
    systemOffline:
      "SYSTEM OFFLINE",
    eyebrow:
      "LOW VOLTAGE DISTRIBUTION MONITORING",
    gridOverview:
      "Grid Overview",
    subtitle:
      "Real-time telemetry, explainable risk analysis and early-warning monitoring.",
    refresh:
      "Refresh Data",
    connectedPanels:
      "Connected Panels",
    connectedPanelsNote:
      "Registered monitoring modules",
    activeAlarms:
      "Active Alarms",
    activeAlarmsNote:
      "Open operational incidents",
    viewAlarmCenter:
      "View Alarm Center →",
    systemHealth:
      "System Health",
    checking:
      "CHECKING",
    online:
      "ONLINE",
    offline:
      "OFFLINE",
    systemHealthNote:
      "GridGuard API and monitoring core",
    normal:
      "Normal",
    warning:
      "Warning",
    high:
      "High",
    critical:
      "Critical",
    unknown:
      "Unknown",
    liveStatus:
      "LIVE STATUS",
    riskDistribution:
      "Risk Distribution",
    noRiskData:
      "No risk data available.",
    priorityMonitoring:
      "PRIORITY MONITORING",
    highestRiskPanels:
      "Highest Risk Panels",
    noElevatedRisk:
      "No elevated-risk panels",
    allNormal:
      "All currently evaluated panels are operating within normal conditions.",
    assetMonitoring:
      "ASSET MONITORING",
    panelMonitor:
      "Panel Monitor",
    panelMonitorNote:
      "Live operational state of registered panels.",
    showing:
      "Showing",
    panelWord:
      "panels",
    clearFilters:
      "Clear Filters",
    searchPlaceholder:
      "Search panel ID...",
    allStatuses:
      "All Statuses",
    tablePanel:
      "Panel",
    tableStatus:
      "Status",
    tableRisk:
      "Risk",
    tableCurrent:
      "Current",
    tableCableTemp:
      "Cable Temp",
    tableAmbient:
      "Ambient",
    tableHumidity:
      "Humidity",
    tablePD:
      "PD",
    tableQuality:
      "Quality",
    tableLastSeen:
      "Last Seen",
    noMatchingPanels:
      "No matching panels found.",
    footer:
      "GridGuard Edge Monitoring & Early Warning System",
    autoRefresh:
      "Auto-refresh: 5 seconds",
    panelsLabel:
      "Panels",
  },
};


const STATUS_LABELS = {
  tr: {
    NORMAL: "Normal",
    WARNING: "Uyarı",
    HIGH: "Yüksek",
    CRITICAL: "Kritik",
    UNKNOWN: "Bilinmiyor",
  },
  en: {
    NORMAL: "Normal",
    WARNING: "Warning",
    HIGH: "High",
    CRITICAL: "Critical",
    UNKNOWN: "Unknown",
  },
};


const QUALITY_LABELS = {
  tr: {
    GOOD: "İyi",
    DEGRADED: "Düşük Kalite",
    BAD: "Hatalı",
    UNKNOWN: "Bilinmiyor",
  },
  en: {
    GOOD: "Good",
    DEGRADED: "Degraded",
    BAD: "Bad",
    UNKNOWN: "Unknown",
  },
};


const PRIMARY_RISK_LABELS = {
  tr: {
    NONE: "Yok",
    NO_DATA: "Veri Yok",
    THERMAL: "Termal",
    CURRENT: "Akım",
    OVERCURRENT: "Aşırı Akım",
    PARTIAL_DISCHARGE: "Kısmi Deşarj",
    ENVIRONMENT: "Çevresel",
    ARC_FLASH: "Ark Parlaması",
  },
  en: {
    NONE: "None",
    NO_DATA: "No Data",
    THERMAL: "Thermal",
    CURRENT: "Current",
    OVERCURRENT: "Overcurrent",
    PARTIAL_DISCHARGE: "Partial Discharge",
    ENVIRONMENT: "Environment",
    ARC_FLASH: "Arc Flash",
  },
};


function labelFromMap(
  map,
  language,
  value
) {
  const key =
    String(
      value ?? "UNKNOWN"
    ).toUpperCase();

  return (
    map?.[language]?.[key] ??
    String(
      value ?? "--"
    ).replaceAll(
      "_",
      " "
    )
  );
}


function App() {
  const [
    language,
    setLanguage,
  ] = useState(() => {
    const saved =
      window.localStorage.getItem(
        "gridguard-language"
      );

    return saved === "en"
      ? "en"
      : "tr";
  });

  const t =
    TEXT[language];

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


  useEffect(() => {
    window.localStorage.setItem(
      "gridguard-language",
      language
    );

    document.documentElement.lang =
      language;
  }, [language]);


  const scrollToSection =
    useCallback(
      (sectionId) => {
        const section =
          document.getElementById(
            sectionId
          );

        if (!section) {
          return;
        }

        section.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      },
      []
    );


  const loadDashboard =
    useCallback(async () => {
      try {
        const [
          summaryResponse,
          panelsResponse,
          alarmsResponse,
        ] =
          await Promise.all([
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
          panelsResponse.data
            .panels ?? []
        );

        setAlarms(
          alarmsResponse.data
            .alarms ?? []
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
            language === "tr"
              ? "Pano ayrıntıları yüklenemedi."
              : "Panel detail could not be loaded."
          );
        } finally {
          setPanelDetailLoading(
            false
          );
        }
      },
      [language]
    );


  const closePanelDetail =
    useCallback(() => {
      setSelectedPanelId(
        null
      );

      setSelectedPanelDetail(
        null
      );

      setPanelDetailError(
        null
      );

      setPanelDetailLoading(
        false
      );
    }, []);


  const filterPanelsByStatus =
    useCallback(
      (status) => {
        setPanelSearch("");
        setStatusFilter(status);

        window.setTimeout(
          () => {
            scrollToSection(
              "panel-monitor"
            );
          },
          50
        );
      },
      [scrollToSection]
    );


  const clearPanelFilters =
    useCallback(() => {
      setPanelSearch("");
      setStatusFilter("ALL");
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
            name: t.normal,
            key: "normal",
            value:
              distribution.normal,
          },
          {
            name: t.warning,
            key: "warning",
            value:
              distribution.warning,
          },
          {
            name: t.high,
            key: "high",
            value:
              distribution.high,
          },
          {
            name: t.critical,
            key: "critical",
            value:
              distribution.critical,
          },
          {
            name: t.unknown,
            key: "unknown",
            value:
              distribution.unknown,
          },
        ].filter(
          (item) =>
            item.value > 0
        ),
      [
        distribution,
        t,
      ]
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
    summary?.connected_panels ??
    0;

  const activeAlarms =
    summary?.active_alarms ??
    0;


  const panelFiltersActive =
    panelSearch.trim() !== "" ||
    statusFilter !== "ALL";


  function formatUpdateTime() {
    if (!lastUpdate) {
      return "--";
    }

    return lastUpdate
      .toLocaleTimeString(
        language === "tr"
          ? "tr-TR"
          : "en-GB",
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
      language === "tr"
        ? "tr-TR"
        : "en-GB",
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
              {t.operationsCenter}
            </p>
          </div>

        </div>


        <nav className="top-navigation">

          <button
            type="button"
            onClick={() =>
              scrollToSection(
                "overview"
              )
            }
          >
            {t.overview}
          </button>

          <button
            type="button"
            onClick={() =>
              scrollToSection(
                "edge-lab"
              )
            }
          >
            {t.edgeLab}
          </button>

          <button
            type="button"
            onClick={() =>
              scrollToSection(
                "panel-view"
              )
            }
          >
            {t.panelView}
          </button>

          <button
            type="button"
            onClick={() =>
              scrollToSection(
                "alarm-center"
              )
            }
          >
            {t.alarms}
          </button>

          <button
            type="button"
            onClick={() =>
              scrollToSection(
                "panel-monitor"
              )
            }
          >
            {t.panels}
          </button>

        </nav>


        <div className="topbar-right">

          <div className="language-switch">
            <button
              className={
                language === "tr"
                  ? "active"
                  : ""
              }
              onClick={() =>
                setLanguage("tr")
              }
              type="button"
              aria-label="Türkçe"
            >
              TR
            </button>

            <span>
              /
            </span>

            <button
              className={
                language === "en"
                  ? "active"
                  : ""
              }
              onClick={() =>
                setLanguage("en")
              }
              type="button"
              aria-label="English"
            >
              EN
            </button>
          </div>


          <div className="update-info">
            {t.lastUpdate}

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
              ? t.systemOnline
              : t.systemOffline}
          </div>

        </div>

      </header>


      <main className="dashboard">

        <section
          className="dashboard-anchor"
          id="overview"
        >

          <section className="intro">

            <div>

              <p className="eyebrow">
                {t.eyebrow}
              </p>

              <h2>
                {t.gridOverview}
              </h2>

              <p className="subtitle">
                {t.subtitle}
              </p>

            </div>


            <button
              className="refresh-button"
              onClick={
                loadDashboard
              }
              type="button"
            >
              {t.refresh}
            </button>

          </section>


          <section className="primary-grid">

            <article className="metric-card">

              <div className="metric-header">
                <span>
                  {t.connectedPanels}
                </span>

                <span className="metric-indicator online-dot" />
              </div>

              <strong>
                {loading
                  ? "--"
                  : connectedPanels}
              </strong>

              <p>
                {t.connectedPanelsNote}
              </p>

            </article>


            <button
              className="metric-card metric-action-card"
              type="button"
              onClick={() =>
                scrollToSection(
                  "alarm-center"
                )
              }
            >

              <div className="metric-header">
                <span>
                  {t.activeAlarms}
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
                {t.activeAlarmsNote}
              </p>

              <span className="metric-action-hint">
                {t.viewAlarmCenter}
              </span>

            </button>


            <article className="metric-card">

              <div className="metric-header">
                <span>
                  {t.systemHealth}
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
                  ? t.checking
                  : backendOnline
                    ? t.online
                    : t.offline}
              </strong>

              <p>
                {t.systemHealthNote}
              </p>

            </article>

          </section>


          <section className="risk-grid">

            {[
              [
                "NORMAL",
                "normal-card",
                distribution.normal,
              ],
              [
                "WARNING",
                "warning-card",
                distribution.warning,
              ],
              [
                "HIGH",
                "high-card",
                distribution.high,
              ],
              [
                "CRITICAL",
                "critical-card",
                distribution.critical,
              ],
            ].map(
              ([
                status,
                className,
                value,
              ]) => (
                <button
                  type="button"
                  className={`risk-card risk-filter-card ${className}`}
                  onClick={() =>
                    filterPanelsByStatus(
                      status
                    )
                  }
                  key={status}
                >
                  <span>
                    {labelFromMap(
                      STATUS_LABELS,
                      language,
                      status
                    ).toUpperCase()}
                  </span>

                  <strong>
                    {value}
                  </strong>
                </button>
              )
            )}

          </section>


          <section className="content-grid">

            <article className="panel-card">

              <div className="section-header">
                <div>
                  <p className="eyebrow">
                    {t.liveStatus}
                  </p>

                  <h3>
                    {t.riskDistribution}
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
                      {t.noRiskData}
                    </div>

                  )}


                  <div className="chart-center">
                    <strong>
                      {connectedPanels}
                    </strong>

                    <span>
                      {t.panelsLabel}
                    </span>
                  </div>

                </div>


                <div className="legend">

                  {[
                    [
                      "normal",
                      t.normal,
                    ],
                    [
                      "warning",
                      t.warning,
                    ],
                    [
                      "high",
                      t.high,
                    ],
                    [
                      "critical",
                      t.critical,
                    ],
                    [
                      "unknown",
                      t.unknown,
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
                    {t.priorityMonitoring}
                  </p>

                  <h3>
                    {t.highestRiskPanels}
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
                    {t.noElevatedRisk}
                  </h4>

                  <p>
                    {t.allNormal}
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
                            {labelFromMap(
                              PRIMARY_RISK_LABELS,
                              language,
                              panel.primary_risk
                            )}
                          </span>
                        </div>


                        <div className="risk-row-right">

                          <span
                            className={`risk-pill ${
                              panel.status
                                .toLowerCase()
                            }`}
                          >
                            {labelFromMap(
                              STATUS_LABELS,
                              language,
                              panel.status
                            )}
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

        </section>


        <section
          className="dashboard-anchor"
          id="edge-lab"
        >
          <EdgeLab
            language={
              language
            }
            onTelemetryProcessed={
              loadDashboard
            }
          />
        </section>


        <section
          className="dashboard-anchor"
          id="panel-view"
        >

          <PanelView
            panels={panels}
            onOpenPanel={
              openPanelDetail
            }
            language={
              language
            }
          />

        </section>


        <div
          className="dashboard-anchor"
          id="alarm-center"
        >

          <AlarmCenter
            alarms={alarms}
            onOpenPanel={
              openPanelDetail
            }
            language={
              language
            }
          />

        </div>


        <section
          className="panel-monitor dashboard-anchor"
          id="panel-monitor"
        >

          <div className="monitor-heading">

            <div>
              <p className="eyebrow">
                {t.assetMonitoring}
              </p>

              <h3>
                {t.panelMonitor}
              </h3>

              <p>
                {t.panelMonitorNote}
              </p>
            </div>


            <div className="monitor-heading-right">

              <div className="panel-count">
                {t.showing}

                <strong>
                  {
                    filteredPanels.length
                  }
                </strong>

                {t.panelWord}
              </div>


              {panelFiltersActive && (
                <button
                  className="clear-filter-button"
                  type="button"
                  onClick={
                    clearPanelFilters
                  }
                >
                  {t.clearFilters}
                </button>
              )}

            </div>

          </div>


          <div className="monitor-controls">

            <input
              type="text"
              placeholder={
                t.searchPlaceholder
              }
              value={
                panelSearch
              }
              onChange={(event) =>
                setPanelSearch(
                  event.target.value
                )
              }
            />


            <select
              value={
                statusFilter
              }
              onChange={(event) =>
                setStatusFilter(
                  event.target.value
                )
              }
            >

              <option value="ALL">
                {t.allStatuses}
              </option>

              <option value="NORMAL">
                {t.normal}
              </option>

              <option value="WARNING">
                {t.warning}
              </option>

              <option value="HIGH">
                {t.high}
              </option>

              <option value="CRITICAL">
                {t.critical}
              </option>

              <option value="UNKNOWN">
                {t.unknown}
              </option>

            </select>

          </div>


          <div className="table-wrapper">

            <table className="panel-table">

              <thead>
                <tr>
                  <th>
                    {t.tablePanel}
                  </th>
                  <th>
                    {t.tableStatus}
                  </th>
                  <th>
                    {t.tableRisk}
                  </th>
                  <th>
                    {t.tableCurrent}
                  </th>
                  <th>
                    {t.tableCableTemp}
                  </th>
                  <th>
                    {t.tableAmbient}
                  </th>
                  <th className="optional-panel-column">
                    {t.tableHumidity}
                  </th>
                  <th>
                    {t.tablePD}
                  </th>
                  <th className="optional-panel-column">
                    {t.tableQuality}
                  </th>
                  <th className="optional-panel-column">
                    {t.tableLastSeen}
                  </th>
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
                      {t.noMatchingPanels}
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
                            {labelFromMap(
                              STATUS_LABELS,
                              language,
                              panel.status
                            )}
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


                        <td className="optional-panel-column">
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


                        <td className="optional-panel-column">

                          <span
                            className={`quality-pill ${
                              (
                                panel.data_quality ??
                                "unknown"
                              ).toLowerCase()
                            }`}
                          >
                            {labelFromMap(
                              QUALITY_LABELS,
                              language,
                              panel.data_quality
                            )}
                          </span>

                        </td>


                        <td className="last-seen-cell optional-panel-column">
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
            {t.footer}
          </span>

          <span>
            {t.autoRefresh}
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
          language={
            language
          }
        />

      )}

    </div>
  );
}


export default App;
