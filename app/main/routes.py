from datetime import datetime

from app import db, bootstrap
from app.main import bp
from app.translate import translate
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Post, Tag

from flask import render_template, flash, redirect, url_for, request, current_app, g, session, jsonify
from flask_login import current_user, login_required


import json

@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
@login_required
def index():
	form = PostForm()
	if form.validate_on_submit():
		tags = form.tags.data.split(',')
		post = Post(body=form.post.data, user_id=current_user.id)
		post.edit_tags(*tags)
		db.session.add(post)
		db.session.commit()
		flash('Post success')
		return redirect(url_for('main.index'))
	title = 'index'
	page_num = request.args.get('page_num',1,type=int)
	posts_paginate = current_user.get_followed_posts().paginate(page_num, current_app.config['POSTS_PER_PAGE'], False)
	posts = posts_paginate.items
	pagination = {
		'first_page' : url_for('main.index'),
		'last_page' : url_for('main.index',page_num=posts_paginate.pages),
		'next_page' : url_for('main.index',page_num=posts_paginate.next_num),
		'prev_page' : url_for('main.index',page_num=posts_paginate.prev_num),
		'has_next' : posts_paginate.has_next,
		'has_prev' : posts_paginate.has_prev,
		'pages':posts_paginate.pages
	}
	return render_template('index.html', form = form, title=title, posts = posts, pagination = pagination, datetime=datetime.utcnow() )


@bp.route('/posts', methods=['GET'])
@login_required
def posts():
	posts = Post.query.all()
	return render_template('posts.html', title='Posts list', posts=posts)

@bp.route('/user/<username>', methods=['GET','POST'])
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).all()
	return render_template('user.html', title='User', user=user, posts=posts)

@bp.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found'.format(username))
		return redirect(url_for('main.index'))
	if user == current_user:
		flash('Could not follow yourself!')
		return redirect(url_for('main.user',username=username))
	current_user.follow(user)
	db.session.commit()
	flash('Follow {} success!'.format(username))
	return redirect(url_for('main.user',username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if not current_user.is_following(user):
		flash('Can not unfollow user {}'.format(username))
		redirect(url_for('main.user',username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('Unfollow {} success'.format(username))
	return redirect(url_for('main.user', username=username))



@bp.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('main.user',username=current_user.username))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile',form=form)


# api服务
@bp.route('/translate', methods=['GET','POST'])
@login_required
def translate_text():
	return jsonify(translate(
		request.args.get('text'),
		request.args.get('from') or 'en',
		request.args.get('to') or 'zh'
	))


# 设置全局钩子
@bp.before_request
def before_request():
	# 将user的 last_seen属性付值
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
	if not session.get('sessionId'):
		print('new_session')
		session['sessionId'] = str(datetime.utcnow())
		print(dir(session))
	g.sessionId = session.get('sessionId')

@bp.after_request
def after_request(response):
	# 添加header，及header验证
	response.headers["X-SaintIC-Media-Type"] = "saintic.v1"
	#response.headers["X-SaintIC-Request-Id"] = request.requestId
	response.headers["Access-Control-Allow-Origin"] = "*"
	username = 'anonymous'

	if current_user.is_authenticated:
		username = current_user.username

	current_app.logger.info(json.dumps({
		"AccessLog": {
			"sessionId":g.sessionId,
			"status_code": response.status_code,
			"method": request.method,
			"ip": request.headers.get('X-Real-Ip', request.remote_addr),
			"url": request.url,
			"referer": request.headers.get('Referer'),
			"agent": request.headers.get("User-Agent"),
			"user": username
		}
	}
	))
	return response


