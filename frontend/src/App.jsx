import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [connectedPanels, setConnectedPanels] = useState(0);
  const [activeAlarms, setActiveAlarms] = useState(0);
  const [backendOnline, setBackendOnline] = useState(false);
  const [loading, setLoading] = useState(true);

  async function loadDashboard() {
    try {
      const [healthResponse, alarmsResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/health`),
        axios.get(`${API_BASE_URL}/alarms?status=OPEN`),
      ]);

      setConnectedPanels(
        healthResponse.data.connected_panels ?? 0
      );

      setActiveAlarms(
        alarmsResponse.data.count ?? 0
      );

      setBackendOnline(true);
    } catch (error) {
      console.error("GridGuard API connection failed:", error);

      setBackendOnline(false);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();

    const interval = setInterval(
      loadDashboard,
      5000
    );

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <div className="brand-row">
            <div className="brand-mark">G</div>

            <div>
              <h1>GridGuard</h1>
              <p>Operations Center</p>
            </div>
          </div>
        </div>

        <div
          className={`system-badge ${
            backendOnline ? "online" : "offline"
          }`}
        >
          <span className="status-dot" />

          {backendOnline
            ? "SYSTEM ONLINE"
            : "SYSTEM OFFLINE"}
        </div>
      </header>

      <main className="dashboard">
        <section className="intro">
          <div>
            <p className="eyebrow">
              LOW VOLTAGE DISTRIBUTION MONITORING
            </p>

            <h2>Grid Overview</h2>

            <p className="subtitle">
              Real-time telemetry, risk analysis and
              early-warning monitoring.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={loadDashboard}
          >
            Refresh
          </button>
        </section>

        <section className="stat-grid">
          <article className="stat-card">
            <p className="stat-label">
              Connected Panels
            </p>

            <strong>
              {loading ? "--" : connectedPanels}
            </strong>

            <span>
              Registered monitoring modules
            </span>
          </article>

          <article className="stat-card">
            <p className="stat-label">
              Active Alarms
            </p>

            <strong>
              {loading ? "--" : activeAlarms}
            </strong>

            <span>
              Open operational alerts
            </span>
          </article>

          <article className="stat-card">
            <p className="stat-label">
              System Status
            </p>

            <strong className={
              backendOnline
                ? "status-text-online"
                : "status-text-offline"
            }>
              {loading
                ? "CHECKING"
                : backendOnline
                  ? "ONLINE"
                  : "OFFLINE"}
            </strong>

            <span>
              GridGuard API health
            </span>
          </article>
        </section>

        <section className="placeholder-panel">
          <div>
            <p className="eyebrow">
              OPERATIONS
            </p>

            <h3>
              Monitoring workspace ready
            </h3>

            <p>
              Panel risk distribution, active alarms and
              live telemetry will be added here next.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;