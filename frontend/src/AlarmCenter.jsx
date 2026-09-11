import {
  useMemo,
  useState,
} from "react";


function formatDateTime(value) {
  if (!value) {
    return "--";
  }

  return new Date(value).toLocaleString(
    "tr-TR",
    {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }
  );
}


function AlarmCenter({
  alarms = [],
  onOpenPanel,
}) {
  const [statusFilter, setStatusFilter] =
    useState("ALL");

  const [search, setSearch] =
    useState("");


  const openCount = useMemo(
    () =>
      alarms.filter(
        (alarm) =>
          alarm.status === "OPEN"
      ).length,
    [alarms]
  );


  const resolvedCount = useMemo(
    () =>
      alarms.filter(
        (alarm) =>
          alarm.status === "RESOLVED"
      ).length,
    [alarms]
  );


  const filteredAlarms = useMemo(() => {
    const searchValue =
      search
        .trim()
        .toLowerCase();

    return [...alarms]
      .filter((alarm) => {
        const matchesStatus =
          statusFilter === "ALL" ||
          alarm.status === statusFilter;

        const matchesSearch =
          !searchValue ||
          alarm.panel_id
            ?.toLowerCase()
            .includes(searchValue) ||
          alarm.primary_risk
            ?.toLowerCase()
            .includes(searchValue) ||
          alarm.message
            ?.toLowerCase()
            .includes(searchValue);

        return (
          matchesStatus &&
          matchesSearch
        );
      })
      .sort((a, b) => {
        const aTime =
          new Date(
            a.opened_at ?? 0
          ).getTime();

        const bTime =
          new Date(
            b.opened_at ?? 0
          ).getTime();

        return bTime - aTime;
      });
  }, [
    alarms,
    statusFilter,
    search,
  ]);


  return (
    <section className="alarm-center">

      <div className="alarm-center-heading">

        <div>

          <p className="eyebrow">
            INCIDENT MANAGEMENT
          </p>

          <h3>
            Alarm Center
          </h3>

          <p>
            Operational alerts generated
            by the GridGuard risk engine.
          </p>

        </div>


        <div className="alarm-summary-strip">

          <div className="alarm-summary-item">

            <span>
              Open
            </span>

            <strong className="alarm-open-number">
              {openCount}
            </strong>

          </div>


          <div className="alarm-summary-item">

            <span>
              Resolved
            </span>

            <strong className="alarm-resolved-number">
              {resolvedCount}
            </strong>

          </div>


          <div className="alarm-summary-item">

            <span>
              Total
            </span>

            <strong>
              {alarms.length}
            </strong>

          </div>

        </div>

      </div>


      <div className="alarm-controls">

        <input
          type="text"
          placeholder="Search panel, risk or message..."
          value={search}
          onChange={(event) =>
            setSearch(
              event.target.value
            )
          }
        />


        <div className="alarm-filter-tabs">

          <button
            type="button"
            className={
              statusFilter === "ALL"
                ? "active"
                : ""
            }
            onClick={() =>
              setStatusFilter("ALL")
            }
          >
            All
          </button>


          <button
            type="button"
            className={
              statusFilter === "OPEN"
                ? "active"
                : ""
            }
            onClick={() =>
              setStatusFilter("OPEN")
            }
          >
            Open
          </button>


          <button
            type="button"
            className={
              statusFilter === "RESOLVED"
                ? "active"
                : ""
            }
            onClick={() =>
              setStatusFilter(
                "RESOLVED"
              )
            }
          >
            Resolved
          </button>

        </div>

      </div>


      <div className="alarm-table-wrapper">

        <table className="alarm-table">

          <thead>

            <tr>
              <th>Status</th>
              <th>Panel</th>
              <th>Severity</th>
              <th>Risk</th>
              <th>Primary Risk</th>
              <th>Message</th>
              <th>Opened</th>
              <th>Resolved</th>
            </tr>

          </thead>


          <tbody>

            {filteredAlarms.length === 0 ? (

              <tr>

                <td
                  colSpan="8"
                  className="alarm-empty-cell"
                >
                  No matching alarms found.
                </td>

              </tr>

            ) : (

              filteredAlarms.map(
                (alarm) => (

                  <tr
                    key={alarm.id}
                    className={
                      alarm.status === "OPEN"
                        ? "open-alarm-row"
                        : ""
                    }
                  >

                    <td>

                      <span
                        className={`alarm-status-badge ${
                          (
                            alarm.status ??
                            "unknown"
                          ).toLowerCase()
                        }`}
                      >
                        {alarm.status ??
                          "UNKNOWN"}
                      </span>

                    </td>


                    <td>

                      <button
                        type="button"
                        className="alarm-panel-button"
                        onClick={() =>
                          onOpenPanel(
                            alarm.panel_id
                          )
                        }
                      >
                        {alarm.panel_id}
                      </button>

                    </td>


                    <td>

                      <span
                        className={`alarm-severity-badge ${
                          (
                            alarm.severity ??
                            "unknown"
                          ).toLowerCase()
                        }`}
                      >
                        {alarm.severity ??
                          "UNKNOWN"}
                      </span>

                    </td>


                    <td className="alarm-risk-score">
                      {alarm.risk_score ?? 0}
                    </td>


                    <td>
                      {alarm.primary_risk ??
                        "NONE"}
                    </td>


                    <td className="alarm-message-cell">
                      {alarm.message ??
                        "--"}
                    </td>


                    <td>
                      {formatDateTime(
                        alarm.opened_at
                      )}
                    </td>


                    <td>
                      {alarm.status ===
                      "RESOLVED"
                        ? formatDateTime(
                            alarm.resolved_at
                          )
                        : "--"}
                    </td>

                  </tr>

                )
              )

            )}

          </tbody>

        </table>

      </div>


      <div className="alarm-center-footer">

        Showing

        <strong>
          {filteredAlarms.length}
        </strong>

        of

        <strong>
          {alarms.length}
        </strong>

        alarm records

      </div>

    </section>
  );
}


export default AlarmCenter;