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
  aiHumor = "You two are like peanut butter and jelly... if jelly could flash-ult and secure pentas!"
}: DuoPartnerSlideProps) {
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
          <h1 className="text-lg sm:text-xl md:text-2xl text-[#A09B8C] uppercase tracking-[0.3em] mb-3" style={{ fontFamily: 'Georgia, serif' }}>
            Your Duo Partner
          </h1>
        </motion.div>

        {/* Partner Icon (using Plus icon as duo symbol) */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="flex items-center justify-center"
        >
          <div className="w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28 rounded-full bg-gradient-to-br from-[#0AC8B9] to-[#C8AA6E] flex items-center justify-center">
            <Plus className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 text-white" strokeWidth={3} />
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
              <div className="text-2xl sm:text-3xl md:text-4xl text-[#C8AA6E]" style={{ fontFamily: 'Georgia, serif' }}>
                {playerName}
              </div>
              <span className="text-xl sm:text-2xl text-[#A09B8C]">+</span>
              <div className="text-2xl sm:text-3xl md:text-4xl text-[#0AC8B9]" style={{ fontFamily: 'Georgia, serif' }}>
                {partnerName}
              </div>
            </div>
          ) : (
            <div className="text-3xl sm:text-4xl md:text-5xl text-white mb-2" style={{ fontFamily: 'Georgia, serif' }}>
              {partnerName}
            </div>
          )}
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="flex items-center gap-6 sm:gap-8 md:gap-10"
        >
          <div className="text-center">
            <div className="text-3xl sm:text-4xl md:text-5xl text-white mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={gamesTogether} />
            </div>
            <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
              Games
            </div>
          </div>

          <div className="w-px h-12 sm:h-14 bg-[#0AC8B9]/30" />

          <div className="text-center">
            <div className="text-3xl sm:text-4xl md:text-5xl text-[#0AC8B9] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={Math.round(winRate)} />%
            </div>
            <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
              Win Rate
            </div>
          </div>

          <div className="w-px h-12 sm:h-14 bg-[#0AC8B9]/30" />

          <div className="text-center">
            <div className="text-3xl sm:text-4xl md:text-5xl text-[#C8AA6E] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={wins} />
            </div>
            <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
              Wins
            </div>
          </div>
        </motion.div>

        {/* AI Text */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-center max-w-sm px-2"
        >
          <p className="text-xs text-[#E8E6E3]/80 italic leading-relaxed">
            {aiHumor}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
