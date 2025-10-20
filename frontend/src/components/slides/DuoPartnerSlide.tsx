import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { Plus } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import duoBg from "../../assets/duo.webp";

interface DuoPartnerSlideProps {
  partnerName: string;
  gamesPlayed: number;
  winRate: number;
  favoriteCombo: {
    yourChampion: string;
    theirChampion: string;
  };
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
  gamesPlayed,
  winRate,
  favoriteCombo,
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
      <div className="relative z-10 flex flex-col items-center justify-center gap-3 sm:gap-4 md:gap-5 max-w-md w-full">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center"
        >
          <h1 className="text-lg sm:text-xl md:text-2xl text-[#A09B8C] uppercase tracking-[0.3em]" style={{ fontFamily: 'Georgia, serif' }}>
            Your Duo Partner
          </h1>
        </motion.div>

        {/* Champion Icons with Plus */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="flex items-center gap-3 sm:gap-4"
        >
          {/* Your Champion */}
          <div className="flex flex-col items-center gap-1.5">
            <div className="w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 overflow-hidden border-2 border-[#C8AA6E]">
              <ImageWithFallback
                src="https://images.unsplash.com/photo-1614294148960-9aa740632a87?w=150"
                alt="Your champion"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="text-xs text-[#A09B8C]">PlayerName</div>
          </div>

          {/* Plus Sign */}
          <Plus className="w-5 h-5 sm:w-6 sm:h-6 text-[#0AC8B9]" />

          {/* Partner's Champion */}
          <div className="flex flex-col items-center gap-1.5">
            <div className="w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 overflow-hidden border-2 border-[#0AC8B9]">
              <ImageWithFallback
                src="https://images.unsplash.com/photo-1614294148960-9aa740632a87?w=150"
                alt="Partner champion"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="text-xs text-[#A09B8C] text-center max-w-[80px] truncate">{partnerName}</div>
          </div>
        </motion.div>

        {/* Champion Names */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="flex items-center gap-2 sm:gap-3"
        >
          <div className="text-base sm:text-lg md:text-xl text-[#C8AA6E]" style={{ fontFamily: 'Georgia, serif' }}>
            {favoriteCombo.yourChampion}
          </div>
          <span className="text-[#A09B8C]">+</span>
          <div className="text-base sm:text-lg md:text-xl text-[#0AC8B9]" style={{ fontFamily: 'Georgia, serif' }}>
            {favoriteCombo.theirChampion}
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="flex items-center gap-4 sm:gap-6 md:gap-8"
        >
          <div className="text-center">
            <div className="text-2xl sm:text-3xl md:text-4xl text-white mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={gamesPlayed} />
            </div>
            <div className="text-xs text-[#A09B8C] uppercase tracking-wider">
              Games
            </div>
          </div>

          <div className="w-px h-10 sm:h-12 bg-[#0AC8B9]/30" />

          <div className="text-center">
            <div className="text-2xl sm:text-3xl md:text-4xl text-[#0AC8B9] mb-1 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
              <Counter value={winRate} />%
            </div>
            <div className="text-xs text-[#A09B8C] uppercase tracking-wider">
              Win Rate
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
