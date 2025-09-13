"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Chrome, AlertCircle } from "lucide-react"
import { initiateGoogleAuth, isGoogleAuthConfigured } from "@/lib/google-auth"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface GoogleAuthButtonProps {
  type: "login" | "register"
  onSuccess?: (user: any) => void
  onError?: (error: string) => void
  disabled?: boolean
}

export function GoogleAuthButton({ type, onSuccess, onError, disabled }: GoogleAuthButtonProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [showConfigWarning, setShowConfigWarning] = useState(false)

  const handleGoogleAuth = async () => {
    // Check if Google OAuth is configured
    if (!isGoogleAuthConfigured()) {
      setShowConfigWarning(true)
      setTimeout(() => setShowConfigWarning(false), 5000)
      return
    }

    setIsLoading(true)

    try {
      const result = await initiateGoogleAuth(type)

      if (result.success && result.user) {
        console.log(`[v0] Google ${type} successful, redirecting to dashboard...`)
        onSuccess?.(result.user)
        // Redirect to dashboard
        window.location.href = "/"
      } else {
        const errorMessage = result.error || `Google ${type} failed`
        console.error(`[v0] Google ${type} error:`, errorMessage)
        onError?.(errorMessage)
      }
    } catch (error) {
      const errorMessage = `Google ${type} failed. Please try again.`
      console.error(`[v0] Google ${type} error:`, error)
      onError?.(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-3">
      <Button
        variant="outline"
        className="w-full h-11 border-border/50 hover:bg-accent/50 bg-transparent"
        onClick={handleGoogleAuth}
        disabled={disabled || isLoading}
      >
        <Chrome className="w-4 h-4 mr-2" />
        {isLoading ? `Connecting to Google...` : `Continue with Google`}
      </Button>

      {showConfigWarning && (
        <Alert className="border-orange-500/50 bg-orange-500/10">
          <AlertCircle className="h-4 w-4 text-orange-500" />
          <AlertDescription className="text-orange-200">
            <strong>Demo Mode:</strong> Google OAuth is not configured. In production, add your Google Client ID to
            environment variables.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}
