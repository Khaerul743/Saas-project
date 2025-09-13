// Google OAuth configuration and utilities
export interface GoogleUser {
  id: string
  email: string
  name: string
  picture: string
  given_name: string
  family_name: string
}

export interface GoogleAuthResponse {
  success: boolean
  user?: GoogleUser
  error?: string
}

// Google OAuth configuration
export const GOOGLE_CONFIG = {
  clientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "demo-client-id",
  redirectUri:
    process.env.NEXT_PUBLIC_GOOGLE_REDIRECT_URI ||
    `${typeof window !== "undefined" ? window.location.origin : ""}/auth/callback/google`,
  scope: "openid email profile",
}

// Simulate Google OAuth flow for demo purposes
export const initiateGoogleAuth = async (type: "login" | "register"): Promise<GoogleAuthResponse> => {
  try {
    // In a real implementation, this would redirect to Google OAuth
    // For demo purposes, we'll simulate the OAuth flow

    console.log(`[v0] Initiating Google ${type} flow...`)

    // Simulate OAuth redirect and callback
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Simulate successful OAuth response
    const mockGoogleUser: GoogleUser = {
      id: "google_" + Math.random().toString(36).substr(2, 9),
      email: "user@example.com",
      name: "Demo User",
      picture: "https://via.placeholder.com/96x96/10b981/ffffff?text=DU",
      given_name: "Demo",
      family_name: "User",
    }

    console.log(`[v0] Google ${type} successful:`, mockGoogleUser)

    return {
      success: true,
      user: mockGoogleUser,
    }
  } catch (error) {
    console.error(`[v0] Google ${type} error:`, error)
    return {
      success: false,
      error: "Google authentication failed. Please try again.",
    }
  }
}

// Handle Google OAuth callback (in a real app, this would be a server-side route)
export const handleGoogleCallback = async (code: string): Promise<GoogleAuthResponse> => {
  try {
    // In a real implementation, this would exchange the code for tokens
    console.log("[v0] Processing Google OAuth callback with code:", code)

    // Simulate token exchange
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Return mock user data
    return await initiateGoogleAuth("login")
  } catch (error) {
    return {
      success: false,
      error: "Failed to process Google authentication callback.",
    }
  }
}

// Check if Google OAuth is properly configured
export const isGoogleAuthConfigured = (): boolean => {
  return !!(GOOGLE_CONFIG.clientId && GOOGLE_CONFIG.clientId !== "demo-client-id")
}
