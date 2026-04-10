/**
 * Error display component with retry functionality
 */

'use client';

import { AlertCircle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

interface ErrorDisplayProps {
  error: Error | string;
  onRetry?: () => void;
  showDetails?: boolean;
}

export default function ErrorDisplay({ error, onRetry, showDetails = false }: ErrorDisplayProps) {
  const [detailsVisible, setDetailsVisible] = useState(false);

  const errorMessage = typeof error === 'string' ? error : error.message;
  const errorStack = typeof error === 'string' ? undefined : error.stack;

  return (
    <div className="space-y-4">
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription className="mt-2 space-y-3">
          <p>{errorMessage}</p>

          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="mt-2"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          )}

          {showDetails && errorStack && (
            <div className="mt-3">
              <button
                onClick={() => setDetailsVisible(!detailsVisible)}
                className="text-sm underline hover:no-underline"
              >
                {detailsVisible ? 'Hide' : 'Show'} technical details
              </button>

              {detailsVisible && (
                <pre className="mt-2 text-xs bg-gray-100 p-3 rounded overflow-auto max-h-40">
                  {errorStack}
                </pre>
              )}
            </div>
          )}
        </AlertDescription>
      </Alert>

      <div className="text-sm text-gray-600">
        <p className="font-medium">Suggestions:</p>
        <ul className="list-disc list-inside mt-1 space-y-1">
          <li>Check your internet connection</li>
          <li>Verify the backend server is running</li>
          <li>Try refreshing the page</li>
          <li>If the problem persists, contact support</li>
        </ul>
      </div>
    </div>
  );
}
