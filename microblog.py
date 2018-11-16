from app import create_app, db
from app.models import User, Post, Tag, followers, Role, Permission

app = create_app()

#shell上下文
@app.shell_context_processor
def make_shell_context():
	return {'db':db, 'User':User, 'Post':Post, 'Tag':Tag, 'followers':followers, 'Role':Role, 'Permission':Permission}
