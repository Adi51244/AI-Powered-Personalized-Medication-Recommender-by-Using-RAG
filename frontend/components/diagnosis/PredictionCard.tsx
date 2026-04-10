/**
 * Individual disease prediction card
 */

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DiseasePrediction } from '@/lib/types';
import { formatDiseaseName, formatConfidence } from '@/lib/utils/formatting';
import { getConfidenceColor, getConfidenceBg } from '@/styles/themes';
import { cn } from '@/lib/utils/cn';
import { Brain, Database } from 'lucide-react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

interface PredictionCardProps {
  prediction: DiseasePrediction;
  rank: number;
}

export default function PredictionCard({ prediction, rank }: PredictionCardProps) {
  const { disease, confidence, source, explanation } = prediction;
  const confidencePercent = confidence * 100;

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium text-gray-500">#{rank}</span>
              <h4 className="text-lg font-semibold text-gray-900">
                {formatDiseaseName(disease)}
              </h4>
            </div>

            {/* Confidence bar */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Confidence</span>
                <span className={cn('font-semibold', getConfidenceColor(confidence))}>
                  {formatConfidence(confidence)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className={cn('h-2.5 rounded-full transition-all', getConfidenceBg(confidence))}
                  style={{ width: `${confidencePercent}%` }}
                />
              </div>
            </div>
          </div>

          {/* Source badge */}
          <Badge
            variant="outline"
            className="ml-4 flex items-center gap-1.5"
          >
            {source === 'ml_model' ? (
              <>
                <Brain className="h-3.5 w-3.5" />
                ML Model
              </>
            ) : (
              <>
                <Database className="h-3.5 w-3.5" />
                RAG Retrieval
              </>
            )}
          </Badge>
        </div>
      </CardHeader>

      {explanation && (
        <CardContent className="pt-0">
          <Accordion type="single" collapsible>
            <AccordionItem value="explanation" className="border-none">
              <AccordionTrigger className="text-sm text-blue-600 hover:text-blue-700 py-2">
                View explanation
              </AccordionTrigger>
              <AccordionContent>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {explanation}
                </p>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      )}
    </Card>
  );
}
