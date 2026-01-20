"use client";

import Link from "next/link";
import { Users, Building2, Settings } from "lucide-react";

export default function HomePage() {
  const faces = [
    {
      name: "Consumer OS",
      description: "Manage your credit, file disputes, and protect your data rights",
      href: "/consumer/dashboard",
      icon: Users,
      color: "bg-consumer",
      gradient: "from-emerald-500 to-emerald-600",
    },
    {
      name: "Partner OS",
      description: "Portfolio management, underwriting, and compliance for lenders",
      href: "/partner/dashboard",
      icon: Building2,
      color: "bg-partner",
      gradient: "from-indigo-500 to-indigo-600",
    },
    {
      name: "Internal OS",
      description: "System administration, agent management, and HITL approvals",
      href: "/internal/dashboard",
      icon: Settings,
      color: "bg-internal",
      gradient: "from-amber-500 to-amber-600",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-consumer via-partner to-internal rounded-2xl mb-6">
            <span className="text-2xl font-bold text-white">CX</span>
          </div>
          <h1 className="text-5xl font-bold text-white mb-4">CreditX Ecosystem</h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            AI-powered credit management platform for consumers, lenders, and operators
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {faces.map((face) => {
            const Icon = face.icon;
            return (
              <Link
                key={face.name}
                href={face.href}
                className="group relative bg-slate-800/50 border border-slate-700 rounded-2xl p-8 hover:border-slate-500 transition-all duration-300 hover:scale-105"
              >
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${face.gradient} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-7 h-7 text-white" />
                </div>
                <h2 className="text-2xl font-semibold text-white mb-3">{face.name}</h2>
                <p className="text-slate-400 leading-relaxed">{face.description}</p>
                <div className="mt-6 flex items-center text-sm font-medium text-slate-300 group-hover:text-white">
                  Enter Dashboard
                  <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Link>
            );
          })}
        </div>

        <div className="mt-16 text-center">
          <p className="text-slate-500 text-sm">
            Powered by CopilotKit AI • Built on Spaceship Infrastructure
          </p>
        </div>
      </div>
    </div>
  );
}
