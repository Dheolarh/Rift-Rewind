import { motion, useMotionValue, useTransform, animate, AnimatePresence } from "motion/react";
import { useEffect, useState } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import { getChampionIconUrl } from "../../utils/championImages";

interface BestMatchSlideProps {
  matchId?: string;
  champion: string;
  kills: number;
  deaths: number;
  assists: number;
  kda: number;
  result?: string;
  duration?: number;
  gameMode?: string;
  timestamp: number;
  aiHumor?: string;
  showHumor?: boolean;
  onRequestNext?: () => void;
  onRequestPrevious?: () => void;
}

function Counter({ value, duration = 1.5, delay = 0 }: { value: number; duration?: number; delay?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, { duration, delay });
    return controls.stop;
  }, [value, duration, delay, count]);

  return <motion.span>{rounded}</motion.span>;
}

export function BestMatchSlide({
  champion,
  kills,
  deaths,
  assists,
  kda,
  result,
  timestamp,
  aiHumor = "Analyzing your legendary performance...",
  showHumor = false
}: BestMatchSlideProps) {
  const [championIcon, setChampionIcon] = useState<string>("");
  const [loading, setLoading] = useState(true);

  // Load champion icon
  useEffect(() => {
    const loadIcon = async () => {
      try {
        const url = await getChampionIconUrl(champion);
        setChampionIcon(url);
      } catch (error) {
        console.error('Failed to load champion icon:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadIcon();
  }, [champion]);

  // Format timestamp to readable date
  const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };
  return (
    <div className="relative w-full h-full overflow-hidden bg-gradient-to-br from-[#1a0b2e] via-[#010A13] to-[#2d0a4e] flex items-center justify-center px-4">
      {/* Animated gradient */}
      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-1/3 left-1/2 -translate-x-1/2 w-64 h-64 sm:w-80 sm:h-80 bg-[#C8AA6E] rounded-full blur-[150px]"
      />

      {/* Centered Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-3 sm:gap-4 max-w-md w-full">
        <AnimatePresence mode="wait">
          {!showHumor ? (
            // Stats Phase
            <motion.div
              key="stats"
              initial={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center gap-3 sm:gap-4 w-full"
            >
              {/* Title */}
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.6 }}
                className="text-center"
              >
                <h1 className="text-lg sm:text-xl md:text-2xl text-[#A09B8C] uppercase tracking-[0.3em]" style={{ fontFamily: 'Georgia, serif' }}>
                  Most Legendary Game
                </h1>
              </motion.div>

              {/* Champion Image */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4, duration: 0.6 }}
                className="w-40 h-40 border-2 border-[#C8AA6E] rounded-sm overflow-hidden bg-[#0A0E15]"
              >
                {!loading ? (
                  <ImageWithFallback
                    src={championIcon}
                    alt={champion}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-[#1a1f2e] animate-pulse flex items-center justify-center">
                    <div className="text-[#C8AA6E] text-sm">Loading...</div>
                  </div>
                )}
              </motion.div>

              {/* Champion Name & Date */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6, duration: 0.6 }}
                className="text-center"
              >
                <h2 className="text-2xl sm:text-3xl md:text-4xl text-white mb-1" style={{ fontFamily: 'Georgia, serif' }}>
                  {champion}
                </h2>
                <p className="text-xs text-[#A09B8C]">{formatDate(timestamp)}</p>
                {result && (
                  <p className={`text-sm mt-1 ${result === 'Victory' ? 'text-[#0AC8B9]' : 'text-[#C75050]'}`}>
                    {result}
                  </p>
                )}
              </motion.div>

              {/* K/D/A Stats */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.6 }}
                className="flex items-center justify-center gap-3 sm:gap-4 md:gap-6"
              >
                <div className="text-center">
                  <div className="text-xs text-[#A09B8C] uppercase tracking-wider mb-1">K</div>
                  <div className="text-2xl sm:text-3xl text-[#0AC8B9] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                    <Counter value={kills} duration={1.5} delay={0.9} />
                  </div>
                </div>

                <div className="w-px h-8 sm:h-10 bg-[#C8AA6E]/30" />

                <div className="text-center">
                  <div className="text-xs text-[#A09B8C] uppercase tracking-wider mb-1">D</div>
                  <div className="text-2xl sm:text-3xl text-white tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                    <Counter value={deaths} duration={1.5} delay={1.0} />
                  </div>
                </div>

                <div className="w-px h-8 sm:h-10 bg-[#C8AA6E]/30" />

                <div className="text-center">
                  <div className="text-xs text-[#A09B8C] uppercase tracking-wider mb-1">A</div>
                  <div className="text-2xl sm:text-3xl text-[#C8AA6E] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                    <Counter value={assists} duration={1.5} delay={1.1} />
                  </div>
                </div>
              </motion.div>

              {/* KDA */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2, duration: 0.6 }}
                className="text-center"
              >
                <div className="text-3xl sm:text-4xl md:text-5xl bg-gradient-to-r from-[#FFD700] via-[#C8AA6E] to-[#0AC8B9] bg-clip-text text-transparent tabular-nums mb-1" style={{ fontFamily: 'Georgia, serif' }}>
                  {kda.toFixed(1)}
                </div>
                <div className="text-xs text-[#A09B8C] uppercase tracking-[0.3em]">KDA</div>
              </motion.div>
            </motion.div>
          ) : (
            // Humor Phase
            <motion.div
              key="humor"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6 }}
              className="flex flex-col items-center justify-center w-full max-w-2xl px-6"
            >
              <p className="text-sm sm:text-base md:text-lg text-[#C8AA6E] leading-relaxed text-center">
                {aiHumor}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
