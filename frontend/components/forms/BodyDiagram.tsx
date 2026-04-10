'use client';

import * as React from 'react';
import { useState } from 'react';
import { cn } from '@/lib/utils/cn';

interface BodyPart {
  id: string;
  name: string;
  x: number;
  y: number;
  radius: number;
}

interface BodyDiagramProps {
  selectedParts: string[];
  onTogglePart: (partId: string) => void;
}

const BODY_PARTS: BodyPart[] = [
  { id: 'head', name: 'Head', x: 200, y: 80, radius: 30 },
  { id: 'chest', name: 'Chest', x: 200, y: 150, radius: 40 },
  { id: 'abdomen', name: 'Abdomen', x: 200, y: 220, radius: 35 },
  { id: 'left-arm', name: 'Left Arm', x: 140, y: 170, radius: 20 },
  { id: 'right-arm', name: 'Right Arm', x: 260, y: 170, radius: 20 },
  { id: 'left-leg', name: 'Left Leg', x: 185, y: 310, radius: 25 },
  { id: 'right-leg', name: 'Right Leg', x: 215, y: 310, radius: 25 },
];

/**
 * BodyDiagram Component
 *
 * Interactive SVG body diagram for symptom location selection.
 */
export function BodyDiagram({
  selectedParts,
  onTogglePart,
}: BodyDiagramProps) {
  const [hoveredPart, setHoveredPart] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      <label className="block font-medium text-gray-900 dark:text-white">
        Symptom Location (optional)
      </label>

      <div className="flex items-center justify-center p-6 rounded-lg border border-gray-300 dark:border-gray-600 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900">
        <svg
          viewBox="0 0 400 400"
          className="w-full max-w-xs h-auto"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Draw stylized body outline */}
          <g strokeWidth="2" fill="none">
            {/* Head */}
            <circle
              cx="200"
              cy="80"
              r="30"
              className="stroke-gray-400 dark:stroke-gray-500"
            />
            {/* Body */}
            <line
              x1="200"
              y1="110"
              x2="200"
              y2="250"
              className="stroke-gray-400 dark:stroke-gray-500"
            />
            {/* Left arm */}
            <line
              x1="200"
              y1="140"
              x2="140"
              y2="170"
              className="stroke-gray-400 dark:stroke-gray-500"
            />
            {/* Right arm */}
            <line
              x1="200"
              y1="140"
              x2="260"
              y2="170"
              className="stroke-gray-400 dark:stroke-gray-500"
            />
            {/* Left leg */}
            <line
              x1="200"
              y1="250"
              x2="185"
              y2="330"
              className="stroke-gray-400 dark:stroke-gray-500"
            />
            {/* Right leg */}
            <line
              x1="200"
              y1="250"
              x2="215"
              y2="330"
              className="stroke-gray-400 dark:stroke-gray-500"
            />
          </g>

          {/* Interactive body parts */}
          {BODY_PARTS.map((part) => (
            <g key={part.id}>
              <circle
                cx={part.x}
                cy={part.y}
                r={part.radius}
                fill={
                  selectedParts.includes(part.id)
                    ? '#3b82f6'
                    : hoveredPart === part.id
                    ? '#93c5fd'
                    : 'rgba(59, 130, 246, 0.1)'
                }
                stroke={selectedParts.includes(part.id) ? '#1e40af' : '#60a5fa'}
                strokeWidth="2"
                opacity={hoveredPart === part.id || selectedParts.includes(part.id) ? 1 : 0.5}
                className="cursor-pointer transition-all"
                onClick={() => onTogglePart(part.id)}
                onMouseEnter={() => setHoveredPart(part.id)}
                onMouseLeave={() => setHoveredPart(null)}
              />
              {/* Label */}
              <text
                x={part.x}
                y={part.y}
                textAnchor="middle"
                dominantBaseline="middle"
                className="text-xs font-medium fill-gray-800 dark:fill-gray-200 pointer-events-none"
              >
                {part.name.split(' ')[0]}
              </text>
            </g>
          ))}
        </svg>
      </div>

      {/* Selected parts display */}
      {selectedParts.length > 0 && (
        <div className="mt-4 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
          <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">
            Selected Areas:
          </p>
          <div className="flex flex-wrap gap-2">
            {selectedParts.map((partId) => {
              const part = BODY_PARTS.find((p) => p.id === partId);
              return (
                <span
                  key={partId}
                  className="inline-flex items-center px-3 py-1 rounded-full bg-blue-200 dark:bg-blue-800 text-blue-900 dark:text-blue-100 text-xs font-medium"
                >
                  {part?.name}
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
