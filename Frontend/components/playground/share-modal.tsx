"use client"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Agent as ApiAgent } from "@/lib/api"
import { Bot, Copy, ExternalLink, Share } from "lucide-react"
import React, { useState } from "react"

// Playground-specific Agent type with required id
interface Agent extends Omit<ApiAgent, 'id'> {
  id: number
}

interface ShareModalProps {
  isOpen: boolean
  onClose: () => void
  agent: Agent | null
}

export function ShareModal({ isOpen, onClose, agent }: ShareModalProps) {
  const [shareLink, setShareLink] = useState("")
  const [customMessage, setCustomMessage] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)

  // Generate share link when modal opens
  const generateShareLink = async () => {
    if (!agent) return

    setIsGenerating(true)
    try {
      // Simulate API call to generate share link
      await new Promise(resolve => setTimeout(resolve, 1000))
      const link = `${window.location.origin}/playground/test/${agent.id}`
      setShareLink(link)
    } catch (error) {
      console.error('Failed to generate share link:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareLink)
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy link:', error)
    }
  }

  const handleOpenLink = () => {
    window.open(shareLink, '_blank')
  }

  // Generate link when modal opens
  React.useEffect(() => {
    if (isOpen && agent && !shareLink) {
      generateShareLink()
    }
  }, [isOpen, agent])

  if (!agent) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share className="h-5 w-5" />
            Share Agent Test
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Agent Info */}
          <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h4 className="font-semibold">{agent.name}</h4>
              <p className="text-sm text-muted-foreground">{agent.description}</p>
            </div>
          </div>

          {/* Share Link */}
          <div className="space-y-2">
            <Label htmlFor="share-link">Share Link</Label>
            <div className="flex space-x-2">
              <Input
                id="share-link"
                value={shareLink}
                readOnly
                placeholder={isGenerating ? "Generating link..." : "Share link will appear here"}
                className="flex-1"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopyLink}
                disabled={!shareLink}
              >
                <Copy className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleOpenLink}
                disabled={!shareLink}
              >
                <ExternalLink className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Custom Message */}
          <div className="space-y-2">
            <Label htmlFor="custom-message">Custom Message (Optional)</Label>
            <Textarea
              id="custom-message"
              value={customMessage}
              onChange={(e) => setCustomMessage(e.target.value)}
              placeholder="Add a custom message for the recipient..."
              rows={3}
            />
          </div>

          {/* Share Options */}
          <div className="space-y-2">
            <Label>Share Options</Label>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="allow-feedback"
                  defaultChecked
                  className="rounded"
                />
                <Label htmlFor="allow-feedback" className="text-sm">
                  Allow feedback and suggestions
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="show-agent-info"
                  defaultChecked
                  className="rounded"
                />
                <Label htmlFor="show-agent-info" className="text-sm">
                  Show agent information
                </Label>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button onClick={handleCopyLink} disabled={!shareLink}>
              <Copy className="h-4 w-4 mr-2" />
              Copy & Share
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
