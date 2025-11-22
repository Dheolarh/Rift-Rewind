import { motion } from "motion/react";
import { RotateCcw, Share2 } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import welcomeBg from "../../assets/WelcomeBg.webp";
import logoImage from "../../assets/logo.webp";
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
    totalKills: number;
    uniqueChampions: number;
    playerLevel: number;
  };
  profileIconId?: number;
  onRestart: () => void;
}

export function FinalRecapSlide({
  summonerName,
  playerTitle,
  year,
  highlightStats,
  profileIconId,
  onRestart,
}: FinalRecapSlideProps) {
  const [showShareCard, setShowShareCard] = useState(false);

  // Get summoner icon URL
  const summonerIconUrl = profileIconId
    ? `https://ddragon.leagueoflegends.com/cdn/14.23.1/img/profileicon/${profileIconId}.png`
    : null;

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
          totalKills: highlightStats.totalKills,
          uniqueChampions: highlightStats.uniqueChampions,
          playerLevel: highlightStats.playerLevel,
        }}
      />

      <div className="min-h-screen w-full p-4 sm:p-20 flex flex-col items-center bg-[#010A13] overflow-y-auto overflow-x-hidden">

        {/* Background Image - Same as Welcome Slide */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#010A13] via-[#0A1428] to-[#010A13]" />

        <ImageWithFallback
          src={welcomeBg}
          alt="Background"
          className="absolute inset-0 size-full object-cover opacity-20"
        />

        {/* Glowing orbs */}
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-[#C8AA6E] rounded-full blur-[120px] opacity-20 animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-[#0AC8B9] rounded-full blur-[120px] opacity-20 animate-pulse" style={{ animationDelay: '1s' }} />

        {/* Content - Centered and Simplified */}
        <div
        className="relative z-10 w-full max-w-4xl flex flex-col items-center px-4 sm:px-6 gap-4 sm:gap-5"
        style={{
          width: "90vw",
          paddingTop: "10%",
        }}
        >

          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-2"
          >
            <ImageWithFallback
              src={logoImage}
              alt="Rift Rewind Logo"
              className="w-48 sm:w-56 md:w-64 mx-auto"
            />
          </motion.div>

          {/* Summoner Icon */}
          {summonerIconUrl && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="w-20 h-20 sm:w-24 sm:h-24 rounded-full border-4 border-[#C8AA6E] overflow-hidden bg-[#0A1428] shadow-lg shadow-[#C8AA6E]/30"
            >
              <ImageWithFallback
                src={summonerIconUrl}
                alt="Summoner Icon"
                className="w-full h-full object-cover"
              />
            </motion.div>
          )}

          {/* Title */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-center"
          >
            <h2 className="text-xl sm:text-2xl md:text-3xl text-white mb-1" style={{ fontFamily: 'Georgia, serif' }}>
              {summonerName}
            </h2>
            <div className="text-sm sm:text-base md:text-lg text-[#C8AA6E] italic" style={{ fontFamily: 'Georgia, serif' }}>
              {playerTitle}
            </div>
          </motion.div>

          {/* Stats Grid - Expanded with more boxes */}
          <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3 w-full max-w-4xl overflow-y-auto"
          style={{
            maxHeight: "50vh",
          WebkitOverflowScrolling: "touch",
          }}
          >

            {/* Hours Played */}
            <div className="bg-[#0A1428]/60 backdrop-blur-sm border border-[#0AC8B9]/30 p-3 sm:p-4 text-center rounded-sm">
              <div className="text-2xl sm:text-3xl text-[#0AC8B9] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {Math.trunc(highlightStats.hoursPlayed)}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase tracking-wider">Hours</div>
            </div>

            {/* Games Played */}
            <div className="bg-[#0A1428]/60 backdrop-blur-sm border border-[#C8AA6E]/30 p-3 sm:p-4 text-center rounded-sm">
              <div className="text-2xl sm:text-3xl text-[#C8AA6E] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.gamesPlayed}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase tracking-wider">Games</div>
            </div>

            {/* Win Rate */}
            <div className="bg-[#0A1428]/60 backdrop-blur-sm border border-[#0AC8B9]/30 p-3 sm:p-4 text-center rounded-sm">
              <div className="text-2xl sm:text-3xl text-[#0AC8B9] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.winRate.toFixed(1)}%
              </div>
              <div className="text-xs text-[#A09B8C] uppercase tracking-wider">Win Rate</div>
            </div>

            {/* Total Kills */}
            <div className="bg-[#0A1428]/60 backdrop-blur-sm border border-[#FF4444]/30 p-3 sm:p-4 text-center rounded-sm">
              <div className="text-2xl sm:text-3xl text-[#FF4444] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.totalKills}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase tracking-wider">Kills</div>
            </div>

            {/* KDA Ratio */}
            <div className="bg-[#0A1428]/60 backdrop-blur-sm border border-[#C8AA6E]/30 p-3 sm:p-4 text-center rounded-sm">
              <div className="text-2xl sm:text-3xl text-[#FFD700] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.kdaRatio.toFixed(2)}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase tracking-wider">KDA</div>
            </div>

            {/* Favorite Champion */}
            <div className="bg-[#0A1428]/60 backdrop-blur-sm border border-[#8B5CF6]/30 p-3 sm:p-4 text-center rounded-sm">
              <div className="text-base sm:text-lg text-white mb-1 truncate" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.favoriteChampion}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase tracking-wider">Main</div>
            </div>

            {/* Peak Rank */}
            <div className="bg-[#0A1428]/60 backdrop-blur-sm border border-[#C8AA6E]/30 p-3 sm:p-4 text-center rounded-sm">
              <div className="text-base sm:text-lg text-[#C8AA6E] mb-1" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.peakRank}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase tracking-wider">Peak Rank</div>
            </div>

            {/* Unique Champions */}
            <div className="bg-[#0A1428]/60 backdrop-blur-sm border border-[#8B5CF6]/30 p-3 sm:p-4 text-center rounded-sm">
              <div className="text-2xl sm:text-3xl text-[#8B5CF6] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                {highlightStats.uniqueChampions}
              </div>
              <div className="text-xs text-[#A09B8C] uppercase tracking-wider">Champions</div>
            </div>

            {/* Player Level */}
            <div className="bg-[#0A1428]/60 backdrop-blur-sm border border-[#C8AA6E]/30 p-3 sm:p-4 text-center rounded-sm">
              <div className="text-2xl sm:text-3xl text-[#C8AA6E] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                  {highlightStats.playerLevel || '—'}
                </div>
              <div className="text-xs text-[#A09B8C] uppercase tracking-wider">Level</div>
            </div>
          </motion.div>

          {/* Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="flex flex-row sm:flex-row gap-3 items-center justify-center mt-2"
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
