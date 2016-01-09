#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup
import time
import datetime

#helpers section



# request hooks section
@app.before_request
def session_before_request():
  pass

@app.teardown_request
def session_teardown_request( exception ):
  pass



""" TEST CONTROLLER - TEST DATA """
def _test_data_menu():
  data = '<ul class="nav nav-pills">'+ ''.join([
    '<li><a href="%s">%s</a></li>' % (url_for('test_data_index'), url_for('test_data_index')), 
    '<li><a href="%s"><b>%s</b></a></li>' % (url_for('test_data_create'), url_for('test_data_create')), 
    '<li><a href="%s"><b>%s</b></a></li>' % (url_for('test_data_delete'), url_for('test_data_delete')), 
    '<li><a href="%s">%s</a></li>' % (url_for('test_data_employees'), url_for('test_data_employees')), 
    '<li><a href="%s">%s</a></li>' % (url_for('test_data_projects'), url_for('test_data_projects')) 
  ]) + '</ul>'
  return data

@app.route('/test/data/', methods=['GET', 'POST'])
@app.route('/test/data/index', methods=['GET', 'POST'])
def test_data_index():
  title = 'Testing | Data'
  
  data = _test_data_menu()
  data = Markup(data)
  
  return render_template('test/index.html', title=title, data=data)



@app.route('/test/data/employees', methods=['GET', 'POST'])
def test_data_employees():
  from models.account import Account
  
  title = 'Testing | Data | Listed per-account-role permissions'
  
  employees = [account for account in Account.all() if account.id.startswith('test.')]
  
  data = _test_data_menu()
  data = data + '<table class="table" width="100%">'
  roles = g._var(name='roles', scope='permissions', default={}).keys()
  
  data = data + '<tr>'
  data = data + '<th>&nbsp;</th>'
  for role in roles:
    data = data + '<th>'+role+'</th>'
  data = data + '</tr>'
  
  for employee in employees:
    data = data + '<tr>'
    data = data + '<th>'+employee.id+'</th>'
    for role in roles:
      is_permitted = app.access('role', account=employee, role_id=role)
      data = data + (is_permitted and '<td class="alert alert-success">yes</td>' or '<td class="alert alert-danger">no</td>')
    data = data + '</tr>'
  
  data = data + '</table>'
  data = Markup(data)
  
  return render_template('test/index.html', title=title, data=data)



@app.route('/test/data/projects', methods=['GET', 'POST'])
def test_data_projects():
  from models.account import Account
  from models.project import Project
  
  title = 'Testing | Data | Listed per-account-project membership'
  
  employees = [account for account in Account.all() if account.id.startswith('test.')]
  projects = [project for project in Project.all() if project.id.startswith('TEST/')]
  
  data = _test_data_menu()
  data = data + '<table class="table" width="100%">'
  roles = g._var(name='roles', scope='permissions', default={}).keys()
  
  data = data + '<tr>'
  data = data + '<th>&nbsp;</th>'
  for project in projects:
    data = data + '<th>'+project.id+'</th>'
  data = data + '</tr>'
  
  for employee in employees:
    data = data + '<tr>'
    data = data + '<th>'+employee.id+'</th>'
    for project in projects:
      #data = data + (project.hasMember(employee.id) and '<td class="alert alert-success">'+project.members.get(employee.id, '---')+'</td>' or '<td class="alert alert-danger">no</td>')
      details = {}
      details['class'] = project.hasMember(employee.id) and 'success' or 'danger'
      details['label'] = project.hasMember(employee.id) and project.members.get(employee.id, '?') or '-'
      details['label'] = details['label'] + '<div class="pull-right">'
      
      details['label'] = details['label'] + (app.access('project', action='read', project=project, account=employee) and '<i class="icon icon-eye-open text-info"></i> | ' or '<i style="opacity:0.2" class="icon icon-eye-open muted"></i> | ')
      details['label'] = details['label'] + (app.access('project', action='update', project=project, account=employee) and '<i class="icon icon-edit text-info"></i> | ' or '<i style="opacity:0.2" class="icon icon-edit muted"></i> | ')
      details['label'] = details['label'] + (app.access('project', action='delete', project=project, account=employee) and '<i class="icon icon-trash text-info"></i>' or '<i style="opacity:0.2" class="icon icon-trash muted"></i>')
      
      details['label'] = details['label'] + '</div>'
      
      data = data + '<td class="alert alert-'+details['class']+'">'+details['label']+'</td>'
    data = data + '</tr>'
  
  data = data + '</table>'
  data = Markup(data)
  
  return render_template('test/index.html', title=title, data=data)



@app.route('/test/data/create', methods=['GET', 'POST'])
def test_data_create():
  from models.account import Account
  from models.project import Project
  from models.report import Report
  from models.variable import Variable
  
  data = {'accounts':[], 'projects':[]}
  
  roles = {
    'administrator':[], 
    'privileged_manager':[], 
    'manager':[], 
    'privileged_member':[], 
    'member':[], 
  }
  rolesVariable = Variable.query.filter_by(name='roles', scope='permissions').first()
  roles.update(rolesVariable.value or {})
  
  # administrator
  administrator_1 = Account({'id':'test.administrator_1', 'email':'test.administrator_1.@test.pmbot.com'})
  administrator_1.save()
  roles['administrator'].append(administrator_1.id)
  data['accounts'].append(administrator_1)
  
  # privileged manager to see everything, manage a project and share management with other manager on a second project
  privileged_manager_1 = Account({'id':'test.privileged_manager_1', 'email':'test.privileged_manager_1.@test.pmbot.com'})
  privileged_manager_1.save()
  roles['privileged_manager'].append(privileged_manager_1.id)
  data['accounts'].append(privileged_manager_1)
  
  # managers, one for a single project to manage, another to manage 2 more projects
  manager_1 = Account({'id':'test.manager_1', 'email':'test.manager_1.@test.pmbot.com'})
  manager_1.save()
  roles['manager'].append(manager_1.id)
  data['accounts'].append(manager_1)
  
  manager_2 = Account({'id':'test.manager_2', 'email':'test.manager_2.@test.pmbot.com'})
  manager_2.save()
  roles['manager'].append(manager_2.id)
  data['accounts'].append(manager_2)
  
  # privileged members aka leads
  privileged_member_1 = Account({'id':'test.privileged_member_1', 'email':'test.privileged_member_1.@test.pmbot.com'})
  privileged_member_1.save()
  roles['privileged_member'].append(privileged_member_1.id)
  data['accounts'].append(privileged_member_1)
  
  privileged_member_2 = Account({'id':'test.privileged_member_2', 'email':'test.privileged_member_2.@test.pmbot.com'})
  privileged_member_2.save()
  roles['privileged_member'].append(privileged_member_2.id)
  data['accounts'].append(privileged_member_2)
  
  # members - developers
  member_1 = Account({'id':'test.member_1', 'email':'test.member_1.@test.pmbot.com'})
  member_1.save()
  roles['member'].append(member_1.id)
  data['accounts'].append(member_1)
  
  member_2 = Account({'id':'test.member_2', 'email':'test.member_2.@test.pmbot.com'})
  member_2.save()
  roles['member'].append(member_2.id)
  data['accounts'].append(member_2)
  
  member_3 = Account({'id':'test.member_3', 'email':'test.member_3.@test.pmbot.com'})
  member_3.save()
  roles['member'].append(member_3.id)
  data['accounts'].append(member_3)
  
  member_4 = Account({'id':'test.member_4', 'email':'test.member_4.@test.pmbot.com'})
  member_4.save()
  roles['member'].append(member_4.id)
  data['accounts'].append(member_4)
  
  member_5 = Account({'id':'test.member_5', 'email':'test.member_5.@test.pmbot.com'})
  member_5.save()
  roles['member'].append(member_5.id)
  data['accounts'].append(member_5)
  
  rolesVariable.value = roles
  rolesVariable.save()
  
  
  
  # projects
  project_1 = Project({'id':'TEST/PROJECT_1', 'title':'project_1', 
    'partitions':{'ONE':{'': 'number one', '1': 'first'}}, 
    'members':{
      administrator_1.id:'admin' 
    }})
  project_1.save()
  data['projects'].append(project_1)
  
  project_2 = Project({'id':'TEST/PROJECT_2', 'title':'project_2', 
    'partitions':{'TWO':{'': 'number two', '1': 'first', '2':'second'}}, 
    'members':{
      manager_1.id:Project.MANAGER_MEMBER, 
      privileged_member_1.id:'lead', 
      member_1.id:'markup', 
      member_2.id:'db_admin', 
      member_3.id:'developer' 
    }})
  project_2.save()
  data['projects'].append(project_2)
  
  project_3 = Project({'id':'TEST/PROJECT_3', 'title':'project_3', 
    'partitions':{'THREE':{'': 'number three', '1': 'first', '2':'second', '3':'third'}}, 
    'members':{
      manager_1.id:Project.MANAGER_MEMBER, 
      privileged_member_2.id:'lead', 
      member_1.id:'markup', 
      member_4.id:'developer' 
    }})
  project_3.save()
  data['projects'].append(project_3)
  
  project_4 = Project({'id':'TEST/PROJECT_4', 'title':'project_4', 
    'partitions':{'FOUR':{'': 'number four', '1': 'first', '2':'second', '3':'third', '4':'fourth'}}, 
    'members':{
      privileged_manager_1.id:Project.MANAGER_MEMBER, 
      manager_2.id:Project.MANAGER_MEMBER, 
      privileged_member_2.id:'lead', 
      member_2.id:'db_admin', 
      member_5.id:'developer' 
    }})
  project_4.save()
  data['projects'].append(project_4)
  
  for account in data['accounts']:
    flash('account created: '+str(account))
  for project in data['projects']:
    flash('project created: '+str(project))
  
  return redirect(url_for('test_data_index'))



@app.route('/test/data/delete', methods=['GET', 'POST'])
def test_data_delete():
  from models.account import Account
  from models.project import Project
  from models.report import Report
  from models.variable import Variable
  
  roles = {
    'administrator':[], 
    'privileged_manager':[], 
    'manager':[], 
    'privileged_member':[], 
    'member':[], 
  }
  rolesVariable = Variable.query.filter_by(name='roles', scope='permissions').first()
  roles.update(rolesVariable.value or {})
  
  for account in [account for account in Account.all() if account.id.startswith('test.')]:
    for role_id, members in roles.items():
      if account.id in members:
        roles[role_id].remove(account.id)
    Account.delete(account.id)
    flash('account deleted: '+str(account))
  
  rolesVariable.value = roles
  rolesVariable.save()
  
  for project in [project for project in Project.all() if project.id.startswith('TEST/')]:
    Project.delete(project.id)
    flash('project deleted: '+str(project))
  
  return redirect(url_for('test_data_index'))
