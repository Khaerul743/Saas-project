import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { MessageSquare, Bot, User, Clock } from "lucide-react"

const recentActivities = [
  {
    id: 1,
    type: "conversation",
    agent: "Customer Support",
    user: "john.doe@example.com",
    message: "Resolved billing inquiry",
    time: "2 minutes ago",
    status: "completed",
  },
  {
    id: 2,
    type: "agent_created",
    agent: "Lead Qualifier",
    user: "admin",
    message: "New agent created and deployed",
    time: "15 minutes ago",
    status: "active",
  },
  {
    id: 3,
    type: "conversation",
    agent: "Sales Assistant",
    user: "sarah.wilson@company.com",
    message: "Product demo scheduled",
    time: "32 minutes ago",
    status: "completed",
  },
  {
    id: 4,
    type: "conversation",
    agent: "FAQ Bot",
    user: "mike.johnson@startup.io",
    message: "Integration questions answered",
    time: "1 hour ago",
    status: "completed",
  },
]

export function RecentActivity() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-heading">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {recentActivities.map((activity) => (
          <div key={activity.id} className="flex items-start space-x-3">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="bg-primary/10">
                {activity.type === "conversation" ? (
                  <MessageSquare className="h-4 w-4 text-primary" />
                ) : (
                  <Bot className="h-4 w-4 text-primary" />
                )}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">{activity.agent}</p>
                <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>{activity.time}</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">{activity.message}</p>
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                  <User className="h-3 w-3" />
                  <span>{activity.user}</span>
                </div>
                <Badge variant={activity.status === "completed" ? "default" : "secondary"} className="text-xs">
                  {activity.status}
                </Badge>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
