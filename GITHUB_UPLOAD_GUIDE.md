# CreditX Frontend - GitHub Upload Guide
**All builds happen in the cloud - NO local tools needed!**

## Quick Steps
1. Go to https://github.com/stackconsult/creditX-Ecosystem
2. For each file below, click the file path → Edit (pencil icon) → Paste content → Commit

---

## FILE 1: `apps/frontend/netlify.toml` (CREATE NEW)

```toml
[build]
  command = "npm run build"
  publish = ".next"

[build.environment]
  NODE_VERSION = "20"
  NEXT_TELEMETRY_DISABLED = "1"
  NEXT_BUILD_STANDALONE = "true"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Strict-Transport-Security = "max-age=31536000; includeSubDomains"
    Content-Security-Policy = "default-src 'self' https://creditx.credit; script-src 'self' 'unsafe-inline' 'unsafe-eval'; connect-src 'self' https://creditx.credit wss://creditx.credit https://api.openai.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:"
    X-XSS-Protection = "1; mode=block"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[redirects]]
  from = "/api/backend/*"
  to = "https://creditx.credit/api/v1/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/api/agents/*"
  to = "https://creditx.credit/api/agents/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/api/health"
  to = "https://creditx.credit/health"
  status = 200
  force = true
```

---

## FILE 2: `apps/frontend/next.config.js` (REPLACE ENTIRE FILE)

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://creditx.credit",
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || "wss://creditx.credit/ws",
    NEXT_PUBLIC_COPILOT_API: process.env.NEXT_PUBLIC_COPILOT_API || "https://creditx.credit/api/copilot",
    NEXT_PUBLIC_DOMAIN: process.env.NEXT_PUBLIC_DOMAIN || "creditx.credit",
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "creditx.credit",
      },
    ],
  },
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://creditx.credit";
    return [
      {
        source: "/api/backend/:path*",
        destination: `${apiUrl}/api/v1/:path*`,
      },
      {
        source: "/api/agents/:path*",
        destination: `${apiUrl}/api/agents/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

---

## FILE 3: `apps/frontend/src/app/api/copilotkit/route.ts` (REPLACE ENTIRE FILE)

```typescript
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
      handler: async ({ agentId, inputData }: { agentId: string; inputData: Record<string, unknown> }) => {
        const response = await fetch(`${BACKEND_URL}/api/v1/agents/execute`, {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "x-tenant-id": "default",
            "x-face": "consumer",
          },
          body: JSON.stringify({ agent_id: agentId, input_data: inputData }),
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
```

---

## FILE 4: `apps/frontend/src/app/(consumer)/dashboard/page.tsx` (REPLACE ENTIRE FILE)

```tsx
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
```

---

## FILE 5: `apps/frontend/src/app/(partner)/dashboard/page.tsx` (REPLACE ENTIRE FILE)

```tsx
"use client";

import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { useState } from "react";

export default function PartnerDashboard() {
  const [portfolioStats, setPortfolioStats] = useState({
    totalAssets: 125000000,
    activeLoans: 1245,
    avgScore: 680,
    defaultRate: 2.3,
  });

  useCopilotReadable({
    description: "Partner's portfolio statistics and performance metrics",
    value: portfolioStats,
  });

  useCopilotAction({
    name: "analyzePortfolio",
    description: "Analyze the current portfolio risk and performance",
    parameters: [],
    handler: async () => {
      return `Portfolio Analysis: Total assets under management: $${(portfolioStats.totalAssets / 1000000).toFixed(1)}M. Default rate of ${portfolioStats.defaultRate}% is within acceptable range. Average borrower score of ${portfolioStats.avgScore} indicates moderate risk profile.`;
    },
  });

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(value);

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-800 mb-8">Partner Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Total Assets</div>
          <div className="text-3xl font-bold text-partner">{formatCurrency(portfolioStats.totalAssets)}</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Active Loans</div>
          <div className="text-3xl font-bold text-slate-800">{portfolioStats.activeLoans.toLocaleString()}</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Avg Credit Score</div>
          <div className="text-3xl font-bold text-slate-800">{portfolioStats.avgScore}</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="text-sm text-slate-500 mb-2">Default Rate</div>
          <div className="text-3xl font-bold text-orange-500">{portfolioStats.defaultRate}%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Recent Underwriting</h2>
          <div className="space-y-3">
            {[
              { id: "UW-2024-001", status: "Approved", amount: 50000 },
              { id: "UW-2024-002", status: "Pending", amount: 75000 },
              { id: "UW-2024-003", status: "Under Review", amount: 120000 },
            ].map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <span className="font-medium">{item.id}</span>
                <span className={`px-2 py-1 rounded text-sm ${
                  item.status === "Approved" ? "bg-emerald-100 text-emerald-700" :
                  item.status === "Pending" ? "bg-amber-100 text-amber-700" :
                  "bg-blue-100 text-blue-700"
                }`}>
                  {item.status}
                </span>
                <span className="text-slate-600">{formatCurrency(item.amount)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Risk Alerts</h2>
          <div className="space-y-3">
            <div className="p-4 rounded-lg bg-amber-50 text-amber-800">
              3 loans approaching 60-day delinquency threshold
            </div>
            <div className="p-4 rounded-lg bg-blue-50 text-blue-800">
              Quarterly compliance review due in 5 days
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## FILE 6: `apps/agent/requirements.txt` (REPLACE ENTIRE FILE)

```
fastapi>=0.109.0,<1.0.0
uvicorn[standard]>=0.27.0,<1.0.0
langgraph>=0.2.0
langchain>=0.3.0,<1.0.0
langchain-openai>=0.2.0
langchain-anthropic>=0.3.0
pydantic>=2.5.3,<3.0.0
python-dotenv>=1.0.0
httpx>=0.26.0
redis>=5.0.1
structlog>=24.1.0
tenacity>=8.2.3
prometheus-client>=0.19.0
opentelemetry-api>=1.22.0
opentelemetry-sdk>=1.22.0
opentelemetry-instrumentation-fastapi>=0.43b0
```

---

## After Uploading All Files

### Deploy to Netlify:
1. Go to https://app.netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect to GitHub → Select `stackconsult/creditX-Ecosystem`
4. Configure:
   - **Base directory**: `apps/frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `.next`
5. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL` = `https://creditx.credit`
   - `OPENAI_API_KEY` = your OpenAI key
6. Click Deploy!

**Netlify builds in the CLOUD - no local tools needed!**
