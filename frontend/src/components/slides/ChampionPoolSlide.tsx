import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect, useState } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import { getChampionIconUrl } from "../../utils/championImages";

interface ChampionPoolSlideProps {
  uniqueChampions: number;
  totalGames: number;
  diversityScore: number;
  championList: string[];
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

// Champion Icon Component with async loading
function ChampionIcon({ championName }: { championName: string }) {
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
      <div 
        className="size-full flex items-center justify-center bg-[#8B5CF6]/10"
      >
        <div className="w-4 h-4 border-2 border-[#8B5CF6] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <ImageWithFallback
      src={iconUrl}
      alt={championName}
      className="size-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
    />
  );
}

export function ChampionPoolSlide({
  uniqueChampions,
  totalGames,
  diversityScore,
  championList,
  aiHumor = "Talk about champion diversity! You're basically a one-person champion ocean. 🌊"
}: ChampionPoolSlideProps) {
  // Display ALL champions, not just 16
  const displayChampions = championList;

  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#2d0a4e] via-[#010A13] to-[#0a1929]">
      {/* Animated gradient */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.15, 0.25, 0.15],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#8B5CF6] rounded-full blur-[120px] opacity-20"
      />

      {/* Fixed Content Container */}
      <div className="relative z-10 size-full flex flex-col items-center w-full max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8">
        {/* Title and Number - Fixed at top */}
        <motion.div
          initial={{ opacity: 0, x: -100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2, duration: 0.8 }}
          className="text-center mb-4 sm:mb-6 flex-shrink-0"
        >
          <p className="text-sm sm:text-base md:text-lg text-[#A09B8C] uppercase tracking-[0.2em] sm:tracking-[0.3em] mb-2 sm:mb-3">
            You mastered
          </p>
          <div className="text-6xl sm:text-7xl md:text-8xl lg:text-9xl leading-none bg-gradient-to-br from-[#8B5CF6] via-[#A78BFA] to-[#C4B5FD] bg-clip-text text-transparent tabular-nums mb-2 sm:mb-3" style={{ fontFamily: 'Georgia, serif' }}>
            <Counter value={uniqueChampions} />
          </div>
          <p className="text-xl sm:text-2xl md:text-3xl text-white mb-1 sm:mb-2" style={{ fontFamily: 'Georgia, serif' }}>
            champions
          </p>
          <p className="text-xs sm:text-sm md:text-base text-[#A09B8C]">
            <span className="text-[#8B5CF6]">{diversityScore}%</span> diversity across {totalGames} games
          </p>
        </motion.div>

        {/* Scrollable Champion Grid */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="flex-1 w-full overflow-y-auto scrollbar-thin scrollbar-thumb-[#8B5CF6] scrollbar-track-[#8B5CF6]/10 px-2"
        >
          <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-1.5 sm:gap-2 w-full max-w-4xl mx-auto pb-4">
            {displayChampions.map((championName, idx) => (
              <motion.div
                key={championName}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8 + idx * 0.05, duration: 0.4, type: "spring" }}
                className="relative aspect-square group"
              >
                {/* Champion portrait */}
                <div 
                  className="size-full border-2 border-[#8B5CF6] overflow-hidden relative rounded-lg bg-[#8B5CF6]/10"
                >
                  <ChampionIcon championName={championName} />
                  
                  {/* Champion name overlay on hover */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-end p-1 sm:p-1.5">
                    <span className="text-white text-[9px] sm:text-[10px] md:text-xs font-bold truncate w-full text-center">{championName}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* AI Humor - Fixed at bottom */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.8, duration: 0.6 }}
          className="max-w-xl text-center px-4 mt-4 flex-shrink-0"
        >
          <p className="text-xs sm:text-sm md:text-base text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
