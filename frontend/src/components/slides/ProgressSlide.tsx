import { motion } from "motion/react";
import { TrendingUp } from "lucide-react";

interface ProgressSlideProps {
  improvement: {
    winRate: number;
    kda: number;
    visionScore: number;
  };
  aiHumor?: string;
}

export function ProgressSlide({
  improvement,
  aiHumor = "You've grown more than a Cho'Gath with full stacks! 🦖 The grind never stops!"
}: ProgressSlideProps) {
  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#1a0b2e] via-[#010A13] to-[#2d0a4e]">
      {/* Animated upward gradient */}
      <motion.div
        animate={{
          y: [0, -50, 0],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-1/2 bg-gradient-to-t from-[#0AC8B9]/30 to-transparent"
      />

      {/* Scrollable Content */}
      <div className="relative z-10 size-full overflow-y-auto scrollbar-hide">
        <div className="min-h-full flex flex-col items-center justify-center px-4 sm:px-6 py-6 sm:py-8">
          {/* Icon */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <TrendingUp className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 text-[#0AC8B9] mb-4 sm:mb-6" />
          </motion.div>

          {/* Title */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-center mb-6 sm:mb-8"
          >
            <p className="text-sm sm:text-base md:text-lg text-[#A09B8C] uppercase tracking-[0.2em] sm:tracking-[0.3em]">
              Your win rate improved by
            </p>
          </motion.div>

          {/* Improvement number */}
          <motion.div
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7, duration: 0.8, type: "spring" }}
            className="mb-4 sm:mb-6"
          >
            <div className="text-6xl sm:text-7xl md:text-8xl lg:text-9xl leading-none bg-gradient-to-br from-[#0AC8B9] via-[#5DADE2] to-[#3498DB] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              +{improvement.winRate}%
            </div>
          </motion.div>

          {/* Label */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="text-center mb-6 sm:mb-8"
          >
            <p className="text-2xl sm:text-3xl md:text-4xl text-white mb-2 sm:mb-3" style={{ fontFamily: 'Georgia, serif' }}>
              this season
            </p>
          </motion.div>

          {/* Other improvements */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.3, duration: 0.6 }}
            className="flex items-center justify-center gap-6 sm:gap-8 md:gap-10 mb-6 sm:mb-8"
          >
            <div className="text-center">
              <div className="text-2xl sm:text-3xl md:text-4xl text-[#C8AA6E] mb-1 sm:mb-2 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                +{improvement.kda}
              </div>
              <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
                KDA
              </div>
            </div>

            <div className="w-px h-12 sm:h-14 bg-[#C8AA6E]/30" />

            <div className="text-center">
              <div className="text-2xl sm:text-3xl md:text-4xl text-[#8B5CF6] mb-1 sm:mb-2 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                +{improvement.visionScore}
              </div>
              <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
                Vision
              </div>
            </div>
          </motion.div>

          {/* AI Humor */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.6, duration: 0.6 }}
            className="max-w-xl text-center px-4"
          >
            <p className="text-xs sm:text-sm md:text-base text-[#E8E6E3]/80 italic leading-relaxed">
              {aiHumor}
            </p>
          </motion.div>

          {/* Bottom Spacing */}
          <div className="h-4 sm:h-6" />
        </div>
      </div>
    </div>
  );
}
