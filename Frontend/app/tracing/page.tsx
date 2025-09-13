"use client"

import { ConversationDetailModal } from "@/components/conversation-detail-modal"
import { ConversationTable } from "@/components/conversation-table"
import { DashboardLayout } from "@/components/dashboard-layout"
import { DatePickerWithRange } from "@/components/date-range-picker"
import { AvgResponseTimeCard, SuccessRateCard, TokenUsageCard, TotalConversationsCard } from "@/components/metric-cards"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { historyService, type HistoryStats, type UserAgent } from "@/lib/api"
import { type Conversation } from "@/lib/types/conversation"
import { Download, Filter, Loader2 } from "lucide-react"
import { useEffect, useState } from "react"

export default function TracingPage() {
  const [userAgents, setUserAgents] = useState<UserAgent[]>([])
  const [stats, setStats] = useState<HistoryStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>("")
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [filters, setFilters] = useState({
    agent: "all",
    platform: "all",
    status: "all",
    search: "",
  })

  // Fetch data from API
  useEffect(() => {
    let mounted = true
    const loadData = async () => {
      try {
        setIsLoading(true)
        setError("")
        const response = await historyService.getUserAgentHistory()
        if (!mounted) return
        
        setUserAgents(response.data.user_agents || [])
        setStats(response.data.stats || null)
      } catch (e: any) {
        if (!mounted) return
        setError(e?.message || "Failed to load conversation data")
      } finally {
        if (mounted) setIsLoading(false)
      }
    }
    
    loadData()
    return () => {
      mounted = false
    }
  }, [])

  // Convert UserAgent data to Conversation format for compatibility
  const conversations: Conversation[] = userAgents.map((userAgent, index) => ({
    id: userAgent.user_agent_id,
    user: userAgent.username,
    agent: userAgent.agent_name,
    platform: userAgent.platform,
    date: userAgent.created_at,
    preview: `Conversation with ${userAgent.agent_name} on ${userAgent.platform}`,
    status: "completed", // Default status since API doesn't provide this
    tokenUsage: stats ? Math.floor(stats.token_usage / stats.total_conversations) : 0, // Average token usage per conversation
    responseTime: stats?.average_response_time || 0,
    confidenceScore: 95, // Default value since API doesn't provide this
    messages: [
      {
        role: "user",
        type: "human" as const,
        content: `Started conversation with ${userAgent.agent_name}`,
        timestamp: new Date(userAgent.created_at).toLocaleTimeString()
      },
      {
        role: "assistant", 
        type: "ai" as const,
        content: "Conversation details not available. Please check the API for full message history.",
        timestamp: new Date(userAgent.created_at).toLocaleTimeString()
      }
    ] // Placeholder messages since API doesn't provide message details
  }))

  const filteredConversations = conversations.filter((conv) => {
    if (filters.agent !== "all" && conv.agent !== filters.agent) return false
    if (filters.platform !== "all" && conv.platform !== filters.platform) return false
    if (filters.status !== "all" && conv.status !== filters.status) return false
    if (
      filters.search &&
      !conv.preview.toLowerCase().includes(filters.search.toLowerCase()) &&
      !conv.user.toLowerCase().includes(filters.search.toLowerCase())
    )
      return false
    return true
  })

  const handleViewConversation = (conversation: Conversation) => {
    setSelectedConversation(conversation)
    setIsDetailOpen(true)
  }

  // Calculate stats from API data
  const totalConversations = stats?.total_conversations || 0
  const avgLength = 0 // Not available in current API
  const successRate = stats?.success_rate || 0
  const avgResponseTime = stats?.average_response_time || 0

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading conversation data...</span>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground font-heading">Conversation Tracing</h1>
            <p className="text-muted-foreground mt-1">Monitor and analyze your AI agent conversations</p>
          </div>
          <Button variant="outline" className="gap-2 bg-transparent">
            <Download className="h-4 w-4" />
            Export Data
          </Button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <TotalConversationsCard 
            value={totalConversations} 
            trend={{ value: 15, isPositive: true }}
          />
          <TokenUsageCard 
            value={stats?.token_usage || 0} 
            trend={{ value: 8, isPositive: true }}
          />
          <SuccessRateCard 
            value={successRate} 
            trend={{ value: 3, isPositive: true }}
          />
          <AvgResponseTimeCard 
            value={avgResponseTime} 
            trend={{ value: 12, isPositive: false }}
          />
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Filters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Search</label>
                <Input
                  placeholder="Search conversations..."
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Agent</label>
                <Select value={filters.agent} onValueChange={(value) => setFilters({ ...filters, agent: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Agents</SelectItem>
                    {Array.from(new Set(userAgents.map(ua => ua.agent_name))).map(agentName => (
                      <SelectItem key={agentName} value={agentName}>{agentName}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Platform</label>
                <Select value={filters.platform} onValueChange={(value) => setFilters({ ...filters, platform: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Platforms</SelectItem>
                    {Array.from(new Set(userAgents.map(ua => ua.platform))).map(platform => (
                      <SelectItem key={platform} value={platform}>{platform}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Status</label>
                <Select value={filters.status} onValueChange={(value) => setFilters({ ...filters, status: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="ongoing">Ongoing</SelectItem>
                    <SelectItem value="failed">Failed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Date Range</label>
                <DatePickerWithRange />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Conversation Table */}
        <ConversationTable conversations={filteredConversations} onViewConversation={handleViewConversation} />

        {/* Conversation Detail Modal */}
        <ConversationDetailModal
          conversation={selectedConversation}
          isOpen={isDetailOpen}
          onClose={() => {
            setIsDetailOpen(false)
            setSelectedConversation(null)
          }}
        />
      </div>
    </DashboardLayout>
  )
}
