/**
 * Safety status badge component (safe, warning, contraindicated)
 */

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils/cn';
import { getSafetyColors, getSafetyLabel, SafetyStatus } from '@/lib/utils/colors';
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

interface SafetyBadgeProps {
  status: SafetyStatus;
  className?: string;
}

const StatusIcons = {
  safe: CheckCircle,
  warning: AlertTriangle,
  contraindicated: XCircle
};

export default function SafetyBadge({ status, className }: SafetyBadgeProps) {
  const colors = getSafetyColors(status);
  const label = getSafetyLabel(status);
  const Icon = StatusIcons[status];

  return (
    <Badge
      className={cn(
        colors.badge,
        'text-white flex items-center gap-1.5 px-2.5 py-1',
        className
      )}
    >
      <Icon className="h-3.5 w-3.5" />
      {label}
    </Badge>
  );
}
