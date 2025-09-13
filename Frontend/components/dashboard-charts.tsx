"use client"

import { useEffect, useMemo, useState } from "react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { dashboardService } from "@/lib/api"
import { Area, AreaChart, Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, XAxis, YAxis } from "recharts"

type TokenPoint = { period: string; total_tokens: number }
type ConversationPoint = { period: string; total_conversations: number }
type AgentPoint = { agent_id: number; agent_name: string; total_tokens: number }

const conversationData = [
  { hour: "00", conversations: 12 },
  { hour: "04", conversations: 8 },
  { hour: "08", conversations: 45 },
  { hour: "12", conversations: 78 },
  { hour: "16", conversations: 92 },
  { hour: "20", conversations: 65 },
]

const agentPerformanceData = [
  { name: "Customer Support", value: 35, color: "hsl(var(--chart-1))" },
  { name: "Sales Assistant", value: 25, color: "hsl(var(--chart-2))" },
  { name: "FAQ Bot", value: 20, color: "hsl(var(--chart-3))" },
  { name: "Lead Qualifier", value: 20, color: "hsl(var(--chart-4))" },
]

export function TokenUsageChart() {
  const [data, setData] = useState<TokenPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>("")

  // last 7 days range
  const { startDate, endDate } = useMemo(() => {
    const end = new Date()
    const start = new Date()
    start.setDate(end.getDate() - 6)
    // Add 1 day to endDate to include today's data
    end.setDate(end.getDate() + 1)
    const fmt = (d: Date) => d.toISOString().slice(0, 10)
    return { startDate: fmt(start), endDate: fmt(end) }
  }, [])

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const res = await dashboardService.getTokenAnalytics({ start_date: startDate, end_date: endDate, group_by: "day" })
        if (!mounted) return
        const arr: TokenPoint[] = Array.isArray(res?.data) ? res.data : []
        setData(arr)
      } catch (e: any) {
        if (!mounted) return
        setError(e?.message || "Failed to load token analytics")
      } finally {
        if (mounted) setIsLoading(false)
      }
    }
    load()
    return () => {
      mounted = false
    }
  }, [startDate, endDate])

  const chartData = useMemo(() => {
    // Map API data to chart rows with readable day label
    return data.map((p) => {
      const d = new Date(p.period)
      const label = d.toLocaleDateString(undefined, { month: "short", day: "2-digit" })
      return { day: label, tokens: p.total_tokens }
    })
  }, [data])

  const totalTokens = useMemo(() => data.reduce((sum, p) => sum + (p.total_tokens || 0), 0), [data])

  return (
    <Card className="lg:col-span-full">
      <CardHeader>
        <CardTitle className="text-base font-heading">Token Usage Trend</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            tokens: {
              label: "Tokens",
              color: "hsl(var(--chart-1))",
            },
          }}
          className="h-[200px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="tokenGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="50%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.2} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="day"
                axisLine={false}
                tickLine={false}
                className="text-xs"
                tick={{ fill: "hsl(var(--muted-foreground))" }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                className="text-xs"
                tick={{ fill: "hsl(var(--muted-foreground))" }}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Area
                type="monotone"
                dataKey="tokens"
                stroke="#10b981"
                fill="url(#tokenGradient)"
                fillOpacity={1}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartContainer>

        <div className="mt-6">
          <h4 className="text-sm font-medium mb-3 text-muted-foreground">Daily Breakdown</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-medium text-muted-foreground">Day</th>
                  <th className="text-right py-2 font-medium text-muted-foreground">Tokens</th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((item, index) => (
                  <tr key={index} className="border-b border-border/50">
                    <td className="py-2 font-medium">{item.day}</td>
                    <td className="text-right py-2">{item.tokens.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t border-border font-medium">
                  <td className="py-2">Total</td>
                  <td className="text-right py-2">{totalTokens.toLocaleString()}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function ConversationChart() {
  const [data, setData] = useState<ConversationPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>("")

  // last 7 days range
  const { startDate, endDate } = useMemo(() => {
    const end = new Date()
    const start = new Date()
    start.setDate(end.getDate() - 6)
    // Add 1 day to endDate to include today's data
    end.setDate(end.getDate() + 1)
    const fmt = (d: Date) => d.toISOString().slice(0, 10)
    return { startDate: fmt(start), endDate: fmt(end) }
  }, [])

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const res = await dashboardService.getConversationAnalytics({ start_date: startDate, end_date: endDate, group_by: "day" })
        if (!mounted) return
        const arr: ConversationPoint[] = Array.isArray(res?.data) ? res.data : []
        setData(arr)
      } catch (e: any) {
        if (!mounted) return
        setError(e?.message || "Failed to load conversation analytics")
      } finally {
        if (mounted) setIsLoading(false)
      }
    }
    load()
    return () => {
      mounted = false
    }
  }, [startDate, endDate])

  const chartData = useMemo(() => {
    // Map API data to chart rows with readable day label
    return data.map((p) => {
      const d = new Date(p.period)
      const label = d.toLocaleDateString(undefined, { month: "short", day: "2-digit" })
      return { day: label, conversations: p.total_conversations }
    })
  }, [data])

  const totalConversations = useMemo(() => data.reduce((sum, p) => sum + (p.total_conversations || 0), 0), [data])

  return (
    <Card className="lg:col-span-full">
      <CardHeader>
        <CardTitle className="text-base font-heading">Conversations Trend</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            conversations: {
              label: "Conversations",
              color: "hsl(var(--chart-2))",
            },
          }}
          className="h-[200px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <defs>
                <linearGradient id="convGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.9} />
                  <stop offset="50%" stopColor="#8b5cf6" stopOpacity={0.8} />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.7} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="day"
                axisLine={false}
                tickLine={false}
                className="text-xs"
                tick={{ fill: "hsl(var(--muted-foreground))" }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                className="text-xs"
                tick={{ fill: "hsl(var(--muted-foreground))" }}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar dataKey="conversations" fill="url(#convGradient)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>

        <div className="mt-6">
          <h4 className="text-sm font-medium mb-3 text-muted-foreground">Daily Breakdown</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-medium text-muted-foreground">Day</th>
                  <th className="text-right py-2 font-medium text-muted-foreground">Conversations</th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((item, index) => (
                  <tr key={index} className="border-b border-border/50">
                    <td className="py-2 font-medium">{item.day}</td>
                    <td className="text-right py-2">{item.conversations.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t border-border font-medium">
                  <td className="py-2">Total</td>
                  <td className="text-right py-2">{totalConversations.toLocaleString()}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function AgentPerformanceChart() {
  const [data, setData] = useState<AgentPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>("")

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const res = await dashboardService.getAgentAnalytics()
        if (!mounted) return
        const agents: AgentPoint[] = Array.isArray(res?.data?.agents) ? res.data.agents : []
        setData(agents)
      } catch (e: any) {
        if (!mounted) return
        setError(e?.message || "Failed to load agent analytics")
      } finally {
        if (mounted) setIsLoading(false)
      }
    }
    load()
    return () => {
      mounted = false
    }
  }, [])

  const chartData = useMemo(() => {
    const totalTokens = data.reduce((sum, agent) => sum + (agent.total_tokens || 0), 0)
    
    // Define colors for each agent
    const colors = ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4", "#84cc16", "#f97316"]
    
    return data.map((agent, index) => {
      const percentage = totalTokens > 0 ? ((agent.total_tokens / totalTokens) * 100) : 0
      return {
        name: agent.agent_name,
        value: percentage,
        tokens: agent.total_tokens,
        color: colors[index % colors.length]
      }
    })
  }, [data])

  const totalTokens = useMemo(() => data.reduce((sum, agent) => sum + (agent.total_tokens || 0), 0), [data])

  return (
    <Card className="lg:col-span-full">
      <CardHeader>
        <CardTitle className="text-base font-heading">Token Usage by Agent</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={chartData.reduce((acc, item) => {
            acc[item.name] = {
              label: item.name,
              color: item.color,
            }
            return acc
          }, {} as Record<string, { label: string; color: string }>)}
          className="h-[200px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
                nameKey="name"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <ChartTooltip content={<ChartTooltipContent nameKey="name" />} />
            </PieChart>
          </ResponsiveContainer>
        </ChartContainer>
        <div className="mt-4 space-y-2">
          {chartData.map((item, index) => (
            <div key={index} className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-2">
                <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-foreground">{item.name}</span>
              </div>
              <div className="text-right">
                <span className="font-medium text-foreground">{item.value.toFixed(1)}%</span>
                <span className="text-xs text-muted-foreground ml-2">({item.tokens.toLocaleString()} tokens)</span>
              </div>
            </div>
          ))}
        </div>
        {totalTokens > 0 && (
          <div className="mt-4 pt-3 border-t border-border">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Total Tokens:</span>
              <span className="font-medium text-foreground">{totalTokens.toLocaleString()}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
