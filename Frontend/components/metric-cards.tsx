"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Clock, MessageSquare, TrendingUp } from "lucide-react"

interface MetricCardProps {
  title: string
  value: string | number
  subtitle: string
  icon: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  chartData?: number[]
  color?: string
}

function MetricCard({ title, value, subtitle, icon, trend, chartData, color = "primary" }: MetricCardProps) {
  const getColorClasses = (color: string) => {
    switch (color) {
      case "green":
        return {
          bg: "bg-green-500",
          text: "text-green-600",
          light: "bg-green-50",
          border: "border-green-200"
        }
      case "blue":
        return {
          bg: "bg-blue-500",
          text: "text-blue-600",
          light: "bg-blue-50",
          border: "border-blue-200"
        }
      case "orange":
        return {
          bg: "bg-orange-500",
          text: "text-orange-600",
          light: "bg-orange-50",
          border: "border-orange-200"
        }
      case "purple":
        return {
          bg: "bg-purple-500",
          text: "text-purple-600",
          light: "bg-purple-50",
          border: "border-purple-200"
        }
      default:
        return {
          bg: "bg-primary",
          text: "text-primary",
          light: "bg-primary/10",
          border: "border-primary/20"
        }
    }
  }

  const colors = getColorClasses(color)

  return (
    <Card className="relative overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={`p-3 rounded-full ${colors.light}`}>
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Main value */}
          <div className="flex items-baseline space-x-2">
            <div className={`text-3xl font-bold ${colors.text}`}>
              {typeof value === 'number' ? value.toLocaleString() : value}
            </div>
            {trend && (
              <div className={`flex items-center space-x-1 text-sm ${
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                <TrendingUp className={`h-3 w-3 ${!trend.isPositive ? 'rotate-180' : ''}`} />
                <span>{Math.abs(trend.value)}%</span>
              </div>
            )}
          </div>
          
          <p className="text-xs text-muted-foreground">{subtitle}</p>

          {/* Color accent bar */}
          <div className={`h-1 w-full ${colors.bg} rounded-full opacity-60`} />
        </div>
      </CardContent>
    </Card>
  )
}

export function TotalConversationsCard({ value, trend }: { value: number, trend?: { value: number, isPositive: boolean } }) {
  return (
    <MetricCard
      title="Total Conversations"
      value={value}
      subtitle="total conversations"
      icon={<MessageSquare className="h-4 w-4 text-primary" />}
      trend={trend}
      color="primary"
    />
  )
}

export function TokenUsageCard({ value, trend }: { value: number, trend?: { value: number, isPositive: boolean } }) {
  return (
    <MetricCard
      title="Token Usage"
      value={value.toLocaleString()}
      subtitle="total tokens used"
      icon={<TrendingUp className="h-4 w-4 text-blue-600" />}
      trend={trend}
      color="blue"
    />
  )
}

export function SuccessRateCard({ value, trend }: { value: number, trend?: { value: number, isPositive: boolean } }) {
  return (
    <MetricCard
      title="Success Rate"
      value={`${value.toFixed(1)}%`}
      subtitle="completed successfully"
      icon={<TrendingUp className="h-4 w-4 text-green-600" />}
      trend={trend}
      color="green"
    />
  )
}

export function AvgResponseTimeCard({ value, trend }: { value: number, trend?: { value: number, isPositive: boolean } }) {
  return (
    <MetricCard
      title="Avg Response Time"
      value={`${value.toFixed(1)}s`}
      subtitle="average response time"
      icon={<Clock className="h-4 w-4 text-orange-600" />}
      trend={trend}
      color="orange"
    />
  )
}
