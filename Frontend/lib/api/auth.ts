import { ApiResponse, BaseApiService } from './base'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface User {
  id?: number
  name: string
  email: string
  plan: string
  avatar?: string
  job_role?: string
  company_name?: string
  created_at?: string
}

export class AuthService extends BaseApiService {
  async login(credentials: LoginRequest): Promise<ApiResponse<User>> {
    return this.post<User>('/login', credentials)
  }

  async register(userData: RegisterRequest): Promise<ApiResponse<User>> {
    return this.post<User>('/register', userData)
  }

  async logout(): Promise<ApiResponse> {
    return this.post('/logout')
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.get<User>('/users/profile')
  }
}

export const authService = new AuthService()
