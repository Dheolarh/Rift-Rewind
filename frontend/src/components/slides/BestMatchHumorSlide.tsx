import { motion } from "motion/react";

interface BestMatchHumorSlideProps {
  aiHumor?: string;
  champion?: string;
  kills?: number;
  deaths?: number;
  assists?: number;
}

export function BestMatchHumorSlide({
  aiHumor = "This match was legendary! The scoreboard couldn't handle your performance.",
}: BestMatchHumorSlideProps) {
  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#2d0a4e] via-[#010A13] to-[#0a1929] flex items-center justify-center px-4">
      {/* Animated gradient - same as Champion Pool */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.15, 0.25, 0.15],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#8B5CF6] rounded-full blur-[120px] opacity-20"
      />

      {/* Centered Humor Text */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
        className="relative z-10 max-w-3xl w-full px-6"
      >
        <p className="text-lg sm:text-xl md:text-2xl text-[#C8AA6E] text-center leading-relaxed font-bold">
          {aiHumor}
        </p>
      </motion.div>
    </div>
  );
}
