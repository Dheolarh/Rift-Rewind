import { motion } from "motion/react";
import { Crown, RotateCcw, Sparkles, Share2, Trophy, Target, Zap, Award, Users, Eye, Swords } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import logoImage from "../../assets/logo.png";
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
          kdaRatio: 3.8,
          winRate: 57,
        }}
      />
      
      <div className="relative size-full overflow-y-auto overflow-x-hidden scrollbar-hide bg-gradient-to-br from-[#010A13] via-[#0A1428] to-[#010A13]">
        {/* Background layers */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#010A13] via-[#0A1428] to-[#010A13]" />
      
        {/* Background Image */}
        <ImageWithFallback 
          src="https://images.unsplash.com/photo-1759049080700-78aa9460c364?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxnb2xkZW4lMjBjcm93biUyMHJveWFsfGVufDF8fHx8MTc2MDAyMjM5MXww&ixlib=rb-4.1.0&q=80&w=1080"
          alt="Background"
          className="absolute inset-0 w-full h-full object-cover opacity-10"
        />

        {/* Multiple floating particles */}
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 rounded-full"
            style={{
              background: i % 2 === 0 ? '#C8AA6E' : '#0AC8B9',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 3,
            }}
          />
        ))}

        {/* Glowing orbs */}
        <div className="absolute top-1/4 left-1/4 w-64 h-64 md:w-96 md:h-96 bg-[#C8AA6E] rounded-full blur-[150px] opacity-30 animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 md:w-96 md:h-96 bg-[#0AC8B9] rounded-full blur-[150px] opacity-30 animate-pulse" style={{ animationDelay: '1s' }} />

        {/* Content */}
        <div className="relative z-10 w-full max-w-[min(90vw,900px)] lg:max-w-[min(55vw,1000px)] px-4 sm:px-6 mx-auto py-12 min-h-full flex flex-col justify-center">


        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
          className="text-center mb-4"
        >
          <ImageWithFallback 
            src={logoImage}
            alt="League of Legends Rift Rewind"
            className="w-full max-w-[200px] mx-auto mb-3"
          />
        </motion.div>

        {/* Title Banner */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="text-center mb-4"
        >
          <div className="inline-block relative">
            <div className="absolute -inset-4 bg-gradient-to-r from-[#FFD700]/20 via-[#C8AA6E]/30 to-[#FFD700]/20 blur-2xl" />
            
            <div className="relative">
              <Crown className="w-10 h-10 lg:w-12 lg:h-12 text-[#FFD700] mx-auto mb-2" />
              <h2 className="text-xl sm:text-2xl lg:text-3xl text-white mb-2" style={{ fontFamily: 'Georgia, serif' }}>
                {summonerName}
              </h2>
              <div className="h-px w-24 bg-gradient-to-r from-transparent via-[#C8AA6E] to-transparent mx-auto mb-2" />
              <div className="text-lg sm:text-xl lg:text-2xl bg-gradient-to-r from-[#FFD700] via-[#C8AA6E] to-[#0AC8B9] bg-clip-text text-transparent" style={{ fontFamily: 'Georgia, serif' }}>
                {playerTitle}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Main Highlight Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="relative mb-4"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-[#C8AA6E]/20 via-[#0AC8B9]/20 to-[#C8AA6E]/20 border border-[#C8AA6E]/30 backdrop-blur-sm" />
          <div className="relative p-4">
            <div className="text-center mb-3">
              <Sparkles className="w-6 h-6 text-[#C8AA6E] mx-auto mb-2" />
              <h3 className="text-sm text-[#C8AA6E] uppercase tracking-widest">
                {year} Highlights
              </h3>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              <div className="text-center p-3 bg-[#0A1428]/40 border border-[#C8AA6E]/20">
                <div className="text-xl text-[#C8AA6E] mb-1 tabular-nums">
                  {highlightStats.gamesPlayed}
                </div>
                <div className="text-xs text-[#A09B8C] uppercase tracking-wide">
                  Games
                </div>
              </div>

              <div className="text-center p-3 bg-[#0A1428]/40 border border-[#0AC8B9]/20">
                <div className="text-xl text-[#0AC8B9] mb-1 tabular-nums">
                  {highlightStats.hoursPlayed}
                </div>
                <div className="text-xs text-[#A09B8C] uppercase tracking-wide">
                  Hours
                </div>
              </div>

              <div className="text-center p-3 bg-[#0A1428]/40 border border-[#C8AA6E]/20">
                <div className="text-base text-[#C8AA6E] mb-1">
                  {highlightStats.peakRank}
                </div>
                <div className="text-xs text-[#A09B8C] uppercase tracking-wide">
                  Peak
                </div>
              </div>

              <div className="text-center p-3 bg-[#0A1428]/40 border border-[#C8AA6E]/20">
                <div className="text-base text-white mb-1">
                  {highlightStats.favoriteChampion}
                </div>
                <div className="text-xs text-[#A09B8C] uppercase tracking-wide">
                  Main
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Additional Achievement Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4"
        >
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-[#C8AA6E]/20 to-transparent border border-[#C8AA6E]/30" />
            <div className="relative p-2 text-center">
              <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                <Trophy className="w-5 h-5 text-[#C8AA6E]" />
              </div>
              <div className="text-xs text-white">5 Pentakills</div>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-[#0AC8B9]/20 to-transparent border border-[#0AC8B9]/30" />
            <div className="relative p-2 text-center">
              <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                <Eye className="w-5 h-5 text-[#0AC8B9]" />
              </div>
              <div className="text-xs text-white">10K Wards</div>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-[#C8AA6E]/20 to-transparent border border-[#C8AA6E]/30" />
            <div className="relative p-2 text-center">
              <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                <Zap className="w-5 h-5 text-[#C8AA6E]" />
              </div>
              <div className="text-xs text-white">47 Champions</div>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-[#8B5CF6]/20 to-transparent border border-[#8B5CF6]/30" />
            <div className="relative p-2 text-center">
              <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                <Award className="w-5 h-5 text-[#8B5CF6]" />
              </div>
              <div className="text-xs text-white">25 Barons</div>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-[#0AC8B9]/20 to-transparent border border-[#0AC8B9]/30" />
            <div className="relative p-2 text-center">
              <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                <Swords className="w-5 h-5 text-[#0AC8B9]" />
              </div>
              <div className="text-xs text-white">3.8 KDA</div>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-[#C8AA6E]/20 to-transparent border border-[#C8AA6E]/30" />
            <div className="relative p-2 text-center">
              <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                <Users className="w-5 h-5 text-[#C8AA6E]" />
              </div>
              <div className="text-xs text-white">287 Duos</div>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-[#C8AA6E]/20 to-transparent border border-[#C8AA6E]/30" />
            <div className="relative p-2 text-center">
              <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                <Target className="w-5 h-5 text-[#C8AA6E]" />
              </div>
              <div className="text-xs text-white">64% WR</div>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-[#8B5CF6]/20 to-transparent border border-[#8B5CF6]/30" />
            <div className="relative p-2 text-center">
              <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                <div className="text-base leading-none">
                  🎯
                </div>
              </div>
              <div className="text-xs text-white">12K CS</div>
            </div>
          </div>
        </motion.div>

        {/* Final Message */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="text-center mb-4"
        >
          <p className="text-sm sm:text-base text-[#E8E6E3] italic max-w-2xl mx-auto mb-3 px-4">
            "Your journey through the Rift has been legendary. May your next season bring even greater victories, Summoner."
          </p>
          <div className="h-px w-48 bg-gradient-to-r from-transparent via-[#C8AA6E] to-transparent mx-auto" />
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5 }}
          className="flex flex-col sm:flex-row gap-3 items-center justify-center"
        >
          <motion.button
            onClick={handleShare}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative group"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-[#0AC8B9] to-[#078378] group-hover:shadow-[0_0_30px_rgba(10,200,185,0.5)] transition-all" />
            <div className="relative bg-gradient-to-r from-[#0AC8B9] to-[#078378] text-white px-6 py-3 flex items-center gap-2 uppercase tracking-widest text-sm">
              <Share2 className="w-4 h-4" />
              <span>Share Results</span>
            </div>
          </motion.button>

          <motion.button
            onClick={onRestart}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative group"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-[#C8AA6E] via-[#0AC8B9] to-[#C8AA6E] group-hover:shadow-[0_0_30px_rgba(200,170,110,0.5)] transition-all" />
            <div className="relative bg-gradient-to-r from-[#C8AA6E] to-[#0AC8B9] text-[#010A13] px-6 py-3 flex items-center gap-2 uppercase tracking-widest text-sm">
              <RotateCcw className="w-4 h-4" />
              <span>Relive the Journey</span>
            </div>
          </motion.button>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
          className="text-center mt-4"
        >
          <p className="text-xs text-[#A09B8C]/60">
            © 2024 Rift Rewind • Powered by your dedication
          </p>
        </motion.div>
        </div>
      </div>
    </>
  );
}
