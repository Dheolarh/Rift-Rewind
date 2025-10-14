import { useState, useEffect } from 'react';
import {
  getChampionSplashUrl,
  getChampionIconUrl,
  getChampionLoadingUrl,
  normalizeChampionName,
} from '../utils/championImages';

/**
 * Hook to get champion splash art URL
 */
export function useChampionSplash(championName: string | null, skinNumber: number = 0) {
  const [imageUrl, setImageUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!championName) {
      setImageUrl('');
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const url = getChampionSplashUrl(championName, skinNumber);
      setImageUrl(url);
      setIsLoading(false);
    } catch (err) {
      setError(err as Error);
      setIsLoading(false);
    }
  }, [championName, skinNumber]);

  return { imageUrl, isLoading, error };
}

/**
 * Hook to get champion icon URL
 */
export function useChampionIcon(championName: string | null) {
  const [imageUrl, setImageUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!championName) {
      setImageUrl('');
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    getChampionIconUrl(championName)
      .then((url) => {
        setImageUrl(url);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err);
        setIsLoading(false);
      });
  }, [championName]);

  return { imageUrl, isLoading, error };
}

/**
 * Hook to get champion loading screen URL
 */
export function useChampionLoading(championName: string | null, skinNumber: number = 0) {
  const [imageUrl, setImageUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!championName) {
      setImageUrl('');
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const url = getChampionLoadingUrl(championName, skinNumber);
      setImageUrl(url);
      setIsLoading(false);
    } catch (err) {
      setError(err as Error);
      setIsLoading(false);
    }
  }, [championName, skinNumber]);

  return { imageUrl, isLoading, error };
}

/**
 * Hook to get multiple champion splash URLs
 */
export function useChampionSplashes(championNames: string[]) {
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);

    const urls = championNames.map((name) => getChampionSplashUrl(name));
    setImageUrls(urls);
    setIsLoading(false);
  }, [championNames]);

  return { imageUrls, isLoading };
}
