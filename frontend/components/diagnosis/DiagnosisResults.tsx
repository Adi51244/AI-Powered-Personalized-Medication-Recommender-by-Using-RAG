/**
 * Main diagnosis results orchestrator with tabs
 */

'use client';

import { DiagnosisResponse, ExplanationResponse } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils/formatting';
import { Activity, Pill, FileText, Brain, RotateCcw } from 'lucide-react';
import PredictionsList from './PredictionsList';
import MedicationsList from '../medications/MedicationsList';
import SafetyAlerts from '../safety/SafetyAlerts';
import EvidenceExplorer from '../evidence/EvidenceExplorer';
import ExplanationPanel from '../explainability/ExplanationPanel';
import { TABS } from '@/lib/utils/constants';

interface DiagnosisResultsProps {
  diagnosis: DiagnosisResponse;
  explanation?: ExplanationResponse | null;
  onNewDiagnosis: () => void;
  isLoadingExplanation?: boolean;
}

export default function DiagnosisResults({
  diagnosis,
  explanation,
  onNewDiagnosis,
  isLoadingExplanation = false
}: DiagnosisResultsProps) {
  const { diagnosis_id, predictions = [], recommendations = [], evidence = [] } = diagnosis;

  // Extract all safety warnings from recommendations
  const allWarnings = (recommendations || []).flatMap(rec =>
    rec.warnings.map(warning => ({
      type: 'drug_interaction' as const,
      severity: rec.safety_status === 'contraindicated' ? 'major' as const : 'moderate' as const,
      message: warning,
      drugs: [rec.name]
    }))
  );

  // Count by type
  const safeCount = recommendations.filter(r => r.safety_status === 'safe').length;
  const warningCount = recommendations.filter(r => r.safety_status === 'warning').length;
  const contraindicatedCount = recommendations.filter(r => r.safety_status === 'contraindicated').length;

  return (
    <div className="space-y-6">
      {/* Header with diagnosis ID and actions */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">Diagnosis Results</CardTitle>
              <div className="mt-2 space-y-1">
                <p className="font-mono text-xs text-gray-600">ID: {diagnosis_id}</p>
                <p className="text-xs text-gray-600">Generated: {formatDate(new Date())}</p>
              </div>
            </div>
            <Button onClick={onNewDiagnosis} variant="outline">
              <RotateCcw className="mr-2 h-4 w-4" />
              New Diagnosis
            </Button>
          </div>
        </CardHeader>

        {/* Quick summary */}
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
              <Activity className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-2xl font-bold text-blue-900">{predictions.length}</p>
                <p className="text-xs text-blue-700">Predictions</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
              <Pill className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-2xl font-bold text-purple-900">{recommendations.length}</p>
                <p className="text-xs text-purple-700">Medications</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
              <FileText className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-2xl font-bold text-green-900">{evidence.length}</p>
                <p className="text-xs text-green-700">Evidence</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-amber-50 rounded-lg">
              <Brain className="h-8 w-8 text-amber-600" />
              <div>
                <p className="text-2xl font-bold text-amber-900">{allWarnings.length}</p>
                <p className="text-xs text-amber-700">Warnings</p>
              </div>
            </div>
          </div>

          {/* Safety summary badges */}
          {recommendations.length > 0 && (
            <div className="flex items-center gap-2 mt-4 pt-4 border-t">
              <span className="text-sm text-gray-600">Safety Status:</span>
              {safeCount > 0 && (
                <Badge variant="outline" className="bg-green-50">
                  {safeCount} Safe
                </Badge>
              )}
              {warningCount > 0 && (
                <Badge variant="outline" className="bg-amber-50">
                  {warningCount} Warnings
                </Badge>
              )}
              {contraindicatedCount > 0 && (
                <Badge variant="outline" className="bg-red-50">
                  {contraindicatedCount} Contraindicated
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabbed content */}
      <Tabs defaultValue={TABS.PREDICTIONS} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value={TABS.PREDICTIONS} className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            <span className="hidden sm:inline">Predictions</span>
          </TabsTrigger>
          <TabsTrigger value={TABS.MEDICATIONS} className="flex items-center gap-2">
            <Pill className="h-4 w-4" />
            <span className="hidden sm:inline">Medications</span>
          </TabsTrigger>
          <TabsTrigger value={TABS.EVIDENCE} className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            <span className="hidden sm:inline">Evidence</span>
          </TabsTrigger>
          <TabsTrigger value={TABS.EXPLANATION} className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            <span className="hidden sm:inline">Explanation</span>
          </TabsTrigger>
        </TabsList>

        {/* Predictions Tab */}
        <TabsContent value={TABS.PREDICTIONS} className="mt-6">
          <PredictionsList predictions={predictions} />
        </TabsContent>

        {/* Medications Tab */}
        <TabsContent value={TABS.MEDICATIONS} className="mt-6 space-y-6">
          {allWarnings.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Safety Warnings</h3>
              <SafetyAlerts warnings={allWarnings} />
            </div>
          )}
          <div>
            <h3 className="text-lg font-semibold mb-4">Recommended Medications</h3>
            <MedicationsList medications={recommendations} />
          </div>
        </TabsContent>

        {/* Evidence Tab */}
        <TabsContent value={TABS.EVIDENCE} className="mt-6">
          <EvidenceExplorer evidence={evidence} />
        </TabsContent>

        {/* Explanation Tab */}
        <TabsContent value={TABS.EXPLANATION} className="mt-6">
          <ExplanationPanel explanation={explanation || null} isLoading={isLoadingExplanation} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
