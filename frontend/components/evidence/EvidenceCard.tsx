/**
 * Individual evidence citation card
 */

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Evidence } from '@/lib/types';
import { formatSourceId, formatRelevance } from '@/lib/utils/formatting';
import { getEvidenceTypeColors, getEvidenceTypeLabel } from '@/lib/utils/colors';
import { FileText } from 'lucide-react';

interface EvidenceCardProps {
  evidence: Evidence;
}

export default function EvidenceCard({ evidence }: EvidenceCardProps) {
  const { source, type, text, relevance_score } = evidence;

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="space-y-3">
          {/* Header with source and type */}
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-900">
                {formatSourceId(source)}
              </span>
            </div>
            <Badge variant="outline" className={getEvidenceTypeColors(type)}>
              {getEvidenceTypeLabel(type)}
            </Badge>
          </div>

          {/* Text excerpt */}
          <p className="text-sm text-gray-700 leading-relaxed">
            {text}
          </p>

          {/* Relevance score */}
          <div className="flex items-center justify-between pt-2 border-t">
            <span className="text-xs text-gray-500">Relevance</span>
            <div className="flex items-center gap-2">
              <div className="w-24 bg-gray-200 rounded-full h-1.5">
                <div
                  className="bg-blue-600 h-1.5 rounded-full"
                  style={{ width: `${relevance_score * 100}%` }}
                />
              </div>
              <span className="text-xs font-medium text-gray-700">
                {formatRelevance(relevance_score)}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
