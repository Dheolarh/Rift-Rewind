import { motion } from "motion/react";
import { Pause, Play, Music } from "lucide-react";

interface SlideNavigationProps {
  currentSlide: number;
  totalSlides: number;
  onPrevious: () => void;
  onNext: () => void;
  isPaused?: boolean;
  onTogglePause?: () => void;
  isMusicPlaying?: boolean;
  onMusicToggle?: () => void;
}

export function SlideNavigation({
  currentSlide,
  totalSlides,
  onPrevious,
  onNext,
  isPaused = false,
  onTogglePause,
  isMusicPlaying = false,
  onMusicToggle,
}: SlideNavigationProps) {
  // Disable previous on Welcome (0) and Loading (1) slides
  // Disable previous on the slide after Loading (slide 2)
  const canGoPrevious = currentSlide > 2;
  
  // Disable next on Loading (1) and Welcome (0) slides
  const canGoNext = currentSlide > 1 && currentSlide < totalSlides - 1;

  // Hide pause/play button on Loading slide (slide 1)
  const showPausePlay = currentSlide !== 1;

  return (
    <>
      {/* Music Toggle Button - Top Left */}
      {onMusicToggle && (
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          onClick={onMusicToggle}
          className="fixed top-4 z-50 w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center bg-gradient-to-br from-[#8B7548]/20 to-[#078378]/20 border border-[#8B7548]/50 backdrop-blur-md hover:border-[#C8AA6E] hover:shadow-lg hover:shadow-[#C8AA6E]/30 transition-all group"
          aria-label={isMusicPlaying ? "Mute music" : "Play music"}
          style={{marginLeft: '15px'}}
        >
          <Music 
            className={`w-5 h-5 sm:w-6 sm:h-6 transition-colors ${
              isMusicPlaying ? 'text-[#C8AA6E]' : 'text-[#8B7548]'
            } group-hover:text-[#C8AA6E]`}
          />
          {isMusicPlaying && (
            <motion.div 
              className="absolute inset-0 border-2 border-[#C8AA6E]"
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          )}
        </motion.button>
      )}
      
      {/* Pause/Play Button - Top Right */}
      {onTogglePause && showPausePlay && (
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
          className="fixed left-0 top-0 bottom-0 w-1/4 z-40 cursor-w-resize transition-opacity"
          aria-label="Previous slide"
        />
      )}

      {/* Right click region */}
      {canGoNext && (
        <div
          onClick={onNext}
          className="fixed right-0 top-0 bottom-0 w-1/4 z-40 cursor-e-resize transition-opacity"
          aria-label="Next slide"
        />
      )}

    </>
  );
}
