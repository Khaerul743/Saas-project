import { ApiResponse, BaseApiService } from './base'

export interface TestMessageRequest {
  agent_id: number
  message: string
  context?: any
}

export interface TestMessageResponse {
  response: string
  response_time: number
  token_usage: number
  model_used: string
}

export interface ShareLinkRequest {
  agent_id: number
  custom_message?: string
  allow_feedback?: boolean
  show_agent_info?: boolean
}

export interface ShareLinkResponse {
  share_url: string
  expires_at: string
  access_code?: string
}

export interface TestScenario {
  id: string
  name: string
  description: string
  messages: string[]
  expected_behavior: string
}

export class PlaygroundService extends BaseApiService {
  /**
   * Test an agent with a message
   */
  async testAgent(request: TestMessageRequest): Promise<ApiResponse<TestMessageResponse>> {
    return this.post<TestMessageResponse>('/playground/test', request)
  }

  /**
   * Invoke an agent directly (for playground chat)
   */
  async invokeAgent(agentId: number, message: string): Promise<ApiResponse<any>> {
    return this.post<any>(`/agents/invoke/${agentId}`, { message })
  }

  /**
   * Generate a shareable link for agent testing
   */
  async generateShareLink(request: ShareLinkRequest): Promise<ApiResponse<ShareLinkResponse>> {
    return this.post<ShareLinkResponse>('/playground/share', request)
  }

  /**
   * Get test scenarios for an agent
   */
  async getTestScenarios(agentId: number): Promise<ApiResponse<TestScenario[]>> {
    return this.get<TestScenario[]>(`/playground/scenarios/${agentId}`)
  }

  /**
   * Run batch test with multiple scenarios
   */
  async runBatchTest(agentId: number, scenarios: string[]): Promise<ApiResponse<any[]>> {
    return this.post<any[]>(`/playground/batch-test/${agentId}`, { scenarios })
  }

  /**
   * Get test history for an agent
   */
  async getTestHistory(agentId: number, limit: number = 50): Promise<ApiResponse<any[]>> {
    return this.get<any[]>(`/playground/history/${agentId}?limit=${limit}`)
  }

  /**
   * Save test conversation
   */
  async saveTestConversation(agentId: number, conversation: any): Promise<ApiResponse<any>> {
    return this.post<any>(`/playground/save-conversation/${agentId}`, conversation)
  }

  /**
   * Deploy agent to production
   */
  async deployAgent(agentId: number): Promise<ApiResponse<any>> {
    return this.post<any>(`/playground/deploy/${agentId}`)
  }

  /**
   * Get deployment status
   */
  async getDeploymentStatus(agentId: number): Promise<ApiResponse<any>> {
    return this.get<any>(`/playground/deployment-status/${agentId}`)
  }
}

export const playgroundService = new PlaygroundService()
