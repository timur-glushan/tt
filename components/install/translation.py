#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

@app.install('install_translation_db')
def install_translation_db():
	"""Create the DB schema for Translation model"""
	from application import db
	from models.translation import Translation
	
	db.create_all()



@app.install('install_translation_data')
def install_translation_data():
	"""Create all the required translations if not defined"""
	from application import db
	from models.translation import Translation
	
	import csv
	csvFile = open('data/t3.csv', 'rb')
	csvData = csv.reader(csvFile, delimiter=',', quotechar='"')
	csvHeaderSkipped = False
	for item in csvData:
		if not csvHeaderSkipped:
			csvHeaderSkipped = True
			continue
		
		if not len(item):
			continue
		
		name = item[0]
		valueDict = {
			'en': (len(item)>1 and str(item[1]) or ''),
			'ru': (len(item)>2 and str(item[2]) or ''),
			'uk': (len(item)>3 and str(item[3]) or '')
		}
		
		for language, value in valueDict.items():
			
			translation = Translation.query.filter_by(language=language, name=name).first()
			if not translation:
				translation = Translation()
				translation.language = language
				translation.name = name
				translation.value = value
				translation.save()
			else:
				translation.value = value
				translation.save()
			
			print '[MIGRATION:TRANSLATION]', name, language, translation
