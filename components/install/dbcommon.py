#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

@app.install('install_couchdb_common_doc')
def install_couchdb_common_doc():
	"""Create the couchdb common documents - users, projects, etc."""
	from application import app
	from libraries.couchDB import CouchDB
	import json
	
	couchdb = CouchDB(
		host=app.config['COUCHDB']['host'], 
		database=app.config['COUCHDB']['database'], 
		name=app.config['COUCHDB']['name'], 
		password=app.config['COUCHDB']['password']
	)
	
	commonDoc = {
		"timur.glushan": 
"""{
   "_id": "timur.glushan",
   "first_name": "Timur",
   "last_name": "Glushan",
   "notify": {
       "interval": 0.16666666666666666,
       "unreported": 2,
       "after": "2014-01-16T18:58:28Z"
   },
   "id": "timur.glushan",
   "last_report": "04e0fb52d00774303b81f6ebbc9c409e",
   "password": "cde4aedd40d0e6c76bc22b3a199c9b62",
   "type": "employee",
   "email": "timur.glushan@p-product.com"
}""",
		
		
		
		"MGM": 
"""{
   "_id": "MGM",
   "info": null,
   "title": "Management records",
   "users": [
       "leonid.usov",
       "lana.ieremieva",
       "nadyam",
       "gleb.dzyuba"
   ],
   "partitions": {
       "VAC": {
           "": "Vacation",
           "KZOT": "Days off by KZoT",
           "NP": "Unpaid Leave",
           "EDU": "Education"
       },
       "SICK": "Sick Leave"
   },
   "type": "project"
}""",
		
		"OUT": 
"""{
   "_id": "OUT",
   "title": "Hours sink for time that an employee was available in XMPP but was neither doing work nor in stand-by",
   "type": "project"
}""",
		
		
		
		"INT/EDU": 
"""{
   "_id": "INT/EDU",
   "title": "Self Education. Report summary is obligatory!",
   "type": "project"
}""",
		
		"INT/IDLE": 
"""{
   "_id": "INT/IDLE",
   "title": "Hours sink for time that an employee is online and available but doesn't have a specific task",
   "type": "project"
}""",
		
		"INT/OFFICE": 
"""{
   "_id": "INT/OFFICE",
   "description": "",
   "title": "shopping for office; psychotherapy; interview; internal caring",
   "members": {
   },
   "active": true,
   "type": "project",
   "id": "INT/OFFICE",
   "partitions": {
   }
}"""
	}
	
	for docID, doc in commonDoc.items():
		if not couchdb.getDocument(docID):
			couchdb.putDocument(docID, json.loads(doc))
