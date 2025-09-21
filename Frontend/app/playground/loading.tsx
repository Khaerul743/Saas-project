import { DashboardLayout } from "@/components/dashboard-layout"
import { Bot } from "lucide-react"

export default function PlaygroundLoading() {
  return (
    <DashboardLayout>
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Bot className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">Loading playground...</p>
        </div>
      </div>
    </DashboardLayout>
  )
}
