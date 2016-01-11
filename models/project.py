#!/usr/bin/python
# -*- coding: utf-8 -*-

from application import db
from models.base import BaseModel

class Version(db.Model, BaseModel):
  __tablename__ = 'versions'
  __table_args__ = {'mysql_charset': 'utf8'}

  id = db.Column(db.Integer, nullable=False, primary_key=True)
  title = db.Column(db.String(64), nullable=False, unique=True)
  released = db.Column(db.Integer, nullable=True)
  project_id = db.Column(db.Integer, db.ForeignKey('projects.id', onupdate='cascade', ondelete='cascade'), nullable=False)
  component_id = db.Column(db.Integer, db.ForeignKey('components.id', onupdate='cascade', ondelete='cascade'), nullable=False)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)

  project = db.relationship('Project', passive_updates=db._config.passive_updates, lazy='select')
  component = db.relationship('Component', passive_updates=db._config.passive_updates, lazy='select')

  def __str__(self):
    key = ''
    if self.title:
      key = self.title

    if self.component:
      key = '['+self.component.path+'] '+key

class Project(db.Model, BaseModel):
  __tablename__ = 'projects'
  __table_args__ = {'mysql_charset': 'utf8'}
  
  id = db.Column(db.Integer, nullable=False, primary_key=True)
  alias = db.Column(db.String(64), nullable=False, unique=True)
  title = db.Column(db.String(255), nullable=True)
  info = db.Column(db.Text, nullable=True)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)
  
  #members = db.relationship('Account', secondary='Membership', passive_updates=db._config.passive_updates, lazy='dynamic', backref=db.backref('projects'))
  
  def __str__(self):
    key = ''
    if self.alias:
      key = self.alias
    
    labels = []
    for label in self.labels:
      if label.title == Label.LABEL_INTERNAL:
        labels.append('INT')
      elif label.title == Label.LABEL_EXTERNAL:
        labels.append('EXT')
      elif label.title == Label.LABEL_VACATION:
        labels.append('OFF')
    
    if labels:
      labels.sort()
      key = ':'.join(labels) + '@' + key
    
    if self.status & self.STATUS_DELETED:
      key = key+' [INACTIVE]'
    
    return key
  
  @property
  def path(self):
    return self.alias
  
  def pre_save(self):
    # set the root project
    pass
  
  def validate( self ):
    self.__errors__ = []
    # alias is required and must be unique or NULL
    if self.query.filter(
        self.__class__.id!=self.id, 
        self.__class__.alias==self.alias 
        ).count() > 0:
      self.__errors__.append(('alias', 'must be unique'))
    if not self.alias:
      self.__errors__.append(('alias', 'required'))
    if not self.title:
      self.__errors__.append(('title', 'required'))
    
    return self.__errors__
  
  @property
  def keys(self):
    keys = [self.alias]
    for component in self.components:
      keys.append(self.alias+'/'+component.alias)
    
    return keys
  
  @property
  def items(self):
    items = [(self.alias, self.title)]
    for component in self.components:
      items.append((self.alias+'/'+component.alias, component.title))
    
    return items
  
  def post_save(self):
    defaultComponent = Component.query.filter_by(project=self, alias=Component.COMPONENT_DEFAULT).first()
    if not defaultComponent:
      defaultComponent = Component()
      defaultComponent.alias = Component.COMPONENT_DEFAULT
      defaultComponent.project = self
      defaultComponent.title = self.title
      defaultComponent.info = self.info
      defaultComponent.save()



class Component(db.Model, BaseModel):
  COMPONENT_DEFAULT = '.'
  
  __tablename__ = 'components'
  __table_args__ = (db.UniqueConstraint('project_id', 'alias'), {'mysql_charset': 'utf8'})
  
  id = db.Column(db.Integer, nullable=False, primary_key=True)
  alias = db.Column(db.String(255), nullable=False)
  title = db.Column(db.String(255), nullable=True)
  info = db.Column(db.Text, nullable=True)
  project_id = db.Column(db.Integer, db.ForeignKey('projects.id', onupdate='cascade', ondelete='cascade'), nullable=False)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)
  
  project = db.relationship('Project', passive_updates=db._config.passive_updates, lazy='joined', backref=db.backref('components', cascade=db._config.cascade_all))
  
  def __str__(self):
    if self.project:
      if self.isDefault():
        key = self.project.path
      else:
        key = self.project.path+'/'+self.alias
      
      labels = []
      for label in self.project.labels:
        if label.title == Label.LABEL_INTERNAL:
          labels.append('INT')
        elif label.title == Label.LABEL_EXTERNAL:
          labels.append('EXT')
        elif label.title == Label.LABEL_VACATION:
          labels.append('OFF')
      
      if labels:
        labels.sort()
        key = ':'.join(labels) + '@' + key
      
    else:
      if self.isDefault():
        key = '/'
      else:
        key = '/'+self.alias
    
    if self.status & self.STATUS_DELETED:
      key = key+' [INACTIVE]'
    
    return key
  
  def validate(self):
    self.__errors__ = []
    # alias is required and must be unique or NULL
    if self.query.filter(
        self.__class__.id!=self.id, 
        self.__class__.alias==self.alias, 
        self.__class__.project_id==self.project_id 
        ).count() > 0:
      self.__errors__.append(('alias', 'must be unique'))
    if not self.alias:
      self.__errors__.append(('alias', 'required'))
    if not self.title:
      self.__errors__.append(('title', 'required'))
    if not self.project_id:
      self.__errors__.append(('project_id', 'required'))
    
    return self.__errors__
  
  @property
  def path(self):
    if self.project:
      if self.isDefault():
        key = self.project.path
      else:
        key = self.project.path+'/'+self.alias
      
      labels = []
      for label in self.project.labels:
        if label.title == Label.LABEL_INTERNAL:
          labels.append('INT')
        elif label.title == Label.LABEL_EXTERNAL:
          labels.append('EXT')
        elif label.title == Label.LABEL_VACATION:
          labels.append('OFF')
      
      if labels:
        labels.sort()
        key = ':'.join(labels) + '@' + key
      
    else:
      if self.isDefault():
        key = '/'
      else:
        key = '/'+self.alias
    
    return key
  
  def isDefault(self):
    return self.alias == self.COMPONENT_DEFAULT



class Label(db.Model, BaseModel):
  LABEL_DEFAULT = 'project'
  LABEL_GENERAL = 'general'
  LABEL_VACATION = 'vacation'
  LABEL_INTERNAL = 'internal'
  LABEL_EXTERNAL = 'external'
  
  __tablename__ = 'labels'
  __table_args__ = (db.UniqueConstraint('project_id', 'title'), {'mysql_charset': 'utf8'})
  
  id = db.Column(db.Integer, nullable=False, primary_key=True)
  title = db.Column(db.String(255), nullable=True)
  info = db.Column(db.Text, nullable=True)
  project_id = db.Column(db.Integer, db.ForeignKey('projects.id', onupdate='cascade', ondelete='cascade'), nullable=False)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)
  
  project = db.relationship('Project', passive_updates=db._config.passive_updates, lazy='joined', backref=db.backref('labels', cascade=db._config.cascade_all))
  
  def __str__(self):
    return self.title
  
  def validate( self ):
    self.__errors__ = []
    # a project cannot have the same label name twice
    if self.query.filter(
        self.__class__.id!=self.id, 
        self.__class__.title==self.title, 
        self.__class__.project_id==self.project_id
        ).count() > 0:
      self.__errors__.append(('title', 'must be unique'))
    if not self.title:
      self.__errors__.append(('title', 'required'))
    if not self.project_id:
      self.__errors__.append(('project_id', 'required'))
    
    return self.__errors__



class Role(db.Model, BaseModel):
  ROLE_MANAGER = 'role:manager'
  ROLE_LEADER = 'role:leader'
  ROLE_DEFAULT = 'role:default'
  
  __tablename__ = 'roles'
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
  
  def validate( self ):
    self.__errors__ = []
    # alias is required and must be unique or NULL
    if self.query.filter(
        self.__class__.id!=self.id, 
        self.__class__.alias==self.alias 
        ).count() > 0:
      self.__errors__.append(('alias', 'must be unique'))
    if not self.alias:
      self.__errors__.append(('alias', 'required'))
    if not self.title:
      self.__errors__.append(('title', 'required'))
    
    return self.__errors__



class Membership(db.Model, BaseModel):
  __tablename__ = 'membership'
  __table_args__ = (db.UniqueConstraint('project_id', 'component_id', 'account_id'), {'mysql_charset': 'utf8'})
  
  id = db.Column(db.Integer, nullable=False, primary_key=True)
  project_id = db.Column(db.Integer, db.ForeignKey('projects.id', onupdate='cascade', ondelete='set null'), nullable=True)
  component_id = db.Column(db.Integer, db.ForeignKey('components.id', onupdate='cascade', ondelete='cascade'), nullable=False)
  account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', onupdate='cascade', ondelete='set null'), nullable=True)
  role_id = db.Column(db.Integer, db.ForeignKey('roles.id', onupdate='cascade', ondelete='set null'), nullable=True)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)
  
  #account = db.relationship('Account', passive_updates=db._config.passive_updates, lazy='joined')#, backref=db.backref('membership', cascade=db._config.cascade_all))
  account = db.relationship('Account', passive_updates=db._config.passive_updates, lazy='subquery')
  #project = db.relationship('Project', passive_updates=db._config.passive_updates, lazy='joined', backref=db.backref('members'))
  project = db.relationship('Project', passive_updates=db._config.passive_updates, lazy='subquery', backref=db.backref('members'))
  #component = db.relationship('Component', passive_updates=db._config.passive_updates, lazy='joined')#, backref=db.backref('members', cascade=db._config.cascade_all))
  component = db.relationship('Component', passive_updates=db._config.passive_updates, lazy='subquery')
  role = db.relationship('Role', passive_updates=db._config.passive_updates, lazy='subquery')#, backref=db.backref('membership'))
  
  
  
  def __str__(self):
    return 'membership: ' + self.account.alias + ' at ' + self.project.alias
  
  def validate( self ):
    self.__errors__ = []
    # cannot be a member twice at the same project/component
    if self.query.filter(
        self.__class__.id!=self.id, 
        self.__class__.account_id==self.account_id, 
        self.__class__.project_id==self.project_id, 
        self.__class__.component_id==self.component_id 
        ).count() > 0:
      self.__errors__.append('duplicate entry')
    if not self.project_id:
      self.__errors__.append(('project_id', 'required'))
    if not self.component_id:
      self.__errors__.append(('component_id', 'required'))
    if not self.account_id:
      self.__errors__.append(('account_id', 'required'))
    if not self.role_id:
      self.__errors__.append(('role_id', 'required'))
    
    return self.__errors__
