"use client";

import { useState, useEffect } from "react";
import { useAgent } from "@copilotkit/react-core";
import { useA2UI } from "@/hooks/use-a2ui";
import A2UIRenderer from "@/components/ui/a2ui-renderer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react";

interface AnalysisResult {
  score: number;
  factors: {
    positive: string[];
    negative: string[];
    neutral: string[];
  };
  recommendations: string[];
  riskLevel: "low" | "medium" | "high";
  confidence: number;
}

export default function CreditAnalysisTool() {
  const agent = useAgent({ agentId: "credit-analyzer" });
  const { state, handleAction, clearComponents } = useA2UI("credit-analyzer");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [applicantData, setApplicantData] = useState({
    name: "",
    income: 0,
    debt: 0,
    creditHistory: 0,
    employment: "",
  });

  // Generate dynamic form based on agent state
  useEffect(() => {
    if (agent && agent.state?.formSchema) {
      const formSchema = agent.state.formSchema;
      // Update A2UI components with the form schema
      clearComponents();
      formSchema.forEach((component: any) => {
        handleAction({ action: "update", data: component });
      });
    }
  }, [agent?.state, handleAction, clearComponents]);

  const startAnalysis = async () => {
    setIsAnalyzing(true);
    
    try {
      // Send applicant data to agent
      if (agent) {
        await agent.addMessage({
          id: Date.now().toString(),
          role: "user",
          content: JSON.stringify({
            action: "analyze_credit",
            data: applicantData
          }),
          timestamp: new Date().toISOString()
        });

        // Listen for response
        const unsubscribe = agent.subscribe({
          onCustomEvent: (event: any) => {
            if (event.name === "analysis_complete") {
              setAnalysisResult(event.value);
              setIsAnalyzing(false);
            }
            if (event.name === "dynamic_form") {
              // Render dynamic form components
              clearComponents();
              event.value.components.forEach((comp: any) => {
                handleAction({ action: "update", data: comp });
              });
            }
          },
        });

        // Timeout after 30 seconds
        setTimeout(() => {
          setIsAnalyzing(false);
          unsubscribe();
        }, 30000);
      }
    } catch (error) {
      console.error("Analysis failed:", error);
      setIsAnalyzing(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case "low": return "text-emerald-600 bg-emerald-50";
      case "medium": return "text-amber-600 bg-amber-50";
      case "high": return "text-red-600 bg-red-50";
      default: return "text-gray-600 bg-gray-50";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 750) return "text-emerald-600";
    if (score >= 700) return "text-blue-600";
    if (score >= 650) return "text-amber-600";
    return "text-red-600";
  };

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Credit Analysis Tool
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Render A2UI components if available */}
          {state.components.length > 0 ? (
            <div className="space-y-4">
              {state.components.map((component, idx) => (
                <A2UIRenderer
                  key={idx}
                  component={component}
                  onAction={handleAction}
                />
              ))}
            </div>
          ) : (
            // Default form
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Applicant Name</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md"
                  value={applicantData.name}
                  onChange={(e) => setApplicantData(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Annual Income</label>
                <input
                  type="number"
                  className="w-full p-2 border rounded-md"
                  value={applicantData.income}
                  onChange={(e) => setApplicantData(prev => ({ ...prev, income: Number(e.target.value) }))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Total Debt</label>
                <input
                  type="number"
                  className="w-full p-2 border rounded-md"
                  value={applicantData.debt}
                  onChange={(e) => setApplicantData(prev => ({ ...prev, debt: Number(e.target.value) }))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Credit History (years)</label>
                <input
                  type="number"
                  className="w-full p-2 border rounded-md"
                  value={applicantData.creditHistory}
                  onChange={(e) => setApplicantData(prev => ({ ...prev, creditHistory: Number(e.target.value) }))}
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-2">Employment Status</label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={applicantData.employment}
                  onChange={(e) => setApplicantData(prev => ({ ...prev, employment: e.target.value }))}
                >
                  <option value="">Select...</option>
                  <option value="employed">Employed</option>
                  <option value="self-employed">Self-Employed</option>
                  <option value="unemployed">Unemployed</option>
                  <option value="student">Student</option>
                </select>
              </div>
            </div>
          )}
          
          <Button 
            onClick={startAnalysis} 
            disabled={isAnalyzing}
            className="w-full"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Start Analysis"
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Analysis Results
              <Badge className={getRiskColor(analysisResult.riskLevel)}>
                {analysisResult.riskLevel.toUpperCase()} RISK
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Credit Score */}
            <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
              <div className="text-5xl font-bold mb-2">
                <span className={getScoreColor(analysisResult.score)}>
                  {analysisResult.score}
                </span>
              </div>
              <div className="text-sm text-gray-600">Credit Score</div>
              <div className="text-xs text-gray-500 mt-1">
                Confidence: {analysisResult.confidence}%
              </div>
            </div>

            {/* Factors */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <h4 className="flex items-center gap-2 text-emerald-700 font-medium mb-3">
                  <CheckCircle className="w-4 h-4" />
                  Positive Factors
                </h4>
                <ul className="space-y-2">
                  {analysisResult.factors.positive.map((factor, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-emerald-500 mt-1">•</span>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="flex items-center gap-2 text-amber-700 font-medium mb-3">
                  <AlertTriangle className="w-4 h-4" />
                  Areas of Concern
                </h4>
                <ul className="space-y-2">
                  {analysisResult.factors.negative.map((factor, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-amber-500 mt-1">•</span>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="flex items-center gap-2 text-blue-700 font-medium mb-3">
                  <TrendingUp className="w-4 h-4" />
                  Recommendations
                </h4>
                <ul className="space-y-2">
                  {analysisResult.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-blue-500 mt-1">→</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
