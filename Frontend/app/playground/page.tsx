"use client"

import { DashboardLayout } from "@/components/dashboard-layout"
import { AgentSelector } from "@/components/playground/agent-selector"
import { ChatInterface } from "@/components/playground/chat-interface"
import { PlaygroundHeader } from "@/components/playground/playground-header"
import { ShareModal } from "@/components/playground/share-modal"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { agentService } from "@/lib/api"
import { Bot, MessageCircle, Play, Share, Zap } from "lucide-react"
import { useEffect, useState } from "react"

interface Agent {
  id: number
  name: string
  avatar: string
  status: "active" | "non-active"
  description: string
  platform: string
}

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export default function PlaygroundPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isDeploying, setIsDeploying] = useState(false)
  const [showShareModal, setShowShareModal] = useState(false)
  const [isLoadingAgents, setIsLoadingAgents] = useState(true)

  // Load agents on component mount
  useEffect(() => {
    const loadAgents = async () => {
      try {
        const response = await agentService.getAgents()
        if (response.status === 'success') {
          setAgents(response.data || [])
          // Auto-select first active agent if available
          const activeAgent = response.data?.find((agent: Agent) => agent.status === 'active')
          if (activeAgent) {
            setSelectedAgent(activeAgent)
          }
        }
      } catch (error) {
        console.error('Failed to load agents:', error)
      } finally {
        setIsLoadingAgents(false)
      }
    }

    loadAgents()
  }, [])

  // Initialize chat with welcome message when agent is selected
  useEffect(() => {
    if (selectedAgent) {
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: `Hi! I'm ${selectedAgent.name}, your AI assistant. How can I help you today?`,
          timestamp: new Date()
        }
      ])
    }
  }, [selectedAgent])

  const handleSendMessage = async (message: string) => {
    if (!selectedAgent || !message.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Simulate API call to test agent
      // In real implementation, this would call the agent testing endpoint
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const agentResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `This is a test response from ${selectedAgent.name}. In a real implementation, this would be the actual agent response based on your message: "${message}"`,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, agentResponse])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleResetChat = () => {
    if (selectedAgent) {
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: `Hi! I'm ${selectedAgent.name}, your AI assistant. How can I help you today?`,
          timestamp: new Date()
        }
      ])
    }
  }

  const handleDeployAgent = async () => {
    if (!selectedAgent) return

    setIsDeploying(true)
    try {
      // Simulate deployment process
      await new Promise(resolve => setTimeout(resolve, 2000))
      alert(`${selectedAgent.name} has been deployed successfully!`)
    } catch (error) {
      console.error('Failed to deploy agent:', error)
      alert('Failed to deploy agent. Please try again.')
    } finally {
      setIsDeploying(false)
    }
  }

  const handleShareAgent = () => {
    setShowShareModal(true)
  }

  if (isLoadingAgents) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Bot className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">Loading agents...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (agents.length === 0) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Bot className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No Agents Available</h3>
            <p className="text-muted-foreground mb-4">Create your first agent to start testing in the playground.</p>
            <Button>
              <Bot className="h-4 w-4 mr-2" />
              Create Agent
            </Button>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <PlaygroundHeader 
          selectedAgent={selectedAgent}
          onDeploy={handleDeployAgent}
          onShare={handleShareAgent}
          isDeploying={isDeploying}
        />

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Agent Selector Sidebar */}
          <div className="lg:col-span-1">
            <AgentSelector
              agents={agents}
              selectedAgent={selectedAgent}
              onSelectAgent={setSelectedAgent}
            />
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <Card className="h-[600px] flex flex-col">
              <CardContent className="flex-1 flex flex-col p-0">
                {selectedAgent ? (
                  <ChatInterface
                    messages={messages}
                    onSendMessage={handleSendMessage}
                    onResetChat={handleResetChat}
                    isLoading={isLoading}
                    agentName={selectedAgent.name}
                  />
                ) : (
                  <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                      <MessageCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-lg font-semibold mb-2">Select an Agent</h3>
                      <p className="text-muted-foreground">Choose an agent from the sidebar to start testing.</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                <Play className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h4 className="font-semibold">Quick Test</h4>
                <p className="text-sm text-muted-foreground">Test your agent with common scenarios</p>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                <Share className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <h4 className="font-semibold">Share & Demo</h4>
                <p className="text-sm text-muted-foreground">Share test link with stakeholders</p>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
                <Zap className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <h4 className="font-semibold">Deploy</h4>
                <p className="text-sm text-muted-foreground">Deploy your agent to production</p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Share Modal */}
      <ShareModal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        agent={selectedAgent}
      />
    </DashboardLayout>
  )
}
