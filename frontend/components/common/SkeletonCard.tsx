import { Skeleton } from "@/components/ui/skeleton";

/**
 * SkeletonCard Component
 *
 * Reusable skeleton pattern for card-based content.
 * Used throughout MediRAG for loading states.
 */
export function SkeletonCard() {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6 shadow-card">
      <div className="flex items-start space-x-4">
        {/* Icon/Image placeholder */}
        <Skeleton className="h-12 w-12 rounded-full" />

        <div className="flex-1 space-y-3">
          {/* Title */}
          <Skeleton className="h-5 w-3/4" />

          {/* Description lines */}
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />

          {/* Metadata/tags */}
          <div className="flex space-x-2 pt-2">
            <Skeleton className="h-6 w-16 rounded-full" />
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
}
