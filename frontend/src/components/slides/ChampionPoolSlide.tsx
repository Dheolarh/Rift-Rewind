import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect, useState } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import { getChampionIconUrl } from "../../utils/championImages";

interface Champion {
  name: string;
  games: number;
  role: string;
}

interface ChampionPoolSlideProps {
  uniqueChampions: number;
  mostPlayedRole: string;
  champions: Champion[];
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

const getRoleColor = (role: string) => {
  const colors: Record<string, string> = {
    Mid: "#C8AA6E",
    Jungle: "#0AC8B9",
    Support: "#8B5CF6",
    ADC: "#EF4444",
    Top: "#F59E0B",
  };
  return colors[role] || "#A09B8C";
};

// Champion Icon Component with async loading
function ChampionIcon({ championName, role }: { championName: string; role: string }) {
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
        className="size-full flex items-center justify-center"
        style={{ backgroundColor: `${getRoleColor(role)}10` }}
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
  mostPlayedRole,
  champions,
}: ChampionPoolSlideProps) {
  const displayChampions = champions.slice(0, 16);

  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#2d0a4e] via-[#010A13] to-[#0a1929]">
      {/* Animated gradient */}
      <motion.div
        animate={{
          rotate: [0, 180, 360],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear"
        }}
        className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#8B5CF6] rounded-full blur-[120px] opacity-20"
      />

      {/* Scrollable Content */}
      <div className="relative z-10 size-full overflow-y-auto scrollbar-hide">
        <div className="min-h-full flex flex-col items-center justify-center w-full max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8">
          {/* Title and Number */}
          <motion.div
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="text-center mb-4 sm:mb-6"
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
              mostly in <span className="text-[#8B5CF6]">{mostPlayedRole}</span>
            </p>
          </motion.div>

          {/* Champion Grid */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-1.5 sm:gap-2 mb-4 sm:mb-6 w-full max-w-4xl"
          >
            {displayChampions.map((champ, idx) => (
              <motion.div
                key={champ.name}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8 + idx * 0.05, duration: 0.4, type: "spring" }}
                className="relative aspect-square group"
              >
                {/* Champion portrait */}
                <div 
                  className="size-full border-2 overflow-hidden relative rounded-lg"
                  style={{ 
                    borderColor: getRoleColor(champ.role),
                    backgroundColor: `${getRoleColor(champ.role)}10`
                  }}
                >
                  <ChampionIcon championName={champ.name} role={champ.role} />
                  
                  {/* Games count overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-end p-1 sm:p-1.5">
                    <span className="text-white text-[9px] sm:text-[10px] md:text-xs font-bold truncate w-full text-center">{champ.name}</span>
                    <span className="text-white/80 text-[8px] sm:text-[9px]">{champ.games} games</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* AI Humor */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.8, duration: 0.6 }}
            className="max-w-xl text-center px-4"
          >
            <p className="text-xs sm:text-sm md:text-base text-[#E8E6E3]/80 italic leading-relaxed">
              Talk about champion diversity! You're basically a one-person champion ocean. 🌊
            </p>
          </motion.div>

          {/* Bottom Spacing */}
          <div className="h-4 sm:h-6" />
        </div>
      </div>
    </div>
  );
}
