import { motion } from "motion/react";
import { TrendingUp, Calendar } from "lucide-react";
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

const rankGradients: Record<string, string> = {
  Iron: "from-[#78716C] to-[#57534E]",
  Bronze: "from-[#CD7F32] to-[#8B5A00]",
  Silver: "from-[#C0C0C0] to-[#808080]",
  Gold: "from-[#FFD700] to-[#C8AA6E]",
  Platinum: "from-[#5DADE2] to-[#3B82F6]",
  Diamond: "from-[#A78BFA] to-[#8B5CF6]",
  Master: "from-[#EF4444] to-[#DC2626]",
  Grandmaster: "from-[#DC2626] to-[#B91C1C]",
  Challenger: "from-[#F59E0B] to-[#D97706]",
};

export function RankedJourneySlide({
  startRank,
  endRank,
  peakRank,
  milestones,
  aiHumor = "You climbed more ranks than a chess grandmaster... but with way more rage quits! ♟️😤"
}: RankedJourneySlideProps) {
  // Find the peak rank from milestones
  const peakMilestone = milestones.find(m => `${m.rank} ${m.division}` === peakRank) || milestones[0];
  const peakRankName = peakMilestone.rank;
  const peakGradient = rankGradients[peakRankName] || "from-[#C8AA6E] to-[#8B7548]";

  // Calculate animation delays
  const baseDelay = 0.5;
  const stepDelay = 0.4; // Each date + rank pair
  const totalMilestoneTime = baseDelay + (milestones.length * stepDelay);
  const highestRankDelay = totalMilestoneTime + 0.3;
  const aiTextDelay = highestRankDelay + 0.5;

  return (
    <div className="relative size-full overflow-hidden bg-[#010A13]">
      {/* LoL Background */}
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
      <div className="relative z-10 size-full flex flex-col px-8 py-12">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center mb-12"
        >
          <TrendingUp className="w-12 h-12 text-[#C8AA6E] mx-auto mb-3" />
          <p className="text-xl text-[#A09B8C] uppercase tracking-[0.3em]">
            Your Ranked Journey
          </p>
        </motion.div>

        {/* Two Column Layout */}
        <div className="flex-1 flex items-center justify-center gap-12">
          {/* LEFT: Journey Timeline */}
          <div className="flex-1 flex justify-end max-w-md">
            <div className="relative w-full max-h-[600px] overflow-y-auto scrollbar-hide pr-4">
              {/* Animated vertical line */}
              <motion.div
                initial={{ height: 0 }}
                animate={{ height: '100%' }}
                transition={{
                  duration: totalMilestoneTime - baseDelay,
                  delay: baseDelay,
                  ease: "linear"
                }}
                className="absolute left-16 top-0 w-0.5 bg-gradient-to-b from-[#C8AA6E] to-[#0AC8B9]"
              />

              {/* Milestones */}
              <div className="space-y-4">
                {milestones.map((milestone, idx) => {
                  const isCurrentRank = idx === milestones.length - 1;
                  const gradient = rankGradients[milestone.rank] || "from-[#C8AA6E] to-[#8B7548]";
                  const animationDelay = baseDelay + (idx * stepDelay);

                  return (
                    <div key={`${milestone.rank}-${idx}`} className="relative flex items-center gap-3">
                      {/* Date (left of line) */}
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{
                          delay: animationDelay,
                          duration: 0.5
                        }}
                        className="w-14 text-right text-xs text-[#A09B8C]"
                      >
                        {milestone.month.substring(0, 3)}
                      </motion.div>

                      {/* Dot on line */}
                      <motion.div
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{
                          delay: animationDelay,
                          duration: 0.4,
                          type: "spring"
                        }}
                        className="w-3 h-3 rounded-full bg-[#C8AA6E] ring-3 ring-[#C8AA6E]/20 relative z-10"
                      />

                      {/* Rank badge (right of line) */}
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{
                          delay: animationDelay + 0.2,
                          duration: 0.5
                        }}
                        className="flex-1"
                      >
                        <div
                          className={`relative px-3 py-2 bg-gradient-to-r ${gradient} rounded border ${
                            isCurrentRank ? 'border-[#C8AA6E] shadow-md shadow-[#C8AA6E]/30' : 'border-[#C8AA6E]/30'
                          }`}
                        >
                          {/* Rank icon */}
                          <div className="absolute -left-2 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-gradient-to-br from-[#1E2328] to-[#0A1428] border-2 border-[#C8AA6E] flex items-center justify-center">
                            <span className="text-[10px] text-[#C8AA6E]">
                              {milestone.rank[0]}
                            </span>
                          </div>

                          <div className="text-center">
                            <div className="text-sm text-white" style={{ fontFamily: 'Georgia, serif' }}>
                              {milestone.rank} {milestone.division}
                            </div>
                            {isCurrentRank && (
                              <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: animationDelay + 0.4 }}
                                className="text-[10px] text-[#C8AA6E] mt-0.5"
                              >
                                Current
                              </motion.div>
                            )}
                          </div>

                          {/* Glow for current rank */}
                          {isCurrentRank && (
                            <motion.div
                              animate={{
                                opacity: [0.3, 0.6, 0.3],
                              }}
                              transition={{
                                duration: 2,
                                repeat: Infinity,
                              }}
                              className="absolute -inset-0.5 bg-[#C8AA6E] rounded -z-10 blur-sm"
                            />
                          )}
                        </div>
                      </motion.div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* RIGHT: Highest Rank + AI Text */}
          <div className="flex-1 flex flex-col items-start justify-center gap-6 max-w-sm">
            {/* Highest Rank Card */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{
                delay: highestRankDelay,
                duration: 0.6,
                type: "spring"
              }}
              className="w-full"
            >
              <div className="relative p-6 bg-[#1E2328]/80 backdrop-blur-sm rounded-lg border-2 border-[#C8AA6E] shadow-xl">
                <div className="relative z-10 text-center">
                  {/* Icon */}
                  <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-gradient-to-br from-[#1E2328] to-[#0A1428] border-3 border-[#C8AA6E] flex items-center justify-center shadow-lg">
                    <TrendingUp className="w-8 h-8 text-[#C8AA6E]" />
                  </div>

                  <p className="text-xs text-[#A09B8C] uppercase tracking-widest mb-2">
                    Highest Rank
                  </p>

                  <div className="text-3xl text-[#C8AA6E] mb-2" style={{ fontFamily: 'Georgia, serif' }}>
                    {peakRank}
                  </div>

                  <div className="flex items-center justify-center gap-2 text-xs text-[#A09B8C]">
                    <Calendar className="w-3 h-3" />
                    <span>{peakMilestone.month}</span>
                  </div>
                </div>

                {/* Animated border glow */}
                <motion.div
                  animate={{
                    opacity: [0.3, 0.6, 0.3],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                  }}
                  className="absolute -inset-1 bg-gradient-to-r from-[#C8AA6E] to-[#0AC8B9] rounded-lg blur-md -z-10"
                />
              </div>
            </motion.div>

            {/* AI Text */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: aiTextDelay,
                duration: 0.6
              }}
              className="w-full"
            >
              <div className="relative p-5 bg-[#1E2328]/60 backdrop-blur-sm rounded-lg border border-[#C8AA6E]/30">
                <p className="text-sm text-[#E8E6E3]/80 italic leading-relaxed text-center">
                  {aiHumor}
                </p>

                {/* Decorative corner accents */}
                <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-[#C8AA6E]" />
                <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-[#C8AA6E]" />
                <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-[#C8AA6E]" />
                <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-[#C8AA6E]" />
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
