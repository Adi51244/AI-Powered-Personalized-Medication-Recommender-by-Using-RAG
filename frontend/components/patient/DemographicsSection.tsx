/**
 * Demographics section: age, gender, weight, height
 */

'use client';

import { UseFormRegister, FieldErrors } from 'react-hook-form';
import { PatientFormData } from '@/lib/utils/validation';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { GENDER_OPTIONS } from '@/lib/utils/constants';
import { Controller, Control } from 'react-hook-form';

interface DemographicsSectionProps {
  register: UseFormRegister<PatientFormData>;
  errors: FieldErrors<PatientFormData>;
  control: Control<PatientFormData>;
}

export default function DemographicsSection({
  register,
  errors,
  control
}: DemographicsSectionProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Patient Demographics</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Age */}
        <div className="space-y-2">
          <Label htmlFor="age">
            Age <span className="text-red-500">*</span>
          </Label>
          <Input
            id="age"
            type="number"
            min={0}
            max={150}
            placeholder="Enter age"
            {...register('age', { valueAsNumber: true })}
            className={errors.age ? 'border-red-500' : ''}
          />
          {errors.age && (
            <p className="text-sm text-red-500">{errors.age.message}</p>
          )}
        </div>

        {/* Gender */}
        <div className="space-y-2">
          <Label htmlFor="gender">
            Gender <span className="text-red-500">*</span>
          </Label>
          <Controller
            name="gender"
            control={control}
            render={({ field }) => (
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <SelectTrigger className={errors.gender ? 'border-red-500' : ''}>
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  {GENDER_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
          {errors.gender && (
            <p className="text-sm text-red-500">{errors.gender.message}</p>
          )}
        </div>

        {/* Weight */}
        <div className="space-y-2">
          <Label htmlFor="weight_kg">Weight (kg) <span className="text-gray-500 text-xs">(Optional)</span></Label>
          <Input
            id="weight_kg"
            type="number"
            min={0}
            step={0.1}
            placeholder="Enter weight"
            {...register('weight_kg', { valueAsNumber: true })}
            className={errors.weight_kg ? 'border-red-500' : ''}
          />
          {errors.weight_kg && (
            <p className="text-sm text-red-500">{errors.weight_kg.message}</p>
          )}
        </div>

        {/* Height */}
        <div className="space-y-2">
          <Label htmlFor="height_cm">Height (cm) <span className="text-gray-500 text-xs">(Optional)</span></Label>
          <Input
            id="height_cm"
            type="number"
            min={0}
            step={0.1}
            placeholder="Enter height"
            {...register('height_cm', { valueAsNumber: true })}
            className={errors.height_cm ? 'border-red-500' : ''}
          />
          {errors.height_cm && (
            <p className="text-sm text-red-500">{errors.height_cm.message}</p>
          )}
        </div>
      </div>
    </div>
  );
}
