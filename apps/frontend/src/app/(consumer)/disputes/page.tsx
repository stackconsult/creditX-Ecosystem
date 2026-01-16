"use client";

import { useState } from "react";
import { useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";
import { FileWarning, Plus, Clock, CheckCircle } from "lucide-react";
import { mockConsumerData, formatDate } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function DisputesPage() {
  const [disputes] = useState(mockConsumerData.disputes);
  const [showForm, setShowForm] = useState(false);

  useCopilotReadable({
    description: "Consumer's dispute history and status",
    value: disputes,
  });

  useCopilotAction({
    name: "fileDispute",
    description: "Help the user file a new dispute",
    parameters: [
      { name: "bureau", type: "string", description: "Credit bureau (Experian, TransUnion, Equifax)", required: true },
      { name: "item", type: "string", description: "The item being disputed", required: true },
    ],
    handler: async ({ bureau, item }) => {
      return `I'll help you file a dispute with ${bureau} regarding "${item}". The dispute process typically takes 30-45 days. Would you like me to draft the dispute letter using FCRA-compliant language?`;
    },
  });

  const activeDisputes = disputes.filter(d => d.status === 'in_progress').length;
  const resolvedDisputes = disputes.filter(d => d.status === 'resolved').length;

  return (
    <div className="max-w-6xl mx-auto">
      <PageHeader
        title="Disputes"
        description="Manage credit report disputes and track their status"
        actions={
          <button 
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 bg-consumer text-white rounded-lg hover:opacity-90"
          >
            <Plus className="w-4 h-4" />
            New Dispute
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Active Disputes"
          value={activeDisputes}
          subtitle="In progress"
          icon={<Clock className="w-5 h-5 text-amber-500" />}
          color="warning"
        />
        <MetricCard
          title="Resolved"
          value={resolvedDisputes}
          subtitle="Completed"
          icon={<CheckCircle className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
        <MetricCard
          title="Items Removed"
          value={disputes.filter(d => d.outcome === 'removed').length}
          subtitle="Successfully disputed"
          color="success"
        />
        <MetricCard
          title="Avg Resolution"
          value="28 days"
          subtitle="Processing time"
        />
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">File New Dispute</h2>
          <form className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Credit Bureau</label>
                <select className="w-full px-3 py-2 border rounded-lg">
                  <option>Experian</option>
                  <option>TransUnion</option>
                  <option>Equifax</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Dispute Type</label>
                <select className="w-full px-3 py-2 border rounded-lg">
                  <option>Incorrect Information</option>
                  <option>Not My Account</option>
                  <option>Duplicate Entry</option>
                  <option>Outdated Information</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Item to Dispute</label>
              <input type="text" className="w-full px-3 py-2 border rounded-lg" placeholder="e.g., Late payment on Chase account" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Explanation</label>
              <textarea className="w-full px-3 py-2 border rounded-lg" rows={3} placeholder="Describe why this information is incorrect..." />
            </div>
            <div className="flex gap-3">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border rounded-lg text-slate-700 hover:bg-slate-50">
                Cancel
              </button>
              <button type="submit" className="px-4 py-2 bg-consumer text-white rounded-lg hover:opacity-90">
                Submit Dispute
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-slate-800">Dispute History</h2>
        </div>
        <div className="p-4 space-y-4">
          {disputes.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <FileWarning className="w-12 h-12 mx-auto mb-3 text-slate-300" />
              <p>No disputes filed yet</p>
            </div>
          ) : (
            disputes.map((dispute) => (
              <div key={dispute.id} className="p-4 border rounded-lg hover:border-consumer/30 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-slate-800">{dispute.id}</span>
                      <StatusBadge status={dispute.status} />
                    </div>
                    <p className="text-slate-700">{dispute.item}</p>
                    <div className="flex items-center gap-4 mt-2 text-sm text-slate-500">
                      <span>Bureau: {dispute.bureau}</span>
                      <span>Filed: {formatDate(dispute.filed)}</span>
                      {dispute.dueDate && <span>Due: {formatDate(dispute.dueDate)}</span>}
                    </div>
                  </div>
                  {dispute.outcome && (
                    <StatusBadge status={dispute.outcome} />
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
