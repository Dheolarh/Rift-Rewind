/**
 * Champion Image Utilities
 * Fetches champion images from Riot's Data Dragon CDN (No API Key Required!)
 */

// Champion name normalization map for special cases
const CHAMPION_NAME_MAP: Record<string, string> = {
  'Wukong': 'MonkeyKing',
  'Renata Glasc': 'Renata',
  'Nunu & Willump': 'Nunu',
  "K'Sante": 'KSante',
  "Kai'Sa": 'Kaisa',
  "Kha'Zix": 'Khazix',
  "Vel'Koz": 'Velkoz',
  "Cho'Gath": 'Chogath',
  "Kog'Maw": 'KogMaw',
  "Rek'Sai": 'RekSai',
  "Bel'Veth": 'Belveth',
  'LeBlanc': 'Leblanc',
};

/**
 * Normalize champion name for API compatibility
 */
export function normalizeChampionName(name: string): string {
  return CHAMPION_NAME_MAP[name] || name.replace(/[^a-zA-Z]/g, '');
}

let cachedVersion: string | null = null;

export async function getLatestVersion(): Promise<string> {
  if (cachedVersion) return cachedVersion;
  
  try {
    const response = await fetch('https://ddragon.leagueoflegends.com/api/versions.json');
    const versions = await response.json();
    cachedVersion = versions[0]; // Latest version
    return cachedVersion || '14.23.1';
  } catch (error) {
    console.error('Failed to fetch Data Dragon version:', error);
    // Fallback to a recent version if fetch fails
    return '14.23.1';
  }
}

/**
 * Get champion splash art URL (Full size ~1920x1080)
 * Best for champion cards and backgrounds
 */
export function getChampionSplashUrl(championName: string, skinNumber: number = 0): string {
  const normalizedName = normalizeChampionName(championName);
  return `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${normalizedName}_${skinNumber}.jpg`;
}

/**
 * Get champion square icon URL (120x120)
 * Best for small displays and lists
 */
export async function getChampionIconUrl(championName: string): Promise<string> {
  const version = await getLatestVersion();
  const normalizedName = normalizeChampionName(championName);
  return `https://ddragon.leagueoflegends.com/cdn/${version}/img/champion/${normalizedName}.png`;
}

/**
 * Get champion loading screen URL (308x560)
 * Vertical portraits
 */
export function getChampionLoadingUrl(championName: string, skinNumber: number = 0): string {
  const normalizedName = normalizeChampionName(championName);
  return `https://ddragon.leagueoflegends.com/cdn/img/champion/loading/${normalizedName}_${skinNumber}.jpg`;
}

/**
 * Get all champions data
 */
interface ChampionData {
  id: string;
  key: string;
  name: string;
  title: string;
  image: {
    full: string;
    sprite: string;
    group: string;
    x: number;
    y: number;
    w: number;
    h: number;
  };
}

interface ChampionsResponse {
  data: Record<string, ChampionData>;
}

let cachedChampions: ChampionsResponse | null = null;

export async function getAllChampions(): Promise<ChampionsResponse> {
  if (cachedChampions) return cachedChampions;

  try {
    const version = await getLatestVersion();
    const response = await fetch(
      `https://ddragon.leagueoflegends.com/cdn/${version}/data/en_US/champion.json`
    );
    cachedChampions = await response.json();
    return cachedChampions!;
  } catch (error) {
    console.error('Failed to fetch champions data:', error);
    throw error;
  }
}

/**
 * Get champion by name
 */
export async function getChampionByName(championName: string): Promise<ChampionData | null> {
  try {
    const champions = await getAllChampions();
    const normalizedName = normalizeChampionName(championName);
    
    // Try to find by normalized name first
    if (champions.data[normalizedName]) {
      return champions.data[normalizedName];
    }
    
    // Try to find by original name
    if (champions.data[championName]) {
      return champions.data[championName];
    }
    
    // Search by name match
    const found = Object.values(champions.data).find(
      (champ) => champ.name.toLowerCase() === championName.toLowerCase()
    );
    
    return found || null;
  } catch (error) {
    console.error(`Failed to get champion ${championName}:`, error);
    return null;
  }
}

/**
 * Preload champion image
 */
export function preloadChampionImage(url: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve();
    img.onerror = reject;
    img.src = url;
  });
}

/**
 * Get multiple champion splash URLs
 */
export function getChampionSplashUrls(champions: string[]): string[] {
  return champions.map((name) => getChampionSplashUrl(name));
}

/**
 * Preload multiple champion images
 */
export async function preloadChampionImages(champions: string[]): Promise<void> {
  const urls = getChampionSplashUrls(champions);
  await Promise.all(urls.map((url) => preloadChampionImage(url)));
}
