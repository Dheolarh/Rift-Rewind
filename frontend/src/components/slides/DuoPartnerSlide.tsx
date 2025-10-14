import { motion, useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";
import { Users, Swords } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";

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
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#1a0b2e] via-[#010A13] to-[#0a1929]">
      {/* Animated gradient */}
      <motion.div
        animate={{
          x: [-50, 50, -50],
          y: [0, 30, 0],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#0AC8B9] rounded-full blur-[150px] opacity-30"
      />

      {/* Scrollable Content */}
      <div className="relative z-10 size-full overflow-y-auto scrollbar-hide">
        <div className="min-h-full flex flex-col items-center justify-center w-full max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          {/* Icon */}
          <motion.div
            initial={{ opacity: 0, scale: 0, rotate: -90 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ delay: 0.2, duration: 0.8, type: "spring" }}
          >
            <Users className="w-12 h-12 sm:w-14 sm:h-14 text-[#0AC8B9] mb-4 sm:mb-5" />
          </motion.div>

          {/* Title */}
          <motion.div
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-center mb-6 sm:mb-8"
          >
            <p className="text-sm sm:text-base md:text-lg text-[#A09B8C] uppercase tracking-[0.2em] sm:tracking-[0.3em]">
              Your Duo Partner
            </p>
          </motion.div>

          {/* Partner cards side by side */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="grid grid-cols-2 gap-3 sm:gap-4 md:gap-6 mb-6 sm:mb-8 w-full max-w-2xl"
          >
            {/* Your champion */}
            <div className="text-center">
              <div className="relative aspect-square mb-2 sm:mb-3 overflow-hidden border-2 border-[#C8AA6E] bg-gradient-to-br from-[#C8AA6E]/20 to-transparent">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1614294148960-9aa740632a87?w=400"
                  alt="Your champion"
                  className="size-full object-cover opacity-60"
                />
              </div>
              <div className="text-[10px] sm:text-xs text-[#A09B8C] uppercase tracking-wider mb-1">You</div>
              <div className="text-lg sm:text-xl md:text-2xl text-[#C8AA6E]" style={{ fontFamily: 'Georgia, serif' }}>
                {favoriteCombo.yourChampion}
              </div>
            </div>

            {/* Partner's champion */}
            <div className="text-center">
              <div className="relative aspect-square mb-2 sm:mb-3 overflow-hidden border-2 border-[#0AC8B9] bg-gradient-to-br from-[#0AC8B9]/20 to-transparent">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1614294148960-9aa740632a87?w=400"
                  alt="Partner champion"
                  className="size-full object-cover opacity-60"
                />
              </div>
              <div className="text-[10px] sm:text-xs text-[#A09B8C] uppercase tracking-wider mb-1">{partnerName}</div>
              <div className="text-lg sm:text-xl md:text-2xl text-[#0AC8B9]" style={{ fontFamily: 'Georgia, serif' }}>
                {favoriteCombo.theirChampion}
              </div>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="flex items-center justify-center gap-6 sm:gap-8 md:gap-12 mb-6 sm:mb-8"
          >
            <div className="text-center">
              <div className="text-3xl sm:text-4xl md:text-5xl text-white mb-1 sm:mb-2 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                <Counter value={gamesPlayed} />
              </div>
              <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
                Games Together
              </div>
            </div>

            <div className="w-px h-12 sm:h-14 bg-[#0AC8B9]/30" />

            <div className="text-center">
              <div className="text-3xl sm:text-4xl md:text-5xl text-[#0AC8B9] mb-1 sm:mb-2 tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                <Counter value={winRate} />%
              </div>
              <div className="text-xs sm:text-sm text-[#A09B8C] uppercase tracking-wider">
                Win Rate
              </div>
            </div>
          </motion.div>

          {/* AI Humor */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.4, duration: 0.6 }}
            className="max-w-xl text-center px-4"
          >
            <p className="text-xs sm:text-sm md:text-base text-[#E8E6E3]/80 italic leading-relaxed">
              {aiHumor}
            </p>
          </motion.div>

          {/* Bottom Spacing */}
          <div className="h-4 sm:h-6" />
        </div>
      </div>
    </div>
  );
}
