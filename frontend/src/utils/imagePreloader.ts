/**
 * Image Preloader Utility
 * Preloads all images that will be used in slides to ensure instant display
 */

import { getChampionSplashUrl, getChampionIconUrl, getLatestVersion } from './championImages';
import rankingBg from '../assets/ranking.webp';

/**
 * Preload a single image
 */
function preloadImage(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve();
    img.onerror = () => {
      resolve(); // Don't reject, just log warning
    };
    img.src = src;
  });
}

/**
 * Extract all image URLs from session data
 */
export async function extractImageUrls(sessionData: any): Promise<string[]> {
  const urls: Set<string> = new Set();
  
  if (!sessionData) return [];

  const version = await getLatestVersion();
  
  // Profile icons
  if (sessionData.slide14_percentile?.playerProfileIconUrl) {
    urls.add(sessionData.slide14_percentile.playerProfileIconUrl);
  }
  
  if (sessionData.slide9_duoPartner?.playerProfileIconUrl) {
    urls.add(sessionData.slide9_duoPartner.playerProfileIconUrl);
  }
  
  if (sessionData.slide14_percentile?.leaderboard) {
    sessionData.slide14_percentile.leaderboard.forEach((entry: any) => {
      if (entry.profileIconUrl) {
        urls.add(entry.profileIconUrl);
      }
    });
  }

  // Champion splash arts and icons from slide3_favoriteChampions
  if (sessionData.slide3_favoriteChampions?.champions) {
    for (const champ of sessionData.slide3_favoriteChampions.champions) {
      if (champ.championName) {
        // Add splash art
        urls.add(getChampionSplashUrl(champ.championName, 0));
        // Add icon
        const iconUrl = await getChampionIconUrl(champ.championName);
        urls.add(iconUrl);
      }
    }
  }

  // Best match champion
  if (sessionData.slide4_bestMatch?.champion) {
    urls.add(getChampionSplashUrl(sessionData.slide4_bestMatch.champion, 0));
    const iconUrl = await getChampionIconUrl(sessionData.slide4_bestMatch.champion);
    urls.add(iconUrl);
  }

  // KDA champion
  if (sessionData.slide5_kda?.topChampion) {
    urls.add(getChampionSplashUrl(sessionData.slide5_kda.topChampion, 0));
    const iconUrl = await getChampionIconUrl(sessionData.slide5_kda.topChampion);
    urls.add(iconUrl);
  }

  // Vision champion
  if (sessionData.slide7_vision?.topChampion) {
    urls.add(getChampionSplashUrl(sessionData.slide7_vision.topChampion, 0));
    const iconUrl = await getChampionIconUrl(sessionData.slide7_vision.topChampion);
    urls.add(iconUrl);
  }

  // Champion pool
  if (sessionData.slide8_championPool?.uniqueChampions) {
    for (const champName of sessionData.slide8_championPool.uniqueChampions.slice(0, 10)) {
      const iconUrl = await getChampionIconUrl(champName);
      urls.add(iconUrl);
    }
  }

  // Duo partner champion
  if (sessionData.slide9_duoPartner?.championName) {
    urls.add(getChampionSplashUrl(sessionData.slide9_duoPartner.championName, 0));
    const iconUrl = await getChampionIconUrl(sessionData.slide9_duoPartner.championName);
    urls.add(iconUrl);
  }

  // Duo partner's partner champion
  if (sessionData.slide9_duoPartner?.partnerChampion) {
    urls.add(getChampionSplashUrl(sessionData.slide9_duoPartner.partnerChampion, 0));
    const iconUrl = await getChampionIconUrl(sessionData.slide9_duoPartner.partnerChampion);
    urls.add(iconUrl);
  }

  // Achievements champion
  if (sessionData.slide13_achievements?.bestChampion) {
    urls.add(getChampionSplashUrl(sessionData.slide13_achievements.bestChampion, 0));
    const iconUrl = await getChampionIconUrl(sessionData.slide13_achievements.bestChampion);
    urls.add(iconUrl);
  }

  // Final recap champion
  if (sessionData.slide15_finalRecap?.topChampion) {
    urls.add(getChampionSplashUrl(sessionData.slide15_finalRecap.topChampion, 0));
    const iconUrl = await getChampionIconUrl(sessionData.slide15_finalRecap.topChampion);
    urls.add(iconUrl);
  }

  // Rank badge images (local assets - these are already bundled)
  // No need to preload, they're imported as modules

  // Background images from slides
  const backgroundImages = [
    rankingBg, // Social comparison background (bundled asset)
    // Add other static background images if any
  ];
  
  backgroundImages.forEach(bg => urls.add(bg));

  return Array.from(urls).filter(url => url && url.trim() !== '');
}

/**
 * Preload all images from session data
 */
export async function preloadAllImages(sessionData: any, onProgress?: (loaded: number, total: number) => void): Promise<void> {
  try {
    const imageUrls = await extractImageUrls(sessionData);
    
    if (imageUrls.length === 0) {
      return;
    }

    let loaded = 0;
    const total = imageUrls.length;

    // Preload images in batches to avoid overwhelming the browser
    const batchSize = 10;
    for (let i = 0; i < imageUrls.length; i += batchSize) {
      const batch = imageUrls.slice(i, i + batchSize);
      await Promise.all(batch.map(async (url) => {
        await preloadImage(url);
        loaded++;
        if (onProgress) {
          onProgress(loaded, total);
        }
      }));
    }

    } catch (error) {
    console.error('Error preloading images:', error);
    // Don't throw - allow the app to continue even if preloading fails
  }
}
