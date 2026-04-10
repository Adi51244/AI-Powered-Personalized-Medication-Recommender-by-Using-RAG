'use client';

import * as React from 'react';
import { cn } from '@/lib/utils/cn';

interface SeveritySliderProps {
  value: number;
  onChange: (value: number) => void;
  label?: string;
  showEmoji?: boolean;
}

const SEVERITY_LEVELS = [
  { level: 1, emoji: '😊', label: 'Mild' },
  { level: 2, emoji: '😊', label: 'Mild' },
  { level: 3, emoji: '🙂', label: 'Mild' },
  { level: 4, emoji: '😐', label: 'Moderate' },
  { level: 5, emoji: '😐', label: 'Moderate' },
  { level: 6, emoji: '😕', label: 'Moderate' },
  { level: 7, emoji: '😟', label: 'Severe' },
  { level: 8, emoji: '😟', label: 'Severe' },
  { level: 9, emoji: '😰', label: 'Very Severe' },
  { level: 10, emoji: '😱', label: 'Very Severe' },
];

/**
 * SeveritySlider Component
 *
 * Visual severity indicator with emoji feedback (1-10 scale).
 */
export function SeveritySlider({
  value,
  onChange,
  label = 'Severity',
  showEmoji = true,
}: SeveritySliderProps) {
  const current = SEVERITY_LEVELS[value - 1];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="font-medium text-gray-900 dark:text-white">
          {label}
        </label>
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {value} / 10
        </span>
      </div>

      {/* Emoji display */}
      {showEmoji && (
        <div className="text-center">
          <span className="text-5xl">{current.emoji}</span>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            {current.label}
          </p>
        </div>
      )}

      {/* Slider */}
      <input
        type="range"
        min="1"
        max="10"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-3 bg-gradient-to-r from-green-400 via-yellow-400 to-red-500 rounded-lg appearance-none cursor-pointer accent-blue-600"
        style={{
          accentColor: '#3b82f6',
        }}
      />

      {/* Level indicators */}
      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>Mild</span>
        <span>Moderate</span>
        <span>Severe</span>
        <span>Crisis</span>
      </div>
    </div>
  );
}
