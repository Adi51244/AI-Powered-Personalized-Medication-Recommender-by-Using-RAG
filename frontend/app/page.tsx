/**
 * Main MediRAG application page
 */

'use client';

import { useState } from 'react';
import { PatientInput, DiagnosisResponse, ExplanationResponse } from '@/lib/types';
import { createDiagnosis, getExplanation } from '@/lib/api';
import EnhancedPatientInputForm from '@/components/patient/EnhancedPatientInputForm';
import DiagnosisResults from '@/components/diagnosis/DiagnosisResults';
import { DiagnosisResultsSkeleton } from '@/components/diagnosis/DiagnosisResultsSkeleton';
import ErrorDisplay from '@/components/common/ErrorDisplay';
import Container from '@/components/layout/Container';
import { toastMessages } from '@/lib/utils/toast-messages';
import { useAuth } from '@/lib/auth/context';
import { appendDiagnosisToHistory } from '@/lib/diagnosis/history';

export default function Home() {
  const { user } = useAuth();
  const [diagnosisData, setDiagnosisData] = useState<DiagnosisResponse | null>(null);
  const [explanationData, setExplanationData] = useState<ExplanationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingExplanation, setIsLoadingExplanation] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleDiagnosisSubmit = async (patientData: PatientInput) => {
    setIsLoading(true);
    setError(null);
    setDiagnosisData(null);
    setExplanationData(null);

    // Show processing toast
    toastMessages.diagnosisProcessing();

    try {
      // Step 1: Get diagnosis
      console.log('Submitting diagnosis request...', patientData);
      const diagnosis = await createDiagnosis(patientData);
      console.log('Diagnosis received:', diagnosis);
      setDiagnosisData(diagnosis);

      if (user?.id) {
        appendDiagnosisToHistory(user.id, diagnosis, patientData);
      }

      // Show success toast
      toastMessages.diagnosisSuccess();

      // Show safety warnings if any
      const warningCount = diagnosis.recommendations?.filter(
        m => m.safety_status === 'warning' || m.safety_status === 'contraindicated'
      ).length || 0;

      if (warningCount > 0) {
        toastMessages.safetyWarning(warningCount);
      }

      // Step 2: Get explanation (in parallel, non-blocking)
      setIsLoadingExplanation(true);
      try {
        console.log('Requesting explanation (SHAP/LIME computation may take 30-60s)...');
        const explanation = await getExplanation({
          patient: patientData,
          top_k_features: 10
        });
        console.log('Explanation received:', explanation);
        setExplanationData(explanation);
        toastMessages.success('Explanation generated successfully');
      } catch (expError) {
        console.warn('Failed to load explanation:', expError);
        const errorMessage = expError instanceof Error ? expError.message : 'Failed to generate explanation';
        // Show warning toast but don't block the main flow
        toastMessages.warning(`Explanation unavailable: ${errorMessage}`);
      } finally {
        setIsLoadingExplanation(false);
      }
    } catch (err) {
      console.error('Diagnosis error:', err);
      const error = err instanceof Error ? err : new Error('Unknown error occurred');
      setError(error);

      // Show error toast
      toastMessages.diagnosisError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewDiagnosis = () => {
    setDiagnosisData(null);
    setExplanationData(null);
    setError(null);
  };

  const handleRetry = () => {
    setError(null);
  };

  return (
    <Container>
      {/* Loading state - Show skeleton instead of spinner */}
      {isLoading && (
        <div className="max-w-7xl mx-auto">
          <DiagnosisResultsSkeleton />
        </div>
      )}

      {/* Error display */}
      {error && !isLoading && (
        <div className="mb-8">
          <ErrorDisplay
            error={error}
            onRetry={handleRetry}
            showDetails={true}
          />
        </div>
      )}

      {/* Patient Input Form (show when no diagnosis data) */}
      {!diagnosisData && !isLoading && (
        <EnhancedPatientInputForm
          onSubmit={handleDiagnosisSubmit}
          isLoading={isLoading}
        />
      )}

      {/* Diagnosis Results (show after successful diagnosis) */}
      {diagnosisData && !isLoading && (
        <DiagnosisResults
          diagnosis={diagnosisData}
          explanation={explanationData}
          onNewDiagnosis={handleNewDiagnosis}
          isLoadingExplanation={isLoadingExplanation}
        />
      )}
    </Container>
  );
}
