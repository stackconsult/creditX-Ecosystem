"use client";

import { useState } from "react";
import { useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";
import { Shield, Download, Trash2, Lock, FileText, Plus } from "lucide-react";
import { mockConsumerData, formatDateTime } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function RightsPage() {
  const [requests] = useState(mockConsumerData.rightsRequests);
  const [showForm, setShowForm] = useState(false);
  const [requestType, setRequestType] = useState<string>("");

  useCopilotReadable({
    description: "Consumer's data rights requests and consent status",
    value: requests,
  });

  useCopilotAction({
    name: "requestDataExport",
    description: "Help the user request an export of their data",
    handler: async () => {
      return "I'll help you request a data export. Under CCPA/GDPR, you have the right to receive a copy of all personal data we hold about you. The export typically takes 2-3 business days to prepare. Would you like me to initiate this request?";
    },
  });

  useCopilotAction({
    name: "requestDataDeletion",
    description: "Help the user request deletion of their data",
    handler: async () => {
      return "I can help you request data deletion. Please note that some data may need to be retained for legal compliance (e.g., financial records). Would you like me to explain what data can be deleted and what must be retained?";
    },
  });

  return (
    <div className="max-w-6xl mx-auto">
      <PageHeader
        title="Data Rights"
        description="Manage your data privacy and consent preferences"
        actions={
          <button 
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 bg-consumer text-white rounded-lg hover:opacity-90"
          >
            <Plus className="w-4 h-4" />
            New Request
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <MetricCard
          title="Data Exports"
          value={requests.filter(r => r.type === 'export').length}
          subtitle="Completed"
          icon={<Download className="w-5 h-5 text-blue-500" />}
        />
        <MetricCard
          title="Active Consents"
          value={3}
          subtitle="Partners with access"
          icon={<Shield className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
        <MetricCard
          title="Pending Requests"
          value={requests.filter(r => r.status === 'pending').length}
          subtitle="In processing"
        />
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Submit Data Rights Request</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <button
              onClick={() => setRequestType('export')}
              className={`p-4 border rounded-lg text-left transition-colors ${
                requestType === 'export' ? 'border-consumer bg-consumer/5' : 'hover:border-slate-300'
              }`}
            >
              <Download className={`w-6 h-6 mb-2 ${requestType === 'export' ? 'text-consumer' : 'text-slate-400'}`} />
              <p className="font-medium text-slate-800">Export Data</p>
              <p className="text-sm text-slate-500">Get a copy of your data</p>
            </button>
            <button
              onClick={() => setRequestType('delete')}
              className={`p-4 border rounded-lg text-left transition-colors ${
                requestType === 'delete' ? 'border-consumer bg-consumer/5' : 'hover:border-slate-300'
              }`}
            >
              <Trash2 className={`w-6 h-6 mb-2 ${requestType === 'delete' ? 'text-consumer' : 'text-slate-400'}`} />
              <p className="font-medium text-slate-800">Delete Data</p>
              <p className="text-sm text-slate-500">Request data deletion</p>
            </button>
            <button
              onClick={() => setRequestType('restrict')}
              className={`p-4 border rounded-lg text-left transition-colors ${
                requestType === 'restrict' ? 'border-consumer bg-consumer/5' : 'hover:border-slate-300'
              }`}
            >
              <Lock className={`w-6 h-6 mb-2 ${requestType === 'restrict' ? 'text-consumer' : 'text-slate-400'}`} />
              <p className="font-medium text-slate-800">Restrict Processing</p>
              <p className="text-sm text-slate-500">Limit how data is used</p>
            </button>
          </div>
          {requestType && (
            <div className="flex gap-3">
              <button onClick={() => { setShowForm(false); setRequestType(""); }} className="px-4 py-2 border rounded-lg text-slate-700 hover:bg-slate-50">
                Cancel
              </button>
              <button className="px-4 py-2 bg-consumer text-white rounded-lg hover:opacity-90">
                Submit Request
              </button>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Request History</h2>
          </div>
          <div className="p-4 space-y-3">
            {requests.length === 0 ? (
              <p className="text-center py-8 text-slate-500">No requests yet</p>
            ) : (
              requests.map((request) => (
                <div key={request.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {request.type === 'export' && <Download className="w-4 h-4 text-blue-500" />}
                      {request.type === 'delete' && <Trash2 className="w-4 h-4 text-red-500" />}
                      {request.type === 'restrict' && <Lock className="w-4 h-4 text-amber-500" />}
                      <span className="font-medium text-slate-800 capitalize">{request.type} Request</span>
                    </div>
                    <StatusBadge status={request.status} />
                  </div>
                  <div className="text-sm text-slate-500">
                    <p>Requested: {formatDateTime(request.requestedAt)}</p>
                    {request.completedAt && <p>Completed: {formatDateTime(request.completedAt)}</p>}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Active Consents</h2>
          </div>
          <div className="p-4 space-y-3">
            {[
              { partner: "Apex Lending", purpose: "Underwriting", granted: "2025-06-15", expires: "2026-06-15" },
              { partner: "Credit Karma", purpose: "Credit Monitoring", granted: "2024-01-10", expires: "2025-01-10" },
              { partner: "Nuvei Finance", purpose: "Loan Offers", granted: "2025-09-20", expires: "2026-09-20" },
            ].map((consent, idx) => (
              <div key={idx} className="p-4 border rounded-lg flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-800">{consent.partner}</p>
                  <p className="text-sm text-slate-500">{consent.purpose}</p>
                  <p className="text-xs text-slate-400 mt-1">Expires: {consent.expires}</p>
                </div>
                <button className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                  Revoke
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 bg-slate-50 border rounded-xl p-6">
        <div className="flex items-start gap-4">
          <FileText className="w-6 h-6 text-slate-400 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-slate-800">Your Data Rights</h3>
            <p className="text-sm text-slate-600 mt-1">
              Under CCPA, GDPR, and FCRA, you have the right to access, correct, delete, and port your personal data. 
              You can also restrict processing and withdraw consent at any time. All requests are processed within 30 days.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
