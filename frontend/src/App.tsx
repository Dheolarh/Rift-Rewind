import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { WelcomeSlide } from "./components/slides/WelcomeSlide";
import { LoadingSlide } from "./components/slides/LoadingSlide";
import { TimeSpentSlide } from "./components/slides/TimeSpentSlide";
import { FavoriteChampionsSlide } from "./components/slides/FavoriteChampionsSlide";
import { BestMatchSlide } from "./components/slides/BestMatchSlide";
import { KDAOverviewSlide } from "./components/slides/KDAOverviewSlide";
import { RankedJourneySlide } from "./components/slides/RankedJourneySlide";
import { VisionSlide } from "./components/slides/VisionSlide";
import { ChampionPoolSlide } from "./components/slides/ChampionPoolSlide";
import { DuoPartnerSlide } from "./components/slides/DuoPartnerSlide";
import { StrengthsSlide } from "./components/slides/StrengthsSlide";
import { WeaknessesSlide } from "./components/slides/WeaknessesSlide";
import { ProgressSlide } from "./components/slides/ProgressSlide";
import { AchievementsSlide } from "./components/slides/AchievementsSlide";
import { SocialComparisonSlide } from "./components/slides/SocialComparisonSlide";
import { FinalRecapSlide } from "./components/slides/FinalRecapSlide";
import { SlideNavigation } from "./components/SlideNavigation";
import { ErrorModal } from "./components/ErrorModal";
import api, { APIError } from "./services/api";

// Mock data with AI humor for each slide
const mockData = {
  timeSpent: {
    hoursPlayed: 847,
    gamesPlayed: 1243,
    aiHumor: "That's approximately 47 binge-worthy Netflix series... but who's counting? 📺"
  },
  favoriteChampions: {
    champions: [
      { name: "Yasuo", mastery: 487250, games: 342, winRate: 58 },
      { name: "Lee Sin", mastery: 356890, games: 287, winRate: 54 },
      { name: "Thresh", mastery: 298450, games: 234, winRate: 61 },
      { name: "Ahri", mastery: 245000, games: 198, winRate: 56 },
      { name: "Zed", mastery: 198500, games: 176, winRate: 52 },
    ],
    aiHumor: "Looks like someone has a type... High skill ceiling champions and pain! 😅"
  },
  bestMatch: {
    championName: "Yasuo",
    kills: 24,
    deaths: 3,
    assists: 18,
    kda: 14.0,
    date: "October 15, 2024",
    aiHumor: "This match was so epic, even the enemy team was probably cheering for you! 🎭"
  },
  kdaOverview: {
    averageKDA: 3.8,
    totalKills: 8742,
    totalDeaths: 5234,
    totalAssists: 11203,
    aiHumor: "You've eliminated more champions than there are people in a small village! 🏰"
  },
  rankedJourney: {
    startRank: "Silver II",
    endRank: "Platinum I",
    peakRank: "Diamond IV",
    milestones: [
      { rank: "Silver", division: "II", month: "January", lp: 42 },
      { rank: "Gold", division: "IV", month: "March", lp: 68 },
      { rank: "Gold", division: "I", month: "May", lp: 84 },
      { rank: "Platinum", division: "III", month: "July", lp: 55 },
      { rank: "Diamond", division: "IV", month: "September", lp: 12 },
      { rank: "Platinum", division: "I", month: "December", lp: 76 },
    ],
    aiHumor: "You climbed more ranks than a chess grandmaster... but with way more rage quits! ♟️😤"
  },
  vision: {
    wardsPlaced: 12847,
    wardsDestroyed: 3542,
    visionScore: 89234,
    controlWardsBought: 2156,
    aiHumor: "You've placed more wards than a hospital has patients! 🏥 Your map awareness is legendary!"
  },
  championPool: {
    uniqueChampions: 47,
    mostPlayedRole: "Mid Lane",
    champions: [
      { name: "Yasuo", games: 342, role: "Mid" },
      { name: "Lee Sin", games: 287, role: "Jungle" },
      { name: "Thresh", games: 234, role: "Support" },
      { name: "Jinx", games: 198, role: "ADC" },
      { name: "Ahri", games: 176, role: "Mid" },
      { name: "Jhin", games: 154, role: "ADC" },
      { name: "Zed", games: 143, role: "Mid" },
      { name: "Vayne", games: 132, role: "ADC" },
      { name: "Lux", games: 121, role: "Support" },
      { name: "Ekko", games: 108, role: "Jungle" },
      { name: "Akali", games: 97, role: "Mid" },
      { name: "Ezreal", games: 89, role: "ADC" },
      { name: "Morgana", games: 76, role: "Support" },
      { name: "Irelia", games: 68, role: "Top" },
      { name: "Kai'Sa", games: 54, role: "ADC" },
      { name: "Blitzcrank", games: 43, role: "Support" },
    ],
  },
  duoPartner: {
    partnerName: "SummonerX",
    gamesPlayed: 287,
    winRate: 64,
    favoriteCombo: {
      yourChampion: "Yasuo",
      theirChampion: "Malphite",
    },
    aiHumor: "You two are like peanut butter and jelly... if jelly could flash-ult and secure pentas! 🥜✨"
  },
  strengths: [
    {
      title: "Mechanical Outplays",
      description: "Your ability to execute complex combos and outplay opponents in critical moments sets you apart.",
      score: 92,
      icon: "zap" as const,
    },
    {
      title: "Objective Control",
      description: "Superior map awareness and timing for securing dragons, barons, and turrets.",
      score: 87,
      icon: "target" as const,
    },
    {
      title: "Team Fighting",
      description: "Exceptional positioning and target selection in 5v5 engagements.",
      score: 85,
      icon: "shield" as const,
    },
    {
      title: "Aggressive Plays",
      description: "Bold early game aggression that creates advantages for your team.",
      score: 89,
      icon: "swords" as const,
    },
  ],
  weaknesses: [
    {
      title: "Vision Denial",
      description: "Opportunities to deny enemy vision are sometimes missed, giving opponents map control.",
      improvement: "Focus on buying control wards and sweeping key areas before objectives.",
      icon: "alert" as const,
    },
    {
      title: "CS in Late Game",
      description: "Farming efficiency drops in late game scenarios when prioritizing team fights.",
      improvement: "Take advantage of wave management between objectives to maintain gold income.",
      icon: "trending" as const,
    },
    {
      title: "Overextension",
      description: "Aggressive playstyle sometimes leads to risky positions without vision or backup.",
      improvement: "Check minimap before pushing deep and communicate dive intentions with team.",
      icon: "xcircle" as const,
    },
    {
      title: "Champion Pool Depth",
      description: "Heavy reliance on comfort picks can make you predictable in champion select.",
      improvement: "Expand your pool with 2-3 meta champions to adapt to enemy compositions.",
      icon: "brain" as const,
    },
  ],
  progress: {
    improvement: {
      winRate: 6,
      kda: 0.6,
      visionScore: 9,
    },
    aiHumor: "You've grown more than a Cho'Gath with full stacks! 🦖 The grind never stops!"
  },
  achievements: [
    {
      title: "Pentakill Master",
      description: "Achieved 5 pentakills in ranked games",
      rarity: "legendary" as const,
      icon: "crown" as const,
      dateEarned: "Oct 23, 2024",
    },
    {
      title: "Vision Legend",
      description: "Placed 10,000+ wards in a season",
      rarity: "epic" as const,
      icon: "star" as const,
      dateEarned: "Nov 12, 2024",
    },
    {
      title: "Comeback King",
      description: "Won 50 games after being 10k gold down",
      rarity: "rare" as const,
      icon: "flame" as const,
      dateEarned: "Aug 5, 2024",
    },
    {
      title: "Speed Demon",
      description: "Won a game in under 15 minutes",
      rarity: "epic" as const,
      icon: "zap" as const,
      dateEarned: "Sep 18, 2024",
    },
    {
      title: "100 Game Streak",
      description: "Played 100 consecutive ranked games",
      rarity: "rare" as const,
      icon: "trophy" as const,
      dateEarned: "Jul 30, 2024",
    },
    {
      title: "Baron Stealer",
      description: "Stole Baron Nashor 25 times",
      rarity: "epic" as const,
      icon: "award" as const,
      dateEarned: "Dec 3, 2024",
    },
  ],
  socialComparison: {
    yourRank: 15847,
    percentile: 8,
    leaderboard: [
      { rank: 1, summonerName: "ProPlayer99", winRate: 68, gamesPlayed: 892 },
      { rank: 2, summonerName: "DiamondAce", winRate: 65, gamesPlayed: 1024 },
      { rank: 3, summonerName: "ChallMaster", winRate: 64, gamesPlayed: 756 },
      { rank: 4, summonerName: "YourUsername", winRate: 57, gamesPlayed: 1243, isYou: true },
      { rank: 5, summonerName: "MidLaner42", winRate: 56, gamesPlayed: 987 },
      { rank: 6, summonerName: "JungleKing", winRate: 55, gamesPlayed: 834 },
      { rank: 7, summonerName: "SupportMain", winRate: 55, gamesPlayed: 1156 },
    ],
    aiHumor: "You're rubbing shoulders with the elite! Just... digitally. And they probably don't know you exist. 😎"
  },
};

export default function App() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [summonerName, setSummonerName] = useState("");
  const [summonerTag, setSummonerTag] = useState("");
  const [region, setRegion] = useState("");
  const [hasStarted, setHasStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isMusicPlaying, setIsMusicPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  
  // Backend integration state
  const [sessionId, setSessionId] = useState<string>("");
  const [sessionData, setSessionData] = useState<any>(null);
  const [loadingError, setLoadingError] = useState<string>("");
  const [isAnalysisComplete, setIsAnalysisComplete] = useState(false);
  const [showErrorModal, setShowErrorModal] = useState(false);

  // Auto-advance slides after 10 seconds (but not on welcome, loading or final slide, and when not paused)
  useEffect(() => {
    if (!hasStarted || currentSlide === 0 || currentSlide === 1 || currentSlide === 15 || isPaused) return;
    
    const timer = setTimeout(() => {
      if (currentSlide < 15) {
        setCurrentSlide(prev => prev + 1);
      }
    }, 10000);

    return () => clearTimeout(timer);
  }, [hasStarted, currentSlide, isPaused]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!hasStarted || isLoading) return;
      
      if (e.key === "ArrowRight" && currentSlide < 15) {
        setCurrentSlide(prev => prev + 1);
      } else if (e.key === "ArrowLeft" && currentSlide > 1) {
        setCurrentSlide(prev => prev - 1);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [hasStarted, currentSlide, isLoading]);

  const handleStart = async () => {
    setHasStarted(true);
    setIsLoading(true);
    setCurrentSlide(1); // Show loading slide
    setLoadingError("");
    setIsAnalysisComplete(false);
    
    try {
      // Call backend API to start rewind
      const response = await api.startRewind({
        gameName: summonerName,
        tagLine: summonerTag,
        region: region
      });
      
      setSessionId(response.sessionId);
      
      // Wait for analysis to complete
      const session = await api.waitForComplete(
        response.sessionId,
        (status) => {
          console.log('Processing status:', status);
        }
      );
      
      setSessionData(session.analytics);
      setIsAnalysisComplete(true);
      
    } catch (error) {
      console.error('Error starting rewind:', error);
      if (error instanceof APIError) {
        setLoadingError(error.message);
      } else {
        setLoadingError('Failed to connect to server. Please try again.');
      }
      setIsAnalysisComplete(true); // Show button even on error
      setShowErrorModal(true); // Show error modal
    }
  };

  const handleLoadingComplete = () => {
    if (sessionData) {
      setIsLoading(false);
      setCurrentSlide(2); // Move to Time Spent slide
    } else if (loadingError) {
      // Error modal will be shown, just go back
      handleRestart();
    }
  };

  const handleCloseError = () => {
    setShowErrorModal(false);
    handleRestart();
  };

  const handleRetryAfterError = () => {
    setShowErrorModal(false);
    handleStart();
  };

  const handleRestart = () => {
    setCurrentSlide(0);
    setSummonerName("");
    setSummonerTag("");
    setRegion("");
    setHasStarted(false);
    setIsLoading(false);
    setIsPaused(false);
  };

  const togglePause = () => {
    setIsPaused(prev => !prev);
  };

  const nextSlide = () => {
    if (currentSlide < 15) {
      setCurrentSlide(prev => prev + 1);
    }
  };

  const previousSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(prev => prev - 1);
    }
  };

  const goToSlide = (index: number) => {
    if (hasStarted || index === 0) {
      setCurrentSlide(index);
    }
  };

  const displayName = summonerName || "YourUsername";

  // Get current slide AI humor
  const getCurrentHumor = () => {
    switch(currentSlide) {
      case 1: return mockData.timeSpent.aiHumor;
      case 2: return mockData.favoriteChampions.aiHumor;
      case 3: return mockData.bestMatch.aiHumor;
      case 4: return mockData.kdaOverview.aiHumor;
      case 5: return mockData.rankedJourney.aiHumor;
      case 6: return mockData.vision.aiHumor;
      case 7: return "You've mastered more champions than most people have mastered breathing! 🎮";
      case 8: return mockData.duoPartner.aiHumor;
      case 9: return "These are the skills that separate the good from the legendary! ⚡";
      case 10: return "Every weakness is just a strength waiting to be discovered! 💪";
      case 11: return mockData.progress.aiHumor;
      case 12: return "Achievement unlocked: Being absolutely legendary! 🏆";
      case 13: return mockData.socialComparison.aiHumor;
      default: return "";
    }
  };

  // Different animation variants for each slide
  const getSlideAnimation = (slideIndex: number) => {
    const animations = [
      // Slide 0 - Welcome (default)
      { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } },
      // Slide 1 - Time (scale up)
      { initial: { opacity: 0, scale: 0.8 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 2 - Champions (fade with scale)
      { initial: { opacity: 0, scale: 0.95 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.05 } },
      // Slide 3 - Best Match (slide from right)
      { initial: { opacity: 0, scale: 0.8 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 4 - KDA (slide from bottom)
      { initial: { opacity: 0, y: 100 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -100 } },
      // Slide 5 - Ranked (slide from left)
      { initial: { opacity: 0, scale: 0.8 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 6 - Vision (scale with rotate)
      { initial: { opacity: 0, scale: 0.8 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 7 - Champion Pool (flip)
      { initial: { opacity: 0, scale: 0.8 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 8 - Duo (slide from sides)
      { initial: { opacity: 0, x: -50, y: 50 }, animate: { opacity: 1, x: 0, y: 0 }, exit: { opacity: 0, x: 50, y: -50 } },
      // Slide 9 - Strengths (slide from top)
      { initial: { opacity: 0, y: -100 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: 100 } },
      // Slide 10 - Weaknesses (fade with slight scale)
      { initial: { opacity: 0, scale: 1.1 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 0.9 } },
      // Slide 11 - Progress (slide from bottom)
      { initial: { opacity: 0, x: -50, y: 50 }, animate: { opacity: 1, x: 0, y: 0 }, exit: { opacity: 0, x: 50, y: -50 } },
      // Slide 12 - Achievements (rotate in)
      { initial: { opacity: 0, x: -50, y: 50 }, animate: { opacity: 1, x: 0, y: 0 }, exit: { opacity: 0, x: 50, y: -50 } },
      // Slide 13 - Social (slide from right)
      { initial: { opacity: 0, x: 100 }, animate: { opacity: 1, x: 0 }, exit: { opacity: 0, x: -100 } },
      // Slide 14 - Final (fade)
      { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } },
    ];
    return animations[slideIndex] || animations[0];
  };

  const currentAnimation = getSlideAnimation(currentSlide);

  return (
    <div className="size-full bg-[#010A13] overflow-hidden">
      <AnimatePresence mode="wait">
        <motion.div
          key={currentSlide}
          initial={currentAnimation.initial}
          animate={currentAnimation.animate}
          exit={currentAnimation.exit}
          transition={{ duration: 0.7, ease: [0.43, 0.13, 0.23, 0.96] }}
          className="size-full"
        >
          {currentSlide === 0 && (
            <WelcomeSlide
              summonerName={summonerName}
              summonerTag={summonerTag}
              region={region}
              onSummonerNameChange={setSummonerName}
              onSummonerTagChange={setSummonerTag}
              onRegionChange={setRegion}
              onStart={handleStart}
              isMusicPlaying={isMusicPlaying}
              onMusicToggle={() => setIsMusicPlaying(!isMusicPlaying)}
            />
          )}
          {currentSlide === 1 && (
            <LoadingSlide 
              playerName={summonerName || "Summoner"} 
              onComplete={isAnalysisComplete ? handleLoadingComplete : undefined}
            />
          )}
          {currentSlide === 2 && sessionData && (
            <TimeSpentSlide
              hoursPlayed={sessionData.slide2_timeSpent?.totalHours || 0}
              gamesPlayed={sessionData.slide2_timeSpent?.totalGames || 0}
              minutesPlayed={sessionData.slide2_timeSpent?.totalMinutes || 0}
              averageGameLength={sessionData.slide2_timeSpent?.avgGameLength || 0}
              summonerName={displayName}
              aiHumor={sessionData.slide2_humor || "Time flies when you're having fun on the Rift!"}
            />
          )}
          {currentSlide === 3 && sessionData && (
            <FavoriteChampionsSlide 
              champions={sessionData.slide3_favoriteChampions || []} 
              aiHumor={sessionData.slide3_humor || "Looks like someone has a type!"}
            />
          )}
          {currentSlide === 4 && sessionData && sessionData.slide4_bestMatch && (
            <BestMatchSlide 
              {...sessionData.slide4_bestMatch}
              aiHumor={sessionData.slide4_humor || "This match was so epic, even the enemy team was probably cheering for you! 🎭"}
            />
          )}
          {currentSlide === 5 && sessionData && sessionData.slide5_kda && (
            <KDAOverviewSlide 
              averageKDA={sessionData.slide5_kda.kdaRatio}
              totalKills={sessionData.slide5_kda.totalKills}
              totalDeaths={sessionData.slide5_kda.totalDeaths}
              totalAssists={sessionData.slide5_kda.totalAssists}
              aiHumor={sessionData.slide5_humor || "You've eliminated more champions than there are people in a small village! 🏰"}
            />
          )}
          {currentSlide === 6 && sessionData && sessionData.slide6_rankedJourney && (
            <RankedJourneySlide 
              {...sessionData.slide6_rankedJourney}
              aiHumor={sessionData.slide6_humor || "You climbed more ranks than a chess grandmaster... but with way more rage quits! ♟️😤"}
            />
          )}
          {currentSlide === 7 && sessionData && sessionData.slide7_visionScore && (
            <VisionSlide 
              {...sessionData.slide7_visionScore}
              aiHumor={sessionData.slide7_humor || "You've placed more wards than a hospital has patients! 🏥"}
            />
          )}
          {currentSlide === 8 && sessionData && sessionData.slide8_championPool && (
            <ChampionPoolSlide 
              {...sessionData.slide8_championPool}
              aiHumor={sessionData.slide8_humor || "Talk about champion diversity! You're basically a one-person champion ocean. 🌊"}
            />
          )}
          {currentSlide === 9 && sessionData && sessionData.slide9_duoPartner && (
            <DuoPartnerSlide 
              {...sessionData.slide9_duoPartner}
              playerName={displayName}
              aiHumor={sessionData.slide9_humor || "You two are like peanut butter and jelly... if jelly could flash-ult and secure pentas! 🥜✨"}
            />
          )}
          {currentSlide === 10 && (
            <StrengthsSlide 
              strengths={sessionData.slide10_11_analysis?.strengths || []} 
              aiHumor={sessionData.slide10_humor || "Your gameplay is so clean, you must have a mental checklist longer than a patch notes document! 📋✨"}
            />
          )}
          {currentSlide === 11 && (
            <WeaknessesSlide 
              weaknesses={sessionData.slide10_11_analysis?.weaknesses || []} 
              aiHumor={sessionData.slide11_humor || "Remember: even Faker started as a Bronze player. You've got this! 💪✨"}
            />
          )}
          {currentSlide === 12 && (
            <ProgressSlide 
              message={sessionData.slide12_progress?.message}
              currentSeason={sessionData.slide12_progress?.currentSeason}
              aiHumor={sessionData.slide12_humor || "Every match is another chapter in your legend! 📖✨"}
            />
          )}
          {currentSlide === 13 && (
            <AchievementsSlide 
              achievements={sessionData.slide13_achievements || []}
              aiHumor={sessionData.slide13_humor || "Achievement unlocked: Being absolutely legendary! 🏆✨"}
            />
          )}
          {currentSlide === 14 && (
            <SocialComparisonSlide 
              yourRank={sessionData.slide14_percentile?.yourRank || 0}
              rankPercentile={sessionData.slide14_percentile?.rankPercentile || 50}
              leaderboard={sessionData.slide14_percentile?.leaderboard || []}
              aiHumor={sessionData.slide14_humor || "You're rubbing shoulders with the elite! 🎮✨"}
            />
          )}
          {currentSlide === 15 && (
            <FinalRecapSlide
              summonerName={displayName}
              playerTitle={sessionData.slide10_11_analysis?.personality_title || "The Rising Legend"}
              year={2025}
              highlightStats={{
                gamesPlayed: sessionData.slide2_timeSpent?.totalGames || 0,
                hoursPlayed: sessionData.slide2_timeSpent?.totalHours || 0,
                peakRank: sessionData.slide6_rankedJourney?.currentRank || "UNRANKED",
                favoriteChampion: sessionData.slide3_favoriteChampions?.[0]?.champion || "Unknown",
                kdaRatio: sessionData.slide5_kda?.kdaRatio || 0,
                winRate: sessionData.slide6_rankedJourney?.winRate || 0,
              }}
              onRestart={handleRestart}
            />
          )}
        </motion.div>
      </AnimatePresence>

      {/* Error Modal */}
      <ErrorModal
        isOpen={showErrorModal}
        error={loadingError}
        onClose={handleCloseError}
        onRetry={handleRetryAfterError}
      />

      {hasStarted && !isLoading && (
        <SlideNavigation
          currentSlide={currentSlide}
          totalSlides={16}
          onPrevious={previousSlide}
          onNext={nextSlide}
          isPaused={isPaused}
          onTogglePause={togglePause}
        />
      )}
    </div>
  );
}
