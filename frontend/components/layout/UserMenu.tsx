"use client";

import * as React from "react";
import { User, Settings, HelpCircle, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/context";
import { useToast } from "@/hooks/use-toast";
import { resolveDisplayName } from "@/lib/auth/display-name";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

/**
 * UserMenu Component
 *
 * User profile dropdown with account settings and actions.
 */
export function UserMenu() {
  const { user, loading, signOut } = useAuth()
  const router = useRouter()
  const { toast } = useToast()

  if (loading) {
    return (
      <Button variant="ghost" size="sm" className="h-9 px-2" disabled>
        Loading...
      </Button>
    )
  }

  if (!user) {
    return (
      <Link href="/auth/login">
        <Button size="sm" className="h-9">
          Sign In
        </Button>
      </Link>
    )
  }

  const handleLogout = async () => {
    try {
      await signOut()
      toast({ title: "Logged out successfully" })
      // Small delay to let the state update
      setTimeout(() => {
        router.push("/auth/login")
      }, 100)
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Failed to logout"
      console.error('Logout error:', error)
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      })
    }
  }

  const userEmail = user.email || "User"
  const userName = resolveDisplayName(user)

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="h-9 px-2">
          <div className="flex items-center space-x-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 text-white">
              <User className="h-4 w-4" />
            </div>
            <span className="hidden md:inline-block text-sm font-medium">
              {userName}
            </span>
          </div>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium">{userName}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {userEmail}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <Link href="/profile">
          <DropdownMenuItem>
            <Settings className="mr-2 h-4 w-4" />
            <span>Profile Settings</span>
          </DropdownMenuItem>
        </Link>
        <Link href="/dashboard">
          <DropdownMenuItem>
            <User className="mr-2 h-4 w-4" />
            <span>Dashboard</span>
          </DropdownMenuItem>
        </Link>
        <DropdownMenuItem>
          <HelpCircle className="mr-2 h-4 w-4" />
          <span>Help & Support</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          className="text-red-600 dark:text-red-400 cursor-pointer"
          onClick={handleLogout}
        >
          <LogOut className="mr-2 h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
