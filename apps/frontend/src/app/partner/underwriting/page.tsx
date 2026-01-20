"use client";

import { useState } from "react";
import { useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";
import { FileCheck, Clock, CheckCircle, XCircle } from "lucide-react";
import { mockPartnerData, formatCurrency, formatDate } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function UnderwritingPage() {
  const [applications] = useState(mockPartnerData.underwriting);

  useCopilotReadable({
    description: "Underwriting applications queue",
    value: applications,
  });

  useCopilotAction({
    name: "approveApplication",
    description: "Approve an underwriting application",
    parameters: [
      { name: "applicationId", type: "string", required: true },
      { name: "apr", type: "number", description: "The APR to offer", required: true },
    ],
    handler: async ({ applicationId, apr }) => {
      return `Application ${applicationId} approved at ${apr}% APR. The borrower will be notified within 24 hours.`;
    },
  });

  const pending = applications.filter(a => a.status === 'pending_review').length;
  const approved = applications.filter(a => a.status === 'approved').length;
  const declined = applications.filter(a => a.status === 'declined').length;

  return (
    <div className="max-w-7xl mx-auto">
      <PageHeader
        title="Underwriting Queue"
        description="Review and process loan applications"
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Pending Review"
          value={pending}
          subtitle="Awaiting decision"
          icon={<Clock className="w-5 h-5 text-amber-500" />}
          color="warning"
        />
        <MetricCard
          title="Approved"
          value={approved}
          subtitle="This week"
          icon={<CheckCircle className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
        <MetricCard
          title="Declined"
          value={declined}
          subtitle="This week"
          icon={<XCircle className="w-5 h-5 text-red-500" />}
        />
        <MetricCard
          title="Avg Decision Time"
          value="4.2h"
          subtitle="Time to decision"
          icon={<FileCheck className="w-5 h-5 text-blue-500" />}
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-slate-800">Applications</h2>
        </div>
        <div className="p-4 space-y-4">
          {applications.map((app) => (
            <div
              key={app.id}
              className={`p-4 border rounded-lg ${
                app.status === 'pending_review' ? 'border-amber-200 bg-amber-50' :
                app.status === 'pending_docs' ? 'border-blue-200 bg-blue-50' :
                'bg-white'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-semibold text-slate-800">{app.id}</span>
                    <StatusBadge status={app.status} />
                    <StatusBadge status={app.riskTier} />
                  </div>
                  <p className="text-lg font-medium text-slate-700">{app.applicant}</p>
                  <div className="flex items-center gap-6 mt-2 text-sm text-slate-500">
                    <span>Amount: {formatCurrency(app.amount)}</span>
                    <span>Score: {app.score}</span>
                    <span>Submitted: {formatDate(app.submitted)}</span>
                    {app.apr && <span className="text-emerald-600 font-medium">APR: {app.apr}%</span>}
                  </div>
                  {app.reason && (
                    <p className="mt-2 text-sm text-red-600">Reason: {app.reason}</p>
                  )}
                </div>
                {app.status === 'pending_review' && (
                  <div className="flex items-center gap-2 ml-4">
                    <button className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                      Decline
                    </button>
                    <button className="px-4 py-2 bg-partner text-white rounded-lg hover:opacity-90 transition-opacity">
                      Approve
                    </button>
                  </div>
                )}
                {app.status === 'pending_docs' && (
                  <button className="px-4 py-2 border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
                    Request Docs
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
