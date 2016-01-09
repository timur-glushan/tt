#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup

#helpers section



# request hooks section
@app.before_request
def session_before_request():
	pass

@app.teardown_request
def session_teardown_request( exception ):
	pass



""" TEST CONTROLLER - PERMISSIONS """
@app.route( '/test/permissions/', methods=['GET', 'POST'] )
@app.route( '/test/permissions/index', methods=['GET', 'POST'] )
def test_permissions_index():
	title = 'Testing permissions'
	data = Markup('<br/>'.join([
		'<a href="%s">%s</a>' % (url_for('test_permissions_login_required'), url_for('test_permissions_login_required')),
		'<a href="%s">%s</a>' % (url_for('test_permissions_authorized_role_administrator'), url_for('test_permissions_authorized_role_administrator')),
		'<a href="%s">%s</a>' % (url_for('test_permissions_authorized_role_manager'), url_for('test_permissions_authorized_role_manager')),
		'<a href="%s">%s</a>' % (url_for('test_permissions_all_accounts_roles'), url_for('test_permissions_all_accounts_roles')),
		'<a href="%s">%s</a>' % (url_for('test_permissions_all_permissions'), url_for('test_permissions_all_permissions')),
		'<a href="%s">%s</a>' % (url_for('test_permissions_custom_word'), url_for('test_permissions_custom_word'))
	]))
	
	return render_template( 'test/index.html', title=title, data=data )



@app.route( '/test/permissions/login_required', methods=['GET', 'POST'] )
@app.login_required
def test_permissions_login_required():
	title = 'Testing "login_required"'
	data = '"login_required" pass'
	
	return render_template( 'test/index.html', title=title, data=data )



@app.route( '/test/permissions/authorized_group/administrator', methods=['GET', 'POST'] )
@app.authorized_group('administrator')
def test_permissions_authorized_role_administrator():
	title = 'Testing authorized_role "administrator"'
	data = 'Role "administrator" is permitted'
	
	return render_template( 'test/index.html', title=title, data=data )



@app.route( '/test/permissions/authorized_group/manager', methods=['GET', 'POST'] )
@app.authorized_group('manager')
def test_permissions_authorized_role_manager():
	title = 'Testing authorized_role "manager"'
	data = 'Role "manager" is permitted'
	
	return render_template('test/index.html', title=title, data=data)



@app.route( '/test/permissions/all_accounts_groups', methods=['GET', 'POST'] )
def test_permissions_all_accounts_groups():
	from models.account import Account
	
	title = 'Testing | Permissions | Listed per-account-role permissions'
	
	data = '<table class="table" width="100%">'
	employees = [employee for employee in Account.all()]
	roles = g._var(name='roles', scope='permissions', default={}).keys()
	data = data + '<tr>'
	data = data + '<th>&nbsp;</th>'
	for role in roles:
		data = data + '<th>'+role+'</th>'
	data = data + '</tr>'
	
	for employee in employees:
		data = data + '<tr>'
		data = data + '<th>'+employee+'</th>'
		for role in roles:
			is_permitted = app.access('role', account=employee, role_id=role)
			data = data + (is_permitted and '<td class="alert alert-success">yes</td>' or '<td class="alert alert-danger">no</td>')
		data = data + '</tr>'
	
	data = data + '</table>'
	data = Markup(data)
	
	return render_template( 'test/index.html', title=title, data=data )



@app.route( '/test/permissions/all_permissions', methods=['GET', 'POST'] )
def test_permissions_all_permissions():
	title = 'Testing | Permissions | All permissions listed'
	data = '<table class="table">'
	data += '<tr><th>Name</th><th>Description</th></tr>'
	for k,v in app.permissions.items():
		data += '<tr><td>%s</td><td><pre>%s</pre></td></tr>' % (k, v.__doc__)
	data += '</table>'
	data = Markup(data)
	
	return render_template( 'test/index.html', title=title, data=data )



@app.permission('test_permission_word')
def test_permission_word(word='nope'):
	"""The word should be "yep" )). 
	@description Check if a given word equals a string "yep". 
	@param <str>word, default="nope" 
	@return bool 
	@example Call as app.access('word', word="yep"), app.access('word')"""
	return word == 'yep'
	
# routes section
@app.route( '/test/permissions/custom/word', methods=['GET', 'POST'] )
def test_permissions_custom_word():
	title = 'Testing custom permission, the word should be "yep"'
	data = {
		"app.access('test_permission_word')": app.access('test_permission_word'),
		"app.access('test_permission_word', word='qwer')": app.access('test_permission_word', word='qwer'),
		"app.access('test_permission_word', word='yep')": app.access('test_permission_word', word='yep')
	}
	data = Markup('<br/>').join(["%s: %s" % (k,v) for k,v in data.items()])
	
	return render_template( 'test/index.html', title=title, data=data )
