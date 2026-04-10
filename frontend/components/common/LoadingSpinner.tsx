/**
 * Loading spinner component with overlay
 */

'use client';

import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

interface LoadingSpinnerProps {
  message?: string;
  fullPage?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12'
};

export default function LoadingSpinner({
  message = 'Loading...',
  fullPage = false,
  size = 'md'
}: LoadingSpinnerProps) {
  if (fullPage) {
    return (
      <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="text-center space-y-4">
          <Loader2 className={cn('animate-spin text-blue-600 mx-auto', sizeClasses.lg)} />
          <p className="text-lg font-medium text-gray-900">{message}</p>
          <p className="text-sm text-gray-500">Please wait while we analyze the data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center py-8">
      <div className="text-center space-y-3">
        <Loader2 className={cn('animate-spin text-blue-600 mx-auto', sizeClasses[size])} />
        <p className="text-sm text-gray-600">{message}</p>
      </div>
    </div>
  );
}
