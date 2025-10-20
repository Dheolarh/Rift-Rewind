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
  champions,
}: FavoriteChampionsSlideProps) {
  // Show top 5 champions
  const topFive = champions.slice(0, 5);

  // Champion icon component with dynamic loading
  const ChampionIcon = ({ championName }: { championName: string }) => {
    const [iconUrl, setIconUrl] = useState<string>("");

    useEffect(() => {
      getChampionIconUrl(championName).then(setIconUrl);
    }, [championName]);

    return (
      <ImageWithFallback
        src={iconUrl}
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
          <h1 className="text-2xl sm:text-2xl md:text-3xl bg-gradient-to-r from-[#FFD700] via-[#C8AA6E] to-[#F0E6D2] bg-clip-text text-transparent" style={{ fontFamily: 'Georgia, serif' }}>
            Your Top Champions
          </h1>
        </motion.div>

        {/* Champions List */}
        <div className="w-full max-w-md space-y-4 sm:space-y-4">
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
              className="flex items-center gap-4 sm:gap-4"
            >
              {/* Number - LoL Gold */}
              <div className="text-2xl sm:text-2xl md:text-3xl text-[#C8AA6E] w-7 sm:w-8 flex-shrink-0 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {index + 1}
              </div>

              {/* Champion Image with Gold Frame - NO corner accents */}
              <div className="relative w-14 h-14 sm:w-14 sm:h-14 md:w-16 md:h-16 flex-shrink-0">
                {/* Gold Frame Border */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#FFD700] via-[#C8AA6E] to-[#8B7548] p-[2px]">
                  <div className="w-full h-full bg-[#010A13] overflow-hidden">
                    <ChampionIcon championName={champion.name} />
                  </div>
                </div>
              </div>

              {/* Champion Info */}
              <div className="flex-1 min-w-0">
                {/* Champion Name - BIG, White */}
                <h2 className="text-lg sm:text-lg md:text-xl text-white truncate mb-0.5" style={{ fontFamily: 'Georgia, serif' }}>
                  {champion.name}
                </h2>
                
                {/* Stats - LoL Theme Colors */}
                <p className="text-xs sm:text-xs">
                  <span className="text-[#0AC8B9]">{champion.games} games</span>
                  <span className="text-[#A09B8C]"> • </span>
                  <span className="text-[#C8AA6E]">{champion.winRate}% WR</span>
                  <span className="text-[#A09B8C]"> • </span>
                  <span className="text-[#FFD700]">{champion.kda.toFixed(2)} KDA</span>
                  <span className="text-[#A09B8C]"> • </span>
                  <span className="text-[#5DADE2]">{champion.avgKills.toFixed(1)} K</span>
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
