"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import { Target, TrendingUp, Calendar, Zap } from "lucide-react";
import { mockConsumerData, formatDate } from "@/lib/mock-data";
import { MetricCard } from "@/components/ui/metric-card";
import { PageHeader } from "@/components/ui/page-header";

export default function PlansPage() {
  const { plans, creditReport } = mockConsumerData;
  const activePlan = plans[0];

  useCopilotReadable({
    description: "Consumer's savings plans and credit improvement campaigns",
    value: { plans, currentScore: creditReport.score },
  });

  const pointsToGo = activePlan ? activePlan.target - activePlan.currentScore : 0;

  return (
    <div className="max-w-6xl mx-auto">
      <PageHeader
        title="Credit Improvement Plans"
        description="Track your progress towards better credit"
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Current Score"
          value={creditReport.score}
          subtitle="Your score now"
          icon={<TrendingUp className="w-5 h-5 text-emerald-500" />}
          color="success"
        />
        <MetricCard
          title="Target Score"
          value={activePlan?.target || "—"}
          subtitle="Your goal"
          icon={<Target className="w-5 h-5 text-consumer" />}
          color="consumer"
        />
        <MetricCard
          title="Points to Go"
          value={pointsToGo}
          subtitle="Remaining"
        />
        <MetricCard
          title="Target Date"
          value={activePlan ? formatDate(activePlan.dueDate) : "—"}
          subtitle="Completion goal"
          icon={<Calendar className="w-5 h-5 text-blue-500" />}
        />
      </div>

      {activePlan && (
        <div className="bg-white rounded-xl shadow-sm border mb-6">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-800">{activePlan.name}</h2>
                <p className="text-slate-500 mt-1">
                  Started at {activePlan.startScore} • Now at {activePlan.currentScore} • Target {activePlan.target}
                </p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-consumer">{activePlan.progress}%</p>
                <p className="text-sm text-slate-500">Complete</p>
              </div>
            </div>
            <div className="mt-4">
              <div className="h-4 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-consumer rounded-full transition-all duration-500"
                  style={{ width: `${activePlan.progress}%` }}
                />
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <h3 className="font-semibold text-slate-800 mb-4">Active Campaigns</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { name: "Pay Down Balances", progress: 65, impact: "+15 pts", status: "active" },
                { name: "Dispute Errors", progress: 100, impact: "+12 pts", status: "completed" },
                { name: "Credit Age Optimization", progress: 30, impact: "+8 pts", status: "active" },
              ].map((campaign, idx) => (
                <div key={idx} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-slate-700">{campaign.name}</span>
                    <span className="text-sm text-emerald-600 font-medium">{campaign.impact}</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden mb-2">
                    <div
                      className={`h-full rounded-full ${campaign.status === 'completed' ? 'bg-emerald-500' : 'bg-consumer'}`}
                      style={{ width: `${campaign.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-500">{campaign.progress}% complete</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-slate-800">Recommended Actions</h2>
        </div>
        <div className="p-4 space-y-3">
          {[
            { action: "Pay Chase Sapphire below 20% utilization", impact: "High", effort: "Medium", points: "+8-12" },
            { action: "Request credit limit increase on Citi card", impact: "Medium", effort: "Low", points: "+3-5" },
            { action: "Dispute late payment from 2024", impact: "High", effort: "Medium", points: "+10-15" },
            { action: "Become authorized user on aged account", impact: "Medium", effort: "Low", points: "+5-10" },
          ].map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-consumer/10 rounded-lg flex items-center justify-center">
                  <Zap className="w-5 h-5 text-consumer" />
                </div>
                <div>
                  <p className="font-medium text-slate-800">{item.action}</p>
                  <div className="flex items-center gap-3 text-sm text-slate-500">
                    <span>Impact: {item.impact}</span>
                    <span>Effort: {item.effort}</span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-emerald-600">{item.points}</p>
                <p className="text-xs text-slate-500">potential</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
