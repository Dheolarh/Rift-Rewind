import { motion, useMotionValue, useTransform, animate, useAnimate } from "motion/react";
import { useEffect, useState } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import { getChampionSplashUrl, getChampionIconUrl } from "../../utils/championImages";
import topChampBg from "../../assets/summoner.jpg";
import { Crown } from "lucide-react";

interface Champion {
  name: string;
  games: number;
  wins: number;
  winRate: number;
  avgKills: number;
  avgDeaths: number;
  avgAssists: number;
  kda: number;
}

interface FavoriteChampionsSlideProps {
  champions: Champion[];
  aiHumor?: string;
}

function Counter({ value, duration = 2, delay = 0 }: { value: number; duration?: number; delay?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, { duration, delay });
    return controls.stop;
  }, [value, duration, delay, count]);

  return <motion.span>{rounded}</motion.span>;
}

// Champion Icon Component with async loading
function ChampionIcon({ championName, className }: { championName: string; className?: string }) {
  const [iconUrl, setIconUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    getChampionIconUrl(championName)
      .then((url) => {
        setIconUrl(url);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error(`Failed to load icon for ${championName}:`, error);
        setIsLoading(false);
      });
  }, [championName]);

  if (isLoading || !iconUrl) {
    return (
      <div className={`${className} bg-[#0A1428] flex items-center justify-center rounded-full`}>
        <div className="w-4 h-4 border-2 border-[#C8AA6E] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <ImageWithFallback
      src={iconUrl}
      alt={championName}
      className={`${className} rounded-full`}
      style={{ borderRadius: '50%' }}
    />
  );
}

export function FavoriteChampionsSlide({
  champions,
  aiHumor = "Looks like someone has a type... High skill ceiling champions and pain! 😅"
}: FavoriteChampionsSlideProps) {
  const topChampion = champions[0];
  const otherChampions = champions.slice(1, 5); // Get 4 champions (indices 1-4)

  return (
    <div className="relative size-full overflow-hidden bg-[#010A13]">
      {/* Background Image - Static Image */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={topChampBg}
          alt="Top Champions"
          className="size-full object-cover opacity-15"
        />
        {/* Dark Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#010A13]/90 via-[#010A13]/95 to-[#010A13]/98" />
        <div className="absolute inset-0 bg-gradient-to-r from-[#010A13]/70 via-transparent to-[#010A13]/70" />
      </div>

      {/* Vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(1,10,19,0.9)_100%)]" />

      {/* Animated Particles */}
      {[...Array(15)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full bg-[#C8AA6E]"
          style={{
            width: `${Math.random() * 3 + 1}px`,
            height: `${Math.random() * 3 + 1}px`,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}

      {/* Scrollable Content */}
      <div className="relative z-10 size-full overflow-y-auto scrollbar-hide">
        {/* Title - Top Left with Crown Icon */}
        <div className="absolute top-4 left-8 sm:left-12 md:left-16 z-20 flex items-center gap-3" style={{ marginLeft: '10px' }}>
          {/* Crown Icon */}
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.4, 0.0, 0.2, 1] }}
          >
            <Crown className="w-5 h-5 sm:w-6 sm:h-6 text-[#C8AA6E]" />
          </motion.div>
          
          {/* Text Section - 2 Vertical Columns with Slide Animation */}
          <div className="flex flex-col leading-tight overflow-hidden">
            <motion.span 
              initial={{ x: -100, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.6, ease: [0.4, 0.0, 0.2, 1] }}
              className="text-xs sm:text-sm text-[#C8AA6E] uppercase tracking-wider"
            >
              Most Played
            </motion.span>
            <motion.span 
              initial={{ x: -100, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.6, ease: [0.4, 0.0, 0.2, 1] }}
              className="text-base sm:text-lg md:text-xl text-[#C8AA6E] uppercase tracking-wider font-bold" 
              style={{ fontFamily: 'Georgia, serif' }}
            >
              Champions
            </motion.span>
          </div>
        </div>

        <div className="min-h-full flex flex-col items-center justify-center px-4 sm:px-6 py-8 sm:py-10 md:py-12">

          {/* Champion Icon - Circular with proper fill */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.6, ease: [0.4, 0.0, 0.2, 1] }}
            className="mb-4 sm:mb-5"
          >
            <div className="w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28 rounded-full overflow-hidden border-2 border-[#C8AA6E] bg-[#0A1428]">
              <ChampionIcon
                championName={topChampion.name}
                className="size-full object-cover rounded-full"
              />
            </div>
          </motion.div>

          {/* Champion Name - Big Heading */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="text-center mb-4 sm:mb-5"
          >
            <h2 
              className="text-4xl sm:text-5xl md:text-6xl "
              style={{ fontFamily: 'Georgia, serif' }}
            >
              {topChampion.name}
            </h2>
          </motion.div>

          {/* Stats with Sub-texts */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            className="flex items-center justify-center gap-6 sm:gap-8 md:gap-12 mb-5 sm:mb-6"
          >
            {/* Games */}
            <div className="text-center">
              <div 
                className="text-2xl sm:text-3xl md:text-4xl text-white mb-1 tabular-nums"
                style={{ fontFamily: 'Georgia, serif' }}
              >
                <Counter value={topChampion.games} duration={2} delay={0.7} />
              </div>
              <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
                Games
              </div>
            </div>

            {/* Divider */}
            <div 
              className="w-px h-12 sm:h-14 md:h-16"
              style={{ background: 'linear-gradient(to bottom, transparent, #C8AA6E, transparent)' }}
            />

            {/* Win Rate */}
            <div className="text-center">
              <div 
                className="text-2xl sm:text-3xl md:text-4xl text-[#0AC8B9] mb-1 tabular-nums"
                style={{ fontFamily: 'Georgia, serif' }}
              >
                {topChampion.winRate}%
              </div>
              <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
                Win Rate
              </div>
            </div>

            {/* Divider */}
            <div 
              className="w-px h-12 sm:h-14 md:h-16"
              style={{ background: 'linear-gradient(to bottom, transparent, #C8AA6E, transparent)' }}
            />

            {/* KDA */}
            <div className="text-center">
              <div 
                className="text-2xl sm:text-3xl md:text-4xl text-[#C8AA6E] mb-1 tabular-nums"
                style={{ fontFamily: 'Georgia, serif' }}
              >
                {topChampion.kda.toFixed(2)}
              </div>
              <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
                KDA
              </div>
            </div>
          </motion.div>

          {/* AI Humor */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9, duration: 0.6 }}
            className="text-center mb-6 sm:mb-8 max-w-xl px-2"
          >
            <p className="text-xs sm:text-sm md:text-base text-[#E8E6E3]/80 italic leading-relaxed">
              {aiHumor}
            </p>
          </motion.div>

          {/* Small Leaderboard */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1, duration: 0.6 }}
            className="w-full max-w-2xl"
          >
            <div 
              className="overflow-hidden border border-[#C8AA6E]/30 rounded-lg"
              style={{
                background: 'rgba(10, 20, 40, 0.7)',
                backdropFilter: 'blur(10px)',
              }}
            >
              {/* Header */}
              <div className="px-3 sm:px-4 py-2 sm:py-3 border-b border-[#C8AA6E]/20">
                <h3 className="text-xs sm:text-sm text-[#C8AA6E] uppercase tracking-wider text-center">
                  Other Top Champions
                </h3>
              </div>

              {/* Table */}
              <div className="divide-y divide-[#C8AA6E]/10">
                {otherChampions.map((champ, idx) => (
                  <motion.div
                    key={champ.name}
                    initial={{ opacity: 0, x: idx % 2 === 0 ? -50 : 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ 
                      delay: 1.3 + idx * 0.15, 
                      duration: 0.5,
                      ease: [0.4, 0.0, 0.2, 1]
                    }}
                    className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2 sm:py-3 hover:bg-[#C8AA6E]/5 transition-colors"
                  >
                    {/* Icon */}
                    <motion.div 
                      className="flex-shrink-0"
                      initial={{ scale: 0, rotate: -180 }}
                      animate={{ scale: 1, rotate: 0 }}
                      transition={{ 
                        delay: 1.4 + idx * 0.15,
                        duration: 0.4,
                        type: "spring",
                        bounce: 0.5
                      }}
                    >
                      <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full overflow-hidden border border-[#C8AA6E]/50 bg-[#0A1428]">
                        <ChampionIcon
                          championName={champ.name}
                          className="size-full object-cover"
                        />
                      </div>
                    </motion.div>

                    {/* Name */}
                    <div className="flex-1 min-w-0">
                      <div 
                        className="text-xs sm:text-sm md:text-base text-white truncate"
                        style={{ fontFamily: 'Georgia, serif' }}
                      >
                        {champ.name}
                      </div>
                    </div>

                    {/* Stats - Fixed Width Columns */}
                    <div className="flex items-center gap-2 sm:gap-3 md:gap-4">
                      {/* Games */}
                      <div className="text-center w-12 sm:w-14">
                        <div className="text-[10px] sm:text-xs text-[#A09B8C] mb-0.5">GAMES</div>
                        <div 
                          className="text-xs sm:text-sm md:text-base text-white tabular-nums"
                          style={{ fontFamily: 'monospace' }}
                        >
                          {champ.games}
                        </div>
                      </div>

                      {/* Win Rate */}
                      <div className="text-center w-12 sm:w-14">
                        <div className="text-[10px] sm:text-xs text-[#A09B8C] mb-0.5">WR</div>
                        <div 
                          className="text-xs sm:text-sm md:text-base text-[#0AC8B9] tabular-nums"
                          style={{ fontFamily: 'monospace' }}
                        >
                          {champ.winRate}%
                        </div>
                      </div>

                      {/* KDA */}
                      <div className="text-center w-12 sm:w-14">
                        <div className="text-[10px] sm:text-xs text-[#A09B8C] mb-0.5">KDA</div>
                        <div 
                          className="text-xs sm:text-sm md:text-base text-[#C8AA6E] tabular-nums"
                          style={{ fontFamily: 'monospace' }}
                        >
                          {champ.kda.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Bottom Spacing */}
          <div className="h-6 sm:h-8" />
        </div>
      </div>
    </div>
  );
}
