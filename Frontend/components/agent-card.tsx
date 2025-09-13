"use client"

import { cn } from "@/lib/utils"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Bot, Cpu, Edit, Globe, MessageCircle, MessageSquare, MoreHorizontal, Phone, Trash2 } from "lucide-react"
import { useEffect, useRef, useState } from "react"

interface Agent {
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

interface AgentCardProps {
  agent: Agent
  onEdit: () => void
  onDelete: () => void
}

const platformIcons = {
  web: Globe,
  whatsapp: Phone,
  telegram: MessageCircle,
}

export function AgentCard({ agent, onEdit, onDelete }: AgentCardProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
    }

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isDropdownOpen])

  return (
    <Card className="card-hover border-border/50 bg-card/50 backdrop-blur-sm overflow-visible">
      <CardHeader className="pb-3 overflow-visible">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <Avatar className="h-10 w-10 ring-2 ring-primary/20">
              <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                {agent.avatar || agent.name.substring(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <h3 className="font-semibold text-foreground font-heading">{agent.name}</h3>
              <Badge
                variant={agent.status === "active" ? "default" : "secondary"}
                className={cn(
                  "text-xs mt-1",
                  agent.status === "active" && "bg-primary/20 text-primary border-primary/30",
                )}
              >
                {agent.status}
              </Badge>
            </div>
          </div>
          <div className="relative" ref={dropdownRef}>
            <Button 
              variant="ghost" 
              size="sm" 
              className="hover:bg-muted/50"
              onClick={() => {
                console.log('Dropdown trigger clicked')
                setIsDropdownOpen(!isDropdownOpen)
              }}
            >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            
            {isDropdownOpen && (
              <div className="absolute right-0 top-8 z-[9999] bg-background border border-border rounded-md shadow-lg min-w-[120px]">
                <div 
                  className="flex items-center px-3 py-2 hover:bg-primary/10 cursor-pointer text-sm"
                  onClick={() => {
                    console.log('Edit clicked')
                    setIsDropdownOpen(false)
                    onEdit()
                  }}
                >
                <Edit className="h-4 w-4 mr-2" />
                Edit
                </div>
                <div 
                  className="flex items-center px-3 py-2 hover:bg-destructive/10 cursor-pointer text-sm text-destructive"
                  onClick={() => {
                    console.log('Delete clicked')
                    setIsDropdownOpen(false)
                    onDelete()
                  }}
                >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
                </div>
              </div>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{agent.description}</p>

        {/* Model */}
        <div className="flex items-center space-x-2">
          <Cpu className="h-4 w-4 text-muted-foreground" />
          <span className="text-xs text-muted-foreground">Model:</span>
          <Badge variant="outline" className="text-xs">
            {agent.model}
          </Badge>
        </div>

        {/* Platform */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-muted-foreground">Platform:</span>
          <div className="flex space-x-1">
            {(() => {
              const Icon = platformIcons[agent.platform as keyof typeof platformIcons] || Bot
              return (
                <div className="h-6 w-6 rounded bg-primary/10 flex items-center justify-center ring-1 ring-primary/20">
                  <Icon className="h-3 w-3 text-primary" />
                </div>
              )
            })()}
            <span className="text-xs text-muted-foreground capitalize">{agent.platform}</span>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-border/50">
          <div>
            <div className="flex items-center space-x-1 text-xs text-muted-foreground">
              <MessageSquare className="h-3 w-3" />
              <span>Conversations</span>
            </div>
            <div className="text-sm font-semibold text-primary">{agent.total_conversations.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Avg Response</div>
            <div className="text-sm font-semibold text-primary">{agent.avg_response_time.toFixed(1)}s</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
