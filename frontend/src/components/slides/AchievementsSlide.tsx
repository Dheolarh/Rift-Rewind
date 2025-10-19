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
  common: { border: '#A09B8C', glow: '#A09B8C', text: '#A09B8C' },
  rare: { border: '#5B92E5', glow: '#5B92E5', text: '#5B92E5' },
  epic: { border: '#8B5CF6', glow: '#8B5CF6', text: '#8B5CF6' },
  legendary: { border: '#C8AA6E', glow: '#FFD700', text: '#FFD700' },
};

export function AchievementsSlide({ achievements }: AchievementsSlideProps) {
  // Show only top 3 achievements
  const topAchievements = achievements.slice(0, 3);

  return (
    <div className="relative w-full h-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* LoL Character Background */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1920"
          alt="Background"
          className="w-full h-full object-cover opacity-5"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#2d0a4e]/90 via-[#1a0b2e]/90 to-[#010A13]/90" />
      </div>

      {/* Twinkling stars */}
      {[...Array(15)].map((_, i) => (
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
            delay: i * 0.2,
          }}
        />
      ))}

      {/* Centered Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-4 sm:gap-6 px-4 max-w-3xl">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center"
        >
          <h2 className="text-xl sm:text-2xl md:text-3xl bg-gradient-to-br from-[#FFD700] via-[#FDB931] to-[#C8AA6E] bg-clip-text text-transparent" style={{ fontFamily: 'Georgia, serif' }}>
            Hall of Achievements
          </h2>
        </motion.div>

        {/* AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-center max-w-lg"
        >
          <p className="text-xs sm:text-sm text-[#E8E6E3]/80 italic leading-relaxed">
            Achievement unlocked: Being absolutely legendary! 🏆
          </p>
        </motion.div>

        {/* Achievement Cards - Vertical Stack */}
        <div className="w-full max-w-md space-y-3 sm:space-y-4">
          {topAchievements.map((achievement, idx) => {
            const Icon = iconMap[achievement.icon];
            const colors = rarityColors[achievement.rarity];
            
            return (
              <motion.div
                key={achievement.title}
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ 
                  delay: 0.6 + idx * 0.15, 
                  duration: 0.5
                }}
                className="relative group"
              >
                {/* Card Background */}
                <div 
                  className="absolute inset-0 bg-[#0A1428]/80 backdrop-blur-sm border"
                  style={{
                    borderColor: `${colors.border}60`,
                  }}
                />
                
                {/* Card Content */}
                <div className="relative p-4 sm:p-5 flex items-center gap-4">
                  {/* Icon */}
                  <div 
                    className="flex-shrink-0 w-12 h-12 sm:w-14 sm:h-14 flex items-center justify-center rounded-full border-2"
                    style={{
                      borderColor: colors.border,
                      backgroundColor: `${colors.glow}20`,
                    }}
                  >
                    <Icon className="w-6 h-6 sm:w-7 sm:h-7" style={{ color: colors.glow }} />
                  </div>

                  {/* Text Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <h3 className="text-sm sm:text-base text-white leading-tight" style={{ fontFamily: 'Georgia, serif' }}>
                        {achievement.title}
                      </h3>
                      <span 
                        className="flex-shrink-0 text-xs uppercase tracking-wider px-2 py-0.5 border rounded-full"
                        style={{
                          color: colors.text,
                          borderColor: colors.border,
                          backgroundColor: `${colors.glow}10`,
                        }}
                      >
                        {achievement.rarity}
                      </span>
                    </div>
                    <p className="text-xs sm:text-sm text-[#A09B8C] leading-relaxed mb-1">
                      {achievement.description}
                    </p>
                    <p className="text-xs text-[#78716C]">
                      Earned: {achievement.dateEarned}
                    </p>
                  </div>
                </div>

                {/* Hover glow */}
                <div 
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
                  style={{
                    background: `radial-gradient(circle at center, ${colors.glow}15, transparent)`,
                  }}
                />
              </motion.div>
            );
          })}
        </div>

        {/* More achievements indicator */}
        {achievements.length > 3 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2, duration: 0.6 }}
            className="text-center"
          >
            <p className="text-xs text-[#A09B8C]/60">
              + {achievements.length - 3} more achievements unlocked
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
