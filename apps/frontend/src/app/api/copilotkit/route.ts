import { CopilotRuntime, OpenAIAdapter } from "@copilotkit/runtime";
import { NextRequest } from "next/server";

const runtime = new CopilotRuntime({
  actions: [
    {
      name: "executeAgent",
      description: "Execute a CreditX agent task",
      parameters: [
        { name: "agentId", type: "string", description: "The agent ID to execute", required: true },
        { name: "inputData", type: "object", description: "Input data for the agent", required: true },
      ],
      handler: async ({ agentId, inputData }) => {
        const response = await fetch(`${process.env.BACKEND_URL || "http://localhost:8000"}/api/v1/agents/execute`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ agent_id: agentId, input_data: inputData }),
        });
        return response.json();
      },
    },
    {
      name: "listAgents",
      description: "List available agents for the current user",
      handler: async () => {
        const response = await fetch(`${process.env.BACKEND_URL || "http://localhost:8000"}/api/v1/agents`);
        return response.json();
      },
    },
  ],
});

const adapter = new OpenAIAdapter({
  model: "gpt-4-turbo-preview",
});

export async function POST(req: NextRequest) {
  const { handleRequest } = runtime;
  return handleRequest(req, adapter);
}
