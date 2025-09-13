import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus, Settings, BarChart3, Download, Upload } from "lucide-react"

export function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-heading">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button className="w-full justify-start bg-transparent" variant="outline">
          <Plus className="h-4 w-4 mr-2" />
          Create New Agent
        </Button>
        <Button className="w-full justify-start bg-transparent" variant="outline">
          <Upload className="h-4 w-4 mr-2" />
          Import Knowledge Base
        </Button>
        <Button className="w-full justify-start bg-transparent" variant="outline">
          <BarChart3 className="h-4 w-4 mr-2" />
          View Analytics
        </Button>
        <Button className="w-full justify-start bg-transparent" variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export Conversations
        </Button>
        <Button className="w-full justify-start bg-transparent" variant="outline">
          <Settings className="h-4 w-4 mr-2" />
          Platform Settings
        </Button>
      </CardContent>
    </Card>
  )
}
