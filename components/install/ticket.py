#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

@app.install('install_ticket_db')
def install_report_db():
  """Create the DB schema for Ticket model"""
  from application import db
  from models.ticket import Ticket
  
  db.create_all()
