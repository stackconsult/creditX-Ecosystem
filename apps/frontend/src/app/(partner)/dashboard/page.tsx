"use client";

import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { useState } from "react";

export default function PartnerDashboard() {
  const [portfolioStats, setPortfolioStats] = useState({
    totalAssets: 125000000,
    activeLoans: 1245,
    avgScore: 680,
    defaultRate: 2.3,
  });

  useCopilotReadable({
    description: "Partner's portfolio statistics and performance metrics",
    value: portfolioStats,
  });

  useCopilotAction({
    name: "analyzePortfolio",
    description: "Analyze the current portfolio risk and performance",
    handler: async () => {
      return `Portfolio Analysis: Total assets under management: $${(portfolioStats.totalAssets / 1000000).toFixed(1)}M. Default rate of ${portfolioStats.defaultRate}% is within acceptable range. Average borrower score of ${portfolioStats.avgScore} indicates moderate risk profile.`;
    },
  });

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(value);

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-800 mb-8">Partner Dashboard</h1>
      
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
