"use client";

import { CopilotSidebar } from "@copilotkit/react-ui";

export default function ConsumerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50 to-white">
      <header className="bg-consumer text-consumer-foreground p-4 shadow-sm">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center font-bold">
              CX
            </div>
            <span className="font-semibold text-lg">Consumer OS</span>
          </div>
          <nav className="flex items-center gap-6">
            <a href="/consumer/dashboard" className="hover:opacity-80">Dashboard</a>
            <a href="/consumer/credit" className="hover:opacity-80">Credit</a>
            <a href="/consumer/apply" className="hover:opacity-80">Apply</a>
            <a href="/consumer/disputes" className="hover:opacity-80">Disputes</a>
            <a href="/consumer/plans" className="hover:opacity-80">Plans</a>
            <a href="/consumer/rights" className="hover:opacity-80">Rights</a>
            <a href="/consumer/settings" className="hover:opacity-80">Settings</a>
          </nav>
        </div>
      </header>
      <div className="flex">
        <main className="flex-1 p-6">{children}</main>
        <CopilotSidebar
          defaultOpen={false}
          labels={{
            title: "CreditX Assistant",
            initial: "How can I help with your credit today?",
          }}
        />
      </div>
    </div>
  );
}
