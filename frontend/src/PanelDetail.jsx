import {
  useMemo,
  useState,
} from "react";

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


const TEXT = {
  tr: {
    panelInspection:
      "PANO İNCELEMESİ",
    loading:
      "Yükleniyor...",
    close:
      "Pano ayrıntılarını kapat",
    loadingPanel:
      "Pano verileri yükleniyor...",
    unavailable:
      "Pano verileri kullanılamıyor.",
    risk:
      "Risk",
    consensus:
      "Ortak Karar",
    predictiveRisk:
      "Tahminsel Risk",
    behavioralAnomaly:
      "Davranışsal Anomali",
    aiUnavailable:
      "AI kullanılamıyor",
    unusualBehavior:
      "Olağandışı davranış",
    healthyPattern:
      "Sağlıklı örüntü",
    dataQuality:
      "Veri Kalitesi",
    primaryRisk:
      "Birincil Risk",
    confidence:
      "Güven",
    layerAgreement:
      "Katman Uyumu",
    horizon:
      "Tahmin Ufku",
    cycles:
      "çevrim",
    lastSeen:
      "Son Görülme",
    intelligence:
      "GRIDGUARD ZEKA KATMANI",
    earlyTimeline:
      "Erken Uyarı Zaman Çizelgesi",
    aiAnalysisUnavailable:
      "AI analizi kullanılamıyor",
    aiNotEnough:
      "AI analizi için yeterli telemetri geçmişi bulunmuyor.",
    currentInterpretation:
      "Güncel Yorum",
    noInterpretation:
      "Yorum bulunmuyor.",
    prototypeNotice:
      "AI çıktısı danışman niteliktedir ve deterministik koruma mantığının yerini almaz.",
    liveTelemetry:
      "CANLI TELEMETRİ",
    currentMeasurements:
      "Güncel Ölçümler",
    current:
      "Akım",
    cableTemperature:
      "Kablo Sıcaklığı",
    ambientTemperature:
      "Ortam Sıcaklığı",
    humidity:
      "Nem",
    pdIndex:
      "PD İndeksi",
    arcDetection:
      "Ark Algılama",
    detected:
      "ALGILANDI",
    clear:
      "TEMİZ",
    explainability:
      "AÇIKLANABİLİRLİK",
    whyRated:
      "Pano neden bu şekilde değerlendiriliyor?",
    openDetails:
      "Ayrıntıları Aç",
    deterministicExplanation:
      "Deterministik Açıklama",
    ruleEvidence:
      "Kural tabanlı kanıt",
    noExplanation:
      "Açıklama verisi bulunmuyor.",
    thermal:
      "Termal",
    environment:
      "Çevresel",
    partialDischarge:
      "Kısmi Deşarj",
    aiDrivers:
      "AI Etkenleri",
    xgboost:
      "XGBoost özellik katkıları",
    value:
      "Değer",
    increasesRisk:
      "RİSKİ ARTIRIR",
    decreasesRisk:
      "RİSKİ AZALTIR",
    neutral:
      "NÖTR",
    noContribution:
      "Özellik katkısı verisi bulunmuyor.",
    alarmState:
      "ALARM DURUMU",
    activeAlarm:
      "Aktif Alarm",
    alarm:
      "Alarm",
    opened:
      "Açılış",
    noActiveAlarm:
      "Bu pano için aktif alarm yok.",
    trendAnalysis:
      "TREND ANALİZİ",
    historicalSignals:
      "Geçmiş Sinyaller",
    temperature:
      "Sıcaklık",
    noCurrentHistory:
      "Akım geçmişi bulunmuyor.",
    noTemperatureHistory:
      "Sıcaklık geçmişi bulunmuyor.",
    noRiskHistory:
      "Risk geçmişi bulunmuyor.",
    riskScore:
      "Risk Skoru",
    cable:
      "Kablo",
    ambient:
      "Ortam",
  },

  en: {
    panelInspection:
      "PANEL INSPECTION",
    loading:
      "Loading...",
    close:
      "Close panel details",
    loadingPanel:
      "Loading panel data...",
    unavailable:
      "Panel data is unavailable.",
    risk:
      "Risk",
    consensus:
      "Consensus",
    predictiveRisk:
      "Predictive Risk",
    behavioralAnomaly:
      "Behavioral Anomaly",
    aiUnavailable:
      "AI unavailable",
    unusualBehavior:
      "Unusual behavior",
    healthyPattern:
      "Healthy pattern",
    dataQuality:
      "Data Quality",
    primaryRisk:
      "Primary Risk",
    confidence:
      "Confidence",
    layerAgreement:
      "Layer Agreement",
    horizon:
      "Horizon",
    cycles:
      "cycles",
    lastSeen:
      "Last Seen",
    intelligence:
      "GRIDGUARD INTELLIGENCE",
    earlyTimeline:
      "Early-Warning Timeline",
    aiAnalysisUnavailable:
      "AI analysis unavailable",
    aiNotEnough:
      "Not enough telemetry history is available for AI analysis.",
    currentInterpretation:
      "Current interpretation",
    noInterpretation:
      "No interpretation available.",
    prototypeNotice:
      "AI output is advisory and does not replace deterministic protection logic.",
    liveTelemetry:
      "LIVE TELEMETRY",
    currentMeasurements:
      "Current Measurements",
    current:
      "Current",
    cableTemperature:
      "Cable Temperature",
    ambientTemperature:
      "Ambient Temperature",
    humidity:
      "Humidity",
    pdIndex:
      "PD Index",
    arcDetection:
      "Arc Detection",
    detected:
      "DETECTED",
    clear:
      "CLEAR",
    explainability:
      "EXPLAINABILITY",
    whyRated:
      "Why is the panel rated this way?",
    openDetails:
      "Open details",
    deterministicExplanation:
      "Deterministic Explanation",
    ruleEvidence:
      "Rule-based evidence",
    noExplanation:
      "No explanation data available.",
    thermal:
      "Thermal",
    environment:
      "Environment",
    partialDischarge:
      "Partial Discharge",
    aiDrivers:
      "AI Drivers",
    xgboost:
      "XGBoost feature contributions",
    value:
      "Value",
    increasesRisk:
      "INCREASES RISK",
    decreasesRisk:
      "DECREASES RISK",
    neutral:
      "NEUTRAL",
    noContribution:
      "No feature-contribution data available.",
    alarmState:
      "ALARM STATE",
    activeAlarm:
      "Active Alarm",
    alarm:
      "Alarm",
    opened:
      "Opened",
    noActiveAlarm:
      "No active alarm for this panel.",
    trendAnalysis:
      "TREND ANALYSIS",
    historicalSignals:
      "Historical Signals",
    temperature:
      "Temperature",
    noCurrentHistory:
      "No current history available.",
    noTemperatureHistory:
      "No temperature history available.",
    noRiskHistory:
      "No risk history available.",
    riskScore:
      "Risk Score",
    cable:
      "Cable",
    ambient:
      "Ambient",
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


const CONSENSUS_LABELS = {
  tr: {
    OBSERVE: "İzle",
    EARLY_WARNING: "Erken Uyarı",
    CRITICAL: "Kritik",
    HOLD_UNRELIABLE: "Güvenilmez Veriyi Tut",
    UNKNOWN: "Bilinmiyor",
  },
  en: {
    OBSERVE: "Observe",
    EARLY_WARNING: "Early Warning",
    CRITICAL: "Critical",
    HOLD_UNRELIABLE: "Hold Unreliable",
    UNKNOWN: "Unknown",
  },
};


const CONFIDENCE_LABELS = {
  tr: {
    LOW: "Düşük",
    MEDIUM: "Orta",
    HIGH: "Yüksek",
    VERY_HIGH: "Çok Yüksek",
    UNKNOWN: "Bilinmiyor",
  },
  en: {
    LOW: "Low",
    MEDIUM: "Medium",
    HIGH: "High",
    VERY_HIGH: "Very High",
    UNKNOWN: "Unknown",
  },
};


const PREDICTION_LABELS = {
  tr: {
    SAFE: "Güvenli",
    HOLD: "İzlemede",
    ESCALATION: "Yükselt",
    UNKNOWN: "Bilinmiyor",
  },
  en: {
    SAFE: "Safe",
    HOLD: "Hold",
    ESCALATION: "Escalation",
    UNKNOWN: "Unknown",
  },
};


const ANOMALY_LABELS = {
  tr: {
    NORMAL: "Normal",
    LOW: "Düşük",
    MEDIUM: "Orta",
    HIGH: "Yüksek",
    UNKNOWN: "Bilinmiyor",
  },
  en: {
    NORMAL: "Normal",
    LOW: "Low",
    MEDIUM: "Medium",
    HIGH: "High",
    UNKNOWN: "Unknown",
  },
};


const DRIVER_LABELS = {
  tr: {
    current_a: "Akım",
    cable_temperature_c:
      "Kablo Sıcaklığı",
    ambient_temperature_c:
      "Ortam Sıcaklığı",
    humidity_pct:
      "Nem",
    pd_index:
      "PD İndeksi",
    arc_detected:
      "Ark Algılama",
    current_delta:
      "Akım Değişimi",
    temperature_delta:
      "Sıcaklık Değişimi",
    cable_temp_delta:
      "Kablo Sıcaklığı Değişimi",
  },
  en: {},
};


const BACKEND_TEXT_TR = {
  "No telemetry data available.":
    "Telemetri verisi bulunmuyor.",
  "Arc flash event detected.":
    "Ark parlaması olayı algılandı.",
  "Immediate operator attention required.":
    "Acil operatör müdahalesi gerekiyor.",
  "Current increased more than 35% above recent baseline.":
    "Akım, yakın dönem baz değerinin %35'ten fazla üzerine çıktı.",
  "Current increased more than 20% above recent baseline.":
    "Akım, yakın dönem baz değerinin %20'den fazla üzerine çıktı.",
  "Current is rising above recent baseline.":
    "Akım, yakın dönem baz değerinin üzerine yükseliyor.",
  "Cable temperature is extremely high.":
    "Kablo sıcaklığı son derece yüksek.",
  "Cable temperature is critically elevated.":
    "Kablo sıcaklığı kritik düzeyde yükselmiş.",
  "Cable temperature is elevated.":
    "Kablo sıcaklığı yükselmiş.",
  "Cable-to-ambient thermal delta is very high.":
    "Kablo ile ortam arasındaki sıcaklık farkı çok yüksek.",
  "Abnormal cable-to-ambient thermal delta detected.":
    "Kablo ile ortam arasında anormal sıcaklık farkı algılandı.",
  "Cable temperature is rising rapidly while ambient temperature remains relatively stable.":
    "Ortam sıcaklığı görece kararlı kalırken kablo sıcaklığı hızla yükseliyor.",
  "Very high humidity detected.":
    "Çok yüksek nem algılandı.",
  "High humidity detected.":
    "Yüksek nem algılandı.",
  "Partial discharge activity is very high.":
    "Kısmi deşarj etkinliği çok yüksek.",
  "Elevated partial discharge activity detected.":
    "Yükselmiş kısmi deşarj etkinliği algılandı.",
  "Partial discharge activity is above normal range.":
    "Kısmi deşarj etkinliği normal aralığın üzerinde.",
  "Partial discharge activity shows a strong rising trend.":
    "Kısmi deşarj etkinliği güçlü bir yükseliş eğilimi gösteriyor.",
  "Partial discharge activity is increasing over time.":
    "Kısmi deşarj etkinliği zaman içinde artıyor.",
  "Severe thermal escalation pattern detected.":
    "Şiddetli termal yükseliş örüntüsü algılandı.",
  "Rising partial discharge pattern detected.":
    "Yükselen kısmi deşarj örüntüsü algılandı.",
  "Severe partial discharge escalation pattern detected.":
    "Şiddetli kısmi deşarj yükseliş örüntüsü algılandı.",
  "No significant anomaly detected.":
    "Belirgin bir anomali algılanmadı.",
  "No strong signals are currently present.":
    "Şu anda güçlü bir risk sinyali bulunmuyor.",
  "Deterministic risk is critical and has priority over AI advisory output.":
    "Deterministik risk kritiktir ve AI danışman çıktısına göre önceliklidir.",
  "AI output is advisory and does not replace deterministic protection logic.":
    "AI çıktısı danışman niteliktedir ve deterministik koruma mantığının yerini almaz.",
  "Insufficient trusted telemetry history for AI analysis.":
    "AI analizi için yeterli güvenilir telemetri geçmişi bulunmuyor.",
  "Unusual behavior detected without confirmed future escalation.":
    "Gelecekte kesin bir risk artışı doğrulanmadan olağandışı davranış algılandı.",
  "ML models are trained on synthetic prototype telemetry and require field calibration before production use.":
    "Makine öğrenmesi modelleri sentetik prototip telemetrisiyle eğitilmiştir; gerçek kullanım öncesinde saha kalibrasyonu gerekir.",
  "Unusual behavior detected.":
    "Olağandışı davranış algılandı.",
  "No unusual behavior detected.":
    "Olağandışı davranış algılanmadı.",
};


function mapLabel(
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

  return `${Number(
    value
  ).toFixed(digits)}%`;
}


function statusClass(value) {
  return String(
    value ?? "unknown"
  )
    .toLowerCase()
    .replaceAll(
      "_",
      "-"
    );
}


function formatTime(
  value,
  language
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


function translateBackendText(
  value,
  language
) {
  if (!value) {
    return "";
  }

  if (
    language !== "tr"
  ) {
    return value;
  }

  let translated =
    BACKEND_TEXT_TR[
      value
    ] ??
    String(value);

  for (
    const [
      source,
      target,
    ] of Object.entries(
      BACKEND_TEXT_TR
    )
  ) {
    translated =
      translated.replaceAll(
        source,
        target
      );
  }

  return translated
    .replace(
      /cable temperature/gi,
      "kablo sıcaklığı"
    )
    .replace(
      /partial discharge/gi,
      "kısmi deşarj"
    )
    .replace(
      /ambient temperature/gi,
      "ortam sıcaklığı"
    )
    .replace(
      /humidity/gi,
      "nem"
    )
    .replace(
      /current/gi,
      "akım"
    );
}


function driverLabel(
  driver,
  language
) {
  if (
    language === "en"
  ) {
    return (
      driver?.label ??
      String(
        driver?.feature ??
        "--"
      ).replaceAll(
        "_",
        " "
      )
    );
  }

  const feature =
    driver?.feature;

  if (
    feature &&
    DRIVER_LABELS.tr[
      feature
    ]
  ) {
    return DRIVER_LABELS.tr[
      feature
    ];
  }

  const original =
    driver?.label ??
    String(
      feature ?? "--"
    ).replaceAll(
      "_",
      " "
    );

  return String(original)
    .replace(
      /Cable Temperature/gi,
      "Kablo Sıcaklığı"
    )
    .replace(
      /Ambient Temperature/gi,
      "Ortam Sıcaklığı"
    )
    .replace(
      /Partial Discharge/gi,
      "Kısmi Deşarj"
    )
    .replace(
      /Current/gi,
      "Akım"
    )
    .replace(
      /Humidity/gi,
      "Nem"
    );
}


function prepareTelemetryChart(
  history = [],
  language
) {
  return history.map(
    (item) => ({
      time: formatTime(
        item.timestamp,
        language
      ),
      current:
        item.current_a,
      cableTemperature:
        item
          .cable_temperature_c,
      ambientTemperature:
        item
          .ambient_temperature_c,
      pd:
        item.pd_index,
    })
  );
}


function prepareRiskChart(
  history = [],
  language
) {
  return history.map(
    (item) => ({
      time: formatTime(
        item.timestamp,
        language
      ),
      risk:
        item.risk_score,
    })
  );
}


export async function fetchPanelDetail(
  panelId
) {
  const response =
    await fetch(
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
  language = "tr",
}) {
  const safeLanguage =
    language === "en"
      ? "en"
      : "tr";

  const t =
    TEXT[safeLanguage];

  const [
    trendTab,
    setTrendTab,
  ] = useState(
    "current"
  );

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
    useMemo(
      () =>
        prepareTelemetryChart(
          detail?.telemetry_history ??
            [],
          safeLanguage
        ),
      [
        detail
          ?.telemetry_history,
        safeLanguage,
      ]
    );

  const riskChart =
    useMemo(
      () =>
        prepareRiskChart(
          detail?.risk_history ??
            [],
          safeLanguage
        ),
      [
        detail?.risk_history,
        safeLanguage,
      ]
    );

  const predictiveProbability =
    predictive?.probability_pct;

  const predictiveDecision =
    predictive?.decision;

  const anomalyLabel =
    intelligence?.available
      ? mapLabel(
          ANOMALY_LABELS,
          safeLanguage,
          anomaly?.level
        )
      : t.aiUnavailable;

  const consensusLabel =
    intelligence?.available
      ? mapLabel(
          CONSENSUS_LABELS,
          safeLanguage,
          consensus?.status
        )
      : t.aiUnavailable;


  function renderTrendChart() {
    if (
      trendTab ===
      "current"
    ) {
      return telemetryChart
        .length > 0 ? (
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <LineChart
            data={
              telemetryChart
            }
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
              name={`${t.current} (A)`}
              stroke="#55bedf"
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={
                false
              }
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="detail-chart-empty">
          {
            t.noCurrentHistory
          }
        </div>
      );
    }

    if (
      trendTab ===
      "temperature"
    ) {
      return telemetryChart
        .length > 0 ? (
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <LineChart
            data={
              telemetryChart
            }
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
              name={`${t.cable} °C`}
              stroke="#ff8a4c"
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={
                false
              }
            />

            <Line
              type="monotone"
              dataKey="ambientTemperature"
              name={`${t.ambient} °C`}
              stroke="#55bedf"
              strokeWidth={2}
              dot={false}
              isAnimationActive={
                false
              }
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="detail-chart-empty">
          {
            t.noTemperatureHistory
          }
        </div>
      );
    }

    return riskChart.length >
    0 ? (
      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <LineChart
          data={
            riskChart
          }
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
            domain={[
              0,
              100,
            ]}
            stroke="#60798b"
            tick={{
              fontSize: 9,
            }}
          />

          <Tooltip />

          <Line
            type="monotone"
            dataKey="risk"
            name={
              t.riskScore
            }
            stroke="#ff5d6c"
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={
              false
            }
          />
        </LineChart>
      </ResponsiveContainer>
    ) : (
      <div className="detail-chart-empty">
        {
          t.noRiskHistory
        }
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
              {
                t.panelInspection
              }
            </p>

            <h2>
              {panel
                ?.panel_id ??
                t.loading}
            </h2>
          </div>

          <button
            className="detail-close"
            onClick={
              onClose
            }
            type="button"
            aria-label={
              t.close
            }
          >
            ×
          </button>

        </div>


        {loading ? (

          <div className="detail-loading">
            {
              t.loadingPanel
            }
          </div>

        ) : error ? (

          <div className="detail-error">
            {error}
          </div>

        ) : !detail ? (

          <div className="detail-error">
            {
              t.unavailable
            }
          </div>

        ) : (

          <div className="detail-content pd-detail-content">

            <section className="pd-hero">

              <article className="pd-hero-card risk">

                <span>
                  {t.risk}
                </span>

                <div className="pd-hero-value-row">

                  <strong>
                    {risk
                      ?.risk_score ??
                      0}
                  </strong>

                  <span
                    className={`detail-status ${(
                      risk?.status ??
                      "unknown"
                    ).toLowerCase()}`}
                  >
                    {mapLabel(
                      STATUS_LABELS,
                      safeLanguage,
                      risk?.status
                    )}
                  </span>

                </div>

                <small>
                  {mapLabel(
                    PRIMARY_RISK_LABELS,
                    safeLanguage,
                    risk
                      ?.primary_risk ??
                      "NO_DATA"
                  )}
                </small>

              </article>


              <article className="pd-hero-card consensus">

                <span>
                  {
                    t.consensus
                  }
                </span>

                <strong
                  className={`pd-consensus-value ${statusClass(
                    consensus
                      ?.status
                  )}`}
                >
                  {
                    consensusLabel
                  }
                </strong>

                <small>
                  {intelligence
                    ?.available
                    ? mapLabel(
                        CONFIDENCE_LABELS,
                        safeLanguage,
                        consensus
                          ?.confidence
                      )
                    : t.aiUnavailable}
                </small>

              </article>


              <article className="pd-hero-card predictive">

                <span>
                  {
                    t.predictiveRisk
                  }
                </span>

                <strong>
                  {intelligence
                    ?.available
                    ? formatPercent(
                        predictiveProbability,
                        1
                      )
                    : "--"}
                </strong>

                <small>
                  {intelligence
                    ?.available
                    ? mapLabel(
                        PREDICTION_LABELS,
                        safeLanguage,
                        predictiveDecision
                      )
                    : t.aiUnavailable}
                </small>

                {intelligence
                  ?.available && (
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
                  {
                    t.behavioralAnomaly
                  }
                </span>

                <strong
                  className={
                    anomaly
                      ?.detected
                      ? "ai-alert-text"
                      : "safe-text"
                  }
                >
                  {
                    anomalyLabel
                  }
                </strong>

                <small>
                  {intelligence
                    ?.available
                    ? anomaly
                        ?.detected
                      ? t.unusualBehavior
                      : t.healthyPattern
                    : t.aiUnavailable}
                </small>

              </article>

            </section>


            <section className="pd-context-strip">

              <div>
                <span>
                  {
                    t.dataQuality
                  }
                </span>

                <strong
                  className={`pd-quality ${statusClass(
                    panel
                      ?.data_quality
                  )}`}
                >
                  {mapLabel(
                    QUALITY_LABELS,
                    safeLanguage,
                    panel
                      ?.data_quality
                  )}
                </strong>
              </div>

              <div>
                <span>
                  {
                    t.primaryRisk
                  }
                </span>

                <strong>
                  {mapLabel(
                    PRIMARY_RISK_LABELS,
                    safeLanguage,
                    risk
                      ?.primary_risk ??
                      "NO_DATA"
                  )}
                </strong>
              </div>

              <div>
                <span>
                  {
                    t.confidence
                  }
                </span>

                <strong>
                  {intelligence
                    ?.available
                    ? mapLabel(
                        CONFIDENCE_LABELS,
                        safeLanguage,
                        consensus
                          ?.confidence
                      )
                    : "--"}
                </strong>
              </div>

              <div>
                <span>
                  {
                    t.layerAgreement
                  }
                </span>

                <strong>
                  {intelligence
                    ?.available
                    ? `${consensus?.strong_signal_count ?? 0}/3`
                    : "--"}
                </strong>
              </div>

              <div>
                <span>
                  {
                    t.horizon
                  }
                </span>

                <strong>
                  {intelligence
                    ?.available
                    ? `${predictive?.prediction_horizon_cycles ?? "--"} ${t.cycles}`
                    : "--"}
                </strong>
              </div>

              <div>
                <span>
                  {
                    t.lastSeen
                  }
                </span>

                <strong>
                  {formatTime(
                    panel
                      ?.last_seen,
                    safeLanguage
                  )}
                </strong>
              </div>

            </section>


            <section className="detail-section pd-timeline-section">

              <div className="detail-section-title pd-section-heading">

                <div>
                  <p className="eyebrow">
                    {
                      t.intelligence
                    }
                  </p>

                  <h3>
                    {
                      t.earlyTimeline
                    }
                  </h3>
                </div>

                {intelligence
                  ?.available && (
                  <span
                    className={`intelligence-status ${statusClass(
                      consensus
                        ?.status
                    )}`}
                  >
                    {
                      consensusLabel
                    }
                  </span>
                )}

              </div>

              {!intelligence
                ?.available ? (

                <div className="intelligence-unavailable">

                  <strong>
                    {
                      t.aiAnalysisUnavailable
                    }
                  </strong>

                  <p>
                    {translateBackendText(
                      intelligence
                        ?.reason,
                      safeLanguage
                    ) ||
                      t.aiNotEnough}
                  </p>

                </div>

              ) : (

                <>
                  <AiTimeline
                    key={
                      panel
                        ?.panel_id
                    }
                    panel={
                      panel
                    }
                    risk={
                      risk
                    }
                    intelligence={
                      intelligence
                    }
                    language={
                      safeLanguage
                    }
                  />

                  <div className="pd-intelligence-note">

                    <div>
                      <span>
                        {
                          t.currentInterpretation
                        }
                      </span>

                      <strong>
                        {translateBackendText(
                          consensus
                            ?.summary ??
                            predictive
                              ?.reason,
                          safeLanguage
                        ) ||
                          t.noInterpretation}
                      </strong>
                    </div>

                    <p>
                      {translateBackendText(
                        intelligence
                          ?.prototype_notice,
                        safeLanguage
                      ) ||
                        t.prototypeNotice}
                    </p>

                  </div>
                </>

              )}

            </section>


            <section className="detail-section">

              <div className="detail-section-title">

                <p className="eyebrow">
                  {
                    t.liveTelemetry
                  }
                </p>

                <h3>
                  {
                    t.currentMeasurements
                  }
                </h3>

              </div>

              <div className="sensor-grid pd-sensor-grid">

                <article>
                  <span>
                    {
                      t.current
                    }
                  </span>

                  <strong>
                    {formatNumber(
                      panel
                        ?.current_a,
                      1
                    )} A
                  </strong>
                </article>

                <article>
                  <span>
                    {
                      t.cableTemperature
                    }
                  </span>

                  <strong>
                    {formatNumber(
                      panel
                        ?.cable_temperature_c,
                      1
                    )} °C
                  </strong>
                </article>

                <article>
                  <span>
                    {
                      t.ambientTemperature
                    }
                  </span>

                  <strong>
                    {formatNumber(
                      panel
                        ?.ambient_temperature_c,
                      1
                    )} °C
                  </strong>
                </article>

                <article>
                  <span>
                    {
                      t.humidity
                    }
                  </span>

                  <strong>
                    {formatNumber(
                      panel
                        ?.humidity_pct,
                      1
                    )} %
                  </strong>
                </article>

                <article>
                  <span>
                    {
                      t.pdIndex
                    }
                  </span>

                  <strong>
                    {formatNumber(
                      panel
                        ?.pd_index,
                      1
                    )}
                  </strong>
                </article>

                <article>
                  <span>
                    {
                      t.arcDetection
                    }
                  </span>

                  <strong
                    className={
                      panel
                        ?.arc_detected
                        ? "danger-text"
                        : "safe-text"
                    }
                  >
                    {panel
                      ?.arc_detected
                      ? t.detected
                      : t.clear}
                  </strong>
                </article>

              </div>

            </section>


            <details className="detail-section pd-disclosure">

              <summary>

                <div>
                  <p className="eyebrow">
                    {
                      t.explainability
                    }
                  </p>

                  <h3>
                    {
                      t.whyRated
                    }
                  </h3>
                </div>

                <span className="pd-disclosure-hint">
                  {
                    t.openDetails
                  }
                </span>

              </summary>


              <div className="pd-disclosure-body">

                <div className="pd-explanation-column">

                  <div className="pd-subheading">

                    <strong>
                      {
                        t.deterministicExplanation
                      }
                    </strong>

                    <span>
                      {
                        t.ruleEvidence
                      }
                    </span>

                  </div>


                  <div className="cause-list">

                    {(risk
                      ?.causes ??
                      []).length >
                    0 ? (

                      (
                        risk
                          ?.causes ??
                        []
                      ).map(
                        (
                          cause,
                          index
                        ) => (

                          <div
                            className="cause-item"
                            key={`${cause}-${index}`}
                          >

                            <span>
                              {
                                index +
                                1
                              }
                            </span>

                            <p>
                              {translateBackendText(
                                cause,
                                safeLanguage
                              )}
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
                          {
                            t.noExplanation
                          }
                        </p>

                      </div>

                    )}

                  </div>


                  <div className="component-score-grid">

                    <div>
                      <span>
                        {
                          t.current
                        }
                      </span>

                      <strong>
                        {risk
                          ?.component_scores
                          ?.current ??
                          0}
                      </strong>
                    </div>

                    <div>
                      <span>
                        {
                          t.thermal
                        }
                      </span>

                      <strong>
                        {risk
                          ?.component_scores
                          ?.thermal ??
                          0}
                      </strong>
                    </div>

                    <div>
                      <span>
                        {
                          t.environment
                        }
                      </span>

                      <strong>
                        {risk
                          ?.component_scores
                          ?.environment ??
                          0}
                      </strong>
                    </div>

                    <div>
                      <span>
                        {
                          t.partialDischarge
                        }
                      </span>

                      <strong>
                        {risk
                          ?.component_scores
                          ?.partial_discharge ??
                          0}
                      </strong>
                    </div>

                  </div>

                </div>


                <div className="pd-explanation-column">

                  <div className="pd-subheading">

                    <strong>
                      {
                        t.aiDrivers
                      }
                    </strong>

                    <span>
                      {
                        t.xgboost
                      }
                    </span>

                  </div>


                  {(explainability
                    ?.top_drivers ??
                    []).length >
                  0 ? (

                    <div className="ai-driver-list pd-driver-list">

                      {(explainability
                        ?.top_drivers ??
                        []).map(
                        (
                          driver,
                          index
                        ) => (

                          <div
                            className="ai-driver-row"
                            key={`${driver.feature}-${index}`}
                          >

                            <div className="ai-driver-rank">
                              {
                                index +
                                1
                              }
                            </div>

                            <div className="ai-driver-copy">

                              <strong>
                                {driverLabel(
                                  driver,
                                  safeLanguage
                                )}
                              </strong>

                              <span>
                                {t.value}:{" "}
                                {formatNumber(
                                  driver
                                    .value,
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
                                {driver.contribution >
                                0
                                  ? "+"
                                  : ""}
                                {formatNumber(
                                  driver
                                    .contribution,
                                  3
                                )}
                              </strong>

                              <span>
                                {driver.direction ===
                                "INCREASES_RISK"
                                  ? t.increasesRisk
                                  : driver.direction ===
                                    "DECREASES_RISK"
                                  ? t.decreasesRisk
                                  : t.neutral}
                              </span>

                            </div>

                          </div>

                        )
                      )}

                    </div>

                  ) : (

                    <div className="intelligence-unavailable compact">
                      {
                        t.noContribution
                      }
                    </div>

                  )}

                </div>

              </div>

            </details>


            <section className="detail-section">

              <div className="detail-section-title">

                <p className="eyebrow">
                  {
                    t.alarmState
                  }
                </p>

                <h3>
                  {
                    t.activeAlarm
                  }
                </h3>

              </div>

              {activeAlarm ? (

                <div className="active-alarm-box">

                  <div className="alarm-heading">

                    <span
                      className={`detail-status ${(
                        activeAlarm
                          .severity ??
                        "unknown"
                      ).toLowerCase()}`}
                    >
                      {mapLabel(
                        STATUS_LABELS,
                        safeLanguage,
                        activeAlarm
                          .severity
                      )}
                    </span>

                    <strong>
                      {t.alarm} #
                      {
                        activeAlarm.id
                      }
                    </strong>

                  </div>

                  <p>
                    {translateBackendText(
                      activeAlarm
                        .message,
                      safeLanguage
                    )}
                  </p>

                  <div className="alarm-meta">

                    <span>
                      {t.risk}:{" "}

                      <strong>
                        {
                          activeAlarm
                            .risk_score
                        }
                      </strong>
                    </span>

                    <span>
                      {t.opened}:{" "}

                      <strong>
                        {formatTime(
                          activeAlarm
                            .opened_at,
                          safeLanguage
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

                  {
                    t.noActiveAlarm
                  }

                </div>

              )}

            </section>


            <section className="detail-section pd-trends">

              <div className="pd-trend-heading">

                <div>
                  <p className="eyebrow">
                    {
                      t.trendAnalysis
                    }
                  </p>

                  <h3>
                    {
                      t.historicalSignals
                    }
                  </h3>
                </div>


                <div
                  className="pd-trend-tabs"
                  role="tablist"
                  aria-label={
                    t.trendAnalysis
                  }
                >

                  <button
                    type="button"
                    className={
                      trendTab ===
                      "current"
                        ? "active"
                        : ""
                    }
                    onClick={() =>
                      setTrendTab(
                        "current"
                      )
                    }
                  >
                    {t.current}
                  </button>

                  <button
                    type="button"
                    className={
                      trendTab ===
                      "temperature"
                        ? "active"
                        : ""
                    }
                    onClick={() =>
                      setTrendTab(
                        "temperature"
                      )
                    }
                  >
                    {
                      t.temperature
                    }
                  </button>

                  <button
                    type="button"
                    className={
                      trendTab ===
                      "risk"
                        ? "active"
                        : ""
                    }
                    onClick={() =>
                      setTrendTab(
                        "risk"
                      )
                    }
                  >
                    {t.risk}
                  </button>

                </div>

              </div>


              <div className="detail-chart pd-trend-chart">
                {
                  renderTrendChart()
                }
              </div>

            </section>

          </div>

        )}

      </aside>
    </>
  );
}


export default PanelDetail;
