"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: number;
  trendLabel?: string;
  icon?: React.ReactNode;
  color?: "default" | "success" | "warning" | "error" | "info" | "consumer" | "partner" | "internal";
}

export function MetricCard({
  title,
  value,
  subtitle,
  trend,
  trendLabel,
  icon,
  color = "default",
}: MetricCardProps) {
  const colorClasses = {
    default: "text-slate-800",
    success: "text-emerald-600",
    warning: "text-amber-500",
    error: "text-red-500",
    info: "text-blue-600",
    consumer: "text-consumer",
    partner: "text-partner",
    internal: "text-internal",
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend > 0) return <TrendingUp className="w-4 h-4 text-emerald-500" />;
    if (trend < 0) return <TrendingDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-slate-400" />;
  };

  const getTrendColor = () => {
    if (!trend) return "text-slate-500";
    return trend > 0 ? "text-emerald-600" : "text-red-600";
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
          <p className={`text-3xl font-bold ${colorClasses[color]}`}>{value}</p>
          {subtitle && (
            <p className="text-sm text-slate-600 mt-1">{subtitle}</p>
          )}
          {trend !== undefined && (
            <div className={`flex items-center gap-1 mt-2 ${getTrendColor()}`}>
              {getTrendIcon()}
              <span className="text-sm font-medium">
                {trend > 0 ? "+" : ""}
                {trend}%
              </span>
              {trendLabel && (
                <span className="text-slate-500 text-sm">{trendLabel}</span>
              )}
            </div>
          )}
        </div>
        {icon && (
          <div className="p-2 bg-slate-100 rounded-lg">{icon}</div>
        )}
      </div>
    </div>
  );
}

export default MetricCard;
