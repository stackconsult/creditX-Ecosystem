"use client";

import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { useState } from "react";

export default function ConsumerDashboard() {
  const [creditScore, setCreditScore] = useState(720);
  const [alerts, setAlerts] = useState([
    { id: 1, type: "info", message: "Your credit report was updated" },
    { id: 2, type: "success", message: "Dispute resolved in your favor" },
  ]);

  useCopilotReadable({
    description: "Consumer's current credit score and status",
    value: { creditScore, alertCount: alerts.length },
  });

  useCopilotAction({
    name: "explainCreditScore",
    description: "Explain the user's credit score and what affects it",
    parameters: [],
    handler: async () => {
      return `Your credit score of ${creditScore} is considered Good. Key factors affecting your score include payment history, credit utilization, and length of credit history.`;
    },
  });

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-800 mb-8">Your Credit Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Credit Score</div>
          <div className="text-4xl font-bold text-consumer">{creditScore}</div>
          <div className="text-sm text-slate-600 mt-2">Good</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Active Disputes</div>
          <div className="text-4xl font-bold text-slate-800">2</div>
          <div className="text-sm text-slate-600 mt-2">In Progress</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Data Rights Requests</div>
          <div className="text-4xl font-bold text-slate-800">0</div>
          <div className="text-sm text-slate-600 mt-2">Pending</div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">Recent Alerts</h2>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg ${
                alert.type === "success"
                  ? "bg-emerald-50 text-emerald-800"
                  : "bg-blue-50 text-blue-800"
              }`}
            >
              {alert.message}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
