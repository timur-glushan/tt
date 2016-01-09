#!/usr/bin/python
# -*- coding: utf-8 -*-

from application import db
from models.base import BaseModel
from models.project import Project, Membership

class Account(db.Model, BaseModel):
  __tablename__ = 'accounts'
  __table_args__ = {'mysql_charset': 'utf8'}
  
  id = db.Column(db.Integer, nullable=False, primary_key=True)
  email = db.Column(db.String(255), nullable=True)
  alias = db.Column(db.String(255), nullable=False, unique=True)
  first_name = db.Column(db.String(255), nullable=True)
  last_name = db.Column(db.String(255), nullable=True)
  stored_password = db.Column(db.String(255), nullable=True, unique=False)
  password = db.Column(db.String(255), nullable=True, unique=False)
  info = db.Column(db.Text, nullable=True)
  group_id = db.Column(db.Integer, db.ForeignKey('groups.id', onupdate='cascade', ondelete='set null'), nullable=True)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)
  
  group = db.relationship('Group', passive_updates=db._config.passive_updates, lazy='joined', backref=db.backref('accounts'))
  projects = db.relationship('Project', secondary='membership', passive_updates=db._config.passive_updates, backref=db.backref('accounts', lazy='dynamic'))
  
  def __str__( self ):
    key = []
    if self.first_name or self.last_name:
      if self.first_name:
        key.append( self.first_name )
      if self.last_name:
        key.append( self.last_name )
    elif self.email:
      key.append( self.email )
    elif self.alias:
      key.append( self.alias )
    
    if self.status & self.STATUS_DELETED:
      key.append( '[INACTIVE]' )
    
    return ' '.join( key )
  
  def validate(self):
    self.__errors__ = []
    # email is required and must be unique or NULL
    if self.email and self.query.filter(
        self.__class__.id!=self.id, 
        self.__class__.email==self.email 
        ).count() > 0:
      self.__errors__.append('email must be unique')
    # alias is required and must be unique or NULL
    if self.query.filter(
        self.__class__.id!=self.id, 
        self.__class__.alias==self.alias 
        ).count() > 0:
      self.__errors__.append(('alias', 'must be unique'))
    if not self.email:
      self.__errors__.append(('email', 'required'))
    if not self.alias:
      self.__errors__.append(('alias', 'required'))
    if not self.group_id:
      self.__errors__.append(('group_id', 'required'))
    
    return self.__errors__
  
  @classmethod
  def hash( cls, string ):
    from hashlib import md5
    import unidecode
    
    return md5(cls.salt + md5(unidecode.unidecode(string)).hexdigest()).hexdigest()
  
  def validatePassword( self, password ):
    return (not self.passwordIsSet() and not password) or (self.hash(password) == self.stored_password)
  
  def passwordIsSet( self ):
    return bool(self.stored_password)
  
  def pre_save(self):
    if self.password != self.stored_password:
      self.password = self.stored_password = self.hash(self.password)
  
  def getPreference(self, name, account_id=None):
    if account_id is None:
      account_id = self.id
    preference = Preference.query.filter_by(account_id=account_id, name=name).first()
    return preference and preference.value or None
  
  def setPreference(self, key, value, account_id=None):
    if account_id is None:
      account_id = self.id
    preference = Preference.query.filter_by(account_id=account_id, name=name).first()
    if not preference:
      preference = Preference()
      preference.name = name
      preference.account_id = account_id
    
    preference.value = value
    preference.save()
    return preference



class Preference(db.Model, BaseModel):
  PREFERENCE_LANGUAGE = 'language'
  PREFERENCE_TIME_FORMAT = 'time format'
  PREFERENCE_SHOW_DELETED_REPORTS = 'show deleted reports'
  
  __tablename__ = 'preferences'
  __table_args__ = (db.UniqueConstraint('name', 'account_id'), {'mysql_charset': 'utf8'})
  
  id = db.Column(db.Integer, nullable=False, primary_key=True)
  account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', onupdate='cascade', ondelete='cascade'), nullable=False)
  name = db.Column(db.String(64), nullable=False)
  raw_value = db.Column(db.Text, nullable=True)
  
  account = db.relationship('Account', passive_updates=db._config.passive_updates, lazy='joined', backref=db.backref('preferences', cascade=db._config.cascade_all))
  
  def __str__(self):
    return '['+self.account.alias+'] '+self.name
  
  def validate(self):
    import json
    
    self.__errors__ = []
    # an account cannot have the same preference name twice
    if self.query.filter(
        self.__class__.id!=self.id, 
        self.__class__.name==self.name, 
        self.__class__.account_id==self.account_id
        ).count() > 0:
      self.__errors__.append(('name', 'must be unique'))
    if not self.name:
      self.__errors__.append(('name', 'required'))
    if not self.account_id:
      self.__errors__.append(('account_id', 'required'))
    try:
      value = json.loads(self.raw_value)
    except Exception as e:
      self.__errors__.append(('value', 'not a json'))
    
    return self.__errors__
  
  @property
  def value(self):
    import json
    if self.raw_value is not None:
      return json.loads(self.raw_value)
    else:
      return self.raw_value
  
  @value.setter
  def value(self, value):
    import json
    self.raw_value = json.dumps(value)



class Group(db.Model, BaseModel):
  GROUP_ADMINISTRATOR = 'administrator'
  GROUP_DEFAULT = 'member'
  
  __tablename__ = 'groups'
  __table_args__ = {'mysql_charset': 'utf8'}
  
  id = db.Column(db.Integer, nullable=False, primary_key=True)
  alias = db.Column(db.String(64), nullable=False, unique=True)
  title = db.Column(db.String(255), nullable=True)
  info = db.Column(db.Text, nullable=True)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)
  
  def __str__(self):
    value = '['+self.alias+']'
    if self.title:
      value = value + ' ' + self.title
    return value
  
  def validate(self):
    self.__errors__ = []
    # alias is required and must be unique or NULL
    if self.query.filter(
        self.__class__.id!=self.id, 
        self.__class__.alias==self.alias 
        ).count() > 0:
      self.__errors__.append(('alias', 'must be unique'))
    # email must be unique or NULL
    if not self.alias:
      self.__errors__.append(('alias', 'required'))
    if not self.title:
      self.__errors__.append(('title', 'required'))
    
    return self.__errors__
