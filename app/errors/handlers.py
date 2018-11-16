from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

#通过request.accept_mimetypes属性的值（0 or 1）判断访问类型，是通过浏览器访问还是接口访问
def wants_json_response():
	return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']

@bp.app_errorhandler(404)
def error_404(error):
	if wants_json_response():
		return api_error_response(404)
	return render_template('404.html'), 404

@bp.app_errorhandler(403)
def error_404(error):
	if wants_json_response():
		return api_error_response(403)
	return render_template('403.html'), 403

@bp.app_errorhandler(500)
def error_500(error):
	db.session.rollback()
	if wants_json_response():
		return api_error_response(500)
	return render_template('500.html'), 500