/**
 * Individual medication recommendation card
 */

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { MedicationRecommendation } from '@/lib/types';
import { formatMedicationName } from '@/lib/utils/formatting';
import SafetyBadge from '../medications/SafetyBadge';
import { AlertTriangle, Clock, Pill } from 'lucide-react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

interface MedicationCardProps {
  medication: MedicationRecommendation;
}

export default function MedicationCard({ medication }: MedicationCardProps) {
  const { name, dosage, duration, safety_status, warnings, evidence } = medication;
  const hasWarnings = warnings.length > 0;

  return (
    <Card className={safety_status === 'contraindicated' ? 'border-red-300 bg-red-50/30' : ''}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Pill className="h-5 w-5 text-blue-600" />
              <h4 className={`text-lg font-semibold ${safety_status === 'contraindicated' ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                {formatMedicationName(name)}
              </h4>
            </div>

            <div className="space-y-1 text-sm text-gray-600">
              <p><span className="font-medium">Dosage:</span> {dosage}</p>
              <div className="flex items-center gap-1.5">
                <Clock className="h-4 w-4" />
                <span><span className="font-medium">Duration:</span> {duration}</span>
              </div>
            </div>
          </div>

          {/* Safety badge */}
          <SafetyBadge status={safety_status} className="ml-4" />
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Warnings */}
        {hasWarnings && (
          <div className="mb-3">
            <Accordion type="single" collapsible>
              <AccordionItem value="warnings" className="border-none">
                <AccordionTrigger className="text-sm text-amber-600 hover:text-amber-700 py-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    View {warnings.length} warning{warnings.length !== 1 ? 's' : ''}
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                    {warnings.map((warning, index) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        )}

        {/* Evidence citations */}
        {evidence.length > 0 && (
          <div className="text-xs text-gray-500 border-t pt-3">
            <span className="font-medium">Evidence: </span>
            {evidence.join(', ')}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
