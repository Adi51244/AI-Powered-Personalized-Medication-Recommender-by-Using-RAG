/**
 * Medical history section: chronic conditions, allergies, current medications
 */

'use client';

import { UseFormRegister, FieldErrors, useFieldArray, Control } from 'react-hook-form';
import { PatientFormData } from '@/lib/utils/validation';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Plus, X } from 'lucide-react';

interface MedicalHistorySectionProps {
  register: UseFormRegister<PatientFormData>;
  errors: FieldErrors<PatientFormData>;
    control: Control<any>;
}

export default function MedicalHistorySection({
  register,
  errors,
  control
}: MedicalHistorySectionProps) {
  const {
    fields: conditionFields,
    append: appendCondition,
    remove: removeCondition
  } = useFieldArray({ control, name: 'chronic_conditions' });

  const {
    fields: allergyFields,
    append: appendAllergy,
    remove: removeAllergy
  } = useFieldArray({ control, name: 'allergies' });

  const {
    fields: medicationFields,
    append: appendMedication,
    remove: removeMedication
  } = useFieldArray({ control, name: 'current_medications' });

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">
        Medical History <span className="text-gray-500 text-sm font-normal">(Optional)</span>
      </h3>

      {/* Chronic Conditions */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label>Chronic Conditions</Label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => appendCondition('')}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Condition
          </Button>
        </div>
        {conditionFields.map((field, index) => (
          <div key={field.id} className="flex items-center gap-2">
            <Input
              placeholder="e.g., Diabetes, Hypertension"
              {...register(`chronic_conditions.${index}` as const)}
              className="flex-1"
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => removeCondition(index)}
              className="h-10 w-10 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ))}
        {conditionFields.length === 0 && (
          <p className="text-sm text-gray-500 italic">No chronic conditions added</p>
        )}
      </div>

      {/* Allergies */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label>Allergies</Label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => appendAllergy('')}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Allergy
          </Button>
        </div>
        {allergyFields.map((field, index) => (
          <div key={field.id} className="flex items-center gap-2">
            <Input
              placeholder="e.g., Penicillin, Latex"
              {...register(`allergies.${index}` as const)}
              className="flex-1"
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => removeAllergy(index)}
              className="h-10 w-10 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ))}
        {allergyFields.length === 0 && (
          <p className="text-sm text-gray-500 italic">No allergies added</p>
        )}
      </div>

      {/* Current Medications */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label>Current Medications</Label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => appendMedication('')}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Medication
          </Button>
        </div>
        {medicationFields.map((field, index) => (
          <div key={field.id} className="flex items-center gap-2">
            <Input
              placeholder="e.g., Metformin, Lisinopril"
              {...register(`current_medications.${index}` as const)}
              className="flex-1"
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => removeMedication(index)}
              className="h-10 w-10 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ))}
        {medicationFields.length === 0 && (
          <p className="text-sm text-gray-500 italic">No current medications added</p>
        )}
      </div>
    </div>
  );
}
