#!/usr/bin/python
# -*- coding: utf-8 -*-

from application import db
from models.base import BaseModel
#import datetime
#import time

class Report(db.Model, BaseModel):
	__tablename__ = 'reports'
	__table_args__ = {'mysql_charset': 'utf8'}
	
	id = db.Column(db.Integer, nullable=False, primary_key=True)
	offline = db.Column(db.Boolean, nullable=True, default=True)
	duration = db.Column(db.Float(2), nullable=False, default=0.0)
	due_date = db.Column(db.String(64), nullable=False)
	summary = db.Column(db.Text, nullable=True)
	project_id = db.Column(db.Integer, db.ForeignKey('projects.id', onupdate='cascade', ondelete='cascade'), nullable=False)
	component_id = db.Column(db.Integer, db.ForeignKey('components.id', onupdate='cascade', ondelete='cascade'), nullable=False)
	account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', onupdate='cascade', ondelete='cascade'), nullable=False)
	reporter_id = db.Column(db.Integer, db.ForeignKey('accounts.id', onupdate='set null', ondelete='set null'), nullable=True)
	created = db.Column(db.Integer, nullable=True)
	modified = db.Column(db.Integer, nullable=True)
	status = db.Column(db.Integer, nullable=False, default=BaseModel.STATUS_ACTIVE)
	
	project = db.relationship('Project', passive_updates=db._config.passive_updates, lazy='select')
	component = db.relationship('Component', passive_updates=db._config.passive_updates, lazy='select')
	account = db.relationship('Account', foreign_keys=[account_id], passive_updates=db._config.passive_updates, lazy='select')
	reporter = db.relationship('Account', foreign_keys=[reporter_id], passive_updates=db._config.passive_updates, lazy='select')
	
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
	
	@property
	def hours(self):
		return float(int(self.duration or 0))
	
	@property
	def minutes(self):
		return float(((float(self.duration or 0) * 3600.0) % 3600.0) / 60)
		#return float(((float((self.duration or 0)) * 3600.0) % 3600.0) / 60)
