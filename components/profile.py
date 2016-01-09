from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import urllib

# permissions section
@app.permission('profile')
def permission_profile(action=None, account=None):
  """Profile CRUD check for signed in account. 
  @description Check if a signed in account has a specified action for a given account. 
  @param <str>action, valid values ["list", "administer", "create", "read", "update", "delete"]
  @param <Account>account (optional) 
  @return bool 
  @example Call as app.access('profile', action='update', account=ACCOUNT)"""
  from models.account import Account
  
  if not action:
    raise Exception('Profile CRUD permission: action missing')
  
  if not account and not action in ['list', 'administer', 'create']:
    raise Exception('Profile CRUD permission: account required for action "'+action+'"')
  
  if action == 'list':
    return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager', 'privileged_member'])
  if action == 'administer':
    return app.access('group', group_alias=['administrator', 'privileged_manager'])
  elif action == 'create':
    return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager'])
  elif action == 'read':
    if account.status & account.STATUS_DELETED:
      return app.access('group', group_alias=['administrator', 'privileged_manager'])
    else:
      return True
  elif action == 'update':
    if account.status & account.STATUS_DELETED:
      return app.access('group', group_alias=['administrator', 'privileged_manager'])
    elif account.id == g.account.id:
      return True
    else:
      return app.access('group', group_alias=['administrator', 'privileged_manager', 'manager'])
  elif action == 'delete':
    if account.id == g.account.id:
      return False
    else:
      return app.access('group', group_alias=['administrator', 'privileged_manager'])
  else:
    raise Exception('Profile CRUD permission: incorrect action "'+action+'", must be ["list", "administer", "create", "read", "update", "delete"]')



# request hooks section
@app.before_request
def profile_before_request():
  pass

@app.teardown_request
def profile_teardown_request(exception):
  pass



# routes section
@app.route('/employees', methods=['GET', 'POST'])
@app.login_required
def profile_employees():
  from models.account import Account
  from helpers.account import AccountHelper
  
  title = g._t('employees')
  if app.access('profile', action='administer'):
    employees = AccountHelper.listAccounts()
  elif app.access('profile', action='list'):
    employees = AccountHelper.listActiveAccounts()
  else:
    employees = [g.account]
    return redirect(url_for('profile_view', account_id=urllib.quote_plus(str(g.account.id))))
    
  return render_template('profile/employees.html', employees=employees, title=title)



@app.route('/profile/<account_id>/view', methods=['GET', 'POST'])
@app.login_required
def profile_view(account_id):
  from models.account import Account
  
  account_id = urllib.unquote_plus(account_id)
  account = Account.query.filter_by(id=account_id).first()
  
  if not account:
    abort(404)
  elif not app.access('profile', action='read', account=account):
    abort(403)
  
  title = (app.access('authenticated', account=account)) and g._t('me') or account.__str__()
  breadcrumbs = (
    ((app.access('authenticated', account=account) and g._t( 'employees' ) or ''), url_for('profile_employees')),
    (title, "#"),
  )
  
  return render_template('profile/view.html', account=account, title=title, breadcrumbs=breadcrumbs)


@app.route('/profile/create', methods=['GET', 'POST'])
@app.route('/profile/<account_id>/edit', methods=['GET', 'POST'])
@app.login_required
def profile_edit(account_id=None):
  from models.account import Account, Group
  from helpers.account import AccountHelper
  
  account = None
  if not account_id:
    if not app.access('profile', action='create'):
      abort(403)
    account = Account()
    account.status = Account.STATUS_ACTIVE
    account.group_id = Group.query.filter_by(alias=Group.GROUP_DEFAULT).first().id
  else:
    account_id = urllib.unquote_plus(account_id)
    account = Account.query.filter_by(id=account_id).first()
    if not account:
      abort(404)
    elif not app.access('profile', action='update', account=account):
      abort(403)
  
  print '[GROUP]',account.group_id, account.group
  
  validationErrors = []
  if request.method == 'POST' and request.form.get('csrf_token', None):
    account.alias = request.values.get('account_alias', account.alias).strip()
    account.first_name = request.values.get('account_first_name', account.first_name).strip()
    account.last_name = request.values.get('account_last_name', account.last_name).strip()
    account.email = request.values.get('account_email', account.email).strip()
    account.info = request.values.get('account_info', account.info).strip()
    account_group_id = request.values.get('account_group_id', '').strip()
    account.status = int(request.form.get('account_status', account.status).strip())
    
    account_group = None
    if account_group_id:
      account_group = Group.query.filter_by(id=account_group_id).first()
    if not account_group:
      account_group = Group.query.filter_by(alias=Group.GROUP_DEFAULT).first()
    account.group_id = account_group.id
    
    validationErrors = account.validate()
    if not validationErrors:
      account.save()
      flash(g._t('profile submit success'))
      
      if account_id:
        return redirect(url_for('profile_view', account_id=urllib.quote_plus(account_id)))
      else:
        return redirect(url_for('profile_employees'))
  
  if account_id:
    title = g._t('edit profile')
  else:
    title = g._t('new profile')
  
  if account_id:
    breadcrumbs = (
      (((not app.access('authenticated', account=account)) and g._t('employees') or ''), url_for('profile_employees')),
      ((app.access('authenticated', account=account) and g._t('me') or account.__str__()), url_for('profile_view', account_id=account_id)),
      (title, "#")
    )
  else:
    breadcrumbs = (
      (g._t('employees'), url_for('profile_employees')),
      (title, "#")
    )
  
  if app.access('profile', action='administer'):
    groupList = AccountHelper.listGroups()
  else:
    groupList = AccountHelper.listActiveGroups()
  
  return render_template('profile/edit.html', account_id=account_id, account=account, groupList=groupList, title=title, breadcrumbs=breadcrumbs, errors=validationErrors)



@app.route('/profile/<account_id>/preferences', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.login_required
def profile_preferences(account_id):
  from models.account import Account, Preference
  from helpers.account import AccountHelper
  
  account_id = urllib.unquote_plus(account_id)
  account = Account.query.filter_by(id=account_id).first()
  if not account:
    abort(404)
  elif not app.access('profile', action='update', account=account):
    abort(403)
  
  preferences = {
    'language': None,
    'floats_format': None,
    'report_time_format': None,
    'show_deleted_reports': None,
    'datepicker_multiple_days': None,
    'show_chinese_cookie': None
  }
  
  for key in preferences.keys():
    preference = Preference.query.filter_by(account_id=account.id, name=key).first()
    if not preference:
      preference = Preference()
      preference.account_id = account.id
      preference.name = key
      preference.value = AccountHelper.getPreference(key)
    preferences[key] = preference
  
  title = g._t('profile preferences')
  
  breadcrumbs = (
    (((not app.access('authenticated', account=account)) and g._t('employees') or ''), url_for('profile_employees')),
    ((app.access('authenticated', account=account) and g._t('me') or account.__str__()), url_for('profile_view', account_id=account_id)),
    (title, "#")
  )
  
  validationErrors = []
  
  if request.method == 'POST' and request.form.get('csrf_token'):
    for key, preference in preferences.items():
      preference.raw_value = request.form.get('preference_'+key, None)
      errors = preference.validate()
      validationErrors.extend(errors)
      if not errors:
        preference.save()
    
    if not validationErrors:
      flash( g._t('preference update success'))
    else:
      flash( g._t('preference update error'), 'error')
    return redirect(url_for('profile_preferences', account_id=urllib.quote_plus(account_id)))
  
  return render_template('profile/preferences.html', account_id=account_id, account=account, preferences=preferences, title=title, breadcrumbs=breadcrumbs, errors=validationErrors)



@app.route('/profile/<account_id>/password', methods=['GET', 'POST'])
@app.login_required
def profile_password( account_id ):
  from models.account import Account
  
  account_id = urllib.unquote_plus(account_id)
  account = Account.query.filter_by(id=account_id).first()
  if not account:
    abort(404)
  elif not app.access('profile', action='update', account=account):
    abort(403)
  title = g._t('profile')+' | '+g._t('profile password set')
  breadcrumbs = (
    (((not app.access('authenticated', account=account)) and g._t('employees') or ''), url_for('profile_employees')),
    ((app.access('authenticated', account=account) and g._t('me') or account.__str__()), url_for('profile_view', account_id=account_id)),
    (title, "#")
  )
  
  errors = []
  
  if request.method == 'POST':
    if account.passwordIsSet() and not request.form.get('current_password'):
      errors.append(('current password', 'required'))
    elif account.passwordIsSet() and not account.validatePassword( request.form.get('current_password')):
      errors.append(('current password', 'incorrect'))
    if not request.form.get('password'):
      errors.append(('new password', 'required'))
    elif not request.form.get('confirm_password'):
      errors.append(('confirm new password', 'required'))
    elif not request.form.get('password') == request.form.get('confirm_password'):
      errors.append(('new password', 'does not match'))
    if not len(errors):
      account.password = request.form.get('password')
      account.save()
      flash(g._t('profile password set success'))
      return redirect(url_for('profile_view', account_id=urllib.quote_plus(account_id)))
  return render_template('profile/password.html', account=account, title=title, breadcrumbs=breadcrumbs, errors=errors)



@app.route('/profile/<account_id>/delete', methods=['GET', 'POST'])
@app.login_required
def profile_delete(account_id):
  from models.account import Account
  
  account_id = urllib.unquote_plus(account_id)
  account = Account.query.filter_by(id=account_id).first()
  
  if not account:
    abort(404)
  elif not app.access('profile', action='update', account=account):
    abort(403)
  
  if request.method == 'POST' and request.form.get('csrf_token', None):
    if request.form.get('action') == 'profile_action_remove_permanently':
      if not app.access('profile', action='delete', account=account):
        abort(403)
      else:
        account.delete()
        success_message = g._t('profile remove permanently success')
        
    elif request.form.get('action') == 'profile_action_delete':
      account.status = account.status | account.STATUS_DELETED
      account.save()
      success_message = g._t('profile delete success')
    
    flash(success_message)
    return redirect(url_for('profile_employees'))
  
  errors = []
  
  title = g._t('delete profile?')
  breadcrumbs = (
    (((not app.access('authenticated', account=account)) and g._t('employees') or ''), url_for('profile_employees')),
    ((app.access('authenticated', account=account) and g._t('me') or account.__str__()), url_for('profile_view', account_id=account_id)),
    (title, "#")
  )
  
  return render_template('profile/delete.html', account=account, title=title, breadcrumbs=breadcrumbs, errors=errors)
