import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";

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

export function ChampionPoolSlide({
  uniqueChampions,
  mostPlayedRole,
  champions,
}: ChampionPoolSlideProps) {
  const displayChampions = champions.slice(0, 16);

  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#2d0a4e] via-[#010A13] to-[#0a1929] flex items-center justify-center">
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

      {/* Content */}
      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-8 md:px-12 py-8 flex flex-col items-center justify-center min-h-full">
        {/* Title and Number */}
        <motion.div
          initial={{ opacity: 0, x: -100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2, duration: 0.8 }}
          className="text-center mb-8 sm:mb-12"
        >
          <p className="text-lg sm:text-xl md:text-2xl text-[#A09B8C] uppercase tracking-[0.3em] mb-4">
            You mastered
          </p>
          <div className="text-[80px] sm:text-[120px] md:text-[160px] lg:text-[200px] leading-none bg-gradient-to-br from-[#8B5CF6] via-[#A78BFA] to-[#C4B5FD] bg-clip-text text-transparent tabular-nums mb-4" style={{ fontFamily: 'Georgia, serif' }}>
            <Counter value={uniqueChampions} />
          </div>
          <p className="text-2xl sm:text-3xl md:text-4xl text-white mb-2" style={{ fontFamily: 'Georgia, serif' }}>
            champions
          </p>
          <p className="text-base sm:text-lg text-[#A09B8C]">
            mostly in <span className="text-[#8B5CF6]">{mostPlayedRole}</span>
          </p>
        </motion.div>

        {/* Champion Grid */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2 sm:gap-3 mb-8 sm:mb-12 max-w-5xl"
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
                className="size-full border overflow-hidden relative"
                style={{ 
                  borderColor: getRoleColor(champ.role),
                  backgroundColor: `${getRoleColor(champ.role)}10`
                }}
              >
                <ImageWithFallback
                  src={`https://images.unsplash.com/photo-1614294148960-9aa740632a87?w=200`}
                  alt={champ.name}
                  className="size-full object-cover opacity-50 group-hover:opacity-100 transition-opacity"
                />
                {/* Games count overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-center p-1">
                  <span className="text-white text-[10px] sm:text-xs">{champ.games}</span>
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
          className="max-w-2xl text-center"
        >
          <p className="text-sm sm:text-base md:text-lg text-[#E8E6E3]/80 italic leading-relaxed">
            Talk about champion diversity! You're basically a one-person champion ocean. 🌊
          </p>
        </motion.div>
      </div>
    </div>
  );
}
