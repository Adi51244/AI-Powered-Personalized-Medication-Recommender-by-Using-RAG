/**
 * Individual safety alert component
 */

import { Alert, AlertDescription } from '@/components/ui/alert';
import { SafetyWarning } from '@/lib/types';
import { getSeverityColor, getSeverityLabel } from '@/lib/utils/colors';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

interface SafetyAlertProps {
  warning: SafetyWarning;
}

const SeverityIcons = {
  major: AlertCircle,
  moderate: AlertTriangle,
  minor: Info
};

const SeverityVariants = {
  major: 'destructive' as const,
  moderate: 'default' as const,
  minor: 'default' as const
};

export default function SafetyAlert({ warning }: SafetyAlertProps) {
  const { type, severity, message, drugs } = warning;
  const Icon = SeverityIcons[severity];
  const severityLabel = getSeverityLabel(severity);

  return (
    <Alert variant={SeverityVariants[severity]} className="border-l-4">
      <Icon className="h-4 w-4" />
      <AlertDescription className="space-y-2">
        <div className="flex items-center gap-2">
          <span className={`font-semibold ${getSeverityColor(severity)}`}>
            {severityLabel} {type.replace('_', ' ')}
          </span>
        </div>
        <p className="text-sm">{message}</p>
        {drugs && drugs.length > 0 && (
          <p className="text-xs text-gray-600">
            <span className="font-medium">Affected medications:</span> {drugs.join(', ')}
          </p>
        )}
      </AlertDescription>
    </Alert>
  );
}
