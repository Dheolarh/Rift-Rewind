import { motion } from "motion/react";
import { AlertTriangle, TrendingDown, XCircle, Brain } from "lucide-react";

interface Weakness {
  title: string;
  description: string;
  improvement: string;
  icon: 'alert' | 'trending' | 'xcircle' | 'brain';
}

interface WeaknessesSlideProps {
  weaknesses: Weakness[];
}

const iconMap = {
  alert: AlertTriangle,
  trending: TrendingDown,
  xcircle: XCircle,
  brain: Brain,
};

export function WeaknessesSlide({ weaknesses }: WeaknessesSlideProps) {
  // Pick the first area to improve
  const firstWeakness = weaknesses[0];
  const Icon = iconMap[firstWeakness.icon];

  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#0a1929] via-[#010A13] to-[#1a0b2e]">
      {/* Animated gradient */}
      <motion.div
        animate={{
          x: [-50, 50, -50],
          y: [0, 30, 0],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#0AC8B9] rounded-full blur-[150px] opacity-30"
      />

      {/* Content */}
      <div className="relative z-10 size-full flex flex-col items-center justify-center p-8">
        {/* Icon */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          <Icon className="w-16 h-16 sm:w-20 sm:h-20 text-[#0AC8B9] mb-8" />
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-center mb-12"
        >
          <p className="text-xl sm:text-2xl text-[#A09B8C] uppercase tracking-[0.3em]">
            Room to grow
          </p>
        </motion.div>

        {/* Weakness title */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7, duration: 0.8 }}
          className="mb-12 max-w-4xl"
        >
          <h1 className="text-5xl sm:text-6xl md:text-7xl text-white text-center leading-tight" style={{ fontFamily: 'Georgia, serif' }}>
            {firstWeakness.title}
          </h1>
        </motion.div>

        {/* Description */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="max-w-2xl text-center mb-12"
        >
          <p className="text-base sm:text-lg text-[#E8E6E3]/80 leading-relaxed">
            {firstWeakness.description}
          </p>
        </motion.div>

        {/* Improvement tip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.6 }}
          className="max-w-2xl text-center mb-12"
        >
          <p className="text-sm sm:text-base text-[#0AC8B9] uppercase tracking-wider mb-3">
            💡 How to improve
          </p>
          <p className="text-base sm:text-lg text-white leading-relaxed">
            {firstWeakness.improvement}
          </p>
        </motion.div>

        {/* Encouragement */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.6, duration: 0.6 }}
          className="max-w-2xl text-center"
        >
          <p className="text-base sm:text-lg text-[#E8E6E3]/80 italic leading-relaxed">
            Every legend has areas to improve. That's what makes the climb worth it! 🚀
          </p>
        </motion.div>
      </div>
    </div>
  );
}
