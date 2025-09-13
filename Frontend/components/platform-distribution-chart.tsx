"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Globe, MessageCircle, Phone, Users } from "lucide-react"

export function PlatformDistributionChart() {
  // Mock data for platform distribution
  const platformData = [
    { platform: "Telegram", users: 1250, percentage: 45, color: "bg-blue-500", icon: MessageCircle },
    { platform: "WhatsApp", users: 890, percentage: 32, color: "bg-green-500", icon: Phone },
    { platform: "Website", users: 420, percentage: 15, color: "bg-purple-500", icon: Globe },
    { platform: "API", users: 240, percentage: 8, color: "bg-orange-500", icon: Users },
  ]

  const totalUsers = platformData.reduce((sum, platform) => sum + platform.users, 0)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Platform Distribution</CardTitle>
        <Users className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Total users */}
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">{totalUsers.toLocaleString()}</div>
            <div className="text-sm text-muted-foreground">Total Active Users</div>
          </div>

          {/* Platform breakdown */}
          <div className="space-y-3">
            {platformData.map((platform, index) => {
              const Icon = platform.icon
              return (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`h-3 w-3 rounded-full ${platform.color}`} />
                    <Icon className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">{platform.platform}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold">{platform.users.toLocaleString()}</span>
                    <span className="text-xs text-muted-foreground">({platform.percentage}%)</span>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Progress bars */}
          <div className="space-y-2">
            {platformData.map((platform, index) => (
              <div key={index} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">{platform.platform}</span>
                  <span className="text-muted-foreground">{platform.percentage}%</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${platform.color} transition-all duration-500`}
                    style={{ width: `${platform.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Growth indicator */}
          <div className="pt-2 border-t border-border">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Growth this month</span>
              <span className="text-sm font-medium text-green-600">+18%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
