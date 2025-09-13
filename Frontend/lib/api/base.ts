import apiClient from '../axios_config'

export interface ApiResponse<T = any> {
  status: string
  message: string
  data: T
}

export class BaseApiService {
  protected client = apiClient

  protected async get<T>(url: string, config?: any): Promise<ApiResponse<T>> {
    const response = await this.client.get(url, config)
    return response.data
  }

  protected async post<T>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    const response = await this.client.post(url, data, config)
    return response.data
  }

  protected async put<T>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    const response = await this.client.put(url, data, config)
    return response.data
  }

  protected async delete<T>(url: string, config?: any): Promise<ApiResponse<T>> {
    const response = await this.client.delete(url, config)
    return response.data
  }

  protected async postFormData<T>(url: string, formData: FormData): Promise<ApiResponse<T>> {
    const response = await this.client.post(url, formData, {
      headers: {
        'Content-Type': undefined, // Let browser set the correct Content-Type with boundary
      },
    })
    return response.data
  }
}
