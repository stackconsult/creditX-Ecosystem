"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import { BarChart3, TrendingUp, PieChart, Calendar } from "lucide-react";
import { mockPartnerData, formatCurrency, formatNumber } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { PageHeader } from "@/components/ui/page-header";

export default function AnalyticsPage() {
  const { portfolio, portfolioTrend, riskDistribution } = mockPartnerData;

  useCopilotReadable({
    description: "Portfolio analytics and trends",
    value: { portfolio, portfolioTrend, riskDistribution },
  });

  return (
    <div className="max-w-7xl mx-auto">
      <PageHeader
        title="Analytics"
        description="Portfolio performance insights and trends"
        actions={
          <div className="flex items-center gap-2">
            <select className="px-3 py-2 border rounded-lg text-sm">
              <option>Last 6 months</option>
              <option>Last 12 months</option>
              <option>Year to date</option>
              <option>All time</option>
            </select>
            <button className="px-4 py-2 bg-partner text-white rounded-lg hover:opacity-90">
              Export Report
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Portfolio Growth"
          value="+27.5%"
          subtitle="vs last year"
          trend={27.5}
          icon={<TrendingUp className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
        <MetricCard
          title="New Originations"
          value={formatCurrency(8500000)}
          subtitle="This month"
          icon={<BarChart3 className="w-5 h-5 text-partner" />}
          color="partner"
        />
        <MetricCard
          title="Avg Loan Size"
          value={formatCurrency(portfolio.avgLoanSize)}
          subtitle="All loans"
        />
        <MetricCard
          title="Net Yield"
          value={`${portfolio.yieldRate}%`}
          subtitle="After defaults"
          icon={<PieChart className="w-5 h-5 text-blue-500" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Portfolio Trend</h2>
          </div>
          <div className="p-6">
            <div className="h-64 flex items-end gap-4">
              {portfolioTrend.map((month, idx) => {
                const maxValue = Math.max(...portfolioTrend.map(m => m.value));
                const height = (month.value / maxValue) * 100;
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-partner rounded-t transition-all hover:bg-partner/80"
                      style={{ height: `${height}%` }}
                      title={formatCurrency(month.value)}
                    />
                    <p className="text-xs text-slate-500 mt-2">{month.month}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Loan Count Trend</h2>
          </div>
          <div className="p-6">
            <div className="h-64 flex items-end gap-4">
              {portfolioTrend.map((month, idx) => {
                const maxLoans = Math.max(...portfolioTrend.map(m => m.loans));
                const height = (month.loans / maxLoans) * 100;
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-400"
                      style={{ height: `${height}%` }}
                      title={`${month.loans} loans`}
                    />
                    <p className="text-xs text-slate-500 mt-2">{month.month}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Risk Distribution</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {riskDistribution.map((tier) => (
                <div key={tier.tier} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded ${
                      tier.tier === 'Prime' ? 'bg-emerald-500' :
                      tier.tier === 'Near Prime' ? 'bg-blue-500' : 'bg-amber-500'
                    }`} />
                    <span className="text-slate-700">{tier.tier}</span>
                  </div>
                  <span className="font-semibold text-slate-800">{tier.percentage}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Performance Metrics</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Approval Rate</span>
              <span className="font-semibold text-slate-800">68%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Avg Time to Fund</span>
              <span className="font-semibold text-slate-800">2.3 days</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Early Payoff Rate</span>
              <span className="font-semibold text-slate-800">12%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Customer Retention</span>
              <span className="font-semibold text-slate-800">45%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold text-slate-800">Cohort Analysis</h2>
          </div>
          <div className="p-6 space-y-3">
            {[
              { cohort: "Q1 2025", loans: 245, performance: "95%" },
              { cohort: "Q4 2024", loans: 312, performance: "92%" },
              { cohort: "Q3 2024", loans: 289, performance: "94%" },
              { cohort: "Q2 2024", loans: 256, performance: "91%" },
            ].map((c, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  <span className="text-slate-700">{c.cohort}</span>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-slate-500">{c.loans} loans</span>
                  <span className="font-medium text-emerald-600">{c.performance}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
