class AccountHelper:
  @classmethod
  def __parseAccountArgument(cls, account_id):
    from models.account import Account
    
    if type(account_id) in [str, u' ']:
      account = Account.query.filter_by(id=account_id).first()
    else:
      account = account_id
    
    return account
  
  
  
  @classmethod
  def listAccounts(cls):
    from models.account import Account
    
    return Account.query\
      .order_by(Account.first_name, Account.last_name, Account.alias)\
      .all()
  
  @classmethod
  def listActiveAccounts(cls):
    from models.account import Account
    
    return Account.query\
      .filter(~Account.status.in_(Account._r(Account.STATUS_DELETED)))\
      .order_by(Account.first_name, Account.last_name, Account.alias)\
      .all()
  
  
  
  @classmethod
  def listGroups(cls):
    from models.account import Group
    
    return Group.query\
      .order_by(Group.alias)\
      .all()
  
  @classmethod
  def listActiveGroups(cls):
    from models.account import Group
    
    return Group.query\
      .filter(~Group.status.in_(Group._r(Group.STATUS_DELETED)))\
      .order_by(Group.alias)\
      .all()
  
  
  
  @classmethod
  def getPreference(cls, name):
    from flask import g, request
    from models.account import Account, Preference
    from models.variable import Variable
    import json
    
    if hasattr(g, 'account') and g.account:
      preference = Preference.query.filter_by(account_id=g.account.id, name=name).first()
      if preference:
        return preference.value
    cookie = request.cookies.get(name)
    # OVERRIDE TO PREVENT THE COOKIE USAGE FOR NOW
    cookie = False
    if cookie:
      try:
        cookie = json.loads(cookie)
      except Exception as e:
        cookie = cookie
      return cookie
    else:
      variable = Variable.query.filter_by(scope='preference', name=name).first()
      if variable:
        return variable.value
  
  @classmethod
  def setPreference(cls, name, value):
    from flask import g, request
    from models.account import Account, Preference
    
    if hasattr(g, 'account') and g.account:
      preference = Preference.query.filter_by(account_id=g.account.id, name=name).first()
      if preference:
        preference.value = value
      else:
        preference = Preference()
        preference.account_id = g.account.id
        preference.name = name
        preference.value = value
      
      if not preference.validate():
        preference.save()
        return True
    
    return False
  
  @classmethod
  def issetPreference(cls, name):
    from flask import g, request
    from models.account import Account, Preference
    
    if hasattr(g, 'account') and g.account and g.account.passwordIsSet():
      return Preference.query.filter_by(account_id=g.account.id, name=name).first() and True or False
    return None
  
  @classmethod
  def getChineseCookie(cls):
    from models.variable import Variable
    import datetime
    import time
    import random
    from application import app
    
    if not app.access('authenticated'):
      # cookie will be shown to the authenticated users only
      return None
    
    if app.access('is_masquerade'):
      # cookie is not shown for the masquerade sessions
      return None
    
    if not cls.getPreference('show_chinese_cookie'):
      # chinese cookie disbled for the user
      return None
    
    language = cls.getPreference('language')
    if not language:
      # no language defined
      return None
    
    variable = Variable.query.filter_by(scope='common', name='chinese_cookie_data').first()
    if not variable or not type(variable.value) == dict:
      # no chinese cookie defined
      return None
    if not variable.value.has_key(language):
      # no chinese cookie for a given language
      return None
    value = variable.value[language]
    
    nowDate = datetime.datetime.now()
    midnightDate = datetime.datetime( year=nowDate.year, month=nowDate.month, day=nowDate.day )
    midnightDateString = midnightDate.strftime( '%Y-%m-%d' )
    
    chinese_cookie_date_shown = cls.getPreference('chinese_cookie_date_shown') or '0'
    if chinese_cookie_date_shown >= midnightDateString:
      # the chinese cookie has been already shown today
      return None
    
    chinese_cookie_list_shown = cls.getPreference('chinese_cookie_list_shown') or []
    available_chinese_cookie_list = []
    for cc in value:
      if not cc in chinese_cookie_list_shown:
        # add a chinese cookie to the list of available ones if it's never shown to the user
        available_chinese_cookie_list.append(cc)
    
    if len(available_chinese_cookie_list) == 0:
      # all chinese cookies for a given language have been shown to the user already
      return None
    
    new_chineese_cookie = available_chinese_cookie_list[random.randint(0, len(available_chinese_cookie_list)-1)]
    cls.setPreference('chinese_cookie_date_shown', midnightDateString)
    chinese_cookie_list_shown.append(new_chineese_cookie)
    cls.setPreference('chinese_cookie_list_shown', chinese_cookie_list_shown)
    
    return new_chineese_cookie
