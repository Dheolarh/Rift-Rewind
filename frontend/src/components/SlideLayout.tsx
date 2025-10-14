import { ReactNode } from "react";
import { motion } from "motion/react";

interface SlideLayoutProps {
  icon?: ReactNode;
  title: string | ReactNode;
  subtitle?: string;
  children: ReactNode;
  heroBackground?: ReactNode;
}

export function SlideLayout({
  icon,
  title,
  subtitle,
  children,
  heroBackground,
}: SlideLayoutProps) {
  return (
    <div className="relative size-full flex flex-col overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#010A13] via-[#0A1428] to-[#1E2328]" />
      
      {heroBackground}

      {/* Fixed Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-20 flex-shrink-0 px-4 sm:px-6 lg:px-8 pt-8 sm:pt-6 md:pt-8 pb-8 sm:pb-6 md:pb-8"
      >
        <div className="text-center w-full max-w-[min(90vw,800px)] mx-auto">
          {icon && (
            <div className="mb-3 sm:mb-4 flex justify-center">
              {icon}
            </div>
          )}
          <div className="mb-2">
            {typeof title === 'string' ? (
              <h2 className="text-2xl sm:text-3xl lg:text-4xl text-white" style={{ fontFamily: 'Georgia, serif' }}>
                {title}
              </h2>
            ) : (
              title
            )}
          </div>
          {subtitle && (
            <p className="text-sm sm:text-base lg:text-lg text-[#A09B8C]">
              {subtitle}
            </p>
          )}
        </div>
      </motion.div>

      {/* Scrollable Body Section */}
      <div 
        className="relative z-10 flex-1 overflow-y-auto overflow-x-hidden px-4 sm:px-6 lg:px-8 pb-8 scrollbar-hide" 
        style={{
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
        }}
      >
        <div className="w-full max-w-[min(90vw,1000px)] lg:max-w-[min(60vw,1200px)] mx-auto">
          {children}
        </div>
      </div>
    </div>
  );
}
