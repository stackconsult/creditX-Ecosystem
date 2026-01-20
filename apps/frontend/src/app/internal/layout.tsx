"use client";

import { CopilotSidebar } from "@copilotkit/react-ui";

export default function InternalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-white">
      <header className="bg-internal text-internal-foreground p-4 shadow-sm">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center font-bold">
              CX
            </div>
            <span className="font-semibold text-lg">Internal OS</span>
          </div>
          <nav className="flex items-center gap-6">
            <a href="/internal/dashboard" className="hover:opacity-80">Dashboard</a>
            <a href="/internal/agents" className="hover:opacity-80">Agents</a>
            <a href="/internal/hitl" className="hover:opacity-80">HITL</a>
            <a href="/internal/services" className="hover:opacity-80">Services</a>
            <a href="/internal/audit" className="hover:opacity-80">Audit</a>
            <a href="/internal/tenants" className="hover:opacity-80">Tenants</a>
            <a href="/internal/settings" className="hover:opacity-80">Settings</a>
          </nav>
        </div>
      </header>
      <div className="flex">
        <main className="flex-1 p-6">{children}</main>
        <CopilotSidebar
          defaultOpen={true}
          labels={{
            title: "Internal Assistant",
            initial: "How can I help manage the ecosystem?",
          }}
        />
      </div>
    </div>
  );
}
