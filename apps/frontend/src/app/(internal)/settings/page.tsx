"use client";

import { Settings, Bell, Shield, Key, Database, Globe } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";

export default function InternalSettingsPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader
        title="System Settings"
        description="Configure system-wide settings and preferences"
      />

      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b flex items-center gap-3">
            <Settings className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-800">General Settings</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between py-3 border-b">
              <div>
                <p className="font-medium text-slate-800">System Name</p>
                <p className="text-sm text-slate-500">Display name for the ecosystem</p>
              </div>
              <input
                type="text"
                defaultValue="CreditX Ecosystem"
                className="px-3 py-2 border rounded-lg text-sm w-64"
              />
            </div>
            <div className="flex items-center justify-between py-3 border-b">
              <div>
                <p className="font-medium text-slate-800">Default Timezone</p>
                <p className="text-sm text-slate-500">System-wide timezone setting</p>
              </div>
              <select className="px-3 py-2 border rounded-lg text-sm w-64">
                <option>America/Phoenix (UTC-7)</option>
                <option>America/New_York (UTC-5)</option>
                <option>Europe/London (UTC+0)</option>
              </select>
            </div>
            <div className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium text-slate-800">Maintenance Mode</p>
                <p className="text-sm text-slate-500">Disable access during maintenance</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-internal"></div>
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
            <div className="flex items-center justify-between py-3 border-b">
              <div>
                <p className="font-medium text-slate-800">HITL Alerts</p>
                <p className="text-sm text-slate-500">Notify on pending HITL requests</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" defaultChecked className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-internal"></div>
              </label>
            </div>
            <div className="flex items-center justify-between py-3 border-b">
              <div>
                <p className="font-medium text-slate-800">Security Alerts</p>
                <p className="text-sm text-slate-500">Notify on threat detection</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" defaultChecked className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-internal"></div>
              </label>
            </div>
            <div className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium text-slate-800">System Health Alerts</p>
                <p className="text-sm text-slate-500">Notify on service degradation</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" defaultChecked className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-internal"></div>
              </label>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b flex items-center gap-3">
            <Shield className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-800">Security</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between py-3 border-b">
              <div>
                <p className="font-medium text-slate-800">Session Timeout</p>
                <p className="text-sm text-slate-500">Auto-logout after inactivity</p>
              </div>
              <select className="px-3 py-2 border rounded-lg text-sm w-64">
                <option>15 minutes</option>
                <option>30 minutes</option>
                <option>1 hour</option>
                <option>4 hours</option>
              </select>
            </div>
            <div className="flex items-center justify-between py-3 border-b">
              <div>
                <p className="font-medium text-slate-800">Require MFA</p>
                <p className="text-sm text-slate-500">Enforce multi-factor authentication</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" defaultChecked className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-internal"></div>
              </label>
            </div>
            <div className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium text-slate-800">Audit Logging</p>
                <p className="text-sm text-slate-500">Log all administrative actions</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" defaultChecked className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-internal"></div>
              </label>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center gap-3 mb-4">
              <Key className="w-5 h-5 text-slate-500" />
              <h3 className="font-semibold text-slate-800">API Keys</h3>
            </div>
            <p className="text-sm text-slate-600 mb-4">Manage system API keys and integrations</p>
            <button className="w-full py-2 border border-internal text-internal rounded-lg hover:bg-internal/5 transition-colors">
              Manage Keys
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center gap-3 mb-4">
              <Database className="w-5 h-5 text-slate-500" />
              <h3 className="font-semibold text-slate-800">Database</h3>
            </div>
            <p className="text-sm text-slate-600 mb-4">Database maintenance and backups</p>
            <button className="w-full py-2 border border-internal text-internal rounded-lg hover:bg-internal/5 transition-colors">
              View Status
            </button>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button className="px-6 py-2 border rounded-lg text-slate-700 hover:bg-slate-50 transition-colors">
            Cancel
          </button>
          <button className="px-6 py-2 bg-internal text-white rounded-lg hover:opacity-90 transition-opacity">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
