"use client";

import CreditAnalysisTool from "@/components/credit/credit-analysis-tool";

export default function AnalysisPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Credit Analysis</h1>
        <p className="text-gray-600">
          Use our AI-powered tool to analyze credit applications and assess risk
        </p>
      </div>
      <CreditAnalysisTool />
    </div>
  );
}
