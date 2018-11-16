from app.api import bp
from app.models import Post
from flask import jsonify, request
from app.api.auth import token_auth

@bp.route('/post/<int:id>', methods=['GET'])
@token_auth.login_required
def get_post(id):
	return jsonify(Post.query.get_or_404(id).to_dict())

@bp.route('/post/list', methods=['GET'])
@token_auth.login_required
def get_posts():
	page = request.args.get('page',type=int)
	per_page = request.args.get('per_page',type=int)
	return jsonify(Post.to_collection_dict(Post.query, page=page, per_page=per_page, endpoint='api.get_posts'))