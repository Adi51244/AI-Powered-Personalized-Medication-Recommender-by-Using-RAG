/**
 * Footer component with disclaimers and version info
 */

import { APP_VERSION } from '@/lib/utils/constants';

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="space-y-3">
          {/* Medical disclaimer */}
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <p className="text-sm text-amber-800 font-medium">
              ⚠️ Medical Disclaimer
            </p>
            <p className="text-xs text-amber-700 mt-1">
              This system is intended for research and educational purposes only.
              All diagnoses and recommendations should be reviewed by qualified healthcare professionals.
              Do not use this system as a substitute for professional medical advice.
            </p>
          </div>

          {/* Footer info */}
          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>© 2026 MediRAG Clinical Decision Support System</p>
            <p className="text-xs">Version {APP_VERSION}</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
