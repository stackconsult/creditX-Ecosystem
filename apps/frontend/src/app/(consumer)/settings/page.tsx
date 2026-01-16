"use client";

import { User, Bell, Lock, CreditCard, Smartphone } from "lucide-react";
import { mockConsumerData } from "@/lib/mock-data";
import { PageHeader } from "@/components/ui/page-header";

export default function ConsumerSettingsPage() {
  const { profile } = mockConsumerData;

  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader
        title="Settings"
        description="Manage your account preferences and security"
      />

      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b flex items-center gap-3">
            <User className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-800">Profile</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                <input type="text" defaultValue={profile.name} className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <input type="email" defaultValue={profile.email} className="w-full px-3 py-2 border rounded-lg" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Member Since</label>
              <p className="text-slate-600">{new Date(profile.memberSince).toLocaleDateString()}</p>
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
              { label: "Credit Score Changes", desc: "Get notified when your score changes", enabled: true },
              { label: "Dispute Updates", desc: "Updates on dispute progress", enabled: true },
              { label: "New Inquiries", desc: "Alert when someone pulls your credit", enabled: true },
              { label: "Payment Reminders", desc: "Upcoming payment due dates", enabled: false },
              { label: "Weekly Summary", desc: "Weekly credit health summary", enabled: true },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center justify-between py-2">
                <div>
                  <p className="font-medium text-slate-800">{item.label}</p>
                  <p className="text-sm text-slate-500">{item.desc}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked={item.enabled} className="sr-only peer" />
                  <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-consumer"></div>
                </label>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b flex items-center gap-3">
            <Lock className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-800">Security</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between py-2 border-b">
              <div>
                <p className="font-medium text-slate-800">Password</p>
                <p className="text-sm text-slate-500">Last changed 3 months ago</p>
              </div>
              <button className="px-4 py-2 border rounded-lg text-slate-700 hover:bg-slate-50">
                Change Password
              </button>
            </div>
            <div className="flex items-center justify-between py-2 border-b">
              <div>
                <p className="font-medium text-slate-800">Two-Factor Authentication</p>
                <p className="text-sm text-slate-500">Add an extra layer of security</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" defaultChecked className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-consumer"></div>
              </label>
            </div>
            <div className="flex items-center justify-between py-2">
              <div>
                <p className="font-medium text-slate-800">Login History</p>
                <p className="text-sm text-slate-500">View recent account activity</p>
              </div>
              <button className="px-4 py-2 border rounded-lg text-slate-700 hover:bg-slate-50">
                View History
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center gap-3 mb-4">
              <CreditCard className="w-5 h-5 text-slate-500" />
              <h3 className="font-semibold text-slate-800">Connected Accounts</h3>
            </div>
            <p className="text-sm text-slate-600 mb-4">Link accounts for automatic monitoring</p>
            <button className="w-full py-2 border border-consumer text-consumer rounded-lg hover:bg-consumer/5">
              Link Account
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center gap-3 mb-4">
              <Smartphone className="w-5 h-5 text-slate-500" />
              <h3 className="font-semibold text-slate-800">Mobile App</h3>
            </div>
            <p className="text-sm text-slate-600 mb-4">Download our app for on-the-go access</p>
            <button className="w-full py-2 border border-consumer text-consumer rounded-lg hover:bg-consumer/5">
              Get the App
            </button>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button className="px-6 py-2 border rounded-lg text-slate-700 hover:bg-slate-50">
            Cancel
          </button>
          <button className="px-6 py-2 bg-consumer text-white rounded-lg hover:opacity-90">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
