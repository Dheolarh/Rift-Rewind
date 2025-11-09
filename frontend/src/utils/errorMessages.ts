export const getUserFriendlyError = (errorMessage: string): string => {
  const lowerError = errorMessage.toLowerCase();
  
  if (lowerError.includes('not found') || lowerError.includes('404')) {
    return "Account not found. Please check your summoner name and region.";
  }
  if (lowerError.includes('unauthorized') || lowerError.includes('401')) {
    return "It's not you, it's us. (Dev: API key error).";
  }
  if (lowerError.includes('network') || lowerError.includes('fetch')) {
    return "Network error. Please check your connection and try again.";
  }
  if (lowerError.includes('timeout')) {
    return "Request timed out. The server might be busy, please try again.";
  }
  if (lowerError.includes('rate limit')) {
    return "Too many requests. Please wait a moment and try again.";
  }
  if (lowerError.includes('api key') || lowerError.includes('forbidden')) {
    return "Service configuration error. Please contact support.";
  }
  if (lowerError.includes('no ranked matches') || lowerError.includes('no matches') || lowerError.includes('0 matches')) {
    return "We found you, but couldn't find any ranked matches in 2025. Try playing some ranked games first!";
  }
  
  return "Something went wrong. Please try again later.";
};
