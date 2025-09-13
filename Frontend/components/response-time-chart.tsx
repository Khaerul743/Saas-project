"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Clock, TrendingDown } from "lucide-react"

export function ResponseTimeChart() {
  // Mock data for response time trend
  const responseTimeData = [
    { time: "00:00", responseTime: 2.1 },
    { time: "04:00", responseTime: 1.8 },
    { time: "08:00", responseTime: 3.2 },
    { time: "12:00", responseTime: 2.8 },
    { time: "16:00", responseTime: 2.5 },
    { time: "20:00", responseTime: 2.3 },
  ]

  const maxResponseTime = Math.max(...responseTimeData.map(d => d.responseTime))
  const minResponseTime = Math.min(...responseTimeData.map(d => d.responseTime))
  const avgResponseTime = responseTimeData.reduce((sum, d) => sum + d.responseTime, 0) / responseTimeData.length

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Response Time Trend</CardTitle>
        <Clock className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{avgResponseTime.toFixed(1)}s</div>
              <div className="text-xs text-muted-foreground">Average</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{minResponseTime.toFixed(1)}s</div>
              <div className="text-xs text-muted-foreground">Fastest</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{maxResponseTime.toFixed(1)}s</div>
              <div className="text-xs text-muted-foreground">Slowest</div>
            </div>
          </div>

          {/* Chart */}
          <div className="h-32 relative">
            <div className="absolute inset-0 flex items-end justify-between px-2">
              {responseTimeData.map((data, index) => {
                const height = (data.responseTime / maxResponseTime) * 100
                const isPeak = data.responseTime === maxResponseTime
                const isLow = data.responseTime === minResponseTime
                
                return (
                  <div key={index} className="flex flex-col items-center space-y-1">
                    <div
                      className={`w-8 rounded-t transition-all duration-300 ${
                        isPeak 
                          ? "bg-orange-500" 
                          : isLow 
                            ? "bg-green-500" 
                            : "bg-primary"
                      }`}
                      style={{ height: `${height}%` }}
                    />
                    <div className="text-xs text-muted-foreground">{data.time}</div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Trend indicator */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TrendingDown className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-600 font-medium">-12% from yesterday</span>
            </div>
            <div className="text-xs text-muted-foreground">
              Last 24 hours
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
