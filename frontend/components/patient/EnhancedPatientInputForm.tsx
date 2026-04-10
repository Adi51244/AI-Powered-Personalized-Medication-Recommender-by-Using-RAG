'use client';

import { useState, useCallback } from 'react';
import { PatientInput, SymptomInput } from '@/lib/types';
import { toastMessages } from '@/lib/utils/toast-messages';
import { Button } from '@/components/ui/button';
import { FormProgress } from '@/components/forms/FormProgress';
import { FormStep } from '@/components/forms/FormStep';
import { SymptomAutocomplete } from '@/components/forms/SymptomAutocomplete';
import { SeveritySlider } from '@/components/forms/SeveritySlider';
import { BodyDiagram } from '@/components/forms/BodyDiagram';
import { ReviewStep } from '@/components/forms/ReviewStep';
import Container from '@/components/layout/Container';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PatientInputFormProps {
  onSubmit: (data: PatientInput) => void;
  isLoading?: boolean;
}

const FORM_STEPS = [
  { title: 'Basic Information', description: 'Start with your age and gender' },
  { title: 'Symptoms', description: 'Tell us about your symptoms' },
  { title: 'Medical History', description: 'Your health background' },
  { title: 'Review', description: 'Verify information before diagnosis' },
];

export default function PatientInputForm({
  onSubmit,
  isLoading = false,
}: PatientInputFormProps) {
  const [currentStep, setCurrentStep] = useState(0);

  // Step 1: Basic Info
  const [age, setAge] = useState<string>('');
  const [gender, setGender] = useState<'male' | 'female' | 'other'>('male');

  // Step 2: Symptoms
  const [symptoms, setSymptoms] = useState<SymptomInput[]>([]);
  const [selectedBodyParts, setSelectedBodyParts] = useState<string[]>([]);

  // Step 3: Medical History
  const [chronicConditions, setChronicConditions] = useState<string[]>([]);
  const [allergies, setAllergies] = useState<string[]>([]);
  const [medications, setMedications] = useState<string[]>([]);

  // Validation functions
  const isStep1Valid = age !== '' && parseInt(age) > 0 && parseInt(age) < 150;
  const isStep2Valid = symptoms.length > 0;
  const isStep3Valid = true;

  // Navigation
  const handleNext = useCallback(() => {
    if (currentStep === 0 && !isStep1Valid) {
      toastMessages.custom('Validation Error', 'Please enter a valid age (1-150)', 'error');
      return;
    }
    if (currentStep === 1 && !isStep2Valid) {
      toastMessages.custom('Validation Error', 'Please add at least one symptom', 'error');
      return;
    }
    if (currentStep < FORM_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  }, [currentStep, isStep1Valid, isStep2Valid]);

  const handlePrev = useCallback(() => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  }, [currentStep]);

  const handleSubmit = useCallback(() => {
    if (!isStep1Valid || !isStep2Valid) {
      toastMessages.custom('Incomplete Form', 'Please fill in all required fields', 'error');
      return;
    }

    const formData: PatientInput = {
      age: parseInt(age),
      gender,
      symptoms,
      chronic_conditions: chronicConditions,
      allergies,
      current_medications: medications,
    };

    onSubmit(formData);

    // Reset form
    setAge('');
    setGender('male');
    setSymptoms([]);
    setChronicConditions([]);
    setAllergies([]);
    setMedications([]);
    setCurrentStep(0);
  }, [age, gender, symptoms, chronicConditions, allergies, medications, isStep1Valid, isStep2Valid, onSubmit]);

  const handleAddSymptom = (symptom: SymptomInput) => {
    setSymptoms((prev) => [...prev, symptom]);
    toastMessages.custom('Success', `${symptom.name} added`, 'success');
  };

  const handleRemoveSymptom = (name: string) => {
    setSymptoms((prev) => prev.filter((s) => s.name !== name));
  };

  const handleUpdateSeverity = (name: string, severity: number) => {
    setSymptoms((prev) =>
      prev.map((s) => (s.name === name ? { ...s, severity } : s))
    );
  };

  return (
    <Container>
      <div className="max-w-2xl mx-auto">
        <div className="mb-12">
          <FormProgress steps={FORM_STEPS} currentStep={currentStep} />
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8">
          {/* Step 1: Basic Information */}
          <FormStep
            title={FORM_STEPS[0].title}
            description={FORM_STEPS[0].description}
            isActive={currentStep === 0}
          >
            <div className="space-y-6">
              {/* Age Input */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Age <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  min="1"
                  max="150"
                  placeholder="Enter your age"
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                />
                {age && (parseInt(age) < 1 || parseInt(age) > 150) && (
                  <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                    Please enter a valid age (1-150)
                  </p>
                )}
              </div>

              {/* Gender Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-3">
                  Gender <span className="text-red-500">*</span>
                </label>
                <div className="flex gap-4">
                  {(['male', 'female', 'other'] as const).map((option) => (
                    <label key={option} className="flex items-center cursor-pointer">
                      <input
                        type="radio"
                        name="gender"
                        value={option}
                        checked={gender === option}
                        onChange={(e) => setGender(e.target.value as 'male' | 'female' | 'other')}
                        className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-gray-700 dark:text-gray-300 capitalize">
                        {option}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </FormStep>

          {/* Step 2: Symptoms */}
          <FormStep
            title={FORM_STEPS[1].title}
            description={FORM_STEPS[1].description}
            isActive={currentStep === 1}
          >
            <div className="space-y-6">
              <SymptomAutocomplete
                symptoms={symptoms}
                onAddSymptom={handleAddSymptom}
                onRemoveSymptom={handleRemoveSymptom}
                onUpdateSeverity={handleUpdateSeverity}
              />

              {symptoms.length > 0 && (
                <div className="mt-8 p-6 rounded-lg bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                    Adjust Symptom Severity
                  </h3>
                  <div className="space-y-6">
                    {symptoms.map((symptom) => (
                      <div key={symptom.name} className="space-y-2">
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {symptom.name}
                        </label>
                        <SeveritySlider
                          value={symptom.severity}
                          onChange={(value) => handleUpdateSeverity(symptom.name, value)}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <BodyDiagram
                selectedParts={selectedBodyParts}
                onTogglePart={(partId) =>
                  setSelectedBodyParts((prev) =>
                    prev.includes(partId)
                      ? prev.filter((p) => p !== partId)
                      : [...prev, partId]
                  )
                }
              />
            </div>
          </FormStep>

          {/* Step 3: Medical History */}
          <FormStep
            title={FORM_STEPS[2].title}
            description={FORM_STEPS[2].description}
            isActive={currentStep === 2}
          >
            <div className="space-y-6">
              {/* Chronic Conditions */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Chronic Conditions
                </label>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    id="condition-input"
                    placeholder="e.g., Diabetes, Hypertension..."
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                  <Button
                    onClick={() => {
                      const input = document.getElementById('condition-input') as HTMLInputElement;
                      const value = input?.value.trim();
                      if (value && !chronicConditions.includes(value)) {
                        setChronicConditions((prev) => [...prev, value]);
                        if (input) input.value = '';
                      }
                    }}
                  >
                    Add
                  </Button>
                </div>
                {chronicConditions.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {chronicConditions.map((condition) => (
                      <span
                        key={condition}
                        className="inline-flex items-center px-3 py-1 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 text-sm font-medium"
                      >
                        {condition}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Allergies */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  ⚠️ Allergies
                </label>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    id="allergy-input"
                    placeholder="e.g., Penicillin, Peanuts..."
                    className="flex-1 px-4 py-2 rounded-lg border border-red-300 dark:border-red-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-red-500 outline-none"
                  />
                  <Button
                    onClick={() => {
                      const input = document.getElementById('allergy-input') as HTMLInputElement;
                      const value = input?.value.trim();
                      if (value && !allergies.includes(value)) {
                        setAllergies((prev) => [...prev, value]);
                        if (input) input.value = '';
                      }
                    }}
                  >
                    Add
                  </Button>
                </div>
                {allergies.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {allergies.map((allergy) => (
                      <span
                        key={allergy}
                        className="inline-flex items-center px-3 py-1 rounded-full bg-red-200 dark:bg-red-800 text-red-900 dark:text-red-100 text-sm font-medium"
                      >
                        {allergy}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Current Medications */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Current Medications
                </label>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    id="med-input"
                    placeholder="e.g., Metformin 500mg..."
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                  <Button
                    onClick={() => {
                      const input = document.getElementById('med-input') as HTMLInputElement;
                      const value = input?.value.trim();
                      if (value && !medications.includes(value)) {
                        setMedications((prev) => [...prev, value]);
                        if (input) input.value = '';
                      }
                    }}
                  >
                    Add
                  </Button>
                </div>
                {medications.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {medications.map((med) => (
                      <span
                        key={med}
                        className="inline-flex items-center px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 text-sm font-medium"
                      >
                        {med}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </FormStep>

          {/* Step 4: Review */}
          <FormStep
            title={FORM_STEPS[3].title}
            description={FORM_STEPS[3].description}
            isActive={currentStep === 3}
          >
            <ReviewStep
              data={{
                age: parseInt(age),
                gender,
                symptoms,
                chronic_conditions: chronicConditions,
                allergies,
                current_medications: medications,
              }}
              isLoading={isLoading}
            />
          </FormStep>

          {/* Navigation Buttons */}
          <div className="flex items-center justify-between mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
            <Button
              variant="outline"
              onClick={handlePrev}
              disabled={currentStep === 0 || isLoading}
              className="flex items-center gap-2"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>

            <div className="text-sm text-gray-600 dark:text-gray-400">
              Step {currentStep + 1} of {FORM_STEPS.length}
            </div>

            {currentStep === FORM_STEPS.length - 1 ? (
              <Button
                onClick={handleSubmit}
                disabled={isLoading || !isStep1Valid || !isStep2Valid}
                className="flex items-center gap-2"
              >
                {isLoading ? 'Analyzing...' : 'Get Diagnosis'}
              </Button>
            ) : (
              <Button
                onClick={handleNext}
                disabled={isLoading}
                className="flex items-center gap-2"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            )}
          </div>

          <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-6">
            Fill in all required fields to proceed
          </p>
        </div>
      </div>
    </Container>
  );
}
