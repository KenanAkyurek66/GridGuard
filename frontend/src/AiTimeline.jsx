import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./AiTimeline.css";


const TIMELINE_LIMIT = 20;


const TEXT = {
  tr: {
    predictiveAi:
      "Tahminsel AI",
    ruleRisk:
      "Kural Riski",
    ruleState:
      "Kural Durumu",
    consensus:
      "Ortak Karar",
    anomaly:
      "Davranışsal Anomali",
    title:
      "AI ERKEN UYARI ZAMAN ÇİZELGESİ",
    subtitle:
      "Canlı oturum geçmişi · pano açık kaldığı sürece telemetri geçmişi",
    confirmed:
      "ERKEN UYARI DOĞRULANDI",
    ledBy:
      "AI önden sinyal verdi:",
    cycle:
      "telemetri çevrimi",
    cycles:
      "telemetri çevrimi",
    observation:
      "CANLI GÖZLEM",
    waitingTransitions:
      "Durum geçişleri bekleniyor",
    predictiveThreshold:
      "Tahmin eşiği",
    ruleThresholds:
      "Kural eşikleri",
    warning:
      "UYARI",
    high:
      "YÜKSEK",
    critical:
      "KRİTİK",
    keepPanel:
      "panosunu telemetri değişirken açık tutun.",
    timelineAfter:
      "Zaman çizelgesi bir sonraki telemetri örneğinden sonra görünecek.",
    predictiveLegend:
      "Tahminsel AI %",
    ruleLegend:
      "Kural Risk Skoru",
  },

  en: {
    predictiveAi:
      "Predictive AI",
    ruleRisk:
      "Rule Risk",
    ruleState:
      "Rule State",
    consensus:
      "Consensus",
    anomaly:
      "Behavioral Anomaly",
    title:
      "AI EARLY-WARNING TIMELINE",
    subtitle:
      "Live session history · telemetry history while the panel remains open",
    confirmed:
      "EARLY WARNING CONFIRMED",
    ledBy:
      "AI led by",
    cycle:
      "telemetry cycle",
    cycles:
      "telemetry cycles",
    observation:
      "LIVE OBSERVATION",
    waitingTransitions:
      "Waiting for state transitions",
    predictiveThreshold:
      "Predictive threshold",
    ruleThresholds:
      "Rule thresholds",
    warning:
      "WARNING",
    high:
      "HIGH",
    critical:
      "CRITICAL",
    keepPanel:
      "panel open while telemetry changes.",
    timelineAfter:
      "Timeline will appear after the next telemetry sample.",
    predictiveLegend:
      "Predictive AI %",
    ruleLegend:
      "Rule Risk Score",
  },
};


const STATUS = {
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


const CONSENSUS = {
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


const ANOMALY = {
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
    map[language]?.[key] ??
    String(
      value ?? "--"
    ).replaceAll(
      "_",
      " "
    )
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


function TimelineTooltip({
  active,
  payload,
  language,
}) {
  if (
    !active ||
    !payload ||
    payload.length === 0
  ) {
    return null;
  }

  const sample =
    payload[0]?.payload;

  if (!sample) {
    return null;
  }

  const t =
    TEXT[language];

  return (
    <div className="ai-timeline-tooltip">
      <strong>
        {sample.time}
      </strong>

      <span>
        {t.predictiveAi}:{" "}
        {formatPercent(
          sample.predictive,
          2
        )}
      </span>

      <span>
        {t.ruleRisk}:{" "}
        {sample.ruleRisk}/100
      </span>

      <span>
        {t.ruleState}:{" "}
        {mapLabel(
          STATUS,
          language,
          sample.ruleStatus
        )}
      </span>

      <span>
        {t.consensus}:{" "}
        {mapLabel(
          CONSENSUS,
          language,
          sample.consensus
        )}
      </span>

      <span>
        {t.anomaly}:{" "}
        {mapLabel(
          ANOMALY,
          language,
          sample.anomaly
        )}
      </span>
    </div>
  );
}


function AiTimeline({
  panel,
  risk,
  intelligence,
  language = "tr",
}) {
  const safeLanguage =
    language === "en"
      ? "en"
      : "tr";

  const t =
    TEXT[safeLanguage];

  const [
    timeline,
    setTimeline,
  ] = useState([]);

  const lastSampleRef =
    useRef(null);

  const predictive =
    intelligence?.predictive;

  const anomaly =
    intelligence?.anomaly;

  const consensus =
    intelligence?.consensus;

  const panelId =
    panel?.panel_id;


  useEffect(() => {
    setTimeline([]);
    lastSampleRef.current =
      null;
  }, [panelId]);


  useEffect(() => {
    if (
      !panelId ||
      !intelligence?.available ||
      !predictive
    ) {
      return;
    }

    const predictiveProbability =
      Number(
        predictive
          ?.probability_pct ??
        0
      );

    const ruleRisk =
      Number(
        risk?.risk_score ??
        0
      );

    const timestamp =
      panel?.last_seen ??
      new Date()
        .toISOString();

    const sampleKey = [
      panelId,
      timestamp,
      ruleRisk,
      predictiveProbability,
      predictive?.decision ??
        "UNKNOWN",
      consensus?.status ??
        "UNKNOWN",
    ].join("|");

    if (
      lastSampleRef.current ===
      sampleKey
    ) {
      return;
    }

    lastSampleRef.current =
      sampleKey;

    const newSample = {
      key: sampleKey,
      time: formatTime(
        timestamp,
        safeLanguage
      ),
      predictive:
        predictiveProbability,
      predictiveDecision:
        predictive?.decision ??
        "UNKNOWN",
      ruleRisk,
      ruleStatus:
        risk?.status ??
        "UNKNOWN",
      consensus:
        consensus?.status ??
        "UNKNOWN",
      anomaly:
        anomaly?.level ??
        "UNKNOWN",
    };

    setTimeline(
      (previous) => [
        ...previous,
        newSample,
      ].slice(
        -TIMELINE_LIMIT
      )
    );
  }, [
    panelId,
    panel?.last_seen,
    risk?.risk_score,
    risk?.status,
    intelligence?.available,
    predictive?.probability_pct,
    predictive?.decision,
    anomaly?.level,
    consensus?.status,
    safeLanguage,
  ]);


  const firstAiEscalationIndex =
    timeline.findIndex(
      (sample) =>
        sample
          .predictiveDecision ===
        "ESCALATION"
    );

  const firstRuleWarningIndex =
    timeline.findIndex(
      (sample) =>
        [
          "WARNING",
          "HIGH",
          "CRITICAL",
        ].includes(
          sample.ruleStatus
        )
    );


  const earlyWarningLead =
    firstAiEscalationIndex >= 0 &&
    firstRuleWarningIndex >= 0 &&
    firstAiEscalationIndex <
      firstRuleWarningIndex
      ? firstRuleWarningIndex -
        firstAiEscalationIndex
      : null;


  const predictiveThresholdPercent =
    Number(
      predictive?.threshold ??
      0.505644
    ) * 100;


  if (
    !intelligence?.available
  ) {
    return null;
  }


  return (
    <div className="ai-timeline-card">

      <div className="ai-timeline-heading">

        <div className="ai-timeline-title">

          <span>
            {t.title}
          </span>

          <small>
            {t.subtitle}
          </small>

        </div>


        {earlyWarningLead !==
        null ? (

          <div className="ai-lead-badge confirmed">

            <strong>
              {t.confirmed}
            </strong>

            <span>
              {safeLanguage === "tr"
                ? `${t.ledBy} ${earlyWarningLead} ${earlyWarningLead === 1 ? t.cycle : t.cycles}`
                : `${t.ledBy} ${earlyWarningLead} ${earlyWarningLead === 1 ? t.cycle : t.cycles}`}
            </span>

          </div>

        ) : (

          <div className="ai-lead-badge">

            <strong>
              {t.observation}
            </strong>

            <span>
              {t.waitingTransitions}
            </span>

          </div>

        )}

      </div>


      {timeline.length >=
      2 ? (

        <>
          <div className="ai-timeline-chart">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <LineChart
                data={timeline}
                margin={{
                  top: 12,
                  right: 15,
                  bottom: 5,
                  left: -10,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#17303d"
                />


                <XAxis
                  dataKey="time"
                  stroke="#60798b"
                  tick={{
                    fontSize: 10,
                  }}
                />


                <YAxis
                  domain={[0, 100]}
                  stroke="#60798b"
                  tick={{
                    fontSize: 10,
                  }}
                />


                <Tooltip
                  content={
                    <TimelineTooltip
                      language={
                        safeLanguage
                      }
                    />
                  }
                />


                <Legend
                  wrapperStyle={{
                    fontSize: 11,
                  }}
                />


                <ReferenceLine
                  y={
                    predictiveThresholdPercent
                  }
                  stroke="#55bedf"
                  strokeDasharray="5 5"
                  strokeOpacity={0.6}
                />


                <ReferenceLine
                  y={20}
                  stroke="#f6c85f"
                  strokeDasharray="3 6"
                  strokeOpacity={0.45}
                />


                <ReferenceLine
                  y={45}
                  stroke="#ff9f43"
                  strokeDasharray="3 6"
                  strokeOpacity={0.45}
                />


                <ReferenceLine
                  y={75}
                  stroke="#ff5f6d"
                  strokeDasharray="3 6"
                  strokeOpacity={0.45}
                />


                <Line
                  type="monotone"
                  dataKey="predictive"
                  name={
                    t.predictiveLegend
                  }
                  stroke="#55bedf"
                  strokeWidth={3}
                  dot={{
                    r: 4,
                  }}
                  activeDot={{
                    r: 6,
                  }}
                  isAnimationActive={
                    false
                  }
                />


                <Line
                  type="monotone"
                  dataKey="ruleRisk"
                  name={
                    t.ruleLegend
                  }
                  stroke="#ff8a4c"
                  strokeWidth={2.5}
                  dot={{
                    r: 4,
                  }}
                  activeDot={{
                    r: 6,
                  }}
                  isAnimationActive={
                    false
                  }
                />

              </LineChart>

            </ResponsiveContainer>

          </div>


          <div className="ai-timeline-footer">

            <span>
              {t.predictiveThreshold}:{" "}
              {formatPercent(
                predictiveThresholdPercent,
                1
              )}
            </span>

            <span>
              {t.ruleThresholds}:{" "}
              {t.warning} 20 ·{" "}
              {t.high} 45 ·{" "}
              {t.critical} 75
            </span>

          </div>
        </>

      ) : (

        <div className="ai-timeline-empty">

          {safeLanguage === "tr"
            ? `${panelId ?? "Seçili"} ${t.keepPanel}`
            : `Keep the ${panelId ?? "selected"} ${t.keepPanel}`}

          <strong>
            {t.timelineAfter}
          </strong>

        </div>

      )}

    </div>
  );
}


export default AiTimeline;
