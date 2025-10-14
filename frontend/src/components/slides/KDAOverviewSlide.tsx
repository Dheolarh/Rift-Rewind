import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { Swords } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";

interface KDAOverviewSlideProps {
  averageKDA: number;
  totalKills: number;
  totalDeaths: number;
  totalAssists: number;
  aiHumor?: string;
}

function Counter({ value, duration = 2.5, decimals = 1 }: { value: number; duration?: number; decimals?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => 
    decimals > 0 ? (latest / 1000).toFixed(decimals) : Math.round(latest)
  );

  useEffect(() => {
    const controls = animate(count, value, { duration, delay: 0.7 });
    return controls.stop;
  }, [value, duration, count]);

  return <motion.span>{rounded}</motion.span>;
}

export function KDAOverviewSlide({
  averageKDA,
  totalKills,
  totalDeaths,
  totalAssists,
  aiHumor = "You've eliminated more champions than there are people in a small village! 🏰"
}: KDAOverviewSlideProps) {
  return (
    <div className="relative size-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* LoL Character Background */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1920"
          alt="Background"
          className="size-full object-cover opacity-5"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#0a1929]/90 via-[#010A13]/90 to-[#0a0515]/90" />
      </div>

      {/* Animated gradient orbs */}
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

      {/* Content */}
      <div className="relative z-10 w-full h-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8 md:py-12 flex flex-col items-center justify-center overflow-y-auto scrollbar-hide">
        {/* Icon */}
        <motion.div
          initial={{ opacity: 0, rotate: -180, scale: 0 }}
          animate={{ opacity: 1, rotate: 0, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.9, type: "spring" }}
        >
          <Swords className="w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 text-[#0AC8B9] mb-6 sm:mb-8" />
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-center mb-12 sm:mb-16"
        >
          <p className="text-lg sm:text-xl md:text-2xl text-[#A09B8C] uppercase tracking-[0.3em]">
            You eliminated
          </p>
        </motion.div>

        {/* HUGE Kill count */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5, rotateX: 90 }}
          animate={{ opacity: 1, scale: 1, rotateX: 0 }}
          transition={{ delay: 0.6, duration: 1, type: "spring" }}
          className="mb-6 sm:mb-8"
        >
          <div className="text-[100px] sm:text-[140px] md:text-[180px] lg:text-[220px] leading-none bg-gradient-to-br from-[#0AC8B9] via-[#5DADE2] to-[#3498DB] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
            <Counter value={totalKills} />K
          </div>
        </motion.div>

        {/* Label */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="text-center mb-12 sm:mb-16"
        >
          <p className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl text-white" style={{ fontFamily: 'Georgia, serif' }}>
            champions
          </p>
        </motion.div>

        {/* AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5, duration: 0.6 }}
          className="max-w-2xl text-center"
        >
          <p className="text-sm sm:text-base md:text-lg text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
