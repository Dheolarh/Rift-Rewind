"""
Session Manager for Progressive Data Loading
Handles S3 checkpoint storage, retrieval, and 72-hour TTL management

NOTE: This is used ONLY by Lambda functions (orchestrator.py, league_data.py, humor_context.py)
for progressive loading and recovery from interruptions.

For long-term user caching (7 days), see session_cache.py (SessionCacheManager)
"""

import json
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages progressive data loading sessions with S3 checkpoint storage.
    
    PURPOSE: Short-term (72h) session recovery during active analysis
    USED BY: Lambda functions for progressive match fetching
    NOT USED BY: api.py (uses SessionCacheManager instead)
    """
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'rift-rewind-sessions'
        self.ttl_hours = 72 
    
    def create_session_id(self, game_name: str, tag_line: str, region: str) -> str:
        """
        Create deterministic session ID based on player identity.
        This allows finding existing sessions for returning players.
        
        Args:
            game_name: Player's Riot ID name
            tag_line: Player's Riot ID tag
            region: Platform region
            
        Returns:
            SHA-256 hash-based session ID
        """
        import hashlib
        unique_string = f"{game_name.lower()}#{tag_line.lower()}#{region.lower()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()
    
    def save_checkpoint(
        self,
        session_id: str,
        player_info: Dict[str, Any],
        match_data: Dict[str, Any],
        analytics: Dict[str, Any],
        ai_humor: Dict[str, Any],
        status: str = 'partial'
    ) -> bool:
        """
        Save progress checkpoint to S3 with 72-hour TTL
        
        Args:
            session_id: Unique session identifier
            player_info: Player account details
            match_data: Match IDs and checkpoint info
            analytics: Calculated analytics per slide
            ai_humor: Generated AI humor per slide
            status: 'partial' or 'complete'
        
        Returns:
            True if save successful
        """
        try:
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=self.ttl_hours)
            
            checkpoint_data = {
                'sessionId': session_id,
                'status': status,
                'playerInfo': player_info,
                'matchData': match_data,
                'analytics': analytics,
                'aiHumor': ai_humor,
                'createdAt': now.isoformat(),
                'lastUpdatedAt': now.isoformat(),
                'expiresAt': expires_at.isoformat()
            }
            
            # Save to S3
            key = f"sessions/{session_id}/checkpoint.json"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(checkpoint_data, indent=2),
                ContentType='application/json',
                Metadata={
                    'status': status,
                    'lastCheckpoint': str(match_data.get('lastCheckpoint', 0)),
                    'expiresAt': expires_at.isoformat()
                }
            )
            
            logger.info(f" Checkpoint saved: {session_id} (status: {status})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {str(e)}")
            return False
    
    def load_checkpoint(self, game_name: str, tag_line: str, region: str) -> Optional[Dict[str, Any]]:
        """
        Load existing session checkpoint for returning player
        
        Args:
            game_name: Player's Riot ID name
            tag_line: Player's Riot ID tag
            region: Player's region
        
        Returns:
            Checkpoint data if exists and not expired, None otherwise
        """
        try:
            session_id = self.create_session_id(game_name, tag_line, region)
            key = f"sessions/{session_id}/checkpoint.json"
            
            # Try to load from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            checkpoint_data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Check if expired
            expires_at = datetime.fromisoformat(checkpoint_data['expiresAt'])
            if datetime.utcnow() > expires_at:
                logger.info(f"Session expired: {session_id}")
                self.delete_session(session_id)
                return None
            
            logger.info(f" Checkpoint loaded: {session_id} (status: {checkpoint_data['status']})")
            return checkpoint_data
            
        except self.s3_client.exceptions.NoSuchKey:
            logger.info(f"No existing session found for {game_name}#{tag_line}")
            return None
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {str(e)}")
            return None
    
    def get_unanalyzed_matches(self, session_id: str) -> List[str]:
        """
        Get list of match IDs that haven't been analyzed yet
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of unanalyzed match IDs
        """
        try:
            key = f"sessions/{session_id}/checkpoint.json"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            checkpoint_data = json.loads(response['Body'].read().decode('utf-8'))
            return checkpoint_data.get('matchData', {}).get('unanalyzedMatchIds', [])
            
        except Exception as e:
            logger.error(f"Failed to get unanalyzed matches: {str(e)}")
            return []
    
    def mark_complete(self, session_id: str) -> bool:
        """
        Mark session as fully analyzed and save final state
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if successful
        """
        try:
            # Load current checkpoint
            key = f"sessions/{session_id}/checkpoint.json"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            checkpoint_data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Update status
            checkpoint_data['status'] = 'complete'
            checkpoint_data['lastUpdatedAt'] = datetime.utcnow().isoformat()
            checkpoint_data['matchData']['unanalyzedMatchIds'] = []
            
            # Save updated checkpoint
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(checkpoint_data, indent=2),
                ContentType='application/json',
                Metadata={
                    'status': 'complete',
                    'lastCheckpoint': str(checkpoint_data['matchData']['lastCheckpoint'])
                }
            )
            
            logger.info(f" Session marked complete: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark session complete: {str(e)}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete expired or invalid session
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if successful
        """
        try:
            key = f"sessions/{session_id}/checkpoint.json"
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            logger.info(f" Session deleted: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")
            return False
    
    def update_analytics(
        self,
        session_id: str,
        new_analytics: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """
        Update analytics data in checkpoint
        
        Args:
            session_id: Session identifier
            new_analytics: New analytics to add/update
            merge: If True, merge with existing; if False, replace
        
        Returns:
            True if successful
        """
        try:
            key = f"sessions/{session_id}/checkpoint.json"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            checkpoint_data = json.loads(response['Body'].read().decode('utf-8'))
            
            if merge:
                # Merge new analytics with existing
                checkpoint_data['analytics'].update(new_analytics)
            else:
                # Replace analytics
                checkpoint_data['analytics'] = new_analytics
            
            checkpoint_data['lastUpdatedAt'] = datetime.utcnow().isoformat()
            
            # Save updated checkpoint
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(checkpoint_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f" Analytics updated: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update analytics: {str(e)}")
            return False
    
    def update_humor(
        self,
        session_id: str,
        slide_num: int,
        humor_text: str
    ) -> bool:
        """
        Update AI humor for a specific slide
        
        Args:
            session_id: Session identifier
            slide_num: Slide number (1-15)
            humor_text: Generated humor text
        
        Returns:
            True if successful
        """
        try:
            key = f"sessions/{session_id}/checkpoint.json"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            checkpoint_data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Update humor for specific slide
            slide_key = f"slide{slide_num}"
            checkpoint_data['aiHumor'][slide_key] = humor_text
            checkpoint_data['lastUpdatedAt'] = datetime.utcnow().isoformat()
            
            # Save updated checkpoint
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(checkpoint_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f" Humor updated: {session_id} - Slide {slide_num}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update humor: {str(e)}")
            return False
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current session status and progress
        
        Args:
            session_id: Session identifier
        
        Returns:
            Status dict with progress info
        """
        try:
            key = f"sessions/{session_id}/checkpoint.json"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            checkpoint_data = json.loads(response['Body'].read().decode('utf-8'))
            match_data = checkpoint_data.get('matchData', {})
            
            total_matches = match_data.get('totalMatches', 0)
            analyzed_count = len(match_data.get('analyzedMatchIds', []))
            unanalyzed_count = len(match_data.get('unanalyzedMatchIds', []))
            
            # Count generated humor
            humor_count = sum(1 for v in checkpoint_data.get('aiHumor', {}).values() if v is not None)
            
            return {
                'sessionId': session_id,
                'status': checkpoint_data.get('status'),
                'totalMatches': total_matches,
                'analyzedMatches': analyzed_count,
                'unanalyzedMatches': unanalyzed_count,
                'progress': (analyzed_count / total_matches * 100) if total_matches > 0 else 0,
                'lastCheckpoint': match_data.get('lastCheckpoint', 0),
                'generatedHumor': humor_count,
                'createdAt': checkpoint_data.get('createdAt'),
                'lastUpdatedAt': checkpoint_data.get('lastUpdatedAt'),
                'expiresAt': checkpoint_data.get('expiresAt')
            }
            
        except Exception as e:
            logger.error(f"Failed to get session status: {str(e)}")
            return None
