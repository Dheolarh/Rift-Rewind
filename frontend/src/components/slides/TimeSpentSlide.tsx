import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import zileanTime from "../../assets/Zilean_Time.webp";

interface TimeSpentSlideProps {
  hoursPlayed: number;
  gamesPlayed: number;
  summonerName: string;
  aiHumor?: string;
}

function Counter({ value, duration = 2.5 }: { value: number; duration?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, { duration, delay: 0.6 });
    return controls.stop;
  }, [value, duration, count]);

  return <motion.span>{rounded}</motion.span>;
}

export function TimeSpentSlide({
  hoursPlayed,
  gamesPlayed,
  summonerName,
  aiHumor = "That's approximately 47 binge-worthy Netflix series... but who's counting? 📺"
}: TimeSpentSlideProps) {
  const days = Math.floor(hoursPlayed / 24);

  return (
    <div className="relative size-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* LoL Character Background */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={zileanTime}
          alt="Background"
          className="size-full object-cover opacity-20"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a0b2e]/70 via-[#0a0515]/70 to-[#010A13]/70" />
      </div>

      {/* Animated gradient orbs */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#C8AA6E] rounded-full blur-[120px]"
      />
      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
        className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-[#0AC8B9] rounded-full blur-[120px]"
      />

      {/* Content - Centered and constrained */}
      <div className="relative z-10 w-full h-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8 md:py-12 flex flex-col items-center justify-center overflow-y-auto scrollbar-hide">
        {/* Small intro text */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center mb-6 sm:mb-8"
        >
          <p className="text-sm sm:text-base md:text-lg text-[#A09B8C] uppercase tracking-[0.3em]">
            In 2024, you spent
          </p>
        </motion.div>

        {/* HUGE number - the hero */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 1, type: "spring", bounce: 0.4 }}
          className="mb-4 sm:mb-6 md:mb-8"
        >
          <div className="text-[80px] sm:text-[120px] md:text-[160px] lg:text-[200px] leading-none bg-gradient-to-br from-[#FFD700] via-[#C8AA6E] to-[#0AC8B9] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
            <Counter value={hoursPlayed} />
          </div>
        </motion.div>

        {/* Label */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="text-center mb-6 sm:mb-8 md:mb-10"
        >
          <p className="text-xl sm:text-2xl md:text-3xl lg:text-4xl text-white mb-2 sm:mb-3" style={{ fontFamily: 'Georgia, serif' }}>
            hours on the Rift
          </p>
          <p className="text-sm sm:text-base md:text-lg text-[#A09B8C]">
            That's <span className="text-[#0AC8B9]">{days} days</span> of pure League
          </p>
        </motion.div>

        {/* AI Humor - storytelling */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="max-w-2xl text-center"
        >
          <p className="text-xs sm:text-sm md:text-base lg:text-lg text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
