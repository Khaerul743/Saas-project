"use client"

import { AgentPerformanceComparison } from "@/components/agent-performance-comparison"
import { DailyActivityHeatmap } from "@/components/daily-activity-heatmap"
import { AgentPerformanceChart, ConversationChart, TokenUsageChart } from "@/components/dashboard-charts"
import { ActiveAgentsCard, AvgResponseCard, ConversationsCard, TokenUsageCard } from "@/components/dashboard-metric-cards"
import { ErrorRateAnalysis } from "@/components/error-rate-analysis"
import { PlatformDistributionChart } from "@/components/platform-distribution-chart"
import { ResponseTimeChart } from "@/components/response-time-chart"
import { useEffect, useMemo, useState } from "react"

import { DashboardLayout } from "@/components/dashboard-layout"
import { QuickActions } from "@/components/quick-actions"
import { RecentActivity } from "@/components/recent-activity"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { dashboardService } from "@/lib/api"
import { Plus, TrendingUp } from "lucide-react"

export default function DashboardPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>("")
  const [overview, setOverview] = useState<any | null>(null)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const res = await dashboardService.getOverview()
        if (!mounted) return
        setOverview(res?.data || null)
      } catch (e: any) {
        if (!mounted) return
        setError(e?.message || "Failed to load overview")
      } finally {
        if (mounted) setIsLoading(false)
      }
    }
    load()
    return () => {
      mounted = false
    }
  }, [])

  const tokenUsed = overview?.token_usage ?? 0
  const tokenQuota = 50000
  const usedPercent = useMemo(() => {
    return Math.max(0, Math.min(100, (tokenUsed / tokenQuota) * 100))
  }, [tokenUsed])

  const usageColor = usedPercent < 50 ? "green" : usedPercent < 80 ? "yellow" : "red"

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground font-heading">Dashboard Overview</h1>
            <p className="text-muted-foreground mt-1">Here's what's happening with your AI agents today.</p>
          </div>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Create Agent
          </Button>
        </div>

        {/* Usage Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <TokenUsageCard 
            tokenUsed={tokenUsed}
            tokenQuota={tokenQuota}
            usedPercent={usedPercent}
          />
          <ConversationsCard 
            totalConversations={overview?.total_conversations ?? 0}
            trend={{ value: 12, isPositive: true, text: "+12% from last month" }}
          />
          <ActiveAgentsCard 
            activeAgents={overview?.active_agents ?? 0}
          />
          <AvgResponseCard 
            avgResponseTime={overview?.average_response_time ?? 0}
            successRate={overview?.success_rate ?? 0}
          />
        </div>

        {/* First row - Original charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          <TokenUsageChart />
          <ConversationChart />
          <AgentPerformanceChart />
        </div>

        {/* Second row - New performance charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          <ResponseTimeChart />
          <PlatformDistributionChart />
          <ErrorRateAnalysis />
        </div>

        {/* Third row - Detailed analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AgentPerformanceComparison />
          <DailyActivityHeatmap />
        </div>

        {/* Fourth row - Activity and actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <RecentActivity />
          </div>
          <QuickActions />
        </div>

        {/* Notification/Tips Box */}
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <TrendingUp className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-foreground font-heading">Upgrade to unlock more agents</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  You're currently using 8 of 10 available agent slots. Upgrade to Pro for unlimited agents and advanced
                  analytics.
                </p>
                <Button variant="outline" size="sm" className="mt-3 bg-transparent">
                  Upgrade Plan
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
