/**
 * API Service for Rift Rewind Backend
 * Connects to Flask development server or AWS API Gateway
 */

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_ENDPOINT || 'http://localhost:8000';

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
  status: 'processing' | 'complete';
  testMode: boolean;
  matchCount: number;
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
  status: string;
  analytics: any;
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
    return this.request<{ regions: Region[] }>('/api/regions');
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
    maxAttempts: number = 60,
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

        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, intervalMs));
      } catch (error) {
        console.error('Error polling session:', error);
        // Continue polling even on errors
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
