"use client"

import { AgentCard } from "@/components/agent-card"
import { AgentDetailModal } from "@/components/agent-detail-modal"
import { AgentSettingsModal } from "@/components/agent-settings-modal"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { agentService } from "@/lib/api"
import { Filter, Plus, Search } from "lucide-react"
import { useEffect, useState } from "react"

type Agent = {
  id?: number
  avatar: string
  name: string
  model: string
  status: "active" | "non-active"
  description: string
  base_prompt: string
  short_term_memory: boolean
  long_term_memory: boolean
  tone: string
  platform: string
  api_key: string
  total_conversations: number
  avg_response_time: number
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>("")
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")

  useEffect(() => {
    let mounted = true
    const loadAgents = async () => {
      try {
        const res = await agentService.getAgents()
        if (!mounted) return
        const agentsData: Agent[] = Array.isArray(res?.data) ? res.data : []
        setAgents(agentsData)
      } catch (e: any) {
        if (!mounted) return
        setError(e?.message || "Failed to load agents")
      } finally {
        if (mounted) setIsLoading(false)
      }
    }
    loadAgents()
    return () => {
      mounted = false
    }
  }, [])

  const filteredAgents = agents.filter(
    (agent) =>
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.model.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const handleEditAgent = (agent: Agent) => {
    setSelectedAgent(agent)
    setIsSettingsOpen(true)
  }

  const handleDetailAgent = (agent: Agent) => {
    setSelectedAgent(agent)
    setIsDetailOpen(true)
  }

  const handleDuplicateAgent = (agent: Agent) => {
    const newAgent = {
      ...agent,
      id: Date.now(),
      name: `${agent.name} (Copy)`,
      status: "non-active" as const,
      total_conversations: 0,
    }
    setAgents([...agents, newAgent])
  }

  const handleDeleteAgent = async (agentId: string | number) => {
    // Show confirmation dialog
    const confirmed = window.confirm('Are you sure you want to delete this agent? This action cannot be undone.')
    
    if (!confirmed) {
      return
    }

    try {
      // Convert string to number if needed
      const agentIdNum = typeof agentId === 'string' ? parseInt(agentId) : agentId
      
      // Validate agent ID
      if (isNaN(agentIdNum) || agentIdNum <= 0) {
        alert('Invalid agent ID. Cannot delete this agent.')
        return
      }
      
      // Call delete API
      await agentService.deleteAgent(agentIdNum)
      
      // Remove agent from local state
      setAgents(agents.filter((agent) => agent.id !== agentIdNum))
      
      // Show success message
      alert('Agent deleted successfully!')
      
    } catch (error: any) {
      console.error('Error deleting agent:', error)
      
      // Handle different types of errors
      if (error.response?.status === 404) {
        alert('Agent not found. It may have already been deleted.')
        // Remove from local state anyway since it doesn't exist on server
        setAgents(agents.filter((agent) => agent.id !== agentId))
      } else if (error.response?.status === 401) {
        alert('Authentication failed. Please log in again.')
      } else if (error.response?.status === 403) {
        alert('You do not have permission to delete this agent.')
      } else {
        alert('Failed to delete agent. Please try again.')
      }
    }
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex items-center space-x-2">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
            <span className="text-muted-foreground">Loading agents...</span>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className="text-destructive mb-4">{error}</p>
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
            <h1 className="text-3xl font-bold text-foreground font-heading">AI Agents</h1>
            <p className="text-muted-foreground mt-1">Manage and configure your AI agents</p>
          </div>
          <Button className="gap-2" onClick={() => setIsSettingsOpen(true)}>
            <Plus className="h-4 w-4" />
            Create Agent
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center space-x-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search agents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline" className="gap-2 bg-transparent">
            <Filter className="h-4 w-4" />
            Filter
          </Button>
        </div>

        {/* Agents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 overflow-visible">
          {filteredAgents.map((agent, index) => (
            <AgentCard
              key={agent.id || index}
              agent={agent}
              onEdit={() => handleEditAgent(agent)}
              onDelete={() => handleDeleteAgent(agent.id || index)}
              onDetail={() => handleDetailAgent(agent)}
            />
          ))}
        </div>

        {/* Agent Settings Modal */}
        <AgentSettingsModal
          agent={selectedAgent}
          isOpen={isSettingsOpen}
          onClose={() => {
            setIsSettingsOpen(false)
            setSelectedAgent(null)
          }}
        />

        {/* Agent Detail Modal */}
        <AgentDetailModal
          agent={selectedAgent}
          isOpen={isDetailOpen}
          onClose={() => {
            setIsDetailOpen(false)
            setSelectedAgent(null)
          }}
        />
      </div>
    </DashboardLayout>
  )
}
