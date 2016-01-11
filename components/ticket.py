#!/usr/bin/python
# -*- coding: utf-8 -*-

from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, Response, render_template, flash
import urllib
import datetime
import time
import json

#helpers section
def _ticketActivityHeader(**kwargs):
  from models.account import Account
  from models.project import Project, Component, Membership, Label
  from helpers.account import AccountHelper
  from helpers.project import ProjectHelper
  
  header = {}
  
  if kwargs.has_key('created_start_date'):
    header['created_start_date'] = kwargs['created_start_date']
  else:
    header['created_start_date'] = request.values.get('created_start_date', g._constant()['DATE']['MONTH'])
  #start_date = datetime.datetime.strptime(start_datestring, '%Y-%m-%d')
  #start_ts = start_date.strftime('%s')
  
  if kwargs.has_key('created_end_date'):
    header['created_end_date'] = kwargs['created_end_date']
  else:
    header['created_end_date'] = request.values.get('created_end_date', g._constant()['DATE']['TODAY'])
  #end_date = datetime.datetime.strptime(end_datestring, '%Y-%m-%d')
  #end_ts = end_date.strftime('%s')
  
  header['eccounts'] = []
  if kwargs.has_key('accounts'):
    header['accounts'] = kwargs['accounts']
  elif app.access('profile', action='administer'):
    header['accounts'] = AccountHelper.listAccounts()
  elif app.access('profile', action='list'):
    header['accouts'] = AccountHelper.listActiveAccounts()
  elif app.access('profile', action='read', account=g.account):
    header['accounts'] = [g.account]
  else:
    header['accounts'] = []

  header['assignees'] = []
  if kwargs.has_key('assignees'):
    header['assignees'] = kwargs['assignees']
  elif app.access('profile', action='administer'):
    header['assignees'] = AccountHelper.listAccounts()
  elif app.access('profile', action='list'):
    header['assignees'] = AccountHelper.listActiveAccounts()
  elif app.access('profile', action='read', account=g.account):
    header['assignees'] = [g.account]
  else:
    header['assignees'] = []
  
  header['skip_projects'] = ProjectHelper.listVacationProjects()
  
  header['projects'] = []
  if kwargs.has_key('projects'):
    header['projects'] = kwargs['projects']
  elif app.access('project', action='administer'):
    header['projects'] = ProjectHelper.listAllComponents()
  elif app.access('project', action='list'):
    header['projects'] = ProjectHelper.listAllActiveComponents()
  elif app.access('membership', account=g.account):
    header['projects'] = ProjectHelper.listAllComponentsForMember(account=g.account)
  else:
    header['projects'] = []
  
  return header



# permissions section
@app.permission('ticket')
def permission_ticket(action=None, ticket=None):
  """Ticket CRUD check for signed in account. 
  @description Check if a signed in account has a specified action for a given ticket. 
  @param <str>action, valid values ["list", "administer", "create", "read", "update", "delete"]
  @param <Ticket>ticket (optional) 
  @return bool 
  @example Call as app.access('ticket', action='update', ticket=TASk)"""
  from models.ticket import Ticket
  
  if not action:
    raise Exception('Ticket CRUD permission: action missing')
  
  if not ticket and not action in ['list', 'administer', 'create', 'delete']:
    raise Exception('Ticket CRUD permission: report required for action "'+action+'"')
  
  if action == 'list':
    return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager', 'privileged_member', 'member'])
  if action == 'administer':
    return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager', 'privileged_member', 'member'])
  elif action == 'create':
    return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager', 'privileged_member', 'member'])
  elif action == 'read':
    if ticket.status & ticket.STATUS_DELETED:
      return app.access('group', group_alias=['administrator', 'privileged_manager'])
    else:
      return True
  elif action == 'update':
    if ticket.status & report.STATUS_DELETED:
      return app.access('group', group_alias=['administrator', 'privileged_manager'])
    elif ticket.account.id == g.account.id or ticket.assignee.id == g.account.id:
      return True
    else:
      return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager'])
  elif action == 'delete':
    return app.access('group', group_alias=['administrator', 'privileged_manager'])
  else:
    raise Exception('Ticket CRUD permission: incorrect action "'+action+'", must be ["list", "administer", "create", "read", "update", "delete"]')



@app.permission('ticket_activity')
def permission_ticket_activity(account=None):
  from helpers.project import ProjectHelper
  
  """Accounts' membership check for signed in account. 
  @description Check if a signed in account is permitted to see the given account's membership activity or totals. 
  @param <Account>account (optional) 
  @return bool 
  @example Call as app.access('membership', account=ACCOUNT)"""
  if not account:
    return app.access('profile', action='list') and app.access('report', action='list')# and app.access('project', action='list')
  else:
    return ProjectHelper.profileHasSubordinate(g.account, account) or app.access('membership', account=account)



# request hooks section
@app.before_request
def session_before_request():
  pass

@app.teardown_request
def session_teardown_request( exception ):
  pass



#context processors section
@app.context_processor
def report_context_processor():
  return {}



@app.route('/ticket_activity/data', methods=['POST'])
@app.login_required
def ticket_activity_data():
  from models.account import Account
  from models.project import Project
  from models.ticket import Ticket
  from helpers.ticket import TicketHelper
  import time
  
  if not app.access('ticket_activity', account=g.account):
    return Response(json.dumps({'status':403, 'description':'Not authorized', 'errors':['not authorized']}), mimetype='application/json')
  
  header = _ticketActivityHeader()
  
  filters = {}
  filters['project'] = request.values.getlist('filter[project]') or [project.id for project in header['projects']]
  filters['component'] = request.values.getlist('filter[component]') or [component.id for component in header['components']]
  filters['version'] = request.values.getlist('filter[version]') or [version.id for version in header['versions']]
  filters['priority'] = request.values.getlist('filter[priority]') or [priority.id for priority in header['priorities']]
  filters['resolution'] = request.values.getlist('filter[resolution]') or [resolution.id for resolution in header['resolutions']]
  # uncomment this line if you need to make sure that the employees would see all reports, whether they are members or not
  #filters['project'] = request.values.getlist('filter[project]') or None
  filters['account'] = request.values.getlist('filter[account]') or [account.id for account in header['account']]
  filters['assignee'] = request.values.getlist('filter[assignee]') or [assignee.id for assignee in header['assignee']]
  filters['account'] = request.values.getlist('filter[account]') or [account.id for account in header['account']]
  filters['created_start_date'] = header['created_start_date']
  filters['created_end_date'] = header['created_end_date']
  
  header['tickets'] = []
  if app.access('ticket', action='administer'):
    header['tickets'] = TicketHelper.listTickets(
      created_start_date=filters['created_start_date'],
      created_end_date=filters['created_end_date'],
      accounts=filters['account'],
      assignees=filters['assignee'],
      components=filters['project'],
      versions=filters['versions'],
      priorities=filters['priorities'],
      resolutions=filters['resolutions']
    )
  elif app.access('ticket', action='list'):
    header['tickets'] = ReportHelper.listActiveTickets(
      created_start_date=filters['created_start_date'],
      created_end_date=filters['created_end_date'],
      accounts=filters['accounts'],
      assignees=filtesr['assignees'],
      components=filters['project'],
      versions=filters['versions'],
      priorities=filters['priorities'],
      resolutions=filters['resolutions']
    )
  else:
    header['reports'] = []
  
  for ticketIndex in range(len(header['reports'])):
    ticketDict = {
      'id': header['reports'][reportIndex].id,
      'offline': header['reports'][reportIndex].offline,
      'due_date': header['reports'][reportIndex].due_date,
      'duration': header['reports'][reportIndex].duration,
      'summary': header['reports'][reportIndex].summary,
      'project_id': header['reports'][reportIndex].project_id,
      'component_id': header['reports'][reportIndex].component_id,
      'account_id': header['reports'][reportIndex].account_id,
      'reporter_id': header['reports'][reportIndex].reporter_id,
      'created': header['reports'][reportIndex].created,
      'modified': header['reports'][reportIndex].modified,
      'status': header['reports'][reportIndex].status,
      'deleted': (header['reports'][reportIndex].status & Report.STATUS_DELETED > 0)
    }
    ticketDict['labels'] = {
      'date': header['tickets'][ticketIndex].created,
      'path': header['tickets'][ticketIndex].path,
      'account': header['tickets'][ticketIndex].account.__str__(),
      'assignee': header['tickets'][ticketIndex].assignee.__str__(),
      'project': header['tickets'][ticketIndex].project.__str__(),
      'component': header['tickets'][ticketIndex].component.__str__(),
      'version': header['tickets'][ticketIndex].version.__str__(),
      'priority': header['tickets'][ticketIndex].priority.__str__(),
      'resolution': header['tickets'][ticketIndex].resolution.__str__(),
    }
    ticketDict['links'] = {
      'edit': url_for('ticket_edit', ticket_id=urllib.quote_plus(str(header['tickets'][ticketIndex].id))),
      'delete': url_for('ticket_delete', ticket_id=urllib.quote_plus(str(header['ticket'][ticketIndex].id))),
      'account': url_for('profile_view', account_id=urllib.quote_plus(str(header['tickets'][ticketIndex].account_id))),
      'assignee': url_for('profile_view', account_id=urllib.quote_plus(str(header['tickets'][ticketIndex].assignee_id))),
      'project': url_for('project_view', project_id=urllib.quote_plus(str(header['tickets'][ticketIndex].project_id))),
      'component': url_for('project_view', project_id=urllib.quote_plus(str(header['tickets'][ticketIndex].project_id)))
    }
    
    header['tickets'][ticketIndex] = ticketDict
  
  header['accounts'] = [account.alias for account in header['accounts']]
  header['assignees'] = [account.alias for account in header['assignees']]
  header['projects'] = [component.path for component in header['projects']]
  header['skip_projects'] = [component.path for component in header['skip_projects']]
  
  return Response(json.dumps({'status':200, 'description':'OK', 'data':header, 'filters':filters, 'errors':[]}), mimetype='application/json')



@app.route('/tickets/', methods=['GET','POST'])
@app.login_required
def ticket_index():
  from models.account import Account
  from models.project import Project, Component, Version
  from models.ticket import Ticket, Priority, Resolution
  from helpers.ticket import TicketHelper
  
  if not app.access('ticket_activity'):
    abort(403)
  
  #header = _ticketActivityHeader()
  options = {
    'account_list': Account.query.order_by(Account.first_name, Account.last_name, Account.alias).all(),
    'component_list': Component.query.order_by(Component.alias).all(),
    'version_list': Version.query.order_by(Version.created.desc()).all(),
    'priority_list': Priority.query.order_by(Priority.weight.desc()).all(),
    'resolution_list': Resolution.query.order_by(Resolution.weight.desc()).all()
  }

  values = {}
  values['account_id'] = request.values.getlist('filter_account_id', [account.id for account in options['account_list']])
  values['assignee_id'] = request.values.getlist('filter_assignee_id', [account.id for account in options['account_list']])
  values['component_id'] = request.values.getlist('filter_component_id', [component.id for component in options['component_list']])
  values['version_id'] = request.values.getlist('filter_version_id', [version.id for version in options['version_list']])
  values['priority_id'] = request.values.getlist('filter_priority_id', [priority.id for priority in options['priority_list']])
  values['resolution_id'] = request.values.getlist('filter_resolution_id', [resolution.id for resolution in options['resolution_list']])
  values['created_since'] = request.values.get('created_since', g._constant()['DATE']['MONTH'])
  values['created_by'] = request.values.get('created_by', g._constant()['DATE']['TODAY'])
  values['csrf_token'] = request.values.get('csrf_token')

  fields = ['id', 'alias', 'title', 'summary', 'component', 'priority', 'resolution', 'assigneee', 'account']
  
  title = g._t('tickets')
  
  breadcrumbs = (
    (title, "#"),
  )

  if app.access('ticket', action='administer'):
    ticket_list = TicketHelper.listTickets(accounts=values['account_id'], assignees=values['assignee_id'], components=values['component_id'], versions=values['version_id'], priorities=values['priority_id'], resolutions=values['resolution_id'], created_since=values['created_since'], created_by=values['created_by'])
  else:
    ticket_list = TicketHelper.listActiveTickets(accounts=values['account_id'], assignees=values['assignee_id'], components=values['component_id'], versions=values['version_id'], priorities=values['priority_id'], resolutions=values['resolution_id'], created_since=values['created_since'], created_by=values['created_by'])
  
  return render_template('ticket/ticket.index.html', title=title, breadcrumbs=breadcrumbs, ticket_list=ticket_list, options=options, values=values, fields=fields)



@app.route('/ticket/submit', methods=['GET', 'POST'])
@app.route('/ticket/<ticket_id>/edit', methods=['GET', 'POST'])
@app.login_required
def ticket_edit(ticket_id=None):
  from models.account import Account
  from models.project import Project, Component
  from models.ticket import Ticket
  
  account = g.account
  
  ticket = None
  if not ticket_id:
    ticket = Ticket()
    ticket.status = Ticket.STATUS_ACTIVE
    if not app.access('ticket', action='create'):
      if request.is_ajax:
        return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
      else:
        abort(403)
  else:
    ticket_id = urllib.unquote_plus(ticket_id)
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    if not ticket:
      if request.is_ajax:
        return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['ticket not found']}), mimetype='application/json')
      else:
        abort(404)
    elif not app.access('ticket', action='update', ticket=ticket):
      if request.is_ajax:
        return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
      else:
        abort(403)
  
  title = g._t('ticket submit')
  
  validationErrors = []
  if (request.method == 'POST' and request.values.get('csrf_token', None)) or request.values.get('no_validate', None):
    ticket.account_id = g.account.id
    
    component_id = request.values.get('ticket_component_id', None)
    if component_id:
      component = Component.query.filter_by(id=component_id).first()
      if component:
        ticket.component_id = component.id
        ticket.project_id = component.project_id

    ticket.status = int(request.form.get('ticket_status', ticket.status).strip())
    ticket.account_id = account.id

    assignee_id = request.values.get('ticket_assignee_id', None)
    if assignee_id:
      assignee = Account.query.filter_by(id=assignee_id).first()
      if assignee:
        ticket.assignee_id = assignee.id

    version_id = request.values.get('ticket_version_id', None)
    if version_id:
      version = Version.query.filter_by(id=version_id).first()
      if version:
        ticket.version_id = version.id

    priority_id = request.values.get('ticket_priority_id', None)
    if priority_id:
      priority = Priority.query.filter_by(id=priority_id).first()
      if priority:
        ticket.priority_id = priority.id

    resolution_id = request.values.get('ticket_resolution_id', None)
    if resolution_id:
      resolution = Resolution.query.filter_by(id=resolution_id).first()
      if resolution:
        ticket.resolution_id = resolution.id

    validationErrors = ticket.validate()
    if request.values.get('no_validate', None):
      status = 200
      description = 'OK'
    elif not validationErrors:
      if not ticket_id:
        ticket.alias = TicketHelper.getAlias(component_id)
      ticket.save()
      
      status = 200
      description = 'OK'
      if request.is_ajax:
        return Response(json.dumps({
          'html':render_template('_popup.html', title=g._t( 'ticket submit success' ), message=g._t( 'ticket submit success message' ), javascript="""setTimeout(function(){$('form[name=statistics-form]').submit(); $('form[name=filter-form]').submit();}, 300);"""),
          'status':status,
          'description':description,
          'errors':validationErrors
        }), mimetype='application/json')
      else:
        flash( g._t( 'ticket submit success' ) )
        return redirect( url_for('ticket_index') )
    else:
      status = 400
      description = 'Bad request'
  else:
    status = 200
    description = 'OK'
    validationErrors = []
  
  """
  If the report exists, but the account is no longer a member of the project, 
  we avoid an ability to change the project by keeping the only project option available
  """
  header = _ticketActivityHeader()
  projectList = header['projects']
  if ticket.id and ticket.component and not ticket.component in projectList:
    projectList = [ticket.component]
  
  if request.is_ajax:
    htmlContent = render_template('ticket/ticket.edit-popup.html', account=account, title=title, ticket=ticket, errors=validationErrors, projectList=projectList)
    return  Response(json.dumps({'html':htmlContent, 'status':status, 'description':description, 'errors':validationErrors}), mimetype='application/json')
  else:
    htmlContent = render_template('report/report.edit.html', account=account, title=title, ticket=ticket, errors=validationErrors, projectList=projectList)
    return htmlContent



@app.route('/ticket/<ticket_id>/delete', methods=['GET', 'POST'])
@app.login_required
def ticket_delete(ticket_id):
  from models.account import Account
  from models.ticket import Ticket
  
  account_id = g.accout.id
  account = g.account
  
  if not account:
    if request.is_ajax:
      return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['user not found']}), mimetype='application/json')
    else:
      abort(404)
  elif not app.access('ticket_activity', account=account):
    if request.is_ajax:
      return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
    else:
      abort(403)
  
  ticket_id = urllib.unquote_plus(ticket_id)
  ticket = Ticket.query.filter_by(id=ticket_id).first()
  
  if not ticket:
    if request.is_ajax:
      return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['ticket not found']}), mimetype='application/json')
    else:
      abort(404)
  elif not app.access('report', action='update', ticket=ticket):
    if request.is_ajax:
      return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
    else:
      abort(403)
  
  title = g._t('ticket delete')
  errors = []
  
  if request.method == 'POST' and request.values.get('csrf_token', None):
    if request.form.get('action') == 'ticket_action_remove_permanently':
      if not app.access('ticket', action='delete', ticket=ticket):
        if request.is_ajax:
          return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
        else:
          abort(403)
      ticket.delete()
      success_title = g._t('ticket remove permanently success')
      success_message= g._t('ticket remove permanently success message')
    elif request.form.get('action') == 'ticket_action_delete':
      ticket.status = ticket.status | ticket.STATUS_DELETED
      ticket.save()
      success_title = g._t('ticket delete success')
      success_message= g._t('ticket delete success message')
    status = 200
    description = 'OK'
    
    if request.is_ajax:
      return Response(json.dumps({
        'html':render_template('_popup.html', title=success_title, message=success_message, javascript="""setTimeout(function(){$('form[name=statistics-form]').submit(); $('form[name=statistics-form]').submit(); $('form[name=filter-form]').submit();;}, 300);"""),
        'status':status,
        'description':description,
        'errors':errors
      }), mimetype='application/json')
    else:
      flash(success_message)
      return redirect(url_for('ticket_index'))
  
  status = 200
  description = 'OK'
  if request.is_ajax:
    htmlContent = render_template('report/report.delete-popup.html', account=account, title=title, report=report, errors=errors)
    return  Response(json.dumps({'html':htmlContent, 'status':status, 'description':description, 'errors':errors}), mimetype='application/json')
  else:
    htmlContent = render_template('report/report.delete.html', account=account, title=title, report=report, errors=errors)
    return htmlContent



@app.route('/ticket/delete_multiple', methods=['GET', 'POST'])
@app.login_required
def ticket_delete_multiple():
  from models.account import Account
  from models.ticket import Ticket

  account_id=g.account.id
  account=g.account
  
  if not account:
    if request.is_ajax:
      return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['user not found']}), mimetype='application/json')
    else:
      abort(404)
  elif not app.access('ticket_activity', account=account):
    if request.is_ajax:
      return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
    else:
      abort(403)
  
  ticketIdList = request.values.getlist('ticket[id]')
  ticketList = Ticket.query.filter(Ticket.id.in_(ticketIdList)).all()
  
  for ticket in ticketList:
    if not ticket:
      if request.is_ajax:
        return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['ticket not found']}), mimetype='application/json')
      else:
        abort(404)
    elif not app.access('ticket', action='update', ticket=ticket):
      if request.is_ajax:
        return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
      else:
        abort(403)
  
  title = g._t('ticket delete') + ' ('+str(len(ticketList))+')'
  errors = []
  
  if request.method == 'POST' and request.values.get('csrf_token', None):
    if request.form.get('action') == 'ticket_action_remove_permanently':
      if not app.access('ticket', action='delete'):
        if request.is_ajax:
          return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
        else:
          abort(403)
    
    if request.form.get('action') == 'ticket_action_remove_permanently':
      for ticket in ticketList:
        ticket.delete()
      success_title = g._t('ticket remove permanently success')
      success_message= g._t('ticket remove permanently success message') + ' ('+str(len(ticketList))+')'
    elif request.form.get('action') == 'ticket_action_delete':
      for ticket in ticketList:
        ticket.status = ticket.status | ticket.STATUS_DELETED
        ticket.save()
      success_title = g._t('ticket delete success')
      success_message= g._t('ticket delete success message') + ' ('+str(len(ticketList))+')'
    status = 200
    description = 'OK'
    
    if request.is_ajax:
      return Response(json.dumps({
        'html':render_template('_popup.html', title=success_title, message=success_message, javascript="""setTimeout(function(){$('form[name=statistics-form]').submit(); $('form[name=statistics-form]').submit(); $('form[name=filter-form]').submit();;}, 300);"""),
        'status':status,
        'description':description,
        'errors':errors
      }), mimetype='application/json')
    else:
      flash(success_message)
      return redirect(url_for('ticket_index'))
  
  status = 200
  description = 'OK'
  if request.is_ajax:
    htmlContent = render_template('ticket/ticket.delete_multiple-popup.html', account=account, title=title, ticketList=ticketList, errors=errors)
    return  Response(json.dumps({'html':htmlContent, 'status':status, 'description':description, 'errors':errors}), mimetype='application/json')
  else:
    htmlContent = render_template('ticket/ticket.delete_multiple.html', account=account, title=title, ticketList=ticketList, errors=errors)
    return htmlContent
