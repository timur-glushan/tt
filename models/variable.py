import json
from application import db
from models.base import BaseModel

class Variable(db.Model, BaseModel):
	VARIABLE_LANGUAGE_DEFAULT = 'language_default'
	
	__tablename__ = 'variables'
	#__table_args__ = {'mysql_charset': 'utf8'}
	__table_args__ = (db.UniqueConstraint('scope', 'name'), {'mysql_charset': 'utf8'})
	
	scope = db.Column(db.String(80), primary_key=True)
	name = db.Column(db.String(80), primary_key=True)
	raw_value = db.Column(db.Text)
	
	def __repr__(self):
		return self.value
	
	@property
	def value(self):
		value = None
		if self.raw_value:
			try:
				value = json.loads(self.raw_value)
			except Exception as e:
				value = None
		return value
	
	@value.setter
	def value(self, value):
		self.raw_value = json.dumps(value)
	
	def validate(self):
		self.__errors__ = []
		if not self.scope:
			self.__errors__.append(('scope', 'required'))
		if not self.name:
			self.__errors__.append(('name', 'required'))
		try:
			json.loads(self.raw_value)
		except Exception as e:
			self.__errors__.append(('value', 'not a json'))
		return self.__errors__
