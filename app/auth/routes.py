from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from app import db
from app.models import User
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse

@bp.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		#提交后台再进行验证一次，有问题重新登录
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('auth.login'))
		#提交验证通过
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('main.index')
		return redirect(next_page)
	#如get方法
	return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout', methods=['GET'])
def logout():
	logout_user()
	next_page = request.args.get('next')
	if not next_page or url_parse(next_page).netloc != '':
		next_page = url_for('main.index')
	flash('logout success!')
	return redirect(next_page)

@bp.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations,{}, register success!'.format(user.username))
		login_user(user)
		return redirect(url_for('main.index'))
	return render_template('register.html', title='Register', form=form)
