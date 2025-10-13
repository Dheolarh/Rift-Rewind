"""
Intelligent Match Sampling System
=================================
Monthly-based adaptive sampling for efficient match analysis

Strategy:
- ≤100 matches: Analyze 100%
- 101-300 matches: Analyze 50%
- 301-500 matches: Analyze 35%
- 501-800 matches: Analyze 25%
- 800+ matches: Analyze 20%

Samples are distributed proportionally across months to avoid seasonal bias.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict
import math


class IntelligentSampler:
    """
    Intelligently samples matches based on total count and monthly distribution.
    """
    
    # Sampling thresholds
    SAMPLING_TIERS = [
        (100, 1.00),   # ≤100 matches: 100%
        (300, 0.50),   # 101-300: 50%
        (500, 0.35),   # 301-500: 35%
        (800, 0.25),   # 501-800: 25%
        (float('inf'), 0.20)  # 800+: 20%
    ]
    
    def __init__(self):
        self.total_matches = 0
        self.sample_percentage = 0.0
        self.sample_count = 0
        self.monthly_distribution = {}
    
    def calculate_sample_percentage(self, total_matches: int) -> float:
        """
        Calculate what percentage of matches to sample based on total count.
        
        Args:
            total_matches: Total number of matches played
            
        Returns:
            Percentage to sample (0.0 to 1.0)
        """
        for threshold, percentage in self.SAMPLING_TIERS:
            if total_matches <= threshold:
                return percentage
        
        return 0.20  # Default to 20% for very high counts
    
    def extract_month_from_match_id(self, match_id: str) -> str:
        """
        Extract month/year from match ID timestamp.
        Match IDs contain Unix timestamps in milliseconds.
        
        Args:
            match_id: Match ID (e.g., "KR_1234567890123")
            
        Returns:
            Month key in format "YYYY-MM"
        """
        try:
            # Match ID format: REGION_TIMESTAMP
            # Extract timestamp (last 13 digits for milliseconds)
            timestamp_str = match_id.split('_')[-1]
            timestamp_ms = int(timestamp_str)
            timestamp_s = timestamp_ms / 1000
            
            date = datetime.fromtimestamp(timestamp_s)
            return date.strftime("%Y-%m")
        except:
            # Fallback to current month if parsing fails
            return datetime.now().strftime("%Y-%m")
    
    def group_matches_by_month(self, match_ids: List[str]) -> Dict[str, List[str]]:
        """
        Group match IDs by month.
        
        Args:
            match_ids: List of match IDs
            
        Returns:
            Dictionary mapping month keys to match ID lists
        """
        monthly_matches = defaultdict(list)
        
        for match_id in match_ids:
            month_key = self.extract_month_from_match_id(match_id)
            monthly_matches[month_key].append(match_id)
        
        return dict(monthly_matches)
    
    def select_samples_from_month(
        self, 
        match_ids: List[str], 
        sample_count: int
    ) -> List[str]:
        """
        Select evenly distributed samples from a month's matches.
        
        Args:
            match_ids: All match IDs from a month
            sample_count: Number of samples to select
            
        Returns:
            Selected match IDs
        """
        total = len(match_ids)
        
        # If sample count >= total, return all
        if sample_count >= total:
            return match_ids
        
        # Calculate step size for even distribution
        step = total / sample_count
        
        selected = []
        for i in range(sample_count):
            index = int(i * step)
            selected.append(match_ids[index])
        
        return selected
    
    def sample_matches(self, match_ids: List[str]) -> Dict[str, Any]:
        """
        Intelligently sample matches with monthly distribution.
        
        Args:
            match_ids: All match IDs from the year
            
        Returns:
            Dictionary containing:
            - sampled_match_ids: List of selected match IDs
            - sample_percentage: Percentage sampled
            - total_matches: Total matches available
            - sample_count: Number of matches to analyze
            - monthly_breakdown: Distribution by month
            - metadata: Additional sampling info
        """
        self.total_matches = len(match_ids)
        
        # Calculate sampling percentage
        self.sample_percentage = self.calculate_sample_percentage(self.total_matches)
        self.sample_count = int(self.total_matches * self.sample_percentage)
        
        # Group matches by month
        monthly_matches = self.group_matches_by_month(match_ids)
        
        # Calculate samples per month (proportional distribution)
        monthly_samples = {}
        sampled_match_ids = []
        
        for month, month_match_ids in monthly_matches.items():
            month_total = len(month_match_ids)
            month_percentage = month_total / self.total_matches
            month_sample_count = max(1, int(self.sample_count * month_percentage))
            
            # Select samples from this month
            selected = self.select_samples_from_month(month_match_ids, month_sample_count)
            sampled_match_ids.extend(selected)
            
            monthly_samples[month] = {
                'total': month_total,
                'sampled': len(selected),
                'percentage': month_percentage * 100,
                'sample_percentage': (len(selected) / month_total * 100) if month_total > 0 else 0
            }
        
        self.monthly_distribution = monthly_samples
        
        return {
            'sampled_match_ids': sampled_match_ids,
            'sample_percentage': self.sample_percentage * 100,
            'total_matches': self.total_matches,
            'sample_count': len(sampled_match_ids),
            'monthly_breakdown': monthly_samples,
            'metadata': {
                'sampling_tier': self._get_tier_name(self.total_matches),
                'is_full_analysis': self.sample_percentage == 1.0,
                'efficiency_gain': f"{int((1 - self.sample_percentage) * 100)}% faster",
                'statistical_confidence': self._calculate_confidence(len(sampled_match_ids))
            }
        }
    
    def _get_tier_name(self, total: int) -> str:
        """Get human-readable tier name."""
        if total <= 100:
            return "Complete Analysis (≤100 matches)"
        elif total <= 300:
            return "High Sampling (101-300 matches)"
        elif total <= 500:
            return "Balanced Sampling (301-500 matches)"
        elif total <= 800:
            return "Efficient Sampling (501-800 matches)"
        else:
            return "Optimized Sampling (800+ matches)"
    
    def _calculate_confidence(self, sample_size: int) -> str:
        """Calculate statistical confidence level."""
        if sample_size >= 200:
            return "Very High (200+ matches)"
        elif sample_size >= 100:
            return "High (100-200 matches)"
        elif sample_size >= 50:
            return "Good (50-100 matches)"
        elif sample_size >= 30:
            return "Moderate (30-50 matches)"
        else:
            return "Fair (<30 matches)"
    
    def extrapolate_stat(self, sampled_value: float, extrapolate: bool = True) -> float:
        """
        Extrapolate a statistic from sampled data to full dataset.
        
        Args:
            sampled_value: Value calculated from sample
            extrapolate: Whether to extrapolate (False = return as-is)
            
        Returns:
            Extrapolated value
        """
        if not extrapolate or self.sample_percentage == 1.0:
            return sampled_value
        
        # For count-based stats, scale up proportionally
        return sampled_value / self.sample_percentage
    
    def get_sampling_report(self) -> str:
        """
        Generate human-readable sampling report.
        
        Returns:
            Formatted report string
        """
        if not self.monthly_distribution:
            return "No sampling performed yet."
        
        report = []
        report.append("="*60)
        report.append("INTELLIGENT SAMPLING REPORT")
        report.append("="*60)
        report.append(f"\nTotal Matches: {self.total_matches}")
        report.append(f"Sample Percentage: {self.sample_percentage * 100:.1f}%")
        report.append(f"Matches to Analyze: {self.sample_count}")
        report.append(f"Time Savings: ~{int((1 - self.sample_percentage) * 100)}%")
        report.append(f"\nMonthly Distribution:")
        report.append("-"*60)
        
        for month, data in sorted(self.monthly_distribution.items()):
            report.append(
                f"{month}: {data['sampled']:3d}/{data['total']:3d} matches "
                f"({data['percentage']:5.1f}% of year, "
                f"{data['sample_percentage']:5.1f}% sampled)"
            )
        
        report.append("="*60)
        
        return "\n".join(report)


# Convenience function for quick sampling
def sample_matches_intelligently(match_ids: List[str]) -> Tuple[List[str], Dict[str, Any]]:
    """
    Quick function to sample matches with intelligent distribution.
    
    Args:
        match_ids: All match IDs
        
    Returns:
        Tuple of (sampled_match_ids, sampling_metadata)
    """
    sampler = IntelligentSampler()
    result = sampler.sample_matches(match_ids)
    
    return result['sampled_match_ids'], result


if __name__ == "__main__":
    # Test with example match IDs
    import random
    
    print("Testing Intelligent Sampling System\n")
    
    # Simulate match IDs for different scenarios
    test_cases = [
        (50, "Casual Player"),
        (150, "Regular Player"),
        (400, "Active Player"),
        (700, "Hardcore Player"),
        (1500, "Streamer/Pro")
    ]
    
    for count, player_type in test_cases:
        # Generate fake match IDs with timestamps spread across a year
        base_timestamp = 1672531200000  # Jan 1, 2023
        year_ms = 365 * 24 * 60 * 60 * 1000
        
        match_ids = [
            f"KR_{base_timestamp + int(random.random() * year_ms)}"
            for _ in range(count)
        ]
        
        sampler = IntelligentSampler()
        result = sampler.sample_matches(match_ids)
        
        print(f"\n{player_type} ({count} matches):")
        print(f"  Sample: {result['sample_count']} matches ({result['sample_percentage']:.1f}%)")
        print(f"  Tier: {result['metadata']['sampling_tier']}")
        print(f"  Confidence: {result['metadata']['statistical_confidence']}")
        print(f"  Speed Gain: {result['metadata']['efficiency_gain']}")
