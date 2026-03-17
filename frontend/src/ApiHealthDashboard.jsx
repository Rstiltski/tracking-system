/**
 * Veryfyn API Health Dashboard
 * 
 * Drop this file into your React frontend src/ folder and
 * render it at a /test route to verify full stack connectivity.
 * 
 * Usage: import ApiHealthDashboard from './ApiHealthDashboard'
 */

import { useState, useEffect, useCallback } from "react";

const API_BASE = "http://localhost:8000";

const ENDPOINTS = [
    { id: "root", label: "Root", method: "GET", path: "/", category: "server" },
    { id: "health", label: "Health Check", method: "GET", path: "/health", category: "server" },
    { id: "db", label: "DB Connection", method: "GET", path: "/api/db/test", category: "server" },
    { id: "docs", label: "Swagger Docs", method: "GET", path: "/docs", category: "server" },
    { id: "habits", label: "Habits List", method: "GET", path: "/api/habits", category: "habits" },
    { id: "tasks", label: "Tasks List", method: "GET", path: "/api/tasks", category: "tasks" },
    { id: "goals", label: "Goals List", method: "GET", path: "/api/goals", category: "goals" },
    { id: "healthm", label: "Health Metrics", method: "GET", path: "/api/health", category: "health" },
    { id: "cors", label: "CORS Preflight", method: "OPT", path: "/api/habits", category: "cors" },
];

const CATEGORY_COLORS = {
    server: { bg: "#0f2027", accent: "#00d4ff", label: "SERVER" },
    habits: { bg: "#0d1f0d", accent: "#39ff14", label: "HABITS" },
    tasks: { bg: "#1a0f00", accent: "#ff9500", label: "TASKS" },
    goals: { bg: "#1a001a", accent: "#da70d6", label: "GOALS" },
    health: { bg: "#0a1a0a", accent: "#00ff88", label: "HEALTH" },
    cors: { bg: "#1a1a00", accent: "#ffff00", label: "CORS" },
};

async function runTest(endpoint) {
    const start = performance.now();
    try {
        const opts =
            endpoint.method === "OPT"
                ? {
                    method: "OPTIONS",
                    headers: {
                        Origin: "http://localhost:5173",
                        "Access-Control-Request-Method": "GET",
                    },
                }
                : { method: endpoint.method };

        const res = await fetch(`${API_BASE}${endpoint.path}`, opts);
        const ms = Math.round(performance.now() - start);

        let body = null;
        try { body = await res.clone().json(); } catch (_) { }

        const corsHeader = res.headers.get("access-control-allow-origin");

        let pass = res.status < 400;
        let note = `HTTP ${res.status}`;

        if (endpoint.id === "cors") {
            pass = !!corsHeader;
            note = corsHeader ? `Origin allowed: ${corsHeader}` : "❌ CORS header missing — React will be blocked";
        }
        if (endpoint.id === "db") {
            pass = body?.status === "connected";
            note = body?.status === "connected" ? "SQLite connected" : body?.message || "DB error";
        }

        return { status: pass ? "pass" : "fail", code: res.status, ms, note, body };
    } catch (err) {
        const ms = Math.round(performance.now() - start);
        return {
            status: "error",
            code: 0,
            ms,
            note: err.message.includes("fetch") ? "Cannot reach server — is uvicorn running?" : err.message,
            body: null,
        };
    }
}

const statusColors = {
    pass: "#39ff14",
    fail: "#ff4444",
    error: "#ff6600",
    pending: "#555",
    running: "#00d4ff",
};

const statusLabels = {
    pass: "PASS",
    fail: "FAIL",
    error: "ERR",
    pending: "—",
    running: "...",
};

export default function ApiHealthDashboard() {
    const [results, setResults] = useState({});
    const [running, setRunning] = useState(false);
    const [lastRun, setLastRun] = useState(null);
    const [selected, setSelected] = useState(null);

    const runAll = useCallback(async () => {
        setRunning(true);
        setResults({});
        setSelected(null);

        for (const ep of ENDPOINTS) {
            setResults(prev => ({ ...prev, [ep.id]: { status: "running" } }));
            const result = await runTest(ep);
            setResults(prev => ({ ...prev, [ep.id]: result }));
        }

        setRunning(false);
        setLastRun(new Date());
    }, []);

    useEffect(() => { runAll(); }, []);

    const passed = Object.values(results).filter(r => r.status === "pass").length;
    const failed = Object.values(results).filter(r => r.status === "fail" || r.status === "error").length;
    const total = ENDPOINTS.length;
    const score = total > 0 ? Math.round((passed / total) * 100) : 0;

    const selectedEndpoint = selected ? ENDPOINTS.find(e => e.id === selected) : null;
    const selectedResult = selected ? results[selected] : null;

    return (
        <div style={{
            minHeight: "100vh",
            background: "#080808",
            color: "#e0e0e0",
            fontFamily: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace",
            padding: "32px",
        }}>
            {/* Google Font */}
            <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Bebas+Neue&display=swap" rel="stylesheet" />

            {/* Header */}
            <div style={{ marginBottom: 40 }}>
                <div style={{ display: "flex", alignItems: "baseline", gap: 16, marginBottom: 8 }}>
                    <h1 style={{
                        fontFamily: "'Bebas Neue', sans-serif",
                        fontSize: 48,
                        letterSpacing: 6,
                        color: "#fff",
                        margin: 0,
                    }}>VERYFYN</h1>
                    <span style={{ color: "#555", fontSize: 13, letterSpacing: 3 }}>API HEALTH MONITOR</span>
                </div>
                <div style={{ display: "flex", gap: 32, alignItems: "center" }}>
                    <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                        <div style={{
                            width: 8, height: 8, borderRadius: "50%",
                            background: running ? "#00d4ff" : score === 100 ? "#39ff14" : score > 50 ? "#ff9500" : "#ff4444",
                            boxShadow: `0 0 8px ${running ? "#00d4ff" : score === 100 ? "#39ff14" : "#ff4444"}`,
                            animation: running ? "pulse 1s infinite" : "none",
                        }} />
                        <span style={{ fontSize: 12, color: "#888" }}>
                            {running ? "RUNNING TESTS..." : lastRun ? `LAST RUN ${lastRun.toLocaleTimeString()}` : "READY"}
                        </span>
                    </div>
                    <div style={{ fontSize: 12, color: "#555" }}>
                        TARGET: <span style={{ color: "#00d4ff" }}>localhost:8000</span>
                        {" "}→{" "}
                        FRONTEND: <span style={{ color: "#39ff14" }}>localhost:5173</span>
                    </div>
                </div>
            </div>

            {/* Score Bar */}
            <div style={{
                background: "#111",
                border: "1px solid #222",
                borderRadius: 8,
                padding: "20px 24px",
                marginBottom: 32,
                display: "flex",
                alignItems: "center",
                gap: 40,
            }}>
                <div>
                    <div style={{
                        fontFamily: "'Bebas Neue', sans-serif",
                        fontSize: 64,
                        lineHeight: 1,
                        color: score === 100 ? "#39ff14" : score > 50 ? "#ff9500" : "#ff4444",
                    }}>{score}%</div>
                    <div style={{ fontSize: 11, color: "#555", letterSpacing: 2 }}>HEALTH SCORE</div>
                </div>
                <div style={{ flex: 1 }}>
                    <div style={{ height: 6, background: "#222", borderRadius: 3, overflow: "hidden", marginBottom: 12 }}>
                        <div style={{
                            height: "100%",
                            width: `${score}%`,
                            background: score === 100 ? "#39ff14" : score > 50 ? "#ff9500" : "#ff4444",
                            transition: "width 0.6s ease",
                            boxShadow: `0 0 12px ${score === 100 ? "#39ff14" : "#ff9500"}`,
                        }} />
                    </div>
                    <div style={{ display: "flex", gap: 24 }}>
                        {[
                            { label: "PASSED", val: passed, color: "#39ff14" },
                            { label: "FAILED", val: failed, color: "#ff4444" },
                            { label: "TOTAL", val: total, color: "#555" },
                        ].map(s => (
                            <div key={s.label}>
                                <span style={{ fontSize: 22, fontWeight: 700, color: s.color }}>{s.val}</span>
                                <span style={{ fontSize: 10, color: "#444", marginLeft: 6, letterSpacing: 2 }}>{s.label}</span>
                            </div>
                        ))}
                    </div>
                </div>
                <button
                    onClick={runAll}
                    disabled={running}
                    style={{
                        background: running ? "#111" : "#00d4ff11",
                        border: `1px solid ${running ? "#333" : "#00d4ff"}`,
                        color: running ? "#444" : "#00d4ff",
                        padding: "12px 24px",
                        borderRadius: 4,
                        fontFamily: "inherit",
                        fontSize: 12,
                        letterSpacing: 3,
                        cursor: running ? "not-allowed" : "pointer",
                        transition: "all 0.2s",
                    }}
                >
                    {running ? "RUNNING..." : "RE-RUN ALL"}
                </button>
            </div>

            {/* Test Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 32 }}>
                {ENDPOINTS.map(ep => {
                    const r = results[ep.id];
                    const cat = CATEGORY_COLORS[ep.category];
                    const isSelected = selected === ep.id;
                    const statusColor = statusColors[r?.status || "pending"];

                    return (
                        <div
                            key={ep.id}
                            onClick={() => setSelected(isSelected ? null : ep.id)}
                            style={{
                                background: isSelected ? cat.bg : "#0e0e0e",
                                border: `1px solid ${isSelected ? cat.accent : r?.status === "pass" ? "#1a3a1a" : r?.status === "error" || r?.status === "fail" ? "#3a1a1a" : "#1a1a1a"}`,
                                borderRadius: 6,
                                padding: "16px 20px",
                                cursor: "pointer",
                                transition: "all 0.2s",
                                position: "relative",
                                overflow: "hidden",
                            }}
                        >
                            {/* Category badge */}
                            <div style={{
                                position: "absolute", top: 10, right: 10,
                                fontSize: 9, letterSpacing: 2,
                                color: cat.accent, opacity: 0.6,
                            }}>{cat.label}</div>

                            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                                <div style={{
                                    width: 10, height: 10, borderRadius: "50%",
                                    background: statusColor,
                                    boxShadow: r?.status === "pass" ? `0 0 6px ${statusColor}` : "none",
                                    flexShrink: 0,
                                }} />
                                <span style={{ fontSize: 13, fontWeight: 700, color: "#ddd" }}>{ep.label}</span>
                            </div>

                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                <code style={{ fontSize: 10, color: "#555" }}>
                                    <span style={{ color: "#888" }}>{ep.method}</span> {ep.path}
                                </code>
                                <span style={{
                                    fontSize: 11, fontWeight: 700, letterSpacing: 1,
                                    color: statusColor,
                                }}>{statusLabels[r?.status || "pending"]}</span>
                            </div>

                            {r?.note && (
                                <div style={{ fontSize: 10, color: "#666", marginTop: 6, fontStyle: "italic" }}>
                                    {r.note}
                                </div>
                            )}

                            {r?.ms !== undefined && (
                                <div style={{ fontSize: 10, color: "#444", marginTop: 4 }}>
                                    {r.ms}ms
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Detail Panel */}
            {selectedResult && selectedEndpoint && (
                <div style={{
                    background: "#0e0e0e",
                    border: `1px solid ${CATEGORY_COLORS[selectedEndpoint.category].accent}44`,
                    borderRadius: 8,
                    padding: "24px",
                    marginBottom: 32,
                }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
                        <div>
                            <span style={{
                                fontFamily: "'Bebas Neue', sans-serif",
                                fontSize: 20,
                                letterSpacing: 3,
                                color: CATEGORY_COLORS[selectedEndpoint.category].accent,
                            }}>{selectedEndpoint.label}</span>
                            <span style={{ marginLeft: 12, fontSize: 11, color: "#555" }}>
                                {selectedEndpoint.method} {API_BASE}{selectedEndpoint.path}
                            </span>
                        </div>
                        <span style={{
                            fontSize: 13, fontWeight: 700,
                            color: statusColors[selectedResult.status],
                        }}>{statusLabels[selectedResult.status]}</span>
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 16 }}>
                        {[
                            { label: "STATUS CODE", val: selectedResult.code || "—" },
                            { label: "RESPONSE TIME", val: selectedResult.ms !== undefined ? `${selectedResult.ms}ms` : "—" },
                            { label: "NOTE", val: selectedResult.note || "—" },
                        ].map(item => (
                            <div key={item.label} style={{ background: "#111", padding: "12px 16px", borderRadius: 4 }}>
                                <div style={{ fontSize: 9, letterSpacing: 2, color: "#555", marginBottom: 4 }}>{item.label}</div>
                                <div style={{ fontSize: 13, color: "#ccc" }}>{item.val}</div>
                            </div>
                        ))}
                    </div>

                    {selectedResult.body && (
                        <div>
                            <div style={{ fontSize: 9, letterSpacing: 2, color: "#555", marginBottom: 8 }}>RESPONSE BODY</div>
                            <pre style={{
                                background: "#060606",
                                border: "1px solid #1a1a1a",
                                borderRadius: 4,
                                padding: 16,
                                fontSize: 11,
                                color: "#7ec8e3",
                                overflow: "auto",
                                maxHeight: 200,
                                margin: 0,
                            }}>
                                {JSON.stringify(selectedResult.body, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            )}

            {/* Checklist */}
            <div style={{
                background: "#0e0e0e",
                border: "1px solid #1a1a1a",
                borderRadius: 8,
                padding: "24px",
            }}>
                <div style={{ fontSize: 11, letterSpacing: 3, color: "#555", marginBottom: 16 }}>INTEGRATION CHECKLIST</div>
                {[
                    { id: "server", label: "FastAPI server running on :8000", check: () => results.root?.status === "pass" },
                    { id: "db", label: "SQLite database connected", check: () => results.db?.status === "pass" },
                    { id: "cors", label: "CORS allows localhost:5173 (React dev)", check: () => results.cors?.status === "pass" },
                    { id: "habits", label: "Habits API responding", check: () => results.habits?.status === "pass" },
                    { id: "tasks", label: "Tasks API responding", check: () => results.tasks?.status === "pass" },
                    { id: "goals", label: "Goals API responding", check: () => results.goals?.status === "pass" },
                    { id: "healthm", label: "Health metrics API responding", check: () => results.healthm?.status === "pass" },
                    { id: "docs", label: "API docs at /docs for development", check: () => results.docs?.status === "pass" },
                ].map(item => {
                    const ok = item.check();
                    return (
                        <div key={item.id} style={{
                            display: "flex", alignItems: "center", gap: 12,
                            padding: "8px 0",
                            borderBottom: "1px solid #111",
                            fontSize: 12,
                        }}>
                            <span style={{ color: ok ? "#39ff14" : "#444", fontSize: 16 }}>{ok ? "✓" : "○"}</span>
                            <span style={{ color: ok ? "#aaa" : "#555" }}>{item.label}</span>
                        </div>
                    );
                })}
            </div>

            <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
        </div>
    );
}
