export interface Message {
  role: string
  type: "human" | "ai" | "tool_call" | "tool_message"
  content: string
  timestamp: string
  toolName?: string
}

export interface Conversation {
  id: string
  user: string
  agent: string
  platform: string
  date: string
  preview: string
  status: string
  tokenUsage: number
  responseTime: number
  confidenceScore: number
  messages: Message[]
}
