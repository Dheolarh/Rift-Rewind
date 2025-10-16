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
    <div className="relative size-full overflow-hidden bg-[#010A13]">
      {/* Background with gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#1a0b2e]/40 via-[#010A13] to-[#0a1428]" />

      {/* Animated particles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full bg-[#C8AA6E]"
          style={{
            width: `${Math.random() * 3 + 1}px`,
            height: `${Math.random() * 3 + 1}px`,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}

      {/* Scrollable Content */}
      <div className="relative z-10 size-full overflow-y-auto scrollbar-hide">
        <div className="min-h-full flex flex-col items-center justify-center px-4 sm:px-6 py-8 sm:py-10">
          
          {/* Centered Title with Slide-In Animation */}
          <motion.div
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, ease: [0.4, 0.0, 0.2, 1] }}
            className="text-center mb-8 sm:mb-12 md:mb-16"
          >
            <h1 
              className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-[#C8AA6E] uppercase tracking-wider"
              style={{ fontFamily: 'Georgia, serif' }}
            >
              Most Legendary Game
            </h1>
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ delay: 0.3, duration: 0.7 }}
              className="h-px bg-gradient-to-r from-transparent via-[#C8AA6E] to-transparent mt-3 sm:mt-4 max-w-md mx-auto"
            />
          </motion.div>

          {/* Horizontal Layout - Image Left, Stats Right */}
          <div className="w-full max-w-6xl flex flex-col lg:flex-row items-center justify-center gap-8 sm:gap-10 lg:gap-16">
            
            {/* LEFT SIDE - Champion Image */}
            <motion.div
              initial={{ opacity: 0, x: -100 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5, duration: 0.6, type: "spring", bounce: 0.3 }}
              className="relative flex-shrink-0"
            >
              <div 
                className="relative w-64 h-80 sm:w-72 sm:h-96 md:w-80 md:h-[28rem] lg:w-96 lg:h-[32rem] overflow-hidden border-2 border-[#C8AA6E]"
                style={{
                  background: 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 50%, #7C3AED 100%)',
                }}
              >
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&h=900&fit=crop"
                  alt={championName}
                  className="size-full object-cover opacity-80"
                />
                
                {/* Glow effect */}
                <div 
                  className="absolute inset-0"
                  style={{
                    background: 'linear-gradient(180deg, transparent 0%, rgba(139, 92, 246, 0.3) 100%)',
                  }}
                />
              </div>

              {/* Decorative corners */}
              <div className="absolute -top-2 -left-2 w-8 h-8 sm:w-10 sm:h-10 border-t-2 border-l-2 border-[#C8AA6E]" />
              <div className="absolute -top-2 -right-2 w-8 h-8 sm:w-10 sm:h-10 border-t-2 border-r-2 border-[#C8AA6E]" />
              <div className="absolute -bottom-2 -left-2 w-8 h-8 sm:w-10 sm:h-10 border-b-2 border-l-2 border-[#C8AA6E]" />
              <div className="absolute -bottom-2 -right-2 w-8 h-8 sm:w-10 sm:h-10 border-b-2 border-r-2 border-[#C8AA6E]" />
            </motion.div>

            {/* RIGHT SIDE - Stats */}
            <div className="flex-1 flex flex-col items-center lg:items-start justify-center max-w-xl">
              
              {/* Champion Name */}
              <motion.div
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7, duration: 0.5 }}
                className="text-center lg:text-left mb-2 sm:mb-3"
              >
                <h2 
                  className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-white"
                  style={{ fontFamily: 'Georgia, serif' }}
                >
                  {championName}
                </h2>
              </motion.div>

              {/* Date */}
              <motion.div
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.9, duration: 0.5 }}
                className="mb-6 sm:mb-8"
              >
                <p className="text-sm sm:text-base md:text-lg text-[#A09B8C] text-center lg:text-left">
                  {date}
                </p>
              </motion.div>

              {/* Stats Grid - K/D/A */}
              <motion.div
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.1, duration: 0.6 }}
                className="grid grid-cols-3 gap-6 sm:gap-8 mb-6 sm:mb-8"
              >
                {/* Kills */}
                <motion.div 
                  className="text-center"
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.3, duration: 0.5, type: "spring", bounce: 0.4 }}
                >
                  <motion.div 
                    className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider mb-2"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.4, duration: 0.4 }}
                  >
                    Kills
                  </motion.div>
                  <div 
                    className="text-4xl sm:text-5xl md:text-6xl text-[#0AC8B9] tabular-nums"
                    style={{ fontFamily: 'Georgia, serif' }}
                  >
                    <Counter value={kills} duration={1.5} delay={1.5} />
                  </div>
                </motion.div>

                {/* Deaths */}
                <motion.div 
                  className="text-center"
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.4, duration: 0.5, type: "spring", bounce: 0.4 }}
                >
                  <motion.div 
                    className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider mb-2"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.5, duration: 0.4 }}
                  >
                    Death
                  </motion.div>
                  <div 
                    className="text-4xl sm:text-5xl md:text-6xl text-white tabular-nums"
                    style={{ fontFamily: 'Georgia, serif' }}
                  >
                    <Counter value={deaths} duration={1.5} delay={1.6} />
                  </div>
                </motion.div>

                {/* Assists */}
                <motion.div 
                  className="text-center"
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.5, duration: 0.5, type: "spring", bounce: 0.4 }}
                >
                  <motion.div 
                    className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider mb-2"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.6, duration: 0.4 }}
                  >
                    Assists
                  </motion.div>
                  <div 
                    className="text-4xl sm:text-5xl md:text-6xl text-[#C8AA6E] tabular-nums"
                    style={{ fontFamily: 'Georgia, serif' }}
                  >
                    <Counter value={assists} duration={1.5} delay={1.7} />
                  </div>
                </motion.div>
              </motion.div>

              {/* Horizontal Line */}
              <motion.div
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ delay: 1.8, duration: 0.7 }}
                className="w-full h-px bg-gradient-to-r from-transparent via-[#C8AA6E] to-transparent mb-6 sm:mb-8"
              />

              {/* KDA Display */}
              <motion.div
                initial={{ opacity: 0, scale: 0.7, x: 100 }}
                animate={{ opacity: 1, scale: 1, x: 0 }}
                transition={{ delay: 2, duration: 0.6, type: "spring", bounce: 0.3 }}
                className="text-center lg:text-left mb-4 sm:mb-6"
              >
                <motion.div
                  animate={{
                    textShadow: [
                      '0 0 20px rgba(200, 170, 110, 0.6)',
                      '0 0 40px rgba(200, 170, 110, 0.8), 0 0 60px rgba(10, 200, 185, 0.4)',
                      '0 0 20px rgba(200, 170, 110, 0.6)',
                    ],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="text-6xl sm:text-7xl md:text-8xl bg-gradient-to-r from-[#FFD700] via-[#C8AA6E] to-[#0AC8B9] bg-clip-text text-transparent mb-2 sm:mb-3 tabular-nums"
                  style={{ fontFamily: 'Georgia, serif' }}
                >
                  {kda.toFixed(1)}
                </motion.div>
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 2.2, duration: 0.5 }}
                  className="text-sm sm:text-base text-[#A09B8C] uppercase tracking-[0.3em]"
                  style={{ fontFamily: 'Georgia, serif' }}
                >
                  KDA
                </motion.div>
              </motion.div>

              {/* AI Text */}
              <motion.div
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 2.4, duration: 0.6 }}
                className="text-center lg:text-left"
              >
                <p className="text-xs sm:text-sm md:text-base text-[#E8E6E3]/80 italic leading-relaxed">
                  {aiHumor}
                </p>
              </motion.div>

            </div>
          </div>

          {/* Bottom Spacing */}
          <div className="h-6 sm:h-8" />
        </div>
      </div>

      {/* Ambient Glows */}
      <motion.div
        className="absolute top-1/3 left-1/4 w-96 h-96 bg-[#8B5CF6] rounded-full blur-[120px] opacity-20 pointer-events-none"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.15, 0.25, 0.15],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-[#C8AA6E] rounded-full blur-[120px] opacity-20 pointer-events-none"
        animate={{
          scale: [1.2, 1, 1.2],
          opacity: [0.15, 0.25, 0.15],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2.5
        }}
      />
    </div>
  );
}
