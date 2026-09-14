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


function PanelView({
  panels = [],
  onOpenPanel,
}) {
  const panelIds = useMemo(
    () =>
      panels.map(
        (panel) => panel.panel_id
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


  const [
    detail,
    setDetail,
  ] = useState(null);


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState(null);


  useEffect(() => {
    if (panelIds.length === 0) {
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
          "Digital Panel Twin data could not be loaded."
        );
      } finally {
        setLoading(false);
      }
    }, [selectedPanelId]);


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
            DIGITAL HARDWARE LAYER
          </p>

          <h2>
            Panel View
          </h2>

          <p>
            Live virtual representation
            of GridGuard field
            instrumentation and edge
            monitoring.
          </p>

        </div>


        <div className="panel-view-controls">

          <label
            htmlFor="panel-view-selector"
          >
            MONITORED PANEL
          </label>

          <select
            id="panel-view-selector"
            value={selectedPanelId}
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
            Open Full Analysis
          </button>

        </div>

      </div>


      <div className="panel-view-status-strip">

        <div>

          <span>
            Panel
          </span>

          <strong>
            {selectedPanelId ||
              "--"}
          </strong>

        </div>


        <div>

          <span>
            Current State
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
            {selectedPanelSummary
              ?.status ??
              "UNKNOWN"}
          </strong>

        </div>


        <div>

          <span>
            Risk Score
          </span>

          <strong>
            {selectedPanelSummary
              ?.risk_score ??
              "--"}
          </strong>

        </div>


        <div>

          <span>
            Data Quality
          </span>

          <strong>
            {selectedPanelSummary
              ?.data_quality ??
              "UNKNOWN"}
          </strong>

        </div>

      </div>


      {error ? (

        <div className="panel-view-error">

          <strong>
            Digital Panel Twin unavailable
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
            Retry
          </button>

        </div>

      ) : !detail ? (

        <div className="panel-view-loading">

          {loading
            ? "Loading Digital Panel Twin..."
            : "Waiting for panel telemetry..."}

        </div>

      ) : (

        <>

          <DigitalPanelTwin
            detail={detail}
          />


          <div className="panel-view-live-note">

            <span className="panel-view-live-dot" />

            <div>

              <strong>
                LIVE VIRTUAL HARDWARE
              </strong>

              <span>
                Refreshing from GridGuard
                telemetry every 5 seconds
              </span>

            </div>

          </div>

        </>

      )}

    </section>
  );
}


export default PanelView;