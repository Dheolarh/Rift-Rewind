import { motion } from "motion/react";
import { Swords, ChevronDown, Music } from "lucide-react";
import { ImageWithFallback } from "../source/ImageWithFallback";
import logoImage from "../../assets/logo.png";
import welcomeBg from "../../assets/WelcomeBg.jpg";

interface WelcomeSlideProps {
  summonerName: string;
  summonerTag: string;
  region: string;
  onSummonerNameChange: (value: string) => void;
  onSummonerTagChange: (value: string) => void;
  onRegionChange: (value: string) => void;
  onStart: () => void;
  isMusicPlaying: boolean;
  onMusicToggle: () => void;
}

const REGIONS = [
  { value: "na", label: "North America" },
  { value: "euw", label: "Europe West" },
  { value: "eune", label: "Europe Nordic & East" },
  { value: "kr", label: "Korea" },
  { value: "br", label: "Brazil" },
  { value: "lan", label: "Latin America North" },
  { value: "las", label: "Latin America South" },
  { value: "oce", label: "Oceania" },
  { value: "ru", label: "Russia" },
  { value: "tr", label: "Turkey" },
  { value: "jp", label: "Japan" },
];

export function WelcomeSlide({
  summonerName,
  summonerTag,
  region,
  onSummonerNameChange,
  onSummonerTagChange,
  onRegionChange,
  onStart,
  isMusicPlaying,
  onMusicToggle,
}: WelcomeSlideProps) {
  const canStart = summonerName.trim() && summonerTag.trim() && region;

  return (
    <div className="relative size-full flex items-center justify-center overflow-hidden">
      {/* Music Toggle Button */}
      <motion.button
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5 }}
        onClick={onMusicToggle}
        className="fixed top-4 right-4 z-50 w-12 h-12 flex items-center justify-center bg-[#0A1428]/80 backdrop-blur-sm border-2 border-[#C8AA6E]/40 rounded-full hover:border-[#C8AA6E] transition-all group"
      >
        <div className="w-6 h-6 flex items-center justify-center">
          {/* Placeholder for future music icon image */}
          <Music className={`w-6 h-6 transition-all ${isMusicPlaying ? 'text-[#C8AA6E]' : 'text-[#A09B8C]'}`} />
        </div>
        {isMusicPlaying && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-[#C8AA6E]"
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </motion.button>
      
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#010A13] via-[#0A1428] to-[#010A13]" />
      
      {/* Background Image */}
      <ImageWithFallback 
        src={welcomeBg}
        alt="Background"
        className="absolute inset-0 size-full object-cover opacity-20"
      />

      {/* Glowing orbs */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-[#C8AA6E] rounded-full blur-[120px] opacity-20 animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-[#0AC8B9] rounded-full blur-[120px] opacity-20 animate-pulse" style={{ animationDelay: '1s' }} />

      {/* Content */}
      <div className="relative z-10 w-full max-w-md px-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-6"
        >
          {/* Logo */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mb-4"
          >
            <ImageWithFallback 
              src={logoImage}
              alt="League of Legends Rift Rewind"
              className="w-full max-w-[280px] mx-auto"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="flex items-center justify-center gap-2 mb-3"
          >
            <div className="h-px w-12 bg-gradient-to-r from-transparent to-[#C8AA6E]" />
            <Swords className="w-5 h-5 text-[#C8AA6E]" />
            <div className="h-px w-12 bg-gradient-to-l from-transparent to-[#C8AA6E]" />
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-sm text-[#A09B8C] italic"
          >
            Relive your greatest battles
          </motion.p>
        </motion.div>

        {/* Input Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
          className="space-y-3"
        >
          {/* Summoner Name & Tag */}
          <div className="relative">
            <div className="absolute inset-0 bg-[#0A1428]/60 rounded-sm border border-[#C8AA6E]/30" />
            <div className="relative p-1">
              <label className="block text-[#C8AA6E] uppercase tracking-widest text-xs mb-2 px-3 pt-2">
                Summoner Identity
              </label>
              <div className="flex gap-2 px-3 pb-3">
                <div className="flex-1">
                  <input
                    type="text"
                    value={summonerName}
                    onChange={(e) => onSummonerNameChange(e.target.value)}
                    placeholder="Summoner Name"
                    className="w-full bg-[#010A13]/80 border-2 border-[#C8AA6E]/40 rounded-sm px-3 py-2 text-white placeholder:text-[#A09B8C] focus:border-[#C8AA6E] focus:outline-none transition-all text-sm"
                  />
                </div>
                <div className="w-20">
                  <div className="relative">
                    <span className="absolute left-2 top-1/2 -translate-y-1/2 text-[#C8AA6E] text-sm">#</span>
                    <input
                      type="text"
                      value={summonerTag}
                      onChange={(e) => onSummonerTagChange(e.target.value)}
                      placeholder="TAG"
                      maxLength={5}
                      className="w-full bg-[#010A13]/80 border-2 border-[#C8AA6E]/40 rounded-sm pl-6 pr-2 py-2 text-white placeholder:text-[#A09B8C] focus:border-[#C8AA6E] focus:outline-none transition-all text-sm uppercase"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Region */}
          <div className="relative">
            <div className="absolute inset-0 bg-[#0A1428]/60 rounded-sm border border-[#0AC8B9]/30" />
            <div className="relative p-1">
              <label className="block text-[#0AC8B9] uppercase tracking-widest text-xs mb-2 px-3 pt-2">
                Region
              </label>
              <div className="px-3 pb-3">
                <div className="relative">
                  <select
                    value={region}
                    onChange={(e) => onRegionChange(e.target.value)}
                    className="w-full bg-[#010A13]/80 border-2 border-[#0AC8B9]/40 rounded-sm px-3 py-2 text-white appearance-none focus:border-[#0AC8B9] focus:outline-none transition-all cursor-pointer text-sm"
                  >
                    <option value="" disabled>Select your region...</option>
                    {REGIONS.map(({ value, label }) => (
                      <option key={value} value={value} className="bg-[#0A1428]">
                        {label}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#0AC8B9] pointer-events-none" />
                </div>
              </div>
            </div>
          </div>

          {/* Start Button */}
          <motion.button
            onClick={onStart}
            disabled={!canStart}
            whileHover={canStart ? { scale: 1.02 } : {}}
            whileTap={canStart ? { scale: 0.98 } : {}}
            className={`relative w-full group ${!canStart ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className={`absolute inset-0 bg-gradient-to-r from-[#C8AA6E] via-[#0AC8B9] to-[#C8AA6E] rounded-sm transition-all ${canStart ? 'group-hover:shadow-[0_0_30px_rgba(200,170,110,0.5)]' : ''}`} />
            <div className="relative bg-gradient-to-r from-[#C8AA6E] to-[#0AC8B9] text-[#010A13] px-6 py-3 rounded-sm uppercase tracking-widest text-sm transition-all">
              Begin Your Journey
            </div>
          </motion.button>
        </motion.div>

        {/* Footer hint */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.3 }}
          className="text-center mt-4"
        >
          <p className="text-[#A09B8C]/60 text-xs">
            "The past is a window to the future, Summoner"
          </p>
        </motion.div>
      </div>
    </div>
  );
}
