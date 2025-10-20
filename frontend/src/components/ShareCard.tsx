import { motion, AnimatePresence } from "motion/react";
import { X, Download } from "lucide-react";
import { ImageWithFallback } from "./source/ImageWithFallback";
import logoImage from "../assets/logo.webp";
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
        backgroundColor: null,
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
              {/* Simplified Beautiful Card */}
              <motion.div
                initial={{ scale: 0.8, opacity: 0, y: 30 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.8, opacity: 0, y: 30 }}
                transition={{ type: "spring", damping: 25, stiffness: 200 }}
                ref={cardRef}
                className="relative w-[min(90vw,400px)] sm:w-[400px]"
                style={{
                  aspectRatio: "3/4"
                }}
              >
                {/* Card Background - Clean gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#0a1929] via-[#010A13] to-[#0a0515]">
                  {/* Subtle pattern overlay */}
                  <div className="absolute inset-0 opacity-5" style={{
                    backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(200,170,110,0.3) 1px, transparent 0)',
                    backgroundSize: '32px 32px'
                  }} />
                </div>

                {/* Top Gold Accent Bar */}
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#C8AA6E] to-transparent" />

                {/* Content Container */}
                <div className="relative w-full h-full flex flex-col p-6">
                  
                  {/* Header - Year Badge */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="px-3 py-1 bg-[#C8AA6E]/20 border border-[#C8AA6E]/40">
                      <span className="text-xs text-[#C8AA6E] uppercase tracking-widest">{year}</span>
                    </div>
                    
                    {/* Win Rate Badge */}
                    <div className="text-right">
                      <div className="text-3xl text-[#C8AA6E] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                        {stats.winRate}%
                      </div>
                      <div className="text-xs text-[#A09B8C] uppercase tracking-wider">Win Rate</div>
                    </div>
                  </div>

                  {/* Champion Image - Centered */}
                  <div className="flex-1 flex items-center justify-center my-4">
                    <div className="relative w-44 h-52">
                      {/* Glow effect */}
                      <div className="absolute inset-0 bg-gradient-radial from-[#C8AA6E]/30 to-transparent blur-3xl" />
                      
                      {/* Image with gold border */}
                      <div className="relative w-full h-full border-2 border-[#C8AA6E]/40 p-1">
                        <ImageWithFallback
                          src="https://images.unsplash.com/photo-1614294148960-9aa740632a87?w=400"
                          alt={summonerName}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Player Info */}
                  <div className="text-center mb-4">
                    <h2 className="text-2xl text-white mb-1 truncate" style={{ fontFamily: 'Georgia, serif' }}>
                      {summonerName}
                    </h2>
                    <p className="text-sm text-[#C8AA6E] italic">{playerTitle}</p>
                  </div>

                  {/* Stats Grid - Clean and Aligned */}
                  <div className="grid grid-cols-4 gap-2 mb-4">
                    {/* Games */}
                    <div className="text-center p-2 bg-[#0A1428]/40 border border-[#C8AA6E]/10">
                      <div className="text-base text-white tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                        {stats.gamesPlayed}
                      </div>
                      <div className="text-[10px] text-[#A09B8C] uppercase mt-0.5">Games</div>
                    </div>

                    {/* Hours */}
                    <div className="text-center p-2 bg-[#0A1428]/40 border border-[#0AC8B9]/10">
                      <div className="text-base text-[#0AC8B9] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                        {stats.hoursPlayed}
                      </div>
                      <div className="text-[10px] text-[#A09B8C] uppercase mt-0.5">Hours</div>
                    </div>

                    {/* KDA */}
                    <div className="text-center p-2 bg-[#0A1428]/40 border border-[#0AC8B9]/10">
                      <div className="text-base text-[#0AC8B9] tabular-nums" style={{ fontFamily: 'Georgia, serif' }}>
                        {stats.kdaRatio}
                      </div>
                      <div className="text-[10px] text-[#A09B8C] uppercase mt-0.5">KDA</div>
                    </div>

                    {/* Main */}
                    <div className="text-center p-2 bg-[#0A1428]/40 border border-[#C8AA6E]/10">
                      <div className="text-xs text-[#FFD700] truncate" style={{ fontFamily: 'Georgia, serif' }}>
                        {stats.favoriteChampion}
                      </div>
                      <div className="text-[10px] text-[#A09B8C] uppercase mt-0.5">Main</div>
                    </div>
                  </div>

                  {/* Peak Rank - Full Width */}
                  <div className="text-center p-2 bg-[#0A1428]/40 border border-[#C8AA6E]/20">
                    <div className="text-sm text-[#C8AA6E]" style={{ fontFamily: 'Georgia, serif' }}>
                      {stats.peakRank}
                    </div>
                    <div className="text-[10px] text-[#A09B8C] uppercase mt-0.5">Peak Rank</div>
                  </div>

                  {/* Logo Watermark - Bottom Left */}
                  <div className="absolute bottom-4 left-4">
                    <ImageWithFallback 
                      src={logoImage}
                      alt="Rift Rewind"
                      className="w-16 opacity-40"
                    />
                  </div>
                </div>

                {/* Bottom Gold Accent Bar */}
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#C8AA6E] to-transparent" />

                {/* Corner Accents - Minimal */}
                <div className="absolute top-0 left-0 w-12 h-12 border-t border-l border-[#C8AA6E]/40" />
                <div className="absolute top-0 right-0 w-12 h-12 border-t border-r border-[#C8AA6E]/40" />
                <div className="absolute bottom-0 left-0 w-12 h-12 border-b border-l border-[#C8AA6E]/40" />
                <div className="absolute bottom-0 right-0 w-12 h-12 border-b border-r border-[#C8AA6E]/40" />
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
