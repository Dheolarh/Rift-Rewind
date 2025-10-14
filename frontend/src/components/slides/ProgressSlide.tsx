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

      {/* Content */}
      <div className="relative z-10 size-full flex flex-col items-center justify-center p-8">
        {/* Icon */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          <TrendingUp className="w-16 h-16 sm:w-20 sm:h-20 text-[#0AC8B9] mb-8" />
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-xl sm:text-2xl text-[#A09B8C] uppercase tracking-[0.3em]">
            Your win rate improved by
          </p>
        </motion.div>

        {/* HUGE improvement number */}
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7, duration: 0.8, type: "spring" }}
          className="mb-8"
        >
          <div className="text-[120px] sm:text-[160px] md:text-[200px] lg:text-[240px] leading-none bg-gradient-to-br from-[#0AC8B9] via-[#5DADE2] to-[#3498DB] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
            +{improvement.winRate}%
          </div>
        </motion.div>

        {/* Label */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-3xl sm:text-4xl md:text-5xl text-white mb-4" style={{ fontFamily: 'Georgia, serif' }}>
            this season
          </p>
        </motion.div>

        {/* Other improvements */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.6 }}
          className="flex flex-wrap items-center justify-center gap-8 sm:gap-12 mb-12"
        >
          <div className="text-center">
            <div className="text-3xl sm:text-4xl text-[#C8AA6E] mb-2 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              +{improvement.kda}
            </div>
            <div className="text-sm sm:text-base text-[#A09B8C] uppercase tracking-wider">
              KDA
            </div>
          </div>

          <div className="w-px h-16 bg-[#C8AA6E]/30" />

          <div className="text-center">
            <div className="text-3xl sm:text-4xl text-[#8B5CF6] mb-2 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              +{improvement.visionScore}
            </div>
            <div className="text-sm sm:text-base text-[#A09B8C] uppercase tracking-wider">
              Vision
            </div>
          </div>
        </motion.div>

        {/* AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.6, duration: 0.6 }}
          className="max-w-2xl text-center"
        >
          <p className="text-base sm:text-lg text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
