#!/usr/bin/python
# -*- coding: utf-8 -*-

from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, Response, render_template, flash
import urllib
import datetime
import time
import json

#helpers section
def _activityHeader(**kwargs):
  from models.account import Account
  from models.project import Project, Component, Membership, Label
  from helpers.account import AccountHelper
  from helpers.project import ProjectHelper
  
  header = {}
  
  if kwargs.has_key('start_date'):
    header['start_date'] = kwargs['start_date']
  else:
    header['start_date'] = request.values.get('start_date', g._constant()['DATE']['MONTH'])
  #start_date = datetime.datetime.strptime(start_datestring, '%Y-%m-%d')
  #start_ts = start_date.strftime('%s')
  
  if kwargs.has_key('end_date'):
    header['end_date'] = kwargs['end_date']
  else:
    header['end_date'] = request.values.get('end_date', g._constant()['DATE']['TODAY'])
  #end_date = datetime.datetime.strptime(end_datestring, '%Y-%m-%d')
  #end_ts = end_date.strftime('%s')
  
  header['employees'] = []
  if kwargs.has_key('employees'):
    header['employees'] = kwargs['employees']
  elif app.access('profile', action='administer'):
    header['employees'] = AccountHelper.listAccounts()
  elif app.access('profile', action='list'):
    header['employees'] = AccountHelper.listActiveAccounts()
  elif app.access('profile', action='read', account=g.account):
    header['employees'] = [g.account]
  else:
    header['employees'] = []
  
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
@app.permission('report')
def permission_report(action=None, report=None):
  """Report CRUD check for signed in account. 
  @description Check if a signed in account has a specified action for a given report. 
  @param <str>action, valid values ["list", "administer", "create", "read", "update", "delete"]
  @param <Report>report (optional) 
  @return bool 
  @example Call as app.access('report', action='update', report=REPORT)"""
  from models.report import Report
  
  if not action:
    raise Exception('Report CRUD permission: action missing')
  
  if not report and not action in ['list', 'administer', 'create', 'delete']:
    raise Exception('Report CRUD permission: report required for action "'+action+'"')
  
  if action == 'list':
    return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager', 'privileged_member', 'member'])
  if action == 'administer':
    return app.access('group', group_alias=['administrator', 'privileged_manager'])
  elif action == 'create':
    return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager', 'privileged_member', 'member'])
  elif action == 'read':
    if report.status & report.STATUS_DELETED:
      return app.access('group', group_alias=['administrator', 'privileged_manager'])
    else:
      return True
  elif action == 'update':
    if report.status & report.STATUS_DELETED:
      return app.access('group', group_alias=['administrator', 'privileged_manager'])
    elif report.account.id == g.account.id:
      return True
    else:
      return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager'])
  elif action == 'delete':
    return app.access('group', group_alias=['administrator', 'privileged_manager'])
  else:
    raise Exception('Report CRUD permission: incorrect action "'+action+'", must be ["list", "administer", "create", "read", "update", "delete"]')



@app.permission('activity')
def permission_activity(account=None):
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



@app.route('/activity/data', methods=['POST'])
@app.login_required
def activity_data():
  from models.account import Account
  from models.project import Project
  from models.report import Report
  from helpers.report import ReportHelper
  import time
  
  if not app.access('activity', account=g.account):
    return Response(json.dumps({'status':403, 'description':'Not authorized', 'errors':['not authorized']}), mimetype='application/json')
  
  header = _activityHeader()
  
  filters = {}
  filters['project'] = request.values.getlist('filter[project]') or [project.id for project in header['projects']]
  # uncomment this line if you need to make sure that the employees would see all reports, whether they are members or not
  #filters['project'] = request.values.getlist('filter[project]') or None
  filters['employee'] = request.values.getlist('filter[employee]') or [account.id for account in header['employees']]
  filters['start_date'] = header['start_date']
  filters['end_date'] = header['end_date']
  
  header['reports'] = []
  if app.access('report', action='administer'):
    header['reports'] = ReportHelper.listReports(
      start_date=filters['start_date'],
      end_date=filters['end_date'],
      accounts=filters['employee'],
      components=filters['project']
    )
  elif app.access('report', action='list'):
    header['reports'] = ReportHelper.listActiveReports(
      start_date=filters['start_date'],
      end_date=filters['end_date'],
      accounts=filters['employee'],
      components=filters['project']
    )
  else:
    header['reports'] = []
  
  for reportIndex in range(len(header['reports'])):
    reportDict = {
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
    reportDict['labels'] = {
      'date': header['reports'][reportIndex].due_date,
      'path': header['reports'][reportIndex].path,
      'account': header['reports'][reportIndex].account.__str__(),
      'project': header['reports'][reportIndex].project.__str__(),
      'component': header['reports'][reportIndex].component.__str__()
    }
    reportDict['links'] = {
      'edit': url_for('report_edit', account_id=urllib.quote_plus(str(header['reports'][reportIndex].account_id)), report_id=urllib.quote_plus(str(header['reports'][reportIndex].id))),
      'delete': url_for('report_delete', account_id=urllib.quote_plus(str(header['reports'][reportIndex].account_id)), report_id=urllib.quote_plus(str(header['reports'][reportIndex].id))),
      'account': url_for('profile_view', account_id=urllib.quote_plus(str(header['reports'][reportIndex].account_id))),
      'project': url_for('project_view', project_id=urllib.quote_plus(str(header['reports'][reportIndex].project_id))),
      'component': url_for('project_view', project_id=urllib.quote_plus(str(header['reports'][reportIndex].project_id)))
    }
    
    header['reports'][reportIndex] = reportDict
  
  header['employees'] = [account.alias for account in header['employees']]
  header['projects'] = [component.path for component in header['projects']]
  header['skip_projects'] = [component.path for component in header['skip_projects']]
  
  return Response(json.dumps({'status':200, 'description':'OK', 'data':header, 'filters':filters, 'errors':[]}), mimetype='application/json')



@app.route('/activity/statistics/<account_id>', methods=['POST'])
@app.login_required
def activity_statistics(account_id=None):
  from models.account import Account
  from models.report import Report
  from helpers.report import ReportHelper
  
  account = Account.query.filter_by(id=account_id).first()
  if not account:
    return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['not found']}), mimetype='application/json')
  elif not app.access('activity', account=account):
    return Response(json.dumps({'status':403, 'description':'Not authorized', 'errors':['not authorized']}), mimetype='application/json')
  
  header = _activityHeader(employees=[account])
  
  filters = {}
  #filters['project'] = header['projects']
  # to allow the users ses all their reports
  filters['project'] = None
  filters['employee'] = [account.id for account in header['employees']]
  filters['start_date'] = header['start_date']
  filters['end_date'] = header['end_date']
  
  dataReports = []
  if app.access('report', action='administer'):
    dataReports = ReportHelper.listReports(
      start_date=filters['start_date'],
      end_date=filters['end_date'],
      accounts=filters['employee'],
      components=filters['project']
    )
  elif app.access('report', action='list'):
    dataReports = ReportHelper.listActiveReports(
      start_date=filters['start_date'],
      end_date=filters['end_date'],
      accounts=filters['employee'],
      components=filters['project']
    )
  else:
    return Response(json.dumps({'status':403, 'description':'Not authorized', 'errors':['not authorized']}), mimetype='application/json')
  
  statistics = {
    'hrs_day': 0.0,
    'hrs_week': 0.0,
    'hrs_month': 0.0,
    'tasks_day': 0,
    'tasks_week': 0,
    'tasks_month': 0,
    'projects_day': {},
    'projects_week': {},
    'projects_month': {}
  }
  
  for report in dataReports:
    if report.due_date == g._constant()['DATE']['TODAY']:
      statistics['hrs_day'] += report.duration
      statistics['tasks_day'] += 1
      if not statistics['projects_day'].has_key(report.path):
        statistics['projects_day'][report.path] = 0.0
      statistics['projects_day'][report.path] += report.duration
    if report.due_date >= g._constant()['DATE']['WEEK']:
      statistics['hrs_week'] += report.duration
      statistics['tasks_week'] += 1
      if not statistics['projects_week'].has_key(report.path):
        statistics['projects_week'][report.path] = 0.0
      statistics['projects_week'][report.path] += report.duration
    if report.due_date >= g._constant()['DATE']['MONTH']:
      statistics['hrs_month'] += report.duration
      statistics['tasks_month'] += 1
      if not statistics['projects_month'].has_key(report.path):
        statistics['projects_month'][report.path] = 0.0
      statistics['projects_month'][report.path] += report.duration
  
  html = render_template('report/dashboard.html', statistics=statistics, filters=filters)
  
  return Response(json.dumps({'status':200, 'description':'OK', 'data':statistics, 'html':html, 'filters':filters, 'errors':[]}), mimetype='application/json')



@app.route('/effort/summary', methods=['GET', 'POST'])
@app.login_required
def effort_summary():
  if not app.access('activity'):
    abort( 403 )
  
  header = _activityHeader()
  
  title = g._t('effort summary')
  return render_template('report/effort.summary.html', account=g.account, title=title, header=header)



@app.route('/effort/<account_id>/', methods=['GET', 'POST'])
@app.login_required
def effort_index(account_id):
  from models.account import Account
  
  account = Account.query.filter_by(id=account_id).first()
  if not account:
    abort(404)
  elif not app.access('activity', account=account):
    abort(403)
  
  header = _activityHeader(employees=[account])
  
  if account.id == g.account.id:
    title = g._t('efforts')
  else:
    title = g._t('efforts') + ' | ' + str(account)
  
  breadcrumbs = (
    (g._t('reports'), url_for('report_index', account_id=account.id)),
    (title, "#")
  )
  
  return render_template('report/effort.index.html', account=account, title=title, breadcrumbs=breadcrumbs, header=header)



@app.route('/report/', methods=['GET','POST'])
@app.route('/report/<account_id>/index', methods=['GET','POST'])
@app.login_required
def report_index_stub(account_id=None):
  if not account_id and g.account:
    account_id = g.account.id
  
  return redirect(url_for('report_index', account_id=account_id))

@app.route('/report/<account_id>/', methods=['GET','POST'])
@app.login_required
def report_index(account_id):
  from models.account import Account
  from models.report import Report
  
  account = Account.query.filter_by(id=account_id).first()
  if not account:
    abort(404)
  elif not app.access('activity', account=account):
    abort(403)
  
  header = _activityHeader(employees=[account])
  
  filters = {}
  filters['project'] = [component.id for component in header['projects']]
  filters['employee'] = [account.id for account in header['employees']]
  filters['start_date'] = header['start_date']
  filters['end_date'] = header['end_date']
  
  title = g._t( 'reports' )
  if account.id == g.account.id:
    title = g._t('reports')
  else:
    title = g._t('reports') + ' - ' + str(account)
  
  breadcrumbs = (
    (title, "#"),
    (g._t('efforts'), url_for('effort_index', account_id=account.id))
  )
  
  return render_template('report/report.index.html', account=account, title=title, breadcrumbs=breadcrumbs, header=header)



@app.route('/report/<account_id>/submit', methods=['GET', 'POST'])
@app.route('/report/<account_id>/<report_id>/edit', methods=['GET', 'POST'])
@app.login_required
def report_edit(account_id, report_id=None):
  from models.account import Account
  from models.project import Project, Component
  from models.report import Report
  
  account = Account.query.filter_by(id=account_id).first()
  if not account:
    if request.is_ajax:
      return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['user not found']}), mimetype='application/json')
    else:
      abort(404)
  
  report = None
  if not report_id:
    report = Report()
    report.status = Report.STATUS_ACTIVE
    report.due_date = datetime.datetime.now().strftime('%Y-%m-%d')
    if not app.access('report', action='create'):
      if request.is_ajax:
        return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
      else:
        abort(403)
  else:
    report_id = urllib.unquote_plus(report_id)
    report = Report.query.filter_by(id=report_id).first()
    if not report:
      if request.is_ajax:
        return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['report not found']}), mimetype='application/json')
      else:
        abort(404)
    elif not app.access('report', action='update', report=report):
      if request.is_ajax:
        return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
      else:
        abort(403)
  
  title = g._t('report submit')
  
  report_due_date_list = []
  validationErrors = []
  if (request.method == 'POST' and request.values.get('csrf_token', None)) or request.values.get('no_validate', None):
    report.reporter_id = g.account.id
    
    component_id = request.values.get('report_component_id', None)
    if component_id:
      component = Component.query.filter_by(id=component_id).first()
      if component:
        report.component_id = component.id
        report.project_id = component.project_id
    
    
    report_due_date_list = request.values.get('report_due_date', report.due_date).strip().split(',')
    report.due_date = report_due_date_list.pop(0)
    
    hours = request.values.get('report_hours', str(report.hours)).strip() or 0
    if not hours or not str(hours).isdigit():
      hours = 0.0
    minutes = request.values.get('report_minutes', str(report.minutes)).strip() or 0
    if not minutes or not str(minutes).isdigit():
      minutes = 0.0
    report.duration = float(hours) + (float(minutes) / 60)
    
    report.summary = request.values.get('report_summary', report.summary).strip()
    report.status = int(request.form.get('report_status', report.status).strip())
    report.account_id = account.id
    validationErrors = report.validate()
    if request.values.get('no_validate', None):
      status = 200
      description = 'OK'
    elif not validationErrors:
      report.save()
      
      for report_clone_due_date in report_due_date_list:
        if report_clone_due_date == report.due_date:
          continue
        reportClone = Report()
        reportClone.reporter_id = report.reporter_id
        reportClone.project_id = report.project_id
        reportClone.component_id = report.component_id
        reportClone.summary = report.summary
        reportClone.status = report.status
        reportClone.duration = report.duration
        reportClone.account_id = report.account_id
        reportClone.due_date = report_clone_due_date
        reportCloneValidationErrors = reportClone.validate()
        if not reportCloneValidationErrors:
          reportClone.save()
          print 'reportClone: saved'
      
      status = 200
      description = 'OK'
      if request.is_ajax:
        return Response(json.dumps({
          'html':render_template('_popup.html', title=g._t( 'report submit success' ), message=g._t( 'report submit success message' ), javascript="""setTimeout(function(){$('form[name=statistics-form]').submit(); $('form[name=filter-form]').submit();}, 300);"""),
          'status':status,
          'description':description,
          'errors':validationErrors
        }), mimetype='application/json')
      else:
        flash( g._t( 'report submit success' ) )
        return redirect( url_for( 'report_index', account_id=account_id ) )
    else:
      status = 400
      description = 'Bad request'
  else:
    status = 200
    description = 'OK'
    validationErrors = []
  
  if report.due_date:
    report_due_date_list.insert(0, report.due_date)
    
  report.due_date = ','.join(report_due_date_list)
  
  """
  If the report exists, but the account is no longer a member of the project, 
  we avoid an ability to change the project by keeping the only project option available
  """
  header = _activityHeader(employees=[account])
  projectList = header['projects']
  if report.id and report.component and not report.component in projectList:
    projectList = [report.component]
  
  if request.is_ajax:
    htmlContent = render_template('report/report.edit-popup.html', account=account, title=title, report=report, errors=validationErrors, projectList=projectList)
    return  Response(json.dumps({'html':htmlContent, 'status':status, 'description':description, 'errors':validationErrors}), mimetype='application/json')
  else:
    htmlContent = render_template('report/report.edit.html', account=account, title=title, report=report, errors=validationErrors, projectList=projectList)
    return htmlContent



@app.route('/report/<account_id>/<report_id>/delete', methods=['GET', 'POST'])
@app.login_required
def report_delete(account_id, report_id):
  from models.account import Account
  from models.report import Report
  
  account_id = urllib.unquote_plus(account_id)
  account = Account.query.filter_by(id=account_id).first()
  
  if not account:
    if request.is_ajax:
      return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['user not found']}), mimetype='application/json')
    else:
      abort(404)
  elif not app.access('activity', account=account):
    if request.is_ajax:
      return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
    else:
      abort(403)
  
  report_id = urllib.unquote_plus(report_id)
  report = Report.query.filter_by(id=report_id).first()
  
  if not report:
    if request.is_ajax:
      return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['report not found']}), mimetype='application/json')
    else:
      abort(404)
  elif not app.access('report', action='update', report=report):
    if request.is_ajax:
      return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
    else:
      abort(403)
  
  title = g._t('report delete')
  errors = []
  
  if request.method == 'POST' and request.values.get('csrf_token', None):
    if request.form.get('action') == 'report_action_remove_permanently':
      if not app.access('report', action='delete', report=report):
        if request.is_ajax:
          return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
        else:
          abort(403)
      report.delete()
      success_title = g._t('report remove permanently success')
      success_message= g._t('report remove permanently success message')
    elif request.form.get('action') == 'report_action_delete':
      report.status = report.status | report.STATUS_DELETED
      report.save()
      success_title = g._t('report delete success')
      success_message= g._t('report delete success message')
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
      return redirect(url_for('report_index', account_id=account_id))
  
  status = 200
  description = 'OK'
  if request.is_ajax:
    htmlContent = render_template('report/report.delete-popup.html', account=account, title=title, report=report, errors=errors)
    return  Response(json.dumps({'html':htmlContent, 'status':status, 'description':description, 'errors':errors}), mimetype='application/json')
  else:
    htmlContent = render_template('report/report.delete.html', account=account, title=title, report=report, errors=errors)
    return htmlContent



@app.route('/report/<account_id>/delete_multiple', methods=['GET', 'POST'])
@app.login_required
def report_delete_multiple(account_id):
  from models.account import Account
  from models.report import Report
  
  account_id = urllib.unquote_plus(account_id)
  account = Account.query.filter_by(id=account_id).first()
  
  if not account:
    if request.is_ajax:
      return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['user not found']}), mimetype='application/json')
    else:
      abort(404)
  elif not app.access('activity', account=account):
    if request.is_ajax:
      return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
    else:
      abort(403)
  
  reportIdList = request.values.getlist('report[id]')
  reportList = Report.query.filter(Report.id.in_(reportIdList)).all()
  
  for report in reportList:
    if not report:
      if request.is_ajax:
        return Response(json.dumps({'status':404, 'description':'Not found', 'errors':['report not found']}), mimetype='application/json')
      else:
        abort(404)
    elif not app.access('report', action='update', report=report):
      if request.is_ajax:
        return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
      else:
        abort(403)
  
  title = g._t('report delete') + ' ('+str(len(reportList))+')'
  errors = []
  
  if request.method == 'POST' and request.values.get('csrf_token', None):
    if request.form.get('action') == 'report_action_remove_permanently':
      if not app.access('report', action='delete'):
        if request.is_ajax:
          return Response(json.dumps({'status':403, 'description':'Forbidden', 'errors':['forbidden']}), mimetype='application/json')
        else:
          abort(403)
    
    if request.form.get('action') == 'report_action_remove_permanently':
      for report in reportList:
        report.delete()
      success_title = g._t('report remove permanently success')
      success_message= g._t('report remove permanently success message') + ' ('+str(len(reportList))+')'
    elif request.form.get('action') == 'report_action_delete':
      for report in reportList:
        report.status = report.status | report.STATUS_DELETED
        report.save()
      success_title = g._t('report delete success')
      success_message= g._t('report delete success message') + ' ('+str(len(reportList))+')'
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
      return redirect(url_for('report_index', account_id=account_id))
  
  status = 200
  description = 'OK'
  if request.is_ajax:
    htmlContent = render_template('report/report.delete_multiple-popup.html', account=account, title=title, reportList=reportList, errors=errors)
    return  Response(json.dumps({'html':htmlContent, 'status':status, 'description':description, 'errors':errors}), mimetype='application/json')
  else:
    htmlContent = render_template('report/report.delete_multiple.html', account=account, title=title, reportList=reportList, errors=errors)
    return htmlContent
