import { motion } from "motion/react";
import { Award, Star, Flame, Zap, Crown, Trophy } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";

interface Achievement {
  title: string;
  description: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  icon: 'award' | 'star' | 'flame' | 'zap' | 'crown' | 'trophy';
  dateEarned: string;
}

interface AchievementsSlideProps {
  achievements: Achievement[];
}

const iconMap = {
  award: Award,
  star: Star,
  flame: Flame,
  zap: Zap,
  crown: Crown,
  trophy: Trophy,
};

const rarityColors = {
  common: { border: '#A09B8C', glow: '#A09B8C', bg: '#78716C' },
  rare: { border: '#5B92E5', glow: '#5B92E5', bg: '#3B82F6' },
  epic: { border: '#8B5CF6', glow: '#8B5CF6', bg: '#7C3AED' },
  legendary: { border: '#C8AA6E', glow: '#FFD700', bg: '#C8AA6E' },
};

export function AchievementsSlide({ achievements }: AchievementsSlideProps) {
  return (
    <div className="relative size-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* LoL Character Background */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1920"
          alt="Background"
          className="size-full object-cover opacity-5"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#2d0a4e]/90 via-[#1a0b2e]/90 to-[#010A13]/90" />
      </div>

      {/* Twinkling stars */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-[#FFD700]"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1.5, 0],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            delay: i * 0.15,
          }}
        />
      ))}

      {/* Content */}
      <div className="relative z-10 w-full h-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8 md:py-12 flex flex-col overflow-y-auto scrollbar-hide">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, scale: 0, rotate: -180 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ delay: 0.2, duration: 1, type: "spring" }}
          className="text-center mb-6 sm:mb-8"
        >
          <Trophy className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 text-[#FFD700] mx-auto mb-3" />
          <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl bg-gradient-to-br from-[#FFD700] via-[#FDB931] to-[#C8AA6E] bg-clip-text text-transparent" style={{ fontFamily: 'Georgia, serif' }}>
            Hall of Achievements
          </h2>
        </motion.div>

        {/* AI Humor - At TOP */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="max-w-2xl mx-auto text-center mb-8 sm:mb-10"
        >
          <p className="text-xs sm:text-sm md:text-base lg:text-lg text-[#E8E6E3]/80 italic leading-relaxed">
            Achievement unlocked: Being absolutely legendary! 🏆
          </p>
        </motion.div>

        {/* Achievement Grid - 4 per row on large, 2 on small */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-5 flex-1">
          {achievements.map((achievement, idx) => {
            const Icon = iconMap[achievement.icon];
            const colors = rarityColors[achievement.rarity];
            
            return (
              <motion.div
                key={achievement.title}
                initial={{ opacity: 0, rotateX: -90 }}
                animate={{ opacity: 1, rotateX: 0 }}
                transition={{ 
                  delay: 0.7 + idx * 0.1, 
                  duration: 0.6,
                  type: "spring"
                }}
                className="relative group"
              >
                <div 
                  className="absolute inset-0 backdrop-blur-sm border"
                  style={{
                    background: `linear-gradient(to bottom right, ${colors.glow}20, transparent)`,
                    borderColor: `${colors.border}40`,
                  }}
                />
                
                <div className="relative p-3 sm:p-4 h-full flex flex-col">
                  {/* Icon with image background */}
                  <div className="mb-2 sm:mb-3 flex justify-center">
                    <div 
                      className="relative w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 flex items-center justify-center overflow-hidden"
                      style={{
                        background: `linear-gradient(to bottom right, ${colors.glow}, ${colors.bg})`,
                      }}
                    >
                      <ImageWithFallback 
                        src="https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=100"
                        alt="Achievement"
                        className="absolute inset-0 w-full h-full object-cover opacity-20"
                      />
                      <Icon className="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7 text-[#010A13] relative z-10" />
                    </div>
                  </div>

                  {/* Content */}
                  <div className="text-center flex-1 flex flex-col">
                    <h3 className="text-xs sm:text-sm md:text-base text-white mb-1 sm:mb-2 leading-tight" style={{ fontFamily: 'Georgia, serif' }}>
                      {achievement.title}
                    </h3>
                    <p className="text-[10px] sm:text-xs text-[#A09B8C] mb-2 sm:mb-3 leading-relaxed flex-1">
                      {achievement.description}
                    </p>

                    {/* Rarity badge */}
                    <div className="flex items-center justify-center">
                      <div 
                        className="text-[8px] sm:text-[9px] md:text-[10px] uppercase tracking-widest px-2 py-0.5 sm:py-1 border"
                        style={{
                          color: colors.glow,
                          borderColor: colors.border,
                          backgroundColor: `${colors.glow}10`,
                        }}
                      >
                        {achievement.rarity}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Hover glow */}
                <div 
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
                  style={{
                    background: `radial-gradient(circle at center, ${colors.glow}20, transparent)`,
                  }}
                />
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
