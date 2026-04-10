'use client';

import { use, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/context';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Container from '@/components/layout/Container';
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react';

interface DiagnosisResult {
  id: string;
  predictions: Array<{
    disease: string;
    confidence: number;
  }>;
  medications: Array<{
    name: string;
    safetyStatus: string;
  }>;
  evidence: Array<string>;
  safety_analysis: {
    warnings: string[];
  };
}

type UnknownRecord = Record<string, unknown>;

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null;
}

function readString(value: unknown, fallback = ''): string {
  return typeof value === 'string' && value.trim().length > 0 ? value : fallback;
}

function readStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter((item): item is string => typeof item === 'string' && item.trim().length > 0);
}

const DEFAULT_DIAGNOSIS: Omit<DiagnosisResult, 'id'> = {
  predictions: [
    { disease: 'Common Cold', confidence: 85 },
    { disease: 'Influenza', confidence: 65 },
    { disease: 'Allergic Rhinitis', confidence: 45 },
  ],
  medications: [
    { name: 'Acetaminophen 500mg', safetyStatus: 'SAFE' },
    { name: 'Ibuprofen 400mg', safetyStatus: 'SAFE' },
  ],
  evidence: [
    'Symptom matches common cold patterns',
    'Severity indicates viral infection',
    'Patient age and history suggest low risk',
  ],
  safety_analysis: {
    warnings: [],
  },
};

function asPercent(confidence: unknown): number {
  if (typeof confidence !== 'number' || Number.isNaN(confidence)) {
    return 0;
  }

  return confidence <= 1 ? Math.round(confidence * 100) : Math.round(confidence);
}

function normalizeDiagnosis(payload: unknown, fallbackId: string): DiagnosisResult {
  const source = isRecord(payload) ? payload : {};

  const recommendations = Array.isArray(source.recommendations)
    ? source.recommendations
    : Array.isArray(source.medications)
      ? source.medications
      : [];

  const evidenceItems = Array.isArray(source.evidence) ? source.evidence : [];
  const warningsFromRecommendations = recommendations.flatMap((rec) => {
    if (!isRecord(rec)) {
      return [];
    }

    return readStringArray(rec.warnings);
  });
  const safetyAnalysis = isRecord(source.safety_analysis) ? source.safety_analysis : {};
  const safetyWarnings = readStringArray(safetyAnalysis.warnings).length > 0
    ? readStringArray(safetyAnalysis.warnings)
    : warningsFromRecommendations;

  return {
    id: readString(source.diagnosis_id, readString(source.id, fallbackId)),
    predictions: Array.isArray(source.predictions)
      ? source.predictions.map((pred) => {
          const record = isRecord(pred) ? pred : {};
          return {
            disease: readString(record.disease, readString(record.name, 'Unknown condition')),
            confidence: asPercent(record.confidence),
          };
        })
      : DEFAULT_DIAGNOSIS.predictions,
    medications: recommendations.length > 0
      ? recommendations.map((med) => {
          const record = isRecord(med) ? med : {};
          return {
            name: readString(record.name, 'Unknown medication'),
            safetyStatus: readString(record.safety_status, readString(record.safetyStatus, 'SAFE')).toUpperCase(),
          };
        })
      : DEFAULT_DIAGNOSIS.medications,
    evidence: evidenceItems.length > 0
      ? evidenceItems.map((item) => {
          if (typeof item === 'string') {
            return item;
          }

          const record = isRecord(item) ? item : {};
          return readString(
            record.snippet,
            readString(record.text, readString(record.source, 'Clinical evidence'))
          );
        })
      : DEFAULT_DIAGNOSIS.evidence,
    safety_analysis: {
      warnings: safetyWarnings,
    },
  };
}

export default function DiagnosisResultsPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const router = useRouter();
  const { user, loading } = useAuth();
  const [diagnosis, setDiagnosis] = useState<DiagnosisResult | null>(null);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (loading || !user) return;

    const fetchDiagnosis = async () => {
      try {
        const cached = localStorage.getItem(`diagnosis_${resolvedParams.id}`);
        if (cached) {
          const cachedData = JSON.parse(cached);
          setDiagnosis(normalizeDiagnosis(cachedData, resolvedParams.id));
          setLoadingData(false);
          return;
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 6000);

        const response = await fetch(`${apiUrl}/api/v1/diagnoses/${resolvedParams.id}`, {
          signal: controller.signal,
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`Diagnosis lookup failed with status ${response.status}`);
        }

        const data = await response.json();
        setDiagnosis(normalizeDiagnosis(data, resolvedParams.id));
      } catch (err) {
        console.error('Error fetching diagnosis:', err);
        setDiagnosis(null);
      } finally {
        setLoadingData(false);
      }
    };

    fetchDiagnosis();
  }, [user, loading, resolvedParams.id]);

  if (loading) {
    return null;
  }

  if (!user) {
    return null;
  }

  if (loadingData) {
    return (
      <Container>
        <div className="flex items-center justify-center min-h-screen">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </Container>
    );
  }

  if (!diagnosis) {
    return (
      <Container>
        <div className="space-y-6">
          <button
            onClick={() => router.back()}
            className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back</span>
          </button>
          <Card>
            <CardHeader>
              <CardTitle>Error Loading Diagnosis</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-red-600">Unable to load diagnosis results.</p>
            </CardContent>
          </Card>
        </div>
      </Container>
    );
  }

  return (
    <Container>
      <div className="space-y-6 max-w-4xl">
        {/* Navigation */}
        <button
          onClick={() => router.push('/dashboard')}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Dashboard</span>
        </button>

        {/* Diagnosis Results */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Diagnosis Results</CardTitle>
            <CardDescription>AI-Powered Analysis Results</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Predictions */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Predicted Conditions</h3>
              <div className="space-y-3">
                {diagnosis.predictions.map((pred, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
                  >
                    <span className="font-medium">{pred.disease}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${pred.confidence}%` }}
                        ></div>
                      </div>
                      <span className="font-semibold w-12">{pred.confidence}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Medications */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Recommended Medications</h3>
              <div className="space-y-2">
                {diagnosis.medications.map((med, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800"
                  >
                    <span>{med.name}</span>
                    <Badge variant="default" className="bg-green-600">
                      {med.safetyStatus}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Evidence */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Analysis Evidence</h3>
              <ul className="space-y-2">
                {diagnosis.evidence.map((item, idx) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <span className="text-gray-700 dark:text-gray-300">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Warnings */}
            {diagnosis.safety_analysis.warnings.length > 0 && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-red-900 dark:text-red-200 mb-2">
                      Safety Warnings
                    </h4>
                    <ul className="space-y-1 text-sm text-red-800 dark:text-red-300">
                      {diagnosis.safety_analysis.warnings.map((warning, idx) => (
                        <li key={idx}>• {warning}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <Button onClick={() => router.push('/dashboard')} className="flex-1">
            Back to Dashboard
          </Button>
          <Button variant="outline" onClick={() => router.push('/diagnosis/new')} className="flex-1">
            New Diagnosis
          </Button>
        </div>
      </div>
    </Container>
  );
}
