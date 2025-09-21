"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Bot, RotateCcw, Send, User } from "lucide-react"
import { useState } from "react"

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

interface ChatInterfaceProps {
  messages: ChatMessage[]
  onSendMessage: (message: string) => void
  onResetChat: () => void
  isLoading: boolean
  agentName: string
}

export function ChatInterface({ 
  messages, 
  onSendMessage, 
  onResetChat, 
  isLoading, 
  agentName 
}: ChatInterfaceProps) {
  const [inputMessage, setInputMessage] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputMessage.trim() && !isLoading) {
      onSendMessage(inputMessage)
      setInputMessage("")
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-3">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-primary/10 text-primary text-sm font-semibold">
              <Bot className="h-4 w-4" />
            </AvatarFallback>
          </Avatar>
          <div>
            <h3 className="font-semibold text-sm">{agentName}</h3>
            <p className="text-xs text-muted-foreground">AI Assistant</p>
          </div>
        </div>
        
        <Button 
          variant="outline" 
          size="sm" 
          onClick={onResetChat}
          disabled={isLoading}
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset
        </Button>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
                message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <Avatar className="h-8 w-8 flex-shrink-0">
                <AvatarFallback className={
                  message.role === 'user' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'bg-primary/10 text-primary'
                }>
                  {message.role === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </AvatarFallback>
              </Avatar>
              
              <div className={`max-w-[80%] ${message.role === 'user' ? 'text-right' : ''}`}>
                <div
                  className={`inline-block p-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatTime(message.timestamp)}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex items-start space-x-3">
              <Avatar className="h-8 w-8 flex-shrink-0">
                <AvatarFallback className="bg-primary/10 text-primary">
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <div className="bg-muted p-3 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <Input
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button 
            type="submit" 
            disabled={!inputMessage.trim() || isLoading}
            size="sm"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}
