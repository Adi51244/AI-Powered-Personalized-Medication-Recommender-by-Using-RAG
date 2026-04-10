import { Skeleton } from "@/components/ui/skeleton";

/**
 * DiagnosisResultsSkeleton Component
 *
 * Loading placeholder for diagnosis results page.
 * Matches the structure of the actual DiagnosisResults component.
 */
export function DiagnosisResultsSkeleton() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header with summary stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6 shadow-card"
          >
            <Skeleton className="h-8 w-8 rounded-full mb-3" />
            <Skeleton className="h-8 w-16 mb-2" />
            <Skeleton className="h-4 w-24" />
          </div>
        ))}
      </div>

      {/* Tabs skeleton */}
      <div className="flex space-x-4 border-b border-gray-200 dark:border-gray-800">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-10 w-32" />
        ))}
      </div>

      {/* Content area - Prediction cards */}
      <div className="space-y-4">
        {/* Main prediction card */}
        <div className="rounded-lg border-2 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex-1 space-y-2">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
            <Skeleton className="h-16 w-16 rounded-full" />
          </div>
          <Skeleton className="h-3 w-full mb-2" />
          <Skeleton className="h-6 w-24 rounded-full" />
        </div>

        {/* Alternative predictions */}
        {[1, 2].map((i) => (
          <div
            key={i}
            className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex-1 space-y-2">
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-4 w-28" />
              </div>
              <Skeleton className="h-12 w-12 rounded-full" />
            </div>
            <Skeleton className="h-3 w-full mb-2" />
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
        ))}
      </div>

      {/* Medications/Evidence sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6">
          <Skeleton className="h-6 w-32 mb-4" />
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center space-x-3">
                <Skeleton className="h-10 w-10 rounded" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6">
          <Skeleton className="h-6 w-28 mb-4" />
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-3 w-5/6" />
                <Skeleton className="h-3 w-4/6" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
