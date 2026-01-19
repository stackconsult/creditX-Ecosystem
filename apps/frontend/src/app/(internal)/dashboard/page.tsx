"use client";

import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { useState, useEffect } from "react";

interface SystemStats {
  activeAgents: number;
  pendingHitl: number;
  threatsToday: number;
  complianceScore: number;
}

export default function InternalDashboard() {
  const [stats, setStats] = useState<SystemStats>({
    activeAgents: 18,
    pendingHitl: 3,
    threatsToday: 2,
    complianceScore: 94,
  });

  const [services, setServices] = useState([
    { name: "creditx-service", status: "healthy", latency: 45 },
    { name: "threat-service", status: "healthy", latency: 32 },
    { name: "guardian-service", status: "healthy", latency: 28 },
    { name: "apps-service", status: "degraded", latency: 120 },
    { name: "phones-service", status: "healthy", latency: 38 },
  ]);

  useCopilotReadable({
    description: "System-wide statistics and service health",
    value: { stats, services },
  });

  useCopilotAction({
    name: "approveHitl",
    description: "Approve a pending HITL request",
    parameters: [
      { name: "taskId", type: "string", description: "The task ID to approve" },
    ],
    handler: async ({ taskId }) => {
      return `HITL request ${taskId} has been approved. The agent will now continue execution.`;
    },
  });

  useCopilotAction({
    name: "getSystemStatus",
    description: "Get detailed system status and health metrics",
    parameters: [],
    handler: async () => {
      const healthyCount = services.filter(s => s.status === "healthy").length;
      return `System Status: ${healthyCount}/${services.length} services healthy. ${stats.activeAgents} agents active. ${stats.pendingHitl} HITL requests pending. Compliance score: ${stats.complianceScore}%.`;
    },
  });

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-800 mb-8">Internal Operations Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Active Agents</div>
          <div className="text-4xl font-bold text-internal">{stats.activeAgents}</div>
          <div className="text-sm text-slate-600 mt-2">of 22 total</div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Pending HITL</div>
          <div className="text-4xl font-bold text-red-500">{stats.pendingHitl}</div>
          <div className="text-sm text-slate-600 mt-2">Require approval</div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Threats Today</div>
          <div className="text-4xl font-bold text-orange-500">{stats.threatsToday}</div>
          <div className="text-sm text-slate-600 mt-2">Detected</div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Compliance Score</div>
          <div className="text-4xl font-bold text-emerald-500">{stats.complianceScore}%</div>
          <div className="text-sm text-slate-600 mt-2">Ecosystem-wide</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Service Health</h2>
          <div className="space-y-3">
            {services.map((service) => (
              <div key={service.name} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    service.status === "healthy" ? "bg-emerald-500" : "bg-amber-500"
                  }`} />
                  <span className="font-medium">{service.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`text-sm ${
                    service.status === "healthy" ? "text-emerald-600" : "text-amber-600"
                  }`}>
                    {service.status}
                  </span>
                  <span className="text-sm text-slate-500">{service.latency}ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Pending HITL Requests</h2>
          <div className="space-y-3">
            {[
              { id: "HITL-001", agent: "Underwriting Decision", risk: "high" },
              { id: "HITL-002", agent: "Rights Request Orchestrator", risk: "high" },
              { id: "HITL-003", agent: "Security Remediation", risk: "critical" },
            ].map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <div>
                  <div className="font-medium text-slate-800">{item.id}</div>
                  <div className="text-sm text-slate-600">{item.agent}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    item.risk === "critical" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"
                  }`}>
                    {item.risk}
                  </span>
                  <button className="px-3 py-1 bg-emerald-500 text-white rounded text-sm hover:bg-emerald-600">
                    Approve
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
