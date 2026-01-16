"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import { Shield, Scale, FileCheck, AlertCircle, Download } from "lucide-react";
import { mockPartnerData } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function CompliancePage() {
  const { complianceScore, fairnessScore, riskDistribution } = mockPartnerData;

  useCopilotReadable({
    description: "Compliance and fairness metrics",
    value: { complianceScore, fairnessScore, riskDistribution },
  });

  return (
    <div className="max-w-7xl mx-auto">
      <PageHeader
        title="Compliance & Fairness"
        description="Regulatory compliance and fair lending metrics"
        actions={
          <button className="flex items-center gap-2 px-4 py-2 bg-partner text-white rounded-lg hover:opacity-90">
            <Download className="w-4 h-4" />
            Export Report
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Compliance Score"
          value={`${complianceScore}%`}
          subtitle="Overall rating"
          icon={<Shield className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
        <MetricCard
          title="Fairness Score"
          value={`${fairnessScore}%`}
          subtitle="Fair lending"
          icon={<Scale className="w-5 h-5 text-blue-500" />}
          color={fairnessScore >= 90 ? "success" : "warning"}
        />
        <MetricCard
          title="Open Issues"
          value={2}
          subtitle="Requiring action"
          icon={<AlertCircle className="w-5 h-5 text-amber-500" />}
          color="warning"
        />
        <MetricCard
          title="Last Audit"
          value="Jan 10"
          subtitle="2026"
          icon={<FileCheck className="w-5 h-5 text-slate-500" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Compliance Checks</h2>
          </div>
          <div className="p-4 space-y-3">
            {[
              { check: "FCRA Compliance", status: "passed", date: "2026-01-15" },
              { check: "ECOA Fair Lending", status: "passed", date: "2026-01-15" },
              { check: "TILA Disclosure", status: "passed", date: "2026-01-15" },
              { check: "State Licensing", status: "passed", date: "2026-01-10" },
              { check: "UDAAP Review", status: "warning", date: "2026-01-10" },
              { check: "Privacy Policy", status: "passed", date: "2026-01-08" },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-3">
                  {item.status === 'passed' ? (
                    <div className="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center">
                      <FileCheck className="w-4 h-4 text-emerald-600" />
                    </div>
                  ) : (
                    <div className="w-6 h-6 bg-amber-100 rounded-full flex items-center justify-center">
                      <AlertCircle className="w-4 h-4 text-amber-600" />
                    </div>
                  )}
                  <span className="font-medium text-slate-700">{item.check}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-slate-500">{item.date}</span>
                  <StatusBadge status={item.status} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Fairness Metrics</h2>
          </div>
          <div className="p-4 space-y-4">
            {[
              { metric: "Approval Rate Parity", value: 94, threshold: 90 },
              { metric: "Pricing Disparity", value: 97, threshold: 95 },
              { metric: "Adverse Action Accuracy", value: 99, threshold: 98 },
              { metric: "Data Quality Score", value: 96, threshold: 95 },
            ].map((item, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-700">{item.metric}</span>
                  <span className={`font-semibold ${item.value >= item.threshold ? 'text-emerald-600' : 'text-amber-600'}`}>
                    {item.value}%
                  </span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${item.value >= item.threshold ? 'bg-emerald-500' : 'bg-amber-500'}`}
                    style={{ width: `${item.value}%` }}
                  />
                </div>
                <p className="text-xs text-slate-400 mt-1">Threshold: {item.threshold}%</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-slate-800">Compliance Calendar</h2>
        </div>
        <div className="p-4">
          <div className="space-y-3">
            {[
              { event: "Quarterly Compliance Review", date: "2026-01-21", status: "upcoming", days: 5 },
              { event: "Annual Fair Lending Analysis", date: "2026-03-15", status: "scheduled", days: 58 },
              { event: "State License Renewal - CA", date: "2026-06-30", status: "scheduled", days: 165 },
              { event: "Privacy Policy Update", date: "2026-12-31", status: "scheduled", days: 349 },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium text-slate-800">{item.event}</p>
                  <p className="text-sm text-slate-500">{item.date}</p>
                </div>
                <div className="text-right">
                  <StatusBadge status={item.status} />
                  <p className="text-sm text-slate-500 mt-1">in {item.days} days</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
