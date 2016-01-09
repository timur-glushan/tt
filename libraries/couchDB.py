from couchdb.client import Server, Document
from hashlib import md5
import pickle

class CouchDB:
	host = 'http://kharkiv.p-product.com:5984/'
	#host = 'http://127.0.0.1:5984/'
	connection = None
	database = 'run4'
	queryCache = {}
	logEnabled = False
	logFile = 'db.log'
	
	@classmethod
	def log( cls, *messages ):
		if not cls.logEnabled:
			return
		from time import time
		logFileHandler = open( cls.logFile, 'a' )
		message = '[%s] %s' % ( str( int( time() ) ), ' '.join( [ str( message ) for message in messages ] ) )
		logFileHandler.write( message+'\n' )
		logFileHandler.close()
	
	
	
	def __init__(self, host=None, database=None, name=None, password=None):
		if not host:
			self.host = 'http://127.0.0.1:5984'
		if not database:
			raise Exception('Database name required for CouchDB connection')
		self.host = host
		self.database = database
		self.name = name
		self.password = password
	
	
	
	def getConnection( self, host=None ):
		if not self.connection:
			self.log( 'connecting...' )
			self.connection = Server( self.host )
			if (self.name is not None) and (self.password is not None):
				self.connection.resource.credentials = (self.name, self.password)
			self.log( 'connected!', self.connection  )
		return self.connection
	
	
	
	def getDatabase( self, database=None ):
		self.log( 'getting DB', database )
		if database:
			self.database = database
		return self.getConnection()[self.database]
	
	
	
	def getDocument( self, documentId ):
		self.log( 'getting DB Document', documentId )
		return self.getDatabase().get( documentId )
	
	
	
	def putDocument( self, documentId, document ):
		storedDocument = self.getDatabase().get( documentId )
		if storedDocument:
			storedDocument.update( document )
		else:
			storedDocument = document
		self.getDatabase()[documentId] = storedDocument
		return ( documentId, storedDocument )
	
	
	
	def createDocument( self, document ):
		from uuid import uuid4
		documentId = uuid4().hex
		return self.putDocument( documentId, document )
	
	
	
	def deleteDocument( self, documentId ):
		print '[CDB] Delete'
		document = self.getDatabase().get( documentId )
		print '[CDB] Delete doc: ', document
		if document:
			del self.getDatabase()[documentId]
		return True
