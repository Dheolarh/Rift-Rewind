import { motion } from "motion/react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import progressBg from "../../assets/progress.webp";

interface StrengthsSlideProps {
  strengths: string[]; // Array of strength descriptions from backend
  aiAnalysis?: string; // AI-generated coaching analysis
}

export function StrengthsSlide({ 
  strengths,
  aiAnalysis = "Analyzing your gameplay strengths..."
}: StrengthsSlideProps) {
  // Get the first strength as the main one to display
  const mainStrength = strengths[0] || "No strengths detected";

  return (
    <div className="relative w-full h-full overflow-hidden bg-[#010A13]">
      {/* Background Image */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={progressBg}
          alt="Progress Background"
          className="w-full h-full object-cover opacity-15"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a0b2e]/90 via-[#010A13]/95 to-[#2d0a4e]/98" />
      </div>

      {/* Animated upward gradient */}
      <motion.div
        animate={{
          y: [0, -50, 0],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-1/2 bg-gradient-to-t from-[#0AC8B9]/30 to-transparent"
      />

      {/* Content */}
      <div className="relative z-10 w-full h-full flex flex-col items-center justify-center px-4 sm:px-6 md:px-8 py-8 sm:py-10 gap-2 sm:gap-3 md:gap-4">
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
            Your Strengths
          </motion.h1>
        </motion.div>

        {/* Main Strength - Smaller size */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.8, type: "spring" }}
          className="text-center"
        >
          <motion.h2 
            className="text-xl sm:text-2xl md:text-3xl bg-gradient-to-br from-[#FFD700] via-[#C8AA6E] to-[#8B7548] bg-clip-text text-transparent mb-2 sm:mb-3 leading-tight px-4" 
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
            {mainStrength.replace(/\.\d+%/g, '%').replace(/(\d+)\.\d+/g, '$1')}
          </motion.h2>
        </motion.div>

        {/* Decorative line (ensure visible across screens) - inline styles to avoid rendering/antialiasing issues */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          style={{
            width: 'min(8rem, 32vw)',
            height: '2px',
            background: 'linear-gradient(to right, rgba(0,0,0,0), rgba(200,170,110,0.9), rgba(0,0,0,0))',
            transformOrigin: 'left',
            zIndex: 20,
            position: 'relative'
          }}
        />

        {/* AI Analysis Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-center max-w-3xl mx-auto space-y-2 px-4"
        >
          {/* Display AI analysis content as white text without bullet points */}
          {aiAnalysis && (
            <motion.div 
              className="space-y-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2, duration: 0.8 }}
            >
              {aiAnalysis.split('\n').filter(line => line.trim()).map((line, index) => {
                // Remove bullet points and clean up the text
                const cleanedLine = line.replace(/^[•\-*]\s*/, '').trim();
                // Remove decimals from percentages and numbers
                const noDecimals = cleanedLine.replace(/(\d+)\.\d+%/g, '$1%').replace(/(\d+)\.\d+(?!\d)/g, '$1');
                
                return cleanedLine ? (
                  <motion.p
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.3 + index * 0.1, duration: 0.5 }}
                    className="text-base sm:text-lg md:text-xl text-white/90 leading-relaxed"
                    style={{ fontFamily: 'Georgia, serif' }}
                  >
                    {noDecimals}
                  </motion.p>
                ) : null;
              })}
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
}