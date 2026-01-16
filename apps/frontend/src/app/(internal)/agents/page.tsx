"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import { Bot, Zap, Clock, Activity } from "lucide-react";
import { mockInternalData, formatNumber } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function AgentsPage() {
  const { agents } = mockInternalData;

  useCopilotReadable({
    description: "List of all 22 CreditX agents and their execution statistics",
    value: agents,
  });

  const engineGroups = agents.reduce((acc, agent) => {
    if (!acc[agent.engine]) acc[agent.engine] = [];
    acc[agent.engine].push(agent);
    return acc;
  }, {} as Record<string, typeof agents>);

  const totalExecutions = agents.reduce((sum, a) => sum + a.executions, 0);
  const avgResponseTime = Math.round(agents.reduce((sum, a) => sum + a.avgTime, 0) / agents.length);

  const columns = [
    { key: "name", header: "Agent Name", sortable: true },
    { key: "id", header: "Agent ID", render: (v: unknown) => <code className="text-xs bg-slate-100 px-2 py-1 rounded">{String(v)}</code> },
    { key: "type", header: "Type", render: (v: unknown) => <StatusBadge status={String(v)} /> },
    { key: "status", header: "Status", render: (v: unknown) => <StatusBadge status={String(v)} /> },
    { key: "executions", header: "Executions", sortable: true, render: (v: unknown) => formatNumber(Number(v)) },
    { key: "avgTime", header: "Avg Time", sortable: true, render: (v: unknown) => `${v}ms` },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      <PageHeader
        title="Agent Management"
        description="Monitor and manage all 22 CreditX agents across 4 engines"
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Active Agents"
          value={`${agents.filter(a => a.status === 'active').length}/${agents.length}`}
          subtitle="Running"
          icon={<Bot className="w-5 h-5 text-internal" />}
          color="internal"
        />
        <MetricCard
          title="Total Executions"
          value={formatNumber(totalExecutions)}
          subtitle="All time"
          icon={<Zap className="w-5 h-5 text-amber-500" />}
        />
        <MetricCard
          title="Avg Response Time"
          value={`${avgResponseTime}ms`}
          subtitle="Across all agents"
          icon={<Clock className="w-5 h-5 text-blue-500" />}
        />
        <MetricCard
          title="Success Rate"
          value="99.2%"
          subtitle="Last 24 hours"
          trend={0.3}
          icon={<Activity className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
      </div>

      {Object.entries(engineGroups).map(([engine, engineAgents]) => (
        <div key={engine} className="bg-white rounded-xl shadow-sm border mb-6">
          <div className="p-4 border-b bg-slate-50 rounded-t-xl">
            <h2 className="text-lg font-semibold text-slate-800">{engine} Engine</h2>
            <p className="text-sm text-slate-500">{engineAgents.length} agents</p>
          </div>
          <div className="p-4">
            <DataTable data={engineAgents} columns={columns} />
          </div>
        </div>
      ))}
    </div>
  );
}
