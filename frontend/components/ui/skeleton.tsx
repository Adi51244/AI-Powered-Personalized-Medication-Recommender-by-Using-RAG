import { cn } from "@/lib/utils/cn";

/**
 * Skeleton Component
 *
 * Provides a loading placeholder with shimmer animation.
 * Use for content that is being loaded asynchronously.
 */
function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-gray-200 dark:bg-gray-800", className)}
      {...props}
    />
  );
}

export { Skeleton };
