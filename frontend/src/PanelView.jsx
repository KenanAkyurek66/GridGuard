import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  fetchPanelDetail,
} from "./PanelDetail";

import DigitalPanelTwin from "./DigitalPanelTwin";

import "./PanelView.css";


const TEXT = {
  tr: {
    eyebrow:
      "DİJİTAL DONANIM KATMANI",
    title:
      "Pano Görünümü",
    subtitle:
      "GridGuard saha enstrümantasyonu ve edge izlemenin canlı sanal temsili.",
    monitoredPanel:
      "İZLENEN PANO",
    fullAnalysis:
      "Tam Analizi Aç",
    panel:
      "Pano",
    currentState:
      "Güncel Durum",
    riskScore:
      "Risk Skoru",
    dataQuality:
      "Veri Kalitesi",
    unavailable:
      "Digital Panel Twin kullanılamıyor",
    loadError:
      "Digital Panel Twin verisi yüklenemedi.",
    retry:
      "Tekrar Dene",
    loading:
      "Digital Panel Twin yükleniyor...",
    waiting:
      "Pano telemetrisi bekleniyor...",
    liveHardware:
      "CANLI SANAL DONANIM",
    refreshing:
      "GridGuard telemetrisinden her 5 saniyede bir yenileniyor",
  },

  en: {
    eyebrow:
      "DIGITAL HARDWARE LAYER",
    title:
      "Panel View",
    subtitle:
      "Live virtual representation of GridGuard field instrumentation and edge monitoring.",
    monitoredPanel:
      "MONITORED PANEL",
    fullAnalysis:
      "Open Full Analysis",
    panel:
      "Panel",
    currentState:
      "Current State",
    riskScore:
      "Risk Score",
    dataQuality:
      "Data Quality",
    unavailable:
      "Digital Panel Twin unavailable",
    loadError:
      "Digital Panel Twin data could not be loaded.",
    retry:
      "Retry",
    loading:
      "Loading Digital Panel Twin...",
    waiting:
      "Waiting for panel telemetry...",
    liveHardware:
      "LIVE VIRTUAL HARDWARE",
    refreshing:
      "Refreshing from GridGuard telemetry every 5 seconds",
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


const QUALITY = {
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


function PanelView({
  panels = [],
  onOpenPanel,
  language = "tr",
}) {
  const safeLanguage =
    language === "en"
      ? "en"
      : "tr";

  const t =
    TEXT[safeLanguage];

  const panelIds = useMemo(
    () =>
      panels.map(
        (panel) =>
          panel.panel_id
      ),
    [panels]
  );


  const preferredPanelId =
    panelIds.includes("LV-050")
      ? "LV-050"
      : panelIds[0] ?? "";


  const [
    selectedPanelId,
    setSelectedPanelId,
  ] = useState("");


  const [detail, setDetail] =
    useState(null);


  const [loading, setLoading] =
    useState(false);


  const [error, setError] =
    useState(null);


  useEffect(() => {
    if (
      panelIds.length === 0
    ) {
      setSelectedPanelId("");
      setDetail(null);

      return;
    }


    if (
      !selectedPanelId ||
      !panelIds.includes(
        selectedPanelId
      )
    ) {
      setSelectedPanelId(
        preferredPanelId
      );
    }
  }, [
    panelIds,
    preferredPanelId,
    selectedPanelId,
  ]);


  const loadPanelTwin =
    useCallback(async () => {
      if (!selectedPanelId) {
        return;
      }

      try {
        setLoading(true);

        const data =
          await fetchPanelDetail(
            selectedPanelId
          );

        setDetail(data);
        setError(null);
      } catch (loadError) {
        console.error(
          "Digital Panel Twin could not be loaded:",
          loadError
        );

        setError(
          t.loadError
        );
      } finally {
        setLoading(false);
      }
    }, [
      selectedPanelId,
      t.loadError,
    ]);


  useEffect(() => {
    if (!selectedPanelId) {
      return undefined;
    }

    loadPanelTwin();

    const interval =
      window.setInterval(
        loadPanelTwin,
        5000
      );

    return () => {
      window.clearInterval(
        interval
      );
    };
  }, [
    selectedPanelId,
    loadPanelTwin,
  ]);


  const selectedPanelSummary =
    panels.find(
      (panel) =>
        panel.panel_id ===
        selectedPanelId
    );


  return (
    <section className="panel-view">

      <div className="panel-view-heading">

        <div>
          <p className="eyebrow">
            {t.eyebrow}
          </p>

          <h2>
            {t.title}
          </h2>

          <p>
            {t.subtitle}
          </p>
        </div>


        <div className="panel-view-controls">

          <label
            htmlFor="panel-view-selector"
          >
            {t.monitoredPanel}
          </label>

          <select
            id="panel-view-selector"
            value={
              selectedPanelId
            }
            onChange={(event) =>
              setSelectedPanelId(
                event.target.value
              )
            }
          >
            {panelIds.map(
              (panelId) => (
                <option
                  key={panelId}
                  value={panelId}
                >
                  {panelId}
                </option>
              )
            )}
          </select>


          <button
            type="button"
            disabled={
              !selectedPanelId
            }
            onClick={() =>
              onOpenPanel?.(
                selectedPanelId
              )
            }
          >
            {t.fullAnalysis}
          </button>

        </div>

      </div>


      <div className="panel-view-status-strip">

        <div>
          <span>
            {t.panel}
          </span>

          <strong>
            {selectedPanelId ||
              "--"}
          </strong>
        </div>


        <div>
          <span>
            {t.currentState}
          </span>

          <strong
            className={`panel-view-state ${
              (
                selectedPanelSummary
                  ?.status ??
                "unknown"
              ).toLowerCase()
            }`}
          >
            {mapLabel(
              STATUS,
              safeLanguage,
              selectedPanelSummary
                ?.status
            )}
          </strong>
        </div>


        <div>
          <span>
            {t.riskScore}
          </span>

          <strong>
            {selectedPanelSummary
              ?.risk_score ??
              "--"}
          </strong>
        </div>


        <div>
          <span>
            {t.dataQuality}
          </span>

          <strong>
            {mapLabel(
              QUALITY,
              safeLanguage,
              selectedPanelSummary
                ?.data_quality
            )}
          </strong>
        </div>

      </div>


      {error ? (

        <div className="panel-view-error">

          <strong>
            {t.unavailable}
          </strong>

          <span>
            {error}
          </span>

          <button
            type="button"
            onClick={
              loadPanelTwin
            }
          >
            {t.retry}
          </button>

        </div>

      ) : !detail ? (

        <div className="panel-view-loading">
          {loading
            ? t.loading
            : t.waiting}
        </div>

      ) : (

        <>
          <DigitalPanelTwin
            detail={detail}
            language={
              safeLanguage
            }
          />


          <div className="panel-view-live-note">

            <span className="panel-view-live-dot" />

            <div>
              <strong>
                {t.liveHardware}
              </strong>

              <span>
                {t.refreshing}
              </span>
            </div>

          </div>
        </>

      )}

    </section>
  );
}


export default PanelView;
