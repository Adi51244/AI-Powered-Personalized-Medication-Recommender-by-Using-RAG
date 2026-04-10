/**
 * List of medication recommendations with safety alerts
 */

import { MedicationRecommendation } from '@/lib/types';
import MedicationCard from './MedicationCard';
import EmptyState from '@/components/common/EmptyState';
import { Pill } from 'lucide-react';

interface MedicationsListProps {
  medications: MedicationRecommendation[];
}

export default function MedicationsList({ medications }: MedicationsListProps) {
  if (medications.length === 0) {
    return (
      <EmptyState
        title="No medications recommended"
        description="No medication recommendations were generated for this diagnosis."
        icon={<Pill className="h-12 w-12 text-gray-400" />}
      />
    );
  }

  // Separate by safety status for better UX
  const safe = medications.filter(m => m.safety_status === 'safe');
  const warnings = medications.filter(m => m.safety_status === 'warning');
  const contraindicated = medications.filter(m => m.safety_status === 'contraindicated');

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          <span className="font-medium">Total: {medications.length} medication{medications.length !== 1 ? 's' : ''}</span>
          {' '}&bull;{' '}
          <span className="text-green-700">{safe.length} safe</span>
          {warnings.length > 0 && <>, <span className="text-amber-700">{warnings.length} with warnings</span></>}
          {contraindicated.length > 0 && <>, <span className="text-red-700">{contraindicated.length} contraindicated</span></>}
        </p>
      </div>

      {/* Safe medications */}
      {safe.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Safe Medications</h4>
          <div className="space-y-3">
            {safe.map((med, index) => (
              <MedicationCard key={`${med.name}-${index}`} medication={med} />
            ))}
          </div>
        </div>
      )}

      {/* Medications with warnings */}
      {warnings.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-amber-700 mb-3">Medications with Warnings</h4>
          <div className="space-y-3">
            {warnings.map((med, index) => (
              <MedicationCard key={`${med.name}-${index}`} medication={med} />
            ))}
          </div>
        </div>
      )}

      {/* Contraindicated medications */}
      {contraindicated.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-red-700 mb-3">Contraindicated Medications</h4>
          <div className="space-y-3">
            {contraindicated.map((med, index) => (
              <MedicationCard key={`${med.name}-${index}`} medication={med} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
