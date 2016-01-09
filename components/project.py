from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import urllib
import json

#helpers section



# permissions section
@app.permission('project')
def permission_project(action=None, project=None, account=None):
	"""Project CRUD check for signed in account. 
	@description Check if a signed in account has a specified action for a given project. 
	@param <str>action, valid values ["list", "administer", "create", "read", "update", "delete"]
	@param <Project>project (optional) 
	@return bool 
	@example Call as app.access('project', action='update', project=PROJECT)"""
	from models.project import Project
	from helpers.project import ProjectHelper
	
	if not action:
		raise Exception('Project CRUD permission: action missing')
	
	if not account or not account.id:
		account=g.account
	
	if not project and not action in ['list', 'administer', 'create']:
		raise Exception('Project CRUD permission: project required for action "'+action+'"')
	
	if action == 'list':
		return app.access('group', account=account, group_alias=['administrator', 'privileged_manager'])
	if action == 'administer':
		return app.access('group', account=account, group_alias=['administrator', 'privileged_manager'])
	elif action == 'create':
		return app.access('group', account=account, group_alias=['administrator', 'privileged_manager', 'manager'])
	elif action == 'read':
		if project.status & project.STATUS_DELETED:
			return app.access('group', account=account, group_alias=['administrator', 'privileged_manager'])
		elif ProjectHelper.projectHasActiveMember(project=project, account=account):
			return True
		else:
			return app.access('group', account=account, group_alias=['administrator', 'privileged_manager'])
	elif action == 'update':
		if project.status & project.STATUS_DELETED:
			return app.access('group', account=account, group_alias=['administrator', 'privileged_manager'])
		elif ProjectHelper.projectHasManager(project=project, account=account):
			return True
		else:
			return app.access('group', account=account, group_alias=['administrator', 'privileged_manager'])
	elif action == 'delete':
		return app.access('group', account=account, group_alias=['administrator', 'privileged_manager'])
	elif action == 'role':
		if project.status & project.STATUS_DELETED:
			return app.access('group', account=account, group_alias=['administrator', 'privileged_manager'])
		else:
			return app.access('group', account=account, group_alias=['administrator', 'privileged_manager'])
	else:
		raise Exception('Project CRUD permission: incorrect action "'+action+'", must be ["list", "administer", "create", "read", "update", "delete"]')



@app.permission('membership')
def permission_membership(account=None):
	"""Accounts' membership check for signed in account. 
	@description Check if a signed in account is permitted to see the given account's membership projects. 
	@param <Account>account 
	@return bool 
	@example Call as app.access('membership', account=ACCOUNT)"""
	if not account:
		raise Exception('Membership permission: account missing')
	
	if account.id == g.account.id:
		return app.access('profile', action='read', account=account)
	else:
		return app.access('profile', action='read', account=account) and app.access('project', action='list')
		



# request hooks section
@app.before_request
def session_before_request():
	pass

@app.teardown_request
def session_teardown_request(exception):
	pass



# routes section
@app.route('/projects', methods=['GET', 'POST'])
@app.route('/projects/membership/<account_id>', methods=['GET', 'POST'])
@app.login_required
def project_index(account_id=None):
	from models.account import Account
	from models.project import Project
	from helpers.project import ProjectHelper
	
	title = g._t('projects')
	
	if account_id:
		account_id = urllib.unquote_plus(account_id)
		account = Account.query.filter_by(id=account_id).first()
		if not account:
			abort(404)
		elif not app.access('membership', account=account):
			abort(403)
		
		projectList = ProjectHelper.listProjectsForMember(account)
	else:
		account = g.account
		
		if app.access('project', action='administer'):
			projectList = ProjectHelper.listProjects()
		elif app.access('project', action='list'):
			projectList = ProjectHelper.listActiveProjects()
		elif app.access('membership', account=account):
			projectList = ProjectHelper.listProjectsForMember(account)
		else:
			abort(403)
	
	return render_template('project/index.html', title=title, projectList=projectList, account=account)



@app.route('/project/<project_id>', methods=['GET', 'POST'])
@app.login_required
def project_view(project_id):
	from models.project import Project
	
	project_id = urllib.unquote_plus(project_id)
	project = Project.query.filter_by(id=project_id).first()
	if not project:
		abort(404)
	elif not app.access('project', action='read', project=project):
		abort(403)
	
	title = project.__str__()
	
	breadcrumbs = (
		(g._t('projects'), url_for('project_index')),
		(title, "#")
	)
	
	return render_template('project/view.html', project=project, title=title, breadcrumbs=breadcrumbs)



@app.route('/project/add', methods=['GET', 'POST'])
@app.route('/project/<project_id>/edit', methods=['GET', 'POST'])
@app.login_required
def project_edit(project_id=None):
	from models.account import Account
	from models.project import Project, Label
	
	project = None
	if not project_id:
		project = Project()
		project.status = Project.STATUS_ACTIVE
		if not app.access('project', action='create'):
			abort(403)
	else:
		project_id = urllib.unquote_plus(project_id)
		project = Project.query.filter_by(id=project_id).first()
		if not project:
			abort(404)
		elif not app.access('project', action='update', project=project):
			abort(403)
	
	validationErrors = []
	if request.method == 'POST' and request.form.get('csrf_token', None):
		project.alias = request.form.get('project_alias', project.alias).strip()
		project.title = request.form.get('project_title', project.title).strip()
		project.info = request.form.get('project_info', project.info).strip()
		project.status = int(request.form.get('project_status', project.status).strip())
		
		validationErrors.extend(project.validate())
		if not validationErrors:
			project.save()
			
			if not Label.query.filter_by(project_id=project.id, title=Label.LABEL_DEFAULT).first():
				label = Label()
				label.project_id = project.id
				label.title = Label.LABEL_DEFAULT
				label.save()
			
			flash(g._t('project submit success'))
			return redirect(url_for('project_view', project_id=urllib.quote_plus(str(project.id))))
	
	if project_id:
		title = g._t('edit project')
	else:
		title = g._t('add project')
	
	if project_id:
		breadcrumbs = (
			(g._t('projects'), url_for('project_index')),
			(project.__str__(), url_for('project_view', project_id=urllib.quote_plus(str(project_id)))),
			(title, "#")
		)
	else:
		breadcrumbs = (
			(g._t('projects'), url_for('project_index')),
			(title, "#")
		)
	
	return render_template('project/edit.html', project_id=project_id, project=project, errors=validationErrors, title=title, breadcrumbs=breadcrumbs)



@app.route('/project/<project_id>/components', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.login_required
def project_components(project_id):
	from models.project import Project, Component
	
	project_id = urllib.unquote_plus(project_id)
	project = Project.query.filter_by(id=project_id).first()
	if not project:
		abort(404)
	elif not app.access('project', action='update', project=project):
		abort(403)
	
	title = g._t('project components')
	
	breadcrumbs = (
		(g._t('projects'), url_for('project_index')),
		(project.__str__(), url_for('project_view', project_id=urllib.quote_plus(str(project_id)))),
		(title, "#")
	)
	
	if (request.form.get('method') == 'PUT' or request.method == 'PUT') and request.form.get('csrf_token'):
		submittedComponent = Component.query.filter_by(id=request.form.get('component_id')).first()
		if submittedComponent:
			submittedComponent.alias = request.form.get('component_alias', '')
			submittedComponent.title = request.form.get('component_title', '')
			submittedComponent.info = request.form.get('component_info', '')
		
			if not submittedComponent.validate():
				submittedComponent.save()
				
				flash( g._t('component update success'))
				return redirect(url_for('project_components', project_id=urllib.quote_plus(str(project_id))))
		else:
			flash( g._t('component not found'), 'error')
		
	elif (request.form.get('method') == 'DELETE' or request.method == 'DELETE') and request.form.get('csrf_token'):
		submittedComponent = Component.query.filter_by(id=request.form.get('component_id')).first()
		if submittedComponent:
			submittedComponent.delete()
		
			flash( g._t('component delete success'))
			return redirect(url_for('project_components', project_id=urllib.quote_plus(str(project_id))))
		else:
			flash( g._t('component not found'), 'error')
		
	elif (request.form.get('method') == 'POST' or request.method == 'POST') and request.form.get('csrf_token'):
		submittedComponent = Component()
		submittedComponent.project_id = project.id
		submittedComponent.alias = request.form.get('component_alias', '')
		submittedComponent.title = request.form.get('component_title', '')
		submittedComponent.info = request.form.get('component_info', '')
		
		if not submittedComponent.validate():
			submittedComponent.save()
			
			flash( g._t('component create success'))
			return redirect(url_for('project_components', project_id=urllib.quote_plus(str(project_id))))
		
	else:
		submittedComponent = Component()
	
	return render_template('project/components.html', project_id=project_id, project=project, submittedComponent=submittedComponent, title=title, breadcrumbs=breadcrumbs)



@app.route('/project/<project_id>/members', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.login_required
def project_members(project_id):
	from models.account import Account
	from models.project import Project, Component, Membership, Role
	from helpers.account import AccountHelper
	from helpers.project import ProjectHelper
	
	project_id = urllib.unquote_plus(project_id)
	project = Project.query.filter_by(id=project_id).first()
	if not project:
		abort(404)
	elif not app.access('project', action='update', project=project):
		abort(403)
	
	title = g._t('project members')
	
	breadcrumbs = (
		(g._t('projects'), url_for('project_index')),
		(project.__str__(), url_for('project_view', project_id=urllib.quote_plus(str(project_id)))),
		(title, "#")
	)
	
	if (request.form.get('method') == 'PUT' or request.method == 'PUT') and request.form.get('csrf_token'):
		submittedMembership = Membership.query.filter_by(project=project, id=request.form.get('membership_id')).first()
		if submittedMembership:
			submittedMembership.component = Component.query.filter_by(project=project, id=request.form.get('membership_component_id', None)).first()
			submittedMembership.account = Account.query.filter_by(id=request.form.get('membership_account_id', None)).first()
			submittedMembership.role = Role.query.filter_by(id=request.form.get('membership_role_id', None)).first()
			
			if not submittedMembership.validate():
				submittedMembership.save()
				
				flash( g._t('membership update success'))
				return redirect(url_for('project_members', project_id=urllib.quote_plus(str(project_id))))
		else:
			flash( g._t('membership not found'), 'error')
		
	elif (request.form.get('method') == 'DELETE' or request.method == 'DELETE') and request.form.get('csrf_token'):
		submittedMembership = Membership.query.filter_by(project=project, id=request.form.get('membership_id')).first()
		if submittedMembership:
			submittedMembership.delete()
		
			flash( g._t('membership delete success'))
			return redirect(url_for('project_members', project_id=urllib.quote_plus(str(project_id))))
		else:
			flash( g._t('membership not found'))
		
	elif (request.form.get('method') == 'POST' or request.method == 'POST') and request.form.get('csrf_token'):
		submittedMembership = Membership()
		submittedMembership.project_id = project.id
		component = Component.query.filter_by(project=project, id=request.form.get('membership_component_id', None)).first()
		if component:
			submittedMembership.component_id = component.id
		account = submittedMembership.account_id = Account.query.filter_by(id=request.form.get('membership_account_id', None)).first()
		if account:
			submittedMembership.account_id = account.id
		role = Role.query.filter_by(id=request.form.get('membership_role_id', None)).first()
		if role:
			submittedMembership.role_id = role.id
		
		if not submittedMembership.validate():
			submittedMembership.save()
			
			flash( g._t('membership create success'))
			return redirect(url_for('project_members', project_id=urllib.quote_plus(str(project_id))))
		
	else:
		submittedMembership = Membership()
	
	if app.access('profile', action='administer'):
		accountList =AccountHelper.listAccounts()
	elif app.access('profile', action='list'):
		accountList = AccountHelper.listActiveAccounts()
	else:
		accountList = [g.account]
	
	if app.access('profile', action='administer'):
		componentList = ProjectHelper.listComponents(project=project)
	elif app.access('profile', action='list'):
		componentList = ProjectHelper.listActiveComponents(project=project)
	else:
		componentList = [ProjectHelper.getDefaultComponent(project=project)]
	
	roleList = ProjectHelper.listRoles()
	
	return render_template('project/members.html', project_id=project_id, project=project, accountList=accountList, roleList=roleList, roleDefault=ProjectHelper.getDefaultRole(), submittedMembership=submittedMembership, title=title, breadcrumbs=breadcrumbs)



@app.route('/project/<project_id>/labels', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.login_required
def project_labels(project_id):
	from models.project import Project, Label
	
	project_id = urllib.unquote_plus(project_id)
	project = Project.query.filter_by(id=project_id).first()
	if not project:
		abort(404)
	elif not app.access('project', action='update', project=project):
		abort(403)
	
	title = g._t('project labels')
	
	breadcrumbs = (
		(g._t('projects'), url_for('project_index')),
		(project.__str__(), url_for('project_view', project_id=urllib.quote_plus(str(project_id)))),
		(title, "#")
	)
	
	if (request.form.get('method') == 'PUT' or request.method == 'PUT') and request.form.get('csrf_token'):
		submittedLabel = Label.query.filter_by(project=project, id=request.form.get('label_id')).first()
		if submittedLabel:
			submittedLabel.title = request.form.get('label_title', '')
		
			if not submittedLabel.validate():
				submittedLabel.save()
				
				flash( g._t('label update success'))
				return redirect(url_for('project_labels', project_id=urllib.quote_plus(str(project_id))))
		else:
			flash( g._t('label not found'), 'error')
		
	elif (request.form.get('method') == 'DELETE' or request.method == 'DELETE') and request.form.get('csrf_token'):
		submittedLabel = Label.query.filter_by(project=project, id=request.form.get('label_id')).first()
		if submittedLabel:
			submittedLabel.delete()
			
			# project may not have zero labels, default one will be set
			if not Label.query.filter_by(project_id=project.id, title=Label.LABEL_DEFAULT).first():
				label = Label()
				label.project_id = project.id
				label.title = Label.LABEL_DEFAULT
				label.save()
			
			flash( g._t('label delete success'))
			return redirect(url_for('project_labels', project_id=urllib.quote_plus(str(project_id))))
		else:
			flash( g._t('label not found'), 'error')
		
	elif (request.form.get('method') == 'POST' or request.method == 'POST') and request.form.get('csrf_token'):
		submittedLabel = Label()
		submittedLabel.project_id = project_id
		submittedLabel.title = request.form.get('label_title', '')
		
		if not submittedLabel.validate():
			submittedLabel.save()
			
			flash( g._t('label create success'))
			return redirect(url_for('project_labels', project_id=urllib.quote_plus(str(project_id))))
		
	else:
		submittedLabel = Label()
	
	return render_template('project/labels.html', project_id=project_id, project=project, submittedLabel=submittedLabel, title=title, breadcrumbs=breadcrumbs)



@app.route('/project/<project_id>/delete', methods=['GET', 'POST'])
@app.login_required
def project_delete(project_id):
	from models.project import Project
	
	project_id = urllib.unquote_plus(project_id)
	project = Project.query.filter_by(id=project_id).first()
	
	if not project:
		abort(404)
	elif not app.access('project', action='update', project=project):
		abort(403)
	
	if request.method == 'POST' and request.form.get('csrf_token', None):
		if request.form.get('action') == 'project_action_remove_permanently':
			if not app.access('project', action='delete', project=project):
				abort(403)
			else:
				project.delete()
				success_message = g._t('project remove permanently success')
		elif request.form.get('action') == 'project_action_delete':
			project.status = project.status | project.STATUS_DELETED
			project.save()
			success_message = g._t('project delete success')
		
		flash(success_message)
		return redirect(url_for('project_index'))
	
	errors = []
	
	title = g._t('project delete')
	breadcrumbs = (
		(g._t('projects'), url_for('project_index')),
		(project.__str__(), url_for('project_view', project_id=urllib.quote_plus(str(project.id)))),
		(title, "#")
	)
	
	return render_template( 'project/delete.html', project=project, title=title, breadcrumbs=breadcrumbs, errors=errors )
