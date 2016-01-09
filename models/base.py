#!/usr/bin/python
# -*- coding: utf-8 -*-

#import uuid
from application import db
from sqlalchemy import orm
import time

class BaseModel:
	STATUS_ACTIVE = 1
	STATUS_PRIVATE = 2
	STATUS_DELETED = 4
	
	@classmethod
	def _r(cls, integerValue, limit=16):
		return [i for i in range(limit) if i & integerValue]
	
	salt = '34o8uy6tp43htg54eytr5'
	
	def isNew(self):
		if hasattr(self, 'id') and self.id:
			return False
		else:
			return True
	
	def validate(self):
		return []
	
	def hasStatus(self, *args):
		for arg in args:
			if arg and not self.status & arg:
				return False
		return True
	
	@property
	def errors(self):
		if hasattr(self, '__errors__'):
			return self.__errors__
		else:
			return []
	
	def save(self):
		if hasattr(self, 'pre_save'):
			if self.pre_save() == False:
				return
		
		if self.isNew():
			self.__create()
		else:
			self.__update()
		
		if hasattr(self, 'post_save'):
			self.post_save()
	
	def __create(self):
		if hasattr(self, 'pre_create'):
			if self.pre_create() == False:
				return
		
		if hasattr(self, 'created') and not self.created:
			self.created = int(time.time())
		
		db.session.add(self)
		db.session.commit()
	
	def __update(self):
		if hasattr(self, 'pre_update'):
			if self.pre_update() == False:
				return
		
		if hasattr(self, 'modified'):
			self.modified = int(time.time())
		
		db.session.commit()
	
	def delete(self):
		if hasattr(self, 'pre_delete'):
			if self.pre_delete() == False:
				return
		
		db.session.delete(self)
		db.session.commit()
		
		if hasattr(self, 'post_delete'):
			self.post_delete()
