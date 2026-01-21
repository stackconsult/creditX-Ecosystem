"use client";

import { useCopilotAction, useCopilotReadable, useAgent } from "@copilotkit/react-core";
import { useState, useEffect } from "react";

export default function PartnerDashboard() {
  const [portfolioStats, setPortfolioStats] = useState({
    totalAssets: 125000000,
    activeLoans: 1245,
    avgScore: 680,
    defaultRate: 2.3,
  });
  
  // Use the useAgent hook for real-time agent status
  const agent = useAgent({ agentId: "partner-dashboard" });
  const [agentStatus, setAgentStatus] = useState({
    isAnalyzing: false,
    lastAnalysis: null as string | null,
    queuedTasks: 0,
  });

  // Subscribe to agent events
  useEffect(() => {
    if (!agent) return;

    const unsubscribe = agent.subscribe({
      onRunStartedEvent: () => {
        setAgentStatus(prev => ({ ...prev, isAnalyzing: true }));
      },
      onRunFinalized: () => {
        setAgentStatus(prev => ({ ...prev, isAnalyzing: false }));
      },
      onCustomEvent: (event: any) => {
        if (event.name === "analysis_complete") {
          setAgentStatus(prev => ({ 
            ...prev, 
            lastAnalysis: event.value.result,
            isAnalyzing: false 
          }));
        }
        if (event.name === "task_queued") {
          setAgentStatus(prev => ({ ...prev, queuedTasks: prev.queuedTasks + 1 }));
        }
      },
    });

    return () => unsubscribe();
  }, [agent]);

  useCopilotReadable({
    description: "Partner's portfolio statistics and performance metrics",
    value: portfolioStats,
  });

  useCopilotAction({
    name: "analyzePortfolio",
    description: "Analyze the current portfolio risk and performance",
    parameters: [],
    handler: async () => {
      // Trigger agent analysis
      if (agent) {
        await agent.setState({
          ...agent.state,
          analysisRequested: true,
          timestamp: new Date().toISOString()
        });
      }
      return `Portfolio Analysis: Total assets under management: $${(portfolioStats.totalAssets / 1000000).toFixed(1)}M. Default rate of ${portfolioStats.defaultRate}% is within acceptable range. Average borrower score of ${portfolioStats.avgScore} indicates moderate risk profile.`;
    },
  });

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(value);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-slate-800">Partner Dashboard</h1>
        <div className="flex items-center gap-4">
          <div className={`px-3 py-1 rounded-full text-sm ${
            agentStatus.isAnalyzing 
              ? "bg-amber-100 text-amber-700" 
              : "bg-emerald-100 text-emerald-700"
          }`}>
            {agentStatus.isAnalyzing ? "Analyzing..." : "Ready"}
          </div>
          {agentStatus.queuedTasks > 0 && (
            <div className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm">
              {agentStatus.queuedTasks} tasks queued
            </div>
          )}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Total Assets</div>
          <div className="text-3xl font-bold text-partner">{formatCurrency(portfolioStats.totalAssets)}</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Active Loans</div>
          <div className="text-3xl font-bold text-slate-800">{portfolioStats.activeLoans.toLocaleString()}</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Avg Credit Score</div>
          <div className="text-3xl font-bold text-slate-800">{portfolioStats.avgScore}</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Default Rate</div>
          <div className="text-3xl font-bold text-orange-500">{portfolioStats.defaultRate}%</div>
        </div>
      </div>

      {agentStatus.lastAnalysis && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-8 border border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Latest AI Analysis</h3>
          <p className="text-blue-800">{agentStatus.lastAnalysis}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Recent Underwriting</h2>
          <div className="space-y-3">
            {[
              { id: "UW-2024-001", status: "Approved", amount: 50000 },
              { id: "UW-2024-002", status: "Pending", amount: 75000 },
              { id: "UW-2024-003", status: "Under Review", amount: 120000 },
            ].map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <span className="font-medium">{item.id}</span>
                <span className={`px-2 py-1 rounded text-sm ${
                  item.status === "Approved" ? "bg-emerald-100 text-emerald-700" :
                  item.status === "Pending" ? "bg-amber-100 text-amber-700" :
                  "bg-blue-100 text-blue-700"
                }`}>
                  {item.status}
                </span>
                <span className="text-slate-600">{formatCurrency(item.amount)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Risk Alerts</h2>
          <div className="space-y-3">
            <div className="p-4 rounded-lg bg-amber-50 text-amber-800">
              3 loans approaching 60-day delinquency threshold
            </div>
            <div className="p-4 rounded-lg bg-blue-50 text-blue-800">
              Quarterly compliance review due in 5 days
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
