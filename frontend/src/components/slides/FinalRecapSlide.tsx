import { motion } from "motion/react";
import { RotateCcw, Share2 } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import logoImage from "../../assets/WelcomeBg.webp";
import { useState } from "react";
import { ShareCard } from "../ShareCard";

interface FinalRecapSlideProps {
  summonerName: string;
  playerTitle: string;
  year: number;
  highlightStats: {
    gamesPlayed: number;
    hoursPlayed: number;
    peakRank: string;
    favoriteChampion: string;
    kdaRatio: number;
    winRate: number;
  };
  onRestart: () => void;
}

export function FinalRecapSlide({
  summonerName,
  playerTitle,
  year,
  highlightStats,
  onRestart,
}: FinalRecapSlideProps) {
  const [showShareCard, setShowShareCard] = useState(false);

  const handleShare = () => {
    setShowShareCard(true);
  };

  return (
    <>
      <ShareCard 
        isOpen={showShareCard}
        onClose={() => setShowShareCard(false)}
        summonerName={summonerName}
        playerTitle={playerTitle}
        year={year}
        stats={{
          gamesPlayed: highlightStats.gamesPlayed,
          hoursPlayed: highlightStats.hoursPlayed,
          peakRank: highlightStats.peakRank,
          favoriteChampion: highlightStats.favoriteChampion,
          kdaRatio: highlightStats.kdaRatio,
          winRate: highlightStats.winRate,
        }}
      />
      
      <div className="relative w-full h-full overflow-hidden bg-[#010A13] flex items-center justify-center">
        {/* Simple Background Image */}
        <div className="absolute inset-0">
          <ImageWithFallback 
            src="https://images.unsplash.com/photo-1759049080700-78aa9460c364?w=1920"
            alt="Background"
            className="w-full h-full object-cover opacity-10"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-[#010A13]/80 via-[#010A13]/60 to-[#010A13]" />
        </div>

        {/* Content - Centered and Simplified */}
        <div className="relative z-10 flex flex-col items-center justify-center px-4 sm:px-6 gap-6">
          
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
          >
            <ImageWithFallback 
              src={logoImage}
              alt="Rift Rewind"
              className="w-24 sm:w-32 md:w-36 mx-auto"
            />
          </motion.div>

          {/* Title */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-center"
          >
            <h2 className="text-xl sm:text-2xl md:text-3xl text-white mb-1" style={{ fontFamily: 'Georgia, serif' }}>
              {summonerName}
            </h2>
            <div className="text-sm sm:text-base text-[#C8AA6E]" style={{ fontFamily: 'Georgia, serif' }}>
              {playerTitle}
            </div>
          </motion.div>

          {/* Stats Grid - Simplified */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="grid grid-cols-2 gap-3 w-full max-w-sm"
          >
            <div className="bg-[#0A1428]/50 border border-[#C8AA6E]/20 p-3 text-center">
              <div className="text-xl sm:text-2xl text-[#C8AA6E] mb-0.5 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.gamesPlayed}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase">Games</div>
            </div>

            <div className="bg-[#0A1428]/50 border border-[#0AC8B9]/20 p-3 text-center">
              <div className="text-xl sm:text-2xl text-[#0AC8B9] mb-0.5 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.hoursPlayed}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase">Hours</div>
            </div>

            <div className="bg-[#0A1428]/50 border border-[#C8AA6E]/20 p-3 text-center">
              <div className="text-sm sm:text-base text-[#C8AA6E] mb-0.5" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.peakRank}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase">Peak Rank</div>
            </div>

            <div className="bg-[#0A1428]/50 border border-[#C8AA6E]/20 p-3 text-center">
              <div className="text-sm sm:text-base text-white mb-0.5" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.favoriteChampion}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase">Main</div>
            </div>
          </motion.div>

          {/* Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="flex flex-col sm:flex-row gap-3 items-center justify-center mt-2"
          >
            <motion.button
              onClick={handleShare}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-[#0AC8B9] hover:bg-[#078378] text-white px-6 py-3 flex items-center gap-2 uppercase tracking-widest text-sm transition-colors"
            >
              <Share2 className="w-4 h-4" />
              <span>Share</span>
            </motion.button>

            <motion.button
              onClick={onRestart}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-[#C8AA6E] hover:bg-[#8B7548] text-[#010A13] px-6 py-3 flex items-center gap-2 uppercase tracking-widest text-sm transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Restart</span>
            </motion.button>
          </motion.div>
        </div>
      </div>
    </>
  );
}
