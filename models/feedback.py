from application import db
from models.base import BaseModel

class Feedback(db.Model, BaseModel):
	__tablename__ = 'feedback'
	__table_args__ = {'mysql_charset': 'utf8'}
	
	id = db.Column(db.Integer, primary_key=True)
	account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', onupdate='cascade', ondelete='cascade'), nullable=False)
	subject = db.Column(db.UnicodeText(128))
	message = db.Column(db.UnicodeText)
	created = db.Column(db.Integer)
	modified = db.Column(db.Integer)
	
	account = db.relationship('Account', passive_updates=False, backref=db.backref('feedback', cascade="all, delete, delete-orphan"))
	
	def __init__(self, **kwargs):
		for k, v in kwargs.items():
			if hasattr(self, k):
				setattr(self, k, v)
	
	def validate(self):
		errors = []
		if not self.subject:
			errors.append(('subject', 'required'))
		if not self.message:
			errors.append(('message', 'required'))
		return errors
	
	def __repr__(self):
		return '=' + self.value
