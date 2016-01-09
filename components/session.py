from application import app
from flask import Flask, request, make_response, session, g, redirect, url_for, abort, render_template, flash
import urllib



#helpers section
def session_account():
  from models.account import Account
  
  if session.get('masquerade_id', None):
    account = Account.query.filter_by(id=session['masquerade_id']).first()
    if account:
      return account
    else:
      session.pop('masquerade_id', None)
  if session.get('authenticated_id', None):
    account = Account.query.filter_by(id=session['authenticated_id']).first()
    if account:
      return account
    else:
      session.pop('authenticated_id', None)
  
  return None

def session_masquerade_host_account():
  from models.account import Account
  
  if session.get('masquerade_id', None) and session.get('authenticated_id', None):
    return Account.query.filter_by(id=session['authenticated_id']).first()
  else:
    return None

def session_authenticate(login, password):
  from models.account import Account
  
  account = Account.query.filter_by(alias=login).first() or Account.query.filter_by(email=login).first()
  if account and not account.status & account.STATUS_DELETED:
    if account.validatePassword(password):
      session['authenticated_id'] = account.id
      return session_account()
  return None

def session_authenticate_masquerade(id):
  from models.account import Account
  
  account = Account.query.filter_by(id=id).first()
  if account:
    session['masquerade_id'] = account.id
    return session_account()
  return None

def session_forget():
  if session.get('masquerade_id', None):
    session.pop('masquerade_id', None)
    return True
  elif session.get('authenticated_id', None):
    session.pop('authenticated_id', None)
    return True
  else:
    return False



@app.permission('masquerade')
def permission_masquerade(account=None):
  """Permission to re-login as another account. 
  @description Check if a signed in account is permitted to re-login as another account. 
  @param <Account>account 
  @return bool 
  @example Call as app.access('masquerade', account=ACCOUNT)"""
  if not account:
    raise Exception('Masquerade permission: account missing')
  
  if account.id == g.account.id:
    return False
  else:
    return app.access('group', group_alias=['administrator', 'privileged_manager']) and app.access('profile', action='update', account=account)



@app.permission('is_masquerade')
def permission_is_masquerade():
  """Is masquerade set. 
  @description Check if an account is currently under masquerade. 
  @return <Account> host account or False 
  @example Call as app.access('is_masquerade')"""
  return g.host_account or False



# request hooks section
@app.before_request
def session_before_request():
  g.host_account = session_masquerade_host_account()
  g.account = session_account()
  
  # call Account::save() method for the account (host_account for masquerade, account for original session) to update the Account.modified field value
  if g.host_account:
    g.host_account.save()
  elif g.account:
    g.account.save()
  
  if g.account and g.account.id:
    if not g.account.passwordIsSet():
      if not request.path.startswith('/signout') and not request.path.startswith('/profile/'+str(g.account.id)+'/password') and not request.path.startswith('/static'):
        flash('Your password is not set. Please set the account password to continue.', 'info')
        return redirect(url_for('profile_password', account_id=urllib.quote_plus(str(g.account.id))))

@app.teardown_request
def session_teardown_request(exception):
  pass



# routes section
@app.route('/signup', methods=['GET', 'POST'])
def session_signup():
  return redirect(url_for('application_NOT_IMPLEMENTED'))



@app.route('/signin', methods=['GET', 'POST'])
def session_signin():
  account = None
  errors = []
  if request.method == 'POST':
    if not request.form.get('email', None):
      errors.append(('login', 'required'))
    if len(errors)==0:
      account = session_authenticate(request.form.get('email'), request.form.get('password', None))
      if not account:
        errors.append('invalid login or password')
      else:
        flash(g._t('signin success'), 'success')
        return redirect(url_for('application_index'))
  title = g._t( 'Sign In' )
  return render_template('session/signin.html', errors=errors, title=title)



@app.route('/masquerade/<account_id>')
@app.login_required
def session_masquerade(account_id):
  from models.account import Account
  
  account_id = urllib.unquote_plus(account_id)
  account = Account.query.filter_by(id=account_id).first()
  
  if app.access('is_masquerade'):
    flash(g._t('already masquerade'), 'error')
    return redirect(url_for(app.config['HOME_PAGE']))
  if not account:
    abort(404)
  elif not app.access('masquerade', account=account):
    abort(403)
  
  session_authenticate_masquerade(account.id)
  
  flash(g._t('masquerade success'), 'success')
  return redirect(url_for(app.config['HOME_PAGE']))



@app.route('/signout')
def session_signout():
  if app.access('authenticated'):
    if app.access('is_masquerade'):
      success_message = g._t('masquerade stop success')
    else:
      success_message = g._t('signout success')
    session_forget()
    flash(success_message, 'success')
  return redirect(url_for(app.config['HOME_PAGE']))



@app.route('/preference/<name>/<value>', methods=['GET', 'POST'])
def session_preference(name, value):
  from helpers.account import AccountHelper
  import json
  
  value = urllib.unquote_plus(value)
  value = json.loads(value)
  
  AccountHelper.setPreference(name, value)
  
  if request.is_ajax:
    response = make_response(json.dumps({'status':200, 'description':'OK', 'errors':[]}))
    response.mimetype = 'application/json'
  else:
    if request.referrer and request.referrer != request.url:
      next = request.referrer
    else:
      next = url_for(app.config['HOME_PAGE'])
    response = make_response(redirect(next))
  
  response.set_cookie(name, json.dumps(value))
  return response
