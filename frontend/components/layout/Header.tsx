/**
 * Header component with app name, health status, search, notifications, and user menu
 */

'use client';

import { APP_NAME } from '@/lib/utils/constants';
import { Activity } from 'lucide-react';
import { ThemeToggle } from '@/components/layout/ThemeToggle';
import { SearchCommand } from '@/components/layout/SearchCommand';
import { NotificationsPanel } from '@/components/layout/NotificationsPanel';
import { UserMenu } from '@/components/layout/UserMenu';

export default function Header() {
  return (
    <header className="sticky top-0 z-40 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm transition-smooth backdrop-blur-sm bg-white/95 dark:bg-gray-900/95">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Logo and branding */}
          <div className="flex items-center space-x-3">
            <Activity className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">{APP_NAME}</h1>
              <p className="hidden sm:block text-xs text-gray-500 dark:text-gray-400">AI-Powered Clinical Decision Support</p>
            </div>
          </div>

          {/* Right: Search + Status + Notifications + Theme + User */}
          <div className="flex items-center space-x-2 sm:space-x-4">
            {/* Search command (Cmd+K) */}
            <div className="hidden md:block">
              <SearchCommand />
            </div>

            {/* System status indicator */}
            <div className="hidden lg:flex items-center space-x-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs text-gray-600 dark:text-gray-300">Online</span>
            </div>

            {/* Notifications */}
            <NotificationsPanel />

            {/* Theme toggle */}
            <ThemeToggle />

            {/* User menu */}
            <UserMenu />
          </div>
        </div>
      </div>
    </header>
  );
}
