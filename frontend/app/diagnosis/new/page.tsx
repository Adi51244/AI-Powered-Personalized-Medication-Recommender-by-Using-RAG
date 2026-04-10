'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/context';
import PatientInputForm from '@/components/patient/EnhancedPatientInputForm';
import { PatientInput } from '@/lib/types';
import { appendDiagnosisToHistory } from '@/lib/diagnosis/history';
import { toastMessages } from '@/lib/utils/toast-messages';

export default function NewDiagnosisPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (loading) {
    return null;
  }

  if (!user) {
    return null;
  }

  const handleSubmit = async (data: PatientInput) => {
    setIsSubmitting(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      console.log('Submitting diagnosis with data:', data);

      const response = await fetch(`${apiUrl}/api/v1/diagnoses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: data.age,
          gender: data.gender === 'male' ? 'M' : data.gender === 'female' ? 'F' : 'O',
          symptoms: data.symptoms.map((s) => ({
            name: s.name,
            severity: s.severity || 5,
            duration_days: 3, // Default to 3 days if not provided
          })),
          chronic_conditions: data.chronic_conditions,
          current_medications: data.current_medications,
          allergies: data.allergies,
        }),
      });

      console.log('API Response Status:', response.status);

      if (!response.ok) {
        const text = await response.text();
        console.error('API Error:', text);
        throw new Error(text || `API returned ${response.status}`);
      }

      const result = await response.json();
      console.log('Diagnosis Result:', result);

      // Cache the exact response so the results page can always render,
      // even if backend retrieval endpoint is unavailable.
      localStorage.setItem(`diagnosis_${result.diagnosis_id}`, JSON.stringify(result));
      appendDiagnosisToHistory(user.id, result, data);

      // Redirect to results page with the diagnosis ID
      router.push(`/diagnosis/${result.diagnosis_id}`);
    } catch (error) {
      console.error('Error submitting diagnosis:', error);
      const errorMessage = error instanceof Error ? error.message : 'Diagnosis failed';
      toastMessages.diagnosisError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return <PatientInputForm onSubmit={handleSubmit} isLoading={isSubmitting} />;
}
