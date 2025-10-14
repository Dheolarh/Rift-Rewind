import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { TrendingUp, Medal, Star } from "lucide-react";
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
    const controls = animate(count, value, { duration, delay: 0.7 });
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
  return (
    <div className="relative size-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* LoL Character Background */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1920"
          alt="Background"
          className="size-full object-cover opacity-5"
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

      {/* Content */}
      <div className="relative z-10 w-full h-full max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8 md:py-12 flex flex-col overflow-y-auto scrollbar-hide">
        {/* Icon */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center mb-4 sm:mb-6"
        >
          <TrendingUp className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 text-[#C8AA6E] mx-auto" />
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-center mb-6 sm:mb-8"
        >
          <p className="text-base sm:text-lg md:text-xl text-[#A09B8C] uppercase tracking-[0.3em] mb-4">
            You're in the
          </p>
        </motion.div>

        {/* HUGE percentile */}
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.8, type: "spring" }}
          className="mb-4 sm:mb-6"
        >
          <div className="flex items-baseline justify-center">
            <span className="text-[80px] sm:text-[120px] md:text-[160px] lg:text-[200px] leading-none bg-gradient-to-br from-[#FFD700] via-[#C8AA6E] to-[#8B7548] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={percentile} />
            </span>
            <span className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-[#C8AA6E] ml-2 sm:ml-4" style={{ fontFamily: 'Georgia, serif' }}>
              %
            </span>
          </div>
        </motion.div>

        {/* Label */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-center mb-6 sm:mb-8"
        >
          <p className="text-xl sm:text-2xl md:text-3xl lg:text-4xl text-white mb-2" style={{ fontFamily: 'Georgia, serif' }}>
            of all players
          </p>
          <p className="text-sm sm:text-base md:text-lg text-[#A09B8C]">
            That's rank <span className="text-[#C8AA6E]">#{yourRank.toLocaleString()}</span> globally
          </p>
        </motion.div>

        {/* Mini Leaderboard Table */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.6 }}
          className="max-w-3xl mx-auto w-full mb-6 sm:mb-8"
        >
          <div className="bg-[#0A1428]/60 border border-[#C8AA6E]/20 backdrop-blur-sm overflow-hidden">
            <div className="p-3 sm:p-4 border-b border-[#C8AA6E]/10">
              <h3 className="text-xs sm:text-sm text-[#C8AA6E] uppercase tracking-wider text-center">
                Regional Leaderboard
              </h3>
            </div>
            <div className="divide-y divide-[#C8AA6E]/10">
              {leaderboard.map((player, index) => (
                <motion.div
                  key={player.rank}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.5 + index * 0.1 }}
                  className={`flex items-center gap-2 sm:gap-3 md:gap-4 p-2 sm:p-3 ${
                    player.isYou ? 'bg-[#C8AA6E]/10' : 'hover:bg-[#0A1428]/40'
                  } transition-colors`}
                >
                  {/* Rank */}
                  <div className="flex-shrink-0 w-8 sm:w-10 text-center">
                    {player.rank <= 3 ? (
                      <div className={`w-6 h-6 sm:w-8 sm:h-8 mx-auto flex items-center justify-center ${
                        player.rank === 1 ? 'bg-gradient-to-br from-[#FFD700] to-[#C8AA6E]' :
                        player.rank === 2 ? 'bg-gradient-to-br from-[#C0C0C0] to-[#A0A0A0]' :
                        'bg-gradient-to-br from-[#CD7F32] to-[#8B5A3C]'
                      }`}>
                        <Star className="w-3 h-3 sm:w-4 sm:h-4 text-[#010A13]" />
                      </div>
                    ) : (
                      <span className="text-xs sm:text-sm text-[#C8AA6E]">#{player.rank}</span>
                    )}
                  </div>

                  {/* Player Image */}
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 bg-gradient-to-br from-[#C8AA6E]/30 to-transparent border border-[#C8AA6E]/40 overflow-hidden">
                      <ImageWithFallback
                        src={`https://images.unsplash.com/photo-${1535713875002 + index}-d1d0cf377fde?w=100`}
                        alt={player.summonerName}
                        className="size-full object-cover opacity-60"
                      />
                    </div>
                  </div>

                  {/* Name */}
                  <div className="flex-1 min-w-0">
                    <div className={`text-xs sm:text-sm md:text-base truncate ${
                      player.isYou ? 'text-[#C8AA6E]' : 'text-white'
                    }`} style={{ fontFamily: 'Georgia, serif' }}>
                      {player.summonerName}
                      {player.isYou && <span className="text-[10px] sm:text-xs ml-1 opacity-75">(You)</span>}
                    </div>
                    <div className="text-[10px] sm:text-xs text-[#78716C]">{player.gamesPlayed} games</div>
                  </div>

                  {/* Win Rate */}
                  <div className="flex-shrink-0 text-right">
                    <div className={`text-sm sm:text-base md:text-lg tabular-nums ${
                      player.winRate >= 60 ? 'text-[#0AC8B9]' :
                      player.winRate >= 55 ? 'text-[#C8AA6E]' :
                      'text-white'
                    }`} style={{ fontFamily: 'Georgia, serif' }}>
                      {player.winRate}%
                    </div>
                    <div className="text-[10px] sm:text-xs text-[#78716C]">WR</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2, duration: 0.6 }}
          className="max-w-2xl mx-auto text-center"
        >
          <p className="text-xs sm:text-sm md:text-base lg:text-lg text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
