#!/usr/bin/python
# -*- coding: utf-8 -*-

from application import db
from models.base import BaseModel
#import datetime
#import time

class Priority(db.Model, BaseModel):
  __tablename__ = 'priorities'
  __table_args__ = {'mysql_charset': 'utf8'}

  id = db.Column(db.Integer, nullable=False, primary_key=True)
  alias = db.Column(db.String(64), nullable=False, unique=True)
  weight = db.Column(db.Integer, nullable=True)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)



class Resolution(db.Model, BaseModel):
  __tablename__ = 'resolutions'
  __table_args__ = {'mysql_charset': 'utf8'}

  id = db.Column(db.Integer, nullable=False, primary_key=True)
  alias = db.Column(db.String(64), nullable=False, unique=True)
  weight = db.Column(db.Integer, nullable=True)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)



class Ticket(db.Model, BaseModel):
  __tablename__ = 'tickets'
  __table_args__ = {'mysql_charset': 'utf8'}
  
  id = db.Column(db.Integer, nullable=False, primary_key=True)
  alias = db.Column(db.String(64), nullable=False, unique=True)
  title = db.Column(db.String(256), nullable=False)
  summary = db.Column(db.Text, nullable=True)
  project_id = db.Column(db.Integer, db.ForeignKey('projects.id', onupdate='cascade', ondelete='cascade'), nullable=False)
  component_id = db.Column(db.Integer, db.ForeignKey('components.id', onupdate='cascade', ondelete='cascade'), nullable=False)
  version_id = db.Column(db.Integer, db.ForeignKey('versions.id', onupdate='cascade', ondelete='set null'), nullable=True)
  account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', onupdate='cascade', ondelete='set null'), nullable=True)
  assignee_id = db.Column(db.Integer, db.ForeignKey('accounts.id', onupdate='set null', ondelete='set null'), nullable=True)
  priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id', onupdate='set null', ondelete='set null'), nullable=True)
  resolution_id = db.Column(db.Integer, db.ForeignKey('resolutions.id', onupdate='set null', ondelete='set null'), nullable=True)
  created = db.Column(db.Integer, nullable=True)
  modified = db.Column(db.Integer, nullable=True)
  status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)
  
  project = db.relationship('Project', passive_updates=db._config.passive_updates, lazy='select')
  component = db.relationship('Component', passive_updates=db._config.passive_updates, lazy='select')
  version = db.relationship('Version', passive_updates=db._config.passive_updates, lazy='select')
  account = db.relationship('Account', foreign_keys=[account_id], passive_updates=db._config.passive_updates, lazy='select')
  assignee = db.relationship('Account', foreign_keys=[assignee_id], passive_updates=db._config.passive_updates, lazy='select')
  priority = db.relationship('Priority', passive_updates=db._config.passive_updates, lazy='select')
  resolution = db.relationship('Resolution', passive_updates=db._config.passive_updates, lazy='select')

  
  def __str__(self):
    return 'report: by '+str(self.account.alias or 'unknown')+' on '+str(self.project.alias or 'unknown')+' due '+str(self.due_date or '?')+ ' ['+str(self.hours or 0.0)+']'
  
  def validate(self):
    self.__errors__ = []
    if not self.account_id:
      self.__errors__.append(('account_id', 'required'))
    if not (self.project_id or self.component_id):
      self.__errors__.append(('project_id', 'required'))
    if not self.due_date:
      self.__errors__.append(('due_date', 'required'))
    
    return self.__errors__
  
  @property
  def path(self):
    path = []
    if self.component_id:
      return self.component.path
    elif self.project_id:
      return self.project.path
