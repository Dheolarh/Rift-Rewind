"""
Loading Screen Messages
=======================
Teaser messages for loading screen - NO SPOILERS!
Keep users engaged while data is being fetched and analyzed.
"""

import random
from typing import List


class LoadingMessages:
    """
    Generates engaging, non-spoiler messages for the loading screen.
    """
    
    # Phase 1: Account fetching (0-5 seconds)
    ACCOUNT_MESSAGES = [
        "Summoner spotted on the Rift! 👀",
        "Connecting to the Nexus...",
        "Scanning the Rift for your profile...",
        "Found you! Preparing your journey...",
        "Loading Summoner data from the Void...",
    ]
    
    # Phase 2: Match history retrieval (5-10 seconds)
    HISTORY_MESSAGES = [
        "Checking your match history... 📜",
        "Wow... you've been busy on the Rift this year 👀",
        "Gathering your epic moments...",
        "Your teammates are going to want to see this...",
        "Compiling your Rift adventures...",
        "This might take a minute... you've got some stories to tell 😏",
    ]
    
    # Phase 3: Analysis in progress (10-60 seconds)
    ANALYSIS_MESSAGES = [
        "Analyzing your biggest plays... 🎮",
        "Calculating your... interesting... decision-making 😏",
        "Our AI is judging your champion choices...",
        "Measuring your impact on the Rift...",
        "Evaluating your 5Head moments (and the others)...",
        "Processing your pentakills and... other moments...",
        "Analyzing your farming skills... or lack thereof 🌾",
        "Counting how many times you pinged '?'...",
        "Reviewing your flash-into-wall technique...",
        "Calculating your ward-to-death ratio... 👁️",
        "Measuring your main character energy...",
        "Analyzing your 200 years of experience...",
    ]
    
    # Phase 4: Final preparation (60+ seconds)
    FINAL_MESSAGES = [
        "Polishing your highlights... ✨",
        "Preparing your personal roast... I mean review 🔥",
        "Generating your custom insights...",
        "Almost there! Getting the good stuff ready...",
        "Finalizing your year on the Rift...",
        "Your Rewind is almost ready... brace yourself 😅",
        "Putting the finishing touches on your story...",
        "Loading the receipts... 📸",
    ]
    
    # Progress indicators (no specific stats)
    PROGRESS_MESSAGES = [
        "Fetching account data...",
        "Loading match history...",
        "Analyzing performance patterns...",
        "Generating insights...",
        "Preparing your Rewind...",
        "Crunching the numbers...",
        "Almost ready...",
    ]
    
    @staticmethod
    def get_random_message(phase: str = "analysis") -> str:
        """
        Get a random message for the specified phase.
        
        Args:
            phase: One of 'account', 'history', 'analysis', 'final', 'progress'
            
        Returns:
            Random message string
        """
        messages = {
            'account': LoadingMessages.ACCOUNT_MESSAGES,
            'history': LoadingMessages.HISTORY_MESSAGES,
            'analysis': LoadingMessages.ANALYSIS_MESSAGES,
            'final': LoadingMessages.FINAL_MESSAGES,
            'progress': LoadingMessages.PROGRESS_MESSAGES,
        }
        
        return random.choice(messages.get(phase, LoadingMessages.ANALYSIS_MESSAGES))
    
    @staticmethod
    def get_message_sequence() -> List[str]:
        """
        Get a sequence of messages for the entire loading process.
        
        Returns:
            List of messages in order
        """
        return [
            random.choice(LoadingMessages.ACCOUNT_MESSAGES),
            random.choice(LoadingMessages.HISTORY_MESSAGES),
            random.choice(LoadingMessages.ANALYSIS_MESSAGES),
            random.choice(LoadingMessages.ANALYSIS_MESSAGES),
            random.choice(LoadingMessages.FINAL_MESSAGES),
        ]
    
    @staticmethod
    def get_progress_update(completed: int, total: int, phase: str = "analysis"):
        """
        Generate a progress update with appropriate messaging.
        
        Args:
            completed: Number of items completed
            total: Total number of items
            phase: Current phase
            
        Returns:
            Dictionary with progress info and message
        """
        percentage = int((completed / total * 100)) if total > 0 else 0
        
        return {
            'percentage': percentage,
            'completed': completed,
            'total': total,
            'message': LoadingMessages.get_random_message(phase),
            'phase': phase
        }


# Export for easy import
def get_loading_message(phase: str = "analysis") -> str:
    """Convenience function to get a loading message."""
    return LoadingMessages.get_random_message(phase)


if __name__ == "__main__":
    # Test loading messages
    print("=== LOADING MESSAGE PREVIEW ===\n")
    
    phases = ['account', 'history', 'analysis', 'final']
    
    for phase in phases:
        print(f"{phase.upper()} PHASE:")
        for _ in range(3):
            print(f"  - {LoadingMessages.get_random_message(phase)}")
        print()
    
    print("\nSAMPLE SEQUENCE:")
    for i, msg in enumerate(LoadingMessages.get_message_sequence(), 1):
        print(f"{i}. {msg}")
