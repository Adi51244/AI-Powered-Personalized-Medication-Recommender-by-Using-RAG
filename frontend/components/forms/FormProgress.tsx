'use client';

import * as React from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

interface FormProgressProps {
  steps: {
    title: string;
    description?: string;
  }[];
  currentStep: number;
  onStepClick?: (step: number) => void;
}

/**
 * FormProgress Component
 *
 * Visual step indicator for multi-step forms.
 * Shows completed, current, and upcoming steps.
 */
export function FormProgress({
  steps,
  currentStep,
  onStepClick,
}: FormProgressProps) {
  return (
    <div className="w-full">
      {/* Step indicators */}
      <div className="flex items-center justify-between mb-8">
        {steps.map((step, index) => (
          <React.Fragment key={index}>
            {/* Step circle */}
            <button
              onClick={() => onStepClick?.(index)}
              disabled={!onStepClick}
              className={cn(
                'flex h-10 w-10 items-center justify-center rounded-full font-semibold transition-all',
                index < currentStep
                  ? 'bg-green-500 text-white cursor-pointer hover:bg-green-600'
                  : index === currentStep
                  ? 'bg-blue-600 text-white ring-4 ring-blue-200 dark:ring-blue-800'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
              )}
            >
              {index < currentStep ? (
                <Check className="h-5 w-5" />
              ) : (
                <span>{index + 1}</span>
              )}
            </button>

            {/* Connector line */}
            {index < steps.length - 1 && (
              <div
                className={cn(
                  'mx-2 flex-1 h-1 rounded transition-colors',
                  index < currentStep
                    ? 'bg-green-500'
                    : 'bg-gray-200 dark:bg-gray-700'
                )}
              />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Step titles and descriptions */}
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div
            key={index}
            className="flex-1 px-2 text-center"
          >
            <p
              className={cn(
                'text-sm font-medium transition-colors',
                index === currentStep
                  ? 'text-gray-900 dark:text-white'
                  : index < currentStep
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-gray-500 dark:text-gray-400'
              )}
            >
              {step.title}
            </p>
            {step.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {step.description}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
