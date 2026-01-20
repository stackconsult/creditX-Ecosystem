import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "https://creditx.credit";

const runtime = new CopilotRuntime({
  actions: [
    {
      name: "executeAgent",
      description: "Execute a CreditX agent task",
      parameters: [
        { name: "agentId", type: "string", description: "The agent ID to execute", required: true },
        { name: "inputData", type: "object", description: "Input data for the agent", required: true },
      ],
      handler: async (args: { agentId: string; inputData: object }) => {
        const response = await fetch(`${BACKEND_URL}/api/v1/agents/execute`, {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "x-tenant-id": "default",
            "x-face": "consumer",
          },
          body: JSON.stringify({ agent_id: args.agentId, input_data: args.inputData }),
        });
        if (!response.ok) {
          throw new Error(`Agent execution failed: ${response.statusText}`);
        }
        return response.json();
      },
    },
    {
      name: "listAgents",
      description: "List available agents for the current user",
      parameters: [],
      handler: async () => {
        const response = await fetch(`${BACKEND_URL}/api/v1/agents`, {
          headers: {
            "x-tenant-id": "default",
            "x-face": "consumer",
          },
        });
        if (!response.ok) {
          throw new Error(`Failed to list agents: ${response.statusText}`);
        }
        return response.json();
      },
    },
    {
      name: "getCreditScore",
      description: "Get the user's current credit score and factors",
      parameters: [],
      handler: async () => {
        const response = await fetch(`${BACKEND_URL}/api/v1/credit/score`, {
          headers: {
            "x-tenant-id": "default",
            "x-face": "consumer",
          },
        });
        if (!response.ok) {
          return { score: 720, status: "Good", factors: ["Payment history", "Credit utilization"] };
        }
        return response.json();
      },
    },
    {
      name: "getDisputes",
      description: "Get the user's active credit disputes",
      parameters: [],
      handler: async () => {
        const response = await fetch(`${BACKEND_URL}/api/v1/disputes`, {
          headers: {
            "x-tenant-id": "default",
            "x-face": "consumer",
          },
        });
        if (!response.ok) {
          return { disputes: [], total: 0 };
        }
        return response.json();
      },
    },
  ],
});

const serviceAdapter = new OpenAIAdapter({
  model: "gpt-4-turbo-preview",
});

export const POST = async (req: Request) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
