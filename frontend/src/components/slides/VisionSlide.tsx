import { motion } from "motion/react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import visionBg from "../../assets/vision.webp";

interface VisionSlideProps {
  avgVisionScore: number;
  avgWardsPlaced: number;
  avgControlWards: number;
  totalVisionScore: number;
  totalWardsPlaced?: number;
  totalControlWards?: number;
  aiHumor?: string;
}

export function VisionSlide({
  avgVisionScore,
  avgWardsPlaced,
  avgControlWards,
  totalWardsPlaced = 0,
  totalControlWards = 0,
  aiHumor = "You've placed more wards than a hospital has patients! 🏥 Your map awareness is legendary!"
}: VisionSlideProps) {
  return (
    <div className="relative size-full overflow-hidden bg-[#010A13]">
      {/* Background Image */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={visionBg}
          alt="Vision Background"
          className="size-full object-cover opacity-15"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a1929]/90 via-[#1a0b2e]/95 to-[#010A13]/98" />
      </div>

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
          {/* Title */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-center mb-6 sm:mb-8"
          >
            <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-[#A09B8C] uppercase tracking-[0.2em] sm:tracking-[0.3em]">
              Your Vision Score
            </p>
          </motion.div>

          {/* Vision Score */}
          <motion.div
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7, duration: 0.8, type: "spring" }}
            className="mb-4 sm:mb-6"
          >
            <div 
              className="leading-none bg-gradient-to-br from-[#0AC8B9] via-[#5DADE2] to-[#3498DB] bg-clip-text text-transparent tabular-nums" 
              style={{ fontFamily: 'Georgia, serif', fontSize: 'clamp(7rem, 15vw, 14rem)', paddingBottom: '5px' }}
            >
              {avgVisionScore.toFixed(1)}
            </div>
          </motion.div>

          {/* Label */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="text-center mb-6 sm:mb-8"
          >
            <p className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl text-white mb-3 sm:mb-4" style={{ fontFamily: 'Georgia, serif' }}>
              Average per game
            </p>
            <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-[#A09B8C]">
              <span className="text-[#C8AA6E]">{totalWardsPlaced.toLocaleString()}</span> wards placed
              <span className="text-[#A09B8C]"> • </span>
              <span className="text-[#0AC8B9]">{totalControlWards.toLocaleString()}</span> control wards
            </p>
          </motion.div>

          {/* AI Humor */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.3, duration: 0.6 }}
            className="max-w-xl text-center px-4"
          >
            <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-[#E8E6E3]/80 italic leading-relaxed">
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
