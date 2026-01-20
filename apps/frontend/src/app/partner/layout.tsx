"use client";

import { CopilotSidebar } from "@copilotkit/react-ui";

export default function PartnerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 to-white">
      <header className="bg-partner text-partner-foreground p-4 shadow-sm">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center font-bold">
              CX
            </div>
            <span className="font-semibold text-lg">Partner OS</span>
          </div>
          <nav className="flex items-center gap-6">
            <a href="/partner/dashboard" className="hover:opacity-80">Dashboard</a>
            <a href="/partner/portfolio" className="hover:opacity-80">Portfolio</a>
            <a href="/partner/underwriting" className="hover:opacity-80">Underwriting</a>
            <a href="/partner/analytics" className="hover:opacity-80">Analytics</a>
            <a href="/partner/compliance" className="hover:opacity-80">Compliance</a>
            <a href="/partner/settings" className="hover:opacity-80">Settings</a>
          </nav>
        </div>
      </header>
      <div className="flex">
        <main className="flex-1 p-6">{children}</main>
        <CopilotSidebar
          defaultOpen={false}
          labels={{
            title: "Partner Assistant",
            initial: "How can I assist with your portfolio today?",
          }}
        />
      </div>
    </div>
  );
}
