"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { agentService, CreateAgentRequest, CreateIntegrationRequest } from "@/lib/api"; // Fixed import
import {
    Brain,
    ChevronLeft,
    ChevronRight,
    Cpu,
    Globe,
    MessageCircle,
    Phone,
    Settings,
    Upload
} from "lucide-react"
import { useEffect, useRef, useState } from "react"

interface Agent {
  id?: number
  avatar: string
  name: string
  model: string
  status: "active" | "non-active"
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

interface AgentSettingsModalProps {
  agent: Agent | null
  isOpen: boolean
  onClose: () => void
}

export function AgentSettingsModal({ agent, isOpen, onClose }: AgentSettingsModalProps) {
  const [activeTab, setActiveTab] = useState("profile")
  const [currentStep, setCurrentStep] = useState(0)
  const [testMessage, setTestMessage] = useState("")
  const [chatMessages, setChatMessages] = useState([
    { role: "assistant", content: "Hello! I'm ready to help. What can I do for you today?" },
  ])
  const [selectedPlatform, setSelectedPlatform] = useState<string>("")
  const [selectedProvider, setSelectedProvider] = useState<string>("")
  const [selectedModel, setSelectedModel] = useState<string>("")
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    status: "active",
    role: "simple RAG agent",
    tone: "formal",
    shortTermMemory: false,
    longTermMemory: false,
    platform: "telegram",
    apiKey: "",
    provider: "",
    model: "",
    maxTokens: "150",
    basePrompt: "You are a helpful AI assistant. Always be polite, professional, and provide accurate information."
  })

  // Initialize form data when agent changes (for edit mode)
  useEffect(() => {
    if (agent) {
      setFormData({
        name: agent.name || "",
        description: agent.description || "",
        status: agent.status || "active",
        role: "simple RAG agent", // Default value since not in Agent interface
        tone: agent.tone || "formal",
        shortTermMemory: agent.short_term_memory || false,
        longTermMemory: agent.long_term_memory || false,
        platform: agent.platform || "telegram",
        apiKey: agent.api_key || "",
        provider: "", // Not stored in Agent interface
        model: agent.model || "",
        maxTokens: "150", // Default value
        basePrompt: agent.base_prompt || "You are a helpful AI assistant. Always be polite, professional, and provide accurate information.",
      })
    } else {
      // Reset to default values for create mode
      setFormData({
        name: "",
        description: "",
        status: "active",
        role: "simple RAG agent",
        tone: "formal",
        shortTermMemory: false,
        longTermMemory: false,
        platform: "telegram",
        apiKey: "",
        provider: "",
        model: "",
        maxTokens: "150",
        basePrompt: "You are a helpful AI assistant. Always be polite, professional, and provide accurate information."
      })
    }
  }, [agent])
  
  const avatarInputRef = useRef<HTMLInputElement>(null)
  const documentInputRef = useRef<HTMLInputElement>(null)

  const steps = [
    { id: "profile", title: "Profile", icon: Upload },
    { id: "model", title: "Model", icon: Cpu },
    { id: "memory", title: "Memory", icon: Brain },
    { id: "platforms", title: "Platform", icon: Settings },
    { id: "behavior", title: "Behavior", icon: Settings },
  ]

  const modelOptions = {
    openai: [
      { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
      { value: "gpt-4o", label: "GPT-4o" },
    ],
  }

  const handleSendTest = () => {
    if (!testMessage.trim()) return

    setChatMessages([
      ...chatMessages,
      { role: "user", content: testMessage },
      {
        role: "assistant",
        content:
          "This is a test response from the agent. In a real implementation, this would connect to your AI model.",
      },
    ])
    setTestMessage("")
  }

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleFinish = () => {
    // Handle agent creation logic here
    onClose()
  }

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider)
    setSelectedModel("")
  }

  const handleAvatarUpload = () => {
    avatarInputRef.current?.click()
  }

  const handleAvatarFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setAvatarFile(file)
      console.log("Avatar uploaded:", file.name)
    }
  }

  const handleDocumentUpload = () => {
    documentInputRef.current?.click()
  }

  const handleDocumentFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    setUploadedFiles(prev => [...prev, ...files])
  }

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault()
    setIsDragOver(false)
    const files = Array.from(event.dataTransfer.files)
    setUploadedFiles(prev => [...prev, ...files])
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }


  const handleFormSubmit = async () => {
    if (!formData.name.trim()) {
      alert('Please enter agent name')
      return
    }

    setIsSubmitting(true)
    
    try {
      if (agent) {
        // Update existing agent
        const updateData = {
          name: formData.name,
          avatar: agent.avatar || "",
          model: formData.model,
          role: formData.role,
          description: formData.description,
          tone: formData.tone,
          status: formData.status
        }
        
        console.log('Updating agent with data:', updateData)
        const updateResponse = await agentService.updateAgent(agent.id!, updateData)
        console.log('Agent updated:', updateResponse)
        
        alert('Agent updated successfully!')
        onClose()
        
      } else {
        // Create new agent
        if (!formData.provider || !formData.model) {
          alert('Please select AI provider and model')
          return
        }
        
        if (!formData.apiKey.trim()) {
          alert('Please enter Telegram API key')
          return
        }

        // Prepare agent data
        const agentData: CreateAgentRequest = {
          name: formData.name,
          model: formData.model,
          avatar: avatarFile ? avatarFile.name : "",
          status: formData.status,
          role: formData.role,
          description: formData.description,
          tone: formData.tone,
          base_prompt: formData.basePrompt,
          short_term_memory: formData.shortTermMemory,
          long_term_memory: formData.longTermMemory
        }
        
        // Step 1: Create agent
        console.log('Uploaded files before sending:', uploadedFiles)
        console.log('Uploaded files count:', uploadedFiles.length)
        console.log('Uploaded files details:', uploadedFiles.map(f => ({ name: f.name, size: f.size, type: f.type })))
        
        // Send the first uploaded file as the main file (or null if no files)
        const mainFile = uploadedFiles.length > 0 ? uploadedFiles[0] : null
        console.log('Main file to send:', mainFile)
        
        const agentResponse = await agentService.createAgent(agentData, mainFile || undefined)
        console.log('Agent created:', agentResponse)
        
        // Step 2: Create integration
        const integrationData: CreateIntegrationRequest = {
          platform: formData.platform,
          api_key: formData.apiKey
        }
        const integrationResponse = await agentService.createIntegration(
          agentResponse.data.id!,
          integrationData
        )
        console.log('Integration created:', integrationResponse)
        
        // Success - close modal and refresh
        alert('Agent created successfully!')
        onClose()
      }
      
    } catch (error: any) {
      console.error('Error with agent operation:', error)
      
      // Handle different types of errors
      if (error.code === 'ECONNABORTED') {
        alert('Request timed out. Please try again.')
      } else if (error.response?.status === 400) {
        alert(`Operation failed: ${error.response.data?.message || 'Invalid data or configuration'}`)
      } else if (error.response?.status === 401) {
        alert('Authentication failed. Please log in again.')
      } else if (error.response?.status === 404) {
        alert('Agent not found. It may have been deleted.')
      } else {
        alert(`Failed to ${agent ? 'update' : 'create'} agent. Please try again.`)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStepContent = () => {
    const stepId = steps[currentStep].id

    switch (stepId) {
      case "profile":
        return (
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <Avatar className="h-16 w-16">
                <AvatarFallback className="bg-primary/10 text-primary text-lg font-semibold">
                  {agent?.avatar || "NA"}
                </AvatarFallback>
              </Avatar>
              <div>
                <Button variant="outline" size="sm" onClick={handleAvatarUpload}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Avatar
              </Button>
                <input
                  ref={avatarInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarFileChange}
                  className="hidden"
                />
                <p className="text-xs text-muted-foreground mt-1">JPG, PNG, GIF up to 2MB</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Agent Name</Label>
                <Input 
                  id="name" 
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter agent name" 
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select 
                  value={formData.status}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, status: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="non-active">Non-Active</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Agent Role</Label>
              <Select 
                value={formData.role}
                onValueChange={(value) => setFormData(prev => ({ ...prev, role: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select agent role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="simple RAG agent">Simple RAG agent</SelectItem>
                  <SelectItem value="customer service">Customer Service</SelectItem>
                  <SelectItem value="data analyst">Data Analyst</SelectItem>
                  <SelectItem value="finance assistant">Finance Assistant</SelectItem>
                  <SelectItem value="sales">Sales</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe what this agent does"
                rows={3}
              />
            </div>
          </div>
        )

      case "model":
        return (
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Cpu className="h-4 w-4" />
                Model Selection
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="provider">AI Provider</Label>
                <Select 
                  value={formData.provider} 
                  onValueChange={(value) => {
                    setFormData(prev => ({ ...prev, provider: value, model: "" }))
                    setSelectedProvider(value)
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose an AI provider" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="openai">OpenAI</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {formData.provider && (
                <div className="space-y-2">
                  <Label htmlFor="model">Model</Label>
                  <Select 
                    value={formData.model} 
                    onValueChange={(value) => {
                      setFormData(prev => ({ ...prev, model: value }))
                      setSelectedModel(value)
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a model" />
                    </SelectTrigger>
                    <SelectContent>
                      {modelOptions[formData.provider as keyof typeof modelOptions]?.map((model) => (
                        <SelectItem key={model.value} value={model.value}>
                          {model.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {formData.provider && formData.model && (
                <div className="p-3 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    Selected:{" "}
                    <span className="font-medium text-foreground">
                      {formData.provider.charAt(0).toUpperCase() + formData.provider.slice(1)} -{" "}
                      {
                        modelOptions[formData.provider as keyof typeof modelOptions]?.find(
                          (m) => m.value === formData.model,
                        )?.label
                      }
                    </span>
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )


      case "memory":
        return (
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Brain className="h-4 w-4" />
                Memory Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Short-term Memory</Label>
                  <p className="text-sm text-muted-foreground">Remember context within conversations</p>
                </div>
                <Switch 
                  checked={formData.shortTermMemory}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, shortTermMemory: checked }))}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Long-term Memory</Label>
                  <p className="text-sm text-muted-foreground">Remember user preferences across sessions</p>
                </div>
                <Switch 
                  checked={formData.longTermMemory}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, longTermMemory: checked }))}
                />
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Memory Retention (days)</Label>
                <Select defaultValue="30">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7">7 days</SelectItem>
                    <SelectItem value="30">30 days</SelectItem>
                    <SelectItem value="90">90 days</SelectItem>
                    <SelectItem value="365">1 year</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        )

      case "platforms":
        return (
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Platform Integration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="platform">Select Platform</Label>
                <Select 
                  value={formData.platform} 
                  onValueChange={(value) => {
                    setFormData(prev => ({ ...prev, platform: value }))
                    setSelectedPlatform(value)
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a platform" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="telegram">
                      <div className="flex items-center gap-2">
                        <MessageCircle className="h-4 w-4" />
                        Telegram
                      </div>
                    </SelectItem>
                    <SelectItem value="whatsapp">
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4" />
                        WhatsApp
                      </div>
                    </SelectItem>
                    <SelectItem value="website">
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        Website
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {formData.platform === "telegram" && (
                <div className="space-y-2">
                  <Label htmlFor="telegram-api-key">Telegram Bot API Key</Label>
                  <Input 
                    id="telegram-api-key" 
                    type="password" 
                    value={formData.apiKey}
                    onChange={(e) => setFormData(prev => ({ ...prev, apiKey: e.target.value }))}
                    placeholder="Enter your Telegram bot token" 
                  />
                  <p className="text-xs text-muted-foreground">Get your bot token from @BotFather on Telegram</p>
                </div>
              )}
            </CardContent>
          </Card>
        )

      case "behavior":
        return (
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Behavior Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Tone</Label>
                <Select 
                  value={formData.tone}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, tone: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="formal">Formal</SelectItem>
                    <SelectItem value="friendly">Friendly</SelectItem>
                    <SelectItem value="casual">Casual</SelectItem>
                    <SelectItem value="profesional">Professional</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Max Tokens</Label>
                <Input 
                  type="number" 
                  value={formData.maxTokens}
                  onChange={(e) => setFormData(prev => ({ ...prev, maxTokens: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label>Base Prompt</Label>
                <Textarea
                  value={formData.basePrompt}
                  onChange={(e) => setFormData(prev => ({ ...prev, basePrompt: e.target.value }))}
                  placeholder="Enter the base prompt that defines your agent's behavior and personality"
                  rows={4}
                />
                <p className="text-xs text-muted-foreground">
                  This prompt will be used as the foundation for all agent interactions
                </p>
              </div>
            </CardContent>
          </Card>
        )

      default:
        return null
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="font-heading">{agent ? `Edit ${agent.name}` : "Create New Agent"}</DialogTitle>
        </DialogHeader>

        {!agent ? (
          <>
            {/* Progress indicator */}
            <div className="mb-6">
              <div className="flex items-center justify-between">
                {steps.map((step, index) => (
                  <div key={step.id} className="flex flex-col items-center flex-1">
                    <div
                      className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                        index <= currentStep
                          ? "bg-primary border-primary text-primary-foreground"
                          : "border-muted-foreground text-muted-foreground"
                      }`}
                    >
                      {index + 1}
                    </div>
                    <span
                      className={`mt-1 text-xs text-center ${
                        index <= currentStep ? "text-foreground" : "text-muted-foreground"
                      }`}
                    >
                      <span className="hidden sm:inline">{step.title}</span>
                      <span className="sm:hidden">
                        {step.title === "Knowledge"
                          ? "Know"
                          : step.title === "Platform"
                            ? "Plat"
                            : step.title === "Behavior"
                              ? "Behav"
                              : step.title}
                      </span>
                    </span>
                    {index < steps.length - 1 && (
                      <div
                        className={`absolute top-4 left-1/2 w-full h-0.5 ${index < currentStep ? "bg-primary" : "bg-muted-foreground"} -z-10`}
                        style={{ transform: `translateX(${100 / steps.length}%)`, width: `${100 / steps.length}%` }}
                      />
                    )}
                  </div>
                ))}
              </div>
              {/* Progress bar background */}
              <div className="relative mt-4">
                <div className="absolute top-0 left-0 w-full h-0.5 bg-muted-foreground -z-20"></div>
                <div
                  className="absolute top-0 left-0 h-0.5 bg-primary transition-all duration-300 -z-10"
                  style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto min-h-0 mb-4">{renderStepContent()}</div>

            <div className="flex justify-between pt-4 border-t border-border flex-shrink-0">
              <Button variant="outline" onClick={currentStep === 0 ? onClose : handleBack} disabled={currentStep === 0}>
                {currentStep === 0 ? (
                  "Cancel"
                ) : (
                  <>
                    <ChevronLeft className="h-4 w-4 mr-2" />
                    Back
                  </>
                )}
              </Button>
              <Button 
                onClick={currentStep === steps.length - 1 ? handleFormSubmit : handleNext}
                disabled={isSubmitting}
              >
                {currentStep === steps.length - 1 ? (
                  isSubmitting ? "Creating..." : "Create Agent"
                ) : (
                  <>
                    Next
                    <ChevronRight className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          </>
        ) : (
          // Existing tab interface for editing agents
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col flex-1 min-h-0">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="profile">Profile</TabsTrigger>
              <TabsTrigger value="model">Model</TabsTrigger>
              <TabsTrigger value="memory">Memory</TabsTrigger>
              <TabsTrigger value="platforms">Platforms</TabsTrigger>
              <TabsTrigger value="behavior">Behavior</TabsTrigger>
            </TabsList>

            <div className="flex-1 overflow-y-auto mt-4 min-h-0">
              <TabsContent value="profile" className="space-y-4">
                <div className="flex items-center space-x-4">
                  <Avatar className="h-16 w-16">
                    <AvatarFallback className="bg-primary/10 text-primary text-lg font-semibold">
                      {agent?.avatar || "NA"}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <Button variant="outline" size="sm" onClick={handleAvatarUpload}>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Avatar
                  </Button>
                    <input
                      ref={avatarInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarFileChange}
                      className="hidden"
                    />
                    <p className="text-xs text-muted-foreground mt-1">JPG, PNG, GIF up to 2MB</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Agent Name</Label>
                    <Input 
                      id="name" 
                      value={formData.name}
                      onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter agent name" 
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select 
                      value={formData.status}
                      onValueChange={(value) => setFormData(prev => ({ ...prev, status: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="non-active">Non-Active</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>


                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe what this agent does"
                    rows={3}
                  />
                </div>
              </TabsContent>

              <TabsContent value="model" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Cpu className="h-4 w-4" />
                      Model Selection
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="provider">AI Provider</Label>
                      <Select 
                        value={formData.provider} 
                        onValueChange={(value) => {
                          setFormData(prev => ({ ...prev, provider: value, model: "" }))
                          setSelectedProvider(value)
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Choose an AI provider" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="openai">OpenAI</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {formData.provider && (
                      <div className="space-y-2">
                        <Label htmlFor="model">Model</Label>
                        <Select 
                          value={formData.model} 
                          onValueChange={(value) => {
                            setFormData(prev => ({ ...prev, model: value }))
                            setSelectedModel(value)
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Choose a model" />
                          </SelectTrigger>
                          <SelectContent>
                            {modelOptions[formData.provider as keyof typeof modelOptions]?.map((model) => (
                              <SelectItem key={model.value} value={model.value}>
                                {model.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    {formData.provider && formData.model && (
                      <div className="p-3 bg-muted rounded-lg">
                        <p className="text-sm text-muted-foreground">
                          Selected:{" "}
                          <span className="font-medium text-foreground">
                            {formData.provider.charAt(0).toUpperCase() + formData.provider.slice(1)} -{" "}
                            {
                              modelOptions[formData.provider as keyof typeof modelOptions]?.find(
                                (m) => m.value === formData.model,
                              )?.label
                            }
                          </span>
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>


              <TabsContent value="memory" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Brain className="h-4 w-4" />
                      Memory Configuration
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-base">Short-term Memory</Label>
                        <p className="text-sm text-muted-foreground">Remember context within conversations</p>
                      </div>
                      <Switch 
                        checked={formData.shortTermMemory}
                        onCheckedChange={(checked) => setFormData(prev => ({ ...prev, shortTermMemory: checked }))}
                      />
                    </div>

                    <Separator />

                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-base">Long-term Memory</Label>
                        <p className="text-sm text-muted-foreground">Remember user preferences across sessions</p>
                      </div>
                      <Switch 
                        checked={formData.longTermMemory}
                        onCheckedChange={(checked) => setFormData(prev => ({ ...prev, longTermMemory: checked }))}
                      />
                    </div>

                    <Separator />

                    <div className="space-y-2">
                      <Label>Memory Retention (days)</Label>
                      <Select defaultValue="30">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="7">7 days</SelectItem>
                          <SelectItem value="30">30 days</SelectItem>
                          <SelectItem value="90">90 days</SelectItem>
                          <SelectItem value="365">1 year</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="platforms" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Settings className="h-4 w-4" />
                      Platform Integration
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="platform">Select Platform</Label>
                      <Select 
                        value={formData.platform} 
                        onValueChange={(value) => {
                          setFormData(prev => ({ ...prev, platform: value }))
                          setSelectedPlatform(value)
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Choose a platform" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="telegram">
                            <div className="flex items-center gap-2">
                              <MessageCircle className="h-4 w-4" />
                              Telegram
                            </div>
                          </SelectItem>
                          <SelectItem value="whatsapp">
                            <div className="flex items-center gap-2">
                              <Phone className="h-4 w-4" />
                              WhatsApp
                            </div>
                          </SelectItem>
                          <SelectItem value="website">
                            <div className="flex items-center gap-2">
                              <Globe className="h-4 w-4" />
                              Website
                            </div>
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {formData.platform === "telegram" && (
                      <div className="space-y-2">
                        <Label htmlFor="telegram-api-key">Telegram Bot API Key</Label>
                        <Input 
                          id="telegram-api-key" 
                          type="password" 
                          value={formData.apiKey}
                          onChange={(e) => setFormData(prev => ({ ...prev, apiKey: e.target.value }))}
                          placeholder="Enter your Telegram bot token" 
                        />
                        <p className="text-xs text-muted-foreground">Get your bot token from @BotFather on Telegram</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="behavior" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Settings className="h-4 w-4" />
                      Behavior Settings
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>Tone</Label>
                      <Select 
                        value={formData.tone}
                        onValueChange={(value) => setFormData(prev => ({ ...prev, tone: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="formal">Formal</SelectItem>
                          <SelectItem value="friendly">Friendly</SelectItem>
                          <SelectItem value="casual">Casual</SelectItem>
                          <SelectItem value="profesional">Professional</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Max Tokens</Label>
                      <Input 
                        type="number" 
                        value={formData.maxTokens}
                        onChange={(e) => setFormData(prev => ({ ...prev, maxTokens: e.target.value }))}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Base Prompt</Label>
                      <Textarea
                        value={formData.basePrompt}
                        onChange={(e) => setFormData(prev => ({ ...prev, basePrompt: e.target.value }))}
                        placeholder="Enter the base prompt that defines your agent's behavior and personality"
                        rows={4}
                      />
                      <p className="text-xs text-muted-foreground">
                        This prompt will be used as the foundation for all agent interactions
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </div>

            <div className="flex justify-end space-x-2 pt-4 border-t border-border flex-shrink-0">
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button 
                onClick={handleFormSubmit}
                disabled={isSubmitting}
              >
                {isSubmitting 
                  ? (agent ? "Updating..." : "Creating...") 
                  : (agent ? "Save Changes" : "Create Agent")
                }
              </Button>
            </div>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  )
}
