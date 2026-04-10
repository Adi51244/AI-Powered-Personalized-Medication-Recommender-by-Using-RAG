'use client';

import * as React from 'react';
import { useState, useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils/cn';

interface Symptom {
  name: string;
  severity: number;
  duration_days: number;
}

interface SymptomAutocompleteProps {
  symptoms: Symptom[];
  onAddSymptom: (symptom: Symptom) => void;
  onRemoveSymptom: (name: string) => void;
  onUpdateSeverity: (name: string, severity: number) => void;
  suggestions?: string[];
}

// Common medical symptoms for autocomplete
const COMMON_SYMPTOMS = [
  'fever',
  'cough',
  'fatigue',
  'headache',
  'shortness of breath',
  'chest pain',
  'abdominal pain',
  'nausea',
  'vomiting',
  'diarrhea',
  'dizziness',
  'muscle pain',
  'joint pain',
  'sore throat',
  'nasal congestion',
  'frequent urination',
  'increased thirst',
  'weight loss',
  'rash',
  'itching',
  'swelling',
  'difficulty sleeping',
  'anxiety',
  'depression',
  'loss of appetite',
];

/**
 * SymptomAutocomplete Component
 *
 * Searchable symptom input with autocomplete suggestions.
 * Allows adding multiple symptoms with duration tracking.
 */
export function SymptomAutocomplete({
  symptoms,
  onAddSymptom,
  onRemoveSymptom,
  onUpdateSeverity,
  suggestions = COMMON_SYMPTOMS,
}: SymptomAutocompleteProps) {
  const [input, setInput] = useState('');
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [duration, setDuration] = useState(7);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Filter suggestions as user types
  useEffect(() => {
    if (input.length > 0) {
      const filtered = suggestions.filter(
        (s) =>
          s.toLowerCase().includes(input.toLowerCase()) &&
          !symptoms.some((sym) => sym.name.toLowerCase() === s.toLowerCase())
      );
      setFilteredSuggestions(filtered);
      setShowSuggestions(true);
    } else {
      setFilteredSuggestions([]);
      setShowSuggestions(false);
    }
  }, [input, symptoms, suggestions]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAddSymptom = (sympName: string) => {
    if (!symptoms.some((s) => s.name.toLowerCase() === sympName.toLowerCase())) {
      onAddSymptom({
        name: sympName,
        severity: 5,
        duration_days: duration,
      });
      setInput('');
      setShowSuggestions(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && input.trim()) {
      handleAddSymptom(input.trim());
    }
  };

  return (
    <div ref={containerRef} className="space-y-4">
      {/* Input with autocomplete */}
      <div className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => input.length > 0 && setShowSuggestions(true)}
            placeholder="Search symptoms..."
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
          />
        </div>

        {/* Autocomplete dropdown */}
        {showSuggestions && filteredSuggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 z-50 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 shadow-lg max-h-48 overflow-y-auto">
            {filteredSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => handleAddSymptom(suggestion)}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-900 dark:text-white"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Duration selector */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Duration (days)
          </label>
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(Math.max(1, parseInt(e.target.value) || 1))}
            min="1"
            max="365"
            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        <div className="flex flex-col justify-end">
          <Button
            onClick={() => input.trim() && handleAddSymptom(input.trim())}
            disabled={!input.trim()}
            className="w-full"
          >
            Add Symptom
          </Button>
        </div>
      </div>

      {/* Added symptoms list */}
      {symptoms.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="font-medium text-gray-900 dark:text-white">
            Added Symptoms ({symptoms.length})
          </h3>
          <div className="grid gap-2">
            {symptoms.map((symptom) => (
              <div
                key={symptom.name}
                className="flex items-center justify-between p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900 dark:text-white">
                    {symptom.name}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    For {symptom.duration_days} days • Severity: {symptom.severity}/10
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onRemoveSymptom(symptom.name)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
