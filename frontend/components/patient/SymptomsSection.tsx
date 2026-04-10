/**
 * Symptoms section with dynamic array of symptoms
 */

'use client';

import { UseFormRegister, FieldErrors, useFieldArray, Control } from 'react-hook-form';
import { PatientFormData } from '@/lib/utils/validation';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import SymptomInput from './SymptomInput';
import { PATIENT_CONSTRAINTS } from '@/lib/utils/constants';

interface SymptomsSectionProps {
  register: UseFormRegister<PatientFormData>;
  errors: FieldErrors<PatientFormData>;
  control: Control<PatientFormData>;
}

export default function SymptomsSection({
  register,
  errors,
  control
}: SymptomsSectionProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'symptoms'
  });

  const addSymptom = () => {
    if (fields.length < PATIENT_CONSTRAINTS.MAX_SYMPTOMS) {
      append({ name: '', severity: 5, duration_days: 0 });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Symptoms <span className="text-red-500">*</span>
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Add at least one symptom (maximum {PATIENT_CONSTRAINTS.MAX_SYMPTOMS})
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={addSymptom}
          disabled={fields.length >= PATIENT_CONSTRAINTS.MAX_SYMPTOMS}
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Symptom
        </Button>
      </div>

      {errors.symptoms && typeof errors.symptoms.message === 'string' && (
        <p className="text-sm text-red-500">{errors.symptoms.message}</p>
      )}

      <div className="space-y-3">
        {fields.map((field, index) => (
          <SymptomInput
            key={field.id}
            index={index}
            register={register}
            errors={errors}
            onRemove={() => remove(index)}
            showRemove={fields.length > 1}
            defaultValue={{ severity: 5 }}
          />
        ))}
      </div>

      {fields.length === 0 && (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <p className="text-gray-500 mb-3">No symptoms added yet</p>
          <Button type="button" variant="outline" onClick={addSymptom}>
            <Plus className="mr-2 h-4 w-4" />
            Add First Symptom
          </Button>
        </div>
      )}
    </div>
  );
}
