"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { UserMenu } from "@/components/user-menu"
import { useAuth } from "@/lib/auth-context"
import { cn } from "@/lib/utils"
import { Activity, Bot, Home, Menu, Play, Plus, X } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Agents", href: "/agents", icon: Bot },
  { name: "Playground", href: "/playground", icon: Play },
  { name: "Tracing", href: "/tracing", icon: Activity },
]

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const pathname = usePathname()
  const { user, isAuthenticated, isLoading } = useAuth()

  // Debug logging
  console.log("[DashboardLayout] Auth state:", { 
    isLoading, 
    isAuthenticated, 
    user: user ? { id: user.id, name: user.name, email: user.email } : null 
  })

  if (!isLoading && !isAuthenticated) {
    console.log("[DashboardLayout] Not authenticated, redirecting to login...")
    if (typeof window !== "undefined") {
      window.location.href = "/auth/login"
    }
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
          <span className="text-muted-foreground">Redirecting to login...</span>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
          <span className="text-muted-foreground">Loading...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 transform bg-sidebar border-r border-sidebar-border transition-transform duration-300 ease-in-out lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-sidebar-border">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-sidebar-primary flex items-center justify-center">
                <Bot className="h-5 w-5 text-sidebar-primary-foreground" />
              </div>
              <span className="text-lg font-bold text-sidebar-foreground font-heading">AI Platform</span>
            </div>
            <Button variant="ghost" size="sm" className="lg:hidden" onClick={() => setSidebarOpen(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 animate-slide-in",
                    isActive
                      ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-lg"
                      : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground hover:translate-x-1",
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </nav>

          {/* Bottom section */}
          <div className="p-4 border-t border-sidebar-border">
            <Button className="w-full shadow-lg hover:shadow-xl transition-all duration-200" size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Create Agent
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top header */}
        <header className="sticky top-0 z-30 glass-effect border-b border-border">
          <div className="flex h-16 items-center justify-between px-6">
            <Button variant="ghost" size="sm" className="lg:hidden" onClick={() => setSidebarOpen(true)}>
              <Menu className="h-5 w-5" />
            </Button>

            <div className="flex items-center space-x-4">
              <div className="text-sm text-muted-foreground">Welcome back, {user?.name || "User"}</div>
              <UserMenu />
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6 animate-fade-in">{children}</main>
      </div>
    </div>
  )
}
