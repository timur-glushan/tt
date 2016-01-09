#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

@app.install('install_report_db')
def install_report_db():
  """Create the DB schema for Report model"""
  from application import db
  from models.report import Report
  
  db.create_all()
