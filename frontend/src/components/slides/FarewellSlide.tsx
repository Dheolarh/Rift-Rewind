import { motion } from "motion/react";
import { useEffect, useState } from "react";

interface FarewellSlideProps {
  summonerName?: string;
  season?: string;
  gamesPlayed?: number;
  hoursPlayed?: number;
  favoriteChampion?: string;
}

export function FarewellSlide({
  summonerName = "Summoner",
  season = "2025",
  gamesPlayed = 0,
  hoursPlayed = 0,
  favoriteChampion = "your favorite champion"
}: FarewellSlideProps) {
  const [visibleLines, setVisibleLines] = useState(0);

  const farewellLines = [
    { text: `Well, what a season.`, highlight: false },
    { text: `${gamesPlayed} games, ${hoursPlayed} hours, and countless memories with ${favoriteChampion}.`, highlight: false },
    { text: `You sure did quite a lot out there, `, highlight: false, name: summonerName },
    { text: ``, highlight: false },
    { text: `Through the wins and the losses,`, highlight: false },
    { text: `The clutch plays and the questionable recalls,`, highlight: false },
    { text: `You showed up and gave it your all.`, highlight: false },
    { text: ``, highlight: false },
    { text: `Every game was another chapter in your legend.`, highlight: false },
    { text: `See you on the Rift, Champion.`, highlight: true },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setVisibleLines((prev) => {
        if (prev < farewellLines.length) {
          return prev + 1;
        }
        clearInterval(interval);
        return prev;
      });
    }, 600); // Each line appears after 600ms (faster)

    return () => clearInterval(interval);
  }, [farewellLines.length]);

  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#2d0a4e] via-[#010A13] to-[#0a1929]">
      {/* Animated gradient - same as champion pool */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.15, 0.25, 0.15],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#8B5CF6] rounded-full blur-[120px] opacity-20"
      />

      {/* Content */}
      <div className="relative z-10 size-full flex flex-col items-center justify-center px-6 sm:px-8 md:px-12">
        <div className="max-w-3xl w-full space-y-3 sm:space-y-4">
          {farewellLines.map((lineObj, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -80 }}
              animate={{
                opacity: index < visibleLines ? 1 : 0,
                x: index < visibleLines ? 0 : -80,
              }}
              transition={{
                duration: 0.6,
                ease: [0.16, 1, 0.3, 1] // Smooth easing
              }}
              className="text-center"
            >
              {lineObj.text === "" ? (
                <div className="h-3" />
              ) : (
                <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl text-[#E8E6E3] leading-relaxed font-serif">
                  {lineObj.text}
                  {lineObj.name && (
                    <span className="text-[#C8AA6E] font-bold">{lineObj.name}.</span>
                  )}
                </p>
              )}
            </motion.div>
          ))}

          {/* Final fade-in emphasis on last line */}
          {visibleLines >= farewellLines.length && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="pt-6 sm:pt-8"
            >
              <div className="w-32 h-px bg-gradient-to-r from-transparent via-[#C8AA6E] to-transparent mx-auto mb-4" />
              <p className="text-xl sm:text-2xl md:text-3xl text-[#C8AA6E] text-center font-serif tracking-wide">
                Until Next Season
              </p>
            </motion.div>
          )}
        </div>
      </div>

      {/* Subtle particles effect */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-[#8B5CF6] rounded-full opacity-30"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.1, 0.4, 0.1],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>
    </div>
  );
}
