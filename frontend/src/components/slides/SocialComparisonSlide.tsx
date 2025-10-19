import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";

interface PlayerComparison {
  rank: number;
  summonerName: string;
  winRate: number;
  gamesPlayed: number;
  isYou?: boolean;
}

interface SocialComparisonSlideProps {
  yourRank: number;
  percentile: number;
  leaderboard: PlayerComparison[];
  aiHumor?: string;
}

function Counter({ value, duration = 2 }: { value: number; duration?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, { duration, delay: 0.6 });
    return controls.stop;
  }, [value, duration, count]);

  return <motion.span>{rounded}</motion.span>;
}

export function SocialComparisonSlide({
  yourRank,
  percentile,
  leaderboard,
  aiHumor = "You're rubbing shoulders with the elite! Just... digitally. And they probably don't know you exist. 😎"
}: SocialComparisonSlideProps) {
  // Find the user's entry
  const userEntry = leaderboard.find(player => player.isYou);

  return (
    <div className="relative w-full h-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* LoL Character Background */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1920"
          alt="Background"
          className="w-full h-full object-cover opacity-5"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#0a1929]/90 via-[#010A13]/90 to-[#1a0b2e]/90" />
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
          <p className="text-base sm:text-lg md:text-xl text-[#A09B8C] uppercase tracking-[0.3em] mb-2">
            Regional Leaderboard
          </p>
          <p className="text-xs sm:text-sm text-[#A09B8C]/70">
            You're in the top
          </p>
        </motion.div>

        {/* HUGE percentile */}
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.8, type: "spring" }}
        >
          <div className="flex items-baseline justify-center">
            <span className="text-6xl sm:text-7xl md:text-8xl leading-none bg-gradient-to-br from-[#FFD700] via-[#C8AA6E] to-[#8B7548] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={percentile} />
            </span>
            <span className="text-3xl sm:text-4xl md:text-5xl text-[#C8AA6E] ml-2" style={{ fontFamily: 'Georgia, serif' }}>
              %
            </span>
          </div>
        </motion.div>

        {/* Your Stats Card - Only show user */}
        {userEntry && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.6 }}
            className="w-full max-w-sm"
          >
            <div className="bg-[#0A1428]/60 border border-[#C8AA6E]/40 backdrop-blur-sm p-4 sm:p-5 rounded">
              <div className="flex items-center gap-4">
                {/* Player Image */}
                <div className="flex-shrink-0 w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-[#C8AA6E]/30 to-transparent border border-[#C8AA6E] overflow-hidden">
                  <ImageWithFallback
                    src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100"
                    alt={userEntry.summonerName}
                    className="w-full h-full object-cover opacity-60"
                  />
                </div>

                {/* Stats */}
                <div className="flex-1">
                  <div className="text-base sm:text-lg text-[#C8AA6E] mb-1" style={{ fontFamily: 'Georgia, serif' }}>
                    {userEntry.summonerName}
                  </div>
                  <div className="text-xs text-[#A09B8C] mb-2">
                    Rank #{userEntry.rank.toLocaleString()}
                  </div>
                  <div className="flex items-center gap-3">
                    <div>
                      <div className="text-lg sm:text-xl text-[#0AC8B9] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                        {userEntry.winRate}%
                      </div>
                      <div className="text-xs text-[#78716C]">Win Rate</div>
                    </div>
                    <div className="w-px h-8 bg-[#C8AA6E]/30" />
                    <div>
                      <div className="text-lg sm:text-xl text-white tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                        {userEntry.gamesPlayed}
                      </div>
                      <div className="text-xs text-[#78716C]">Games</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

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
