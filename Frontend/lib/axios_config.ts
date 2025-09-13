import axios, { AxiosInstance, AxiosResponse } from 'axios'

// Get base URL from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://c7b67e3ef858.ngrok-free.app/api'

// Debug logging
console.log('[Axios Config] API_BASE_URL:', API_BASE_URL)
console.log('[Axios Config] NEXT_PUBLIC_API_BASE_URL:', process.env.NEXT_PUBLIC_API_BASE_URL)

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased to 30 seconds for integration endpoints
  withCredentials: true, // Include cookies for authentication
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true', // Skip ngrok browser warning
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any request modifications here
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`)
    console.log(`[API Request] Full URL: ${config.baseURL}${config.url}`)
    console.log(`[API Request] Content-Type: ${config.headers?.['Content-Type']}`)
    
    // Log FormData contents if it's FormData
    if (config.data instanceof FormData) {
      console.log('[API Request] FormData detected')
      console.log('[API Request] FormData entries:')
      for (const [key, value] of config.data.entries()) {
        if (value instanceof File) {
          console.log(`[API Request] ${key}: File(${value.name}, ${value.size} bytes, ${value.type})`)
        } else {
          console.log(`[API Request] ${key}: ${value}`)
        }
      }
    }
    
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Add any response modifications here
    console.log(`[API Response] ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message)
    
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access - redirecting to login')
      // You can add redirect logic here if needed
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
export { API_BASE_URL }

