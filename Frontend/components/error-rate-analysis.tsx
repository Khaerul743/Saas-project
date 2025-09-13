"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle, CheckCircle, Clock, XCircle } from "lucide-react"

export function ErrorRateAnalysis() {
  // Mock data for error analysis
  const errorData = [
    { type: "API Timeout", count: 45, percentage: 35, trend: "down", trendValue: 12 },
    { type: "Invalid Input", count: 32, percentage: 25, trend: "up", trendValue: 8 },
    { type: "Rate Limit", count: 28, percentage: 22, trend: "stable", trendValue: 0 },
    { type: "Authentication", count: 15, percentage: 12, trend: "down", trendValue: 5 },
    { type: "Server Error", count: 8, percentage: 6, trend: "down", trendValue: 3 },
  ]

  const totalErrors = errorData.reduce((sum, error) => sum + error.count, 0)
  const successRate = 95.2 // Mock success rate

  const getErrorIcon = (type: string) => {
    switch (type) {
      case "API Timeout":
        return <Clock className="h-4 w-4 text-orange-500" />
      case "Invalid Input":
        return <XCircle className="h-4 w-4 text-red-500" />
      case "Rate Limit":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case "Authentication":
        return <XCircle className="h-4 w-4 text-red-600" />
      case "Server Error":
        return <AlertTriangle className="h-4 w-4 text-red-700" />
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "down":
        return "text-green-600"
      case "up":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Error Rate Analysis</CardTitle>
        <AlertTriangle className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Overall stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-green-50 rounded-lg border border-green-200">
              <CheckCircle className="h-6 w-6 text-green-600 mx-auto mb-1" />
              <div className="text-lg font-bold text-green-600">{successRate}%</div>
              <div className="text-xs text-green-700">Success Rate</div>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg border border-red-200">
              <XCircle className="h-6 w-6 text-red-600 mx-auto mb-1" />
              <div className="text-lg font-bold text-red-600">{totalErrors}</div>
              <div className="text-xs text-red-700">Total Errors</div>
            </div>
          </div>

          {/* Error breakdown */}
          <div className="space-y-3">
            {errorData.map((error, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getErrorIcon(error.type)}
                    <span className="text-sm font-medium">{error.type}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold">{error.count}</span>
                    <span className={`text-xs font-medium ${getTrendColor(error.trend)}`}>
                      {error.trend === "down" ? "↓" : error.trend === "up" ? "↑" : "→"} {error.trendValue}%
                    </span>
                  </div>
                </div>
                
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-red-500 transition-all duration-500"
                    style={{ width: `${error.percentage}%` }}
                  />
                </div>
                
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{error.percentage}% of total errors</span>
                  <span>Last 24 hours</span>
                </div>
              </div>
            ))}
          </div>

          {/* Recommendations */}
          <div className="pt-3 border-t border-border">
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-foreground">Recommendations</h4>
              <div className="space-y-1 text-xs text-muted-foreground">
                <div className="flex items-center space-x-2">
                  <div className="w-1 h-1 rounded-full bg-orange-500" />
                  <span>Increase API timeout for better reliability</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-1 h-1 rounded-full bg-yellow-500" />
                  <span>Implement input validation to reduce invalid requests</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-1 h-1 rounded-full bg-blue-500" />
                  <span>Consider rate limiting optimization</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
