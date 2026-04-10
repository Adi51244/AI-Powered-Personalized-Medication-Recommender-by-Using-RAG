"use client";

import * as React from "react";
import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

/**
 * NotificationsPanel Component
 *
 * Displays recent system notifications and alerts.
 * Shows badge with unread count.
 */
export function NotificationsPanel() {
  const [unreadCount] = React.useState(2); // Mock data

  const mockNotifications = [
    {
      id: 1,
      title: "Diagnosis Complete",
      message: "Patient John Doe - Diabetes Type 2 diagnosis ready",
      time: "5 min ago",
      read: false,
    },
    {
      id: 2,
      title: "Safety Alert",
      message: "Drug interaction detected in recent prescription",
      time: "1 hour ago",
      read: false,
    },
    {
      id: 3,
      title: "System Update",
      message: "ML models updated with latest data",
      time: "3 hours ago",
      read: true,
    },
  ];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="relative h-9 w-9 px-0">
          <Bell className="h-[1.2rem] w-[1.2rem]" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
              {unreadCount}
            </span>
          )}
          <span className="sr-only">Notifications</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel className="font-semibold">
          Notifications
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {mockNotifications.length === 0 ? (
          <div className="py-8 text-center text-sm text-gray-500 dark:text-gray-400">
            No notifications
          </div>
        ) : (
          mockNotifications.map((notification) => (
            <DropdownMenuItem
              key={notification.id}
              className={`flex flex-col items-start space-y-1 ${
                !notification.read ? "bg-blue-50 dark:bg-blue-950" : ""
              }`}
            >
              <div className="flex w-full items-center justify-between">
                <p className="text-sm font-medium">{notification.title}</p>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {notification.time}
                </span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-300">
                {notification.message}
              </p>
            </DropdownMenuItem>
          ))
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem className="justify-center text-sm text-blue-600 dark:text-blue-400">
          View all notifications
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
