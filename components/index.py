from application import app
from flask import Flask, request, Response, session, g, redirect, url_for, abort, render_template, render_template_string, flash
import json
import MySQLdb
import MySQLdb.cursors

#helpers section
def _dbconnect():
	connection = MySQLdb.connect(host=app.config['DATABASE']['host'],user=app.config['DATABASE']['user'],passwd=app.config['DATABASE']['passwd'], db=app.config['DATABASE']['schema'], charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)
	connection.autocommit( True )
	setattr( g, '__dbc__', connection )
	cursor = getattr( g, '__dbc__' ).cursor()
	setattr( g, '__cur__', cursor )

def _dbexec( query, *arg, **kwarg ):
	try:
		cursor = getattr( g, '__dbc__' ).cursor()
	except (AttributeError, MySQLdb.OperationalError):
		_dbconnect()
		cursor = getattr( g, '__dbc__' ).cursor()
	cursor.execute( query, *arg, **kwarg )
	return cursor

def _db( command=None, *arg, **kwarg ):
	if command == 'close':
		if hasattr( g, '__cur__' ):
			delattr( g, '__cur__' )
		if hasattr( g, '__dbc__' ):
			getattr( g, '__dbc__' ).close()
			delattr( g, '__dbc__' )
	elif command == 'commit':
		return
	elif command is not None:
		return getattr( getattr( g, '__dbc__' ), command )( *arg, **kwarg )
	else:
		try:
			getattr( g, '__dbc__' ).cursor()
		except (AttributeError, MySQLdb.OperationalError):
			_dbconnect()
		return getattr( g, '__cur__' )

def _constant( name=None, group=None ):
	import datetime
	import time
	
	nowDate = datetime.datetime.now()
	midnightDate = datetime.datetime( year=nowDate.year, month=nowDate.month, day=nowDate.day )
	midnightTime = int( midnightDate.strftime( '%s' ) )
	midnightDateString = midnightDate.strftime( '%Y-%m-%d' )
	
	tomorrowDate = midnightDate + datetime.timedelta(days=1)
	tomorrowTime = int( tomorrowDate.strftime( '%s' ) )
	tomorrowDateString = tomorrowDate.strftime( '%Y-%m-%d' )
	
	thisWeekDate = midnightDate - datetime.timedelta(days=midnightDate.weekday())
	thisWeekTime = thisWeekDate.strftime( '%s' )
	thisWeekDateString = thisWeekDate.strftime( '%Y-%m-%d' )
	
	thisMonthDate = midnightDate - datetime.timedelta(days=(midnightDate.day-1))
	thisMonthTime = thisMonthDate.strftime( '%s' )
	thisMonthDateString = thisMonthDate.strftime( '%Y-%m-%d' )
	
	if nowDate.month == 1:
		lastMonthDate = datetime.datetime( year=nowDate.year-1, month=12, day=1 )
	else:
		lastMonthDate = datetime.datetime( year=nowDate.year, month=nowDate.month-1, day=1 )
	lastMonthTime = lastMonthDate.strftime( '%s' )
	lastMonthDateString = lastMonthDate.strftime( '%Y-%m-%d' )
	
	thisYearDate = datetime.datetime( year=nowDate.year, month=1, day=1 )
	thisYearTime = thisYearDate.strftime( '%s' )
	thisYearDateString = thisYearDate.strftime( '%Y-%m-%d' )
	
	lastYearDate = datetime.datetime( year=thisYearDate.year-1, month=1, day=1 )
	lastYearTime = lastYearDate.strftime( '%s' )
	lastYearDateString = lastYearDate.strftime( '%Y-%m-%d' )
	
	foreverDate = datetime.datetime( year=2013, month=1, day=1 )
	foreverTime = foreverDate.strftime( '%s' )
	foreverDateString = foreverDate.strftime( '%Y-%m-%d' )
	
	CONSTANTS = {
		'TS':{
			'TOMORROW':tomorrowTime,
			'NOW':int(time.time()),
			'TODAY':midnightTime,
			'WEEK':thisWeekTime,
			'MONTH':thisMonthTime,
			'LASTMONTH':lastMonthTime,
			'YEAR':thisYearTime,
			'LASTYEAR':lastYearTime,
			'FOREVER':foreverTime,
		},
		'DATE':{
			'TOMORROW':tomorrowDateString,
			'TODAY':midnightDateString,
			'WEEK':thisWeekDateString,
			'MONTH':thisMonthDateString,
			'LASTMONTH':lastMonthDateString,
			'YEAR':thisYearDateString,
			'LASTYEAR':lastYearDateString,
			'FOREVER':foreverDateString,
		},
		'PERIOD':{
			'TODAY':'today',
			'WEEK':'week',
			'MONTH':'month',
			'LASTMONTH':'lastmonth',
			'YEAR':'year',
			'LASTYEAR':'lastyear',
			'FOREVER':'forever',
		}
	}
	return CONSTANTS

def _pager( items, url=None, limit=10 ):
	import math
	if url is None: url = request.path
	pages = int( math.ceil( float( len( items ) ) / float( limit ) ) )
	if pages <= 1:
		return ( items, [] )
	end = int( request.args.get( 'page', 1 ) ) * limit
	if end < limit: end = limit
	start = int( end ) - int( limit )
	links  = [ url+( ('?' in url) and '&' or '?' ) + 'page='+str( p + 1 ) for p in range( pages ) ]
	return ( items[start:end], links )

def _date( timestamp, dateFormat='%Y-%m-%d %H:%M:%S' ):
	import datetime
	return timestamp and str(timestamp).isdigit() and datetime.datetime.fromtimestamp( int( str(timestamp).split('.')[0] ) ).strftime( dateFormat ) or ''

def _str( *subs ):
	return ' '.join([unidecode( sub or '' ) for sub in subs])

def _query( *args, **kwargs ):
	from libraries.couchDB import CouchDB
	
	return CouchDB.query( *args, **kwargs )

def _t(name, language=None, nodefault=False):
	from models.translation import Translation
	from helpers.account import AccountHelper
	
	if not language:
		language = AccountHelper.getPreference('language')
	
	translation = Translation.query.filter_by(name=name, language=language).first()
	if translation:
		return translation.value
	else:
		return (nodefault == False) and ':'+name or None

def _var(name, scope=None, default=None):
	from models.variable import Variable
	
	if not scope:
		scope = "general"
	
	variable = Variable.query.filter_by(name=name, scope=scope).first()
	if variable:
		return variable.value
	else:
		return default

def _reportdate( timestamp ):
	import datetime
	return timestamp and str( timestamp ).isdigit() and unicode(datetime.datetime.fromtimestamp( int( str( timestamp ).split('.')[0] ) ).strftime('%Y-%m-%d')) or ''

def _timestamp( datestring ):
	import datetime
	return datetime.datetime.strptime( datestring, '%Y-%m-%d' ).strftime( '%s' )

def _is_active_path( path ):
	return str( request.path ).startswith( str( path ) )

def _is_holiday( timestamp ):
	import datetime
	if str( timestamp ).isdigit():
		return datetime.datetime.fromtimestamp( int( str( timestamp ).split('.')[0] ) ).weekday() > 4
	else:
		return datetime.datetime.strptime( timestamp, '%Y-%m-%d' ).weekday() > 4

def _is_vacation(project):
	from helpers.project import ProjectHelper
	
	return ProjectHelper.projectIsHoliday(project)
	
	
	import datetime
	if str( timestamp ).isdigit():
		return datetime.datetime.fromtimestamp( int( str( timestamp ).split('.')[0] ) ).weekday() > 4
	else:
		return datetime.datetime.strptime( timestamp, '%Y-%m-%d' ).weekday() > 4

def _help_message():
	helpMessage = g._t('help-'+g.current_page, nodefault=True) or g._t('help-application', nodefault=True)
	#if helpMessage:
	#	helpMessage = render_template_string(helpMessage.decode('string_escape'), account=g.account)
	return helpMessage



def _get_preference(name):
	from helpers.account import AccountHelper
	
	return AccountHelper.getPreference(name)

def _isset_preference(name):
	from helpers.account import AccountHelper
	
	return AccountHelper.issetPreference(name) is not False

def _get_chinese_cookie():
	from helpers.account import AccountHelper
	
	if not hasattr(request, 'chinese_cookie'):
		cc = AccountHelper.getChineseCookie()
		setattr(request, 'chinese_cookie', cc)
	return getattr(request, 'chinese_cookie')



#template filters section
@app.template_filter('urlencode')
def application_urlencode_filter( s ):
	import urllib
	
	if type(s) in [int, float]:
		return str(s)
	s = s.encode( 'utf8' )
	s = urllib.quote_plus( s )
	return s



@app.template_filter('json')
def application_json_filter( s ):
	import json
	
	return json.dumps(s)



#context processors section
@app.context_processor
def application_context_processor():
	return dict( date_format=_date, _date=_date, _str=_str, _t=_t, _db=_db, _is_active_path=_is_active_path, _var=_var, _is_holiday=_is_holiday, _is_vacation=_is_vacation, _help_message=_help_message, _get_preference=_get_preference, _isset_preference=_isset_preference, _get_chinese_cookie=_get_chinese_cookie)



# request hooks section
@app.before_request
def application_before_request():
	if request.headers.get('X-Requested-With', None) == 'XMLHttpRequest':
		setattr(request, 'is_ajax', True)
	else:
		setattr(request, 'is_ajax', False)
	
	g._str = _str
	g._pager = _pager
	g._date = _date
	g._reportdate = _reportdate
	g._timestamp = _timestamp
	g._query = _query
	g._constant = _constant
	g._t = _t
	g._var = _var
	g._is_active_path = _is_active_path
	g.SUPPRESSED_ACTION = True
	g.current_page = request.url_rule and request.url_rule.endpoint and request.url_rule.endpoint.replace('_', '-') or 'guest'

@app.teardown_request
def application_teardown_request( exception ):
	pass



# request hooks section



# routes section
@app.route('/application/vacation', methods=['GET', 'POST'])
def application_vacation():
	from helpers.project import ProjectHelper
	
	data = []
	
	for component in ProjectHelper.listVacationComponents():
		data.append((component.path, component.title))
	
	data = dict(data)
	
	return Response(json.dumps({'status':200, 'description':'OK', 'data':data, 'errors':[]}), mimetype='application/json')



@app.route('/application/holidays', methods=['GET', 'POST'])
def application_holidays():
	from models.translation import Translation
	
	data = _var(name='holidays', scope='date', default={'weekdays':[], 'monthdays':[], 'dates':[]})
	weekdays = []
	for day in data['weekdays']:
		if day<6:
			day = day+1
		else:
			day = 0
		weekdays.append(day)
	
	data['weekdays'] = weekdays
	
	return Response(json.dumps({'status':200, 'description':'OK', 'data':data, 'errors':[]}), mimetype='application/json')



@app.route('/application/translations', methods=['GET', 'POST'])
def application_translations():
	from models.translation import Translation
	
	from helpers.account import AccountHelper
	
	language = AccountHelper.getPreference('language')
	
	data = dict([(translation.name, translation.value) for translation in Translation.query.filter_by(language=language).all()])
	
	return Response(json.dumps({'status':200, 'description':'OK', 'data':data, 'errors':[]}), mimetype='application/json')



# routes section
@app.route('/', methods=['GET', 'POST'])
def application_index():
	if g.account and g.account.id:
		return redirect(url_for('report_index', account_id=g.account.id))
	else:
		return redirect( url_for( 'session_signin' ) )
		#return render_template( 'application/index.html' )

@app.route('/about', methods=['GET'])
def application_about():
	title = g._t('about service')
	
	return render_template('application/about.html', title=title)

@app.route('/not_implemented', methods=['GET', 'POST'])
def application_NOT_IMPLEMENTED():
	return render_template('application/not_implemented.html')

@app.errorhandler( 400 )
@app.errorhandler( 401 )
@app.errorhandler( 403 )
@app.errorhandler( 404 )
def application_error_40x( e ):
	return render_template('application/error_40x.html', title=str( e ), error=e), e.code

@app.errorhandler( 500 )
@app.errorhandler( 501 )
@app.errorhandler( 502 )
@app.errorhandler( 503 )
def application_error_50x( e ):
	return render_template('application/error_50x.html', title='Ooops!', error=e), 500
