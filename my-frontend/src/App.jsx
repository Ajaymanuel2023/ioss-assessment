import { useState } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [url, setUrl] = useState("");
  const [short, setShort] = useState(null);
  const [loading, setLoading] = useState(false);
  const [codeForStats, setCodeForStats] = useState("");
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  const handleShorten = async (e) => {
    e.preventDefault();
    setError("");
    setShort(null);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/shorten`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) {
        const msg = await res.json().catch(() => ({}));
        throw new Error(msg.detail || "Failed to shorten URL");
      }
      const data = await res.json();
      setShort(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      alert("Copied!");
    } catch {
      alert("Copy failed");
    }
  };

  const fetchStats = async () => {
    setStats(null);
    setError("");
    if (!codeForStats.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/stats/${codeForStats.trim()}`);
      if (!res.ok) {
        const msg = await res.json().catch(() => ({}));
        throw new Error(msg.detail || "Failed to load stats");
      }
      const data = await res.json();
      setStats(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ maxWidth: 720, margin: "2rem auto", padding: "1rem" }}>
      <h1 style={{ textAlign: "center" }}>URL Shortener</h1>

      <form onSubmit={handleShorten} style={{ display: "grid", gap: ".75rem", marginTop: "1rem" }}>
        <label htmlFor="longurl">Enter a long URL</label>
        <input
          id="longurl"
          type="url"
          required
          placeholder="https://example.com/some/very/long/link"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={{ padding: "0.6rem", borderRadius: 8, border: "1px solid #ccc" }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{ padding: "0.7rem 1rem", borderRadius: 8, border: "none", cursor: "pointer" }}
        >
          {loading ? "Shortening..." : "Shorten"}
        </button>
      </form>

      {error && (
        <p style={{ color: "crimson", marginTop: ".75rem" }}>
          {error}
        </p>
      )}

      {short && (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            border: "1px solid #ddd",
            borderRadius: 12,
          }}
        >
          <p style={{ marginBottom: ".5rem" }}>Short URL:</p>
          <div style={{ display: "flex", gap: ".5rem", alignItems: "center" }}>
            <a href={short.short_url} target="_blank" rel="noreferrer">
              {short.short_url}
            </a>
            <button
              onClick={() => copyToClipboard(short.short_url)}
              style={{ padding: ".4rem .8rem", borderRadius: 8, border: "1px solid #ccc" }}
            >
              Copy
            </button>
          </div>
        </div>
      )}

      <hr style={{ margin: "2rem 0" }} />

      <section>
        <h2>Stats</h2>
        <div style={{ display: "flex", gap: ".5rem", marginTop: ".5rem" }}>
          <input
            placeholder="Enter short code (e.g., abc123)"
            value={codeForStats}
            onChange={(e) => setCodeForStats(e.target.value)}
            style={{ flex: 1, padding: "0.6rem", borderRadius: 8, border: "1px solid #ccc" }}
          />
          <button
            onClick={fetchStats}
            style={{ padding: ".6rem 1rem", borderRadius: 8, border: "none", cursor: "pointer" }}
          >
            Get Stats
          </button>
        </div>
        {stats && (
          <div
            style={{
              marginTop: "1rem",
              padding: "1rem",
              border: "1px solid #ddd",
              borderRadius: 12,
            }}
          >
            <p><strong>Short code:</strong> {stats.short_code}</p>
            <p><strong>Destination:</strong> <a href={stats.long_url} target="_blank" rel="noreferrer">{stats.long_url}</a></p>
            <p><strong>Clicks:</strong> {stats.clicks}</p>
            <p><strong>Created:</strong> {stats.created_at}</p>
          </div>
        )}
      </section>

      <p style={{ marginTop: "2rem", fontSize: 12, color: "#666" }}>
        Backend: <code>{API_BASE}</code>
      </p>
    </div>
  );
}
