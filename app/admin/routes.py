from flask import render_template,request,url_for, flash, redirect,  abort
from app import db
from app.utils import permission_required
from app.admin import bp
from app.models import User, Role, Permission
from app.admin.forms import EditUserRoleForm, ChoiceObj, AddNewRole, DelRole, EditRole

@bp.route('/users')
@bp.route('/')
@permission_required('ADMIN')
def users_setup():
	page = request.args.get('page')
	per_page = request.args.get('per_page')
	users = User.query.all()

	return render_template('users.html',users = users, title='users')


@bp.route('/user_edit_role/<user_id>',methods=['GET','POST'])
@permission_required('ADMIN')
def user_edit_role(user_id):
	user = User.query.get_or_404(user_id)
	role = Role.query.all()

	selectedChoice = ChoiceObj('roles',[role.name for role in user.role])
	form = EditUserRoleForm(obj=selectedChoice)
	form.roles.choices = [(x.name,x.name) for x in Role.query.all()]

	if form.validate_on_submit():
		roles = form.roles.data
		user.set_role(*roles)
		db.session.commit()
		flash('update success')
		redirect(url_for('admin.user_edit_role',user_id=user_id))

	return render_template('user_edit_role.html', role = role,user=user,title='edit_user_role',form = form)

@bp.route('/roles', methods=['GET','POST'])
@permission_required('ADMIN')
def roles_setup():
	roles = Role.query.all()
	form = AddNewRole()
	form_del = DelRole()
	if request.method=="POST":
		flash('post')
	if form.validate_on_submit():
		role_name = form.role.data
		print(role_name)
		if(Role.query.filter_by(name=role_name).first() is not None):
			flash('Have role already')
			return redirect(url_for('admin.roles_setup'))
		role = Role(name=role_name)
		db.session.add(role)
		db.session.commit()
		flash('add new role successfull')
		return redirect(url_for('admin.roles_setup'))
	return render_template('roles.html', roles=roles, title='roles setup',form=form,form_del = form_del)


@bp.route('/role_del/<roleid>', methods=['GET','POST'])
@permission_required('ADMIN')
def roles_del(roleid):
	role = Role.query.get(roleid)
	form = DelRole()
	if form.validate_on_submit():
		db.session.delete(role)
		db.session.commit()
		flash('del success')
		return redirect(url_for('admin.roles_setup'))
	return abort(404)


@bp.route('/role_edit/<roleid>', methods=['GET','POST'])
@permission_required('ADMIN')
def roles_edit(roleid):
	perms = Permission.query.all()
	role = Role.query.get(roleid)
	selectedChoice = ChoiceObj('perms',[perm.id for perm in role.perms])
	form = EditRole(obj=selectedChoice)
	form.perms.choices = [(x.id,x.name) for x in perms]
	if form.validate_on_submit():
		print('++++')
		sub_perms = form.perms.data
		role.set_perms(*sub_perms)
		db.session.commit()
		flash('edit ok')
		return redirect(url_for('admin.roles_edit',roleid=roleid))
	return render_template('roles_edit.html', role = role, perms = perms,form = form)