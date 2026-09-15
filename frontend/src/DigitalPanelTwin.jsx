import "./DigitalPanelTwin.css";


const DETERMINISTIC_STATES = [
  "WARNING",
  "HIGH",
  "CRITICAL",
];


const TEXT = {
  tr: {
    virtualHardwareModel:
      "SANAL DONANIM MODELİ",
    electricalPanel:
      "Elektrik Panosu",
    intro:
      "Ana dağıtım barasından izlenen çıkış kablosuna kadar elektriksel güç yolunu ve durumunu izleyin.",
    panelState:
      "PANO DURUMU",
    risk:
      "Risk",
    predictiveAi:
      "GRIDGUARD TAHMİNSEL AI",
    earlyBeforeThreshold:
      "Deterministik eşikten önce erken uyarı",
    electricalPowerFlow:
      "ELEKTRİKSEL GÜÇ AKIŞI",
    electricalPathCondition:
      "Elektriksel Yol ve Durum",
    mainBusbar:
      "Ana Bara",
    mainBusbarDesc:
      "Pano içinde elektrik enerjisini dağıtan ana iletken.",
    arcMonitoring:
      "Ark izleme",
    circuitBreaker:
      "Devre Kesici",
    circuitBreakerDesc:
      "Çıkış devresi için koruma ve anahtarlama elemanı.",
    monitoredPathCurrent:
      "İzlenen yol akımı",
    breakerNote:
      "Renk, doğrulanmış bir kesici arızasını değil izlenen elektriksel yolun durumunu temsil eder.",
    outgoingFeeder:
      "Çıkış Fideri",
    outgoingFeederDesc:
      "Elektrik enerjisini kesiciden bağlı yüke taşıyan çıkış yolu.",
    currentMeasurement:
      "Akım ölçümü",
    cableLoadArea:
      "Kablo / Yük Bölgesi",
    cableLoadDesc:
      "Termal ve kısmi deşarj koşullarının izlendiği çıkış kablosu ve yük bölgesi.",
    cableTemperature:
      "Kablo sıcaklığı",
    partialDischarge:
      "Kısmi deşarj",
    sensorStatus:
      "SENSÖR DURUMU",
    whatSeeing:
      "GridGuard ne görüyor?",
    current:
      "Akım",
    currentDesc:
      "Elektriksel yük ölçümü",
    cableTempDesc:
      "Kablo / yüzey termal izlemesi",
    pdDesc:
      "PD izleme kanalı",
    arcDetection:
      "Ark Algılama",
    arcDesc:
      "Optik ark izleme",
    ambient:
      "Ortam",
    ambientDesc:
      "Pano içi ortam",
    virtual:
      "SANAL",
    telemetry:
      "Telemetri",
    connected:
      "BAĞLI",
    noData:
      "VERİ YOK",
    dataQuality:
      "Veri Kalitesi",
    aiAnalysis:
      "AI Analizi",
    available:
      "KULLANILABİLİR",
    unavailable:
      "KULLANILAMIYOR",
    prediction:
      "Tahmin",
    consensus:
      "Ortak Karar",
    fieldSensors:
      "Saha Sensörleri",
    measurePanel:
      "Pano koşullarını ölçer",
    collects:
      "Veriyi toplar ve doğrular",
    industrialCommunication:
      "Endüstriyel haberleşme",
    server:
      "GridGuard Sunucusu",
    riskEngineAi:
      "Risk Motoru + AI",
    normal:
      "Normal",
    warning:
      "Uyarı",
    high:
      "Yüksek",
    critical:
      "Kritik",
    aiEarly:
      "AI ERKEN",
    aiEarlyWarning:
      "AI Erken Uyarı",
    clear:
      "TEMİZ",
    detected:
      "ALGILANDI",
    conceptual:
      "Yalnızca kavramsal görselleştirmedir. Nihai sensör yerleşimi, elektriksel izolasyon, koruma ve kurulum; yetkin elektrik mühendisliği doğrulaması gerektirir.",
  },

  en: {
    virtualHardwareModel:
      "VIRTUAL HARDWARE MODEL",
    electricalPanel:
      "Electrical Panel",
    intro:
      "Follow the electrical power path from the main distribution bus to the monitored outgoing cable.",
    panelState:
      "PANEL STATE",
    risk:
      "Risk",
    predictiveAi:
      "GRIDGUARD PREDICTIVE AI",
    earlyBeforeThreshold:
      "Early warning before deterministic threshold",
    electricalPowerFlow:
      "ELECTRICAL POWER FLOW",
    electricalPathCondition:
      "Electrical Path & Condition",
    mainBusbar:
      "Main Busbar",
    mainBusbarDesc:
      "Main conductor that distributes electrical power inside the panel.",
    arcMonitoring:
      "Arc monitoring",
    circuitBreaker:
      "Circuit Breaker",
    circuitBreakerDesc:
      "Protection and switching device for the outgoing electrical circuit.",
    monitoredPathCurrent:
      "Monitored path current",
    breakerNote:
      "Color represents the monitored electrical path, not a confirmed breaker fault.",
    outgoingFeeder:
      "Outgoing Feeder",
    outgoingFeederDesc:
      "Electrical path carrying power from the breaker toward the connected load.",
    currentMeasurement:
      "Current measurement",
    cableLoadArea:
      "Cable / Load Area",
    cableLoadDesc:
      "Monitored outgoing cable and load area where thermal and PD conditions are observed.",
    cableTemperature:
      "Cable temperature",
    partialDischarge:
      "Partial discharge",
    sensorStatus:
      "SENSOR STATUS",
    whatSeeing:
      "What is GridGuard seeing?",
    current:
      "Current",
    currentDesc:
      "Electrical load measurement",
    cableTempDesc:
      "Cable / surface thermal monitoring",
    pdDesc:
      "PD monitoring channel",
    arcDetection:
      "Arc Detection",
    arcDesc:
      "Optical arc monitoring",
    ambient:
      "Ambient",
    ambientDesc:
      "Panel environment",
    virtual:
      "VIRTUAL",
    telemetry:
      "Telemetry",
    connected:
      "CONNECTED",
    noData:
      "NO DATA",
    dataQuality:
      "Data Quality",
    aiAnalysis:
      "AI Analysis",
    available:
      "AVAILABLE",
    unavailable:
      "UNAVAILABLE",
    prediction:
      "Prediction",
    consensus:
      "Consensus",
    fieldSensors:
      "Field Sensors",
    measurePanel:
      "Measure panel conditions",
    collects:
      "Collects and validates data",
    industrialCommunication:
      "Industrial communication",
    server:
      "GridGuard Server",
    riskEngineAi:
      "Risk Engine + AI",
    normal:
      "Normal",
    warning:
      "Warning",
    high:
      "High",
    critical:
      "Critical",
    aiEarly:
      "AI EARLY",
    aiEarlyWarning:
      "AI Early Warning",
    clear:
      "CLEAR",
    detected:
      "DETECTED",
    conceptual:
      "Conceptual visualization only. Final sensor placement, electrical isolation, protection and installation require qualified electrical engineering validation.",
  },
};


const STATE_LABELS = {
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


const DECISION_LABELS = {
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


function formatNumber(
  value,
  digits = 1
) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "--";
  }

  return Number(value)
    .toFixed(digits);
}


function statusClass(value) {
  return String(
    value ?? "NORMAL"
  ).toLowerCase();
}


function isPositiveScore(value) {
  return Number(value ?? 0) >
    0;
}


function containsAny(
  text,
  words
) {
  const normalized =
    String(
      text ?? ""
    ).toLowerCase();

  return words.some(
    (word) =>
      normalized.includes(
        word
      )
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
      label.includes(
        "arc"
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


function aiFocusLabel(
  focus,
  language
) {
  const labels = {
    tr: {
      current:
        "AKIM / FİDER",
      thermal:
        "KABLO SICAKLIĞI",
      pd:
        "KISMİ DEŞARJ",
      environment:
        "ÇEVRESEL",
      arc:
        "ARK",
      unknown:
        "GELİŞEN DURUM",
    },
    en: {
      current:
        "CURRENT / FEEDER",
      thermal:
        "CABLE TEMPERATURE",
      pd:
        "PARTIAL DISCHARGE",
      environment:
        "ENVIRONMENT",
      arc:
        "ARC",
      unknown:
        "DEVELOPING CONDITION",
    },
  };

  return (
    labels[language]?.[
      focus
    ] ??
    labels[language]
      .unknown
  );
}


function aiFocusDescription(
  focus,
  language
) {
  const descriptions = {
    tr: {
      current:
        "AI, çıkış fiderinde gelişen bir yük veya akım eğilimi algıladı.",
      thermal:
        "AI, izlenen kablo / yük bölgesinde gelişen bir termal durum algıladı.",
      pd:
        "AI, izlenen çıkış devresinde olağandışı kısmi deşarj davranışı algıladı.",
      environment:
        "AI, pano riskine katkıda bulunabilecek çevresel bir örüntü algıladı.",
      arc:
        "AI, ark izleme yoluyla ilişkili özellikler algıladı.",
      unknown:
        "AI, deterministik uyarı eşiğine ulaşılmadan önce gelişen bir durum algıladı.",
    },
    en: {
      current:
        "AI detected a developing load or current trend on the outgoing feeder.",
      thermal:
        "AI detected a developing thermal condition around the monitored cable / load area.",
      pd:
        "AI detected unusual partial-discharge behavior in the monitored outgoing circuit.",
      environment:
        "AI detected an environmental pattern that may contribute to panel risk.",
      arc:
        "AI detected features associated with the arc-monitoring path.",
      unknown:
        "AI detected a developing condition before the deterministic warning threshold was reached.",
    },
  };

  return (
    descriptions[
      language
    ]?.[focus] ??
    descriptions[
      language
    ].unknown
  );
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
  language = "tr",
}) {
  const t =
    TEXT[language];

  if (ai) {
    return (
      <span className="simple-state-badge ai">
        {t.aiEarly}
      </span>
    );
  }

  return (
    <span
      className={`simple-state-badge ${statusClass(
        state
      )}`}
    >
      {mapLabel(
        STATE_LABELS,
        language,
        state
      )}
    </span>
  );
}


function PowerStage({
  number,
  title,
  description,
  state = "NORMAL",
  ai = false,
  language = "tr",
  children,
}) {
  return (
    <article
      className={[
        "power-stage",
        statusClass(state),
        ai
          ? "ai-warning"
          : "",
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
            language={
              language
            }
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
  language = "tr",
}) {
  return (
    <div
      className={[
        "simple-sensor-row",
        statusClass(state),
        ai
          ? "ai-warning"
          : "",
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
          language={
            language
          }
        />

      </div>
    </div>
  );
}


function DigitalPanelTwin({
  detail,
  language = "tr",
}) {
  const safeLanguage =
    language === "en"
      ? "en"
      : "tr";

  const t =
    TEXT[safeLanguage];

  const panel =
    detail?.panel ?? {};

  const risk =
    detail?.risk ?? {};

  const intelligence =
    detail?.intelligence ??
    {};

  const predictive =
    intelligence?.predictive ??
    {};

  const consensus =
    intelligence?.consensus ??
    {};

  const scores =
    risk?.component_scores ??
    {};


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
      primaryRisk ===
        "PD"
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
    aiFocus ===
      "current";


  const aiThermal =
    aiEarlyWarning &&
    aiFocus ===
      "thermal";


  const aiPd =
    aiEarlyWarning &&
    aiFocus === "pd";


  const aiEnvironment =
    aiEarlyWarning &&
    aiFocus ===
      "environment";


  const aiArc =
    aiEarlyWarning &&
    aiFocus ===
      "arc";


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
            {t.virtualHardwareModel}
          </p>

          <h3>
            {panel?.panel_id ??
              "PANEL"}{" "}
            {t.electricalPanel}
          </h3>

          <p>
            {t.intro}
          </p>
        </div>


        <div
          className={`simple-panel-state ${statusClass(
            overallStatus
          )}`}
        >
          <span>
            {t.panelState}
          </span>

          <strong>
            {mapLabel(
              STATE_LABELS,
              safeLanguage,
              overallStatus
            )}
          </strong>

          <small>
            {t.risk}{" "}
            {risk?.risk_score ??
              0}
            /100
          </small>
        </div>

      </div>


      {aiEarlyWarning && (

        <div className="simple-ai-banner">

          <div className="simple-ai-pulse" />

          <div>
            <span>
              {t.predictiveAi}
            </span>

            <strong>
              {
                t.earlyBeforeThreshold
              }
            </strong>

            <p>
              {aiFocusDescription(
                aiFocus,
                safeLanguage
              )}
            </p>
          </div>

          <div className="simple-ai-focus">
            {aiFocusLabel(
              aiFocus,
              safeLanguage
            )}
          </div>

        </div>

      )}


      <div className="simple-twin-grid">

        <div className="simple-power-flow">

          <div className="simple-section-heading">
            <div>
              <span>
                {t.electricalPowerFlow}
              </span>

              <strong>
                {t.electricalPathCondition}
              </strong>
            </div>
          </div>


          <PowerStage
            number="1"
            title={
              t.mainBusbar
            }
            description={
              t.mainBusbarDesc
            }
            state={
              busbarState
            }
            ai={
              aiArc
            }
            language={
              safeLanguage
            }
          >

            <div className="stage-reading">
              <span>
                {t.arcMonitoring}
              </span>

              <strong
                className={
                  panel?.arc_detected
                    ? "danger-reading"
                    : "safe-reading"
                }
              >
                {panel?.arc_detected
                  ? t.detected
                  : t.clear}
              </strong>
            </div>

          </PowerStage>


          <FlowArrow />


          <PowerStage
            number="2"
            title={
              t.circuitBreaker
            }
            description={
              t.circuitBreakerDesc
            }
            state={
              breakerPathState
            }
            ai={
              aiBreaker
            }
            language={
              safeLanguage
            }
          >

            <div className="stage-reading">
              <span>
                {t.monitoredPathCurrent}
              </span>

              <strong>
                {formatNumber(
                  panel?.current_a,
                  1
                )} A
              </strong>
            </div>

            <small className="stage-note">
              {t.breakerNote}
            </small>

          </PowerStage>


          <FlowArrow />


          <PowerStage
            number="3"
            title={
              t.outgoingFeeder
            }
            description={
              t.outgoingFeederDesc
            }
            state={
              feederState
            }
            ai={
              aiFeeder
            }
            language={
              safeLanguage
            }
          >

            <div className="stage-reading">
              <span>
                {t.currentMeasurement}
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
            title={
              t.cableLoadArea
            }
            description={
              t.cableLoadDesc
            }
            state={
              cableState
            }
            ai={
              aiCable
            }
            language={
              safeLanguage
            }
          >

            <div className="stage-reading-grid">

              <div>
                <span>
                  {t.cableTemperature}
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
                  {t.partialDischarge}
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
                {t.sensorStatus}
              </span>

              <strong>
                {t.whatSeeing}
              </strong>
            </div>
          </div>


          <SensorRow
            label={
              t.current
            }
            value={`${formatNumber(
              panel?.current_a,
              1
            )} A`}
            description={
              t.currentDesc
            }
            state={
              currentState
            }
            ai={
              aiCurrent
            }
            language={
              safeLanguage
            }
          />


          <SensorRow
            label={
              t.cableTemperature
            }
            value={`${formatNumber(
              panel?.cable_temperature_c,
              1
            )} °C`}
            description={
              t.cableTempDesc
            }
            state={
              thermalState
            }
            ai={
              aiThermal
            }
            language={
              safeLanguage
            }
          />


          <SensorRow
            label={
              t.partialDischarge
            }
            value={formatNumber(
              panel?.pd_index,
              1
            )}
            description={
              t.pdDesc
            }
            state={
              pdState
            }
            ai={
              aiPd
            }
            language={
              safeLanguage
            }
          />


          <SensorRow
            label={
              t.arcDetection
            }
            value={
              panel?.arc_detected
                ? t.detected
                : t.clear
            }
            description={
              t.arcDesc
            }
            state={
              arcState
            }
            ai={
              aiArc
            }
            language={
              safeLanguage
            }
          />


          <SensorRow
            label={
              t.ambient
            }
            value={`${formatNumber(
              panel
                ?.ambient_temperature_c,
              1
            )} °C · ${formatNumber(
              panel?.humidity_pct,
              1
            )}% RH`}
            description={
              t.ambientDesc
            }
            state={
              environmentState
            }
            ai={
              aiEnvironment
            }
            language={
              safeLanguage
            }
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
                {t.virtual}
              </span>

            </div>


            <div className="simple-edge-status">

              <div>
                <span>
                  {t.telemetry}
                </span>

                <strong
                  className={
                    telemetryAvailable
                      ? "edge-ok"
                      : "edge-problem"
                  }
                >
                  {telemetryAvailable
                    ? t.connected
                    : t.noData}
                </strong>
              </div>


              <div>
                <span>
                  {t.dataQuality}
                </span>

                <strong
                  className={
                    dataQuality ===
                    "GOOD"
                      ? "edge-ok"
                      : "edge-warning"
                  }
                >
                  {mapLabel(
                    QUALITY_LABELS,
                    safeLanguage,
                    dataQuality
                  )}
                </strong>
              </div>


              <div>
                <span>
                  {t.aiAnalysis}
                </span>

                <strong
                  className={
                    intelligence?.available
                      ? "edge-ok"
                      : "edge-warning"
                  }
                >
                  {intelligence?.available
                    ? t.available
                    : t.unavailable}
                </strong>
              </div>


              <div>
                <span>
                  {t.prediction}
                </span>

                <strong>
                  {mapLabel(
                    DECISION_LABELS,
                    safeLanguage,
                    predictive?.decision
                  )}
                </strong>
              </div>


              <div>
                <span>
                  {t.consensus}
                </span>

                <strong>
                  {mapLabel(
                    CONSENSUS_LABELS,
                    safeLanguage,
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
            {t.fieldSensors}
          </strong>

          <small>
            {t.measurePanel}
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
            {t.collects}
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
            {t.industrialCommunication}
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
            {t.server}
          </strong>

          <small>
            {t.riskEngineAi}
          </small>
        </div>

      </div>


      <div className="simple-twin-footer">

        <div className="simple-legend">

          <span>
            <StatusDot state="NORMAL" />
            {t.normal}
          </span>

          <span>
            <StatusDot state="WARNING" />
            {t.warning}
          </span>

          <span>
            <StatusDot state="HIGH" />
            {t.high}
          </span>

          <span>
            <StatusDot state="CRITICAL" />
            {t.critical}
          </span>

          <span>
            <StatusDot ai />
            {t.aiEarlyWarning}
          </span>

        </div>


        <p>
          {t.conceptual}
        </p>

      </div>

    </section>
  );
}


export default DigitalPanelTwin;
