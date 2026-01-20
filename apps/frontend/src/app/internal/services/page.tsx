"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import { Server, Activity, Cpu, HardDrive, Zap, RefreshCw } from "lucide-react";
import { mockInternalData, formatNumber } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function ServicesPage() {
  const { services, systemStats } = mockInternalData;

  useCopilotReadable({
    description: "Microservice health status and metrics",
    value: { services, systemStats },
  });

  const healthyCount = services.filter(s => s.status === 'healthy').length;
  const totalRequests = services.reduce((sum, s) => sum + s.requests, 0);
  const avgCpu = Math.round(services.reduce((sum, s) => sum + s.cpu, 0) / services.length);
  const avgMemory = Math.round(services.reduce((sum, s) => sum + s.memory, 0) / services.length);

  return (
    <div className="max-w-7xl mx-auto">
      <PageHeader
        title="Service Health"
        description="Monitor microservice status, performance, and resource utilization"
        actions={
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Services Health"
          value={`${healthyCount}/${services.length}`}
          subtitle="Healthy"
          icon={<Server className="w-5 h-5 text-emerald-500" />}
          color={healthyCount === services.length ? "success" : "warning"}
        />
        <MetricCard
          title="Total Requests"
          value={formatNumber(totalRequests)}
          subtitle="Last 24 hours"
          icon={<Zap className="w-5 h-5 text-blue-500" />}
        />
        <MetricCard
          title="Avg CPU Usage"
          value={`${avgCpu}%`}
          subtitle="Across services"
          icon={<Cpu className="w-5 h-5 text-amber-500" />}
          color={avgCpu > 70 ? "warning" : "default"}
        />
        <MetricCard
          title="Avg Memory"
          value={`${avgMemory}%`}
          subtitle="Utilization"
          icon={<HardDrive className="w-5 h-5 text-purple-500" />}
          color={avgMemory > 80 ? "warning" : "default"}
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-slate-800">Service Status</h2>
        </div>
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {services.map((service) => (
              <div
                key={service.name}
                className={`p-4 rounded-lg border ${
                  service.status === 'healthy' ? 'border-emerald-200 bg-emerald-50' :
                  service.status === 'degraded' ? 'border-amber-200 bg-amber-50' :
                  'border-red-200 bg-red-50'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${
                      service.status === 'healthy' ? 'bg-emerald-500' :
                      service.status === 'degraded' ? 'bg-amber-500' : 'bg-red-500'
                    }`} />
                    <span className="font-semibold text-slate-800">{service.name}</span>
                  </div>
                  <StatusBadge status={service.status} />
                </div>
                
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-slate-500">Latency</p>
                    <p className={`font-medium ${service.latency > 100 ? 'text-amber-600' : 'text-slate-700'}`}>
                      {service.latency}ms
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-500">Requests</p>
                    <p className="font-medium text-slate-700">{formatNumber(service.requests)}</p>
                  </div>
                  <div>
                    <p className="text-slate-500">CPU</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            service.cpu > 70 ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${service.cpu}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-600">{service.cpu}%</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-slate-500">Memory</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            service.memory > 80 ? 'bg-red-500' : service.memory > 60 ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${service.memory}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-600">{service.memory}%</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">System Metrics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-sm text-slate-500">Uptime</p>
            <p className="text-2xl font-bold text-emerald-600">{systemStats.uptime}%</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Requests Today</p>
            <p className="text-2xl font-bold text-slate-800">{formatNumber(systemStats.requestsToday)}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Avg Latency</p>
            <p className="text-2xl font-bold text-slate-800">{systemStats.avgLatency}ms</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Active Agents</p>
            <p className="text-2xl font-bold text-internal">{systemStats.activeAgents}/{systemStats.totalAgents}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
