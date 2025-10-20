import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import rankingBg from "../../assets/ranking.webp";

interface SocialComparisonSlideProps {
  rankPercentile: number;
  rank?: string;
  kdaRatio?: number;
  comparison?: string;
  aiHumor?: string;
}

function Counter({ value, duration = 2 }: { value: number; duration?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest * 10) / 10);

  useEffect(() => {
    const controls = animate(count, value, { duration, delay: 0.6 });
    return controls.stop;
  }, [value, duration, count]);

  return <motion.span>{rounded}</motion.span>;
}

export function SocialComparisonSlide({
  rankPercentile,
  rank = "UNRANKED",
  kdaRatio = 0,
  comparison = "Keep climbing!",
  aiHumor = "You're rubbing shoulders with the elite! 🎮✨"
}: SocialComparisonSlideProps) {

  return (
    <div className="relative w-full h-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* Background Image */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={rankingBg}
          alt="Ranking Background"
          className="w-full h-full object-cover opacity-15"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#0a1929]/90 via-[#010A13]/95 to-[#1a0b2e]/98" />
      </div>

      {/* Animated gradient */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-1/3 right-1/4 w-96 h-96 bg-[#C8AA6E] rounded-full blur-[150px]"
      />

      {/* Centered Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-4 sm:gap-6 px-4 max-w-lg">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="text-center"
        >
          <p className="text-base sm:text-lg md:text-xl text-[#A09B8C] uppercase tracking-[0.3em] mb-2" style={{ fontFamily: 'Georgia, serif' }}>
            Global Standing
          </p>
          <p className="text-xs sm:text-sm text-[#A09B8C]/70">
            You're in the
          </p>
        </motion.div>

        {/* HUGE percentile */}
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.8, type: "spring" }}
          className="text-center"
        >
          <div className="flex items-baseline justify-center mb-2">
            <span className="text-6xl sm:text-7xl md:text-8xl leading-none bg-gradient-to-br from-[#FFD700] via-[#C8AA6E] to-[#8B7548] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={rankPercentile} />
            </span>
            <span className="text-3xl sm:text-4xl md:text-5xl text-[#C8AA6E] ml-2" style={{ fontFamily: 'Georgia, serif' }}>
              %
            </span>
          </div>
          <p className="text-sm sm:text-base text-[#A09B8C]/80">
            {comparison}
          </p>
        </motion.div>

        {/* Stats Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="w-full max-w-sm"
        >
          <div className="bg-[#0A1428]/60 border border-[#C8AA6E]/40 backdrop-blur-sm p-4 sm:p-5 rounded">
            <div className="flex items-center justify-around gap-4">
              {/* Current Rank */}
              <div className="text-center">
                <div className="text-lg sm:text-xl text-[#C8AA6E] mb-1 font-semibold" style={{ fontFamily: 'Georgia, serif' }}>
                  {rank}
                </div>
                <div className="text-xs text-[#78716C]">Current Rank</div>
              </div>

              <div className="w-px h-12 bg-[#C8AA6E]/30" />

              {/* KDA */}
              <div className="text-center">
                <div className="text-lg sm:text-xl text-[#0AC8B9] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                  <Counter value={kdaRatio} />
                </div>
                <div className="text-xs text-[#78716C]">KDA Ratio</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-center max-w-md px-4"
        >
          <p className="text-xs sm:text-sm text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
