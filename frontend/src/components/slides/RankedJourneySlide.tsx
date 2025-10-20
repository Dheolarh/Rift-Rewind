import { motion } from "motion/react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import { useMemo } from "react";

// Rank images
import ironRank from "../../assets/ranks/iron.webp";
import bronzeRank from "../../assets/ranks/bronze.webp";
import silverRank from "../../assets/ranks/silver.webp";
import goldRank from "../../assets/ranks/gold.webp";
import platinumRank from "../../assets/ranks/platinum.webp";
import emeraldRank from "../../assets/ranks/emerald.webp";
import diamondRank from "../../assets/ranks/diamond.webp";
import masterRank from "../../assets/ranks/master.webp";
import grandmasterRank from "../../assets/ranks/grandmaster.png";
import challengerRank from "../../assets/ranks/challenger.webp";

interface RankedJourneySlideProps {
  currentRank: string;
  tier: string;
  division: string;
  lp: number;
  wins: number;
  losses: number;
  winRate: number;
  aiHumor?: string;
}

const RANK_IMAGES: Record<string, string> = {
  'IRON': ironRank,
  'BRONZE': bronzeRank,
  'SILVER': silverRank,
  'GOLD': goldRank,
  'PLATINUM': platinumRank,
  'EMERALD': emeraldRank,
  'DIAMOND': diamondRank,
  'MASTER': masterRank,
  'GRANDMASTER': grandmasterRank,
  'CHALLENGER': challengerRank,
  'UNRANKED': ironRank, // Default fallback
};

export function RankedJourneySlide({
  currentRank,
  tier,
  division,
  lp,
  wins,
  losses,
  winRate,
  aiHumor = "You climbed more ranks than a chess grandmaster... but with way more rage quits! ♟️😤"
}: RankedJourneySlideProps) {
  // Get the appropriate rank image based on tier
  const rankImage = useMemo(() => {
    return RANK_IMAGES[tier.toUpperCase()] || RANK_IMAGES['UNRANKED'];
  }, [tier]);

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
            src={rankImage}
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
            {tier} {division}
          </div>
          <div className="flex items-center justify-center gap-4 text-base sm:text-lg text-[#A09B8C]">
            <span>{lp} LP</span>
            <span>•</span>
            <span className="text-[#0AC8B9]">{wins}W</span>
            <span className="text-[#C75050]">{losses}L</span>
          </div>
          <div className="text-sm text-[#C8AA6E] mt-1">
            {winRate.toFixed(1)}% Win Rate
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
