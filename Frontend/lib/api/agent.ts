import { ApiResponse, BaseApiService } from './base'

export interface Agent {
  id?: number
  avatar: string
  name: string
  model: string
  status: 'active' | 'non-active'
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

export interface CreateAgentRequest {
  name: string
  model: string
  avatar: string
  status: string
  role: string
  description: string
  tone: string
  base_prompt: string
  short_term_memory: boolean
  long_term_memory: boolean
}

export interface UpdateAgentRequest {
  name: string
  avatar: string
  model: string
  role?: string | null
  description: string
  tone: string
  status: string
}

export interface CreateIntegrationRequest {
  platform: string
  api_key?: string
}

export interface UpdateIntegrationRequest {
  platform: string
  api_key: string
}

export interface CustomerSupportAgent {
  id: number
  name: string
  avatar: string | null
  model: string
  description: string
  base_prompt: string
  tone: string
  short_term_memory: boolean
  long_term_memory: boolean
  status: string
  created_at: string
  company_information: {
    id: number
    agent_id: number
    name: string
    industry: string
    description: string
    address: string
    email: string
    website: string | null
    fallback_email: string
    created_at: string
  }
}

export class AgentService extends BaseApiService {
  async getAgents(): Promise<ApiResponse<Agent[]>> {
    return this.get<Agent[]>('/agents')
  }

  async createAgent(agentData: CreateAgentRequest, file?: File): Promise<ApiResponse<Agent>> {
    const formData = new FormData()
    
    // Add file if provided
    if (file) {
      console.log('Adding file to FormData:', file.name, file.size, file.type)
      console.log('File instanceof File:', file instanceof File)
      console.log('File constructor:', file.constructor.name)
      formData.append('file', file, file.name)
      
      // Verify file was added to FormData
      console.log('FormData has file after append:', formData.has('file'))
      console.log('FormData file value:', formData.get('file'))
    } else {
      console.log('No file provided')
    }
    
    // Add agent data as JSON string (backend expects this format)
    const agentDataString = JSON.stringify(agentData)
    console.log('Agent data JSON string:', agentDataString)
    formData.append('agent_data', agentDataString)
    
    // Debug: Log FormData contents
    console.log('FormData entries:')
    for (const [key, value] of formData.entries()) {
      if (key === 'agent_data') {
        console.log(key, 'JSON string:', value)
      } else {
        console.log(key, value)
      }
    }
    
    // Additional debug: Check if FormData has the expected fields
    console.log('FormData has agent_data?', formData.has('agent_data'))
    console.log('FormData has file?', formData.has('file'))
    console.log('FormData size:', formData.get('agent_data') ? 'has agent_data' : 'no agent_data')
    
    // Debug: Try to get file from FormData
    const fileFromFormData = formData.get('file')
    console.log('File from FormData:', fileFromFormData)
    console.log('File from FormData type:', typeof fileFromFormData)
    console.log('File from FormData instanceof File:', fileFromFormData instanceof File)
    
    // Debug: Check all FormData entries
    console.log('All FormData entries:')
    for (const [key, value] of formData.entries()) {
      console.log(`  ${key}:`, value, typeof value)
    }
    
    return this.postFormData<Agent>('/agents', formData)
  }

  async createIntegration(agentId: number, integrationData: CreateIntegrationRequest): Promise<ApiResponse> {
    return this.post(`/integrations/${agentId}`, integrationData)
  }

  async updateIntegration(agentId: number, integrationData: UpdateIntegrationRequest): Promise<ApiResponse> {
    return this.put(`/integrations/${agentId}`, integrationData)
  }

  // New method for customer support agent creation
  async createCustomerSupportAgent(
    agentData: any,
    datasets: Array<{ filename: string; description: string }>,
    files: File[]
  ): Promise<ApiResponse> {
    const formData = new FormData()
    
    // Add agent_data as JSON string
    formData.append('agent_data', JSON.stringify(agentData))
    
    // Add datasets as JSON string
    formData.append('datasets', JSON.stringify(datasets))
    
    // Add files
    files.forEach((file, index) => {
      formData.append('files', file)
    })
    
    return this.postFormData('/agents/customer-service', formData)
  }

  // New method for simple RAG agent creation
  async createSimpleRagAgent(agentData: any, file?: File): Promise<ApiResponse> {
    const formData = new FormData()
    
    // Add file if provided
    if (file) {
      formData.append('file', file, file.name)
    }
    
    // Add agent data as JSON string
    formData.append('agent_data', JSON.stringify(agentData))
    
    return this.postFormData('/agents/simple-rag', formData)
  }

  // Get customer support agent details
  async getCustomerSupportAgent(agentId: number): Promise<ApiResponse> {
    return this.get(`/agents/customer-service/${agentId}`)
  }

  // Update customer support agent
  async updateCustomerSupportAgent(agentId: number, agentData: any): Promise<ApiResponse> {
    return this.put(`/agents/customer-service/${agentId}`, agentData)
  }

  async updateAgent(agentId: number, agentData: UpdateAgentRequest): Promise<ApiResponse<Agent>> {
    return this.put<Agent>(`/agents/${agentId}`, agentData)
  }

  async deleteAgent(agentId: number): Promise<ApiResponse> {
    return this.delete(`/agents/${agentId}`)
  }
}

export const agentService = new AgentService()
