#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app
from couchdb.client import Server, Document

def __couchdb():
	config = {
		'host': 'http://kharkiv.p-product.com:5984/',
		'database': 'run4',
		'name': None,
		'password': None
	}
	
	connection = Server(config['host'])
	if config['name'] and config['password']:
		connection.resource.credentials = (config['name'], config['password'])
	
	return connection[config['database']]



@app.install('install_migration')
def install_migration():
	"""Migrate the data from the old CouchDB storage"""
	pass



@app.install('install_migration_accounts')
def install_migration_accounts():
	"""Migrate the accounts data from the old CouchDB storage"""
	from models.account import Account, Group
	
	defaultGroup = Group.query.filter_by(alias=Group.GROUP_DEFAULT).first()
	
	for row in __couchdb().view('_design/employees/_view/employees_list'):
		value = row['value']
		account = Account.query.filter_by(alias=value.get('_id', '')).first()
		if not account:
			account = Account()
			account.alias = value.get('_id', '')
			account.email = value.get('email')
			account.first_name = value.get('first_name')
			account.last_name = value.get('last_name')
			account.stored_password = account.password = value.get('password', None)
			if value.get('deleted', False):
				account.status = Account.STATUS_ACTIVE | Account.STATUS_DELETED
			account.group_id = defaultGroup.id
			
			account.save()
			print '[MIGRATION:ACCOUNT]', account.__str__()
		



def treeRecursion(key, value, parentKey, items):
	if key == '':
		key = parentKey
	elif parentKey:
		key = parentKey+'/'+key
	else:
		key = key
	if type(value) in [str, type(u'')]:
		items.append((key,value))
	else:
		for k,v in value.items():
			treeRecursion(k, v, key, items)



@app.install('install_migration_projects')
def install_migration_projects():
	"""Migrate the projects data from the old CouchDB storage"""
	from models.account import Account
	from models.project import Project, Component, Label, Role
	
	for row in __couchdb().view('_design/projects/_view/list'):
		value = row['value']
		
		value['_id'] = value.get('_id', '').replace(':', '/')
		
		# resolve the labels INT or EXT
		value['labels'] = []
		if value.get('_id', '').startswith('INT'):
			value['labels'].append(Label.LABEL_INTERNAL)
		elif value.get('_id', '').startswith('EXT'):
			value['labels'].append(Label.LABEL_EXTERNAL)
		elif value.get('_id', '').startswith('MGM') or value.get('_id', '').startswith('OUT'):
			value['labels'].append(Label.LABEL_VACATION)
		elif value.get('_id', '') == 'NOKIA/OFFICIAL':
			value['labels'].append(Label.LABEL_VACATION)
		
		value['_id'] = value.get('_id', '').replace('EXT/', '').replace('INT/', '')
		project = Project.query.filter_by(alias=value.get('_id', '')).first()
		if not project:
			project = Project()
			project.alias = value.get('_id', '')
			project.title = value.get('title')
			project.info = value.get('description')
			if value.get('deleted', False):
				project.status = Project.STATUS_ACTIVE | Project.STATUS_DELETED
			project.save()
			print '[MIGRATION:PROJECT]', project.__str__()
		
		items = [(None, value.get('title'))]
		for k,v in value.get('partitions', {}).items():
			treeRecursion(k, v, None, items)
		
		for component_alias, component_title in items:
			if not component_alias:
				continue
			component = Component.query.filter_by(project=project, alias=component_alias).first()
			if not component:
				component = Component()
				component.alias = component_alias
				component.title = component_title
				component.project = project
				component.save()
				print '[MIGRATION:COMPONENT]', project.__str__(), component.__str__()
		
		for labelItem in value.get('labels', []):
			label = Label.query.filter_by(title=labelItem, project=project).first()
			if not label:
				label = Label()
				label.title = labelItem
				label.project = project
				label.save()



#@app.install('install_migration_reports')
def install_migration_reports():
	"""Migrate the reports data from the old CouchDB storage"""
	from models.account import Account
	from models.project import Project, Component
	from models.report import Report
	import datetime
	
	fault = open('data/fault.log', 'w')
	
	for row in __couchdb().view('_design/reports/_view/list_by_date', startkey=['2013-01-01'], endkey=['2014-12-12']):
		try:
			value = row['value']
			value['project'] = value.get('project', '').replace(':', '/').replace('EXT/', '').replace('INT/', '')
			
			report = Report()
			report.due_date = value.get('due_date')
		
			if value.get('reporter', ''):
				report.reporter = Account.query.filter_by(alias=value.get('reporter', '')).first()
		
			if value.get('project', ''):
				report.project = Project.query.filter_by(alias=value.get('project', '')).first()
		
			if value.get('partition', []):
				component_alias = '/'.join(partition.keys()[0] for partition in value.get('partition', []))
			else:
				component_alias = Component.COMPONENT_DEFAULT
			report.component = Component.query.filter_by(project=report.project, alias=component_alias).first() or Component.query.filter_by(project=project, alias=Component.COMPONENT_DEFAULT).first()
		
			report.duration = float(value.get('hours', 0))
			report.summary = value.get('summary', '')
			if value.get('employee', ''):
				report.account = Account.query.filter_by(alias=value.get('employee', '')).first()
		
			if value.get('deleted', False):
					report.status = Report.STATUS_ACTIVE | Report.STATUS_DELETED
		
			report.save()
			print '[MIGRATION:REPORT]', report.__str__()
		except Exception as e:
			message = datetime.datetime.now().__str__().split('.')[0] + '\n\t' + str(e)
			print message
			fault.write(message)
	
	fault.close()
