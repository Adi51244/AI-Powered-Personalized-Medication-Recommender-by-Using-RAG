"use client";

export interface Toast {
  title?: string;
  description?: string;
  variant?: "default" | "destructive";
}

export function useToast() {
  const toast = (props: Toast) => {
    // Simple implementation: log to console in dev, could be enhanced with UI toast
    console.log("[Toast]", props.title, props.description);
  };

  return { toast };
}
