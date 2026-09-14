import {
  useMemo,
  useState,
} from "react";

import "./EdgeLab.css";


const SCENARIOS = {
  NORMAL: {
    currentA: 320,
    cableTempC: 45,
    ambientTempC: 28,
    humidityPct: 42,
    pdIndex: 8,
    arcDetected: false,
    dataQuality: "GOOD",
    previewStatus: "NORMAL",
    previewScore: 0,
    primaryRisk: "NONE",
  },

  OVERHEATING: {
    currentA: 470,
    cableTempC: 76,
    ambientTempC: 31,
    humidityPct: 44,
    pdIndex: 12,
    arcDetected: false,
    dataQuality: "GOOD",
    previewStatus: "HIGH",
    previewScore: 45,
    primaryRisk: "THERMAL",
  },

  ARC_EVENT: {
    currentA: 330,
    cableTempC: 47,
    ambientTempC: 29,
    humidityPct: 41,
    pdIndex: 10,
    arcDetected: true,
    dataQuality: "GOOD",
    previewStatus: "CRITICAL",
    previewScore: 100,
    primaryRisk: "ARC_FLASH",
  },

  BAD_SENSOR: {
    currentA: 900,
    cableTempC: 120,
    ambientTempC: 31,
    humidityPct: 43,
    pdIndex: 11,
    arcDetected: false,
    dataQuality: "BAD",
    previewStatus: "HELD",
    previewScore: null,
    primaryRisk: "QUALITY_GUARD",
  },

  RECOVERY: {
    currentA: 300,
    cableTempC: 44,
    ambientTempC: 27,
    humidityPct: 40,
    pdIndex: 6,
    arcDetected: false,
    dataQuality: "GOOD",
    previewStatus: "NORMAL",
    previewScore: 0,
    primaryRisk: "RECOVERY",
  },
};


const TEXT = {
  en: {
    eyebrow: "SOFTWARE-BASED FIELD / EDGE EMULATOR",
    title: "GridGuard Edge Lab",
    subtitle:
      "A visual test bench for the proposed 1600 kVA LV panel sensing and edge-acquisition architecture.",
    badge: "DESIGN PREVIEW",
    reference: "Reference panel",
    panelName: "1600 kVA LV Panel",
    panelNote:
      "Conceptual sensor placement based on the supplied technical drawing.",
    busbar: "Main Busbar",
    breaker: "Circuit Breaker",
    feeder: "Outgoing Feeder",
    cableArea: "Cable / Load Area",
    sensorLayer: "Virtual Field Sensors",
    edgeTitle: "GridGuard EDGE-01",
    edgeSubtitle: "Proposed field acquisition module",
    edgeOnline: "EDGE ONLINE",
    dataQuality: "Data Quality",
    buffer: "Local Buffer",
    watchdog: "Watchdog",
    network: "Network",
    io: "Sensor I/O",
    healthy: "HEALTHY",
    ready: "READY",
    connected: "CONNECTED",
    active: "ACTIVE",
    routeTitle: "End-to-End Data Path",
    field: "Field Sensors",
    edge: "EDGE-01",
    transport: "MQTT / Modbus",
    server: "GridGuard Server",
    analysis: "Risk + AI",
    resultTitle: "Prototype Output",
    localPreview: "LOCAL PREVIEW",
    resultNote:
      "Tomorrow this panel will be connected to the real /telemetry endpoint, risk engine, AI layer and alarm lifecycle.",
    scenarioTitle: "Field Scenario",
    scenarioNote:
      "Tonight these controls drive the visual prototype only. Backend integration is the next step.",
    normal: "Normal",
    overheating: "Overheating",
    arc: "Arc Event",
    badSensor: "Bad Sensor",
    recovery: "Recovery",
    current: "Current",
    cableTemp: "Cable Temp",
    ambient: "Ambient",
    humidity: "Humidity",
    pd: "PD Index",
    arcSensor: "Arc Sensor",
    clear: "CLEAR",
    detected: "DETECTED",
    referenceHardware: "Reference hardware",
    powerMeter: "MPR-53CS power meter / Modbus reference",
    hfct: "HFCT reference for partial-discharge sensing",
    tvoc: "TVOC-2 reference for arc detection",
    technicalTitle: "Technical References",
    technicalNote:
      "Values and exact field installation details will be validated against the supplied documents before final demo use.",
    disclaimer:
      "Software prototype only. Reference hardware, sensor placement and field installation require qualified electrical-engineering validation.",
    status: "Status",
    score: "Risk Score",
    primary: "Primary Risk",
  },

  tr: {
    eyebrow: "YAZILIM TABANLI SAHA / EDGE EMÜLATÖRÜ",
    title: "GridGuard Edge Lab",
    subtitle:
      "Önerilen 1600 kVA AG pano sensör ve edge veri toplama mimarisini gösteren görsel test ortamı.",
    badge: "TASARIM ÖNİZLEMESİ",
    reference: "Referans pano",
    panelName: "1600 kVA AG Pano",
    panelNote:
      "Sağlanan teknik çizime dayalı kavramsal sensör yerleşimi.",
    busbar: "Ana Bara",
    breaker: "Devre Kesici",
    feeder: "Çıkış Fideri",
    cableArea: "Kablo / Yük Bölgesi",
    sensorLayer: "Sanal Saha Sensörleri",
    edgeTitle: "GridGuard EDGE-01",
    edgeSubtitle: "Önerilen saha veri toplama modülü",
    edgeOnline: "EDGE ÇEVRİMİÇİ",
    dataQuality: "Veri Kalitesi",
    buffer: "Yerel Buffer",
    watchdog: "Watchdog",
    network: "Ağ",
    io: "Sensör I/O",
    healthy: "SAĞLIKLI",
    ready: "HAZIR",
    connected: "BAĞLI",
    active: "AKTİF",
    routeTitle: "Uçtan Uca Veri Akışı",
    field: "Saha Sensörleri",
    edge: "EDGE-01",
    transport: "MQTT / Modbus",
    server: "GridGuard Sunucusu",
    analysis: "Risk + AI",
    resultTitle: "Prototip Çıktısı",
    localPreview: "YEREL ÖNİZLEME",
    resultNote:
      "Yarın bu bölüm gerçek /telemetry endpoint'i, risk motoru, AI katmanı ve alarm yaşam döngüsüne bağlanacak.",
    scenarioTitle: "Saha Senaryosu",
    scenarioNote:
      "Bu akşam kontroller yalnızca görsel prototipi çalıştırıyor. Sonraki adım gerçek backend entegrasyonu.",
    normal: "Normal",
    overheating: "Aşırı Isınma",
    arc: "Ark Olayı",
    badSensor: "Bozuk Sensör",
    recovery: "Toparlanma",
    current: "Akım",
    cableTemp: "Kablo Sıcaklığı",
    ambient: "Ortam",
    humidity: "Nem",
    pd: "PD İndeksi",
    arcSensor: "Ark Sensörü",
    clear: "TEMİZ",
    detected: "ALGILANDI",
    referenceHardware: "Referans donanım",
    powerMeter: "MPR-53CS güç analizörü / Modbus referansı",
    hfct: "Kısmi deşarj algılama için HFCT referansı",
    tvoc: "Ark algılama için TVOC-2 referansı",
    technicalTitle: "Teknik Referanslar",
    technicalNote:
      "Değerler ve saha kurulum detayları final demodan önce sağlanan teknik belgelerle doğrulanacak.",
    disclaimer:
      "Yazılım prototipidir. Referans donanım, sensör yerleşimi ve saha kurulumu yetkin elektrik mühendisliği doğrulaması gerektirir.",
    status: "Durum",
    score: "Risk Skoru",
    primary: "Birincil Risk",
  },
};


function SensorCard({
  channel,
  label,
  source,
  value,
  tone = "cyan",
}) {
  return (
    <article
      className={`edge-lab-sensor edge-lab-sensor--${tone}`}
    >
      <div className="edge-lab-sensor__top">
        <span>{channel}</span>
        <span className="edge-lab-sensor__led" />
      </div>

      <strong>{value}</strong>

      <p>{label}</p>

      <small>{source}</small>
    </article>
  );
}


function EdgeStatus({
  label,
  value,
  tone = "good",
}) {
  return (
    <div className="edge-lab-edge-status">
      <span>{label}</span>

      <strong
        className={`edge-lab-edge-status__value edge-lab-edge-status__value--${tone}`}
      >
        {value}
      </strong>
    </div>
  );
}


function EdgeLab({
  language = "en",
}) {
  const safeLanguage =
    language === "tr"
      ? "tr"
      : "en";

  const t = TEXT[safeLanguage];

  const [
    scenarioKey,
    setScenarioKey,
  ] = useState("NORMAL");

  const scenario =
    SCENARIOS[scenarioKey];

  const resultTone =
    scenario.previewStatus === "CRITICAL"
      ? "critical"
      : scenario.previewStatus === "HIGH"
        ? "high"
        : scenario.previewStatus === "HELD"
          ? "held"
          : "normal";

  const sensorRows = useMemo(
    () => [
      {
        channel: "CH-01",
        label: t.current,
        source: "MPR-53CS",
        value: `${scenario.currentA} A`,
        tone:
          scenario.currentA >= 450
            ? "orange"
            : "cyan",
      },
      {
        channel: "CH-02",
        label: t.cableTemp,
        source: "Surface / cable probe",
        value: `${scenario.cableTempC} °C`,
        tone:
          scenario.cableTempC >= 70
            ? "orange"
            : "cyan",
      },
      {
        channel: "CH-03",
        label: t.ambient,
        source: "Cabinet environment",
        value: `${scenario.ambientTempC} °C`,
        tone: "cyan",
      },
      {
        channel: "CH-04",
        label: t.humidity,
        source: "Cabinet environment",
        value: `${scenario.humidityPct} %`,
        tone: "cyan",
      },
      {
        channel: "CH-05",
        label: t.pd,
        source: "HFCT reference",
        value: String(
          scenario.pdIndex
        ),
        tone:
          scenario.pdIndex >= 40
            ? "orange"
            : "cyan",
      },
      {
        channel: "DI-01",
        label: t.arcSensor,
        source: "TVOC-2 reference",
        value:
          scenario.arcDetected
            ? t.detected
            : t.clear,
        tone:
          scenario.arcDetected
            ? "red"
            : "green",
      },
    ],
    [
      scenario,
      t,
    ]
  );

  const scenarioButtons = [
    ["NORMAL", t.normal],
    [
      "OVERHEATING",
      t.overheating,
    ],
    ["ARC_EVENT", t.arc],
    [
      "BAD_SENSOR",
      t.badSensor,
    ],
    ["RECOVERY", t.recovery],
  ];

  return (
    <section
      className="edge-lab"
      aria-labelledby="edge-lab-title"
    >
      <div className="edge-lab__grid-overlay" />

      <header className="edge-lab-header">
        <div>
          <p className="edge-lab-eyebrow">
            {t.eyebrow}
          </p>

          <h2 id="edge-lab-title">
            {t.title}
          </h2>

          <p className="edge-lab-subtitle">
            {t.subtitle}
          </p>
        </div>

        <div className="edge-lab-preview-badge">
          <span className="edge-lab-preview-badge__dot" />
          {t.badge}
        </div>
      </header>

      <div className="edge-lab-workbench">
        <section className="edge-lab-panel-stage">
          <div className="edge-lab-section-label">
            <span>
              {t.reference}
            </span>

            <strong>
              {t.panelName}
            </strong>
          </div>

          <div className="edge-lab-panel-shell">
            <div className="edge-lab-panel-shell__header">
              <span>
                GRIDGUARD FIELD REFERENCE
              </span>

              <span>
                1600 kVA
              </span>
            </div>

            <div className="edge-lab-panel-shell__body">
              <div className="edge-lab-panel-column">
                <div className="edge-lab-panel-device edge-lab-panel-device--busbar">
                  <span>
                    {t.busbar}
                  </span>
                </div>

                <div className="edge-lab-power-line edge-lab-power-line--one" />

                <div className="edge-lab-panel-device edge-lab-panel-device--breaker">
                  <span>
                    {t.breaker}
                  </span>

                  <b>
                    CB
                  </b>
                </div>

                <div className="edge-lab-power-line edge-lab-power-line--two" />

                <div className="edge-lab-panel-device edge-lab-panel-device--feeder">
                  <span>
                    {t.feeder}
                  </span>
                </div>

                <div className="edge-lab-power-line edge-lab-power-line--three" />

                <div className="edge-lab-panel-device edge-lab-panel-device--cable">
                  <span>
                    {t.cableArea}
                  </span>

                  <div className="edge-lab-cable-bundle">
                    <i />
                    <i />
                    <i />
                  </div>
                </div>
              </div>

              <div className="edge-lab-panel-sensors">
                <span className="edge-lab-marker edge-lab-marker--current">
                  I
                </span>

                <span className="edge-lab-marker edge-lab-marker--temp">
                  T
                </span>

                <span className="edge-lab-marker edge-lab-marker--pd">
                  PD
                </span>

                <span
                  className={`edge-lab-marker edge-lab-marker--arc ${
                    scenario.arcDetected
                      ? "is-active"
                      : ""
                  }`}
                >
                  ARC
                </span>

                <span className="edge-lab-marker edge-lab-marker--ambient">
                  ENV
                </span>
              </div>
            </div>
          </div>

          <p className="edge-lab-panel-note">
            {t.panelNote}
          </p>
        </section>

        <section className="edge-lab-sensors-stage">
          <div className="edge-lab-section-label">
            <span>
              {t.sensorLayer}
            </span>

            <strong>
              6 INPUT CHANNELS
            </strong>
          </div>

          <div className="edge-lab-sensor-grid">
            {sensorRows.map(
              (sensor) => (
                <SensorCard
                  key={sensor.channel}
                  {...sensor}
                />
              )
            )}
          </div>
        </section>

        <section className="edge-lab-edge-stage">
          <div className="edge-lab-section-label">
            <span>
              EDGE COMPUTING
            </span>

            <strong>
              EDGE-01
            </strong>
          </div>

          <div className="edge-lab-edge-device">
            <div className="edge-lab-edge-device__top">
              <div>
                <p>
                  GRIDGUARD
                </p>

                <h3>
                  {t.edgeTitle}
                </h3>

                <span>
                  {t.edgeSubtitle}
                </span>
              </div>

              <div className="edge-lab-edge-online">
                <span />
                {t.edgeOnline}
              </div>
            </div>

            <div className="edge-lab-edge-terminal-strip">
              {[
                "CH1",
                "CH2",
                "CH3",
                "CH4",
                "CH5",
                "DI1",
              ].map(
                (channel) => (
                  <span key={channel}>
                    {channel}
                  </span>
                )
              )}
            </div>

            <div className="edge-lab-edge-status-grid">
              <EdgeStatus
                label={t.dataQuality}
                value={
                  scenario.dataQuality
                }
                tone={
                  scenario.dataQuality ===
                  "BAD"
                    ? "bad"
                    : "good"
                }
              />

              <EdgeStatus
                label={t.buffer}
                value={t.ready}
              />

              <EdgeStatus
                label={t.watchdog}
                value={t.healthy}
              />

              <EdgeStatus
                label={t.network}
                value={t.connected}
              />

              <EdgeStatus
                label={t.io}
                value={t.active}
              />
            </div>

            <div className="edge-lab-edge-ports">
              <div>
                <span>
                  RS485
                </span>

                <strong>
                  MODBUS
                </strong>
              </div>

              <div>
                <span>
                  ETH
                </span>

                <strong>
                  MQTT
                </strong>
              </div>
            </div>
          </div>
        </section>

        <section className="edge-lab-output-stage">
          <div className="edge-lab-section-label">
            <span>
              {t.resultTitle}
            </span>

            <strong>
              {t.localPreview}
            </strong>
          </div>

          <div
            className={`edge-lab-result edge-lab-result--${resultTone}`}
          >
            <div className="edge-lab-result__halo" />

            <span>
              {t.status}
            </span>

            <strong className="edge-lab-result__status">
              {scenario.previewStatus}
            </strong>

            <div className="edge-lab-result__metrics">
              <div>
                <span>
                  {t.score}
                </span>

                <strong>
                  {scenario.previewScore ??
                    "--"}
                </strong>
              </div>

              <div>
                <span>
                  {t.primary}
                </span>

                <strong>
                  {
                    scenario.primaryRisk
                  }
                </strong>
              </div>
            </div>

            <p>
              {t.resultNote}
            </p>
          </div>
        </section>
      </div>

      <section className="edge-lab-route">
        <div className="edge-lab-section-label">
          <span>
            {t.routeTitle}
          </span>

          <strong>
            FIELD → OPERATIONS
          </strong>
        </div>

        <div className="edge-lab-route__track">
          {[
            t.field,
            t.edge,
            t.transport,
            t.server,
            t.analysis,
          ].map(
            (node, index) => (
              <div
                className="edge-lab-route__node"
                key={node}
              >
                <span className="edge-lab-route__index">
                  {String(
                    index + 1
                  ).padStart(
                    2,
                    "0"
                  )}
                </span>

                <strong>
                  {node}
                </strong>

                {index < 4 && (
                  <i className="edge-lab-route__pulse" />
                )}
              </div>
            )
          )}
        </div>
      </section>

      <section className="edge-lab-scenario-panel">
        <div>
          <p className="edge-lab-eyebrow">
            {t.scenarioTitle}
          </p>

          <p className="edge-lab-scenario-note">
            {t.scenarioNote}
          </p>
        </div>

        <div className="edge-lab-scenario-buttons">
          {scenarioButtons.map(
            ([
              key,
              label,
            ]) => (
              <button
                className={
                  scenarioKey === key
                    ? "is-active"
                    : ""
                }
                key={key}
                onClick={() =>
                  setScenarioKey(
                    key
                  )
                }
                type="button"
              >
                {label}
              </button>
            )
          )}
        </div>
      </section>

      <details className="edge-lab-technical">
        <summary>
          {t.technicalTitle}
        </summary>

        <div className="edge-lab-technical__content">
          <div>
            <span>
              MPR-53CS
            </span>

            <p>
              {t.powerMeter}
            </p>
          </div>

          <div>
            <span>
              HFCT
            </span>

            <p>
              {t.hfct}
            </p>
          </div>

          <div>
            <span>
              TVOC-2
            </span>

            <p>
              {t.tvoc}
            </p>
          </div>

          <div>
            <span>
              1600 kVA AG
            </span>

            <p>
              {t.referenceHardware}
            </p>
          </div>

          <p className="edge-lab-technical__note">
            {t.technicalNote}
          </p>
        </div>
      </details>

      <p className="edge-lab-disclaimer">
        {t.disclaimer}
      </p>
    </section>
  );
}


export default EdgeLab;
