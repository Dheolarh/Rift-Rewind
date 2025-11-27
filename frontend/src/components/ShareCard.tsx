import { motion, AnimatePresence } from "motion/react";
import { X, Download } from "lucide-react";
import { ImageWithFallback } from "./source/ImageWithFallback";
import logoImage from "../assets/logo.webp";
import lolLogo from "../assets/LeagueOfLegends.webp";
import { useRef } from "react";
import { getChampionSplashUrl } from "../utils/championImages";

interface ShareCardProps {
  isOpen: boolean;
  onClose: () => void;
  summonerName: string;
  playerTitle: string;
  year: number;
  stats: {
    gamesPlayed: number;
    hoursPlayed: number;
    peakRank: string;
    favoriteChampion: string;
    kdaRatio: number;
    winRate: number;
    totalKills: number;
    uniqueChampions: number;
    playerLevel: number;
  };
}

export function ShareCard({ isOpen, onClose, summonerName, playerTitle, year, stats }: ShareCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  // Get champion splash art URL
  const championSplashUrl = getChampionSplashUrl(stats.favoriteChampion);

  const handleDownload = async () => {
    if (!cardRef.current) return;

    try {
      const domtoimage = (await import('dom-to-image')).default;
      
      const dataUrl = await domtoimage.toPng(cardRef.current, {
        quality: 1,
        width: 400 * 2,
        height: 200 * 2,
        style: {
          transform: 'scale(2)',
          transformOrigin: 'top left',
          width: '400px',
          height: '200px'
        }
      });

      const link = document.createElement('a');
      link.download = `${summonerName}-RiftRewind-${year}.png`;
      link.href = dataUrl;
      link.click();
    } catch (error) {
      console.error('Failed to generate image:', error);
      alert('Failed to download image. Please try again.');
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
          >
            {/* Close button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center bg-white/10 hover:bg-white/20 rounded-full transition-colors z-10"
            >
              <X className="w-6 h-6 text-white" />
            </button>

            {/* Container for card and download button */}
            <div className="flex flex-col items-center gap-4" onClick={(e) => e.stopPropagation()}>
              {/* Wide Landscape Card with Champion Background - 16:9 */}
              <motion.div
                initial={{ scale: 0.8, opacity: 0, y: 30 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.8, opacity: 0, y: 30 }}
                transition={{ type: "spring", damping: 25, stiffness: 200 }}
                ref={cardRef}
                className="relative border-4 border-[#C8AA6E] overflow-hidden"
                style={{width: "400px", height: "200px"}}
              >
                {/* Champion Splash Background with Dark Dim */}
                <div className="absolute inset-0">
                  <ImageWithFallback
                    src={championSplashUrl}
                    alt={stats.favoriteChampion}
                    className="w-full h-full object-cover"
                    style={{ filter: 'brightness(0.35) saturate(0.8)' }}
                  />
                </div>

                {/* Content Container with Padding from Edges */}
                <div className="relative w-full h-full flex" style={{ padding: '12px' }}>
                  {/* Left Side - Stats */}
                  <div className="flex flex-col justify-between" style={{ width: '65%', paddingRight: '8px' }}>
                    {/* Player Name & Title */}
                    <div style={{ marginBottom: '6px' }}>
                      <h2 className="text-[#C8AA6E] uppercase tracking-wide" style={{ fontFamily: 'Georgia, serif', fontSize: '12px', fontWeight: 'bold', marginBottom: '2px', lineHeight: '1.2' }}>
                        {summonerName}
                      </h2>
                      <p className="text-[#A09B8C] italic" style={{ fontSize: '8px' }}>{playerTitle}</p>
                    </div>

                    {/* Stats Grid - 3 columns, compact - ALL 8 STATS */}
                    <div className="grid grid-cols-3" style={{ gap: '3px', flex: '1' }}>
                      {/* Hours - Teal border like Final Recap */}
                      <div className="bg-black/70 backdrop-blur-sm border border-[#0AC8B9]/30 text-center flex flex-col justify-center" style={{ padding: '3px' }}>
                        <div className="text-[#0AC8B9] tabular-nums" style={{ fontFamily: 'Georgia, serif', fontSize: '11px', fontWeight: 'bold' }}>
                          {Math.trunc(stats.hoursPlayed)}
                        </div>
                        <div className="text-[#A09B8C] uppercase tracking-widest" style={{ fontSize: '6px', marginTop: '1px' }}>Hours</div>
                      </div>

                      {/* Games - Gold border like Final Recap */}
                      <div className="bg-black/70 backdrop-blur-sm border border-[#C8AA6E]/30 text-center flex flex-col justify-center" style={{ padding: '3px' }}>
                        <div className="text-[#C8AA6E] tabular-nums" style={{ fontFamily: 'Georgia, serif', fontSize: '11px', fontWeight: 'bold' }}>
                          {stats.gamesPlayed}
                        </div>
                        <div className="text-[#A09B8C] uppercase tracking-widest" style={{ fontSize: '6px', marginTop: '1px' }}>Games</div>
                      </div>

                      {/* Win Rate - Teal border like Final Recap */}
                      <div className="bg-black/70 backdrop-blur-sm border border-[#0AC8B9]/30 text-center flex flex-col justify-center" style={{ padding: '3px' }}>
                        <div className="text-[#0AC8B9] tabular-nums" style={{ fontFamily: 'Georgia, serif', fontSize: '11px', fontWeight: 'bold' }}>
                          {stats.winRate.toFixed(1)}%
                        </div>
                        <div className="text-[#A09B8C] uppercase tracking-widest" style={{ fontSize: '6px', marginTop: '1px' }}>Win Rate</div>
                      </div>

                      {/* Kills - Red border like Final Recap */}
                      <div className="bg-black/70 backdrop-blur-sm border border-[#FF4444]/30 text-center flex flex-col justify-center" style={{ padding: '3px' }}>
                        <div className="text-[#FF4444] tabular-nums" style={{ fontFamily: 'Georgia, serif', fontSize: '11px', fontWeight: 'bold' }}>
                          {stats.totalKills}
                        </div>
                        <div className="text-[#A09B8C] uppercase tracking-widest" style={{ fontSize: '6px', marginTop: '1px' }}>Kills</div>
                      </div>

                      {/* KDA - Gold border with gold text like Final Recap */}
                      <div className="bg-black/70 backdrop-blur-sm border border-[#C8AA6E]/30 text-center flex flex-col justify-center" style={{ padding: '3px' }}>
                        <div className="text-[#FFD700] tabular-nums" style={{ fontFamily: 'Georgia, serif', fontSize: '11px', fontWeight: 'bold' }}>
                          {stats.kdaRatio.toFixed(2)}
                        </div>
                        <div className="text-[#A09B8C] uppercase tracking-widest" style={{ fontSize: '6px', marginTop: '1px' }}>KDA</div>
                      </div>

                      {/* Main Champion - Purple border like Final Recap */}
                      <div className="bg-black/70 backdrop-blur-sm border border-[#8B5CF6]/30 text-center flex flex-col justify-center" style={{ padding: '3px' }}>
                        <div className="text-white truncate" style={{ fontFamily: 'Georgia, serif', fontSize: '9px', fontWeight: 'bold' }}>
                          {stats.favoriteChampion}
                        </div>
                        <div className="text-[#A09B8C] uppercase tracking-widest" style={{ fontSize: '6px', marginTop: '1px' }}>Main</div>
                      </div>

                      {/* Peak Rank - Gold border like Final Recap */}
                      <div className="bg-black/70 backdrop-blur-sm border border-[#C8AA6E]/30 text-center flex flex-col justify-center" style={{ padding: '3px' }}>
                        <div className="text-[#C8AA6E]" style={{ fontFamily: 'Georgia, serif', fontSize: '8px', fontWeight: 'bold' }}>
                          {stats.peakRank}
                        </div>
                        <div className="text-[#A09B8C] uppercase tracking-widest" style={{ fontSize: '6px', marginTop: '1px' }}>Peak Rank</div>
                      </div>

                      {/* Unique Champions - Purple border like Final Recap */}
                      <div className="bg-black/70 backdrop-blur-sm border border-[#8B5CF6]/30 text-center flex flex-col justify-center" style={{ padding: '3px' }}>
                        <div className="text-[#8B5CF6] tabular-nums" style={{ fontFamily: 'Georgia, serif', fontSize: '11px', fontWeight: 'bold' }}>
                          {stats.uniqueChampions}
                        </div>
                        <div className="text-[#A09B8C] uppercase tracking-widest" style={{ fontSize: '6px', marginTop: '1px' }}>Champions</div>
                      </div>

                      {/* Player Level - Gold border like Final Recap */}
                      <div className="bg-black/70 backdrop-blur-sm border border-[#C8AA6E]/30 text-center flex flex-col justify-center" style={{ padding: '3px' }}>
                        <div className="text-[#C8AA6E] tabular-nums" style={{ fontFamily: 'Georgia, serif', fontSize: '11px', fontWeight: 'bold' }}>
                          {stats.playerLevel || '—'}
                        </div>
                        <div className="text-[#A09B8C] uppercase tracking-widest" style={{ fontSize: '6px', marginTop: '1px' }}>Level</div>
                      </div>
                    </div>
                  </div>

                  {/* Right Side - See you next season text */}
                  <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                      <p className="text-[#C8AA6E] italic tracking-wide" style={{ fontFamily: 'Georgia, serif', fontSize: '12px', whiteSpace: 'nowrap' }}>
                        See You Next Season
                      </p>
                    </div>
                  </div>
                </div>

                {/* Logo at Bottom Right of Frame */}
                <div className="absolute" style={{ bottom: '12px', right: '12px' }}>
                  <ImageWithFallback 
                    src={logoImage}
                    alt="Rift Rewind"
                    className="opacity-80"
                    style={{ height: '20px', width: 'auto' }}
                  />
                </div>

                {/* League of Legends Logo at Top Right */}
                <div className="absolute" style={{ top: '12px', right: '12px' }}>
                  <ImageWithFallback 
                    src={lolLogo}
                    alt="League of Legends"
                    className="opacity-80"
                    style={{ height: '24px', width: 'auto' }}
                  />
                </div>
              </motion.div>

              {/* Download Button */}
              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                onClick={handleDownload}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#C8AA6E] to-[#FFD700] text-[#010A13] hover:from-[#FFD700] hover:to-[#C8AA6E] transition-all shadow-lg"
              >
                <Download className="w-5 h-5" />
                <span className="uppercase tracking-wider" style={{ fontFamily: 'Georgia, serif' }}>Download Card</span>
              </motion.button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
