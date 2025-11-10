import { ImageWithFallback } from "../source/ImageWithFallback";
import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { getChampionIconUrl } from "../../utils/championImages";

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

export function FavoriteChampionsSlide({
  champions = [],
}: FavoriteChampionsSlideProps) {
  // Show top 5 champions
  const topFive = champions.slice(0, 5);
  const [iconUrls, setIconUrls] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  // Preload all champion icons at once
  useEffect(() => {
    const loadIcons = async () => {
      const urls: Record<string, string> = {};
      const championsToLoad = champions.slice(0, 5);
      await Promise.all(
        championsToLoad.map(async (champion) => {
          const url = await getChampionIconUrl(champion.name);
          urls[champion.name] = url;
        })
      );
      setIconUrls(urls);
      setLoading(false);
    };
    
    loadIcons();
  }, [champions]);

  // Champion icon component
  const ChampionIcon = ({ championName }: { championName: string }) => {
    return (
      <ImageWithFallback
        src={iconUrls[championName] || ""}
        alt={championName}
        className="size-full object-cover"
      />
    );
  };

  return (
    <div className="relative size-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* Background Image */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1920"
          alt="Background"
          className="size-full object-cover opacity-5"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#0a1929]/90 via-[#010A13]/90 to-[#0a0515]/90" />
      </div>

      {/* Animated gradient orbs - blue theme like KDA */}
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

      <motion.div
        animate={{
          x: [0, -80, 0],
          y: [0, 60, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
        className="absolute bottom-0 left-1/4 w-80 h-80 bg-[#5DADE2] rounded-full blur-[120px] opacity-20"
      />

      {/* Content Container - Brute fitted */}
      <div className="relative z-10 flex flex-col items-center justify-center px-6">
        
        {/* Title - LoL Gold Theme */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-6 sm:mb-8"
        >
          <h1 className="text-2xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl bg-gradient-to-r from-[#FFD700] via-[#C8AA6E] to-[#FFD700] bg-clip-text text-transparent" style={{ fontFamily: 'Georgia, serif' }}>
            Your Top Champions
          </h1>
        </motion.div>

        {/* Champions List */}
        <div className="w-full max-w-md lg:max-w-2xl space-y-5 sm:space-y-6">
          {topFive.map((champion, index) => (
            <motion.div
              key={champion.name}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{
                delay: 0.3 + index * 0.15,
                duration: 0.5,
                ease: [0.4, 0, 0.2, 1]
              }}
              className="flex items-center gap-4 sm:gap-5 lg:gap-6"
            >
              {/* Number - LoL Gold */}
              <div className="text-2xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl text-[#C8AA6E] w-7 sm:w-8 lg:w-12 xl:w-16 flex-shrink-0 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {index + 1}
              </div>

              {/* Champion Image with Gold Frame */}
              <div className="relative w-16 h-16 sm:w-16 sm:h-16 md:w-18 md:h-18 lg:w-24 lg:h-24 xl:w-28 xl:h-28 flex-shrink-0" style={{marginTop: '2px', marginBottom: '2px'}}>
                {/* Gold Border Frame */}
                <div className="relative w-full h-full border-2 lg:border-3 border-[#C8AA6E] rounded-sm overflow-hidden bg-[#0A0E15]">
                  {!loading ? (
                    <ChampionIcon championName={champion.name} />
                  ) : (
                    <div className="w-full h-full bg-[#1a1f2e] animate-pulse"></div>
                  )}
                </div>
                
                {/* Corner Accents - Small gold corners */}
                <div className="absolute top-0 left-0 w-2 h-2 lg:w-3 lg:h-3 border-t-2 border-l-2 border-[#FFD700]"></div>
                <div className="absolute top-0 right-0 w-2 h-2 lg:w-3 lg:h-3 border-t-2 border-r-2 border-[#FFD700]"></div>
                <div className="absolute bottom-0 left-0 w-2 h-2 lg:w-3 lg:h-3 border-b-2 border-l-2 border-[#FFD700]"></div>
                <div className="absolute bottom-0 right-0 w-2 h-2 lg:w-3 lg:h-3 border-b-2 border-r-2 border-[#FFD700]"></div>
              </div>

              {/* Champion Info */}
              <div className="flex-1 min-w-0">
                {/* Champion Name - BIG, White */}
                <h2 className="text-lg sm:text-lg md:text-xl lg:text-2xl xl:text-3xl text-white truncate mb-0.5" style={{ fontFamily: 'Georgia, serif' }}>
                  {champion.name}
                </h2>
                
                {/* Stats - LoL Theme Colors */}
                <p className="text-xs sm:text-xs lg:text-sm xl:text-base">
                  <span className="text-[#0AC8B9]">{champion.games} games</span>
                  <span className="text-[#A09B8C]"> • </span>
                  <span className="text-[#C8AA6E]">{champion.winRate}% WR</span>
                  <span className="text-[#A09B8C]"> • </span>
                  <span className="text-[#FFD700]">{champion.kda.toFixed(2)} KDA</span>
                  <span className="text-[#A09B8C]"> • </span>
                  <span className="text-[#0AC8B9]">{champion.avgKills.toFixed(1)} Average kills</span>
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
