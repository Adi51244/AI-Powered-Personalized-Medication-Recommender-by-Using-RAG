'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, CheckCircle, Info, Lightbulb } from 'lucide-react';

interface MedicationExplained {
  name: string;
  dosage: string;
  purpose: string;
  how_it_works?: string;
  side_effects?: string;
  safety: string;
}

interface SimpleExplanationProps {
  problem: string;
  cause: string;
  why_our_system_recommended_this: string;
  what_you_should_do: string;
  medications_explained: MedicationExplained[];
  risk_factors_explained: string[];
  when_to_seek_help: string[];
  confidence_level: string;
}

export default function SimpleExplanationComponent(props: SimpleExplanationProps) {
  const formatText = (text: string) => {
    return text.split('\n').map((line, i) => <div key={i}>{line}</div>);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Confidence Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center gap-2">
          <CheckCircle className="h-5 w-5 text-blue-600" />
          <div>
            <p className="font-semibold text-blue-900">System Confidence</p>
            <p className="text-sm text-blue-800">{props.confidence_level}</p>
          </div>
        </div>
      </div>

      {/* What's the Problem? */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-blue-600" />
            What's the Problem?
          </CardTitle>
          <CardDescription>Your diagnosis in simple terms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <p className="text-gray-900 leading-relaxed">{props.problem}</p>
          </div>
        </CardContent>
      </Card>

      {/* Why These Symptoms? */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-amber-600" />
            Why These Symptoms?
          </CardTitle>
          <CardDescription>How these symptoms indicate your condition</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
            <p className="text-gray-900 leading-relaxed">{props.cause}</p>
          </div>
        </CardContent>
      </Card>

      {/* How Our AI Made This Recommendation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            How Our AI Made This Recommendation
          </CardTitle>
          <CardDescription>Our reasoning process</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <p className="text-gray-900 leading-relaxed">{props.why_our_system_recommended_this}</p>
          </div>
        </CardContent>
      </Card>

      {/* Medications Explained */}
      {props.medications_explained.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Your Medications Explained</CardTitle>
            <CardDescription>What each medication does and how to take it</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {props.medications_explained.map((med, idx) => (
                <div key={idx} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-semibold text-lg">{med.name}</p>
                      <p className="text-sm text-gray-600">Dosage: {med.dosage}</p>
                    </div>
                    <Badge variant="secondary">{med.safety}</Badge>
                  </div>

                  <div className="space-y-3 mt-3">
                    <div>
                      <p className="text-sm font-medium text-gray-700">What it does:</p>
                      <p className="text-sm text-gray-600">{med.purpose}</p>
                    </div>

                    {med.how_it_works && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">How it works:</p>
                        <p className="text-sm text-gray-600">{med.how_it_works}</p>
                      </div>
                    )}

                    {med.side_effects && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">Side effects:</p>
                        <p className="text-sm text-gray-600">{med.side_effects}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* What You Should Do */}
      <Card>
        <CardHeader>
          <CardTitle>What You Should Do</CardTitle>
          <CardDescription>Action plan for recovery</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-line">
            <p className="text-gray-900 leading-relaxed font-mono text-sm">
              {formatText(props.what_you_should_do)}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Risk Factors */}
      {props.risk_factors_explained.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Things That Increase Your Risk</CardTitle>
            <CardDescription>Factors that contribute to this condition</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {props.risk_factors_explained.map((factor, idx) => (
                <div key={idx} className="flex items-start gap-2 p-2 rounded bg-orange-50">
                  <span className="text-orange-600 mt-1">•</span>
                  <p className="text-sm text-gray-700">{factor}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Emergency Warning Signs */}
      {props.when_to_seek_help.length > 0 && (
        <Alert className="border-red-300 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-900">
            <p className="font-semibold mb-2">⚠️ Seek Emergency Help If:</p>
            <ul className="space-y-1">
              {props.when_to_seek_help.map((sign, idx) => (
                <li key={idx} className="text-sm">
                  • {sign.replace('🚨 ', '')}
                </li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Disclaimer */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <p className="font-semibold mb-1">⚕️ Important Note</p>
          <p className="text-sm">
            This AI-generated diagnosis is for educational purposes. Always consult with a healthcare professional
            for proper diagnosis and treatment. This information should not replace professional medical advice.
          </p>
        </AlertDescription>
      </Alert>
    </div>
  );
}
