import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { Trophy } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";

interface BestMatchSlideProps {
  championName: string;
  kills: number;
  deaths: number;
  assists: number;
  kda: number;
  date: string;
  aiHumor?: string;
}

function Counter({ value, duration = 1.5 }: { value: number; duration?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, { duration, delay: 0.7 });
    return controls.stop;
  }, [value, duration, count]);

  return <motion.span>{rounded}</motion.span>;
}

export function BestMatchSlide({
  championName,
  kills,
  deaths,
  assists,
  kda,
  date,
  aiHumor = "This match was so epic, even the enemy team was probably cheering for you! 🎭"
}: BestMatchSlideProps) {
  return (
    <div className="relative size-full overflow-hidden bg-[#010A13]">
      {/* LoL Character Background */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1560419450-6c59831ba551?w=1920"
          alt="Background"
          className="size-full object-cover opacity-5"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#2d0a4e]/90 via-[#1a0b2e]/90 to-[#010A13]/90" />
      </div>

      {/* Animated particles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 rounded-full bg-[#FFD700]"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            scale: [0, 1, 0],
            opacity: [0, 0.8, 0],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            delay: i * 0.2,
          }}
        />
      ))}

      {/* Scrollable Content */}
      <div className="relative z-10 size-full overflow-y-auto scrollbar-hide">
        <div className="min-h-full flex flex-col items-center justify-center w-full max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          {/* Trophy icon */}
          <motion.div
            initial={{ opacity: 0, scale: 0, rotateY: -180 }}
            animate={{ opacity: 1, scale: 1, rotateY: 0 }}
            transition={{ delay: 0.2, duration: 0.8, type: "spring" }}
            className="mb-4 sm:mb-6"
          >
            <Trophy className="w-12 h-12 sm:w-16 sm:h-16 md:w-20 md:h-20 text-[#FFD700]" />
          </motion.div>

          {/* Title */}
          <motion.div
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4, duration: 0.7 }}
            className="text-center mb-6 sm:mb-8"
          >
            <p className="text-sm sm:text-base md:text-lg text-[#A09B8C] uppercase tracking-[0.2em] sm:tracking-[0.3em] mb-2 sm:mb-3">
              Your Most Legendary Game
            </p>
            <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl text-white mb-2" style={{ fontFamily: 'Georgia, serif' }}>
              {championName}
            </h2>
            <p className="text-xs sm:text-sm md:text-base text-[#78716C]">
              {date}
            </p>
          </motion.div>

          {/* KDA Display */}
          <motion.div
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="mb-6 sm:mb-8"
          >
            <div className="flex items-center justify-center gap-2 sm:gap-3 md:gap-4">
              <span className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-[#0AC8B9] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                <Counter value={kills} duration={1} />
              </span>
              <span className="text-2xl sm:text-3xl md:text-4xl text-[#78716C]">/</span>
              <span className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-white tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                <Counter value={deaths} duration={1} />
              </span>
              <span className="text-2xl sm:text-3xl md:text-4xl text-[#78716C]">/</span>
              <span className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-[#C8AA6E] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                <Counter value={assists} duration={1} />
              </span>
            </div>
          </motion.div>

          {/* KDA Ratio */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2, duration: 0.6 }}
            className="text-center mb-6 sm:mb-8"
          >
            <div className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl bg-gradient-to-r from-[#FFD700] to-[#0AC8B9] bg-clip-text text-transparent tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              {kda.toFixed(1)}
            </div>
            <div className="text-xs sm:text-sm md:text-base text-[#A09B8C] uppercase tracking-wider mt-1 sm:mt-2">
              KDA Ratio
            </div>
          </motion.div>

          {/* AI Humor */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.5, duration: 0.6 }}
            className="max-w-xl text-center px-4"
          >
            <p className="text-xs sm:text-sm md:text-base text-[#E8E6E3]/80 italic leading-relaxed">
              {aiHumor}
            </p>
          </motion.div>

          {/* Bottom Spacing */}
          <div className="h-4 sm:h-6" />
        </div>
      </div>
    </div>
  );
}
