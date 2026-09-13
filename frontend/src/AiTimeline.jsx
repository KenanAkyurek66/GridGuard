import { useEffect, useRef, useState } from "react";

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


function formatTime(value) {
  if (!value) {
    return "--";
  }

  return new Date(value).toLocaleTimeString("tr-TR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}


function formatPercent(value, digits = 1) {
  if (value === null || value === undefined) {
    return "--";
  }

  return `${Number(value).toFixed(digits)}%`;
}


function humanize(value) {
  if (!value) {
    return "UNKNOWN";
  }

  return String(value).replaceAll("_", " ");
}


function TimelineTooltip({ active, payload }) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const sample = payload[0]?.payload;

  if (!sample) {
    return null;
  }

  return (
    <div className="ai-timeline-tooltip">
      <strong>{sample.time}</strong>

      <span>
        Predictive AI: {formatPercent(sample.predictive, 2)}
      </span>

      <span>
        Rule Risk: {sample.ruleRisk}/100
      </span>

      <span>
        Rule State: {humanize(sample.ruleStatus)}
      </span>

      <span>
        Consensus: {humanize(sample.consensus)}
      </span>

      <span>
        Behavioral Anomaly: {humanize(sample.anomaly)}
      </span>
    </div>
  );
}


function AiTimeline({
  panel,
  risk,
  intelligence,
}) {
  const [timeline, setTimeline] = useState([]);

  const lastSampleRef = useRef(null);

  const predictive = intelligence?.predictive;
  const anomaly = intelligence?.anomaly;
  const consensus = intelligence?.consensus;

  const panelId = panel?.panel_id;


  useEffect(() => {
    setTimeline([]);
    lastSampleRef.current = null;
  }, [panelId]);


  useEffect(() => {
    if (
      !panelId ||
      !intelligence?.available ||
      !predictive
    ) {
      return;
    }

    const predictiveProbability = Number(
      predictive?.probability_pct ?? 0
    );

    const ruleRisk = Number(
      risk?.risk_score ?? 0
    );

    const timestamp =
      panel?.last_seen ??
      new Date().toISOString();

    const sampleKey = [
      panelId,
      timestamp,
      ruleRisk,
      predictiveProbability,
      predictive?.decision ?? "UNKNOWN",
      consensus?.status ?? "UNKNOWN",
    ].join("|");

    if (lastSampleRef.current === sampleKey) {
      return;
    }

    lastSampleRef.current = sampleKey;

    const newSample = {
      key: sampleKey,

      time: formatTime(timestamp),

      predictive: predictiveProbability,

      predictiveDecision:
        predictive?.decision ?? "UNKNOWN",

      ruleRisk,

      ruleStatus:
        risk?.status ?? "UNKNOWN",

      consensus:
        consensus?.status ?? "UNKNOWN",

      anomaly:
        anomaly?.level ?? "UNKNOWN",
    };

    setTimeline((previous) => {
      return [
        ...previous,
        newSample,
      ].slice(-TIMELINE_LIMIT);
    });
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
  ]);


  const firstAiEscalationIndex =
    timeline.findIndex(
      (sample) =>
        sample.predictiveDecision === "ESCALATION"
    );

  const firstRuleWarningIndex =
    timeline.findIndex(
      (sample) =>
        [
          "WARNING",
          "HIGH",
          "CRITICAL",
        ].includes(sample.ruleStatus)
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
      predictive?.threshold ?? 0.505644
    ) * 100;


  if (!intelligence?.available) {
    return null;
  }


  return (
    <div className="ai-timeline-card">

      <div className="ai-timeline-heading">

        <div className="ai-timeline-title">

          <span>
            AI EARLY-WARNING TIMELINE
          </span>

          <small>
            Live session history · panel açık
            kaldığı sürece telemetry geçmişi
          </small>

        </div>


        {earlyWarningLead !== null ? (

          <div className="ai-lead-badge confirmed">

            <strong>
              EARLY WARNING CONFIRMED
            </strong>

            <span>
              AI led by {earlyWarningLead} telemetry{" "}
              {earlyWarningLead === 1
                ? "cycle"
                : "cycles"}
            </span>

          </div>

        ) : (

          <div className="ai-lead-badge">

            <strong>
              LIVE OBSERVATION
            </strong>

            <span>
              Waiting for state transitions
            </span>

          </div>

        )}

      </div>


      {timeline.length >= 2 ? (

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
                    <TimelineTooltip />
                  }
                />


                <Legend
                  wrapperStyle={{
                    fontSize: 11,
                  }}
                />


                <ReferenceLine
                  y={predictiveThresholdPercent}
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
                  name="Predictive AI %"
                  stroke="#55bedf"
                  strokeWidth={3}
                  dot={{
                    r: 4,
                  }}
                  activeDot={{
                    r: 6,
                  }}
                  isAnimationActive={false}
                />


                <Line
                  type="monotone"
                  dataKey="ruleRisk"
                  name="Rule Risk Score"
                  stroke="#ff8a4c"
                  strokeWidth={2.5}
                  dot={{
                    r: 4,
                  }}
                  activeDot={{
                    r: 6,
                  }}
                  isAnimationActive={false}
                />

              </LineChart>

            </ResponsiveContainer>

          </div>


          <div className="ai-timeline-footer">

            <span>
              Predictive threshold:{" "}
              {formatPercent(
                predictiveThresholdPercent,
                1
              )}
            </span>

            <span>
              Rule thresholds:
              WARNING 20 · HIGH 45 · CRITICAL 75
            </span>

          </div>
        </>

      ) : (

        <div className="ai-timeline-empty">

          Keep the LV-050 panel open while
          telemetry changes.

          <strong>
            Timeline will appear after the
            next telemetry sample.
          </strong>

        </div>

      )}

    </div>
  );
}


export default AiTimeline;