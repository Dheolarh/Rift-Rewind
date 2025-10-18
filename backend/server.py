"""
Flask Development Server for Frontend Integration
==================================================
Run this server to test frontend locally before deploying to AWS
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Import API wrapper
from api import RiftRewindAPI

# Create Flask app
app = Flask(__name__)

# Enable CORS for frontend development
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
CORS(app, origins=allowed_origins)

# Initialize API
api = RiftRewindAPI()


@app.route('/api/regions', methods=['GET'])
def get_regions():
    """GET /api/regions - Get available regions"""
    response = api.get_regions()
    return jsonify(response['body']), response['statusCode']


@app.route('/api/rewind', methods=['POST', 'OPTIONS'])
def start_rewind():
    """POST /api/rewind - Start new Rift Rewind session"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json
    response = api.start_rewind(
        data.get('gameName', ''),
        data.get('tagLine', ''),
        data.get('region', '')
    )
    
    body = response.get('body')
    return jsonify(body), response['statusCode']


@app.route('/api/rewind/<session_id>', methods=['GET'])
def get_session(session_id):
    """GET /api/rewind/{sessionId} - Get session data"""
    response = api.get_session(session_id)
    
    body = response.get('body')
    return jsonify(body), response['statusCode']


@app.route('/api/rewind/<session_id>/slide/<int:slide_number>', methods=['GET'])
def get_slide(session_id, slide_number):
    """GET /api/rewind/{sessionId}/slide/{slideNumber} - Get slide data"""
    response = api.get_slide(session_id, slide_number)
    
    body = response.get('body')
    return jsonify(body), response['statusCode']


@app.route('/api/cache/check', methods=['POST'])
def check_cache():
    """POST /api/cache/check - Check if cached session exists"""
    data = request.json
    response = api.check_cache(
        data.get('gameName', ''),
        data.get('tagLine', ''),
        data.get('region', '')
    )
    
    body = response.get('body')
    return jsonify(body), response['statusCode']


@app.route('/api/cache/invalidate', methods=['POST'])
def invalidate_cache():
    """POST /api/cache/invalidate - Invalidate cached session (force refresh)"""
    data = request.json
    response = api.invalidate_cache(
        data.get('gameName', ''),
        data.get('tagLine', ''),
        data.get('region', '')
    )
    
    body = response.get('body')
    return jsonify(body), response['statusCode']


@app.route('/api/health', methods=['GET'])
def health_check():
    """GET /api/health - Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'testMode': api.test_mode,
        'maxMatches': api.max_matches_analyze,
        'cacheEnabled': True,
        'cacheExpiryDays': api.cache_manager.cache_expiry_days
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  RIFT REWIND - Development API Server                   ║
╚══════════════════════════════════════════════════════════╝

Server running at: http://localhost:{port}

API Endpoints:
  GET  /api/health                                 Health check
  GET  /api/regions                                Get regions
  POST /api/rewind                                 Start session (checks cache first)
  GET  /api/rewind/:sessionId                      Get session
  GET  /api/rewind/:sessionId/slide/:slideNumber   Get slide
  POST /api/cache/check                            Check cache status
  POST /api/cache/invalidate                       Force refresh (clear cache)

Configuration:
  Test Mode: {api.test_mode}
  Max Matches to Fetch: {api.max_matches_fetch}
  Max Matches to Analyze: {api.max_matches_analyze}
  Humor Slides: {api.humor_slides if api.test_mode else 'All (2-15)'}
  Cache Expiry: {api.cache_manager.cache_expiry_days} days

Frontend CORS: {', '.join(allowed_origins)}
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
