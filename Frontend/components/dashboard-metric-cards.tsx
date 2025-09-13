"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { ArrowUpRight, Bot, MessageSquare, TrendingUp, Zap } from "lucide-react"

interface DashboardMetricCardProps {
  title: string
  value: string | number
  subtitle: string
  icon: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
    text: string
  }
  progress?: {
    value: number
    max: number
    color: string
  }
  color?: string
  children?: React.ReactNode
}

function DashboardMetricCard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend, 
  progress, 
  color = "primary",
  children 
}: DashboardMetricCardProps) {
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
    <Card className={`relative overflow-hidden border-l-4 ${colors.border}`}>
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
                <span>{trend.text}</span>
              </div>
            )}
          </div>
          
          <p className="text-xs text-muted-foreground">{subtitle}</p>

          {/* Progress bar if provided */}
          {progress && (
            <div className="space-y-2">
              <Progress value={progress.value} color={progress.color as any} className="h-2" />
              <div className="text-xs text-muted-foreground">
                {progress.value.toFixed(1)}% of {progress.max.toLocaleString()}
              </div>
            </div>
          )}

          {/* Custom content */}
          {children}

          {/* Color accent bar */}
          <div className={`h-1 w-full ${colors.bg} rounded-full opacity-60`} />
        </div>
      </CardContent>
    </Card>
  )
}

export function TokenUsageCard({ 
  tokenUsed, 
  tokenQuota, 
  usedPercent 
}: { 
  tokenUsed: number
  tokenQuota: number
  usedPercent: number
}) {
  const usageColor = usedPercent < 50 ? "green" : usedPercent < 80 ? "yellow" : "red"
  
  return (
    <DashboardMetricCard
      title="Token Usage"
      value={tokenUsed.toLocaleString()}
      subtitle={`of ${tokenQuota.toLocaleString()} tokens`}
      icon={<Zap className="h-4 w-4 text-primary" />}
      progress={{
        value: usedPercent,
        max: 100,
        color: usageColor
      }}
      color="primary"
    />
  )
}

export function ConversationsCard({ 
  totalConversations, 
  trend 
}: { 
  totalConversations: number
  trend?: { value: number, isPositive: boolean, text: string }
}) {
  return (
    <DashboardMetricCard
      title="Conversations"
      value={totalConversations.toLocaleString()}
      subtitle="total conversations"
      icon={<MessageSquare className="h-4 w-4 text-blue-600" />}
      trend={trend}
      color="blue"
    />
  )
}

export function ActiveAgentsCard({ 
  activeAgents 
}: { 
  activeAgents: number
}) {
  return (
    <DashboardMetricCard
      title="Active Agents"
      value={activeAgents}
      subtitle="currently running"
      icon={<Bot className="h-4 w-4 text-green-600" />}
      color="green"
    >
      <div className="flex items-center space-x-1 mt-2">
        <div className="flex -space-x-1">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-6 w-6 rounded-full bg-primary/20 border-2 border-background flex items-center justify-center"
            >
              <Bot className="h-3 w-3 text-primary" />
            </div>
          ))}
        </div>
        <span className="text-xs text-muted-foreground">+5 more</span>
      </div>
    </DashboardMetricCard>
  )
}

export function AvgResponseCard({ 
  avgResponseTime, 
  successRate 
}: { 
  avgResponseTime: number
  successRate: number
}) {
  return (
    <DashboardMetricCard
      title="Avg Response"
      value={`${avgResponseTime.toFixed(1)}s`}
      subtitle={`${successRate.toFixed(1)}% success rate`}
      icon={<ArrowUpRight className="h-4 w-4 text-orange-600" />}
      color="orange"
    />
  )
}
