"use client"

import { ChatInterface } from "@/components/playground"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { agentService, Agent as ApiAgent } from "@/lib/api"
import { ArrowLeft, Bot } from "lucide-react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"

// Playground-specific Agent type with required id
interface Agent extends Omit<ApiAgent, 'id'> {
  id: number
}

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export default function TestAgentPage() {
  const params = useParams()
  const router = useRouter()
  const agentId = params.agentId as string
  
  const [agent, setAgent] = useState<Agent | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingAgent, setIsLoadingAgent] = useState(true)
  const [error, setError] = useState<string>("")

  // Load agent data
  useEffect(() => {
    const loadAgent = async () => {
      try {
        const response = await agentService.getAgent(parseInt(agentId))
        if (response.status === 'success' && response.data.id !== undefined) {
          // Convert to playground Agent type
          const agentWithId = { ...response.data, id: response.data.id! }
          setAgent(agentWithId)
          // Initialize with welcome message
          setMessages([
            {
              id: '1',
              role: 'assistant',
              content: `Hi! I'm ${agentWithId.name}, your AI assistant. How can I help you today?`,
              timestamp: new Date()
            }
          ])
        } else {
          setError('Agent not found')
        }
      } catch (error) {
        console.error('Failed to load agent:', error)
        setError('Failed to load agent')
      } finally {
        setIsLoadingAgent(false)
      }
    }

    if (agentId) {
      loadAgent()
    }
  }, [agentId])

  const handleSendMessage = async (userMessage: string, agentResponse?: string) => {
    if (!agent || !userMessage.trim()) return

    // Add user message
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMsg])

    // If agentResponse is provided, add it directly
    if (agentResponse) {
      const agentMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: agentResponse,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, agentMsg])
    } else {
      // Set loading state if no response provided yet
      setIsLoading(true)
    }
  }

  const handleResetChat = () => {
    if (agent) {
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: `Hi! I'm ${agent.name}, your AI assistant. How can I help you today?`,
          timestamp: new Date()
        }
      ])
    }
  }

  if (isLoadingAgent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Bot className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">Loading agent...</p>
        </div>
      </div>
    )
  }

  if (error || !agent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Bot className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Agent Not Found</h3>
          <p className="text-muted-foreground mb-4">{error || 'The agent you are looking for does not exist.'}</p>
          <Button onClick={() => router.push('/playground')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Playground
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Link href="/playground">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Playground
                </Button>
              </Link>
              <div className="h-6 w-px bg-border" />
              <div className="flex items-center space-x-2">
                <Bot className="h-5 w-5 text-primary" />
                <span className="font-semibold">{agent.name}</span>
              </div>
            </div>
            <div className="text-sm text-muted-foreground">
              Test Mode
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6">
        <div className="max-w-4xl mx-auto">
          {/* Agent Info */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                {agent.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{agent.description}</p>
              <div className="mt-2 text-sm text-muted-foreground">
                Platform: {agent.platform} • Status: {agent.status}
              </div>
            </CardContent>
          </Card>

          {/* Chat Interface */}
          <Card className="h-[600px]">
            <CardContent className="p-0 h-full">
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                onResetChat={handleResetChat}
                isLoading={isLoading}
                agentName={agent.name}
                agentId={agent.id}
              />
            </CardContent>
          </Card>

          {/* Footer */}
          <div className="mt-6 text-center text-sm text-muted-foreground">
            <p>This is a test environment. Responses are simulated for demonstration purposes.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
