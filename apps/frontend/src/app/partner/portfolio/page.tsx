"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import { DollarSign, Users, TrendingUp, AlertTriangle } from "lucide-react";
import { mockPartnerData, formatCurrency, formatNumber } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/ui/page-header";

export default function PortfolioPage() {
  const { portfolio, loans, riskDistribution } = mockPartnerData;

  useCopilotReadable({
    description: "Partner's loan portfolio data including loans and risk distribution",
    value: { portfolio, loans, riskDistribution },
  });

  const columns = [
    { key: "id", header: "Loan ID", sortable: true },
    { key: "borrower", header: "Borrower", sortable: true },
    { key: "amount", header: "Amount", sortable: true, render: (v: unknown) => formatCurrency(Number(v)) },
    { key: "apr", header: "APR", render: (v: unknown) => `${v}%` },
    { key: "term", header: "Term", render: (v: unknown) => `${v} mo` },
    { key: "score", header: "Score", sortable: true },
    { key: "status", header: "Status", render: (v: unknown) => <StatusBadge status={String(v)} /> },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      <PageHeader
        title="Loan Portfolio"
        description="View and analyze your loan portfolio performance"
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Assets"
          value={formatCurrency(portfolio.totalAssets)}
          subtitle="Under management"
          icon={<DollarSign className="w-5 h-5 text-partner" />}
          color="partner"
        />
        <MetricCard
          title="Active Loans"
          value={formatNumber(portfolio.activeLoans)}
          subtitle={`${portfolio.totalBorrowers} borrowers`}
          icon={<Users className="w-5 h-5 text-blue-500" />}
        />
        <MetricCard
          title="Avg Loan Size"
          value={formatCurrency(portfolio.avgLoanSize)}
          subtitle="Per loan"
        />
        <MetricCard
          title="Yield Rate"
          value={`${portfolio.yieldRate}%`}
          subtitle="Portfolio yield"
          icon={<TrendingUp className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Risk Distribution</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {riskDistribution.map((tier) => (
                <div key={tier.tier}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-700">{tier.tier}</span>
                      <span className="text-sm text-slate-500">({tier.count} loans)</span>
                    </div>
                    <div className="text-right">
                      <span className="font-medium text-slate-700">{tier.percentage}%</span>
                      <span className="text-sm text-slate-500 ml-2">@ {tier.avgApr}% APR</span>
                    </div>
                  </div>
                  <div className="h-4 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        tier.tier === 'Prime' ? 'bg-emerald-500' :
                        tier.tier === 'Near Prime' ? 'bg-blue-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${tier.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Portfolio Health</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Default Rate</span>
              <span className={`font-semibold ${portfolio.defaultRate < 3 ? 'text-emerald-600' : 'text-amber-600'}`}>
                {portfolio.defaultRate}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Delinquency Rate</span>
              <span className={`font-semibold ${portfolio.delinquencyRate < 5 ? 'text-emerald-600' : 'text-amber-600'}`}>
                {portfolio.delinquencyRate}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Avg Credit Score</span>
              <span className="font-semibold text-slate-800">{portfolio.avgCreditScore}</span>
            </div>
            <div className="pt-4 border-t">
              <div className="flex items-center gap-2 text-amber-600">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm">3 loans at 60-day threshold</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">All Loans</h2>
          <button className="px-4 py-2 border rounded-lg text-slate-700 hover:bg-slate-50 text-sm">
            Export CSV
          </button>
        </div>
        <div className="p-4">
          <DataTable data={loans} columns={columns} />
        </div>
      </div>
    </div>
  );
}
