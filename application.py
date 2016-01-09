#!/usr/bin/python
# -*- coding: utf-8 -*-

#requirements:
# sqlite3
# flask
# jinja2
# flask-sqlalchemy
# uuid
# wtforms
# flask-wtf
# WTForms-Alchemy



# all the imports
from __future__ import with_statement
from contextlib import closing
from optparse import OptionParser
#import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
import os

config = {
  'VERSION': '2.1.0.3'
}

def getEnvironment():
  parser = OptionParser()
  parser.add_option( '-e', '--environment', dest='environment', default='development')
  parser.add_option( '-a', '--action', dest='action', default='webapp')
  ( options, args ) = parser.parse_args()
  return type('options', (object,), {"options": options, "args": args})

def createApp():
  app = Flask( __name__ )
  app.config.from_object( 'config.' + environment.options.environment )
  app.config.update(config)
  return app

def createDB():
  #sqliteDBPath = os.path.abspath(os.path.join(os.getcwd(), 'data', 't3.db'))
  #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + sqliteDBPath
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+app.config['DATABASE']['user']+':'+app.config['DATABASE']['passwd']+'@'+app.config['DATABASE']['host']+':'+str(app.config['DATABASE']['port'] or '')+'/'+app.config['DATABASE']['schema']
  db = SQLAlchemy(app, session_options={
    #'autoflush': False,
    #'autocommit': False,
    'expire_on_commit': False
  })
  
  dbConfig = {
    'mysql': {
      'passive_updates': True,
      'cascade_all': 'all, delete, delete-orphan'
    },
    'sqlite': {
      'passive_updates': False,
      'cascade_all': 'all, delete, delete-orphan'
    },
  }
  dbConfigSet = app.config['SQLALCHEMY_DATABASE_URI'].split(':')[0]
  
  db._config = type('CustomConfiguration', (object,), dbConfig[dbConfigSet])
  
  return db



environment = getEnvironment()
app = createApp()
db = createDB()



# import system parts
#from libraries import Migration
#Migration.run()



from functools import wraps

app.permissions = {}

def login_required(f):
  """A decorator for the page callback. 
  When a page is requested, the callback will redirect to signin if not authenticated, 
  otherwise will return the page as usual"""
  from flask import request, Response, redirect, url_for, abort, g
  
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if not g.account:
      if request.is_ajax:
        return Response(json.dumps({'status':401, 'description':'Not authenticated', 'errors':['authentication required']}), mimetype='application/json')
      else:
        return redirect(url_for('session_signin', next=request.url))
    return f(*args, **kwargs)
  return decorated_function

def authorized_group(*group_alias_list):
  """A decorator for the page callback. 
  When a page is requested, the callback will drop the request to 403 if not authorized with the given callback args, 
  otherwise will return the page as usual"""
  from flask import request, redirect, url_for, abort, g
  from models.account import Account, Group
  
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      
      if not g.account:
        return redirect(url_for('session_signin', next=request.url))
      
      if not group_alias_list:
        raise Exception('Authorized group: group_alias_list missing')
      
      groupList = Group.query\
        .filter(Group.alias.in_(group_alias_list))\
        .join(Group.accounts, aliased=True)\
        .filter(Account.id==g.account.id).all()
  
      if len(groupList) > 0:
        return f(*args, **kwargs)
      
      if request.is_ajax:
        return Response(json.dumps({'status':403, 'description':'Not authorized', 'errors':['not authorized']}), mimetype='application/json')
      else:
        abort(403)
    return decorated_function
  return decorator

def access(permission_id, *arg, **kwarg):
  if not app.permissions.has_key(permission_id):
    raise Exception('Permission not found: "'+permission_id+'"')
  return app.permissions[permission_id](*arg, **kwarg)

def permission(permission_id):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      return f(*args, **kwargs)
    app.permissions[permission_id] = decorated_function
    return decorated_function
  return decorator

setattr(app, 'login_required', login_required)
setattr(app, 'authorized_group', authorized_group)
setattr(app, 'access', access)
setattr(app, 'permission', permission)



app.installs = []

def install(install_id):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      return f(*args, **kwargs)
    app.installs.append((install_id, decorated_function))
    return decorated_function
  return decorator

setattr(app, 'install', install)



app.updates = {}

def update(update_version, update_id):
  update_version = str(update_version)
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      return f(*args, **kwargs)
    if not app.updates.has_key(update_version):
      app.updates[update_version] = []
    app.updates[update_version].append((update_id, decorated_function))
    return decorated_function
  return decorator

setattr(app, 'update', update)



#context processors section
@app.context_processor
def permission_context_processor():
  return dict(access=access)

@app.permission('authenticated')
def permission_authenticated(account=None):
  """Check whether the account session is authenticated. 
  If an account argument is provided - check whether the account is the current session account
  @param <Account>account (optional)
  @return bool
  @example Call as app.access('authenticated'), app.access('authenticated', account=account)"""
  if g.account and g.account.id:
    if account and account.id:
      return g.account.id == account.id
    else:
      return True
  else:
    return False

@app.permission('group')
def permission_group(account=None, group_alias=[]):
  """Group check for a given account or signed in account. 
  @description Check if a given account_id has a role_id defined. 
  @param <str>account_id, default=g.account.id 
  @param <str>role_id | <list><str>group_alias 
  @return bool 
  @example Call as app.access('group', account_id=ACCOUNT_ID, group_alias=GROUP_ALIAS)"""
  from flask import g
  from models.account import Group
  
  if not group_alias:
    raise Exception('Group check: group_alias missing')
  
  if not account:
    account=g.account
  
  if not type(group_alias) in (list, tuple):
    group_alias = [group_alias]
  
  groupList = Group.query\
    .filter(Group.alias.in_(group_alias))\
    .join(Group.accounts, aliased=True)\
    .filter(Account.id==account.id).all()
  
  return len(groupList) > 0



if environment.options.action == 'test':
  from components.test.migration import *
elif environment.options.action == 'install':
  from components.install.index import *
  #from components.install.dbdesign import *
  #from components.install.dbcommon import *
  #from components.install.db import *
  from components.install.account import *
  from components.install.project import *
  from components.install.report import *
  from components.install.variable import *
  from components.install.translation import *
  from components.install.feedback import *
  from components.install.migration import *
  from components.install.common import *
  from components.install.updates import *
elif environment.options.action == 'webapp':
  from components.index import *
  from components.profile import *
  from components.project import *
  from components.report import *
  from components.session import *
  from components.test.index import *
  from components.test.data import *
  from components.test.permissions import *
  from components.feedback import *
  from components.administration.index import *
  from components.administration.translation import *
  from components.administration.variable import *
else:
  raise Exception("Action argument not specified (-a, --action) \nAvailable options are: install, webapp")



# start the application
if __name__ == '__main__':
  app.run( app.config['HOST'], app.config['PORT'] )
