import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { Crown, Trophy, Zap } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";

interface Champion {
  name: string;
  mastery: number;
  games: number;
  winRate: number;
}

interface FavoriteChampionsSlideProps {
  champions: Champion[];
  aiHumor?: string;
}

function Counter({ value, duration = 2 }: { value: number; duration?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, { duration, delay: 0.8 });
    return controls.stop;
  }, [value, duration, count]);

  return <motion.span>{rounded}</motion.span>;
}

const getRankIcon = (rank: number) => {
  if (rank === 1) return Crown;
  if (rank === 2) return Trophy;
  return Zap;
};

export function FavoriteChampionsSlide({
  champions,
  aiHumor = "Looks like someone has a type... High skill ceiling champions and pain! 😅"
}: FavoriteChampionsSlideProps) {
  const topChampion = champions[0];
  const displayChampions = champions.slice(0, 6);

  return (
    <div className="relative size-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* Dynamic Top Champion Background */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1614294148960-9aa740632a87?w=1920"
          alt={topChampion.name}
          className="size-full object-cover opacity-10"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#0a1929]/85 via-[#010A13]/85 to-[#1a0b2e]/85" />
      </div>

      {/* Animated gradient */}
      <motion.div
        animate={{
          scale: [1, 1.1, 1],
          rotate: [0, 5, 0],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute inset-0 bg-gradient-to-br from-[#C8AA6E]/20 via-transparent to-[#0AC8B9]/20"
      />

      {/* Content */}
      <div className="relative z-10 w-full h-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8 md:py-12 flex flex-col overflow-y-auto scrollbar-hide">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center mb-6 sm:mb-8"
        >
          <Crown className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 text-[#C8AA6E] mx-auto mb-3" />
          <p className="text-base sm:text-lg md:text-xl text-[#A09B8C] uppercase tracking-[0.3em]">
            Your Top Champions
          </p>
        </motion.div>

        {/* Champion Grid - Like champion pool but with more details */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4 md:gap-5 mb-6 sm:mb-8 flex-1">
          {displayChampions.map((champ, idx) => {
            const RankIcon = getRankIcon(idx + 1);
            const isTop1 = idx === 0;
            
            return (
              <motion.div
                key={champ.name}
                initial={{ opacity: 0, y: 50, scale: 0.8 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ delay: 0.4 + idx * 0.15, duration: 0.6, type: "spring" }}
                className={`relative group ${isTop1 ? 'sm:col-span-2 sm:row-span-2' : ''}`}
              >
                {/* Card */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#C8AA6E]/20 to-transparent border-2 border-[#C8AA6E]/40 backdrop-blur-sm group-hover:border-[#C8AA6E] transition-all" />
                
                <div className="relative h-full flex flex-col p-3 sm:p-4">
                  {/* Champion Portrait */}
                  <div className="relative mb-3 sm:mb-4 flex-shrink-0">
                    <div className={`relative aspect-square overflow-hidden border-2 border-[#C8AA6E]/50 bg-gradient-to-br from-[#C8AA6E]/20 to-transparent ${
                      isTop1 ? '' : ''
                    }`}>
                      <ImageWithFallback
                        src={`https://images.unsplash.com/photo-1614294148960-9aa740632a87?w=400`}
                        alt={champ.name}
                        className="size-full object-cover opacity-60 group-hover:opacity-100 group-hover:scale-110 transition-all duration-300"
                      />
                      
                      {/* Rank Badge */}
                      <div className={`absolute top-2 left-2 ${isTop1 ? 'w-10 h-10 sm:w-12 sm:h-12' : 'w-8 h-8'} bg-gradient-to-br from-[#C8AA6E] to-[#8B7548] flex items-center justify-center`}>
                        <RankIcon className={`${isTop1 ? 'w-5 h-5 sm:w-6 sm:h-6' : 'w-4 h-4'} text-[#010A13]`} />
                      </div>

                      {/* Mastery Badge */}
                      <div className="absolute top-2 right-2 bg-[#8B5CF6]/90 px-2 py-0.5 sm:py-1">
                        <span className={`${isTop1 ? 'text-xs sm:text-sm' : 'text-[10px] sm:text-xs'} text-white tabular-nums`}>
                          {Math.floor(champ.mastery / 1000)}K
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Champion Info */}
                  <div className="flex-1 flex flex-col">
                    <h3 className={`${isTop1 ? 'text-xl sm:text-2xl md:text-3xl' : 'text-base sm:text-lg md:text-xl'} text-[#C8AA6E] mb-2 text-center`} style={{ fontFamily: 'Georgia, serif' }}>
                      {champ.name}
                    </h3>
                    
                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-2 sm:gap-3 flex-1">
                      <div className="text-center">
                        <div className={`${isTop1 ? 'text-xl sm:text-2xl' : 'text-base sm:text-lg'} text-white mb-0.5 tabular-nums`} style={{ fontFamily: 'Georgia, serif' }}>
                          <Counter value={champ.games} duration={1.5} />
                        </div>
                        <div className="text-[10px] sm:text-xs text-[#A09B8C] uppercase tracking-wide">Games</div>
                      </div>
                      
                      <div className="text-center">
                        <div className={`${isTop1 ? 'text-xl sm:text-2xl' : 'text-base sm:text-lg'} text-[#0AC8B9] mb-0.5 tabular-nums`} style={{ fontFamily: 'Georgia, serif' }}>
                          {champ.winRate}%
                        </div>
                        <div className="text-[10px] sm:text-xs text-[#A09B8C] uppercase tracking-wide">Win Rate</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Hover glow */}
                <div className="absolute inset-0 bg-gradient-to-t from-[#C8AA6E]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              </motion.div>
            );
          })}
        </div>

        {/* AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5, duration: 0.6 }}
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
