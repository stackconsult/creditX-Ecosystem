import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "https://creditx.credit";

export async function POST(request: NextRequest) {
  try {
    const { agentId, message, state } = await request.json();

    // Forward to agent orchestrator
    const response = await fetch(`${BACKEND_URL}/api/v1/agents/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-tenant-id": "default",
        "x-face": "partner",
      },
      body: JSON.stringify({
        agent_id: agentId,
        message,
        state,
      }),
    });

    if (!response.ok) {
      throw new Error(`Agent chat failed: ${response.statusText}`);
    }

    const data = await response.json();

    // Handle A2UI generation
    if (data.generate_ui) {
      const a2uiComponents = generateA2UI(data.ui_type, data.data);
      return NextResponse.json({
        ...data,
        a2ui: a2uiComponents,
      });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Agent chat error:", error);
    return NextResponse.json(
      { error: "Failed to process agent request" },
      { status: 500 }
    );
  }
}

function generateA2UI(uiType: string, data: any) {
  switch (uiType) {
    case "credit_application":
      return [
        {
          type: "Card",
          title: "Credit Application Form",
          elements: [
            {
              type: "Row",
              elements: [
                {
                  type: "TextField",
                  id: "applicant_name",
                  label: { text: "Full Name" },
                  element: { placeholder: "Enter full name" },
                },
                {
                  type: "TextField",
                  id: "applicant_email",
                  label: { text: "Email Address" },
                  element: { placeholder: "email@example.com" },
                },
              ],
            },
            {
              type: "Row",
              elements: [
                {
                  type: "TextField",
                  id: "annual_income",
                  label: { text: "Annual Income" },
                  element: { 
                    type: "number",
                    placeholder: "0" 
                  },
                },
                {
                  type: "TextField",
                  id: "loan_amount",
                  label: { text: "Requested Loan Amount" },
                  element: { 
                    type: "number",
                    placeholder: "0" 
                  },
                },
              ],
            },
            {
              type: "Column",
              elements: [
                {
                  type: "MultipleChoice",
                  id: "employment_status",
                  label: { text: "Employment Status" },
                  options: ["Employed", "Self-Employed", "Unemployed", "Student", "Retired"],
                },
                {
                  type: "Slider",
                  id: "credit_score_range",
                  label: { text: "Estimated Credit Score Range" },
                  min: 300,
                  max: 850,
                  value: 700,
                },
              ],
            },
            {
              type: "Button",
              id: "submit_application",
              content: "Submit Application",
              element: { className: "w-full mt-4" },
            },
          ],
        },
      ];

    case "risk_analysis":
      return [
        {
          type: "Card",
          title: "Risk Analysis Parameters",
          elements: [
            {
              type: "Column",
              elements: [
                {
                  type: "Text",
                  content: "Configure the risk analysis parameters for the portfolio.",
                },
                {
                  type: "Slider",
                  id: "risk_tolerance",
                  label: { text: "Risk Tolerance" },
                  min: 0,
                  max: 100,
                  value: 50,
                },
                {
                  type: "MultipleChoice",
                  id: "analysis_type",
                  label: { text: "Analysis Type" },
                  options: ["Conservative", "Moderate", "Aggressive"],
                  selected: "Moderate",
                },
                {
                  type: "Button",
                  id: "run_analysis",
                  content: "Run Risk Analysis",
                },
              ],
            },
          ],
        },
      ];

    case "dispute_form":
      return [
        {
          type: "Card",
          title: "File a Credit Dispute",
          elements: [
            {
              type: "Column",
              elements: [
                {
                  type: "TextField",
                  id: "dispute_reason",
                  label: { text: "Reason for Dispute" },
                  element: { 
                    type: "textarea",
                    placeholder: "Explain why you're disputing this item...",
                    rows: 4
                  },
                },
                {
                  type: "MultipleChoice",
                  id: "dispute_type",
                  label: { text: "Type of Dispute" },
                  options: [
                    "Incorrect Information",
                    "Outdated Information",
                    "Fraudulent Activity",
                    "Identity Theft",
                    "Other"
                  ],
                },
                {
                  type: "TextField",
                  id: "supporting_docs",
                  label: { text: "Supporting Documents" },
                  element: { 
                    type: "file",
                    multiple: true,
                    accept: ".pdf,.jpg,.jpeg,.png"
                  },
                },
                {
                  type: "Button",
                  id: "submit_dispute",
                  content: "Submit Dispute",
                },
              ],
            },
          ],
        },
      ];

    default:
      return [];
  }
}
