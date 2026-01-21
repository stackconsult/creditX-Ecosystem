"use client";

import { useState } from "react";
import { useAgent } from "@copilotkit/react-core";
import { useCopilotAction } from "@copilotkit/react-core";
import A2UIRenderer from "@/components/ui/a2ui-renderer";
import { useA2UI } from "@/hooks/use-a2ui";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, FileText, CheckCircle } from "lucide-react";

// Example A2UI specification for credit application
const creditApplicationA2UI = {
  type: "Card",
  title: "Credit Application",
  elements: [
    {
      type: "Column",
      elements: [
        {
          type: "Text",
          content: "Please fill out the form below to apply for credit. All fields marked with * are required.",
          element: { className: "text-gray-600 mb-4" },
        },
        {
          type: "Row",
          elements: [
            {
              type: "TextField",
              id: "first_name",
              label: { text: "First Name *" },
              element: { 
                placeholder: "Enter your first name",
                className: "required"
              },
            },
            {
              type: "TextField",
              id: "last_name",
              label: { text: "Last Name *" },
              element: { 
                placeholder: "Enter your last name",
                className: "required"
              },
            },
          ],
        },
        {
          type: "Row",
          elements: [
            {
              type: "TextField",
              id: "email",
              label: { text: "Email Address *" },
              element: { 
                type: "email",
                placeholder: "your.email@example.com",
                className: "required"
              },
            },
            {
              type: "TextField",
              id: "phone",
              label: { text: "Phone Number *" },
              element: { 
                type: "tel",
                placeholder: "(555) 123-4567",
                className: "required"
              },
            },
          ],
        },
        {
          type: "Row",
          elements: [
            {
              type: "TextField",
              id: "ssn",
              label: { text: "Social Security Number *" },
              element: { 
                type: "password",
                placeholder: "XXX-XX-XXXX",
                className: "required"
              },
            },
            {
              type: "TextField",
              id: "dob",
              label: { text: "Date of Birth *" },
              element: { 
                type: "date",
                className: "required"
              },
            },
          ],
        },
        {
          type: "Heading",
          level: 2,
          content: "Financial Information",
          element: { className: "text-xl font-semibold mt-6 mb-4" },
        },
        {
          type: "Row",
          elements: [
            {
              type: "TextField",
              id: "annual_income",
              label: { text: "Annual Income *" },
              element: { 
                type: "number",
                placeholder: "0",
                className: "required"
              },
            },
            {
              type: "TextField",
              id: "employment_status",
              label: { text: "Employment Status *" },
              element: { 
                type: "select",
                options: [
                  { value: "", label: "Select..." },
                  { value: "full-time", label: "Full-time" },
                  { value: "part-time", label: "Part-time" },
                  { value: "self-employed", label: "Self-Employed" },
                  { value: "unemployed", label: "Unemployed" },
                  { value: "student", label: "Student" },
                ],
                className: "required"
              },
            },
          ],
        },
        {
          type: "Row",
          elements: [
            {
              type: "TextField",
              id: "monthly_rent",
              label: { text: "Monthly Rent/Mortgage" },
              element: { 
                type: "number",
                placeholder: "0"
              },
            },
            {
              type: "TextField",
              id: "monthly_debt",
              label: { text: "Monthly Debt Payments" },
              element: { 
                type: "number",
                placeholder: "0"
              },
            },
          ],
        },
        {
          type: "Heading",
          level: 2,
          content: "Loan Details",
          element: { className: "text-xl font-semibold mt-6 mb-4" },
        },
        {
          type: "Row",
          elements: [
            {
              type: "TextField",
              id: "loan_amount",
              label: { text: "Requested Loan Amount *" },
              element: { 
                type: "number",
                placeholder: "10000",
                className: "required"
              },
            },
            {
              type: "TextField",
              id: "loan_purpose",
              label: { text: "Loan Purpose *" },
              element: { 
                type: "select",
                options: [
                  { value: "", label: "Select..." },
                  { value: "debt_consolidation", label: "Debt Consolidation" },
                  { value: "home_improvement", label: "Home Improvement" },
                  { value: "business", label: "Business" },
                  { value: "personal", label: "Personal" },
                  { value: "education", label: "Education" },
                  { value: "other", label: "Other" },
                ],
                className: "required"
              },
            },
          ],
        },
        {
          type: "Column",
          elements: [
            {
              type: "MultipleChoice",
              id: "consent_credit_check",
              label: { text: "I authorize CreditX to check my credit history *" },
              options: ["Yes, I authorize"],
              required: true,
            },
            {
              type: "MultipleChoice",
              id: "consent_terms",
              label: { text: "I agree to the terms and conditions *" },
              options: ["Yes, I agree"],
              required: true,
            },
          ],
        },
        {
          type: "Button",
          id: "submit_application",
          content: "Submit Application",
          element: { 
            className: "w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3"
          },
        },
      ],
    },
  ],
};

export default function CreditApplicationForm() {
  const agent = useAgent({ agentId: "credit-application" });
  const { state, handleAction, handleSubmit } = useA2UI("credit-application");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [applicationId, setApplicationId] = useState<string | null>(null);

  // Initialize with the A2UI specification
  useState(() => {
    handleAction({ action: "update", data: creditApplicationA2UI });
  });

  // Copilot action for form validation
  useCopilotAction({
    name: "validateApplication",
    description: "Validate the credit application form",
    parameters: [
      { name: "formData", type: "object", description: "Form data to validate" },
    ],
    handler: async (args) => {
      // Basic validation logic
      const required = [
        "first_name",
        "last_name", 
        "email",
        "phone",
        "ssn",
        "dob",
        "annual_income",
        "employment_status",
        "loan_amount",
        "loan_purpose"
      ];
      
      const missing = required.filter(field => !args.formData[field]);
      
      if (missing.length > 0) {
        return {
          valid: false,
          errors: missing.map(field => `${field} is required`),
        };
      }
      
      return { valid: true, errors: [] };
    },
  });

  const onSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Submit to agent
      if (agent) {
        await agent.addMessage({
          id: Date.now().toString(),
          role: "user",
          content: JSON.stringify({
            action: "submit_application",
            data: state.values
          }),
          timestamp: new Date().toISOString()
        });

        // Listen for response
        const unsubscribe = agent.subscribe({
          onCustomEvent: (event: any) => {
            if (event.name === "application_submitted") {
              setApplicationId(event.value.application_id);
              setSubmitted(true);
              setIsSubmitting(false);
            }
          },
        });

        // Simulate submission
        setTimeout(() => {
          setApplicationId("APP-" + Date.now());
          setSubmitted(true);
          setIsSubmitting(false);
        }, 2000);
      }
    } catch (error) {
      console.error("Submission failed:", error);
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-emerald-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Application Submitted!</h2>
            <p className="text-gray-600">
              Your credit application has been successfully submitted.
            </p>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Application ID</p>
              <p className="font-mono text-lg">{applicationId}</p>
            </div>
            <p className="text-sm text-gray-500">
              We'll review your application and contact you within 2-3 business days.
            </p>
            <Button 
              onClick={() => {
                setSubmitted(false);
                setApplicationId(null);
              }}
              variant="outline"
            >
              Submit Another Application
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">Credit Application</h1>
        <p className="text-gray-600">
          Apply for credit in minutes with our secure online form
        </p>
        <div className="flex justify-center gap-2">
          <Badge variant="outline">Secure</Badge>
          <Badge variant="outline">Fast Approval</Badge>
          <Badge variant="outline">No Hidden Fees</Badge>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Application Form
          </CardTitle>
        </CardHeader>
        <CardContent>
          {state.components.length > 0 ? (
            <div className="space-y-4">
              {state.components.map((component, idx) => (
                <A2UIRenderer
                  key={idx}
                  component={component}
                  onAction={(action, data) => {
                    handleAction(action, data);
                    if (action === "click" && data.id === "submit_application") {
                      onSubmit();
                    }
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
              <p className="text-gray-500">Loading form...</p>
            </div>
          )}
          
          {isSubmitting && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 space-y-4">
                <Loader2 className="w-8 h-8 animate-spin mx-auto" />
                <p className="text-gray-700">Submitting your application...</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
