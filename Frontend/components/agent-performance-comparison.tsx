"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bot, Minus, TrendingDown, TrendingUp } from "lucide-react"

export function AgentPerformanceComparison() {
  // Mock data for agent performance
  const agentData = [
    {
      name: "Customer Support Bot",
      conversations: 1250,
      avgResponseTime: 1.8,
      successRate: 94.5,
      trend: "up",
      trendValue: 12,
      status: "active"
    },
    {
      name: "Sales Assistant",
      conversations: 890,
      avgResponseTime: 2.3,
      successRate: 87.2,
      trend: "up",
      trendValue: 8,
      status: "active"
    },
    {
      name: "Technical Helper",
      conversations: 650,
      avgResponseTime: 3.1,
      successRate: 91.8,
      trend: "down",
      trendValue: 5,
      status: "active"
    },
    {
      name: "FAQ Bot",
      conversations: 420,
      avgResponseTime: 1.2,
      successRate: 96.1,
      trend: "stable",
      trendValue: 0,
      status: "active"
    },
    {
      name: "Lead Generator",
      conversations: 320,
      avgResponseTime: 2.8,
      successRate: 82.4,
      trend: "down",
      trendValue: 3,
      status: "non-active"
    }
  ]

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-3 w-3 text-green-600" />
      case "down":
        return <TrendingDown className="h-3 w-3 text-red-600" />
      default:
        return <Minus className="h-3 w-3 text-gray-600" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "up":
        return "text-green-600"
      case "down":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Agent Performance</CardTitle>
        <Bot className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {agentData.map((agent, index) => (
            <div key={index} className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Bot className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{agent.name}</span>
                  <Badge 
                    variant={agent.status === "active" ? "default" : "secondary"}
                    className="text-xs"
                  >
                    {agent.status}
                  </Badge>
                </div>
                <div className="flex items-center space-x-1">
                  {getTrendIcon(agent.trend)}
                  <span className={`text-xs font-medium ${getTrendColor(agent.trend)}`}>
                    {agent.trendValue > 0 ? "+" : ""}{agent.trendValue}%
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-bold text-primary">{agent.conversations.toLocaleString()}</div>
                  <div className="text-xs text-muted-foreground">Conversations</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-blue-600">{agent.avgResponseTime}s</div>
                  <div className="text-xs text-muted-foreground">Avg Response</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-green-600">{agent.successRate}%</div>
                  <div className="text-xs text-muted-foreground">Success Rate</div>
                </div>
              </div>

              {/* Performance bar */}
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-primary transition-all duration-500"
                  style={{ width: `${agent.successRate}%` }}
                />
              </div>

              {index < agentData.length - 1 && (
                <div className="border-t border-border" />
              )}
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="pt-4 border-t border-border">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-primary">
                {agentData.reduce((sum, agent) => sum + agent.conversations, 0).toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">Total Conversations</div>
            </div>
            <div>
              <div className="text-lg font-bold text-green-600">
                {(agentData.reduce((sum, agent) => sum + agent.successRate, 0) / agentData.length).toFixed(1)}%
              </div>
              <div className="text-xs text-muted-foreground">Avg Success Rate</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
