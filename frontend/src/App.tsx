import { useState, useEffect, useRef } from "react";
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
import { SocialComparisonSlide } from "./components/slides/SocialComparisonSlide";
import { FarewellSlide } from "./components/slides/FarewellSlide";
import { FinalRecapSlide } from "./components/slides/FinalRecapSlide";
import { SlideNavigation } from "./components/SlideNavigation";
import { ErrorModal } from "./components/ErrorModal";
import { APIError, api } from "./services/api";
import { getUserFriendlyError } from "./utils/errorMessages";
import { preloadAllImages } from "./utils/imagePreloader";
import backgroundMusic from "./assets/sound/League of Legends Season 5.mp3";

export default function App() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [summonerName, setSummonerName] = useState("");
  const [summonerTag, setSummonerTag] = useState("");
  const [region, setRegion] = useState("");
  const [hasStarted, setHasStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState<'searching' | 'found' | 'analyzing' | 'caching'>('searching');
  const [isMusicPlaying, setIsMusicPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // Backend integration state
  const [_sessionId, setSessionId] = useState<string>("");  // Kept for potential future use
  const [sessionData, setSessionData] = useState<any>(null);
  const [playerInfo, setPlayerInfo] = useState<any>(null);
  const [loadingError, setLoadingError] = useState<string>("");
  const [isAnalysisComplete, setIsAnalysisComplete] = useState(false);
  const [showErrorModal, setShowErrorModal] = useState(false);

  const [showHumorPhase, setShowHumorPhase] = useState(false);

  // Audio ref for background music
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.volume = 0.3;

    if (isMusicPlaying) {
      audio.play().catch(error => {
        console.error("Error playing audio:", error);
      });
    } else {
      audio.pause();
    }
  }, [isMusicPlaying]);

  const slidesWithHumor = [4, 6, 8];
  const currentSlideHasHumor = slidesWithHumor.includes(currentSlide);

  useEffect(() => {
    if (!hasStarted || currentSlide === 0 || currentSlide === 1 || currentSlide === 14 || isPaused) return;

    const timer = setTimeout(() => {
      if (currentSlide < 14) {
        if (currentSlideHasHumor && !showHumorPhase) {
          setShowHumorPhase(true);
        } else {
          setCurrentSlide(prev => prev + 1);
          setShowHumorPhase(false);
        }
      }
    }, 10000);

    return () => clearTimeout(timer);
  }, [hasStarted, currentSlide, isPaused, showHumorPhase, currentSlideHasHumor]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!hasStarted || isLoading) return;

      if (e.key === "ArrowRight" && currentSlide < 17) {
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
    setLoadingError("");
    setIsAnalysisComplete(false);
    setLoadingStatus('searching');
    setCurrentSlide(1);

    // Start music when beginning the rewind
    setIsMusicPlaying(true);
    if (audioRef.current) {
      audioRef.current.play().catch(error => {
        console.error("Error starting music:", error);
      });
    }

    try {
      // Call backend API to start rewind
      const response = await api.startRewind({
        gameName: summonerName,
        tagLine: summonerTag,
        region: region
      });
      // Debug the response to ensure sessionId is present
      // eslint-disable-next-line no-console
      console.debug('startRewind response:', response);

      if (!response || !response.sessionId) {
        // If backend didn't return a sessionId, stop and show an error instead of calling follow-up APIs
        const msg = 'Server did not return a sessionId. Please try again.';
        // eslint-disable-next-line no-console
        console.error(msg, response);
        setLoadingError(msg);
        setShowErrorModal(true);
        setIsLoading(false);
        setLoadingStatus('searching');
        return;
      }

      // Player found! API returned successfully
      setSessionId(response.sessionId);
      if (response.player) {
        setPlayerInfo(response.player);
      }

      setLoadingStatus('found');

      await new Promise(resolve => setTimeout(resolve, 1500));

      setLoadingStatus('analyzing')
      const session = await api.waitForComplete(
        response.sessionId,
        () => { }
      );

      // Store analytics
      setSessionData(session.analytics);

      const sessionPlayer = session.player || null;
      const leaderboard = session.analytics?.slide14_percentile?.leaderboard || [];
      const yourEntry = leaderboard.find((e: any) => e.isYou) || null;

      const resolvedPlayer = {
        ...(sessionPlayer || {}),
        summonerLevel: (sessionPlayer && sessionPlayer.summonerLevel) ?? yourEntry?.summonerLevel ?? undefined,
      };

      setPlayerInfo(resolvedPlayer);

      setLoadingStatus('caching');
      await preloadAllImages(session.analytics, () => { });
      setIsAnalysisComplete(true);

    } catch (error) {
      console.error('Error starting rewind:', error);
      if (error instanceof APIError) {
        setLoadingError(error.message);
      } else {
        setLoadingError('Failed to connect to server. Please try again.');
      }
      setShowErrorModal(true);
    }
  };

  const handleLoadingComplete = () => {
    if (sessionData) {
      setIsLoading(false);
      setCurrentSlide(2);
    }
  };

  const handleCloseError = () => {
    setShowErrorModal(false);
    handleRestart();
  };

  const handleRetryAfterError = () => {
    // Reset error states
    setShowErrorModal(false);
    setLoadingError("");
    setIsAnalysisComplete(false);
    setSessionData(null);

    // Restart the process
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
    setLoadingError("");
    setShowErrorModal(false);
    setLoadingStatus('searching');
    setIsAnalysisComplete(false);
    setSessionData(null);
    setIsMusicPlaying(false);
  };

  const togglePause = () => {
    setIsPaused(prev => !prev);
  };

  const nextSlide = () => {
    if (currentSlideHasHumor && !showHumorPhase) {
      setShowHumorPhase(true);
    } else {
      if (currentSlide < 14) {
        setCurrentSlide(prev => prev + 1);
        setShowHumorPhase(false);
      }
    }
  };

  const previousSlide = () => {
    if (currentSlideHasHumor && showHumorPhase) {
      setShowHumorPhase(false);
    } else {
      if (currentSlide > 0) {
        setCurrentSlide(prev => prev - 1);
        setShowHumorPhase(false);
      }
    }
  };

  const displayName = summonerName || "YourUsername";

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
      // Slide 4 - Best Match Stats
      { initial: { opacity: 0, x: 50 }, animate: { opacity: 1, x: 0 }, exit: { opacity: 0, x: -50 } },
      // Slide 5 - Best Match Humor (fade with glow)
      { initial: { opacity: 0, scale: 0.9 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 6 - KDA (slide from bottom)
      { initial: { opacity: 0, y: 100 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -100 } },
      // Slide 7 - Ranked Stats
      { initial: { opacity: 0, scale: 0.8 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 8 - Ranked Humor (fade with glow)
      { initial: { opacity: 0, scale: 0.9 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 9 - Vision (scale with rotate)
      { initial: { opacity: 0, scale: 0.8 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 10 - Champion Pool Stats
      { initial: { opacity: 0, scale: 0.8 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 11 - Champion Pool Humor (fade with glow)
      { initial: { opacity: 0, scale: 0.9 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.1 } },
      // Slide 12 - Duo (slide from sides)
      { initial: { opacity: 0, x: -50, y: 50 }, animate: { opacity: 1, x: 0, y: 0 }, exit: { opacity: 0, x: 50, y: -50 } },
      // Slide 13 - Strengths (slide from top)
      { initial: { opacity: 0, y: -100 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: 100 } },
      // Slide 14 - Weaknesses (fade with slight scale)
      { initial: { opacity: 0, scale: 1.1 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 0.9 } },
      // Slide 15 - Progress (slide from bottom)
      { initial: { opacity: 0, x: -50, y: 50 }, animate: { opacity: 1, x: 0, y: 0 }, exit: { opacity: 0, x: 50, y: -50 } },
      // Slide 16 - Social (slide from right)
      { initial: { opacity: 0, x: 100 }, animate: { opacity: 1, x: 0 }, exit: { opacity: 0, x: -100 } },
      // Slide 17 - Farewell (fade with subtle scale)
      { initial: { opacity: 0, scale: 0.95 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 1.05 } },
      // Slide 18 - Final Recap (fade)
      { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } },
    ];
    return animations[slideIndex] || animations[0];
  };

  const currentAnimation = getSlideAnimation(currentSlide);

  return (
    <div className="size-full bg-[#010A13] overflow-hidden">
      {/* Background Music */}
      <audio
        ref={audioRef}
        src={backgroundMusic}
        loop
        preload="auto"
      />

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
            />
          )}
          {currentSlide === 1 && (
            <LoadingSlide
              playerName={summonerName || "Summoner"}
              onComplete={isAnalysisComplete ? handleLoadingComplete : undefined}
              hasError={!!loadingError}
              loadingStatus={loadingStatus}
              isMusicPlaying={isMusicPlaying}
              onMusicToggle={() => setIsMusicPlaying(!isMusicPlaying)}
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
              showHumor={showHumorPhase}
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
              showHumor={showHumorPhase}
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
              showHumor={showHumorPhase}
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
              aiAnalysis={sessionData.slide10_humor || "Analyzing your gameplay strengths..."}
            />
          )}
          {currentSlide === 11 && (
            <WeaknessesSlide
              weaknesses={sessionData.slide10_11_analysis?.weaknesses || []}
              aiAnalysis={sessionData.slide11_humor || "Analyzing areas for improvement..."}
            />
          )}
          {currentSlide === 12 && (
            <SocialComparisonSlide
              yourRank={sessionData.slide14_percentile?.yourRank || 0}
              rankPercentile={sessionData.slide14_percentile?.rankPercentile || 50}
              leaderboard={sessionData.slide14_percentile?.leaderboard || []}
              aiHumor={sessionData.slide14_humor || "You're in the top ranks! Keep climbing! 🎮✨"}
            />
          )}
          {currentSlide === 13 && (
            <FarewellSlide
              summonerName={displayName}
              season="2025"
              gamesPlayed={sessionData.slide2_timeSpent?.totalGames || 0}
              hoursPlayed={sessionData.slide2_timeSpent?.totalHours || 0}
              favoriteChampion={sessionData.slide3_favoriteChampions?.[0]?.name || "your favorite champion"}
              aiFarewell={sessionData.slide15_farewell || undefined}
            />
          )}
          {currentSlide === 14 && (
            <FinalRecapSlide
              summonerName={displayName}
              playerTitle={sessionData.slide10_11_analysis?.personality_title || "The Rising Legend"}
              year={2025}
              highlightStats={{
                gamesPlayed: sessionData.slide2_timeSpent?.totalGames || 0,
                hoursPlayed: sessionData.slide2_timeSpent?.totalHours || 0,
                peakRank: sessionData.slide6_rankedJourney?.currentRank || "UNRANKED",
                favoriteChampion: sessionData.slide3_favoriteChampions?.[0]?.name || "Unknown",
                kdaRatio: sessionData.slide5_kda?.kdaRatio || 0,
                winRate: sessionData.slide6_rankedJourney?.winRate || 0,
                totalKills: sessionData.slide5_kda?.totalKills || 0,
                uniqueChampions: sessionData.slide8_championPool?.uniqueChampions || 0,
                playerLevel: playerInfo?.summonerLevel || 0,
              }}
              profileIconUrl={sessionData.playerInfo?.profileIconUrl || playerInfo?.profileIconUrl}
              onRestart={handleRestart}
            />
          )}
        </motion.div>
      </AnimatePresence>

      {/* Error Modal */}
      <ErrorModal
        isOpen={showErrorModal}
        error={getUserFriendlyError(loadingError)}
        onClose={handleCloseError}
        onRetry={handleRetryAfterError}
      />

      {hasStarted && !isLoading && (
        <SlideNavigation
          currentSlide={currentSlide}
          totalSlides={15}
          onPrevious={previousSlide}
          onNext={nextSlide}
          isPaused={isPaused}
          onTogglePause={togglePause}
          isMusicPlaying={isMusicPlaying}
          onMusicToggle={() => setIsMusicPlaying(!isMusicPlaying)}
        />
      )}
    </div>
  );
}
