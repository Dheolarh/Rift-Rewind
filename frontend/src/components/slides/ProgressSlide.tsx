import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import progressBg from "../../assets/progress.webp";

interface ProgressSlideProps {
  message?: string;
  currentSeason?: {
    currentRank?: string;
    tier?: string;
    division?: string;
    lp?: number;
    wins?: number;
    losses?: number;
    winRate?: number;
  };
  aiHumor?: string;
}

function Counter({ value, duration = 2, isDecimal = false }: { value: number; duration?: number; isDecimal?: boolean }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => {
    // For integers (games, wins), round to whole numbers
    // For decimals (win rate), round to 1 decimal place
    return isDecimal ? Math.round(latest * 10) / 10 : Math.round(latest);
  });

  useEffect(() => {
    const controls = animate(count, value, { duration, delay: 0.6 });
    return controls.stop;
  }, [value, duration, count]);

  return <motion.span>{rounded}</motion.span>;
}

export function ProgressSlide({
  message = "Progress tracking requires multi-season data",
  currentSeason,
  aiHumor = "Every game is a step forward in your journey! 🎯"
}: ProgressSlideProps) {
  const wins = currentSeason?.wins || 0;
  const losses = currentSeason?.losses || 0;
  const winRate = currentSeason?.winRate || 0;
  const totalGames = wins + losses;
  return (
    <div className="relative w-full h-full overflow-hidden bg-[#010A13]">
      {/* Background Image */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={progressBg}
          alt="Progress Background"
          className="w-full h-full object-cover opacity-15"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a0b2e]/90 via-[#010A13]/95 to-[#2d0a4e]/98" />
      </div>

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
      <div className="relative z-10 w-full h-full flex flex-col items-center justify-center px-4 sm:px-6 md:px-8 py-8 sm:py-10 gap-6 sm:gap-8 md:gap-10">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="text-center"
        >
          <h1 className="text-2xl sm:text-3xl md:text-4xl text-[#A09B8C] uppercase tracking-[0.3em]" style={{ fontFamily: 'Georgia, serif' }}>
            Season Journey
          </h1>
          <p className="text-sm sm:text-base text-[#A09B8C]/70 mt-2">Your Ranked Performance</p>
        </motion.div>

        {/* Three Stats - Horizontal Row */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="flex flex-wrap items-center justify-center gap-8 sm:gap-12 md:gap-16"
        >
          {/* Total Games */}
          <div className="text-center">
            <div className="text-5xl sm:text-6xl md:text-7xl text-[#0AC8B9] mb-2 sm:mb-3 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={totalGames} />
            </div>
            <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
              Games Played
            </div>
          </div>

          <div className="w-px h-16 sm:h-20 md:h-24 bg-[#C8AA6E]/30" />

          {/* Wins */}
          <div className="text-center">
            <div className="text-5xl sm:text-6xl md:text-7xl text-[#C8AA6E] mb-2 sm:mb-3 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={wins} />
            </div>
            <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
              Victories
            </div>
          </div>

          <div className="w-px h-16 sm:h-20 md:h-24 bg-[#C8AA6E]/30" />

          {/* Win Rate */}
          <div className="text-center">
            <div className="text-5xl sm:text-6xl md:text-7xl text-[#8B5CF6] mb-2 sm:mb-3 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={winRate} isDecimal={true} />%
            </div>
            <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
              Win Rate
            </div>
          </div>
        </motion.div>

        {/* AI Text */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="w-full max-w-md px-4"
        >
          <div className="relative p-3 sm:p-4 bg-[#1E2328]/60 backdrop-blur-sm rounded-lg border border-[#C8AA6E]/30">
            <p className="text-xs sm:text-sm text-[#E8E6E3]/80 italic leading-relaxed text-center">
              {aiHumor}
            </p>

            {/* Decorative corner accents */}
            <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-[#C8AA6E]" />
            <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-[#C8AA6E]" />
            <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-[#C8AA6E]" />
            <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-[#C8AA6E]" />
          </div>
        </motion.div>
      </div>
    </div>
  );
}
