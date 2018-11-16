from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from hashlib import md5
from flask_login import UserMixin, AnonymousUserMixin
from flask import url_for, current_app
from app import login, db
import base64,os

tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
                )

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
					  db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                      )

role_perms = db.Table('role_perms',
                      db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                      db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                      )

# 成功调用的前提是：原类需要提供to_dict方法，输出成为python 字典格式的数据
# endpoint指url_for 可调用的资源地址，kwargs指需要传递的参数
# paginate
class PaginatedAPIMixin(object):
	@staticmethod
	def to_collection_dict(query, page, per_page, endpoint, **kwargs):
		recourse = query.paginate(page, per_page, False)
		data = {
			'items': [item.to_dict() for item in recourse.items],
			'_meta': {
				'page':page,
				'per_page':per_page,
				'total_page':recourse.pages,
				'total_items':recourse.total
			},
			'_links':{
				'self':url_for(endpoint,page=page,per_page=per_page,**kwargs),
				'next':url_for(endpoint,page=page+1,per_page=per_page,**kwargs) if recourse.has_next else None,
				'prev':url_for(endpoint,page=page-1,per_page=per_page,**kwargs) if recourse.has_prev else None
			}
		}
		return data

class User(db.Model, UserMixin, PaginatedAPIMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)

	token = db.Column(db.String(32), index=True, unique=True)
	token_expiration = db.Column(db.DateTime)

	followed = db.relationship(
		'User',
		secondary=followers,
		lazy='dynamic',
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers', lazy='dynamic'))

	role = db.relationship(
		'Role',
		secondary=user_roles,
		lazy='dynamic',
		backref=db.backref('users', lazy='dynamic')
	)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	#需要调整
	def get_avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,size)

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id
		).count() > 0

	def follow(self,user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def get_followed_posts(self):
		return Post.query.join(
			followers,
			followers.c.followed_id == Post.user_id
		).filter(
			followers.c.follower_id == self.id
		).union(
			Post.query.filter_by(user_id=self.id)
		).order_by(
			Post.timestamp.desc()
		)

	#权限管理
	#权限验证
	def can_do(self,perm_name):
		can_do = False
		for r in self.role:
			if r.can_do(perm_name):
				can_do = True
		return can_do
	#权限列表
	def perms_list(self):
		perms = {}
		for r in self.role:
			for per in r.perms:
				perms[per.name] = 1
		return perms

	# 给用户设置角色
	def set_role(self, *role_name):
		self.role = []
		if len(role_name)>0:
			for name in role_name:
				if Role.query.filter_by(name=name).first() is None:
					return False
			for name in role_name:
				self.role.append(Role.query.filter_by(name=name).first())
		return True

	def set_admin(self):
		self.set_role('ADMIN')

	# API
	# 返回字典数据（用于api）
	def to_dict(self):
		data = {
			'id':self.id,
			'username':self.username,
			'last_seen':self.last_seen,
			'about_me':self.about_me,
			'post_count':self.posts.count(),
			'followed_count':self.followed.count(),
			'follower_count':self.followers.count(),
			'_links':{
				'self':url_for('api.get_user',id=self.id),
				'followers':url_for('api.get_followers', id=self.id),
				'followed':url_for('api.get_followed', id=self.id),
				'avatar':self.get_avatar(128)
			}
		}
		return data

	# 需要先定义好或获取到user对象
	# 这样不能修改密码？
	def from_dict(self, data, is_new = False):
		for field in ['username','email','about_me']:
			if field in data:
				setattr(self, field, data[field])
			if is_new and 'password' in data:
				self.set_password(data['password'])

	# 生成或获取已有token
	# 获取返回值token
	def get_token(self,expires_in=3600):
		now = datetime.utcnow()
		if self.token and self.token_expiration - now < 60:
			return self.token
		#实际上就是为了生成一组随机数
		self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
		#过期时间延后1小时
		self.token_expiration = now + timedelta(seconds=expires_in)

		db.session.add(self)
		return self.token

	#将token设置失效
	def revoke_token(self):
		self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

	# 通过token返回用户对象
	@classmethod
	def check_token(cls,token):
		user = cls.query.filter_by(token=token).first()
		if user is None or user.token_expiration < datetime.utcnow():
			return None
		return user

	def __repr__(self):
		return '<User {}: {} @ {}>'.format(self.id, self.username, self.email)

class Post(db.Model, PaginatedAPIMixin):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	author = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
	tags = db.relationship('Tag', secondary=tags, lazy=True, backref=db.backref('pages', lazy='dynamic'))

	def __repr__(self):
		return '<Post {}: {} @ {}>'.format(self.id, self.body, self.user_id)

	# 根据tag文本编辑tag，自动判断是否已经存在tag，调用方法：p1.edit_tags('tech','aa')
	def edit_tags(self, *tags):
		for tag in tags:
			if Tag.has_tag(tag):
				self.tags.append(Tag.query.filter_by(name=tag).first())
			else:
				t = Tag(name=tag)
				db.session.add(t)
				self.tags.append(t)

	def to_dict(self):
		data = {
			'id':self.id,
			'body':self.body,
			'timestamp':self.timestamp,
			'user_id':self.user_id,
			'tags':[tag.name for tag in self.tags],
			'_links':{
				'author':url_for('api.get_user',id=self.user_id),
				'self':url_for('api.get_post',id=self.id)
			}
		}
		return data

class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)

	@classmethod
	def has_tag(cls,text):
		return cls.query.filter_by(name=text).count() > 0

	def __repr__(self):
		return '<Tag {}: {}>'.format(self.id,self.name)

#权限管理
class Role(db.Model, PaginatedAPIMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	perms = db.relationship('Permission', secondary=role_perms, lazy='dynamic', backref=db.backref('roles',lazy='dynamic'))

	#给角色设置权限
	def set_perms(self,*permid):
		for id in permid:
			if Permission.query.get(id) is None:
				return False
		self.perms = []
		for perm in permid:
			self.perms.append(Permission.query.get(perm))
		return True

	#判断角色是否有该权限
	def can_do(self,perm_name):
		return True if self.perms.filter_by(name=perm_name).first() is not None else False

	#角色、权限初始化
	@staticmethod
	def init_role_map():
		for role_name in current_app.config['INIT_ROLE']:
			if Role.query.filter_by(name=role_name).first() is None:
				db.session.add(Role(name=role_name))
		for perm_name in current_app.config['INIT_PERMISSION']:
			if Permission.query.filter_by(name=perm_name).first() is None:
				db.session.add(Permission(name=perm_name))
		for role_name in current_app.config['INIT_ROLE_PERM_MAP']:
			role = Role.query.filter_by(name=role_name).first()
			if role is not None:
				for perm_name in current_app.config['INIT_ROLE_PERM_MAP'][role_name]:
					perm = Permission.query.filter_by(name=perm_name).first()
					if perm is not None:
						role.perms.append(perm)

		# 如User没有角色，自动添加USER
		for user in User.query.all():
			if len(user.role.all())==0:
				user.role.append(Role.query.filter_by(name='USER').first())

	@staticmethod
	def reset_role_map():
		tables_to_clear = [Role.__table__,Permission.__table__,user_roles,role_perms]
		for table in tables_to_clear:
			db.session.execute(table.delete())
		Role.init_role_map()

	def __repr__(self):
		return '<Role {}: {}>'.format(self.id,self.name)

class Permission(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)

	def __repr__(self):
		return '<Permission {}: {}>'.format(self.id,self.name)

#处理Guest用户没有can_do及is_admin方法
class Guest(AnonymousUserMixin):
	def can_do(self,perm_name):
		return False

def init_data():
	Role.init_role_map()
	db.session.drop_all()
	db.session.create_all()
	admin = User(username=current_app.config['ADMIN'] or 'Admin')
	db.session.add(admin)
	db.session.commit()
	admin.set_admin()

login.anonymous_user = Guest
#用户载入函数
@login.user_loader
def load_user(id):
	return User.query.get(int(id))