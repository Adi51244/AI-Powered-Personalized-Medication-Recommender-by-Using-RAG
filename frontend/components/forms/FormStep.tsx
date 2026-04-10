'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface FormStepProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  isActive?: boolean;
}

/**
 * FormStep Component
 *
 * Wrapper for individual wizard steps with animations.
 */
export function FormStep({
  title,
  description,
  children,
  isActive = true,
}: FormStepProps) {
  return (
    <AnimatePresence mode="wait">
      {isActive && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="w-full"
        >
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {title}
            </h2>
            {description && (
              <p className="text-gray-600 dark:text-gray-400">
                {description}
              </p>
            )}
          </div>

          <div className="space-y-6">{children}</div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
