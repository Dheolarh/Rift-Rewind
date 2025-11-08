import { motion, AnimatePresence } from "motion/react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import { useMemo } from "react";
import LightRays from "../backgrounds/rankedJourneyBackground";

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
  showHumor?: boolean;
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
  aiHumor = "Analyzing your ranked journey...",
  showHumor = false
}: RankedJourneySlideProps) {
  // Get the appropriate rank image based on tier
  const rankImage = useMemo(() => {
    return RANK_IMAGES[tier.toUpperCase()] || RANK_IMAGES['UNRANKED'];
  }, [tier]);

  return (
    <div className="relative w-full h-full overflow-hidden bg-[#010A13] flex items-center justify-center">
      {/* LightRays Background */}
      <LightRays
        raysOrigin="top-center"
        raysColor="#D4AF37"
        raysSpeed={1.0}
        lightSpread={3.0}
        rayLength={5.0}
        pulsating={false}
        fadeDistance={0.4}
        saturation={2.0}
        followMouse={false}
        mouseInfluence={0.0}
        noiseAmount={0.03}
        distortion={0.01}
        className="opacity-100"
      />

      {/* Centered Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-4 sm:gap-6 px-4 max-w-md">
        <AnimatePresence mode="wait">
          {!showHumor ? (
            // Stats Phase
            <motion.div
              key="stats"
              initial={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center gap-4 sm:gap-6"
            >
              {/* Title */}
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.6 }}
                className="text-center"
              >
                <h1 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl text-[#A09B8C] uppercase tracking-[0.3em]" style={{ fontFamily: 'Georgia, serif' }}>
                  Current Rank
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
                <div className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl xl:text-9xl text-[#C8AA6E] mb-2" style={{ fontFamily: 'Georgia, serif' }}>
                  {tier} {division}
                </div>
                <div className="flex items-center justify-center gap-4 text-base sm:text-lg lg:text-xl xl:text-2xl text-[#A09B8C]">
                  <span>{lp} LP</span>
                  <span>•</span>
                  <span className="text-[#0AC8B9]">{wins}W</span>
                  <span>•</span>
                  <span className="text-[#C75050]">{losses}L</span>
                </div>
                <div className="text-sm lg:text-base xl:text-lg text-[#C8AA6E] mt-1">
                  {winRate.toFixed(1)}% Win Rate
                </div>
              </motion.div>
            </motion.div>
          ) : (
            // Humor Phase
            <motion.div
              key="humor"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6 }}
              className="flex flex-col items-center justify-center w-full max-w-2xl px-6"
            >
              <p className="text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl text-[#C8AA6E] leading-relaxed text-center">
                {aiHumor}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
