"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, Calendar } from "lucide-react"

export function DailyActivityHeatmap() {
  // Mock data for daily activity (last 7 days)
  const activityData = [
    { day: "Mon", hours: [2, 5, 8, 12, 15, 18, 22, 25, 28, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100] },
    { day: "Tue", hours: [1, 3, 6, 10, 14, 17, 20, 24, 27, 32, 38, 42, 48, 52, 58, 62, 68, 72, 78, 82, 88, 92, 96, 100] },
    { day: "Wed", hours: [3, 7, 11, 16, 19, 23, 26, 29, 33, 37, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96, 100, 95] },
    { day: "Thu", hours: [4, 8, 13, 18, 22, 25, 28, 31, 35, 39, 44, 49, 54, 59, 64, 69, 74, 79, 84, 89, 94, 99, 100, 98] },
    { day: "Fri", hours: [5, 9, 14, 19, 24, 27, 30, 34, 38, 43, 48, 53, 58, 63, 68, 73, 78, 83, 88, 93, 98, 100, 97, 94] },
    { day: "Sat", hours: [2, 4, 7, 11, 15, 18, 21, 25, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88] },
    { day: "Sun", hours: [1, 3, 5, 8, 12, 16, 19, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62, 66, 70, 74, 78, 82, 86] }
  ]

  const hours = Array.from({ length: 24 }, (_, i) => i)

  const getIntensityColor = (value: number) => {
    if (value >= 80) return "bg-green-600"
    if (value >= 60) return "bg-green-500"
    if (value >= 40) return "bg-yellow-500"
    if (value >= 20) return "bg-orange-500"
    return "bg-gray-200"
  }

  const getIntensityText = (value: number) => {
    if (value >= 80) return "High"
    if (value >= 60) return "Medium-High"
    if (value >= 40) return "Medium"
    if (value >= 20) return "Low"
    return "Very Low"
  }

  const totalActivity = activityData.reduce((sum, day) => 
    sum + day.hours.reduce((daySum, hour) => daySum + hour, 0), 0
  )
  const avgActivity = totalActivity / (activityData.length * 24)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Daily Activity Heatmap</CardTitle>
        <Activity className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary">{totalActivity.toLocaleString()}</div>
              <div className="text-xs text-muted-foreground">Total Activity</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">{avgActivity.toFixed(0)}</div>
              <div className="text-xs text-muted-foreground">Avg per Hour</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">Peak: 2-4 PM</div>
              <div className="text-xs text-muted-foreground">Busiest Time</div>
            </div>
          </div>

          {/* Heatmap */}
          <div className="space-y-2">
            {/* Hour labels */}
            <div className="flex justify-between text-xs text-muted-foreground px-2">
              <span>12 AM</span>
              <span>6 AM</span>
              <span>12 PM</span>
              <span>6 PM</span>
              <span>12 AM</span>
            </div>

            {/* Heatmap grid */}
            <div className="space-y-1">
              {activityData.map((day, dayIndex) => (
                <div key={dayIndex} className="flex items-center space-x-2">
                  <div className="w-8 text-xs text-muted-foreground text-right">
                    {day.day}
                  </div>
                  <div className="flex space-x-1">
                    {day.hours.map((value, hourIndex) => (
                      <div
                        key={hourIndex}
                        className={`w-3 h-3 rounded-sm ${getIntensityColor(value)} hover:scale-110 transition-transform cursor-pointer`}
                        title={`${day.day} ${hours[hourIndex]}:00 - ${getIntensityText(value)} activity (${value} interactions)`}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center justify-between pt-2 border-t border-border">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-muted-foreground">Less</span>
              <div className="flex space-x-1">
                <div className="w-3 h-3 rounded-sm bg-gray-200" />
                <div className="w-3 h-3 rounded-sm bg-orange-500" />
                <div className="w-3 h-3 rounded-sm bg-yellow-500" />
                <div className="w-3 h-3 rounded-sm bg-green-500" />
                <div className="w-3 h-3 rounded-sm bg-green-600" />
              </div>
              <span className="text-xs text-muted-foreground">More</span>
            </div>
            <div className="flex items-center space-x-1 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>Last 7 days</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
