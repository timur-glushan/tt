#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, Response, session, g, redirect, url_for, abort, render_template, render_template_string, flash, make_response
from application import app



# request hooks section
@app.before_request
def install_before_request():
	if not request.path.startswith('/install') and not request.path.startswith('/update') and not request.path.startswith('/static'):
		return redirect(url_for('install_index'))



@app.route( '/install/', methods=['GET', 'POST'] )
def install_index():
	return render_template('install/index.html')



@app.route( '/install/process', methods=['GET', 'POST'] )
def install_process():
	from flask import make_response
	import time
	
	if request.method != 'POST':
		return redirect(url_for('install_index'))
	
	data = []
	errors = []
	status = 200
	startTime = time.time()
	endTime = None
	
	for install_id, install in app.installs:
		try:
			data.append('[PROGRESS] Running install: '+install_id)
			print '[PROGRESS] Running install: '+install_id
			install()
		except Exception as e:
			status = 500
			data.append('* [ERROR] Exception occured during the install: '+install_id)
			print '* [ERROR] Exception occured during the install: '+install_id
			print '** ', e
			errors.append('[ERROR] Exception occured during the install: '+install_id)
			errors.append(str(e))
		finally:
			data.append('[DONE] Finished install: '+install_id)
	
	endTime = time.time()
	
	responseData = "\n".join(data) or 'None'
	responseErrors = "\n".join(errors) or 'None'
	responseStatus = str(status)
	responseText = 'STATUS: '+responseStatus\
			+"\n\nDATA:\n"+responseData\
			+"\n\nERRORS:"+responseErrors\
			+"\n\nSTARTED:\t"+str(startTime)\
			+"\n\nFINISHED:\t"+str(endTime)\
			+"\n\nDURATION:\t"+str(int(endTime)-int(startTime))\
	
	response = make_response(responseText, responseStatus)
	response.headers['Content-Type'] = 'text/plain'
	
	return response



@app.route( '/update/process', methods=['GET', 'POST'] )
def update_process():
	from flask import make_response
	import time
	
	
	if request.method != 'POST':
		return redirect(url_for('install_index'))
	
	data = []
	errors = []
	status = 200
	startTime = time.time()
	endTime = None
	
	version = request.form.get('version', '1')
	
	for update_id, update in app.updates.get(version):
		try:
			data.append('[PROGRESS] Running update: '+update_id)
			print '[PROGRESS] Running update: '+update_id
			update()
		except Exception as e:
			status = 500
			data.append('* [ERROR] Exception occured during the update: '+update_id)
			print '* [ERROR] Exception occured during the update: '+update_id
			print '** ', e
			errors.append('[ERROR] Exception occured during the update: '+update_id)
			errors.append(str(e))
		finally:
			data.append('[DONE] Finished update: '+update_id)
	
	endTime = time.time()
	
	responseData = "\n".join(data) or 'None'
	responseErrors = "\n".join(errors) or 'None'
	responseStatus = str(status)
	responseText = 'STATUS: '+responseStatus\
			+"\n\nDATA:\n"+responseData\
			+"\n\nERRORS:"+responseErrors\
			+"\n\nSTARTED:\t"+str(startTime)\
			+"\n\nFINISHED:\t"+str(endTime)\
			+"\n\nDURATION:\t"+str(int(endTime)-int(startTime))\
	
	response = make_response(responseText, responseStatus)
	response.headers['Content-Type'] = 'text/plain'
	
	return response
