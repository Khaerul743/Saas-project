"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import {
    Bot,
    Check,
    Clock,
    Code,
    Copy,
    Eye,
    EyeOff,
    Globe,
    MessageCircle,
    MessageSquare,
    Phone,
    Settings,
    Shield,
    Zap
} from "lucide-react"
import { useState } from "react"

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

interface AgentDetailModalProps {
  agent: Agent | null
  isOpen: boolean
  onClose: () => void
}

const platformIcons = {
  web: Globe,
  website: Globe,
  whatsapp: Phone,
  telegram: MessageCircle,
  api: Code,
}

const platformNames = {
  web: "Website",
  website: "Website", 
  whatsapp: "WhatsApp",
  telegram: "Telegram",
  api: "API",
}

export function AgentDetailModal({ agent, isOpen, onClose }: AgentDetailModalProps) {
  const [showApiKey, setShowApiKey] = useState(false)
  const [copied, setCopied] = useState(false)

  if (!agent) return null

  const handleCopyApiKey = async () => {
    try {
      await navigator.clipboard.writeText(agent.api_key)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy API key:', err)
    }
  }

  const PlatformIcon = platformIcons[agent.platform as keyof typeof platformIcons] || Bot
  const platformName = platformNames[agent.platform as keyof typeof platformNames] || agent.platform

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl max-h-[95vh] overflow-y-auto p-4 sm:p-6">
        <DialogHeader className="pb-4">
          <DialogTitle className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <Avatar className="h-12 w-12 sm:h-10 sm:w-10 ring-2 ring-primary/20 flex-shrink-0">
              <AvatarFallback className="bg-primary/10 text-primary font-semibold text-sm sm:text-base">
                {agent.avatar || agent.name.substring(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="min-w-0 flex-1">
              <h2 className="text-lg sm:text-xl font-heading truncate">{agent.name}</h2>
              <Badge
                variant={agent.status === "active" ? "default" : "secondary"}
                className={`mt-1 text-xs ${
                  agent.status === "active" 
                    ? "bg-primary/20 text-primary border-primary/30" 
                    : ""
                }`}
              >
                {agent.status}
              </Badge>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Agent Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Bot className="h-4 w-4" />
                Agent Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Description</label>
                <p className="text-sm mt-1">{agent.description}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-muted-foreground">Base Prompt</label>
                <div className="mt-1 p-4 bg-muted/50 rounded-lg border">
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{agent.base_prompt}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Tone</label>
                  <Badge variant="outline" className="mt-1 capitalize">
                    {agent.tone}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Model</label>
                  <Badge variant="outline" className="mt-1">
                    {agent.model}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Status</label>
                  <Badge 
                    variant={agent.status === "active" ? "default" : "secondary"}
                    className={`mt-1 ${
                      agent.status === "active" 
                        ? "bg-primary/20 text-primary border-primary/30" 
                        : ""
                    }`}
                  >
                    {agent.status}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Agent ID</label>
                  <div className="mt-1">
                    <span className="font-mono text-xs bg-muted px-2 py-1 rounded">
                      {agent.id}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Memory Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Memory Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                  <div>
                    <label className="text-sm font-medium">Short-term Memory</label>
                    <p className="text-xs text-muted-foreground">Remember recent conversations</p>
                  </div>
                  <Badge variant={agent.short_term_memory ? "default" : "secondary"}>
                    {agent.short_term_memory ? "Enabled" : "Disabled"}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                  <div>
                    <label className="text-sm font-medium">Long-term Memory</label>
                    <p className="text-xs text-muted-foreground">Learn from all interactions</p>
                  </div>
                  <Badge variant={agent.long_term_memory ? "default" : "secondary"}>
                    {agent.long_term_memory ? "Enabled" : "Disabled"}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Platform Integration */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Platform Integration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center ring-1 ring-primary/20">
                  <PlatformIcon className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-medium text-base">{platformName}</h3>
                  <p className="text-sm text-muted-foreground capitalize">{agent.platform} integration</p>
                </div>
              </div>

              {agent.api_key && (
                <div className="space-y-3">
                  <label className="text-sm font-medium text-muted-foreground">API Key</label>
                  
                  {/* Mobile Layout - Stacked */}
                  <div className="flex flex-col sm:hidden space-y-3">
                    <div className="p-4 bg-muted/50 rounded-lg border font-mono text-xs break-all">
                      {showApiKey ? agent.api_key : "•".repeat(32)}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="flex-1"
                      >
                        {showApiKey ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
                        {showApiKey ? "Hide" : "Show"}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopyApiKey}
                        className={`flex-1 ${copied ? "bg-green-50 border-green-200" : ""}`}
                      >
                        {copied ? <Check className="h-4 w-4 mr-1 text-green-600" /> : <Copy className="h-4 w-4 mr-1" />}
                        {copied ? "Copied!" : "Copy"}
                      </Button>
                    </div>
                  </div>

                  {/* Desktop Layout - Horizontal */}
                  <div className="hidden sm:flex items-center gap-3">
                    <div className="flex-1 p-4 bg-muted/50 rounded-lg border font-mono text-sm break-all min-w-0">
                      {showApiKey ? agent.api_key : "•".repeat(32)}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="flex-shrink-0"
                    >
                      {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCopyApiKey}
                      className={`flex-shrink-0 ${copied ? "bg-green-50 border-green-200" : ""}`}
                    >
                      {copied ? <Check className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>

                  {copied && (
                    <p className="text-xs text-green-600 flex items-center gap-1">
                      <Check className="h-3 w-3" />
                      API key copied to clipboard
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Performance Statistics */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Performance Statistics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-primary/5 rounded-lg border border-primary/20">
                  <MessageSquare className="h-6 w-6 text-primary mx-auto mb-2" />
                  <div className="text-2xl font-bold text-primary">{agent.total_conversations.toLocaleString()}</div>
                  <div className="text-xs text-muted-foreground">Total Conversations</div>
                </div>
                
                <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <Clock className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-blue-600">{agent.avg_response_time.toFixed(1)}s</div>
                  <div className="text-xs text-muted-foreground">Avg Response Time</div>
                </div>

                <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                  <Settings className="h-6 w-6 text-green-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-green-600">{agent.platform}</div>
                  <div className="text-xs text-muted-foreground">Platform</div>
                </div>

                <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <Bot className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-purple-600">{agent.model.split('-')[0]}</div>
                  <div className="text-xs text-muted-foreground">AI Model</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-center sm:justify-end pt-4 border-t border-border">
          <Button variant="outline" onClick={onClose} className="w-full sm:w-auto">
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
