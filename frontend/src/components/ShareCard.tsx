import { motion, AnimatePresence } from "motion/react";
import { X, Trophy, Target, Zap, Award, Download, Swords, Users, Eye, Crown } from "lucide-react";
import { ImageWithFallback } from "./source/ImageWithFallback";
import { useRef } from "react";

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
  };
}

export function ShareCard({ isOpen, onClose, summonerName, playerTitle, year, stats }: ShareCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleDownload = async () => {
    if (!cardRef.current) return;

    try {
      const html2canvas = (await import('html2canvas')).default;
      
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: '#010A13',
        scale: 2,
        logging: false,
      });

      canvas.toBlob((blob) => {
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = `${summonerName}-RiftRewind-${year}.png`;
        link.href = url;
        link.click();
        URL.revokeObjectURL(url);
      });
    } catch (error) {
      console.error('Failed to generate image:', error);
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
            className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
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
              {/* Playing Card */}
              <motion.div
                initial={{ scale: 0.5, rotateZ: -10, opacity: 0 }}
                animate={{ scale: 1, rotateZ: -3, opacity: 1 }}
                exit={{ scale: 0.5, rotateZ: -10, opacity: 0 }}
                transition={{ type: "spring", damping: 20 }}
                ref={cardRef}
                className="relative w-[400px] h-[600px]"
                style={{ transformStyle: "preserve-3d" }}
              >
                <div className="relative w-full h-full bg-gradient-to-br from-[#0A1428] via-[#010A13] to-[#0A1428] rounded-lg border-4 border-[#C8AA6E] overflow-hidden">
                  {/* Background Champion Image */}
                  <div className="absolute inset-0 opacity-15">
                    <ImageWithFallback 
                      src="https://images.unsplash.com/photo-1759207291235-75bcc145b20d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkYXJrJTIwZmFudGFzeSUyMG1hZ2ljfGVufDF8fHx8MTc2MDAyMjM5MXww&ixlib=rb-4.1.0&q=80&w=1080"
                      alt="Champion"
                      className="w-full h-full object-cover"
                    />
                  </div>

                  {/* Decorative corners */}
                  <div className="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 border-[#C8AA6E]/60" />
                  <div className="absolute top-0 right-0 w-16 h-16 border-t-2 border-r-2 border-[#C8AA6E]/60" />
                  <div className="absolute bottom-0 left-0 w-16 h-16 border-b-2 border-l-2 border-[#C8AA6E]/60" />
                  <div className="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 border-[#C8AA6E]/60" />

                  {/* Content */}
                  <div className="relative p-8 h-full flex flex-col">
                    {/* Header */}
                    <div className="text-center mb-6">
                      <div className="w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                        {/* Placeholder for future crown image */}
                        <div className="text-4xl leading-none">
                          👑
                        </div>
                      </div>
                      <h2 className="text-2xl text-white mb-1" style={{ fontFamily: 'Georgia, serif' }}>
                        {summonerName}
                      </h2>
                      <div className="text-lg bg-gradient-to-r from-[#FFD700] via-[#C8AA6E] to-[#0AC8B9] bg-clip-text text-transparent mb-1" style={{ fontFamily: 'Georgia, serif' }}>
                        {playerTitle}
                      </div>
                      <div className="text-xs text-[#A09B8C]">{year} Rift Rewind</div>
                    </div>

                    {/* Stats Grid */}
                    <div className="flex-1 flex flex-col gap-2">
                      {/* Games & Hours */}
                      <div className="grid grid-cols-2 gap-2">
                        <div className="bg-[#0A1428]/80 rounded-sm border border-[#C8AA6E]/30 p-3 text-center">
                          <div className="w-6 h-6 mx-auto mb-1 flex items-center justify-center">
                            <Trophy className="w-5 h-5 text-[#C8AA6E]" />
                          </div>
                          <div className="text-xl text-[#C8AA6E] tabular-nums">{stats.gamesPlayed}</div>
                          <div className="text-xs text-[#A09B8C]">Games</div>
                        </div>

                        <div className="bg-[#0A1428]/80 rounded-sm border border-[#0AC8B9]/30 p-3 text-center">
                          <div className="w-6 h-6 mx-auto mb-1 flex items-center justify-center">
                            <Target className="w-5 h-5 text-[#0AC8B9]" />
                          </div>
                          <div className="text-xl text-[#0AC8B9] tabular-nums">{stats.hoursPlayed}</div>
                          <div className="text-xs text-[#A09B8C]">Hours</div>
                        </div>
                      </div>

                      {/* Peak Rank */}
                      <div className="bg-[#0A1428]/80 rounded-sm border border-[#FFD700]/30 p-3 text-center">
                        <div className="w-6 h-6 mx-auto mb-1 flex items-center justify-center">
                          <Award className="w-5 h-5 text-[#FFD700]" />
                        </div>
                        <div className="text-lg text-[#FFD700]">{stats.peakRank}</div>
                        <div className="text-xs text-[#A09B8C]">Peak Rank</div>
                      </div>

                      {/* Main Champion */}
                      <div className="bg-[#0A1428]/80 rounded-sm border border-[#C8AA6E]/30 p-3 text-center">
                        <div className="w-6 h-6 mx-auto mb-1 flex items-center justify-center">
                          <Crown className="w-5 h-5 text-[#C8AA6E]" />
                        </div>
                        <div className="text-lg text-white">{stats.favoriteChampion}</div>
                        <div className="text-xs text-[#A09B8C]">Main Champion</div>
                      </div>

                      {/* KDA & Win Rate */}
                      <div className="grid grid-cols-2 gap-2">
                        <div className="bg-[#0A1428]/80 rounded-sm border border-[#0AC8B9]/30 p-3 text-center">
                          <div className="w-6 h-6 mx-auto mb-1 flex items-center justify-center">
                            <Swords className="w-5 h-5 text-[#0AC8B9]" />
                          </div>
                          <div className="text-xl text-[#0AC8B9] tabular-nums">{stats.kdaRatio}</div>
                          <div className="text-xs text-[#A09B8C]">KDA</div>
                        </div>

                        <div className="bg-[#0A1428]/80 rounded-sm border border-[#FFD700]/30 p-3 text-center">
                          <div className="w-6 h-6 mx-auto mb-1 flex items-center justify-center">
                            <Zap className="w-5 h-5 text-[#FFD700]" />
                          </div>
                          <div className="text-xl text-[#FFD700] tabular-nums">{stats.winRate}%</div>
                          <div className="text-xs text-[#A09B8C]">Win Rate</div>
                        </div>
                      </div>

                      {/* Additional Stats */}
                      <div className="grid grid-cols-3 gap-2">
                        <div className="bg-[#0A1428]/80 rounded-sm border border-[#C8AA6E]/20 p-2 text-center">
                          <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                            <Users className="w-4 h-4 text-[#C8AA6E]" />
                          </div>
                          <div className="text-sm text-white tabular-nums">287</div>
                          <div className="text-xs text-[#A09B8C]">Duos</div>
                        </div>

                        <div className="bg-[#0A1428]/80 rounded-sm border border-[#0AC8B9]/20 p-2 text-center">
                          <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                            <Eye className="w-4 h-4 text-[#0AC8B9]" />
                          </div>
                          <div className="text-sm text-white tabular-nums">10K</div>
                          <div className="text-xs text-[#A09B8C]">Wards</div>
                        </div>

                        <div className="bg-[#0A1428]/80 rounded-sm border border-[#FFD700]/20 p-2 text-center">
                          <div className="w-5 h-5 mx-auto mb-1 flex items-center justify-center">
                            <div className="text-sm leading-none">
                              🏆
                            </div>
                          </div>
                          <div className="text-sm text-white tabular-nums">5</div>
                          <div className="text-xs text-[#A09B8C]">Pentas</div>
                        </div>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="text-center mt-4">
                      <div className="inline-flex items-center gap-2 text-[#C8AA6E] text-xs">
                        <div className="h-px w-8 bg-gradient-to-r from-transparent to-[#C8AA6E]" />
                        <span className="uppercase tracking-widest">League of Legends</span>
                        <div className="h-px w-8 bg-gradient-to-l from-transparent to-[#C8AA6E]" />
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Download Button */}
              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                onClick={handleDownload}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#C8AA6E] to-[#FFD700] text-[#010A13] rounded-sm hover:from-[#FFD700] hover:to-[#C8AA6E] transition-all"
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
