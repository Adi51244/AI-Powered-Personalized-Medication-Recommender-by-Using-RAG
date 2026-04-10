/**
 * Design tokens and theme configuration for MediRAG
 * Medical-specific color schemes for safety, confidence, and evidence types
 */

// Safety status colors (for medication safety badges and alerts)
export const safetyColors = {
  safe: {
    badge: 'bg-green-600',
    bg: 'bg-green-50',
    text: 'text-green-800',
    border: 'border-green-600'
  },
  warning: {
    badge: 'bg-amber-600',
    bg: 'bg-amber-50',
    text: 'text-amber-800',
    border: 'border-amber-600'
  },
  contraindicated: {
    badge: 'bg-red-600',
    bg: 'bg-red-50',
    text: 'text-red-800',
    border: 'border-red-600'
  }
} as const;

// Warning severity colors
export const  severityColors = {
  major: 'text-red-700',
  moderate: 'text-amber-600',
  minor: 'text-yellow-600'
} as const;

// Confidence level colors (for ML predictions)
export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.5) return 'text-blue-600';
  return 'text-gray-600';
};

export const getConfidenceBg = (confidence: number): string => {
  if (confidence >= 0.8) return 'bg-green-100';
  if (confidence >= 0.5) return 'bg-blue-100';
  return 'bg-gray-100';
};

// Evidence type colors (for RAG citations)
export const evidenceTypeColors = {
  clinical_case: 'bg-blue-100 text-blue-800 border-blue-300',
  drug_profile: 'bg-purple-100 text-purple-800 border-purple-300',
  clinical_guideline: 'bg-green-100 text-green-800 border-green-300'
} as const;

// Spacing tokens
export const spacing = {
  sectionGap: 'gap-6', // 1.5rem between major sections
  cardGap: 'gap-4',    // 1rem between cards
  inputGap: 'gap-3'    // 0.75rem between form inputs
} as const;

// Typography tokens
export const typography = {
  h1: 'text-3xl font-bold',
  h2: 'text-2xl font-semibold',
  h3: 'text-xl font-semibold',
  body: 'text-base',
  caption: 'text-sm text-gray-600',
  label: 'text-sm font-medium'
} as const;

// Container widths
export const containerWidths = {
  sm: 'max-w-2xl',
  md: 'max-w-4xl',
  lg: 'max-w-6xl',
  xl: 'max-w-7xl',
  full: 'max-w-full'
} as const;

// Medical application specific constants
export const medicalTheme = {
  primaryBlue: '#3B82F6',    // For headers, primary actions
  clinicalGray: '#6B7280',   // For secondary text
  successGreen: '#10B981',   // For safe medications
  warningAmber: '#F59E0B',   // For warnings
  dangerRed: '#EF4444',      // For contraindications
  backgroundColor: '#F9FAFB' // Light gray background
} as const;
