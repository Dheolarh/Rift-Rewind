import { motion, AnimatePresence } from "motion/react";
import { useState, useEffect } from "react";
import "./LoadingSlide.css";

interface LoadingSlideProps {
  playerName?: string;
  onComplete?: () => void;
  hasError?: boolean;
}

// Dynamic loading messages with League of Legends gimmicks
const loadingMessageSets = {
  initial: [
    "Connecting to the Rift...",
    "Connected",
    "Checking how much chaos you caused...",
    "Hmmm {playerName} right?",
    "I see......",
  ],
  ongoing: [
    "Haha we found you!",
    "Wow I'm seeing some numbers here...",
    "Wait... is that even possible?",
    "Oh my... someone's been busy!",
    "Calculating the damage...",
    "Counting all those pentakills... or not",
    "Analyzing your masterpieces",
    "Checking if you Ward properly... spoiler alert",
    "So many champions, so little time",
    "Your enemies remember you well",
    "The Rift remembers everything",
    "Digging through the replays",
    "Finding your highlights",
    "And your lowlights too...",
    "Hold on, this is interesting",
    "Hmm, that's a lot of games",
    "Someone loves this game!",
    "Crunching the numbers",
    "Reading between the lines",
    "Your stats are loading",
    "Almost there, summoner",
    "Patience is a virtue",
    "Good things come to those who wait",
    "The anticipation builds...",
    "Just a moment longer",
  ]
};

export function LoadingSlide({ playerName = "Summoner", onComplete, hasError = false }: LoadingSlideProps) {
  const [currentMessage, setCurrentMessage] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [messagePhase, setMessagePhase] = useState<'initial' | 'ongoing'>('initial');
  const [ongoingMessages, setOngoingMessages] = useState<string[]>([]);

  const initialMessages = loadingMessageSets.initial.map(msg => 
    msg.replace('{playerName}', playerName)
  );

  useEffect(() => {
    const shuffled = [...loadingMessageSets.ongoing].sort(() => Math.random() - 0.5);
    setOngoingMessages(shuffled);
  }, []);

  useEffect(() => {
    // Stop message rotation if there's an error
    if (hasError) return;
    
    const interval = setInterval(() => {
      if (messagePhase === 'initial') {
        setCurrentMessage((prev) => {
          const next = prev + 1;
          if (next >= initialMessages.length) {
            // Switch to ongoing phase
            setMessagePhase('ongoing');
            setCurrentMessage(0);
            return 0;
          }
          return next;
        });
      } else {
        // Ongoing phase - cycle through random messages
        setCurrentMessage((prev) => {
          const next = (prev + 1) % ongoingMessages.length;
          return next;
        });
      }
    }, messagePhase === 'initial' ? 2000 : 3000); // 2s for initial, 3s for ongoing

    return () => clearInterval(interval);
  }, [messagePhase, initialMessages.length, ongoingMessages.length, hasError]);

  // When onComplete callback is provided, mark as complete
  useEffect(() => {
    if (onComplete) {
      setIsComplete(true);
    }
  }, [onComplete]);

  const currentMessageText = messagePhase === 'initial' 
    ? initialMessages[currentMessage] 
    : ongoingMessages[currentMessage];

  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#010A13] via-[#0A1428] to-[#1a0b2e]">
      {/* Ripple Loader */}
      <div className="ripple-container">
        <div className="hole">
          <i />
          <i />
          <i />
          <i />
          <i />
          <i />
          <i />
          <i />
          <i />
          <i />
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 size-full flex flex-col items-center justify-center px-4 sm:px-6 gap-8">
        {/* Loading Messages or Begin Button */}
        <AnimatePresence mode="wait">
          {!isComplete ? (
            <motion.div
              key={`${messagePhase}-${currentMessage}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.5 }}
              className="text-center max-w-md"
            >
              <p className="text-lg sm:text-xl md:text-2xl text-[#E8E6E3] font-semibold">
                {currentMessageText}
              </p>
            </motion.div>
          ) : onComplete ? (
            <motion.button
              key="begin-button"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              onClick={onComplete}
              className="text-center max-w-md"
            >
              <p className="text-lg sm:text-xl md:text-2xl text-[#C8AA6E] font-semibold 
                          hover:text-[#E8C478] transition-colors cursor-pointer">
                BEGIN YOUR REWIND
              </p>
            </motion.button>
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  );
}
