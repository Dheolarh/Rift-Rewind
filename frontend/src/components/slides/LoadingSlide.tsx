import { motion, AnimatePresence } from "motion/react";
import { useState, useEffect, useRef } from "react";
import { Music } from "lucide-react";
import LoadBG from "../../assets/LoadBG.webm";
import "./LoadingSlide.css";

interface LoadingSlideProps {
  playerName?: string;
  onComplete?: () => void;
  hasError?: boolean;
  loadingStatus?: string; // e.g., 'searching', 'found', 'analyzing', 'caching', 'complete'
  isMusicPlaying?: boolean;
  onMusicToggle?: () => void;
}

const loadingMessageSets = {
  searching: [
    "Connecting to the Rift...",
    "Searching for summoner data...",
    "Looking up your account...",
  ],
  found: [
    "Haha, found you!",
    "There you are, {playerName}!",
    "Let's dive in...",
  ],
  analyzing: [
    "Reviewing your game history...",
    "Crunching the numbers...",
    "Checking your match records...",
    "This might take a while",
    "Performing analysis...",
    "Analyzing your performance...",
    "Calculating statistics...",
    "Examining your champion pool...",
    "Tracking your ranked journey...",
    "Measuring your impact...",
    "Evaluating your playstyle...",
    "Almost there, summoner...",
  ],
  caching: [
    "Loading champions...",
    "Preparing your visual experience...",
    "Just a few more seconds...",
    "Almost ready to begin...",
  ]
};

export function LoadingSlide({ 
  playerName = "Summoner", 
  onComplete, 
  hasError = false,
  loadingStatus = 'searching',
  isMusicPlaying = false,
  onMusicToggle 
}: LoadingSlideProps) {
  const [currentMessage, setCurrentMessage] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [currentPhase, setCurrentPhase] = useState<'searching' | 'found' | 'analyzing' | 'caching'>(loadingStatus as any);
  const [displayedMessages, setDisplayedMessages] = useState<string[]>([]);
  const [phaseHistory, setPhaseHistory] = useState<Set<string>>(new Set(['searching']));
  const prevLoadingStatusRef = useRef(loadingStatus);

  // Update phase when loadingStatus changes
  useEffect(() => {
    if (hasError) return;
    
    const newPhase = loadingStatus as 'searching' | 'found' | 'analyzing' | 'caching';
    const prevPhase = prevLoadingStatusRef.current;
    
    if (newPhase !== prevPhase && ['searching', 'found', 'analyzing', 'caching'].includes(newPhase)) {
      setCurrentPhase(newPhase);
      setPhaseHistory(prev => new Set([...prev, newPhase]));
      setCurrentMessage(0);
      prevLoadingStatusRef.current = newPhase;
    }
  }, [loadingStatus, hasError]);

  // Prepare messages for current phase
  useEffect(() => {
    if (hasError) return;
    
    // Defensive: ensure we have a messages array for the current phase
    const phaseMessages = loadingMessageSets[currentPhase as keyof typeof loadingMessageSets] ?? [];
    const messages = phaseMessages.map((msg) =>
      msg.replace("{playerName}", playerName.split("#")[0]),
    );
    
    // For analyzing and caching phases, shuffle messages for variety
    if (currentPhase === 'analyzing' || currentPhase === 'caching') {
      const shuffled = [...messages].sort(() => Math.random() - 0.5);
      setDisplayedMessages(shuffled);
    } else {
      setDisplayedMessages(messages);
    }
  }, [currentPhase, playerName, hasError]);

  // Message rotation logic
  useEffect(() => {
    // Stop message rotation if there's an error or complete
    if (hasError || isComplete) return;
    
    const getInterval = () => {
      if (currentPhase === 'searching') return 2000;
      if (currentPhase === 'found') return 1500;
      if (currentPhase === 'caching') return 2000;
      return 3000; // analyzing phase
    };

    const interval = setInterval(() => {
      setCurrentMessage((prev) => {
        const next = prev + 1;
        
        // For 'searching' and 'found' phases, move to next phase after all messages
        if (next >= displayedMessages.length) {
          if (currentPhase === 'searching' && phaseHistory.has('found')) {
            return 0;
          } else if (currentPhase === 'found' && phaseHistory.has('analyzing')) {
            return prev;
          }
          return (currentPhase === 'analyzing' || currentPhase === 'caching') ? 0 : prev;
        }
        
        return next;
      });
    }, getInterval());

    return () => clearInterval(interval);
  }, [currentPhase, displayedMessages.length, hasError, isComplete, phaseHistory]);

  // When onComplete callback is provided, mark as complete
  useEffect(() => {
    if (onComplete) {
      setIsComplete(true);
    }
  }, [onComplete]);

  const currentMessageText = displayedMessages[currentMessage] || "";

  return (
    <div className="relative size-full overflow-hidden bg-gradient-to-br from-[#010A13] via-[#0A1428] to-[#1a0b2e]">
      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover opacity-20"
      >
        <source src={LoadBG} type="video/webm" />
      </video>

      {/* Dark overlay for better readability */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#010A13]/80 via-[#0A1428]/75 to-[#1a0b2e]/80" />

      {/* Music Toggle Button - Top Left */}
      {onMusicToggle && (
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          onClick={onMusicToggle}
          className="fixed top-4 z-50 w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center bg-gradient-to-br from-[#8B7548]/20 to-[#078378]/20 border border-[#8B7548]/50 backdrop-blur-md hover:border-[#C8AA6E] hover:shadow-lg hover:shadow-[#C8AA6E]/30 transition-all group"
          style={{marginLeft: '15px'}}
          aria-label={isMusicPlaying ? "Mute music" : "Play music"}
        >
          <Music 
            className={`w-5 h-5 sm:w-6 sm:h-6 transition-colors ${
              isMusicPlaying ? 'text-[#C8AA6E]' : 'text-[#8B7548]'
            } group-hover:text-[#C8AA6E]`}
          />
          {isMusicPlaying && (
            <motion.div 
              className="absolute inset-0 border-2 border-[#C8AA6E]"
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          )}
        </motion.button>
      )}
      
      {/* Ripple Loader - hide when error or complete */}
      {!hasError && !isComplete && (
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
      )}

      {/* Content */}
      <div className="relative z-10 size-full flex flex-col items-center justify-center px-4 sm:px-6 gap-8">
        <AnimatePresence mode="wait">
          {!isComplete ? (
            <motion.div
              key={`${currentPhase}-${currentMessage}`}
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
