import { motion } from "motion/react";
import { TrendingUp } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";

interface Milestone {
  rank: string;
  division: string;
  month: string;
  lp: number;
}

interface RankedJourneySlideProps {
  startRank: string;
  endRank: string;
  peakRank: string;
  milestones: Milestone[];
  aiHumor?: string;
}

const rankColors: Record<string, string> = {
  Iron: "#78716C",
  Bronze: "#CD7F32",
  Silver: "#A09B8C",
  Gold: "#C8AA6E",
  Platinum: "#5DADE2",
  Diamond: "#8B5CF6",
  Master: "#EF4444",
  Grandmaster: "#DC2626",
  Challenger: "#F59E0B",
};

export function RankedJourneySlide({
  startRank,
  endRank,
  peakRank,
  milestones,
  aiHumor = "You climbed more ranks than a chess grandmaster... but with way more rage quits! ♟️😤"
}: RankedJourneySlideProps) {
  const currentMilestone = milestones[milestones.length - 1];

  return (
    <div className="relative size-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* LoL Character Background */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=1920"
          alt="Background"
          className="size-full object-cover opacity-5"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a0b2e]/90 via-[#010A13]/90 to-[#0a1929]/90" />
      </div>

      {/* Animated gradient */}
      <motion.div
        animate={{
          rotate: [0, 360],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: "linear"
        }}
        className="absolute inset-0 bg-gradient-to-br from-[#C8AA6E]/10 via-transparent to-[#0AC8B9]/10"
      />

      {/* Content */}
      <div className="relative z-10 w-full h-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8 md:py-12 flex flex-col overflow-y-auto scrollbar-hide">
        {/* Icon & Title */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center mb-6 sm:mb-8"
        >
          <TrendingUp className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 text-[#C8AA6E] mx-auto mb-3" />
          <p className="text-base sm:text-lg md:text-xl text-[#A09B8C] uppercase tracking-[0.3em]">
            Your Ranked Journey
          </p>
        </motion.div>

        {/* Horizontal Timeline */}
        <div className="flex-1 flex flex-col justify-center mb-6 sm:mb-8">
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-[#78716C] via-[#C8AA6E] to-[#0AC8B9]" />

            {/* Milestones */}
            <div className="relative flex justify-between items-center overflow-x-auto scrollbar-hide pb-4">
              {milestones.map((milestone, idx) => {
                const isCurrentRank = idx === milestones.length - 1;
                const rankColor = rankColors[milestone.rank] || "#A09B8C";

                return (
                  <motion.div
                    key={`${milestone.rank}-${idx}`}
                    initial={{ opacity: 0, y: 50, scale: 0 }}
                    animate={{ opacity: 1, y: 0, scale: isCurrentRank ? 1.2 : 1 }}
                    transition={{ 
                      delay: 0.4 + idx * 0.15, 
                      duration: 0.6,
                      type: "spring"
                    }}
                    className={`flex flex-col items-center min-w-[80px] sm:min-w-[100px] ${
                      isCurrentRank ? 'z-10' : ''
                    }`}
                  >
                    {/* Rank Badge */}
                    <div 
                      className={`relative w-12 h-12 sm:w-16 sm:h-16 md:w-20 md:h-20 mb-2 sm:mb-3 ${
                        isCurrentRank ? 'ring-4 ring-[#C8AA6E]' : ''
                      }`}
                      style={{
                        background: `linear-gradient(to bottom right, ${rankColor}, ${rankColor}80)`,
                      }}
                    >
                      <ImageWithFallback
                        src={`https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=100`}
                        alt={milestone.rank}
                        className="absolute inset-0 size-full object-cover opacity-20"
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-[10px] sm:text-xs text-white/90 text-center px-1">
                          {milestone.rank[0]}
                        </span>
                      </div>
                      {isCurrentRank && (
                        <motion.div
                          animate={{
                            scale: [1, 1.2, 1],
                            opacity: [0.5, 1, 0.5],
                          }}
                          transition={{
                            duration: 2,
                            repeat: Infinity,
                          }}
                          className="absolute -inset-2 border-2 border-[#C8AA6E]"
                        />
                      )}
                    </div>

                    {/* Rank Info */}
                    <div className="text-center">
                      <div 
                        className={`text-xs sm:text-sm md:text-base mb-0.5 sm:mb-1 ${
                          isCurrentRank ? 'text-[#C8AA6E]' : 'text-white'
                        }`}
                        style={{ fontFamily: 'Georgia, serif' }}
                      >
                        {milestone.rank} {milestone.division}
                      </div>
                      <div className="text-[10px] sm:text-xs text-[#78716C]">
                        {milestone.month}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Peak Achievement */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="text-center mb-6 sm:mb-8"
        >
          <p className="text-xs sm:text-sm md:text-base text-[#A09B8C] mb-2">
            Peak Rank
          </p>
          <div className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl bg-gradient-to-r from-[#FFD700] to-[#C8AA6E] bg-clip-text text-transparent" style={{ fontFamily: 'Georgia, serif' }}>
            {peakRank}
          </div>
        </motion.div>

        {/* AI Humor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5, duration: 0.6 }}
          className="max-w-2xl mx-auto text-center"
        >
          <p className="text-xs sm:text-sm md:text-base lg:text-lg text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
