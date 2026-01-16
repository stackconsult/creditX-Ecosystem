"use client";

interface StatusBadgeProps {
  status: string;
  variant?: "default" | "outline";
  size?: "sm" | "md";
}

const statusConfig: Record<string, { bg: string; text: string; border?: string }> = {
  // General
  active: { bg: "bg-emerald-100", text: "text-emerald-700" },
  healthy: { bg: "bg-emerald-100", text: "text-emerald-700" },
  success: { bg: "bg-emerald-100", text: "text-emerald-700" },
  completed: { bg: "bg-emerald-100", text: "text-emerald-700" },
  approved: { bg: "bg-emerald-100", text: "text-emerald-700" },
  resolved: { bg: "bg-emerald-100", text: "text-emerald-700" },
  current: { bg: "bg-emerald-100", text: "text-emerald-700" },
  
  // Warning
  pending: { bg: "bg-amber-100", text: "text-amber-700" },
  pending_review: { bg: "bg-amber-100", text: "text-amber-700" },
  pending_docs: { bg: "bg-amber-100", text: "text-amber-700" },
  in_progress: { bg: "bg-amber-100", text: "text-amber-700" },
  degraded: { bg: "bg-amber-100", text: "text-amber-700" },
  warning: { bg: "bg-amber-100", text: "text-amber-700" },
  investigating: { bg: "bg-amber-100", text: "text-amber-700" },
  trial: { bg: "bg-amber-100", text: "text-amber-700" },
  "30_dpd": { bg: "bg-amber-100", text: "text-amber-700" },
  
  // Info
  info: { bg: "bg-blue-100", text: "text-blue-700" },
  processing: { bg: "bg-blue-100", text: "text-blue-700" },
  draft: { bg: "bg-blue-100", text: "text-blue-700" },
  
  // Error
  error: { bg: "bg-red-100", text: "text-red-700" },
  failed: { bg: "bg-red-100", text: "text-red-700" },
  declined: { bg: "bg-red-100", text: "text-red-700" },
  rejected: { bg: "bg-red-100", text: "text-red-700" },
  blocked: { bg: "bg-red-100", text: "text-red-700" },
  down: { bg: "bg-red-100", text: "text-red-700" },
  suspended: { bg: "bg-red-100", text: "text-red-700" },
  critical: { bg: "bg-red-100", text: "text-red-700" },
  "60_dpd": { bg: "bg-red-100", text: "text-red-700" },
  "90_dpd": { bg: "bg-red-100", text: "text-red-700" },
  default: { bg: "bg-red-100", text: "text-red-700" },
  
  // Neutral
  inactive: { bg: "bg-slate-100", text: "text-slate-600" },
  cancelled: { bg: "bg-slate-100", text: "text-slate-600" },
  withdrawn: { bg: "bg-slate-100", text: "text-slate-600" },
  
  // Risk levels
  low: { bg: "bg-emerald-100", text: "text-emerald-700" },
  medium: { bg: "bg-amber-100", text: "text-amber-700" },
  high: { bg: "bg-orange-100", text: "text-orange-700" },
  
  // Tiers
  prime: { bg: "bg-emerald-100", text: "text-emerald-700" },
  near_prime: { bg: "bg-blue-100", text: "text-blue-700" },
  subprime: { bg: "bg-amber-100", text: "text-amber-700" },
};

export function StatusBadge({ status, variant = "default", size = "sm" }: StatusBadgeProps) {
  const normalizedStatus = status.toLowerCase().replace(/\s+/g, "_");
  const config = statusConfig[normalizedStatus] || { bg: "bg-slate-100", text: "text-slate-600" };
  
  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";
  
  const baseClasses = `inline-flex items-center rounded-full font-medium ${sizeClasses}`;
  
  if (variant === "outline") {
    return (
      <span className={`${baseClasses} border ${config.text} border-current bg-transparent`}>
        {status.replace(/_/g, " ")}
      </span>
    );
  }
  
  return (
    <span className={`${baseClasses} ${config.bg} ${config.text}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}

export default StatusBadge;
