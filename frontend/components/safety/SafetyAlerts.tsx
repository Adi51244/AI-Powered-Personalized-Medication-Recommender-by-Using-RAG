/**
 * Safety alerts list grouped by severity
 */

import { SafetyWarning } from '@/lib/types';
import SafetyAlert from './SafetyAlert';
import EmptyState from '@/components/common/EmptyState';
import { ShieldCheck } from 'lucide-react';

interface SafetyAlertsProps {
  warnings: SafetyWarning[];
}

export default function SafetyAlerts({ warnings }: SafetyAlertsProps) {
  if (warnings.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <ShieldCheck className="h-6 w-6 text-green-600" />
          <div>
            <p className="font-medium text-green-900">No Safety Concerns</p>
            <p className="text-sm text-green-700">
              All recommended medications appear safe for this patient.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Group warnings by severity
  const major = warnings.filter(w => w.severity === 'major');
  const moderate = warnings.filter(w => w.severity === 'moderate');
  const minor = warnings.filter(w => w.severity === 'minor');

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <p className="text-sm text-amber-900">
          <span className="font-medium">{warnings.length} safety warning{warnings.length !== 1 ? 's' : ''} detected</span>
          {major.length > 0 && <>, <span className="text-red-700 font-semibold">{major.length} major</span></>}
          {moderate.length > 0 && <>, <span className="text-amber-700">{moderate.length} moderate</span></>}
          {minor.length > 0 && <>, <span className="text-yellow-700">{minor.length} minor</span></>}
        </p>
      </div>

      {/* Major warnings */}
      {major.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-red-700 mb-3">Major Warnings</h4>
          <div className="space-y-3">
            {major.map((warning, index) => (
              <SafetyAlert key={`major-${index}`} warning={warning} />
            ))}
          </div>
        </div>
      )}

      {/* Moderate warnings */}
      {moderate.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-amber-700 mb-3">Moderate Warnings</h4>
          <div className="space-y-3">
            {moderate.map((warning, index) => (
              <SafetyAlert key={`moderate-${index}`} warning={warning} />
            ))}
          </div>
        </div>
      )}

      {/* Minor warnings */}
      {minor.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-yellow-700 mb-3">Minor Warnings</h4>
          <div className="space-y-3">
            {minor.map((warning, index) => (
              <SafetyAlert key={`minor-${index}`} warning={warning} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
