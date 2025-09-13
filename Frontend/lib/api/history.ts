import { ApiResponse, BaseApiService } from './base'

export interface UserAgent {
  agent_name: string
  agent_id: number
  username: string
  user_agent_id: string
  platform: string
  created_at: string
}

export interface HistoryStats {
  token_usage: number
  total_conversations: number
  active_agents: number
  average_response_time: number
  success_rate: number
}

export interface HistoryResponse {
  user_agents: UserAgent[]
  stats: HistoryStats
}

export interface HistoryMessage {
  user_agent_id: string
  user_message: string
  response: string
  created_at: string
  metadata: {
    total_tokens: number
    response_time: number
    model: string
    is_success: boolean
  }
}

export interface MessageStats {
  token_usage: number
  response_time: number
  messages: number
}

export interface MessagesResponse {
  history_message: HistoryMessage[]
  stats: MessageStats
}

export class HistoryService extends BaseApiService {
  async getUserAgentHistory(): Promise<ApiResponse<HistoryResponse>> {
    return this.get<HistoryResponse>('/agents/users')
  }

  async getMessages(userAgentId: string): Promise<ApiResponse<MessagesResponse>> {
    return this.get<MessagesResponse>(`/history/messages/${userAgentId}`)
  }
}

export const historyService = new HistoryService()
