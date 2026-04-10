'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertCircle, MessageCircle } from 'lucide-react'

interface ExplanationPanelProps {
  diagnosis: string
  explanation: string
  medications?: string[]
  evidenceSources?: any[]
}

export function ImprovedExplanationPanel({
  diagnosis,
  explanation,
  medications = [],
  evidenceSources = [],
}: ExplanationPanelProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="space-y-4">
      {/* Simple Diagnosis Explanation */}
      <Card className="border-l-4 border-l-blue-500 bg-blue-50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <MessageCircle className="w-5 h-5" />
            What Does This Mean?
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-sm leading-relaxed">
            <p className="font-medium text-gray-900 mb-2">{diagnosis}</p>
            <p className="text-gray-700">
              {explanation || 'Understanding your condition helps you manage it better.'}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Medications Explanation */}
      {medications && medications.length > 0 && (
        <Card className="border-l-4 border-l-green-500 bg-green-50">
          <CardHeader>
            <CardTitle className="text-lg">Your Medications</CardTitle>
            <CardDescription>What you're taking and why</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {medications.map((med, idx) => (
                <div key={idx} className="text-sm p-3 bg-white rounded border">
                  <p className="font-medium">{med}</p>
                  <p className="text-gray-600 text-xs mt-1">
                    This medicine helps your body heal and manage your condition.
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Important Information */}
      <Card className="border-l-4 border-l-amber-500 bg-amber-50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Important to Remember
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="text-sm space-y-2 list-disc list-inside text-gray-700">
            <li>Take medications exactly as prescribed</li>
            <li>Write down any side effects you experience</li>
            <li>Follow up with your doctor as scheduled</li>
            <li>Make the lifestyle changes recommended</li>
            <li>Call your doctor if symptoms get worse</li>
          </ul>
        </CardContent>
      </Card>

      {/* Research & Evidence */}
      {evidenceSources && evidenceSources.length > 0 && (
        <Card className="border-l-4 border-l-purple-500">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-lg">Where This Information Comes From</CardTitle>
                <CardDescription>Research and medical guidelines</CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setExpanded(!expanded)}
              >
                {expanded ? 'Hide' : 'Show'} Details
              </Button>
            </div>
          </CardHeader>
          {expanded && (
            <CardContent>
              <div className="space-y-2 text-sm">
                {evidenceSources.slice(0, 3).map((source, idx) => (
                  <div key={idx} className="p-2 bg-gray-50 rounded text-gray-600">
                    <p className="font-medium">{source.title}</p>
                    <p className="text-xs">{source.source}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          )}
        </Card>
      )}
    </div>
  )
}
