from application import db
from models.base import BaseModel

class Translation(db.Model, BaseModel):
  __tablename__ = 'translations'
  __table_args__ = (db.UniqueConstraint('language', 'name'), {'mysql_charset': 'utf8'})
  
  language = db.Column(db.String(64), primary_key=True)
  name = db.Column(db.String(80), primary_key=True)
  value = db.Column(db.UnicodeText)

  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      if hasattr(self, k):
        setattr(self, k, v)

  def __repr__(self):
    return '=' + self.value
