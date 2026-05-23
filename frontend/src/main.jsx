import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Gauge,
  GitBranch,
  RefreshCw,
  ShieldCheck,
  TicketPlus,
} from "lucide-react";
import { fetchDashboard, fetchHealth, fetchTickets, submitTicket } from "./api";
import "./styles.css";

const emptyForm = {
  title: "",
  description: "",
  priority: "Medium",
  business_impact: "",
  technical_area: "",
};

function App() {
  const [health, setHealth] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [status, setStatus] = useState({ type: "idle", message: "" });
  const [loading, setLoading] = useState(false);

  async function loadData() {
    setLoading(true);
    try {
      const [healthData, dashboardData, ticketData] = await Promise.all([
        fetchHealth(),
        fetchDashboard(),
        fetchTickets(),
      ]);
      setHealth(healthData);
      setDashboard(dashboardData);
      setTickets(ticketData);
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus({ type: "idle", message: "" });

    try {
      await submitTicket(form);
      setForm(emptyForm);
      setStatus({ type: "success", message: "Ticket triaged and persisted." });
      await loadData();
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    }
  }

  const latestTicket = tickets[0];
  const averageRisk = dashboard?.average_risk_score ?? 0;

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">AI Operations Control Plane</p>
          <h1>Enterprise AI Triage</h1>
        </div>
        <div className="system-status">
          <span className="status-dot" />
          <span className="provider-name">{health?.provider || "provider loading"}</span>
          <button className="icon-button" onClick={loadData} aria-label="Refresh dashboard" title="Refresh dashboard">
            <RefreshCw size={17} />
          </button>
        </div>
      </section>

      <section className="kpi-grid">
        <KpiCard icon={TicketPlus} label="Tickets" value={dashboard?.total_tickets ?? 0} />
        <KpiCard icon={Gauge} label="Avg risk" value={averageRisk.toFixed(2)} />
        <KpiCard icon={AlertTriangle} label="High risk" value={dashboard?.high_risk_tickets ?? 0} />
        <KpiCard icon={GitBranch} label="Escalations" value={Object.keys(dashboard?.escalation_counts || {}).length} />
      </section>

      <section className="workspace-grid">
        <form className="panel triage-form" onSubmit={handleSubmit}>
          <div className="panel-heading">
            <div>
              <p className="eyebrow">New intake</p>
              <h2>Submit ticket</h2>
            </div>
            <BrainCircuit size={22} />
          </div>

          <label>
            Title
            <input
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
              placeholder="Production incident, AI use case, governance issue..."
              required
            />
          </label>

          <label>
            Description
            <textarea
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
              placeholder="Describe symptoms, request, affected service, user group, or business process."
              required
            />
          </label>

          <div className="form-row">
            <label>
              Priority
              <select
                value={form.priority}
                onChange={(event) => setForm({ ...form, priority: event.target.value })}
              >
                <option>Low</option>
                <option>Medium</option>
                <option>High</option>
                <option>Critical</option>
              </select>
            </label>

            <label>
              Technical area
              <input
                value={form.technical_area}
                onChange={(event) => setForm({ ...form, technical_area: event.target.value })}
                placeholder="DevOps, Security, AI Automation"
                required
              />
            </label>
          </div>

          <label>
            Business impact
            <textarea
              className="compact"
              value={form.business_impact}
              onChange={(event) => setForm({ ...form, business_impact: event.target.value })}
              placeholder="Revenue, SLA, compliance, productivity, customer impact..."
              required
            />
          </label>

          <button className="primary-button" type="submit">
            <ShieldCheck size={18} />
            Triage and save
          </button>

          {status.message && (
            <p className={`notice ${status.type}`}>
              {status.type === "success" ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
              {status.message}
            </p>
          )}
        </form>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Live decisioning</p>
              <h2>Latest classification</h2>
            </div>
            <BarChart3 size={22} />
          </div>

          {latestTicket ? (
            <TicketDecision ticket={latestTicket} />
          ) : (
            <p className="empty-state">No tickets yet.</p>
          )}

          <Distribution title="Priorities" data={dashboard?.priority_counts || {}} />
          <Distribution title="Categories" data={dashboard?.category_counts || {}} />
          <Distribution title="Escalation" data={dashboard?.escalation_counts || {}} />
        </section>
      </section>

      <section className="panel ticket-table-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Service portfolio view</p>
            <h2>Ticket register</h2>
          </div>
          <span className="subtle">{loading ? "Refreshing" : `${tickets.length} records`}</span>
        </div>
        <TicketTable tickets={tickets} />
      </section>
    </main>
  );
}

function KpiCard({ icon: Icon, label, value }) {
  return (
    <article className="kpi-card">
      <Icon size={20} />
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function TicketDecision({ ticket }) {
  return (
    <article className="decision-card">
      <div className="decision-header">
        <span className="tag">{ticket.category}</span>
        <span className={`risk risk-${ticket.risk_score}`}>Risk {ticket.risk_score}/5</span>
      </div>
      <h3>{ticket.title}</h3>
      <p>{ticket.recommendation}</p>
      <dl>
        <div>
          <dt>Escalation</dt>
          <dd>{ticket.escalation}</dd>
        </div>
        <div>
          <dt>Area</dt>
          <dd>{ticket.technical_area}</dd>
        </div>
      </dl>
    </article>
  );
}

function Distribution({ title, data }) {
  const entries = Object.entries(data);
  const max = useMemo(() => Math.max(...entries.map(([, value]) => value), 1), [entries]);

  return (
    <div className="distribution">
      <h3>{title}</h3>
      {entries.length === 0 ? (
        <p className="empty-state">No data</p>
      ) : (
        entries.map(([label, value]) => (
          <div className="bar-row" key={label}>
            <span>{label}</span>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${(value / max) * 100}%` }} />
            </div>
            <strong>{value}</strong>
          </div>
        ))
      )}
    </div>
  );
}

function TicketTable({ tickets }) {
  if (!tickets.length) {
    return <p className="empty-state">No ticket records available.</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Priority</th>
            <th>Category</th>
            <th>Risk</th>
            <th>Escalation</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr key={ticket.id}>
              <td>
                <strong>{ticket.title}</strong>
                <span>{ticket.business_impact}</span>
              </td>
              <td>{ticket.priority}</td>
              <td>{ticket.category}</td>
              <td>
                <span className={`risk risk-${ticket.risk_score}`}>{ticket.risk_score}/5</span>
              </td>
              <td>{ticket.escalation}</td>
              <td>{new Date(`${ticket.created_at}Z`).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
