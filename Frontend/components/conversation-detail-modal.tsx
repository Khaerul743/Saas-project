"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { historyService, type HistoryMessage, type MessageStats } from "@/lib/api"
import { type Conversation } from "@/lib/types/conversation"
import {
    Activity,
    BarChart3,
    Bot,
    CheckCircle,
    Loader2,
    MessageCircle,
    Settings,
    Timer,
    User,
    Wrench,
    Zap
} from "lucide-react"
import { useEffect, useState } from "react"

interface ConversationDetailModalProps {
  conversation: Conversation | null
  isOpen: boolean
  onClose: () => void
}

const getMessageTypeIcon = (type: string) => {
  switch (type) {
    case "human":
      return { icon: User, bgColor: "bg-blue-500/10", iconColor: "text-blue-500" }
    case "ai":
      return { icon: Bot, bgColor: "bg-emerald-500/10", iconColor: "text-emerald-500" }
    case "tool_call":
      return { icon: Settings, bgColor: "bg-orange-500/10", iconColor: "text-orange-500" }
    case "tool_message":
      return { icon: Wrench, bgColor: "bg-purple-500/10", iconColor: "text-purple-500" }
    default:
      return { icon: MessageCircle, bgColor: "bg-gray-500/10", iconColor: "text-gray-500" }
  }
}

export function ConversationDetailModal({ conversation, isOpen, onClose }: ConversationDetailModalProps) {
  const [messages, setMessages] = useState<HistoryMessage[]>([])
  const [messageStats, setMessageStats] = useState<MessageStats | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>("")

  // Fetch messages when modal opens and conversation changes
  useEffect(() => {
    if (!isOpen || !conversation) {
      setMessages([])
      setMessageStats(null)
      setError("")
      return
    }

    let mounted = true
    const loadMessages = async () => {
      try {
        setIsLoading(true)
        setError("")
        const response = await historyService.getMessages(conversation.id)
        if (!mounted) return
        
        setMessages(response.data.history_message || [])
        setMessageStats(response.data.stats || null)
      } catch (e: any) {
        if (!mounted) return
        setError(e?.message || "Failed to load conversation messages")
      } finally {
        if (mounted) setIsLoading(false)
      }
    }

    loadMessages()
    return () => {
      mounted = false
    }
  }, [isOpen, conversation?.id])

  if (!conversation) return null

  const successRate = messages.length > 0 
    ? ((messages.filter(m => m.metadata.is_success).length / messages.length) * 100)
    : conversation.confidenceScore

  const avgResponseTime = messageStats?.response_time || conversation.responseTime
  const tokenUsage = messageStats?.token_usage || conversation.tokenUsage
  const totalMessages = messageStats?.messages || messages.length

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="w-[98vw] max-w-xs sm:max-w-lg md:max-w-2xl lg:max-w-4xl xl:max-w-5xl 2xl:max-w-6xl h-[98vh] flex flex-col p-0">
        <div className="flex flex-col xl:flex-row flex-1 min-h-0">
          {/* Messages Section */}
          <div className="flex-1 xl:flex-[2] flex flex-col min-h-0">
            <div className="p-3 sm:p-4 border-b bg-muted/30 flex-shrink-0">
              <div className="flex flex-col space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-2 sm:space-y-0">
                  <h3 className="font-semibold flex items-center text-sm sm:text-base">
                    <MessageCircle className="h-4 w-4 mr-2 flex-shrink-0" />
                    <span className="truncate">Conversation with {conversation.user}</span>
                  </h3>
                  <Badge variant="outline" className="text-xs self-start sm:self-center">
                    {totalMessages} messages
                  </Badge>
                </div>
                <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                  <Badge variant="outline" className="text-xs flex items-center">
                    <Bot className="h-3 w-3 mr-1 flex-shrink-0" />
                    <span className="truncate max-w-20 sm:max-w-none">{conversation.agent}</span>
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    {conversation.platform}
                  </Badge>
                  <span className="text-xs sm:text-sm text-muted-foreground whitespace-nowrap">
                    {new Date(conversation.date).toLocaleDateString()}
                  </span>
                  <Badge 
                    variant={conversation.status === 'completed' ? 'default' : 'secondary'}
                    className="text-xs"
                  >
                    {conversation.status}
                  </Badge>
                </div>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-3 sm:p-4">
                {isLoading ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="flex flex-col items-center space-y-3">
                      <Loader2 className="h-8 w-8 animate-spin text-primary" />
                      <span className="text-sm text-muted-foreground">Loading conversation...</span>
                    </div>
                  </div>
                ) : error ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="text-center space-y-3">
                      <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center mx-auto">
                        <MessageCircle className="h-6 w-6 text-red-500" />
                      </div>
                      <p className="text-red-500 text-sm">{error}</p>
                      <button 
                        onClick={() => window.location.reload()} 
                        className="text-xs text-primary hover:underline"
                      >
                        Retry
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4 sm:space-y-6">
                    {messages.length === 0 ? (
                      <div className="text-center text-muted-foreground py-8 sm:py-12">
                        <div className="h-12 w-12 sm:h-16 sm:w-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-3 sm:mb-4">
                          <MessageCircle className="h-6 w-6 sm:h-8 sm:w-8 opacity-50" />
                        </div>
                        <p className="text-xs sm:text-sm">No messages found in this conversation</p>
                      </div>
                    ) : (
                      messages.map((message, index) => (
                        <div key={index} className="space-y-3 sm:space-y-4">
                          {/* User Message */}
                          <div className="flex items-start space-x-2 sm:space-x-3 flex-row-reverse space-x-reverse">
                            <Avatar className="h-8 w-8 sm:h-9 sm:w-9 md:h-10 md:w-10 flex-shrink-0 bg-blue-500/10 border-2 border-blue-200/50">
                              <AvatarFallback className="bg-blue-500/10 text-blue-600 font-semibold">
                                <User className="h-4 w-4 sm:h-5 sm:w-5" />
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1 text-right max-w-[85%] sm:max-w-[80%] min-w-0">
                              <div className="inline-block p-3 sm:p-4 rounded-2xl rounded-tr-md bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg">
                                <p className="text-xs sm:text-sm whitespace-pre-wrap leading-relaxed break-words">{message.user_message}</p>
                              </div>
                              <div className="text-xs text-muted-foreground mt-1 sm:mt-2 flex flex-col sm:flex-row sm:items-center justify-end space-y-1 sm:space-y-0 sm:space-x-2">
                                <span className="whitespace-nowrap">{new Date(message.created_at).toLocaleTimeString()}</span>
                                <Badge variant="outline" className="text-xs px-2 py-0 self-end sm:self-center">
                                  User
                                </Badge>
                              </div>
                            </div>
                          </div>

                          {/* AI Response */}
                          <div className="flex items-start space-x-2 sm:space-x-3">
                            <Avatar className="h-8 w-8 sm:h-9 sm:w-9 md:h-10 md:w-10 flex-shrink-0 bg-emerald-500/10 border-2 border-emerald-200/50">
                              <AvatarFallback className="bg-emerald-500/10 text-emerald-600 font-semibold">
                                <Bot className="h-4 w-4 sm:h-5 sm:w-5" />
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1 max-w-[85%] sm:max-w-[80%] min-w-0">
                              <div className="inline-block p-3 sm:p-4 rounded-2xl rounded-tl-md bg-gradient-to-r from-emerald-50 to-emerald-100 border border-emerald-200/50 shadow-sm">
                                <p className="text-xs sm:text-sm whitespace-pre-wrap leading-relaxed text-gray-800 break-words">{message.response}</p>
                              </div>
                              <div className="text-xs text-muted-foreground mt-1 sm:mt-2 flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-2">
                                <span className="whitespace-nowrap">{new Date(message.created_at).toLocaleTimeString()}</span>
                                <div className="flex flex-wrap gap-1 sm:gap-2">
                                  {message.metadata.model && (
                                    <Badge variant="secondary" className="text-xs px-2 py-0">
                                      {message.metadata.model}
                                    </Badge>
                                  )}
                                  <Badge 
                                    variant={message.metadata.is_success ? "default" : "destructive"}
                                    className="text-xs px-2 py-0"
                                  >
                                    {message.metadata.is_success ? "Success" : "Failed"}
                                  </Badge>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
            </div>
          </div>

          {/* Metrics Sidebar */}
          <div className="xl:flex-1 xl:max-w-sm border-t xl:border-t-0 xl:border-l bg-muted/20 flex flex-col min-h-0">
            <div className="p-3 sm:p-4 space-y-3 sm:space-y-4 flex-1 overflow-y-auto">
              {/* Performance Overview */}
              <Card className="border-l-4 border-l-primary">
                <CardHeader className="pb-2 sm:pb-3">
                  <CardTitle className="text-sm sm:text-base flex items-center">
                    <BarChart3 className="h-4 w-4 mr-2 text-primary flex-shrink-0" />
                    <span className="truncate">Performance Overview</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 sm:space-y-4">
                  {/* Success Rate */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 min-w-0">
                        <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <span className="text-xs sm:text-sm font-medium truncate">Success Rate</span>
                      </div>
                      <span className="text-xs sm:text-sm font-bold text-green-600 flex-shrink-0">
                        {successRate.toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={successRate} className="h-2" />
                  </div>

                  {/* Response Time */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 min-w-0">
                        <Timer className="h-4 w-4 text-blue-600 flex-shrink-0" />
                        <span className="text-xs sm:text-sm font-medium truncate">Avg Response</span>
                      </div>
                      <span className="text-xs sm:text-sm font-bold text-blue-600 flex-shrink-0">
                        {avgResponseTime.toFixed(1)}s
                      </span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(100, (avgResponseTime / 5) * 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Token Usage */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 min-w-0">
                        <Zap className="h-4 w-4 text-orange-600 flex-shrink-0" />
                        <span className="text-xs sm:text-sm font-medium truncate">Token Usage</span>
                      </div>
                      <span className="text-xs sm:text-sm font-bold text-orange-600 flex-shrink-0">
                        {tokenUsage.toLocaleString()}
                      </span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-orange-500 to-orange-600 rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(100, (tokenUsage / 10000) * 100)}%` }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Conversation Stats */}
              <Card className="border-l-4 border-l-emerald-500">
                <CardHeader className="pb-2 sm:pb-3">
                  <CardTitle className="text-sm sm:text-base flex items-center">
                    <Activity className="h-4 w-4 mr-2 text-emerald-600 flex-shrink-0" />
                    <span className="truncate">Conversation Stats</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 sm:space-y-3">
                  <div className="flex items-center justify-between p-2 sm:p-3 bg-emerald-50 rounded-lg">
                    <div className="flex items-center space-x-2 min-w-0">
                      <MessageCircle className="h-4 w-4 text-emerald-600 flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium truncate">Total Messages</span>
                    </div>
                    <span className="text-base sm:text-lg font-bold text-emerald-600 flex-shrink-0">
                      {totalMessages}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 sm:p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-2 min-w-0">
                      <User className="h-4 w-4 text-blue-600 flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium truncate">User Messages</span>
                    </div>
                    <span className="text-base sm:text-lg font-bold text-blue-600 flex-shrink-0">
                      {Math.ceil(totalMessages / 2)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 sm:p-3 bg-purple-50 rounded-lg">
                    <div className="flex items-center space-x-2 min-w-0">
                      <Bot className="h-4 w-4 text-purple-600 flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium truncate">AI Responses</span>
                    </div>
                    <span className="text-base sm:text-lg font-bold text-purple-600 flex-shrink-0">
                      {Math.floor(totalMessages / 2)}
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Model Information */}
              {messages.length > 0 && messages[0].metadata.model && (
                <Card className="border-l-4 border-l-purple-500">
                  <CardHeader className="pb-2 sm:pb-3">
                    <CardTitle className="text-sm sm:text-base flex items-center">
                      <Settings className="h-4 w-4 mr-2 text-purple-600 flex-shrink-0" />
                      <span className="truncate">Model Info</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs sm:text-sm text-muted-foreground truncate">Model</span>
                        <Badge variant="outline" className="text-xs flex-shrink-0">
                          {messages[0].metadata.model}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs sm:text-sm text-muted-foreground truncate">Platform</span>
                        <Badge variant="secondary" className="text-xs flex-shrink-0">
                          {conversation.platform}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
