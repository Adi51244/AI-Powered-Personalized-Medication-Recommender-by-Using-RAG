/**
 * Single symptom input component with name, severity slider, and duration
 */

'use client';

import { UseFormRegister, FieldErrors } from 'react-hook-form';
import { PatientFormData } from '@/lib/utils/validation';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

interface SymptomInputProps {
  index: number;
  register: UseFormRegister<PatientFormData>;
  errors: FieldErrors<PatientFormData>;
  onRemove: () => void;
  showRemove: boolean;
  defaultValue?: { severity: number };
}

export default function SymptomInput({
  index,
  register,
  errors,
  onRemove,
  showRemove,
  defaultValue
}: SymptomInputProps) {
  const symptomError = errors.symptoms?.[index];

  return (
    <div className="border border-gray-200 rounded-lg p-4 space-y-4 bg-white">
      <div className="flex items-start justify-between">
        <h4 className="text-sm font-medium text-gray-900">Symptom {index + 1}</h4>
        {showRemove && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onRemove}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Symptom Name */}
      <div className="space-y-2">
        <Label htmlFor={`symptoms.${index}.name`}>
          Symptom Name <span className="text-red-500">*</span>
        </Label>
        <Input
          id={`symptoms.${index}.name`}
          placeholder="e.g., fever, cough, headache"
          {...register(`symptoms.${index}.name` as const)}
          className={symptomError?.name ? 'border-red-500' : ''}
        />
        {symptomError?.name && (
          <p className="text-sm text-red-500">{symptomError.name.message}</p>
        )}
      </div>

      {/* Severity Slider */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor={`symptoms.${index}.severity`}>
            Severity <span className="text-red-500">*</span>
          </Label>
          <span className="text-sm text-gray-600">
            {defaultValue?.severity || 5} / 10
          </span>
        </div>
        <input
          type="number"
          defaultValue={5}
          min={1}
          max={10}
          {...register(`symptoms.${index}.severity` as const, { valueAsNumber: true })}
          className="hidden"
        />
        <Slider
          defaultValue={[defaultValue?.severity || 5]}
          min={1}
          max={10}
          step={1}
          className="w-full"
          onValueChange={(value) => {
            const input = document.querySelector(
              `input[name="symptoms.${index}.severity"]`
            ) as HTMLInputElement;
            if (input) input.value = value[0].toString();
          }}
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>Mild</span>
          <span>Severe</span>
        </div>
        {symptomError?.severity && (
          <p className="text-sm text-red-500">{symptomError.severity.message}</p>
        )}
      </div>

      {/* Duration */}
      <div className="space-y-2">
        <Label htmlFor={`symptoms.${index}.duration_days`}>
          Duration (days) <span className="text-red-500">*</span>
        </Label>
        <Input
          id={`symptoms.${index}.duration_days`}
          type="number"
          min={0}
          placeholder="0"
          {...register(`symptoms.${index}.duration_days` as const, { valueAsNumber: true })}
          className={symptomError?.duration_days ? 'border-red-500' : ''}
        />
        {symptomError?.duration_days && (
          <p className="text-sm text-red-500">{symptomError.duration_days.message}</p>
        )}
      </div>
    </div>
  );
}
