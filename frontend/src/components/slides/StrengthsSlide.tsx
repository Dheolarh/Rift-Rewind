import { motion } from "motion/react";

interface Strength {
  title: string;
  description: string;
  score: number;
  icon: 'zap' | 'target' | 'shield' | 'swords';
}

interface StrengthsSlideProps {
  strengths: Strength[];
}

export function StrengthsSlide({ strengths }: StrengthsSlideProps) {
  // Pick the top strength
  const topStrength = strengths[0];

  return (
    <div className="relative w-full h-full overflow-hidden bg-gradient-to-br from-[#1a0b2e] via-[#0a0515] to-[#010A13] flex items-center justify-center">
      {/* Animated gradient orbs */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#C8AA6E] rounded-full blur-[120px]"
      />
      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
        className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-[#0AC8B9] rounded-full blur-[120px]"
      />

      {/* Floating particles for animation */}
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-[#FFD700]"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0, 1, 0],
            scale: [0, 1.5, 0],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.3,
          }}
        />
      ))}

      {/* Centered Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-4 sm:gap-6 px-4 sm:px-6 max-w-xl">
        {/* Title with animation */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center"
        >
          <motion.h1 
            className="text-xl sm:text-2xl md:text-3xl text-[#A09B8C] uppercase tracking-[0.3em]" 
            style={{ fontFamily: 'Georgia, serif' }}
            animate={{
              textShadow: [
                '0 0 10px rgba(200, 170, 110, 0)',
                '0 0 20px rgba(200, 170, 110, 0.6)',
                '0 0 10px rgba(200, 170, 110, 0)',
              ],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
            }}
          >
            Your Strength
          </motion.h1>
        </motion.div>

        {/* Strength Title - HUGE with animation */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.8, type: "spring" }}
          className="text-center"
        >
          <motion.h2 
            className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl bg-gradient-to-br from-[#FFD700] via-[#C8AA6E] to-[#8B7548] bg-clip-text text-transparent mb-3 sm:mb-4 leading-tight" 
            style={{ fontFamily: 'Georgia, serif' }}
            animate={{
              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: "linear"
            }}
          >
            {topStrength.title}
          </motion.h2>
          <motion.div 
            className="text-2xl sm:text-3xl md:text-4xl text-[#C8AA6E] tabular-nums" 
            style={{ fontFamily: 'Georgia, serif' }}
            animate={{
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
          >
            {topStrength.score}%
          </motion.div>
        </motion.div>

        {/* Decorative line */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="w-24 sm:w-32 h-px bg-gradient-to-r from-transparent via-[#C8AA6E] to-transparent"
        />

        {/* Description with fade in */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-center max-w-md space-y-3"
        >
          <motion.p 
            className="text-xs sm:text-sm text-[#E8E6E3]/90 leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2, duration: 0.8 }}
          >
            {topStrength.description}
          </motion.p>
          <motion.p 
            className="text-xs sm:text-sm text-[#FFD700] italic leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.4, duration: 0.8 }}
            animate-pulse
          >
            These are the skills that separate the good from the legendary! ⚡
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
