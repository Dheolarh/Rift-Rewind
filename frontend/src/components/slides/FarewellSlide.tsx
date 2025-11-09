import { motion } from "motion/react";
import { useEffect, useState, useMemo } from "react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import farewellBg from "../../assets/farewell.webp";

interface FarewellSlideProps {
  summonerName?: string;
  season?: string;
  gamesPlayed?: number;
  hoursPlayed?: number;
  favoriteChampion?: string;
  aiFarewell?: string;
}

export function FarewellSlide({
  summonerName = "Summoner",
  season = "2025",
  gamesPlayed = 0,
  hoursPlayed = 0,
  favoriteChampion = "your favorite champion",
  aiFarewell
}: FarewellSlideProps) {
  const [visibleLines, setVisibleLines] = useState(0);

  const farewellText = aiFarewell || `Well, what a season.\n\n${gamesPlayed} games, ${hoursPlayed} hours, and countless memories with ${favoriteChampion}.\n\nYou sure did quite a lot out there, ${summonerName}.\n\nThrough the wins and the losses,\nThe clutch plays and the questionable recalls,\nYou showed up and gave it your all.\n\nEvery game was another chapter in your legend.\n\nSee you on the Rift, Champion.`;

  const farewellLines = farewellText.split('\n');

  useEffect(() => {
    // Reset animation when text changes
    setVisibleLines(0);
    
    // Animate lines appearing one by one
    const timer = setInterval(() => {
      setVisibleLines(prev => {
        if (prev >= farewellLines.length) {
          clearInterval(timer);
          return prev;
        }
        return prev + 1;
      });
  }, 900); // Each line appears every 900ms (slower fade-in for more dramatic pacing)

    return () => clearInterval(timer);
  }, [farewellText, farewellLines.length]);

  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#2d0a4e] via-[#010A13] to-[#0a1929]">
      {/* Background Image */}
      <div className="absolute inset-0">
        <ImageWithFallback
          src={farewellBg}
          alt="Farewell Background"
          className="w-full h-full object-cover opacity-15"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#2d0a4e]/90 via-[#010A13]/95 to-[#0a1929]/98" />
      </div>

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
        <div className="max-w-3xl w-full">
          {farewellLines.map((line, index) => {
            const isVisible = index < visibleLines;
            const isEmptyLine = line.trim() === "";
            const isLastLine = index === farewellLines.length - 1;
            
            // Highlight summoner name if present in the line
            const hasSummonerName = line.includes(summonerName);
            
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{
                  opacity: isVisible ? 1 : 0,
                  y: isVisible ? 0 : 10
                }}
                transition={{
                  duration: 1.0,
                  ease: "easeOut"
                }}
                className="text-center"
                style={{ minHeight: isEmptyLine ? '1.5rem' : 'auto' }}
              >
                {!isEmptyLine && (
                  <p
                    className={`text-lg sm:text-xl md:text-2xl lg:text-3xl leading-relaxed italic tracking-wide ${
                      isLastLine ? 'text-[#C8AA6E] font-semibold' : 'text-[#C8AA6E]/90'
                    }`}
                    style={{ fontFamily: 'Georgia, serif' }}
                  >
                    {hasSummonerName ? (
                      <>
                        {line.split(summonerName).map((part, i, arr) => (
                          <span key={i}>
                            {part}
                            {i < arr.length - 1 && (
                              <span className="text-[#0AC8B9] font-semibold not-italic">
                                {summonerName}
                              </span>
                            )}
                          </span>
                        ))}
                      </>
                    ) : (
                      line
                    )}
                  </p>
                )}
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Subtle particles effect */}
      <div className="absolute inset-0 pointer-events-none">
        {
          // Precompute particle positions so they don't jump on re-render
          // Use vw/vh so they are positioned relative to the viewport and
          // won't collapse to a single edge due to layout quirks.
        }
        {useMemo(() => {
          const particles = Array.from({ length: 20 }).map(() => ({
            left: Math.random() * 100,
            top: Math.random() * 100,
            duration: 3 + Math.random() * 2,
            delay: Math.random() * 2
          }));

          return particles.map((p, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-[#8B5CF6] rounded-full opacity-30"
              style={{ left: `${p.left}vw`, top: `${p.top}vh` }}
              animate={{
                y: [0, -30, 0],
                opacity: [0.1, 0.4, 0.1],
              }}
              transition={{
                duration: p.duration,
                repeat: Infinity,
                delay: p.delay,
                ease: "easeInOut"
              }}
            />
          ));
        }, [])}
      </div>
    </div>
  );
}
