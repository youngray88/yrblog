from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectMultipleField, widgets, HiddenField
from wtforms.validators import DataRequired, ValidationError, Length

from app.models import User, Post

class ChoiceObj(object):
	def __init__(self, name, choices):
		setattr(self,name,choices)

class MultiCheckboxField(SelectMultipleField):
	widget = widgets.ListWidget(prefix_label=True)

# 角色操作
class EditUserRoleForm(FlaskForm):
	roles = MultiCheckboxField('roles',option_widget = widgets.RadioInput())
	submit = SubmitField('Submit')


class AddNewRole(FlaskForm):
	role = StringField('new role',validators=[DataRequired()])
	submit = SubmitField('Submit')


class DelRole(FlaskForm):
	submit = SubmitField('delete')


class EditRole(FlaskForm):
	perms = MultiCheckboxField('perms',coerce=int,option_widget = widgets.CheckboxInput())
	submit = SubmitField('Submit')