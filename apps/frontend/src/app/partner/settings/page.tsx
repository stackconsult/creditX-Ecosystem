"use client";

import { Building2, Key, Bell, Globe, Users } from "lucide-react";
import { mockPartnerData } from "@/lib/mock-data";
import { PageHeader } from "@/components/ui/page-header";

export default function PartnerSettingsPage() {
  const { profile } = mockPartnerData;

  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader
        title="Partner Settings"
        description="Manage your organization and integration settings"
      />

      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b flex items-center gap-3">
            <Building2 className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-800">Organization</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Organization Name</label>
                <input type="text" defaultValue={profile.name} className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Type</label>
                <input type="text" defaultValue={profile.type} className="w-full px-3 py-2 border rounded-lg" disabled />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Partner Since</label>
              <p className="text-slate-600">{new Date(profile.since).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b flex items-center gap-3">
            <Key className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-800">API Configuration</h2>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">API Key</label>
              <div className="flex gap-2">
                <input
                  type="password"
                  defaultValue="pk_live_xxxxxxxxxxxxxxxxxxxxxxxx"
                  className="flex-1 px-3 py-2 border rounded-lg font-mono"
                  disabled
                />
                <button className="px-4 py-2 border rounded-lg text-slate-700 hover:bg-slate-50">
                  Reveal
                </button>
                <button className="px-4 py-2 bg-partner text-white rounded-lg hover:opacity-90">
                  Regenerate
                </button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Webhook URL</label>
              <input
                type="url"
                placeholder="https://your-server.com/webhooks/creditx"
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div className="flex items-center justify-between py-2">
              <div>
                <p className="font-medium text-slate-800">Sandbox Mode</p>
                <p className="text-sm text-slate-500">Test integrations without affecting production data</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-partner"></div>
              </label>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b flex items-center gap-3">
            <Bell className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-800">Notifications</h2>
          </div>
          <div className="p-6 space-y-4">
            {[
              { label: "New Application Alerts", desc: "Notify when new applications are received", enabled: true },
              { label: "Decision Required", desc: "Notify for pending underwriting decisions", enabled: true },
              { label: "Delinquency Alerts", desc: "Alert on loan delinquency status changes", enabled: true },
              { label: "Compliance Reminders", desc: "Upcoming compliance deadlines", enabled: false },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center justify-between py-2">
                <div>
                  <p className="font-medium text-slate-800">{item.label}</p>
                  <p className="text-sm text-slate-500">{item.desc}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked={item.enabled} className="sr-only peer" />
                  <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-partner"></div>
                </label>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center gap-3 mb-4">
              <Globe className="w-5 h-5 text-slate-500" />
              <h3 className="font-semibold text-slate-800">Integrations</h3>
            </div>
            <p className="text-sm text-slate-600 mb-4">Connect to external systems</p>
            <div className="space-y-2">
              <button className="w-full py-2 border rounded-lg text-slate-700 hover:bg-slate-50 text-left px-4">
                Salesforce CRM
              </button>
              <button className="w-full py-2 border rounded-lg text-slate-700 hover:bg-slate-50 text-left px-4">
                Plaid
              </button>
              <button className="w-full py-2 border rounded-lg text-slate-700 hover:bg-slate-50 text-left px-4">
                DocuSign
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center gap-3 mb-4">
              <Users className="w-5 h-5 text-slate-500" />
              <h3 className="font-semibold text-slate-800">Team Members</h3>
            </div>
            <p className="text-sm text-slate-600 mb-4">Manage access for your team</p>
            <div className="space-y-2 mb-4">
              <div className="flex items-center justify-between py-2">
                <span className="text-slate-700">Admin users</span>
                <span className="font-medium">3</span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-slate-700">Standard users</span>
                <span className="font-medium">12</span>
              </div>
            </div>
            <button className="w-full py-2 border border-partner text-partner rounded-lg hover:bg-partner/5">
              Manage Team
            </button>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button className="px-6 py-2 border rounded-lg text-slate-700 hover:bg-slate-50">
            Cancel
          </button>
          <button className="px-6 py-2 bg-partner text-white rounded-lg hover:opacity-90">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
