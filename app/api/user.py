from app.api import bp
from app.models import User
from flask import jsonify, request, url_for
from app.api.errors import bad_request
from app import db
from app.api.auth import token_auth

@bp.route('/user/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
	return jsonify(User.query.get_or_404(id).to_dict())

#获取用户列表
@bp.route('/user/list', methods=['GET'])
@token_auth.login_required
def get_users():
	page = request.args.get('page',type=int)
	per_page = request.args.get('per_page',type=int)
	return jsonify(User.to_collection_dict(User.query,page=page,per_page=per_page,
	                                       endpoint='api.get_users'))
#获取用户粉丝
@bp.route('/user/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page',type=int)
	per_page = min(request.args.get('per_page',10,type=int),50)
	return jsonify(User.to_collection_dict(user.followers,page=page,per_page=per_page,
	                                       endpoint='api.get_followers',id=id))
#获取关注人
@bp.route('/user/<int:id>/followed', methods=['GET'])
@token_auth.login_required
def get_followed(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page',type=int)
	per_page = min(request.args.get('per_page',10,type=int),50)
	return jsonify(User.to_collection_dict(user.followed,page=page,per_page=per_page,
	                                       endpoint='api.get_followed',id=id))

# 操作：添加新用户
@bp.route('/user', methods=['POST'])
@token_auth.login_required
def create_user():
	# 获取数据
	data = request.get_json() or {}

	# 校验
	if not 'username' in data or not 'email' in data or not 'password' in data:
		return bad_request('Please input username, email or password')
	if User.query.filter_by(username=data['username']).count()>0:
		return bad_request('Please enter a new username')
	if User.query.filter_by(email=data['email']).count()>0:
		return bad_request('Please enter a new email address')

	# 添加数据
	print(data)
	user = User()
	user.from_dict(data,is_new=True)
	db.session.add(user)
	db.session.commit()

	# 返回值
	response = jsonify(user.to_dict())
	#response.status_code=201
	#response.headers['Location'] = url_for('api.get_user',id=user.id)
	return response

# 操作：修改用户信息
@bp.route('/user/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
	user = User.query.get_or_404(id)
	data = request.get_json() or {}
	# 校验：用户名，
	# 1. 是否要改用户名
	# 2. 预改名是否和现有不一致
	# 3. 预改名是否和其他重复（怎么判断其他？）
	if 'username' in data and user.username!= data['username'] and User.query.filter_by(username=data['username']).first():
		return bad_request('Please enter a different name')
	if 'email' in data and user.email != data['email'] and User.query.filter_by(email=data['email']).first():
		return bad_request('Please enter a different email')
	user.from_dict(data, is_new=False)

	# 提交数据
	db.session.commit()
	return jsonify(user.to_dict())


#操作：删除用户
@bp.route('/user/<int:id>', methods=['DELETE'])
@token_auth.login_required
def del_user(id):
	pass
