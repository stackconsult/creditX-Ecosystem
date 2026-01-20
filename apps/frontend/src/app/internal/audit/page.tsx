"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import { FileText, Shield, Download, Filter } from "lucide-react";
import { mockInternalData, formatDateTime } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function AuditPage() {
  const { auditLogs, systemStats } = mockInternalData;

  useCopilotReadable({
    description: "Audit logs and compliance events",
    value: auditLogs,
  });

  const columns = [
    { 
      key: "timestamp", 
      header: "Time", 
      sortable: true,
      render: (v: unknown) => formatDateTime(String(v))
    },
    { key: "id", header: "Event ID" },
    { 
      key: "action", 
      header: "Action",
      render: (v: unknown) => (
        <span className="font-medium text-slate-700">{String(v).replace(/_/g, ' ')}</span>
      )
    },
    { key: "agent", header: "Agent", render: (v: unknown) => v ? String(v) : <span className="text-slate-400">—</span> },
    { key: "user", header: "User" },
    { key: "status", header: "Status", render: (v: unknown) => <StatusBadge status={String(v)} /> },
  ];

  const actionCounts = auditLogs.reduce((acc, log) => {
    acc[log.action] = (acc[log.action] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="max-w-7xl mx-auto">
      <PageHeader
        title="Audit Logs"
        description="System-wide audit trail and compliance event tracking"
        actions={
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors">
              <Filter className="w-4 h-4" />
              Filter
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-internal text-white rounded-lg hover:opacity-90 transition-opacity">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Compliance Score"
          value={`${systemStats.complianceScore}%`}
          subtitle="Ecosystem-wide"
          icon={<Shield className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
        <MetricCard
          title="Total Events"
          value={auditLogs.length}
          subtitle="Last 24 hours"
          icon={<FileText className="w-5 h-5 text-blue-500" />}
        />
        <MetricCard
          title="Agent Executions"
          value={actionCounts['agent_execution'] || 0}
          subtitle="Logged"
        />
        <MetricCard
          title="HITL Decisions"
          value={actionCounts['hitl_approval'] || 0}
          subtitle="Recorded"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Recent Events</h2>
          </div>
          <div className="p-4">
            <DataTable data={auditLogs} columns={columns} />
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border p-4">
            <h3 className="font-semibold text-slate-800 mb-3">Event Types</h3>
            <div className="space-y-2">
              {Object.entries(actionCounts).map(([action, count]) => (
                <div key={action} className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">{action.replace(/_/g, ' ')}</span>
                  <span className="text-sm font-medium text-slate-800">{count}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-4">
            <h3 className="font-semibold text-slate-800 mb-3">Compliance Reports</h3>
            <div className="space-y-2">
              <button className="w-full text-left p-2 hover:bg-slate-50 rounded-lg text-sm text-slate-700">
                SOC 2 Type II Report
              </button>
              <button className="w-full text-left p-2 hover:bg-slate-50 rounded-lg text-sm text-slate-700">
                GDPR Compliance Audit
              </button>
              <button className="w-full text-left p-2 hover:bg-slate-50 rounded-lg text-sm text-slate-700">
                FCRA Evidence Package
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
