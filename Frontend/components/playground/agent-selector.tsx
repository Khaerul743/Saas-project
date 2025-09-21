"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { Bot, Code, Globe, MessageCircle, Phone } from "lucide-react"

interface Agent {
  id: number
  name: string
  avatar: string
  status: "active" | "non-active"
  description: string
  platform: string
}

interface AgentSelectorProps {
  agents: Agent[]
  selectedAgent: Agent | null
  onSelectAgent: (agent: Agent) => void
}

const platformIcons = {
  telegram: MessageCircle,
  whatsapp: Phone,
  website: Globe,
  api: Code,
}

export function AgentSelector({ agents, selectedAgent, onSelectAgent }: AgentSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-heading">Select Agent</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {agents.length === 0 ? (
          <div className="text-center py-8">
            <Bot className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">No agents available</p>
          </div>
        ) : (
          agents.map((agent) => {
            const PlatformIcon = platformIcons[agent.platform as keyof typeof platformIcons] || Bot
            
            return (
              <div
                key={agent.id}
                onClick={() => onSelectAgent(agent)}
                className={cn(
                  "p-3 rounded-lg border cursor-pointer transition-all hover:bg-muted/50",
                  selectedAgent?.id === agent.id 
                    ? "border-primary bg-primary/5" 
                    : "border-border hover:border-primary/50"
                )}
              >
                <div className="flex items-start space-x-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-primary/10 text-primary text-sm font-semibold">
                      {agent.avatar || agent.name.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-sm font-semibold truncate">{agent.name}</h4>
                      <Badge 
                        variant={agent.status === 'active' ? 'default' : 'secondary'}
                        className="text-xs"
                      >
                        {agent.status}
                      </Badge>
                    </div>
                    
                    <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                      {agent.description}
                    </p>
                    
                    <div className="flex items-center space-x-1">
                      <PlatformIcon className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground capitalize">
                        {agent.platform}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </CardContent>
    </Card>
  )
}
