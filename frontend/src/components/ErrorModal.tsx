import { motion, AnimatePresence } from "motion/react";

interface ErrorModalProps {
  isOpen: boolean;
  error: string;
  onClose: () => void;
  onRetry?: () => void;
}

export function ErrorModal({ isOpen, error, onClose, onRetry }: ErrorModalProps) {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
        >
          {/* Simple centered error message */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            onClick={(e) => e.stopPropagation()}
            className="text-center space-y-6 max-w-md"
          >
            {/* Error message */}
            <p className="text-[#E8E6E3] text-base sm:text-lg leading-relaxed">
              {error}
            </p>

            {/* Action buttons */}
            <div className="flex justify-center gap-6 text-sm sm:text-base">
              {onRetry && (
                <button
                  onClick={onRetry}
                  className="text-[#C8AA6E] hover:text-[#E8C478] transition-colors"
                >
                  Try Again
                </button>
              )}
              
              <button
                onClick={onClose}
                className="text-[#A09B8C] hover:text-[#E8E6E3] transition-colors"
              >
                Go Back
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
