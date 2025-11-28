import { motion } from "motion/react";

interface RankedJourneyHumorSlideProps {
  aiHumor?: string;
}

export function RankedJourneyHumorSlide({
  aiHumor = "You climbed more ranks than a chess grandmaster... but with way more rage quits!",
}: RankedJourneyHumorSlideProps) {
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
        className="relative z-10 max-w-xl w-full px-6"
      >
        <p className="text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl text-[#C8AA6E] text-center leading-relaxed font-bold">
          {aiHumor}
        </p>
      </motion.div>
    </div>
  );
}
