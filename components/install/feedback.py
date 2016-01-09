#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

@app.install('install_feedback_db')
def install_feedback_db():
  """Create the DB schema for Feedback model"""
  from application import db
  from models.feedback import Feedback
  
  db.create_all()



@app.install('install_feedback_data')
def install_feedback_data():
  """Create all the required feedback if not defined"""
  from application import db
  from models.feedback import Feedback
  
  itemList = [
    #{'scope': 'roles', 'name': 'member', 'raw_value': '[]'}
  ]
  
  for item in itemList:
    feedback = Feedback.query.filter_by(scope=item['scope'], name=item['name']).first()
    if not feedback:
      feedback = Feedback(**item)
      feedback.save()
