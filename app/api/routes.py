from flask import Blueprint, request, jsonify, current_app
from app.services.search_service import search_documents
from app.models import User
import time, logging
from app.services.document_service import collection
from app.services.cache_service import get_cached_results

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    current_app.logger.info('Health check endpoint accessed')
    return jsonify({"status": "healthy"}), 200

@api_bp.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        user_id = data.get('user_id')
        text = data.get('text')
        top_k = data.get('top_k', 5)
        threshold = data.get('threshold', 0.5)

        if not user_id or not text:
            return jsonify({"error": "Missing user_id or text"}), 400

        # Update user request count
        user = User.update_request_count(user_id)
        if user['request_count'] > 5:
            return jsonify({"error": "Rate limit exceeded"}), 429

        # Check if results are cached
        cached = get_cached_results(text, top_k, threshold) is not None

        results = search_documents(text, top_k, threshold)
        
        logging.info(f"Search results for query '{text}': {results}")
        
        # Include debug information in the response
        debug_info = {
            "total_documents": len(collection.get()['ids']),
            "query": text,
            "query_length": len(text.split()),
            "top_k": top_k,
            "threshold": threshold,
            "results_count": len(results),
            "cached": cached
        }
        
        return jsonify({
            "results": results,
            "debug_info": debug_info
        })

    except Exception as e:
        logging.error(f"Error in search endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# Error handlers (same as before)
@api_bp.errorhandler(404)
def not_found_error(error):
    current_app.logger.error('404 error: %s', (request.path))
    return jsonify({"error": "Not found"}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    current_app.logger.error('Server Error: %s', str(error))
    return jsonify({"error": "Internal server error"}), 500