import {
  useEffect,
  useMemo,
  useState,
} from "react";

import "./EdgeLab.css";


const API_BASE_URL =
  "http://127.0.0.1:8000";

const EDGE_PANEL_ID =
  "LV-050";


const SCENARIOS = {
  NORMAL: {
    labelEn: "Normal",
    labelTr: "Normal",
    descriptionEn:
      "Send one healthy telemetry sample.",
    descriptionTr:
      "Tek bir sağlıklı telemetri örneği gönderir.",
    packets: [
      {
        currentA: 320,
        cableTempC: 45,
        ambientTempC: 28,
        humidityPct: 42,
        pdIndex: 8,
        arcDetected: false,
        dataQuality: "GOOD",
      },
    ],
  },

  OVERHEATING: {
    labelEn: "Overheating",
    labelTr: "Aşırı Isınma",
    descriptionEn:
      "Run the seven-step synthetic overheating sequence used in the jury demo.",
    descriptionTr:
      "Jüri demosunda kullanılan yedi adımlı sentetik aşırı ısınma senaryosunu çalıştırır.",
    packets: [
      {
        currentA: 320,
        cableTempC: 45,
        ambientTempC: 28,
        humidityPct: 42,
        pdIndex: 8,
        arcDetected: false,
        dataQuality: "GOOD",
      },
      {
        currentA: 340,
        cableTempC: 48,
        ambientTempC: 28,
        humidityPct: 42,
        pdIndex: 8,
        arcDetected: false,
        dataQuality: "GOOD",
      },
      {
        currentA: 370,
        cableTempC: 54,
        ambientTempC: 29,
        humidityPct: 43,
        pdIndex: 9,
        arcDetected: false,
        dataQuality: "GOOD",
      },
      {
        currentA: 400,
        cableTempC: 60,
        ambientTempC: 29,
        humidityPct: 43,
        pdIndex: 9,
        arcDetected: false,
        dataQuality: "GOOD",
      },
      {
        currentA: 435,
        cableTempC: 68,
        ambientTempC: 30,
        humidityPct: 44,
        pdIndex: 10,
        arcDetected: false,
        dataQuality: "GOOD",
      },
      {
        currentA: 470,
        cableTempC: 76,
        ambientTempC: 31,
        humidityPct: 44,
        pdIndex: 11,
        arcDetected: false,
        dataQuality: "GOOD",
      },
      {
        currentA: 500,
        cableTempC: 82,
        ambientTempC: 32,
        humidityPct: 45,
        pdIndex: 12,
        arcDetected: false,
        dataQuality: "GOOD",
      },
    ],
  },

  ARC_EVENT: {
    labelEn: "Arc Event",
    labelTr: "Ark Olayı",
    descriptionEn:
      "Inject a fail-safe digital arc event.",
    descriptionTr:
      "Güvenli moda (fail-safe) göre dijital ark olayı gönderir.",
    packets: [
      {
        currentA: 330,
        cableTempC: 47,
        ambientTempC: 29,
        humidityPct: 41,
        pdIndex: 10,
        arcDetected: true,
        dataQuality: "GOOD",
      },
    ],
  },

  BAD_SENSOR: {
    labelEn: "Bad Sensor",
    labelTr: "Bozuk Sensör",
    descriptionEn:
      "Store extreme raw analog values with BAD quality without trusting them as the latest analog state.",
    descriptionTr:
      "Aşırı ham analog değerleri BAD veri kalitesiyle kaydeder; bu değerleri güvenilir güncel analog durum olarak kullanmaz.",
    packets: [
      {
        currentA: 900,
        cableTempC: 120,
        ambientTempC: 31,
        humidityPct: 43,
        pdIndex: 11,
        arcDetected: false,
        dataQuality: "BAD",
      },
    ],
  },

  RECOVERY: {
    labelEn: "Recovery",
    labelTr: "Toparlanma",
    descriptionEn:
      "Send three GOOD recovery samples and allow the alarm lifecycle to resolve normally.",
    descriptionTr:
      "Üç güvenilir (GOOD) toparlanma örneği gönderir ve alarmın normal şekilde çözülmesini sağlar.",
    packets: [
      {
        currentA: 315,
        cableTempC: 46,
        ambientTempC: 28,
        humidityPct: 41,
        pdIndex: 7,
        arcDetected: false,
        dataQuality: "GOOD",
      },
      {
        currentA: 305,
        cableTempC: 45,
        ambientTempC: 27,
        humidityPct: 40,
        pdIndex: 6,
        arcDetected: false,
        dataQuality: "GOOD",
      },
      {
        currentA: 300,
        cableTempC: 44,
        ambientTempC: 27,
        humidityPct: 40,
        pdIndex: 6,
        arcDetected: false,
        dataQuality: "GOOD",
      },
    ],
  },
};


const TEXT = {
  en: {
    eyebrow: "SOFTWARE-BASED FIELD / EDGE EMULATOR",
    title: "GridGuard Edge Lab",
    subtitle:
      "A live software test bench for the proposed 1600 kVA LV panel sensing and edge-acquisition architecture.",
    liveBadge: "LIVE BACKEND",
    offlineBadge: "BACKEND OFFLINE",
    reference: "Reference Panel",
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
    edgeOffline: "EDGE OFFLINE",
    dataQuality: "Data Quality",
    buffer: "Local Buffer",
    watchdog: "Watchdog",
    network: "Network",
    io: "Sensor I/O",
    healthy: "HEALTHY",
    ready: "READY",
    connected: "CONNECTED",
    disconnected: "DISCONNECTED",
    active: "ACTIVE",
    routeTitle: "End-to-End Data Path",
    field: "Field Sensors",
    edge: "EDGE-01",
    transport: "MQTT / Modbus",
    server: "GridGuard Server",
    analysis: "Risk + AI",
    resultTitle: "GridGuard Decision",
    inputChannels: "6 INPUT CHANNELS",
    edgeComputing: "EDGE COMPUTING",
    fieldReference: "GRIDGUARD FIELD REFERENCE",
    fieldOperations: "FIELD → OPERATIONS",
    errorTitle: "EDGE LAB ERROR",
    liveResult: "LIVE RESULT",
    waiting: "WAITING",
    status: "Status",
    score: "Risk Score",
    primary: "Primary Risk",
    qualityPolicy: "Quality Policy",
    aiAdvisory: "AI Advisory",
    aiProbability: "Predictive Probability",
    consensus: "Consensus",
    alarm: "Alarm",
    noAlarm: "NO OPEN ALARM",
    scenarioTitle: "Field Scenario",
    current: "Current",
    cableTemp: "Cable Temp",
    ambient: "Ambient",
    humidity: "Humidity",
    pd: "PD Index",
    arcSensor: "Arc Sensor",
    clear: "CLEAR",
    detected: "DETECTED",
    runScenario: "RUN SCENARIO",
    running: "RUNNING",
    step: "Step",
    of: "of",
    scenarioTrace: "Scenario Trace",
    noTrace:
      "Run a scenario to populate the live processing trace.",
    deterministic: "Deterministic",
    predictive: "Predictive AI",
    technicalTitle: "Technical References",
    referenceHardware: "Reference hardware",
    powerMeter:
      "MPR-53CS power meter / Modbus reference",
    hfct:
      "HFCT reference for partial-discharge sensing",
    tvoc:
      "TVOC-2 reference for arc detection",
    technicalNote:
      "Reference devices and field placement are conceptual integration choices based on the supplied project material; physical installation requires electrical-engineering validation.",
    disclaimer:
      "Software prototype only. GridGuard is an advisory monitoring and early-warning system, not certified protection or autonomous switching logic.",
    requestFailed:
      "The Edge Lab request failed. Check Backend Terminal 1.",
    livePanel: "Live panel",
  },

  tr: {
    eyebrow: "YAZILIM TABANLI SAHA / EDGE EMÜLATÖRÜ",
    title: "GridGuard Edge Lab",
    subtitle:
      "Önerilen 1600 kVA AG pano için sensör ve uç birim veri toplama mimarisini gerçek GridGuard sunucusuyla çalıştıran yazılım test ortamı.",
    liveBadge: "CANLI SUNUCU",
    offlineBadge: "SUNUCU ÇEVRİMDIŞI",
    reference: "Referans Pano",
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
    edgeOffline: "EDGE ÇEVRİMDIŞI",
    dataQuality: "Veri Kalitesi",
    buffer: "Yerel Buffer",
    watchdog: "Watchdog",
    network: "Ağ",
    io: "Sensör I/O",
    healthy: "SAĞLIKLI",
    ready: "HAZIR",
    connected: "BAĞLI",
    disconnected: "BAĞLANTI YOK",
    active: "AKTİF",
    routeTitle: "Uçtan Uca Veri Akışı",
    field: "Saha Sensörleri",
    edge: "EDGE-01",
    transport: "MQTT / Modbus",
    server: "GridGuard Sunucusu",
    analysis: "Risk + AI",
    resultTitle: "GridGuard Kararı",
    inputChannels: "6 GİRİŞ KANALI",
    edgeComputing: "EDGE BİRİMİ",
    fieldReference: "GRIDGUARD SAHA REFERANSI",
    fieldOperations: "SAHA → OPERASYON",
    errorTitle: "EDGE LAB HATASI",
    liveResult: "CANLI SONUÇ",
    waiting: "BEKLİYOR",
    status: "Durum",
    score: "Risk Skoru",
    primary: "Birincil Risk",
    qualityPolicy: "Kalite Politikası",
    aiAdvisory: "AI Önerisi",
    aiProbability: "Tahmin Olasılığı",
    consensus: "Ortak Karar",
    alarm: "Alarm",
    noAlarm: "AÇIK ALARM YOK",
    scenarioTitle: "Saha Senaryosu",
    current: "Akım",
    cableTemp: "Kablo Sıcaklığı",
    ambient: "Ortam",
    humidity: "Nem",
    pd: "PD İndeksi",
    arcSensor: "Ark Sensörü",
    clear: "TEMİZ",
    detected: "ALGILANDI",
    runScenario: "SENARYOYU ÇALIŞTIR",
    running: "ÇALIŞIYOR",
    step: "Adım",
    of: "/",
    scenarioTrace: "Senaryo İz Kaydı",
    noTrace:
      "Canlı işlem izini görmek için bir senaryo çalıştır.",
    deterministic: "Deterministik",
    predictive: "AI Tahmini",
    technicalTitle: "Teknik Referanslar",
    referenceHardware: "Referans donanım",
    powerMeter:
      "MPR-53CS güç analizörü / Modbus referansı",
    hfct:
      "Kısmi deşarj algılama için HFCT referansı",
    tvoc:
      "Ark algılama için TVOC-2 referansı",
    technicalNote:
      "Referans cihazlar ve saha yerleşimi, sağlanan proje materyallerine dayalı kavramsal entegrasyon seçimleridir; fiziksel kurulum elektrik mühendisliği doğrulaması gerektirir.",
    disclaimer:
      "GridGuard bir yazılım prototipidir; sertifikalı koruma veya otonom anahtarlama sistemi değildir. İzleme ve erken uyarı amacıyla geliştirilmiştir.",
    requestFailed:
      "Edge Lab isteği başarısız oldu. Terminal 1 — BACKEND'i kontrol et.",
    livePanel: "Canlı Panel",
  },
};


function sleep(
  milliseconds
) {
  return new Promise(
    (resolve) => {
      window.setTimeout(
        resolve,
        milliseconds
      );
    }
  );
}


function humanize(
  value
) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "--";
  }

  return String(value)
    .replaceAll("_", " ");
}


const SYSTEM_LABELS_TR = {
  NORMAL: "Normal",
  WARNING: "Uyarı",
  HIGH: "Yüksek",
  CRITICAL: "Kritik",
  UNKNOWN: "Bilinmiyor",

  NONE: "Yok",
  THERMAL: "Termal",
  ARC_FLASH: "Ark Parlaması",
  NO_DATA: "Veri Yok",

  STANDARD: "Standart",
  DEGRADED_CAUTION: "Sınırlı Güven",
  BAD_HOLD: "Hatalı Veri Koruması",
  ARC_FAIL_SAFE: "Ark Güvenli Modu",
  HISTORY_ONLY: "Yalnızca Geçmiş",
  DUPLICATE: "Yinelenen",

  SAFE: "Güvenli",
  HOLD: "İzlemede",
  ESCALATION: "Yükselt",
  OBSERVE: "İzle",
  EARLY_WARNING: "Erken Uyarı",

  OPEN: "Açık",
  OPENED: "Açıldı",
  UPDATED: "Güncellendi",
  RESOLVED: "Çözüldü",
  HELD: "Bekletildi",
  PRESERVED: "Korundu",

  GOOD: "İyi",
  DEGRADED: "Sınırlı",
  BAD: "Hatalı",
};


function displaySystemValue(
  value,
  language
) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "--";
  }

  const raw =
    String(value);

  if (
    language !== "tr"
  ) {
    return humanize(
      raw
    );
  }

  if (
    raw.includes(" / ")
  ) {
    return raw
      .split(" / ")
      .map(
        (part) =>
          SYSTEM_LABELS_TR[
            part
          ] ??
          humanize(
            part
          )
      )
      .join(" / ");
  }

  return (
    SYSTEM_LABELS_TR[
      raw
    ] ??
    humanize(
      raw
    )
  );
}


function formatProbability(
  value
) {
  if (
    value === null ||
    value === undefined
  ) {
    return "--";
  }

  const numeric =
    Number(value);

  if (
    Number.isNaN(
      numeric
    )
  ) {
    return String(value);
  }

  return `${numeric.toFixed(1)}%`;
}


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
        <span>
          {channel}
        </span>

        <span className="edge-lab-sensor__led" />
      </div>

      <strong>
        {value}
      </strong>

      <p>
        {label}
      </p>

      <small>
        {source}
      </small>
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
      <span>
        {label}
      </span>

      <strong
        className={`edge-lab-edge-status__value edge-lab-edge-status__value--${tone}`}
      >
        {value}
      </strong>
    </div>
  );
}


function EdgeLab({
  language = "tr",
  onTelemetryProcessed,
}) {
  const safeLanguage =
    language === "en"
      ? "en"
      : "tr";

  const t =
    TEXT[safeLanguage];

  const [
    scenarioKey,
    setScenarioKey,
  ] = useState(
    "NORMAL"
  );

  const [
    activePacket,
    setActivePacket,
  ] = useState(
    SCENARIOS.NORMAL
      .packets[0]
  );

  const [
    running,
    setRunning,
  ] = useState(false);

  const [
    backendOnline,
    setBackendOnline,
  ] = useState(false);

  const [
    lastResponse,
    setLastResponse,
  ] = useState(null);

  const [
    panelDetail,
    setPanelDetail,
  ] = useState(null);

  const [
    trace,
    setTrace,
  ] = useState([]);

  const [
    progress,
    setProgress,
  ] = useState({
    step: 0,
    total: 0,
  });

  const [
    error,
    setError,
  ] = useState(null);


  const selectedScenario =
    SCENARIOS[
      scenarioKey
    ];


  async function fetchPanelDetail() {
    const response =
      await fetch(
        `${API_BASE_URL}/dashboard/panels/${EDGE_PANEL_ID}/detail?history_limit=30`
      );

    if (
      !response.ok
    ) {
      throw new Error(
        "Panel detail request failed."
      );
    }

    return response.json();
  }


  async function loadInitialState() {
    try {
      const healthResponse =
        await fetch(
          `${API_BASE_URL}/health`
        );

      if (
        !healthResponse.ok
      ) {
        throw new Error(
          "Backend health check failed."
        );
      }

      setBackendOnline(
        true
      );

      try {
        const detail =
          await fetchPanelDetail();

        setPanelDetail(
          detail
        );

        if (
          detail?.panel
        ) {
          setActivePacket({
            currentA:
              detail.panel
                .current_a ??
              activePacket.currentA,
            cableTempC:
              detail.panel
                .cable_temperature_c ??
              activePacket.cableTempC,
            ambientTempC:
              detail.panel
                .ambient_temperature_c ??
              activePacket.ambientTempC,
            humidityPct:
              detail.panel
                .humidity_pct ??
              activePacket.humidityPct,
            pdIndex:
              detail.panel
                .pd_index ??
              activePacket.pdIndex,
            arcDetected:
              Boolean(
                detail.panel
                  .arc_detected
              ),
            dataQuality:
              detail.panel
                .data_quality ??
              "GOOD",
          });
        }
      } catch {
        // LV-050 should exist in the demo baseline.
        // The Edge Lab can still become active after
        // the first telemetry event if it does not.
      }
    } catch {
      setBackendOnline(
        false
      );
    }
  }


  useEffect(() => {
    loadInitialState();
    // Intentionally run once for the Edge Lab mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  async function getBaseTimestamp() {
    try {
      const response =
        await fetch(
          `${API_BASE_URL}/panels/${EDGE_PANEL_ID}/telemetry?limit=1`
        );

      if (
        !response.ok
      ) {
        return Date.now();
      }

      const data =
        await response.json();

      const latest =
        data?.telemetry?.[0]
          ?.timestamp;

      if (
        !latest
      ) {
        return Date.now();
      }

      const latestMs =
        new Date(
          latest
        ).getTime();

      return Math.max(
        Date.now(),
        latestMs + 1000
      );
    } catch {
      return Date.now();
    }
  }


  async function runScenario() {
    if (
      running
    ) {
      return;
    }

    setRunning(true);
    setError(null);
    setTrace([]);
    setLastResponse(null);

    const packets =
      selectedScenario
        .packets;

    setProgress({
      step: 0,
      total:
        packets.length,
    });

    try {
      const baseTimestamp =
        await getBaseTimestamp();

      for (
        let index = 0;
        index <
        packets.length;
        index += 1
      ) {
        const packet =
          packets[index];

        setActivePacket(
          packet
        );

        setProgress({
          step:
            index + 1,
          total:
            packets.length,
        });

        const payload = {
          panel_id:
            EDGE_PANEL_ID,
          timestamp:
            new Date(
              baseTimestamp +
                index * 1000
            ).toISOString(),
          current_a:
            packet.currentA,
          cable_temperature_c:
            packet.cableTempC,
          ambient_temperature_c:
            packet.ambientTempC,
          humidity_pct:
            packet.humidityPct,
          pd_index:
            packet.pdIndex,
          arc_detected:
            packet.arcDetected,
          data_quality:
            packet.dataQuality,
        };

        const telemetryResponse =
          await fetch(
            `${API_BASE_URL}/telemetry`,
            {
              method:
                "POST",
              headers: {
                "Content-Type":
                  "application/json",
              },
              body:
                JSON.stringify(
                  payload
                ),
            }
          );

        if (
          !telemetryResponse.ok
        ) {
          const failureBody =
            await telemetryResponse
              .json()
              .catch(
                () => null
              );

          throw new Error(
            failureBody?.detail
              ?.message ??
              failureBody?.detail ??
              `Telemetry request failed (${telemetryResponse.status}).`
          );
        }

        const telemetryData =
          await telemetryResponse
            .json();

        const detail =
          await fetchPanelDetail();

        setBackendOnline(
          true
        );

        setLastResponse(
          telemetryData
        );

        setPanelDetail(
          detail
        );

        const traceItem = {
          step:
            index + 1,
          currentA:
            packet.currentA,
          cableTempC:
            packet.cableTempC,
          quality:
            packet.dataQuality,
          deterministicStatus:
            telemetryData
              ?.risk
              ?.status ??
            detail
              ?.risk
              ?.status ??
            "--",
          riskScore:
            telemetryData
              ?.risk
              ?.risk_score ??
            detail
              ?.risk
              ?.risk_score ??
            "--",
          predictiveDecision:
            detail
              ?.intelligence
              ?.predictive
              ?.decision ??
            "--",
          predictiveProbability:
            detail
              ?.intelligence
              ?.predictive
              ?.probability_pct ??
            null,
          alarmAction:
            telemetryData
              ?.alarm
              ?.action ??
            (
              detail
                ?.active_alarm
                ?.status ===
              "OPEN"
                ? "OPEN"
                : "--"
            ),
          qualityPolicy:
            telemetryData
              ?.processing
              ?.quality_policy ??
            "--",
        };

        setTrace(
          (
            previous
          ) => [
            ...previous,
            traceItem,
          ]
        );

        if (
          onTelemetryProcessed
        ) {
          onTelemetryProcessed({
            telemetry:
              telemetryData,
            detail,
            scenario:
              scenarioKey,
            step:
              index + 1,
          });
        }

        if (
          index <
          packets.length -
            1
        ) {
          await sleep(
            600
          );
        }
      }
    } catch (
      requestError
    ) {
      console.error(
        "GridGuard Edge Lab scenario failed:",
        requestError
      );

      setBackendOnline(
        false
      );

      setError(
        requestError
          ?.message ||
          t.requestFailed
      );
    } finally {
      setRunning(false);
    }
  }


  function selectScenario(
    key
  ) {
    if (
      running
    ) {
      return;
    }

    setScenarioKey(
      key
    );

    setActivePacket(
      SCENARIOS[
        key
      ].packets[0]
    );

    setTrace([]);
    setProgress({
      step: 0,
      total:
        SCENARIOS[
          key
        ].packets
          .length,
    });
    setError(null);
  }


  const risk =
    lastResponse
      ?.risk ??
    panelDetail?.risk;

  const intelligence =
    panelDetail
      ?.intelligence;

  const predictive =
    intelligence
      ?.predictive;

  const consensus =
    intelligence
      ?.consensus;

  const activeAlarm =
    panelDetail
      ?.active_alarm;

  const resultStatus =
    risk?.status ??
    t.waiting;

  const resultScore =
    risk?.risk_score ??
    "--";

  const resultPrimary =
    risk?.primary_risk ??
    "--";

  const qualityPolicy =
    lastResponse
      ?.processing
      ?.quality_policy ??
    "--";

  const alarmLabel =
    lastResponse
      ?.alarm
      ?.action ??
    (
      activeAlarm
        ? `${activeAlarm.status} / ${activeAlarm.severity}`
        : t.noAlarm
    );

  const predictiveLabel =
    intelligence
      ?.available
      ? displaySystemValue(
          predictive?.decision,
          safeLanguage
        )
      : "--";

  const consensusLabel =
    intelligence
      ?.available
      ? displaySystemValue(
          consensus?.status,
          safeLanguage
        )
      : "--";


  const resultTone =
    resultStatus ===
    "CRITICAL"
      ? "critical"
      : resultStatus ===
          "HIGH"
        ? "high"
        : resultStatus ===
            "WARNING"
          ? "held"
          : resultStatus ===
              "NORMAL"
            ? "normal"
            : "held";


  const sensorRows =
    useMemo(
      () => [
        {
          channel:
            "CH-01",
          label:
            t.current,
          source:
            "MPR-53CS",
          value:
            `${activePacket.currentA} A`,
          tone:
            activePacket.currentA >=
            450
              ? "orange"
              : "cyan",
        },
        {
          channel:
            "CH-02",
          label:
            t.cableTemp,
          source:
            safeLanguage === "tr"
              ? "Yüzey / kablo probu"
              : "Surface / cable probe",
          value:
            `${activePacket.cableTempC} °C`,
          tone:
            activePacket.cableTempC >=
            70
              ? "orange"
              : "cyan",
        },
        {
          channel:
            "CH-03",
          label:
            t.ambient,
          source:
            safeLanguage === "tr"
              ? "Pano iç ortamı"
              : "Cabinet environment",
          value:
            `${activePacket.ambientTempC} °C`,
          tone:
            "cyan",
        },
        {
          channel:
            "CH-04",
          label:
            t.humidity,
          source:
            safeLanguage === "tr"
              ? "Pano iç ortamı"
              : "Cabinet environment",
          value:
            `${activePacket.humidityPct} %`,
          tone:
            "cyan",
        },
        {
          channel:
            "CH-05",
          label:
            t.pd,
          source:
            safeLanguage === "tr"
              ? "HFCT referansı"
              : "HFCT reference",
          value:
            String(
              activePacket.pdIndex
            ),
          tone:
            activePacket.pdIndex >=
            40
              ? "orange"
              : "cyan",
        },
        {
          channel:
            "DI-01",
          label:
            t.arcSensor,
          source:
            safeLanguage === "tr"
              ? "TVOC-2 referansı"
              : "TVOC-2 reference",
          value:
            activePacket
              .arcDetected
              ? t.detected
              : t.clear,
          tone:
            activePacket
              .arcDetected
              ? "red"
              : "green",
        },
      ],
      [
        activePacket,
        t,
        safeLanguage,
      ]
    );


  const scenarioButtons =
    Object.entries(
      SCENARIOS
    ).map(
      ([
        key,
        scenario,
      ]) => [
        key,
        safeLanguage ===
        "tr"
          ? scenario
              .labelTr
          : scenario
              .labelEn,
      ]
    );


  const scenarioDescription =
    safeLanguage ===
    "tr"
      ? selectedScenario
          .descriptionTr
      : selectedScenario
          .descriptionEn;


  return (
    <section
      className={`edge-lab ${
        running
          ? "edge-lab--running"
          : ""
      }`}
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

        <div
          className={`edge-lab-preview-badge ${
            backendOnline
              ? "is-live"
              : "is-offline"
          }`}
        >
          <span className="edge-lab-preview-badge__dot" />

          {backendOnline
            ? t.liveBadge
            : t.offlineBadge}
        </div>
      </header>

      <div className="edge-lab-live-strip">
        <span>
          {t.livePanel}
        </span>

        <strong>
          {EDGE_PANEL_ID}
        </strong>

        <span>
          API
        </span>

        <strong>
          /telemetry
        </strong>

        <span>
          {t.dataQuality}
        </span>

        <strong>
          {displaySystemValue(
            activePacket.dataQuality,
            safeLanguage
          )}
        </strong>
      </div>

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
                {t.fieldReference}
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

                <div className="edge-lab-power-line" />

                <div className="edge-lab-panel-device edge-lab-panel-device--breaker">
                  <span>
                    {t.breaker}
                  </span>

                  <b>
                    CB
                  </b>
                </div>

                <div className="edge-lab-power-line" />

                <div className="edge-lab-panel-device edge-lab-panel-device--feeder">
                  <span>
                    {t.feeder}
                  </span>
                </div>

                <div className="edge-lab-power-line" />

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
                    activePacket
                      .arcDetected
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
              {t.inputChannels}
            </strong>
          </div>

          <div className="edge-lab-sensor-grid">
            {sensorRows.map(
              (
                sensor
              ) => (
                <SensorCard
                  key={
                    sensor.channel
                  }
                  {...sensor}
                />
              )
            )}
          </div>
        </section>

        <section className="edge-lab-edge-stage">
          <div className="edge-lab-section-label">
            <span>
              {t.edgeComputing}
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

                {backendOnline
                  ? t.edgeOnline
                  : t.edgeOffline}
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
                (
                  channel
                ) => (
                  <span
                    key={
                      channel
                    }
                  >
                    {channel}
                  </span>
                )
              )}
            </div>

            <div className="edge-lab-edge-status-grid">
              <EdgeStatus
                label={
                  t.dataQuality
                }
                value={
                  displaySystemValue(
                    activePacket.dataQuality,
                    safeLanguage
                  )
                }
                tone={
                  activePacket
                    .dataQuality ===
                  "BAD"
                    ? "bad"
                    : "good"
                }
              />

              <EdgeStatus
                label={
                  t.buffer
                }
                value={
                  t.ready
                }
              />

              <EdgeStatus
                label={
                  t.watchdog
                }
                value={
                  t.healthy
                }
              />

              <EdgeStatus
                label={
                  t.network
                }
                value={
                  backendOnline
                    ? t.connected
                    : t.disconnected
                }
                tone={
                  backendOnline
                    ? "good"
                    : "bad"
                }
              />

              <EdgeStatus
                label={
                  t.io
                }
                value={
                  t.active
                }
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
              {t.liveResult}
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
              {displaySystemValue(
                resultStatus,
                safeLanguage
              )}
            </strong>

            <div className="edge-lab-result__metrics edge-lab-result__metrics--live">
              <div>
                <span>
                  {t.score}
                </span>

                <strong>
                  {resultScore}
                </strong>
              </div>

              <div>
                <span>
                  {t.primary}
                </span>

                <strong>
                  {displaySystemValue(
                    resultPrimary,
                    safeLanguage
                  )}
                </strong>
              </div>

              <div>
                <span>
                  {t.qualityPolicy}
                </span>

                <strong>
                  {displaySystemValue(
                    qualityPolicy,
                    safeLanguage
                  )}
                </strong>
              </div>

              <div>
                <span>
                  {t.aiAdvisory}
                </span>

                <strong>
                  {predictiveLabel}
                </strong>
              </div>

              <div>
                <span>
                  {t.aiProbability}
                </span>

                <strong>
                  {formatProbability(
                    predictive
                      ?.probability_pct
                  )}
                </strong>
              </div>

              <div>
                <span>
                  {t.consensus}
                </span>

                <strong>
                  {consensusLabel}
                </strong>
              </div>

              <div className="edge-lab-result__metric-wide">
                <span>
                  {t.alarm}
                </span>

                <strong>
                  {displaySystemValue(
                    alarmLabel,
                    safeLanguage
                  )}
                </strong>
              </div>
            </div>
          </div>
        </section>
      </div>

      <section className="edge-lab-route">
        <div className="edge-lab-section-label">
          <span>
            {t.routeTitle}
          </span>

          <strong>
            {t.fieldOperations}
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
            (
              node,
              index
            ) => (
              <div
                className="edge-lab-route__node"
                key={
                  node
                }
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

                {index <
                  4 && (
                  <i className="edge-lab-route__pulse" />
                )}
              </div>
            )
          )}
        </div>
      </section>

      <section className="edge-lab-scenario-panel edge-lab-scenario-panel--live">
        <div className="edge-lab-scenario-copy">
          <p className="edge-lab-eyebrow">
            {t.scenarioTitle}
          </p>

          <p className="edge-lab-scenario-note">
            {scenarioDescription}
          </p>

          {progress.total >
            0 && (
            <div className="edge-lab-progress">
              <div className="edge-lab-progress__label">
                <span>
                  {t.step}
                </span>

                <strong>
                  {progress.step}
                  {" "}
                  {t.of}
                  {" "}
                  {progress.total}
                </strong>
              </div>

              <div className="edge-lab-progress__track">
                <span
                  style={{
                    width:
                      progress.total >
                      0
                        ? `${Math.round(
                            (
                              progress.step /
                              progress.total
                            ) *
                              100
                          )}%`
                        : "0%",
                  }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="edge-lab-scenario-actions">
          <div className="edge-lab-scenario-buttons">
            {scenarioButtons.map(
              ([
                key,
                label,
              ]) => (
                <button
                  className={
                    scenarioKey ===
                    key
                      ? "is-active"
                      : ""
                  }
                  disabled={
                    running
                  }
                  key={
                    key
                  }
                  onClick={() =>
                    selectScenario(
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

          <button
            className="edge-lab-run-button"
            disabled={
              running ||
              !backendOnline
            }
            onClick={
              runScenario
            }
            type="button"
          >
            <span className="edge-lab-run-button__led" />

            {running
              ? t.running
              : t.runScenario}
          </button>
        </div>
      </section>

      {error && (
        <div className="edge-lab-error">
          <strong>
            {t.errorTitle}
          </strong>

          <span>
            {error}
          </span>
        </div>
      )}

      <section className="edge-lab-trace">
        <div className="edge-lab-section-label">
          <span>
            {t.scenarioTrace}
          </span>

          <strong>
            {safeLanguage === "tr"
              ? selectedScenario.labelTr
              : selectedScenario.labelEn}
          </strong>
        </div>

        {trace.length ===
        0 ? (
          <div className="edge-lab-trace__empty">
            {t.noTrace}
          </div>
        ) : (
          <div className="edge-lab-trace__table-wrap">
            <table className="edge-lab-trace__table">
              <thead>
                <tr>
                  <th>
                    #
                  </th>
                  <th>
                    A
                  </th>
                  <th>
                    °C
                  </th>
                  <th>
                    {t.dataQuality}
                  </th>
                  <th>
                    {t.deterministic}
                  </th>
                  <th>
                    {t.score}
                  </th>
                  <th>
                    {t.predictive}
                  </th>
                  <th>
                    {t.aiProbability}
                  </th>
                  <th>
                    {t.alarm}
                  </th>
                </tr>
              </thead>

              <tbody>
                {trace.map(
                  (
                    item
                  ) => (
                    <tr
                      key={
                        item.step
                      }
                    >
                      <td>
                        {
                          item.step
                        }
                      </td>

                      <td>
                        {
                          item.currentA
                        }
                      </td>

                      <td>
                        {
                          item.cableTempC
                        }
                      </td>

                      <td>
                        {displaySystemValue(
                          item.quality,
                          safeLanguage
                        )}
                      </td>

                      <td>
                        {displaySystemValue(
                          item.deterministicStatus,
                          safeLanguage
                        )}
                      </td>

                      <td>
                        {
                          item.riskScore
                        }
                      </td>

                      <td>
                        {displaySystemValue(
                          item.predictiveDecision,
                          safeLanguage
                        )}
                      </td>

                      <td>
                        {formatProbability(
                          item.predictiveProbability
                        )}
                      </td>

                      <td>
                        {displaySystemValue(
                          item.alarmAction,
                          safeLanguage
                        )}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
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
