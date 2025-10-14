import { motion } from "motion/react";
import { Pause, Play } from "lucide-react";

interface SlideNavigationProps {
  currentSlide: number;
  totalSlides: number;
  onPrevious: () => void;
  onNext: () => void;
  isPaused?: boolean;
  onTogglePause?: () => void;
}

export function SlideNavigation({
  currentSlide,
  totalSlides,
  onPrevious,
  onNext,
  isPaused = false,
  onTogglePause,
}: SlideNavigationProps) {
  const canGoPrevious = currentSlide > 0;
  const canGoNext = currentSlide < totalSlides - 1;

  return (
    <>
      {/* Pause/Play Button - Top Right */}
      {onTogglePause && (
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          onClick={onTogglePause}
          className="fixed top-4 right-4 z-50 w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center bg-gradient-to-br from-[#8B7548]/20 to-[#078378]/20 border border-[#8B7548]/50 backdrop-blur-md hover:border-[#C8AA6E] hover:shadow-lg hover:shadow-[#C8AA6E]/30 transition-all group"
          aria-label={isPaused ? "Play slideshow" : "Pause slideshow"}
        >
          {isPaused ? (
            <Play className="w-5 h-5 sm:w-6 sm:h-6 text-[#8B7548] group-hover:text-[#C8AA6E] transition-colors fill-current" />
          ) : (
            <Pause className="w-5 h-5 sm:w-6 sm:h-6 text-[#8B7548] group-hover:text-[#C8AA6E] transition-colors" />
          )}
        </motion.button>
      )}

      {/* Left click region */}
      {canGoPrevious && (
        <div
          onClick={onPrevious}
          className="fixed left-0 top-0 bottom-0 w-1/4 z-40 cursor-w-resize hover:bg-white/5 transition-colors"
          aria-label="Previous slide"
        />
      )}

      {/* Right click region */}
      {canGoNext && (
        <div
          onClick={onNext}
          className="fixed right-0 top-0 bottom-0 w-1/4 z-40 cursor-e-resize hover:bg-white/5 transition-colors"
          aria-label="Next slide"
        />
      )}

    </>
  );
}
