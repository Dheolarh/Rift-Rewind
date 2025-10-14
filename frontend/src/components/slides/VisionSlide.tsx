import { motion } from "motion/react";
import { Eye } from "lucide-react";

interface VisionSlideProps {
  wardsPlaced: number;
  wardsDestroyed: number;
  visionScore: number;
  controlWardsBought: number;
  aiHumor?: string;
}

export function VisionSlide({
  wardsPlaced,
  wardsDestroyed,
  visionScore,
  controlWardsBought,
  aiHumor = "You've placed more wards than a hospital has patients! 🏥 Your map awareness is legendary!"
}: VisionSlideProps) {
  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#0a1929] via-[#1a0b2e] to-[#010A13]">
      {/* Pulsing gradient */}
      <motion.div
        animate={{
          opacity: [0.2, 0.4, 0.2],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#0AC8B9] rounded-full blur-[150px]"
      />

      {/* Scrollable Content */}
      <div className="relative z-10 size-full overflow-y-auto scrollbar-hide">
        <div className="min-h-full flex flex-col items-center justify-center px-4 sm:px-6 py-6 sm:py-8">
          {/* Icon */}
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.6, type: "spring" }}
          >
            <Eye className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 text-[#0AC8B9] mb-4 sm:mb-6" />
          </motion.div>

          {/* Title */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-center mb-6 sm:mb-8"
          >
            <p className="text-sm sm:text-base md:text-lg text-[#A09B8C] uppercase tracking-[0.2em] sm:tracking-[0.3em]">
              You lit up the map with
            </p>
          </motion.div>

          {/* Ward count */}
          <motion.div
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7, duration: 0.8, type: "spring" }}
            className="mb-4 sm:mb-6"
          >
            <div className="text-6xl sm:text-7xl md:text-8xl lg:text-9xl leading-none bg-gradient-to-br from-[#0AC8B9] via-[#5DADE2] to-[#3498DB] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              {(wardsPlaced / 1000).toFixed(1)}K
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
              wards
            </p>
            <p className="text-sm sm:text-base md:text-lg text-[#A09B8C]">
              and destroyed <span className="text-[#C8AA6E]">{(wardsDestroyed / 1000).toFixed(1)}K</span> enemy wards
            </p>
          </motion.div>

          {/* AI Humor */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.3, duration: 0.6 }}
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
