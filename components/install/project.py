#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

@app.install('install_project_db')
def install_project_db():
  """Create the DB schema for Account and Group models"""
  from application import db
  from models.project import Project, Component, Label, Membership, Role
  
  db.create_all()



@app.install('install_role_data')
def install_role_data():
  """Create all the required roles if not defined"""
  from application import db
  from models.project import Role
  
  roleList = [
    {
      'alias': Role.ROLE_MANAGER,
      'title': 'Manager',
      'info': """Responsibilities: order, schedules, resources"""
    },
    {
      'alias': Role.ROLE_LEADER,
      'title': 'Leader',
      'info': """Responsibilities: perfectionism, inspiration, research"""
    },
    {
      'alias': Role.ROLE_DEFAULT,
      'title': 'Default',
      'info': """Responsibilities: subordination, compliance, dedication"""
    }
  ]
  
  for roleItem in roleList:
    role = Role.query.filter_by(alias=roleItem['alias']).first()
    if not role:
      role = Role()
      role.alias = roleItem['alias']
      role.title = roleItem['title']
      role.info = roleItem['info']
      role.save()



@app.install('install_project_data')
def install_project_data():
  """Create all the required projects if not defined"""
  from application import db
  from models.project import Project, Component, Label
  
  projectList = [
    {
      'alias': 'MGM',
      'title': 'Management records',
      'info': None,
      'components': [
        {
          'alias': 'VAC',
          'title': 'Vacation',
          'info': None
        },
        {
          'alias': 'VAC/KZOT',
          'title': 'Vacation. Days off by KZoT',
          'info': None
        },
        {
          'alias': 'VAC/NP',
          'title': 'Vacation. Unpaid Leave',
          'info': None
        },
        {
          'alias': 'VAC/EDU',
          'title': 'Vacation. Education',
          'info': None
        }
      ],
      'labels': [Label.LABEL_GENERAL, Label.LABEL_VACATION]
    },
    {
      'alias': 'OUT',
      'title': 'N/A Time',
      'info': """Hours sink for time that an employee was available in XMPP but was neither doing work or in stand-by""",
      'components': [],
      'labels': [Label.LABEL_GENERAL, Label.LABEL_VACATION]
    },
    {
      'alias': 'EDU',
      'title': 'Self Education',
      'info': """Self Education. Report summary is obligatory!""",
      'components': [],
      'labels': [Label.LABEL_GENERAL, Label.LABEL_INTERNAL]
    },
    {
      'alias': 'IDLE',
      'title': 'Idle Time',
      'info': """Hours sink for time that an employee is online and available but doesn't have a specific task""",
      'components': [],
      'labels': [Label.LABEL_GENERAL, Label.LABEL_INTERNAL]
    },
    {
      'alias': 'PP',
      'title': 'P-Product internal tasks',
      'info': None,
      'components': [],
      'labels': [Label.LABEL_GENERAL, Label.LABEL_INTERNAL]
    },
    {
      'alias': 'OFFICE',
      'title': 'Office Tasks',
      'info': """Shopping for Office, Psychotherapy, Interviews, etc.""",
      'components': [],
      'labels': [Label.LABEL_INTERNAL]
    }
  ]
  
  for projectItem in projectList:
    project = Project.query.filter_by(alias=projectItem['alias']).first()
    if not project:
      project = Project()
      project.alias = projectItem['alias']
      project.title = projectItem['title']
      project.info = projectItem['info']
      project.save()
  
      for componentItem in projectItem['components']:
        component = Component.query.filter_by(alias=componentItem['alias'], project=project).first()
        if not component:
          component = Component()
          component.alias = componentItem['alias']
          component.title = componentItem['title']
          component.info = componentItem['info']
          component.project = project
          component.save()
      
      for labelItem in projectItem['labels']:
        label = Label.query.filter_by(title=labelItem, project=project).first()
        if not label:
          label = Label()
          label.title = labelItem
          label.project = project
          label.save()
