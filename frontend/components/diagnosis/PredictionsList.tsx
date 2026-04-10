/**
 * List of disease predictions
 */

import { DiseasePrediction } from '@/lib/types';
import PredictionCard from './PredictionCard';
import EmptyState from '@/components/common/EmptyState';
import { Activity } from 'lucide-react';

interface PredictionsListProps {
  predictions: DiseasePrediction[];
}

export default function PredictionsList({ predictions }: PredictionsListProps) {
  if (predictions.length === 0) {
    return (
      <EmptyState
        title="No predictions available"
        description="No disease predictions were generated for this patient."
        icon={<Activity className="h-12 w-12 text-gray-400" />}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-600">
          Showing top {predictions.length} disease prediction{predictions.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="space-y-3">
        {predictions.map((prediction, index) => (
          <PredictionCard
            key={`${prediction.disease}-${index}`}
            prediction={prediction}
            rank={index + 1}
          />
        ))}
      </div>
    </div>
  );
}
