"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import { Building2, Users, Box, Globe, Plus } from "lucide-react";
import { mockInternalData, formatNumber } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function TenantsPage() {
  const { tenants } = mockInternalData;

  useCopilotReadable({
    description: "Multi-tenant configuration and user management",
    value: tenants,
  });

  const totalUsers = tenants.reduce((sum, t) => sum + t.users, 0);
  const activeTenants = tenants.filter(t => t.status === 'active').length;

  const moduleColors: Record<string, string> = {
    'creditx': 'bg-emerald-100 text-emerald-700',
    '91apps': 'bg-blue-100 text-blue-700',
    'guardian': 'bg-purple-100 text-purple-700',
    'global-ai-alert': 'bg-red-100 text-red-700',
    'market': 'bg-amber-100 text-amber-700',
  };

  return (
    <div className="max-w-7xl mx-auto">
      <PageHeader
        title="Tenant Management"
        description="Manage multi-tenant configurations, modules, and user access"
        actions={
          <button className="flex items-center gap-2 px-4 py-2 bg-internal text-white rounded-lg hover:opacity-90 transition-opacity">
            <Plus className="w-4 h-4" />
            Add Tenant
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Tenants"
          value={tenants.length}
          subtitle="Organizations"
          icon={<Building2 className="w-5 h-5 text-internal" />}
          color="internal"
        />
        <MetricCard
          title="Active"
          value={activeTenants}
          subtitle="Live tenants"
          icon={<Globe className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
        <MetricCard
          title="Total Users"
          value={formatNumber(totalUsers)}
          subtitle="Across all tenants"
          icon={<Users className="w-5 h-5 text-blue-500" />}
        />
        <MetricCard
          title="Modules Deployed"
          value={5}
          subtitle="Available modules"
          icon={<Box className="w-5 h-5 text-purple-500" />}
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-slate-800">All Tenants</h2>
        </div>
        <div className="p-4">
          <div className="space-y-4">
            {tenants.map((tenant) => (
              <div
                key={tenant.id}
                className="p-4 border rounded-lg hover:border-internal/30 hover:bg-slate-50 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-slate-800">{tenant.name}</h3>
                      <StatusBadge status={tenant.status} />
                    </div>
                    <p className="text-sm text-slate-500 mb-3">{tenant.domain}</p>
                    <div className="flex flex-wrap gap-2">
                      {tenant.modules.map((module) => (
                        <span
                          key={module}
                          className={`px-2 py-1 rounded text-xs font-medium ${moduleColors[module] || 'bg-slate-100 text-slate-600'}`}
                        >
                          {module}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1 text-slate-600">
                      <Users className="w-4 h-4" />
                      <span className="font-medium">{tenant.users}</span>
                      <span className="text-sm">users</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="font-semibold text-slate-800 mb-4">Module Usage</h3>
          <div className="space-y-3">
            {Object.keys(moduleColors).map((module) => {
              const count = tenants.filter(t => t.modules.includes(module)).length;
              const percentage = (count / tenants.length) * 100;
              return (
                <div key={module}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-slate-600">{module}</span>
                    <span className="text-sm font-medium text-slate-800">{count} tenants</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-internal rounded-full"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="font-semibold text-slate-800 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <button className="w-full text-left p-3 hover:bg-slate-50 rounded-lg text-slate-700 flex items-center gap-3">
              <Building2 className="w-5 h-5 text-slate-400" />
              Create New Tenant
            </button>
            <button className="w-full text-left p-3 hover:bg-slate-50 rounded-lg text-slate-700 flex items-center gap-3">
              <Box className="w-5 h-5 text-slate-400" />
              Manage Modules
            </button>
            <button className="w-full text-left p-3 hover:bg-slate-50 rounded-lg text-slate-700 flex items-center gap-3">
              <Users className="w-5 h-5 text-slate-400" />
              Bulk User Import
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
