/**
 * API Service for Rift Rewind Backend
 * Connects to Flask development server or AWS API Gateway
 */

// API Configuration
// Prefer VITE_API_BASE_URL (explicit), fall back to VITE_API_ENDPOINT (older name), then localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_ENDPOINT || 'http://localhost:8000';

// Types
export interface Region {
  label: string;
  value: string;
  flag: string;
  regional: string;
}

export interface StartRewindRequest {
  gameName: string;
  tagLine: string;
  region: string;
}

export interface StartRewindResponse {
  sessionId: string;
  status: 'found' | 'complete';
  testMode: boolean;
  matchCount?: number;
  player: {
    gameName: string;
    tagLine: string;
    region: string;
    summonerLevel: number;
    rank: string;
  };
}

export interface SessionData {
  sessionId: string;
  status: 'searching' | 'found' | 'analyzing' | 'generating' | 'complete' | 'error';
  message?: string;
  analytics?: any;
  player?: {
    gameName: string;
    tagLine: string;
    region: string;
    summonerLevel: number;
    profileIconId: number;
    rank: string;
  };
}

export interface SlideData {
  sessionId: string;
  slideNumber: number;
  data: any;
  humor?: string;
}

export interface HealthCheck {
  status: string;
  testMode: boolean;
  maxMatches: number;
}

// Fallback regions in case API is unavailable
export const FALLBACK_REGIONS: Region[] = [
  { label: "North America (NA)", value: "na1", flag: "", regional: "americas" },
  { label: "Europe West (EUW)", value: "euw1", flag: "", regional: "europe" },
  { label: "Europe Nordic & East (EUNE)", value: "eun1", flag: "", regional: "europe" },
  { label: "Korea (KR)", value: "kr", flag: "", regional: "asia" },
  { label: "Brazil (BR)", value: "br1", flag: "", regional: "americas" },
  { label: "Japan (JP)", value: "jp1", flag: "", regional: "asia" },
  { label: "Latin America North (LAN)", value: "la1", flag: "", regional: "americas" },
  { label: "Latin America South (LAS)", value: "la2", flag: "", regional: "americas" },
  { label: "Oceania (OCE)", value: "oc1", flag: "", regional: "americas" },
  { label: "Turkey (TR)", value: "tr1", flag: "", regional: "europe" },
  { label: "Russia (RU)", value: "ru", flag: "", regional: "europe" },
  { label: "Philippines (PH)", value: "ph2", flag: "", regional: "sea" },
  { label: "Singapore (SG)", value: "sg2", flag: "", regional: "sea" },
  { label: "Thailand (TH)", value: "th2", flag: "", regional: "sea" },
  { label: "Taiwan (TW)", value: "tw2", flag: "", regional: "asia" },
  { label: "Vietnam (VN)", value: "vn2", flag: "", regional: "sea" },
];

// API Error class
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// API Service
class RiftRewindAPIService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Make HTTP request with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new APIError(
          data.error || 'An error occurred',
          response.status,
          data
        );
      }

      return data as T;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Network or parsing error
      throw new APIError(
        error instanceof Error ? error.message : 'Network error occurred'
      );
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>('/api/health');
  }

  /**
   * Get available regions
   */
  async getRegions(): Promise<{ regions: Region[] }> {
    try {
      return await this.request<{ regions: Region[] }>('/api/regions');
    } catch (error) {
      console.warn('Failed to fetch regions from API, using fallback:', error);
      return { regions: FALLBACK_REGIONS };
    }
  }

  /**
   * Start a new Rift Rewind session
   */
  async startRewind(data: StartRewindRequest): Promise<StartRewindResponse> {
    return this.request<StartRewindResponse>('/api/rewind', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Get session data and analytics
   */
  async getSession(sessionId: string): Promise<SessionData> {
    return this.request<SessionData>(`/api/rewind/${sessionId}`);
  }

  /**
   * Get specific slide data
   */
  async getSlide(sessionId: string, slideNumber: number): Promise<SlideData> {
    return this.request<SlideData>(
      `/api/rewind/${sessionId}/slide/${slideNumber}`
    );
  }

  /**
   * Poll for session completion
   * Returns when analytics are ready
   */
  async waitForSessionComplete(
    sessionId: string,
    onProgress?: (status: string) => void,
    maxAttempts: number = 1800, 
    intervalMs: number = 2000
  ): Promise<SessionData> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const session = await this.getSession(sessionId);
        
        if (onProgress) {
          onProgress(session.status);
        }

        if (session.status === 'complete') {
          return session;
        }

        // Check for error status
        if (session.status === 'error') {
          throw new APIError(
            session.message || 'An error occurred during analysis',
            500
          );
        }

        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, intervalMs));
      } catch (error) {
        console.error('Error polling session:', error);
        // Re-throw APIError so it can be caught by the caller
        if (error instanceof APIError) {
          throw error;
        }
        // Continue polling on other errors
      }
    }

    throw new APIError('Session processing timeout');
  }
}

// Export singleton instance
export const apiService = new RiftRewindAPIService();

// Export helper functions
export const api = {
  healthCheck: () => apiService.healthCheck(),
  getRegions: () => apiService.getRegions(),
  startRewind: (data: StartRewindRequest) => apiService.startRewind(data),
  getSession: (sessionId: string) => apiService.getSession(sessionId),
  getSlide: (sessionId: string, slideNumber: number) => 
    apiService.getSlide(sessionId, slideNumber),
  waitForComplete: (
    sessionId: string, 
    onProgress?: (status: string) => void
  ) => apiService.waitForSessionComplete(sessionId, onProgress),
};

export default api;
