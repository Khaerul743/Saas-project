// Export all API services
export { AgentService, agentService } from './agent'
export { AuthService, authService } from './auth'
export { BaseApiService } from './base'
export type { ApiResponse } from './base'
export { DashboardService, dashboardService } from './dashboard'
export { HistoryService, historyService } from './history'

// Export types
export type {
    Agent,
    CreateAgentRequest,
    CreateIntegrationRequest,
    UpdateAgentRequest
} from './agent'
export type { LoginRequest, RegisterRequest, User } from './auth'
export type {
    AgentAnalytics,
    AgentAnalyticsResponse, ConversationAnalytics, DashboardOverview,
    TokenAnalytics
} from './dashboard'
export type { HistoryMessage, HistoryResponse, HistoryStats, MessageStats, MessagesResponse, UserAgent } from './history'

