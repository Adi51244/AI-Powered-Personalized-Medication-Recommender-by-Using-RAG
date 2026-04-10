/**
 * Main patient input form orchestrator with React Hook Form and Zod validation
 */

'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { PatientFormData, PatientInputSchema } from '@/lib/utils/validation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { AlertCircle, Send, RotateCcw } from 'lucide-react';
import DemographicsSection from './DemographicsSection';
import SymptomsSection from './SymptomsSection';
import MedicalHistorySection from './MedicalHistorySection';
import { PatientInput } from '@/lib/types';

interface PatientInputFormProps {
  onSubmit: (data: PatientInput) => void;
  isLoading?: boolean;
}

export default function PatientInputForm({ onSubmit, isLoading = false }: PatientInputFormProps) {
  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<PatientFormData>({
    resolver: zodResolver(PatientInputSchema),
    defaultValues: {
      age: undefined,
      gender: undefined,
      weight_kg: undefined,
      height_cm: undefined,
      symptoms: [{ name: '', severity: 5, duration_days: 0 }],
      chronic_conditions: [],
      allergies: [],
      current_medications: []
    }
  });

  const onFormSubmit = (data: PatientFormData) => {
    // Transform data to match backend schema (filter empty strings from arrays)
    const patientInput: PatientInput = {
      ...data,
       chronic_conditions: data.chronic_conditions?.filter(c => c.trim() !== '') || [],
       allergies: data.allergies?.filter(a => a.trim() !== '') || [],
       current_medications: data.current_medications?.filter(m => m.trim() !== '') || []
    };

    onSubmit(patientInput);
  };

  const handleReset = () => {
    reset({
      age: undefined,
      gender: undefined,
      weight_kg: undefined,
      height_cm: undefined,
      symptoms: [{ name: '', severity: 5, duration_days: 0 }],
      chronic_conditions: [],
      allergies: [],
      current_medications: []
    });
  };

  const hasErrors = Object.keys(errors).length > 0;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Patient Information</CardTitle>
        <CardDescription>
          Enter patient demographics, symptoms, and medical history for AI-powered diagnosis
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-8">
          {/* Error Summary */}
          {hasErrors && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Please fix the following errors:</p>
                <ul className="list-disc list-inside text-sm text-red-700 mt-2 space-y-1">
                  {errors.age && <li>{errors.age.message}</li>}
                  {errors.gender && <li>{errors.gender.message}</li>}
                  {errors.symptoms && typeof errors.symptoms.message === 'string' && (
                    <li>{errors.symptoms.message}</li>
                  )}
                  {errors.symptoms && Array.isArray(errors.symptoms) && (
                    <li>Some symptoms have validation errors</li>
                  )}
                </ul>
              </div>
            </div>
          )}

          {/* Demographics Section */}
          <DemographicsSection
            register={register}
            errors={errors}
            control={control}
          />

          <Separator />

          {/* Symptoms Section */}
          <SymptomsSection
            register={register}
            errors={errors}
            control={control}
          />

          <Separator />

          {/* Medical History Section */}
          <MedicalHistorySection
            register={register}
            errors={errors}
             control={control as any}
          />

          <Separator />

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleReset}
              disabled={isLoading || isSubmitting}
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              Reset Form
            </Button>
            <Button
              type="submit"
              disabled={isLoading || isSubmitting}
              className="min-w-[200px]"
            >
              {isLoading || isSubmitting ? (
                <>Loading...</>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Analyze & Diagnose
                </>
              )}
            </Button>
          </div>

          {/* Help Text */}
          <p className="text-xs text-gray-500 text-center">
            <span className="text-red-500">*</span> Required fields
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
