"use client"

import { authService } from "@/lib/api"
import type React from "react"
import { createContext, useContext, useEffect, useState } from "react"

interface User {
  id?: number
  name: string
  email: string
  avatar?: string
  plan: "free" | "pro" | "enterprise"
  job_role?: string
  company_name?: string
  created_at?: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  refreshAuth: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check for existing session on mount via backend (cookie is HttpOnly)
  const checkAuth = async () => {
    try {
      setIsLoading(true)
      console.log("[Auth] Checking authentication...")
      const response = await authService.getCurrentUser()
      console.log("[Auth] API Response:", response)
      
      if (response.status === 'success' && response.data) {
        // Map backend response to frontend User interface
        const userData = {
          id: response.data.id,
          name: response.data.username || response.data.name, // Backend returns 'username'
          email: response.data.email,
          plan: response.data.plan,
          avatar: response.data.avatar,
          job_role: response.data.job_role,
          company_name: response.data.company_name,
          created_at: response.data.created_at,
        }
        setUser(userData)
        console.log("[Auth] User loaded from backend:", userData)
      } else {
        setUser(null)
        console.log("[Auth] No valid session found, response:", response)
      }
    } catch (error) {
      console.warn("[Auth] Not authenticated or failed to load user", error)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  const refreshAuth = async () => {
    console.log("[Auth] Refreshing auth state...")
    await checkAuth()
  }

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      // Call real login API
      const response = await authService.login({ email, password })
      
      if (response.status === 'success' && response.data) {
        setUser(response.data)
        console.log("[Auth] User logged in:", response.data)
      } else {
        throw new Error(response.message || 'Login failed')
      }
    } catch (error) {
      console.error("[Auth] Login error:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error("[Auth] Error during logout:", error)
    } finally {
      setUser(null)
      console.log("[Auth] User logged out")
      // Redirect to login page
      window.location.href = "/auth/login"
    }
  }

  const value = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
    refreshAuth,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
