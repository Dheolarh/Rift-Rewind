import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { Plus } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import duoBg from "../../assets/duo.webp";

interface DuoPartnerSlideProps {
  partnerName: string;
  gamesTogether: number;
  wins: number;
  winRate: number;
  playerName?: string; // Player's own name
  playerProfileIconUrl?: string; // Direct URL to player's profile icon from backend
  aiHumor?: string;
}

function Counter({ value, duration = 2 }: { value: number; duration?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, { duration, delay: 0.8 });
    return controls.stop;
  }, [value, duration, count]);

  return <motion.span>{rounded}</motion.span>;
}

export function DuoPartnerSlide({
  partnerName,
  gamesTogether,
  wins,
  winRate,
  playerName,
  playerProfileIconUrl,
  aiHumor = "You two are like peanut butter and jelly... if jelly could flash-ult and secure pentas!"
}: DuoPartnerSlideProps) {
  // Riot Data Dragon URLs
  const DDRAGON_VERSION = '14.23.1';
  
  // Player's actual profile icon - use direct URL from backend or fallback to default
  const playerIconUrl = playerProfileIconUrl || `https://ddragon.leagueoflegends.com/cdn/${DDRAGON_VERSION}/img/profileicon/29.png`;
  
  // Partner icon - use a popular champion icon (Yasuo - represents duo synergy/teamwork)
  const partnerIconUrl = `https://ddragon.leagueoflegends.com/cdn/${DDRAGON_VERSION}/img/champion/Yasuo.png`;
  
  return (
    <div className="relative w-full h-full overflow-hidden bg-[#010A13] flex items-center justify-center px-4">
      {/* Background Image */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={duoBg}
          alt="Duo Background"
          className="w-full h-full object-cover opacity-15"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a0b2e]/90 via-[#010A13]/95 to-[#0a1929]/98" />
      </div>

      {/* Animated gradient */}
      <motion.div
        animate={{
          x: [-30, 30, -30],
          y: [0, 20, 0],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute bottom-1/4 right-1/4 w-64 h-64 sm:w-80 sm:h-80 bg-[#0AC8B9] rounded-full blur-[150px] opacity-30"
      />

      {/* Centered Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-4 sm:gap-6 max-w-md w-full">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center"
        >
          <h1 className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl text-[#A09B8C] uppercase tracking-[0.3em] mb-3" style={{ fontFamily: 'Georgia, serif' }}>
            Your Duo Partner
          </h1>
        </motion.div>

        {/* Profile Icons with Plus */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="flex items-center gap-3 sm:gap-4 lg:gap-6"
        >
          {/* Your Profile Icon */}
          <div className="flex flex-col items-center gap-1.5">
            <div className="w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 lg:w-28 lg:h-28 xl:w-32 xl:h-32 rounded-full overflow-hidden border-2 lg:border-3 border-[#C8AA6E] bg-[#0A0E15]">
              <ImageWithFallback
                src={playerIconUrl}
                alt="Your profile"
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* Plus Sign */}
          <Plus className="w-5 h-5 sm:w-6 sm:h-6 lg:w-8 lg:h-8 xl:w-10 xl:h-10 text-[#0AC8B9]" />

          {/* Partner's Profile Icon */}
          <div className="flex flex-col items-center gap-1.5">
            <div className="w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 lg:w-28 lg:h-28 xl:w-32 xl:h-32 rounded-full overflow-hidden border-2 lg:border-3 border-[#0AC8B9] bg-[#0A0E15]">
              <ImageWithFallback
                src={partnerIconUrl}
                alt="Partner profile"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </motion.div>

        {/* Partner Names */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="text-center"
        >
          {playerName ? (
            <div className="flex items-center justify-center gap-2 sm:gap-3 flex-wrap">
              <div className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl text-[#C8AA6E]" style={{ fontFamily: 'Georgia, serif' }}>
                {playerName}
              </div>
              <span className="text-xl sm:text-2xl lg:text-3xl xl:text-4xl text-[#A09B8C]">+</span>
              <div className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl text-[#0AC8B9]" style={{ fontFamily: 'Georgia, serif' }}>
                {partnerName}
              </div>
            </div>
          ) : (
            <div className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-white mb-2" style={{ fontFamily: 'Georgia, serif' }}>
              {partnerName}
            </div>
          )}
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="flex items-center gap-6 sm:gap-8 md:gap-10 lg:gap-12 xl:gap-16"
        >
          <div className="text-center">
            <div className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-white mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={gamesTogether} />
            </div>
            <div className="text-xs sm:text-sm lg:text-base xl:text-lg text-[#A09B8C] uppercase tracking-wider">
              Games
            </div>
          </div>

          <div className="w-px h-12 sm:h-14 lg:h-20 xl:h-24 bg-[#0AC8B9]/30" />

          <div className="text-center">
            <div className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-[#0AC8B9] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={Math.round(winRate)} />%
            </div>
            <div className="text-xs sm:text-sm lg:text-base xl:text-lg text-[#A09B8C] uppercase tracking-wider">
              Win Rate
            </div>
          </div>

          <div className="w-px h-12 sm:h-14 lg:h-20 xl:h-24 bg-[#0AC8B9]/30" />

          <div className="text-center">
            <div className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-[#C8AA6E] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={wins} />
            </div>
            <div className="text-xs sm:text-sm lg:text-base xl:text-lg text-[#A09B8C] uppercase tracking-wider">
              Wins
            </div>
          </div>
        </motion.div>

        {/* AI Text */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-center max-w-md sm:max-w-lg px-4"
        >
          <p className="text-base sm:text-lg md:text-xl text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
