"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Bot, Deploy, Share } from "lucide-react"

interface Agent {
  id: number
  name: string
  avatar: string
  status: "active" | "non-active"
  description: string
  platform: string
}

interface PlaygroundHeaderProps {
  selectedAgent: Agent | null
  onDeploy: () => void
  onShare: () => void
  isDeploying: boolean
}

export function PlaygroundHeader({ 
  selectedAgent, 
  onDeploy, 
  onShare, 
  isDeploying 
}: PlaygroundHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold text-foreground font-heading">Agent Playground</h1>
        <p className="text-muted-foreground mt-1">
          Test your agents before deploying to production
        </p>
      </div>

      <div className="flex items-center space-x-3">
        {selectedAgent && (
          <div className="flex items-center space-x-2 mr-4">
            <Bot className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">{selectedAgent.name}</span>
            <Badge variant={selectedAgent.status === 'active' ? 'default' : 'secondary'}>
              {selectedAgent.status}
            </Badge>
          </div>
        )}

        <Button 
          variant="outline" 
          onClick={onShare}
          disabled={!selectedAgent}
        >
          <Share className="h-4 w-4 mr-2" />
          Share
        </Button>

        <Button 
          onClick={onDeploy}
          disabled={!selectedAgent || isDeploying}
        >
          <Deploy className="h-4 w-4 mr-2" />
          {isDeploying ? "Deploying..." : "Deploy"}
        </Button>
      </div>
    </div>
  )
}
