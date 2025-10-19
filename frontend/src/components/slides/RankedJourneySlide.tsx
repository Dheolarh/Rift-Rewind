import { motion } from "motion/react";
import { Calendar } from "lucide-react";
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

export function RankedJourneySlide({
  startRank,
  endRank,
  peakRank,
  milestones,
  aiHumor = "You climbed more ranks than a chess grandmaster... but with way more rage quits! ♟️😤"
}: RankedJourneySlideProps) {
  // Find the peak rank from milestones
  const peakMilestone = milestones.find(m => `${m.rank} ${m.division}` === peakRank) || milestones[0];

  return (
    <div className="relative w-full h-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* LoL Background */}
      <div className="absolute inset-0 w-full h-full">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=1920"
          alt="Background"
          className="w-full h-full object-cover opacity-5"
        />
        <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-[#1a0b2e]/90 via-[#010A13]/90 to-[#0a1929]/90" />
      </div>

      {/* Animated gradient - reduced */}
      <motion.div
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.1, 0.2, 0.1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute inset-0 w-full h-full bg-gradient-to-br from-[#C8AA6E]/10 via-transparent to-[#0AC8B9]/10"
      />

      {/* Centered Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-4 sm:gap-6 px-4 max-w-md">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center"
        >
          <h1 className="text-xl sm:text-2xl md:text-3xl text-[#A09B8C] uppercase tracking-[0.3em]" style={{ fontFamily: 'Georgia, serif' }}>
            Highest Rank Achieved
          </h1>
        </motion.div>

        {/* Rank Image - No border, no wrapper */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{
            delay: 0.4,
            duration: 0.6
          }}
        >
          <ImageWithFallback
            src="https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=400"
            alt="Rank Icon"
            className="object-cover"
            style={{ width: '160px', height: '160px' }}
          />
        </motion.div>

        {/* Rank Text - Increased size */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="text-center"
        >
          <div className="text-5xl sm:text-6xl md:text-7xl text-[#C8AA6E] mb-2" style={{ fontFamily: 'Georgia, serif' }}>
            {peakRank}
          </div>
          <div className="flex items-center justify-center gap-2 text-base sm:text-lg text-[#A09B8C]">
            <Calendar className="w-5 h-5" />
            <span>{peakMilestone.month}</span>
          </div>
        </motion.div>

        {/* AI Text */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="text-center max-w-md px-4"
        >
          <p className="text-xs sm:text-sm text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
