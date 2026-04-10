'use client';

import * as React from 'react';
import { PatientInput } from '@/lib/types';
import { FormStep } from './FormStep';

interface ReviewStepProps {
  data: PatientInput;
  isLoading?: boolean;
}

/**
 * ReviewStep Component
 *
 * Final review screen before form submission.
 */
export function ReviewStep({ data, isLoading = false }: ReviewStepProps) {
  return (
    <FormStep
      title="Review Your Information"
      description="Please verify all information before submitting for diagnosis"
      isActive={true}
    >
      <div className="grid gap-6">
        {/* Basic Info */}
        <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-6 bg-white dark:bg-gray-800">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Basic Information
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Age</p>
              <p className="font-medium text-gray-900 dark:text-white">
                {data.age} years
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Gender</p>
              <p className="font-medium text-gray-900 dark:text-white capitalize">
                {data.gender}
              </p>
            </div>
          </div>
        </div>

        {/* Symptoms */}
        {data.symptoms && data.symptoms.length > 0 && (
          <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-6 bg-white dark:bg-gray-800">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
              Symptoms ({data.symptoms.length})
            </h3>
            <div className="space-y-3">
              {data.symptoms.map((symptom, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 rounded bg-gray-100 dark:bg-gray-700"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {symptom.name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {symptom.duration_days} days • Severity: {symptom.severity}/10
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Chronic Conditions */}
        {data.chronic_conditions && data.chronic_conditions.length > 0 && (
          <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-6 bg-white dark:bg-gray-800">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
              Chronic Conditions
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.chronic_conditions.map((condition) => (
                <span
                  key={condition}
                  className="inline-flex items-center px-3 py-1 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 text-sm font-medium"
                >
                  {condition}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Current Medications */}
        {data.current_medications && data.current_medications.length > 0 && (
          <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-6 bg-white dark:bg-gray-800">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
              Current Medications
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.current_medications.map((medication) => (
                <span
                  key={medication}
                  className="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-sm font-medium"
                >
                  {medication}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Allergies */}
        {data.allergies && data.allergies.length > 0 && (
          <div className="rounded-lg border border-red-200 dark:border-red-800 p-6 bg-red-50 dark:bg-red-900/10">
            <h3 className="font-semibold text-red-900 dark:text-red-200 mb-4">
              ⚠️ Allergies
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.allergies.map((allergy) => (
                <span
                  key={allergy}
                  className="inline-flex items-center px-3 py-1 rounded-full bg-red-200 dark:bg-red-800 text-red-900 dark:text-red-100 text-sm font-medium"
                >
                  {allergy}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Empty state message */}
        {(!data.symptoms || data.symptoms.length === 0) && (
          <div className="rounded-lg border border-gray-300 dark:border-gray-600 p-6 bg-yellow-50 dark:bg-yellow-900/10 text-center">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              ℹ️ Please add at least one symptom before proceeding
            </p>
          </div>
        )}
      </div>
    </FormStep>
  );
}
