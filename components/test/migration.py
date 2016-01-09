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



# routes section
@app.route( '/test/migration/', methods=['GET', 'POST'] )
def test_migration_index():
  title = 'Testing'
  data = ''
  
  return render_template( 'test/migration.html', title=title, data=data )



@app.route( '/test/migration/couchdb', methods=['GET', 'POST'] )
def test_migration_couchdb():
  from couchdb.client import Server, Document
  
  title = 'Testing | CouchDB views'
  
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
  
  #for row in __couchdb().view('_design/employees/_view/employees_list'):
  # print row['value']
  
  data = []
  
  options = {
    'startkey': ['2014-07-01'],
    'endkey': ['2014-12-12']
  }
  
  for row in __couchdb().view('_design/reports/_view/list_by_date', **options):
    print row['value']
    data.append(row['value'])
  
  #data = '<br/>'.join(data)
  return render_template( 'test/migration.html', title=title, data=data )



@app.route( '/test/migration/init_db', methods=['GET', 'POST'] )
def test_migration_init_db():
  """Create the DB schema for all models"""
  from application import db
  from models.feedback import Feedback
  from models.translation import Translation
  from models.variable import Variable
  from models.account import Account, Preference, Group
  from models.project import Project, Component, Membership, Role
  from models.report import Report
  
  title = 'Testing | init_db'
  
  db.create_all()
  data = 'all the models have been created'
  
  return render_template( 'test/migration.html', title=title, data=data )



@app.route( '/test/migration/generate_data', methods=['GET', 'POST'] )
def test_migration_generate_data():
  from application import db
  from models.feedback import Feedback
  from models.translation import Translation
  from models.variable import Variable
  from models.account import Account, Preference, Group
  from models.project import Project, Component, Membership, Role
  from models.report import Report
  
  title = 'Testing | generate_data'
  
  ### ACCOUNT GROUPS
  administratorGroup = Group()
  administratorGroup.alias = Group.GROUP_ADMINISTRATOR
  administratorGroup.title = 'Administrator'
  administratorGroup.info = """Administrators are the unstoppable guys - everything is permitted"""
  administratorGroup.save()
  
  privilegedManagerGroup = Group()
  privilegedManagerGroup.alias = 'privileged_manager'
  privilegedManagerGroup.title = 'Privileged Manager'
  privilegedManagerGroup.info = """Privileged Managers are almost as cool as the administrators"""
  privilegedManagerGroup.save()
  
  managerGroup = Group()
  managerGroup.alias = 'manager'
  managerGroup.title = 'Manager'
  managerGroup.info = """Managers have some extra features for management over the accounts and projects"""
  managerGroup.save()
  
  privilegedMemberGroup = Group()
  privilegedMemberGroup.alias = 'privileged_member'
  privilegedMemberGroup.title = 'Privileged Member'
  privilegedMemberGroup.info = """Privileged Members have just few extra features"""
  privilegedMemberGroup.save()
  
  memberGroup = Group.GROUP_DEFAULT
  memberGroup.alias = 'member'
  memberGroup.title = 'Member'
  memberGroup.info = """Members can submit reports and watch their own stats"""
  memberGroup.save()
  
  
  
  ### ACCOUNTS
  # administrator
  administrator_1 = Account()
  administrator_1.alias = 'test.administrator_1'
  administrator_1.email = 'test.administrator_1.@test.pmbot.com'
  administrator_1.info = 'test user: administrator_1'
  administrator_1.group = administratorGroup
  administrator_1.save()
  
  # privileged manager to see everything, manage a project and share management with other manager on a second project
  privileged_manager_1 = Account()
  privileged_manager_1.alias = 'test.privileged_manager_1'
  privileged_manager_1.email = 'test.privileged_manager_1.@test.pmbot.com'
  privileged_manager_1.info = 'test user: privileged_manager_1'
  privileged_manager_1.group = privilegedManagerGroup
  privileged_manager_1.save()
  
  # managers, one for a single project to manage, another to manage 2 more projects
  manager_1 = Account()
  manager_1.alias = 'test.manager_1'
  manager_1.email = 'test.manager_1.@test.pmbot.com'
  manager_1.info = 'test user: manager_1'
  manager_1.group = managerGroup
  manager_1.save()
  
  manager_2 = Account()
  manager_2.alias = 'test.manager_2'
  manager_2.email = 'test.manager_2.@test.pmbot.com'
  manager_2.info = 'test user: manager_2'
  manager_2.group = managerGroup
  manager_2.save()
  
  # privileged members aka leads
  privileged_member_1 = Account()
  privileged_member_1.alias = 'test.privileged_member_1'
  privileged_member_1.email = 'test.privileged_member_1.@test.pmbot.com'
  privileged_member_1.info = 'test user: privileged_member_1'
  privileged_member_1.group = privilegedMemberGroup
  privileged_member_1.save()
  
  privileged_member_2 = Account()
  privileged_member_2.alias = 'test.privileged_member_2'
  privileged_member_2.email = 'test.privileged_member_2.@test.pmbot.com'
  privileged_member_2.info = 'test user: privileged_member_2'
  privileged_member_2.group = privilegedMemberGroup
  privileged_member_2.save()
  
  # members - developers
  member_1 = Account()
  member_1.alias = 'test.member_1'
  member_1.email = 'test.member_1.@test.pmbot.com'
  member_1.info = 'test user: member_1'
  member_1.group = memberGroup
  member_1.save()
  
  member_2 = Account()
  member_2.alias = 'test.member_2'
  member_2.email = 'test.member_2.@test.pmbot.com'
  member_2.info = 'test user: member_2'
  member_2.group = memberGroup
  member_2.save()
  
  member_3 = Account()
  member_3.alias = 'test.member_3'
  member_3.email = 'test.member_3.@test.pmbot.com'
  member_3.info = 'test user: member_3'
  member_3.group = memberGroup
  member_3.save()
  
  member_4 = Account()
  member_4.alias = 'test.member_4'
  member_4.email = 'test.member_4.@test.pmbot.com'
  member_4.info = 'test user: member_4'
  member_4.group = memberGroup
  member_4.save()
  
  member_5 = Account()
  member_5.alias = 'test.member_5'
  member_5.email = 'test.member_5.@test.pmbot.com'
  member_5.info = 'test user: member_5'
  member_5.group = memberGroup
  member_5.save()
  
  
  
  ### PROJECT ROLES
  managerRole = Role()
  managerRole.alias = Role.ROLE_MANAGER
  managerRole.title = 'Manager'
  managerRole.info = 'Responsibilities: order, schedules, resources'
  managerRole.save()
  
  leaderRole = Role()
  leaderRole.alias = Role.ROLE_LEADER
  leaderRole.title = 'Leader'
  leaderRole.info = 'Responsibilities: perfectionism, inspiration, research'
  leaderRole.save()
  
  defaultRole = Role()
  defaultRole.alias = Role.ROLE_DEFAULT
  defaultRole.title = 'Default'
  defaultRole.info = 'Responsibilities: subordination, compliance, dedication'
  defaultRole.save()
  
  
  
  ### PROJECTS
  project_1 = Project()
  project_1.alias = 'TEST/PROJECT_1'
  project_1.title = 'project_1'
  project_1.info = 'test project: project_1'
  project_1.save()
  
  project_1_component_1 = Component()
  project_1_component_1.project = project_1
  project_1_component_1.alias = 'ONE'
  project_1_component_1.title = 'First'
  project_1_component_1.info = 'test component: project_1_component_1'
  project_1_component_1.save()
  
  project_1_membership_1 = Membership()
  project_1_membership_1.project = project_1
  project_1_membership_1.account = administrator_1
  project_1_membership_1.role = defaultRole
  project_1_membership_1.save()
  
  project_2 = Project()
  project_2.alias = 'TEST/PROJECT_2'
  project_2.title = 'project_2'
  project_2.info = 'test project: project_2'
  project_2.save()
  
  project_2_component_1 = Component()
  project_2_component_1.project = project_2
  project_2_component_1.alias = 'ONE'
  project_2_component_1.title = 'First'
  project_2_component_1.info = 'test component: project_2_component_1'
  project_2_component_1.save()
  
  project_2_component_2 = Component()
  project_2_component_2.project = project_2
  project_2_component_2.alias = 'TWO'
  project_2_component_2.title = 'Second'
  project_2_component_2.info = 'test component: project_2_component_2'
  project_2_component_2.save()
  
  project_2_membership_1 = Membership()
  project_2_membership_1.project = project_2
  project_2_membership_1.account = manager_1
  project_2_membership_1.role = managerRole
  project_2_membership_1.save()
  
  project_2_membership_2 = Membership()
  project_2_membership_2.project = project_2
  project_2_membership_2.account = privileged_member_1
  project_2_membership_2.role = leaderRole
  project_2_membership_2.save()
  
  project_2_membership_3 = Membership()
  project_2_membership_3.project = project_2
  project_2_membership_3.account = member_1
  project_2_membership_3.role = defaultRole
  project_2_membership_3.save()
  
  project_2_membership_4 = Membership()
  project_2_membership_4.project = project_2
  project_2_membership_4.account = member_2
  project_2_membership_4.role = defaultRole
  project_2_membership_4.save()
  
  project_2_membership_5 = Membership()
  project_2_membership_5.project = project_2
  project_2_membership_5.account = member_3
  project_2_membership_5.role = defaultRole
  project_2_membership_5.save()
  
  project_3 = Project()
  project_3.alias = 'TEST/PROJECT_3'
  project_3.title = 'project_3'
  project_3.info = 'test project: project_3'
  project_3.save()
  
  project_3_component_1 = Component()
  project_3_component_1.project = project_3
  project_3_component_1.alias = 'ONE'
  project_3_component_1.title = 'First'
  project_3_component_1.info = 'test component: project_3_component_1'
  project_3_component_1.save()
  
  project_3_component_2 = Component()
  project_3_component_2.project = project_3
  project_3_component_2.alias = 'TWO'
  project_3_component_2.title = 'Second'
  project_3_component_2.info = 'test component: project_3_component_2'
  project_3_component_2.save()
  
  project_3_component_3 = Component()
  project_3_component_3.project = project_3
  project_3_component_3.alias = 'THREE'
  project_3_component_3.title = 'Third'
  project_3_component_3.info = 'test component: project_3_component_3'
  project_3_component_3.save()
  
  project_3_membership_1 = Membership()
  project_3_membership_1.project = project_3
  project_3_membership_1.account = manager_1
  project_3_membership_1.role = managerRole
  project_3_membership_1.save()
  
  project_3_membership_2 = Membership()
  project_3_membership_2.project = project_3
  project_3_membership_2.account = privileged_member_2
  project_3_membership_2.role = leaderRole
  project_3_membership_2.save()
  
  project_3_membership_3 = Membership()
  project_3_membership_3.project = project_3
  project_3_membership_3.account = member_1
  project_3_membership_3.role = defaultRole
  project_3_membership_3.save()
  
  project_3_membership_4 = Membership()
  project_3_membership_4.project = project_3
  project_3_membership_4.account = member_4
  project_3_membership_4.role = defaultRole
  project_3_membership_4.save()
  
  project_4 = Project()
  project_4.alias = 'TEST/PROJECT_4'
  project_4.title = 'project_4'
  project_4.info = 'test project: project_4'
  project_4.save()
  
  project_4_component_1 = Component()
  project_4_component_1.project = project_4
  project_4_component_1.alias = 'ONE'
  project_4_component_1.title = 'First'
  project_4_component_1.info = 'test component: project_4_component_1'
  project_4_component_1.save()
  
  project_4_component_2 = Component()
  project_4_component_2.project = project_4
  project_4_component_2.alias = 'TWO'
  project_4_component_2.title = 'Second'
  project_4_component_2.info = 'test component: project_4_component_2'
  project_4_component_2.save()
  
  project_4_component_3 = Component()
  project_4_component_3.project = project_4
  project_4_component_3.alias = 'THREE'
  project_4_component_3.title = 'Third'
  project_4_component_3.info = 'test component: project_4_component_3'
  project_4_component_3.save()
  
  project_4_component_4 = Component()
  project_4_component_4.project = project_4
  project_4_component_4.alias = 'FOUR'
  project_4_component_4.title = 'Fourth'
  project_4_component_4.info = 'test component: project_4_component_4'
  project_4_component_4.save()
  
  project_4_membership_1 = Membership()
  project_4_membership_1.project = project_4
  project_4_membership_1.account = privileged_manager_1
  project_4_membership_1.role = managerRole
  project_4_membership_1.save()
  
  project_4_membership_2 = Membership()
  project_4_membership_2.project = project_4
  project_4_membership_2.account = manager_2
  project_4_membership_2.role = managerRole
  project_4_membership_2.save()
  
  project_4_membership_3 = Membership()
  project_4_membership_3.project = project_4
  project_4_membership_3.account = privileged_member_2
  project_4_membership_3.role = leaderRole
  project_4_membership_3.save()
  
  project_4_membership_4 = Membership()
  project_4_membership_4.project = project_4
  project_4_membership_4.account = member_2
  project_4_membership_4.role = defaultRole
  project_4_membership_4.save()
  
  project_4_membership_5 = Membership()
  project_4_membership_5.project = project_4
  project_4_membership_5.account = member_5
  project_4_membership_5.role = defaultRole
  project_4_membership_5.save()
  
  data = 'all the test items have been created'
  
  return render_template( 'test/migration.html', title=title, data=data )



@app.route( '/test/migration/exception', methods=['GET', 'POST'] )
def test_migration_exception():
  title = 'Testing | exception'
  
  ### The Imports
  from application import db
  from models.feedback import Feedback
  from models.translation import Translation
  from models.variable import Variable
  from models.account import Account, Preference, Group
  from models.project import Project, Component, Membership, Role
  from models.report import Report
  
  raise Exception('testing migration')
