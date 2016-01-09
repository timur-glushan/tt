#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup

#helpers section



# request hooks section
@app.before_request
def session_before_request():
	pass

@app.teardown_request
def session_teardown_request( exception ):
	pass



# routes section
@app.route( '/test/', methods=['GET', 'POST'] )
def test_index():
	title = 'Testing'
	data = Markup('<br/>'.join([
		'<a href="%s">%s</a>' % (url_for('test_index'), url_for('test_index')),
		'<a href="%s">%s</a>' % (url_for('test_permissions_index'), url_for('test_permissions_index'))
	]))
	
	return render_template( 'test/index.html', title=title, data=data )



@app.route('/test/endpoints', methods=['GET', 'POST'])
def test_endpoints():
	title = 'Endpoints'
	
	links = []
	for rule in app.url_map.iter_rules():
		if "GET" in rule.methods and ((rule.defaults and len(rule.defaults) >= len(rule.arguments)) or (not rule.arguments)):
			url = url_for(rule.endpoint)
			links.append((url, rule.endpoint))
	data = '<br/>'.join(["<b>%s:</b> %s" % (endpoint, link) for link,endpoint in links])
	data = Markup(data)
	
	return render_template('test/index.html', title=title, data=data)



def _install_translation_translate(key, value, src='en', dest='ru'):
	#http://syslang.com/?src=en&dest=ru&text=Account+name&email=timpeor&password=,kzlcndj&outformat=json
	from httplib2 import Http
	from urllib import urlencode
	from time import sleep
	import json
	import shelve
	
	print '[TRANSLATION]', src+' > '+dest, key
	
	sh = shelve.open('data/translations.db', writeback=True)
	if sh.has_key(key) and sh[key].has_key(dest):
		return sh[key][dest]
	
	if not sh.has_key(key):
		sh[key] = {src: value}
	elif not sh[key].has_key(src):
		sh[key][src] = value
	
	data = {
		'src': src,
		'dest': dest,
		'text': value,
		'email': 'timpeor',
		'password': ',kzlcndj',
		'outformat': 'json'
	}
	
	try:
		sleep(3)
		h = Http(".cache")
		resp, content = h.request("http://syslang.com/?"+urlencode(data), "GET")
		responseData = json.loads(content)
		translation = responseData['translation']
		sh[key][dest] = translation
		sh.sync()
		sh.close()
		return translation
	except Exception as e:
		print '[TRANSLATION:EXCEPTION]', str(e)
		return value



@app.route( '/test/translations_repr', methods=['GET', 'POST'] )
def test_translations_repr():
	title = 'Testing | Translations'

	import csv
	csvfile = open('data/t3.csv', 'rb')
	csvdata = csv.reader(csvfile, delimiter=',', quotechar='"')
	
	data = "{\n"
	for item in csvdata:
		if not len(item):
			continue
		data = data + "\t'" + item[0] + "': {\n"
		
		data = data + "\t\t'en': u'" + (len(item)>1 and str(item[1]) or '') + "',\n"
		data = data + "\t\t'ru': u'" + (len(item)>2 and str(item[2]) or '') + "',\n"
		data = data + "\t\t'uk': u'" + (len(item)>3 and str(item[3]) or '') + "',\n"
		print '['+item[0]+']', \
				(len(item)>1 and str(item[1]) or ''), \
				(len(item)>2 and str(item[2]) or ''), \
				(len(item)>3 and str(item[3]) or '')
		
		data = data + (item[0] == 'year' and "\t}\n" or "\t},\n")
	data = data + "}"
	data = data.decode('utf-8')
	
	#import json
	#data = json.dumps([row for row in csvdata])
	
	"""
	itemList = _install_translation_data_source()
	
	data = "{\n"
	for item in itemList:
		data = data + "\t'" + item['name'] + "': {\n"
		data = data + "\t\t'en': u'" + item['value'].replace("'", "\\'") + "',\n"
		valueRU = _install_translation_translate(item['name'], item['value'], src='en', dest='ru')
		data = data + "\t\t'ru': u'" + valueRU + "',\n"
		valueUA = _install_translation_translate(item['name'], item['value'], src='en', dest='ua')
		data = data + "\t\t'ua': u'" + valueUA + "'\n"
		if item['name'] == 'year':
			data = data + "\t},\n"
		else:
			data = data + "\t}\n"
	data = data + "}"
	
	"""
	
	from flask import Markup
	data = Markup('<pre>'+data+'</pre>')
	
	return render_template( 'test/index.html', title=title, data=data )
