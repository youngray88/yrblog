from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, ValidationError, Length

from app.models import User, Post

class PostForm(FlaskForm):
	post = TextAreaField('Said', validators=[DataRequired(), Length(min=1, max=140)])
	tags = StringField('Tags')
	submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	about_me = TextAreaField('About Me', validators=[Length(min=0, max=140)])
	submit = SubmitField('Submit')

	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username

	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Please use a different username.')