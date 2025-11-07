import { motion } from "motion/react";
import { ImageWithFallback } from "../source/ImageWithFallback";

interface ChampionPoolHumorSlideProps {
  aiHumor?: string;
}

export function ChampionPoolHumorSlide({
  aiHumor = "Talk about champion diversity! You're basically a one-person champion ocean.",
}: ChampionPoolHumorSlideProps) {
  return (
    <div className="relative size-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* Background Image - same as Favorite Champions */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1920"
          alt="Background"
          className="size-full object-cover opacity-5"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#0a1929]/90 via-[#010A13]/90 to-[#0a0515]/90" />
      </div>

      {/* Animated gradient orbs - blue theme like Favorite Champions */}
      <motion.div
        animate={{
          x: [0, 100, 0],
          y: [0, -50, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-0 right-1/4 w-96 h-96 bg-[#0AC8B9] rounded-full blur-[120px] opacity-30"
      />

      <motion.div
        animate={{
          x: [0, -80, 0],
          y: [0, 60, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
        className="absolute bottom-0 left-1/4 w-80 h-80 bg-[#5DADE2] rounded-full blur-[120px] opacity-20"
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
