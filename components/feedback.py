#!/usr/bin/python
# -*- coding: utf-8 -*-

from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, Response, render_template, flash
from models.account import Account
import urllib
import json
import time

#helpers section



# request hooks section
@app.before_request
def profile_before_request():
	pass

@app.teardown_request
def profile_teardown_request(exception):
	pass



# routes section
@app.route('/feedback/', methods=['GET', 'POST'])
@app.authorized_group('administrator')
def feedback_index():
	from models.feedback import Feedback
	
	title = g._t('feedback')
	breadcrumbs = (
		(g._t('administration'), url_for('administration_index')),
		(title, "#")
	)
	
	feedbackList = Feedback.query.all()
	
	return render_template('feedback/index.html', title=title, breadcrumbs=breadcrumbs, feedbackList=feedbackList)



# routes section
@app.route('/feedback/submit', methods=['GET', 'POST'])
@app.login_required
def feedback_submit():
	from models.feedback import Feedback
	
	title = g._t('submit feedback')
	
	if request.values.get('csrf_token', None):
		feedback = Feedback()
		feedback.account = g.account
		feedback.subject = request.values.get('feedback_subject', '').strip()
		feedback.message = request.values.get('feedback_message', '').strip()
		feedback.created = int(time.time())
		validationErrors = feedback.validate()
		if not validationErrors:
			status = 200
			description = 'OK'
			feedback.save()
			if request.is_ajax:
				return Response(json.dumps({
					'html':render_template('_popup.html', title=g._t( 'feedback submit success' ), message=g._t('feedback submit success message')),
					'status':status,
					'description':description,
					'errors':validationErrors
				}), mimetype='application/json')
			else:
				flash(g._t('feedback submit success'))
				return redirect(url_for('application_index'))
		else:
			status = 400
			description = 'Bad request'
	else:
		status = 200
		description = 'OK'
		validationErrors = []
		
	if request.is_ajax:
		htmlContent = render_template('feedback/submit-popup.html', title=title, errors=validationErrors)
		return  Response(json.dumps({'html':htmlContent, 'status':status, 'description':description, 'errors':validationErrors}), mimetype='application/json')
	else:
		htmlContent = render_template('feedback/submit.html', title=title, errors=validationErrors)
		return htmlContent



@app.route('/feedback/<feedback_id>/delete', methods=['GET', 'POST'])
@app.authorized_group('administrator')
def feedback_delete(feedback_id):
	from models.feedback import Feedback
	
	if not g.account:
		return redirect( url_for( 'session_signin' ) )
	if not g.account.isAdministrator():
		abort( 403 )
	
	feedback = Feedback.query.filter(feedback_id).first_or_404()
	
	feedback.delete()
	
	flash(g._t('feedback remove success'))
	
	return redirect(url_for('feedback_index'))
