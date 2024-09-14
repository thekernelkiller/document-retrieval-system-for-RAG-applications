from flask import Blueprint, request, jsonify, current_app
from app.services.search_service import search_documents
from app.models import User
import time

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
        
        if not user_id:
            current_app.logger.warning('Search request received without user_id')
            return jsonify({"error": "user_id is required"}), 400

        query = data.get('text', '')
        top_k = data.get('top_k', 5)
        threshold = data.get('threshold', 0.5)
        
        current_app.logger.info(f'Search request received for user {user_id}')

        # Check and update user request count
        user = User.update_request_count(user_id)
        
        if user['request_count'] > 5:
            current_app.logger.warning(f'Rate limit exceeded for user {user_id}')
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        start_time = time.time()
        results = search_documents(query, top_k, threshold)
        end_time = time.time()
        
        inference_time = end_time - start_time
        
        response = {
            "results": results,
            "inference_time": inference_time
        }
        
        current_app.logger.info(f'Search completed for user {user_id}. Inference time: {inference_time:.4f} seconds')
        return jsonify(response)

    except Exception as e:
        current_app.logger.error(f'An error occurred during search: {str(e)}', exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500

# Error handlers (same as before)
@api_bp.errorhandler(404)
def not_found_error(error):
    current_app.logger.error('404 error: %s', (request.path))
    return jsonify({"error": "Not found"}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    current_app.logger.error('Server Error: %s', str(error))
    return jsonify({"error": "Internal server error"}), 500