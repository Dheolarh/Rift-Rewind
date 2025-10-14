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

      {/* Content */}
      <div className="relative z-10 size-full flex flex-col items-center justify-center p-8">
        {/* Icon */}
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6, type: "spring" }}
        >
          <Eye className="w-16 h-16 sm:w-20 sm:h-20 text-[#0AC8B9] mb-8" />
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-xl sm:text-2xl text-[#A09B8C] uppercase tracking-[0.3em]">
            You lit up the map with
          </p>
        </motion.div>

        {/* HUGE Ward count */}
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7, duration: 0.8, type: "spring" }}
          className="mb-8"
        >
          <div className="text-[100px] sm:text-[140px] md:text-[180px] lg:text-[220px] leading-none bg-gradient-to-br from-[#0AC8B9] via-[#5DADE2] to-[#3498DB] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
            {(wardsPlaced / 1000).toFixed(1)}K
          </div>
        </motion.div>

        {/* Label */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-4xl sm:text-5xl md:text-6xl text-white mb-4" style={{ fontFamily: 'Georgia, serif' }}>
            wards
          </p>
          <p className="text-lg sm:text-xl text-[#A09B8C]">
            and destroyed <span className="text-[#C8AA6E]">{(wardsDestroyed / 1000).toFixed(1)}K</span> enemy wards
          </p>
        </motion.div>

        {/* AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.6 }}
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
