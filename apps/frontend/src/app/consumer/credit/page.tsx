"use client";

import { useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";
import { TrendingUp, CreditCard, AlertCircle, FileText } from "lucide-react";
import { mockConsumerData, formatCurrency, getScoreColor, getScoreLabel } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function CreditPage() {
  const { creditReport } = mockConsumerData;

  useCopilotReadable({
    description: "Consumer's full credit report including score, factors, and accounts",
    value: creditReport,
  });

  useCopilotAction({
    name: "explainScoreFactor",
    description: "Explain a specific credit score factor",
    parameters: [
      { name: "factor", type: "string", description: "The factor to explain", required: true },
    ],
    handler: async ({ factor }) => {
      const factorData = creditReport.scoreFactors.find(f => 
        f.factor.toLowerCase().includes(factor.toLowerCase())
      );
      if (!factorData) return `Factor "${factor}" not found in your report.`;
      return `${factorData.factor}: This accounts for ${factorData.weight}% of your score. Your current impact is ${factorData.impact} with a score of ${factorData.score}.`;
    },
  });

  const totalBalance = creditReport.accounts.reduce((sum, acc) => sum + acc.balance, 0);
  const totalLimit = creditReport.accounts
    .filter(acc => acc.limit)
    .reduce((sum, acc) => sum + (acc.limit || 0), 0);
  const utilization = totalLimit > 0 ? Math.round((totalBalance / totalLimit) * 100) : 0;

  return (
    <div className="max-w-6xl mx-auto">
      <PageHeader
        title="Credit Report"
        description="Your complete credit profile and score breakdown"
        actions={
          <button className="flex items-center gap-2 px-4 py-2 bg-consumer text-white rounded-lg hover:opacity-90">
            <FileText className="w-4 h-4" />
            Download Report
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="md:col-span-1 bg-white rounded-xl shadow-sm border p-6 text-center">
          <p className="text-sm text-slate-500 mb-2">Credit Score</p>
          <p className={`text-5xl font-bold ${getScoreColor(creditReport.score)}`}>
            {creditReport.score}
          </p>
          <p className="text-lg text-slate-600 mt-1">{getScoreLabel(creditReport.score)}</p>
          <div className="flex items-center justify-center gap-1 mt-3 text-emerald-600">
            <TrendingUp className="w-4 h-4" />
            <span className="font-medium">+{creditReport.scoreChange} pts</span>
            <span className="text-slate-500 text-sm">this month</span>
          </div>
        </div>

        <MetricCard
          title="Credit Utilization"
          value={`${utilization}%`}
          subtitle={utilization < 30 ? "Good" : utilization < 50 ? "Fair" : "High"}
          color={utilization < 30 ? "success" : utilization < 50 ? "warning" : "error"}
          icon={<CreditCard className="w-5 h-5 text-blue-500" />}
        />
        <MetricCard
          title="Total Accounts"
          value={creditReport.accounts.length}
          subtitle="Open accounts"
        />
        <MetricCard
          title="Hard Inquiries"
          value={creditReport.inquiries.length}
          subtitle="Last 12 months"
          icon={<AlertCircle className="w-5 h-5 text-amber-500" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Score Factors</h2>
          </div>
          <div className="p-4 space-y-4">
            {creditReport.scoreFactors.map((factor) => (
              <div key={factor.factor} className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-slate-700">{factor.factor}</span>
                    <span className="text-sm text-slate-500">{factor.weight}% of score</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        factor.impact === 'positive' ? 'bg-emerald-500' :
                        factor.impact === 'negative' ? 'bg-red-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${factor.score}%` }}
                    />
                  </div>
                </div>
                <StatusBadge status={factor.impact} />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Recent Inquiries</h2>
          </div>
          <div className="p-4 space-y-3">
            {creditReport.inquiries.map((inquiry, idx) => (
              <div key={idx} className="p-3 bg-slate-50 rounded-lg">
                <p className="font-medium text-slate-700">{inquiry.lender}</p>
                <div className="flex items-center justify-between mt-1 text-sm text-slate-500">
                  <span>{inquiry.type}</span>
                  <span>{new Date(inquiry.date).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-slate-800">Accounts</h2>
        </div>
        <div className="p-4">
          <div className="space-y-3">
            {creditReport.accounts.map((account, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div>
                  <p className="font-medium text-slate-800">{account.name}</p>
                  <p className="text-sm text-slate-500">{account.type}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-slate-800">{formatCurrency(account.balance)}</p>
                  {account.limit && (
                    <p className="text-sm text-slate-500">of {formatCurrency(account.limit)} limit</p>
                  )}
                </div>
                <StatusBadge status={account.status} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
