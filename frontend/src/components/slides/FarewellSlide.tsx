import { motion } from "motion/react";
import { useEffect, useState } from "react";

interface FarewellSlideProps {
  summonerName?: string;
  season?: string;
  gamesPlayed?: number;
  hoursPlayed?: number;
  favoriteChampion?: string;
  aiFarewell?: string;
}

// Typing animation component
function TypingText({ text, delay = 0, onComplete, highlightName }: { text: string; delay?: number; onComplete?: () => void; highlightName?: string }) {
  const [displayedText, setDisplayedText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const startDelay = setTimeout(() => {
      if (currentIndex < text.length) {
        const timer = setTimeout(() => {
          setDisplayedText(prev => prev + text[currentIndex]);
          setCurrentIndex(prev => prev + 1);
        }, 30); // 30ms per character for smooth typing

        return () => clearTimeout(timer);
      } else if (onComplete && currentIndex === text.length) {
        onComplete();
      }
    }, delay);

    return () => clearTimeout(startDelay);
  }, [currentIndex, text, delay, onComplete]);

  // If we need to highlight a name, split and render character by character with proper styling
  if (highlightName && text.includes(highlightName)) {
    const nameIndex = text.indexOf(highlightName);
    const beforeName = text.substring(0, nameIndex);
    const nameText = highlightName;
    const afterName = text.substring(nameIndex + highlightName.length);

    const displayedBefore = displayedText.substring(0, Math.min(displayedText.length, nameIndex));
    const displayedNamePart = displayedText.substring(nameIndex, Math.min(displayedText.length, nameIndex + nameText.length));
    const displayedAfter = displayedText.substring(nameIndex + nameText.length);

    return (
      <span>
        {displayedBefore}
        {displayedNamePart && <span className="text-[#0AC8B9] font-semibold">{displayedNamePart}</span>}
        {displayedAfter}
      </span>
    );
  }

  return <span>{displayedText}</span>;
}

export function FarewellSlide({
  summonerName = "Summoner",
  season = "2025",
  gamesPlayed = 0,
  hoursPlayed = 0,
  favoriteChampion = "your favorite champion",
  aiFarewell
}: FarewellSlideProps) {
  const [currentLine, setCurrentLine] = useState(0);

  // Use AI-generated farewell if available, otherwise use default
  const farewellText = aiFarewell || `Well, what a season.\n\n${gamesPlayed} games, ${hoursPlayed} hours, and countless memories with ${favoriteChampion}.\n\nYou sure did quite a lot out there, ${summonerName}.\n\nThrough the wins and the losses,\nThe clutch plays and the questionable recalls,\nYou showed up and gave it your all.\n\nEvery game was another chapter in your legend.\n\nSee you on the Rift, Champion.`;

  // Split AI text into lines (split by newlines)
  const farewellLines = farewellText.split('\n').map((line, index, array) => ({
    text: line,
    highlight: index === array.length - 1 && line.trim() !== '' // Highlight last non-empty line
  }));

  const handleLineComplete = (index: number) => {
    if (index < farewellLines.length - 1) {
      setTimeout(() => {
        setCurrentLine(index + 1);
      }, 100); // Small delay between lines
    }
  };

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
        <div className="max-w-3xl w-full space-y-2 sm:space-y-3">
          {farewellLines.map((lineObj, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0 }}
              animate={{
                opacity: index <= currentLine ? 1 : 0,
              }}
              transition={{
                duration: 0.3,
                ease: "easeOut"
              }}
              className="text-center"
            >
              {lineObj.text === "" ? (
                <div className="h-2" />
              ) : (
                <p className={`text-sm sm:text-base md:text-lg leading-relaxed ${lineObj.highlight ? 'text-[#C8AA6E] font-semibold' : 'text-[#C8AA6E]'}`}>
                  {index <= currentLine && (
                    <TypingText 
                      text={lineObj.text} 
                      delay={0}
                      onComplete={() => handleLineComplete(index)}
                      highlightName={lineObj.text.includes(summonerName) ? summonerName : undefined}
                    />
                  )}
                </p>
              )}
            </motion.div>
          ))}

          {/* Final fade-in emphasis on last line */}
          {currentLine >= farewellLines.length - 1 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, duration: 0.8 }}
              className="pt-4 sm:pt-6"
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
