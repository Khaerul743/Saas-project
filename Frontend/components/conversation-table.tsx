"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Conversation } from "@/lib/types/conversation"
import { Bot, Code, Eye, Globe, MessageCircle, Phone } from "lucide-react"

interface ConversationTableProps {
  conversations: Conversation[]
  onViewConversation: (conversation: Conversation) => void
}

const platformIcons = {
  web: Globe,
  website: Globe,
  whatsapp: Phone,
  telegram: MessageCircle,
  api: Code,
}

function ConversationTable({ conversations, onViewConversation }: ConversationTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-heading">Conversation Logs</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Agent</TableHead>
              <TableHead>Platform</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {conversations.map((conversation) => {
              const PlatformIcon = platformIcons[conversation.platform as keyof typeof platformIcons] || Bot
              return (
                <TableRow key={conversation.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-primary/10 text-primary text-xs">
                          {conversation.user.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="font-medium text-sm">{conversation.user}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium text-sm">{conversation.agent}</div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-1">
                      <PlatformIcon className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm capitalize">{conversation.platform}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-muted-foreground">
                      {new Date(conversation.date).toLocaleDateString()}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(conversation.date).toLocaleTimeString()}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm" onClick={() => onViewConversation(conversation)}>
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

export { ConversationTable }

