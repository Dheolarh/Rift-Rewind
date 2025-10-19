import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
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
  championName,
  kills,
  deaths,
  assists,
  kda,
  date,
  aiHumor = "This match was so epic, even the enemy team was probably cheering for you! 🎭"
}: BestMatchSlideProps) {
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
          style={{ width: '160px', height: '160px' }}
        >
          <ImageWithFallback
            src="https://images.unsplash.com/photo-1542751371-adc38448a05e?w=300"
            alt={championName}
            className="w-full h-full object-cover"
          />
        </motion.div>

        {/* Champion Name & Date */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="text-center"
        >
          <h2 className="text-2xl sm:text-3xl md:text-4xl text-white mb-1" style={{ fontFamily: 'Georgia, serif' }}>
            {championName}
          </h2>
          <p className="text-xs text-[#A09B8C]">{date}</p>
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

        {/* AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.4, duration: 0.6 }}
          className="text-center max-w-sm px-2"
        >
          <p className="text-xs text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
