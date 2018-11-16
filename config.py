import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'never-guess'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False


	# 分页
	POSTS_PER_PAGE = 3


	# 百度翻译认证参数
	BD_TRANSLATOR_APPID = 20180906000203714
	BD_TRANSLATOR_KEY = 'u3gaBnpIVYcwjWdaOIqN'
	BD_TRANSLATOR_URL = 'http://api.fanyi.baidu.com/api/trans/vip/translate'


	# 基础用户分类
	# 基础权限定义
	INIT_PERMISSION = [
		'POST_WRITE','POST_UPLOAD','POST_COLLECT','POST_COMMENT',
		'USER_FOLLOW',
		'ADMIN'
	]
	INIT_ROLE = ['ADMIN','USER','LOCKED','GUEST']
	INIT_ROLE_PERM_MAP = {
		'ADMIN':[
			'POST_WRITE','POST_COMMENT','POST_COLLECT','POST_UPLOAD',
			'USER_FOLLOW',
			'ADMIN'
		],
		'USER':[
			'POST_WRITE','POST_COMMENT','POST_COLLECT',
			'USER_FOLLOW'
		],
		'LOCKED':[
			'USER_FOLLOW','POST_COLLECT'
		]
	}