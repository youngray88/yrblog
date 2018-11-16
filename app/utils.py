from functools import wraps
from flask_login import current_user
from flask import abort

def permission_required(permission_name):
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			if not current_user.can_do(permission_name):
				abort(403)
			return func(*args, **kwargs)
		return wrapper
	return decorator