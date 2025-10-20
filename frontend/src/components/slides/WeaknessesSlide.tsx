import { motion } from "motion/react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import growthBg from "../../assets/growth.webp";

interface WeaknessesSlideProps {
  weaknesses: string[]; // Array of weakness descriptions from backend
  aiHumor?: string;
}

export function WeaknessesSlide({ 
  weaknesses,
  aiHumor = "Every legend has room to grow - even the greats started somewhere! 💪"
}: WeaknessesSlideProps) {
  // Get the first weakness as the main one to display
  const mainWeakness = weaknesses[0] || "No significant weaknesses detected";
  const additionalWeaknesses = weaknesses.slice(1);

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
            Areas to Improve
          </motion.h1>
        </motion.div>

        {/* Main Weakness - HUGE with animation */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.8, type: "spring" }}
          className="text-center"
        >
          <motion.h2 
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-white mb-3 sm:mb-4 leading-tight px-4" 
            style={{ fontFamily: 'Georgia, serif' }}
            animate={{
              opacity: [0.9, 1, 0.9],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
            }}
          >
            {mainWeakness}
          </motion.h2>
        </motion.div>

        {/* Decorative line */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="w-24 sm:w-32 h-px bg-gradient-to-r from-transparent via-[#0AC8B9] to-transparent"
        />

        {/* Additional Weaknesses and AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-center max-w-2xl mx-auto space-y-4 px-4"
        >
          {/* Additional Weaknesses List */}
          {additionalWeaknesses.length > 0 && (
            <div className="space-y-2">
              {additionalWeaknesses.map((weakness, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.2 + index * 0.1, duration: 0.5 }}
                  className="text-sm sm:text-base text-[#E8E6E3]/90 leading-relaxed flex items-start justify-center gap-2"
                  style={{ fontFamily: 'Georgia, serif' }}
                >
                  <span className="text-[#0AC8B9] mt-0.5">•</span>
                  <span>{weakness}</span>
                </motion.div>
              ))}
            </div>
          )}
          
          {/* AI Humor */}
          {aiHumor && (
            <motion.p 
              className="text-xs sm:text-sm text-[#0AC8B9] italic leading-relaxed pt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.6, duration: 0.8 }}
            >
              {aiHumor}
            </motion.p>
          )}
        </motion.div>
      </div>
    </div>
  );
}
