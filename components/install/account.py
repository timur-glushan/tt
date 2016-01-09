#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

@app.install('install_account_db')
def install_account_db():
  """Create the DB schema for Account and Group models"""
  from application import db
  from models.account import Account, Group
  
  db.create_all()



@app.install('install_group_data')
def install_group_data():
  """Create all the required groups if not defined"""
  from application import db
  from models.account import Account, Group
  from models.project import Project, Membership
  
  groupList = [
    {
      'alias': Group.GROUP_ADMINISTRATOR,
      'title': 'Administrator',
      'info': """Administrators are the unstoppable guys - everything is permitted"""
    },
    {
      'alias': 'privileged_manager',
      'title': 'Privileged Manager',
      'info': """Privileged Managers are almost as cool as the administrators"""
    },
    {
      'alias': 'manager',
      'title': 'Manager',
      'info': """Managers have some extra features for management over the accounts and projects"""
    },
    {
      'alias': 'privileged_member',
      'title': 'Privileged Member',
      'info': """Privileged Members have just few extra features"""
    },
    {
      'alias': Group.GROUP_DEFAULT,
      'title': 'Member',
      'info': """Members can submit reports and watch their own stats"""
    }
  ]
  
  for groupItem in groupList:
    group = Group.query.filter_by(alias=groupItem['alias']).first()
    if not group:
      group = Group()
      group.alias = groupItem['alias']
      group.title = groupItem['title']
      group.info = groupItem['info']
      group.save()



@app.install('install_account_data')
def install_account_data():
  """Create all the required accounts if not defined"""
  from application import db
  from models.account import Account, Group
  
  accountList = [
    {
      'alias': 'timur.glushan',
      'first_name': 'Timur',
      'last_name': 'Glushan',
      'email': 'timur.glushan@p-product.com',
      'info': None,
      'group': Group.query.filter_by(alias='administrator').first()
    }
  ]
  
  for accountItem in accountList:
    account = Account.query.filter_by(alias=accountItem['alias']).first()
    if not account:
      account = Account()
      account.alias = accountItem['alias']
      account.first_name = accountItem['first_name']
      account.last_name = accountItem['last_name']
      account.email = accountItem['email']
      account.info = accountItem['info']
      account.group = accountItem['group']
      account.save()
