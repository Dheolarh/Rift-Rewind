import { motion } from "motion/react";
import { Zap, Target, Shield, Swords } from "lucide-react";

interface Strength {
  title: string;
  description: string;
  score: number;
  icon: 'zap' | 'target' | 'shield' | 'swords';
}

interface StrengthsSlideProps {
  strengths: Strength[];
}

const iconMap = {
  zap: Zap,
  target: Target,
  shield: Shield,
  swords: Swords,
};

export function StrengthsSlide({ strengths }: StrengthsSlideProps) {
  // Pick the top strength
  const topStrength = strengths[0];
  const Icon = iconMap[topStrength.icon];

  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#1a0b2e] via-[#010A13] to-[#2d0a4e]">
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
        className="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 bg-[#C8AA6E] rounded-full blur-[150px]"
      />

      {/* Content */}
      <div className="relative z-10 size-full flex flex-col items-center justify-center p-8">
        {/* Icon */}
        <motion.div
          initial={{ opacity: 0, rotate: -45 }}
          animate={{ opacity: 1, rotate: 0 }}
          transition={{ delay: 0.2, duration: 0.8, type: "spring" }}
        >
          <Icon className="w-16 h-16 sm:w-20 sm:h-20 text-[#C8AA6E] mb-8" />
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-center mb-12"
        >
          <p className="text-xl sm:text-2xl text-[#A09B8C] uppercase tracking-[0.3em]">
            Your biggest strength
          </p>
        </motion.div>

        {/* Strength title - HUGE */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7, duration: 0.8 }}
          className="mb-12 max-w-4xl"
        >
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl bg-gradient-to-br from-[#FFD700] via-[#C8AA6E] to-[#8B7548] bg-clip-text text-transparent text-center leading-tight" style={{ fontFamily: 'Georgia, serif' }}>
            {topStrength.title}
          </h1>
        </motion.div>

        {/* Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="mb-12"
        >
          <div className="text-6xl sm:text-7xl md:text-8xl text-[#C8AA6E] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
            {topStrength.score}%
          </div>
        </motion.div>

        {/* Description */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.6 }}
          className="max-w-2xl text-center mb-12"
        >
          <p className="text-base sm:text-lg text-[#E8E6E3]/80 leading-relaxed">
            {topStrength.description}
          </p>
        </motion.div>

        {/* Other strengths - minimal */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.6, duration: 0.6 }}
          className="flex flex-wrap items-center justify-center gap-6"
        >
          {strengths.slice(1, 4).map((strength, idx) => (
            <div key={strength.title} className="text-center">
              <div className="text-sm text-[#78716C] mb-1">{strength.title}</div>
              <div className="text-lg text-[#A09B8C]">{strength.score}%</div>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}
