/**
 * Evidence explorer with filtering and grouping
 */

import { Evidence } from '@/lib/types';
import EvidenceCard from './EvidenceCard';
import EmptyState from '@/components/common/EmptyState';
import { FileText } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface EvidenceExplorerProps {
  evidence: Evidence[];
}

export default function EvidenceExplorer({ evidence }: EvidenceExplorerProps) {
  if (evidence.length === 0) {
    return (
      <EmptyState
        title="No evidence available"
        description="No evidence citations were retrieved for this diagnosis."
        icon={<FileText className="h-12 w-12 text-gray-400" />}
      />
    );
  }

  // Group evidence by type
  const clinicalCases = evidence.filter(e => e.type === 'clinical_case');
  const drugProfiles = evidence.filter(e => e.type === 'drug_profile');
  const guidelines = evidence.filter(e => e.type === 'clinical_guideline');

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          <span className="font-medium">{evidence.length} evidence citation{evidence.length !== 1 ? 's' : ''}</span>
          {clinicalCases.length > 0 && <> &bull; {clinicalCases.length} clinical case{clinicalCases.length !== 1 ? 's' : ''}</>}
          {drugProfiles.length > 0 && <> &bull; {drugProfiles.length} drug profile{drugProfiles.length !== 1 ? 's' : ''}</>}
          {guidelines.length > 0 && <> &bull; {guidelines.length} guideline{guidelines.length !== 1 ? 's' : ''}</>}
        </p>
      </div>

      {/* Tabbed view by evidence type */}
      <Tabs defaultValue="all" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">All ({evidence.length})</TabsTrigger>
          <TabsTrigger value="cases">Cases ({clinicalCases.length})</TabsTrigger>
          <TabsTrigger value="drugs">Drugs ({drugProfiles.length})</TabsTrigger>
          <TabsTrigger value="guidelines">Guidelines ({guidelines.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-3 mt-4">
          {evidence.map((ev, index) => (
            <EvidenceCard key={`${ev.source}-${index}`} evidence={ev} />
          ))}
        </TabsContent>

        <TabsContent value="cases" className="space-y-3 mt-4">
          {clinicalCases.length > 0 ? (
            clinicalCases.map((ev, index) => (
              <EvidenceCard key={`${ev.source}-${index}`} evidence={ev} />
            ))
          ) : (
            <EmptyState title="No clinical cases" description="No clinical case evidence was found." />
          )}
        </TabsContent>

        <TabsContent value="drugs" className="space-y-3 mt-4">
          {drugProfiles.length > 0 ? (
            drugProfiles.map((ev, index) => (
              <EvidenceCard key={`${ev.source}-${index}`} evidence={ev} />
            ))
          ) : (
            <EmptyState title="No drug profiles" description="No drug profile evidence was found." />
          )}
        </TabsContent>

        <TabsContent value="guidelines" className="space-y-3 mt-4">
          {guidelines.length > 0 ? (
            guidelines.map((ev, index) => (
              <EvidenceCard key={`${ev.source}-${index}`} evidence={ev} />
            ))
          ) : (
            <EmptyState title="No guidelines" description="No clinical guideline evidence was found." />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
