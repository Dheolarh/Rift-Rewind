import { motion, AnimatePresence } from "motion/react";
import { AlertCircle, X, RotateCcw } from "lucide-react";

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
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ type: "spring", duration: 0.5 }}
              onClick={(e) => e.stopPropagation()}
              className="relative w-full max-w-md bg-gradient-to-br from-[#1a0b2e] via-[#0a0515] to-[#010A13] 
                       border-2 border-[#C8AA6E]/30 rounded-lg shadow-2xl overflow-hidden"
            >
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 z-10 text-[#A09B8C] hover:text-[#C8AA6E] 
                         transition-colors p-1 rounded-full hover:bg-white/5"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Glow effect */}
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-red-500/20 rounded-full blur-[100px]" />

              {/* Content */}
              <div className="relative p-6 sm:p-8">
                {/* Icon */}
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring", bounce: 0.5 }}
                  className="flex justify-center mb-4"
                >
                  <div className="relative">
                    <motion.div
                      animate={{ 
                        scale: [1, 1.2, 1],
                        opacity: [0.5, 0.8, 0.5]
                      }}
                      transition={{ 
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                      className="absolute inset-0 bg-red-500/30 rounded-full blur-xl"
                    />
                    <div className="relative bg-red-500/20 p-4 rounded-full border-2 border-red-500/50">
                      <AlertCircle className="w-12 h-12 text-red-400" />
                    </div>
                  </div>
                </motion.div>

                {/* Title */}
                <motion.h2
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-2xl sm:text-3xl font-bold text-center mb-3 bg-gradient-to-r 
                           from-red-400 to-orange-500 bg-clip-text text-transparent"
                >
                  Oops! Something Went Wrong
                </motion.h2>

                {/* Error message */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="mb-6"
                >
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <p className="text-sm sm:text-base text-[#E8E6E3] text-center leading-relaxed">
                      {error}
                    </p>
                  </div>
                </motion.div>

                {/* Common issues */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="mb-6 space-y-2"
                >
                  <p className="text-xs text-[#A09B8C] text-center mb-2">Common issues:</p>
                  <ul className="text-xs text-[#A09B8C] space-y-1">
                    <li className="flex items-start gap-2">
                      <span className="text-[#C8AA6E]">•</span>
                      <span>Check your summoner name and tag spelling</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[#C8AA6E]">•</span>
                      <span>Verify the region is correct</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[#C8AA6E]">•</span>
                      <span>Ensure backend server is running</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-[#C8AA6E]">•</span>
                      <span>Check your internet connection</span>
                    </li>
                  </ul>
                </motion.div>

                {/* Buttons */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="flex flex-col sm:flex-row gap-3"
                >
                  {onRetry && (
                    <button
                      onClick={onRetry}
                      className="flex-1 group relative px-6 py-3 bg-gradient-to-r from-[#8B7548] to-[#C8AA6E] 
                               hover:from-[#C8AA6E] hover:to-[#8B7548] transition-all duration-300 
                               shadow-lg hover:shadow-[#C8AA6E]/50 transform hover:scale-105 rounded"
                    >
                      <span className="flex items-center justify-center gap-2 text-[#0A1428] font-bold text-sm sm:text-base">
                        <RotateCcw className="w-4 h-4" />
                        Try Again
                      </span>
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent 
                                    translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 rounded" />
                    </button>
                  )}
                  
                  <button
                    onClick={onClose}
                    className="flex-1 px-6 py-3 bg-white/5 hover:bg-white/10 border border-[#C8AA6E]/30 
                             hover:border-[#C8AA6E] transition-all duration-300 text-[#E8E6E3] 
                             font-semibold text-sm sm:text-base rounded hover:shadow-lg"
                  >
                    Go Back
                  </button>
                </motion.div>
              </div>

              {/* Decorative corner accents */}
              <div className="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 border-[#C8AA6E]/30" />
              <div className="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 border-[#C8AA6E]/30" />
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
