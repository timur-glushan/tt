#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

def install_db_create_all():
	"""Create the DB schema for all models"""
	from application import db
	from models.feedback import Feedback
	from models.translation import Translation
	from models.variable import Variable
	from models.account import Account, Preference, Group
	from models.project import Project, Component, Label, Role, Membership
	from models.report import Report
	
	db.create_all()

