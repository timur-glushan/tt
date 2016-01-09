#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

@app.install('install_common_groups')
def install_common_groups():
  """Define all the required groups for accounts"""
  from models.account import Account, Group
  
  newValue = {
    Group.GROUP_ADMINISTRATOR: ['gleb.dzyuba', 'timur.glushan'],
    'privileged_manager': ['lana.ieremieva', 'nadyam', 'ivan.kupriyan', 'olya.donchenko'],
    'manager': ['mike.petruk'],
    'privileged_member': [],
    Group.GROUP_DEFAULT: ['alexander.rykanov', 'alexandr.karlin', 'alexey.golosenko', 'alexey.krivosheev', 'alexey.paschenko', 'anatolii.shevchenko', 'anatoly.maziy', 'andrew.ashmarin', 'andrew.storchous', 'andrey.dmitrenko', 'andrey.palyvoda', 'anna.zanizdra', 'anton.trubianov', 'danylo.vus', 'denis.nikiforov', 'denys.kravchenko', 'dmitriy.vukolov', 'dmitry.bondarenko', 'dmitry.dunaevsky', 'dmitry.mizuch', 'dmytro.kolomiyets', 'dmytro.shevchuk', 'dummy', 'hariton.batkov', 'igor.grankov', 'ivan.guy', 'konstantin.shulika', 'leonid.usov', 'ludmila.sadovenko', 'marina.usmanova', 'michael.kotlyar', 'oleg.voitenko', 'oleksii.miroshnychenko', 'olesya.les', 'olga.chermenets', 'pyotr.brysin', 'raed.senayh', 'rostislav.chernenko', 'sergei.gorenko', 'sergey.bykov', 'slava.miakishev', 'tymur.baksheyev', 'vadim.ovchinnikov', 'vadym.pastushenko', 'valentina.davidenko', 'vasily.kovtun', 'veronica.belous', 'vitaliy.shevchenko', 'vjacheslav.volodko', 'vladislav.nemirovskiy', 'yevgen.derkach', 'yury.mirgorodsky']
    }
  
  for groupAlias, accountList in newValue.items():
    group = Group.query.filter_by(alias=groupAlias).first()
    if group:
      for accountAlias in accountList:
        account = Account.query.filter_by(alias=accountAlias).first()
        if account:
          account.group = group
          account.save()



@app.install('install_common_holidays')
def install_common_holidays():
  """Define all the required holidays"""
  from models.variable import Variable
  
  newValue = {
    'weekdays': [5, 6],
    'monthdays': [],
    'dates': {
      '2014-01-01': 'holiday:new year',
      '2014-01-07': 'holiday:christmass',
      '2014-03-08': 'holiday:international womens day',
      '2014-03-10': 'holiday:international womens day (saturday)',
      '2014-04-20': 'holiday:easter',
      '2014-04-21': 'holiday:easter (sunday)',
      '2014-05-01': 'holiday:international workers day',
      '2014-05-02': 'holiday:international workers day',
      '2014-05-09': 'holiday:victory day',
      '2014-06-08': 'holiday:trinity',
      '2014-06-09': 'holiday:trinity (sunday)',
      '2014-06-28': 'holiday:ukrainian constitution day',
      '2014-06-30': 'holiday:ukrainian constitution day (saturday)',
      '2014-08-24': 'holiday:ukrainian independence day',
      '2014-08-25': 'holiday:ukrainian independence day (sunday)',
      },
    }
  
  variable = Variable.query.filter_by(scope='date', name='holidays').first()
  if not variable:
    variable = Variable()
    variable.scope = 'date'
    variable.name = 'holidays'
  
  variable.value = newValue
  
  variable.save()



@app.install('install_common_members')
def install_common_members():
  """Define all the required members for the corresponding projects"""
  from models.account import Account
  from models.project import Project, Component, Membership, Label, Role
  
  newMembers = {
    'ALTI': {
      'alexey.paschenko': Role.ROLE_DEFAULT,
      'michael.kotlyar': Role.ROLE_DEFAULT,
      'sergey.bykov': Role.ROLE_DEFAULT,
      'valentina.davidenko': Role.ROLE_DEFAULT,
      'vladislav.nemirovskiy': Role.ROLE_DEFAULT
    },
    'ARK/HA': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'hariton.batkov': Role.ROLE_DEFAULT,
      'andrey.dmitrenko': Role.ROLE_DEFAULT
    },
    'BD': {
      'alexey.golosenko': Role.ROLE_DEFAULT,
      'rostislav.chernenko': Role.ROLE_DEFAULT
    },
    'DARIO': {
      'mike.petruk': Role.ROLE_MANAGER,
      'timur.glushan': Role.ROLE_DEFAULT,
      'dmitry.mizuch': Role.ROLE_DEFAULT,
      'igor.grankov': Role.ROLE_DEFAULT,
      'vitaliy.shevchenko': Role.ROLE_DEFAULT,
      'andrey.dmitrenko': Role.ROLE_DEFAULT
    },
    'DARIO:IOS': {
      'anatolii.shevchenko': Role.ROLE_DEFAULT
    },
    'DARIO:3/IOS': {
      'anatolii.shevchenko': Role.ROLE_DEFAULT
    },
    'DARIO:A': {
      'danylo.vus': Role.ROLE_DEFAULT,
      'denys.kravchenko': Role.ROLE_DEFAULT,
      'oleksii.miroshnychenko': Role.ROLE_DEFAULT
    },
    'DARIO:3/A': {
      'danylo.vus': Role.ROLE_DEFAULT,
      'denys.kravchenko': Role.ROLE_DEFAULT,
      'oleksii.miroshnychenko': Role.ROLE_DEFAULT
    },
    'DARIO:B': {
      'yury.mirgorodsky': Role.ROLE_DEFAULT,
      'anna.zanizdra': Role.ROLE_DEFAULT
    },
    'DARIO:3/B': {
      'yury.mirgorodsky': Role.ROLE_DEFAULT,
      'anna.zanizdra': Role.ROLE_DEFAULT
    },
    'DARIO:WEB': {
      'yury.mirgorodsky': Role.ROLE_DEFAULT,
      'anna.zanizdra': Role.ROLE_DEFAULT,
      'oleg.voitenko': Role.ROLE_DEFAULT
    },
    'DARIO:3/WEB': {
      'yury.mirgorodsky': Role.ROLE_DEFAULT,
      'anna.zanizdra': Role.ROLE_DEFAULT,
      'oleg.voitenko': Role.ROLE_DEFAULT
    },
    'KIBOSH': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'denys.kravchenko': Role.ROLE_DEFAULT,
      'ivan.guy': Role.ROLE_DEFAULT,
      'oleksii.miroshnychenko': Role.ROLE_DEFAULT,
      'danylo.vus': Role.ROLE_DEFAULT,
      'andrey.dmitrenko': Role.ROLE_DEFAULT,
      'vitaliy.shevchenko': Role.ROLE_DEFAULT
    },
    'KIKO/TT': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'hariton.batkov': Role.ROLE_DEFAULT
    },
    'LYCOS/MSGR': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'hariton.batkov': Role.ROLE_DEFAULT,
      'anton.trubianov': Role.ROLE_DEFAULT,
      'konstantin.shulika': Role.ROLE_DEFAULT
    },
    'MYH': {
      'ivan.kupriyan': Role.ROLE_MANAGER
    },
    'MYH/MVP': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'konstantin.shulika': Role.ROLE_DEFAULT,
      'hariton.batkov': Role.ROLE_DEFAULT,
      'anton.trubianov': Role.ROLE_DEFAULT,
      'dmitry.bondarenko': Role.ROLE_DEFAULT,
      'slava.miakishev': Role.ROLE_DEFAULT,
      'alexey.krivosheev': Role.ROLE_DEFAULT,
      'ludmila.sadovenko': Role.ROLE_DEFAULT,
      'igor.grankov': Role.ROLE_DEFAULT,
      'vitaliy.shevchenko': Role.ROLE_DEFAULT
    },
    'NOKIA': {
      'timur.glushan': Role.ROLE_DEFAULT
    },
    'NOKIA/OFFICIAL': {
      'timur.glushan': Role.ROLE_DEFAULT
    },
    'PHOTO': {
      'alexandr.karlin': Role.ROLE_DEFAULT,
      'dmitry.dunaevsky': Role.ROLE_DEFAULT
    },
    'QUART': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'alexander.rykanov': Role.ROLE_DEFAULT,
      'tymur.baksheyev': Role.ROLE_DEFAULT
    },
    'TINYTAP/A': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'hariton.batkov': Role.ROLE_DEFAULT
    },
    'USTORE': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'alexander.rykanov': Role.ROLE_DEFAULT,
      'vadym.pastushenko': Role.ROLE_DEFAULT,
      'andrew.ashmarin': Role.ROLE_DEFAULT
    },
    'UVIDEO': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'alexander.rykanov': Role.ROLE_DEFAULT,
      'vadym.pastushenko': Role.ROLE_DEFAULT,
      'andrew.ashmarin': Role.ROLE_DEFAULT
    },
    'VIS': {
      'ivan.kupriyan': Role.ROLE_MANAGER,
      'andrew.ashmarin': Role.ROLE_DEFAULT
    },
    'IVIEW': {
      'lana.ieremieva': Role.ROLE_DEFAULT,
      'nadyam': Role.ROLE_DEFAULT
    },
    'MBOT': {
      'gleb.dzyuba': Role.ROLE_DEFAULT,
      'timur.glushan': Role.ROLE_DEFAULT
    },
    'OFFICE': {
      'lana.ieremieva': Role.ROLE_DEFAULT,
      'marina.usmanova': Role.ROLE_DEFAULT,
      'nadyam': Role.ROLE_DEFAULT,
      'veronica.belous': Role.ROLE_DEFAULT
    }
  }
  
  for project_alias, memberList in newMembers.items():
    if project_alias.find(':') > 0:
      project_alias, component_alias = project_alias.split(':', 1)
      project = Project.query.filter_by(alias=project_alias).first()
      component = Component.query.filter_by(project=project, alias=component_alias).first()
    else:
      project = Project.query.filter_by(alias=project_alias).first()
      component = Component.query.filter_by(project=project, alias=Component.COMPONENT_DEFAULT).first()
    
    if project:
      for account_alias, role_alias in memberList.items():
        account = Account.query.filter_by(alias=account_alias).first()
        if account:
          role = Role.query.filter_by(alias=role_alias).first() or Role.query.filter_by(alias=Role.ROLE_DEFAULT).first()
          membership = Membership.query.filter_by(project_id=project.id, component_id=component.id, account_id=account.id).first()
          if not membership:
            membership = Membership()
            membership.project_id = project.id
            membership.component_id = component.id
            membership.account_id = account.id
          membership.role_id = role.id
          membership.save()



@app.install('install_common_labels')
def install_common_labels():
  """Define all the required labels for the corresponding projects"""
  from models.project import Project, Label
  
  projectLabelList = {
    'NOKIA/OFFICIAL': [Label.LABEL_VACATION],
    'MGM': [Label.LABEL_GENERAL, Label.LABEL_VACATION],
    'OUT': [Label.LABEL_GENERAL, Label.LABEL_VACATION],
    'EDU': [Label.LABEL_GENERAL],
    'IDLE': [Label.LABEL_GENERAL],
    'PP': [Label.LABEL_GENERAL]
  }
  
  for project_alias, labelList in projectLabelList.items():
    project = Project.query.filter_by(alias=project_alias).first()
    if project:
      for labelItem in labelList:
        label = Label.query.filter_by(title=labelItem, project=project).first()
        if not label:
          label = Label()
          label.title = labelItem
          label.project = project
          label.save()
