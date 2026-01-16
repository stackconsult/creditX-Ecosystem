"use client";

import { useState } from "react";
import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react";
import { mockInternalData, formatCurrency } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function HitlPage() {
  const [queue, setQueue] = useState(mockInternalData.hitlQueue);
  const [history, setHistory] = useState<Array<{id: string; agent: string; decision: string; decidedAt: string}>>([]);

  useCopilotReadable({
    description: "Pending HITL (Human-in-the-Loop) approval requests",
    value: queue,
  });

  useCopilotAction({
    name: "approveHitlRequest",
    description: "Approve a pending HITL request by ID",
    parameters: [
      { name: "requestId", type: "string", description: "The HITL request ID to approve", required: true },
    ],
    handler: async ({ requestId }) => {
      const request = queue.find(r => r.id === requestId);
      if (!request) return `Request ${requestId} not found`;
      
      setQueue(prev => prev.filter(r => r.id !== requestId));
      setHistory(prev => [...prev, { id: requestId, agent: request.agent, decision: 'approved', decidedAt: new Date().toISOString() }]);
      return `Approved HITL request ${requestId} for ${request.agent}`;
    },
  });

  useCopilotAction({
    name: "rejectHitlRequest",
    description: "Reject a pending HITL request by ID",
    parameters: [
      { name: "requestId", type: "string", description: "The HITL request ID to reject", required: true },
    ],
    handler: async ({ requestId }) => {
      const request = queue.find(r => r.id === requestId);
      if (!request) return `Request ${requestId} not found`;
      
      setQueue(prev => prev.filter(r => r.id !== requestId));
      setHistory(prev => [...prev, { id: requestId, agent: request.agent, decision: 'rejected', decidedAt: new Date().toISOString() }]);
      return `Rejected HITL request ${requestId}`;
    },
  });

  const handleApprove = (id: string) => {
    const request = queue.find(r => r.id === id);
    if (request) {
      setQueue(prev => prev.filter(r => r.id !== id));
      setHistory(prev => [...prev, { id, agent: request.agent, decision: 'approved', decidedAt: new Date().toISOString() }]);
    }
  };

  const handleReject = (id: string) => {
    const request = queue.find(r => r.id === id);
    if (request) {
      setQueue(prev => prev.filter(r => r.id !== id));
      setHistory(prev => [...prev, { id, agent: request.agent, decision: 'rejected', decidedAt: new Date().toISOString() }]);
    }
  };

  const criticalCount = queue.filter(r => r.risk === 'critical').length;
  const highCount = queue.filter(r => r.risk === 'high').length;
  const avgWaitTime = queue.length > 0 ? Math.round(queue.reduce((sum, r) => sum + r.waitTime, 0) / queue.length) : 0;

  return (
    <div className="max-w-7xl mx-auto">
      <PageHeader
        title="HITL Approval Queue"
        description="Human-in-the-Loop approval requests for high-risk agent actions"
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Pending Requests"
          value={queue.length}
          subtitle="Awaiting decision"
          icon={<Clock className="w-5 h-5 text-amber-500" />}
          color={queue.length > 5 ? "warning" : "default"}
        />
        <MetricCard
          title="Critical"
          value={criticalCount}
          subtitle="Immediate attention"
          icon={<AlertTriangle className="w-5 h-5 text-red-500" />}
          color={criticalCount > 0 ? "error" : "default"}
        />
        <MetricCard
          title="High Risk"
          value={highCount}
          subtitle="Review required"
          icon={<AlertTriangle className="w-5 h-5 text-orange-500" />}
          color={highCount > 0 ? "warning" : "default"}
        />
        <MetricCard
          title="Avg Wait Time"
          value={`${avgWaitTime}m`}
          subtitle="Minutes pending"
          icon={<Clock className="w-5 h-5 text-blue-500" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Pending Approvals</h2>
          </div>
          <div className="p-4 space-y-4">
            {queue.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <CheckCircle className="w-12 h-12 mx-auto mb-3 text-emerald-500" />
                <p>All caught up! No pending requests.</p>
              </div>
            ) : (
              queue.map((request) => (
                <div
                  key={request.id}
                  className={`p-4 rounded-lg border-l-4 ${
                    request.risk === 'critical' ? 'border-l-red-500 bg-red-50' :
                    request.risk === 'high' ? 'border-l-orange-500 bg-orange-50' :
                    'border-l-amber-500 bg-amber-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-slate-800">{request.id}</span>
                        <StatusBadge status={request.risk} />
                      </div>
                      <p className="text-sm text-slate-700 font-medium">{request.agent}</p>
                      <p className="text-sm text-slate-600 mt-1">{request.task}</p>
                      <div className="flex items-center gap-4 mt-2 text-sm text-slate-500">
                        <span>Target: {request.consumer}</span>
                        {request.amount && <span>Amount: {formatCurrency(request.amount)}</span>}
                        <span>Waiting: {request.waitTime}m</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => handleReject(request.id)}
                        className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                        title="Reject"
                      >
                        <XCircle className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleApprove(request.id)}
                        className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors flex items-center gap-2"
                      >
                        <CheckCircle className="w-4 h-4" />
                        Approve
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Recent Decisions</h2>
          </div>
          <div className="p-4 space-y-3">
            {history.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8">No decisions yet</p>
            ) : (
              history.slice(-10).reverse().map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-slate-700">{item.id}</p>
                    <p className="text-xs text-slate-500">{item.agent}</p>
                  </div>
                  <StatusBadge status={item.decision} />
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
