import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import rankingBg from "../../assets/ranking.webp";

interface PlayerComparison {
  rank: number;
  summonerName: string;
  summonerLevel?: number;
  winRate: number;
  wins?: number;
  gamesPlayed: number;
  rankTier?: string;
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
  rankPercentile,
  leaderboard,
  aiHumor = "You're rubbing shoulders with the elite! 🎮✨"
}: SocialComparisonSlideProps) {
  const userEntry = leaderboard.find(player => player.isYou);
  const topPercentage = 100 - rankPercentile;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -50 }}
      transition={{ duration: 0.6, ease: [0.43, 0.13, 0.23, 0.96] }}
      className="relative w-full h-full overflow-hidden bg-[#010A13] flex items-center justify-center"
    >
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
          <p className="text-lg sm:text-xl md:text-2xl text-[#A09B8C] uppercase tracking-[0.3em] mb-2" style={{ fontFamily: 'Georgia, serif' }}>
            Leaderboard Position
          </p>
          <p className="text-sm sm:text-base md:text-lg text-[#A09B8C]/70">
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
            <span 
              className="leading-none bg-gradient-to-br from-[#FFD700] via-[#C8AA6E] to-[#8B7548] bg-clip-text text-transparent tabular-nums" 
              style={{ fontFamily: 'Georgia, serif', fontSize: 'clamp(7rem, 15vw, 12rem)', paddingBottom: '8px' }}
            >
              <Counter value={topPercentage} />
            </span>
            <span 
              className="text-[#C8AA6E] ml-2" 
              style={{ fontFamily: 'Georgia, serif', fontSize: 'clamp(4rem, 8vw, 7rem)' }}
            >
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
            className="w-full max-w-2xl"
          >
            <div className="relative">
              <div className="relative">
                {/* Player Entry */}
                <div className="p-3 sm:p-4 lg:p-6">
                  <div className="relative scale-100 sm:scale-105">
                    <div className="absolute inset-0 rounded-sm bg-gradient-to-r from-[#C8AA6E]/30 to-[#FFD700]/20 border-2 border-[#C8AA6E] shadow-[0_0_20px_rgba(200,170,110,0.3)] backdrop-blur-sm" />
                    <div className="relative p-4 sm:p-5 lg:p-8 flex items-center gap-4 sm:gap-6 lg:gap-8">
                      {/* Profile Icon */}
                      <div className="flex-shrink-0">
                        {userEntry.profileIconUrl ? (
                          <div className="w-14 h-14 sm:w-16 sm:h-16 lg:w-20 lg:h-20 rounded-full border-2 border-[#C8AA6E] overflow-hidden">
                            <ImageWithFallback
                              src={userEntry.profileIconUrl}
                              alt="Profile Icon"
                              className="w-full h-full object-cover"
                            />
                          </div>
                        ) : (
                          <div className="w-14 h-14 sm:w-16 sm:h-16 lg:w-20 lg:h-20 rounded-full bg-gradient-to-br from-[#C8AA6E] to-[#8B7548] border-2 border-[#C8AA6E] flex items-center justify-center">
                            <span className="text-xl sm:text-2xl font-bold text-[#0A1428]">?</span>
                          </div>
                        )}
                      </div>

                      {/* Player Info */}
                      <div className="flex-1 min-w-0">
                        <div className="text-base sm:text-lg lg:text-2xl truncate text-[#C8AA6E]">
                          {userEntry.summonerName.split('#')[0]}
                        </div>
                        <div className="text-xs sm:text-sm lg:text-base text-[#A09B8C] mt-2 flex items-center gap-3">
                          <span>Level {userEntry.summonerLevel || 0}</span>
                          <span className="text-[#A09B8C]/30">|</span>
                          <span>{userEntry.rankTier || 'UNRANKED'}</span>
                        </div>
                        <div className="text-xs sm:text-sm lg:text-base text-[#A09B8C] mt-2 flex items-center gap-3">
                          <span>{userEntry.gamesPlayed} games</span>
                          <span className="text-[#A09B8C]/30">|</span>
                          <span>{userEntry.wins || Math.round(userEntry.gamesPlayed * (userEntry.winRate / 100))} wins</span>
                        </div>
                      </div>

                      {/* Win Rate */}
                      <div className="flex-shrink-0 text-right">
                        <div className={`text-lg sm:text-xl lg:text-3xl tabular-nums ${
                          userEntry.winRate >= 60 ? 'text-[#0AC8B9]' :
                          userEntry.winRate >= 55 ? 'text-[#C8AA6E]' :
                          'text-white'
                        }`}>
                          {userEntry.winRate}%
                        </div>
                        <div className="text-sm sm:text-base lg:text-lg text-[#A09B8C]">Win Rate</div>
                      </div>
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
          <p className="text-sm sm:text-base md:text-lg text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}
