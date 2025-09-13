import { ApiResponse, BaseApiService } from './base'

export interface DashboardOverview {
  token_usage: number
  total_conversations: number
  active_agents: number
  avg_response_time: number
  success_rate: number
}

export interface TokenAnalytics {
  period: string
  total_tokens: number
}

export interface ConversationAnalytics {
  period: string
  total_conversations: number
}

export interface AgentAnalytics {
  agent_id: number
  agent_name: string
  total_tokens: number
}

export interface AgentAnalyticsResponse {
  agents: AgentAnalytics[]
}

export class DashboardService extends BaseApiService {
  async getOverview(): Promise<ApiResponse<DashboardOverview>> {
    return this.get<DashboardOverview>('/dashboard/overview')
  }

  async getTokenAnalytics(params: {
    start_date: string
    end_date: string
    group_by?: string
  }): Promise<ApiResponse<TokenAnalytics[]>> {
    const queryParams = new URLSearchParams({
      start_date: params.start_date,
      end_date: params.end_date,
      ...(params.group_by && { group_by: params.group_by }),
    })
    
    return this.get<TokenAnalytics[]>(`/dashboard/analytics/tokens?${queryParams}`)
  }

  async getConversationAnalytics(params: {
    start_date: string
    end_date: string
    group_by?: string
  }): Promise<ApiResponse<ConversationAnalytics[]>> {
    const queryParams = new URLSearchParams({
      start_date: params.start_date,
      end_date: params.end_date,
      ...(params.group_by && { group_by: params.group_by }),
    })
    
    return this.get<ConversationAnalytics[]>(`/dashboard/analytics/conversations?${queryParams}`)
  }

  async getAgentAnalytics(): Promise<ApiResponse<AgentAnalyticsResponse>> {
    return this.get<AgentAnalyticsResponse>('/dashboard/analytics/agents')
  }
}

export const dashboardService = new DashboardService()
