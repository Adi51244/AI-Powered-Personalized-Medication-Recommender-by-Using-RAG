/**
 * Explanation panel with SHAP visualization and summary
 */

'use client';

import { ExplanationResponse } from '@/lib/types';
import { formatDiseaseName, formatConfidence } from '@/lib/utils/formatting';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import ShapChart from './ShapChart';
import { Brain, TrendingUp } from 'lucide-react';
import EmptyState from '@/components/common/EmptyState';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ExplanationPanelProps {
  explanation: ExplanationResponse | null;
  isLoading?: boolean;
}

export default function ExplanationPanel({ explanation, isLoading }: ExplanationPanelProps) {
  if (isLoading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Loading explanation...</p>
      </div>
    );
  }

  if (!explanation) {
    return (
      <EmptyState
        title="No explanation available"
        description="Explanation data could not be loaded for this diagnosis."
        icon={<Brain className="h-12 w-12 text-gray-400" />}
      />
    );
  }

  const { predicted_disease, predicted_confidence, method, summary, shap_values, top_features } = explanation;

  return (
    <div className="space-y-6">
      {method === 'fallback' && (
        <Alert>
          <AlertDescription>
            Detailed SHAP/LIME analysis timed out, so this explanation shows a faster importance-based summary.
          </AlertDescription>
        </Alert>
      )}

      {/* Prediction Summary */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-xl">
                {formatDiseaseName(predicted_disease)}
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Confidence: <span className="font-semibold text-blue-600">{formatConfidence(predicted_confidence)}</span>
              </p>
            </div>
            <Badge variant="outline" className="capitalize">
              {method} method
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-700 leading-relaxed">
            {summary}
          </p>
        </CardContent>
      </Card>

      {/* SHAP Feature Importance Chart */}
      {shap_values.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Feature Importance
            </CardTitle>
            <p className="text-sm text-gray-600">
              Top {Math.min(shap_values.length, 10)} features contributing to the prediction
            </p>
          </CardHeader>
          <CardContent>
            <ShapChart shapValues={shap_values} topK={10} />
          </CardContent>
        </Card>
      )}

      {/* Top Features List */}
      {top_features.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Key Contributing Features</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="list-decimal list-inside space-y-2">
              {top_features.map((feature, index) => (
                <li key={index} className="text-sm text-gray-700">
                  {feature}
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      )}

      {/* Method info */}
      <div className="text-xs text-gray-500 text-center">
        <p>
          Explanation generated using <span className="font-medium uppercase">{method}</span> explainability method
        </p>
      </div>
    </div>
  );
}
