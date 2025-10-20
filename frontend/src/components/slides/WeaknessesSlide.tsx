import { motion } from "motion/react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import growthBg from "../../assets/growth.webp";

interface Weakness {
  title: string;
  description: string;
  improvement: string;
  icon: 'alert' | 'trending' | 'xcircle' | 'brain';
}

interface WeaknessesSlideProps {
  weaknesses: Weakness[];
}

export function WeaknessesSlide({ weaknesses }: WeaknessesSlideProps) {
  // Pick the first area to improve
  const firstWeakness = weaknesses[0];

  return (
    <div className="relative w-full h-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* Background Image */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={growthBg}
          alt="Growth Background"
          className="w-full h-full object-cover opacity-15"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a0b2e]/90 via-[#0a0515]/95 to-[#010A13]/98" />
      </div>

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
      {[...Array(10)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-[#0AC8B9]"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, 30, 0],
            opacity: [0, 0.8, 0],
            scale: [0, 1.2, 0],
          }}
          transition={{
            duration: 4 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.4,
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
                '0 0 10px rgba(10, 200, 185, 0)',
                '0 0 20px rgba(10, 200, 185, 0.6)',
                '0 0 10px rgba(10, 200, 185, 0)',
              ],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
            }}
          >
            Room to Grow
          </motion.h1>
        </motion.div>

        {/* Weakness Title - HUGE with animation */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.8, type: "spring" }}
          className="text-center"
        >
          <motion.h2 
            className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl text-white mb-2 sm:mb-3 leading-tight" 
            style={{ fontFamily: 'Georgia, serif' }}
            animate={{
              opacity: [0.9, 1, 0.9],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
            }}
          >
            {firstWeakness.title}
          </motion.h2>
        </motion.div>

        {/* Decorative line */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="w-24 sm:w-32 h-px bg-gradient-to-r from-transparent via-[#0AC8B9] to-transparent"
        />

        {/* Description & Improvement with fade in */}
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
            {firstWeakness.description}
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.4, duration: 0.8 }}
            className="pt-2"
          >
            <div className="text-xs sm:text-sm text-[#0AC8B9] uppercase tracking-wider mb-2">
              How to improve
            </div>
            <p className="text-xs sm:text-sm text-white/90 leading-relaxed mb-2">
              {firstWeakness.improvement}
            </p>
          </motion.div>

          <motion.p 
            className="text-xs sm:text-sm text-[#0AC8B9] italic leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.6, duration: 0.8 }}
          >
            Every weakness is just a strength waiting to be discovered!
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
