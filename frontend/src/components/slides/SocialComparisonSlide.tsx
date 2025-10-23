import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import rankingBg from "../../assets/ranking.webp";

interface PlayerComparison {
  rank: number;
  summonerName: string;
  winRate: number;
  gamesPlayed: number;
  profileIconUrl?: string;
  isYou?: boolean;
}

interface SocialComparisonSlideProps {
  yourRank: number;
  rankPercentile: number;
  leaderboard: PlayerComparison[];
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
  yourRank,
  rankPercentile,
  leaderboard,
  aiHumor = "You're rubbing shoulders with the elite! 🎮✨"
}: SocialComparisonSlideProps) {
  // Find the user's entry
  const userEntry = leaderboard.find(player => player.isYou);

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
            Leaderboard Position
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
              <Counter value={rankPercentile} />
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
                {/* Profile Icon or Rank Badge */}
                {userEntry.profileIconUrl ? (
                  <div className="flex-shrink-0 w-14 h-14 sm:w-16 sm:h-16 rounded-full border-2 border-[#FFD700] overflow-hidden">
                    <ImageWithFallback
                      src={userEntry.profileIconUrl}
                      alt="Profile Icon"
                      className="w-full h-full object-cover"
                    />
                  </div>
                ) : (
                  <div className="flex-shrink-0 w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-[#C8AA6E] to-[#8B7548] flex items-center justify-center rounded-full border-2 border-[#FFD700]">
                    <span className="text-xl sm:text-2xl font-bold text-[#0A1428]" style={{ fontFamily: 'Georgia, serif' }}>
                      #{userEntry.rank > 0 ? userEntry.rank.toLocaleString() : '?'}
                    </span>
                  </div>
                )}

                {/* Stats */}
                <div className="flex-1">
                  <div className="text-base sm:text-lg text-[#C8AA6E] mb-1 font-semibold" style={{ fontFamily: 'Georgia, serif' }}>
                    {userEntry.summonerName}
                  </div>
                  <div className="text-xs text-[#A09B8C] mb-2">
                    {userEntry.rank ? `Rank #${userEntry.rank.toLocaleString()}` : `Top ${rankPercentile.toFixed(1)}%`}
                  </div>
                  <div className="flex items-center gap-3">
                    <div>
                      <div className="text-lg sm:text-xl text-[#0AC8B9] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                        {userEntry.winRate.toFixed(1)}%
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
