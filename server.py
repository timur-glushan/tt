#!/usr/bin/python
#-*- coding: utf-8  -*-
from cherrypy import wsgiserver
from application import app

dispatcher = wsgiserver.WSGIPathInfoDispatcher( { '/':app } )
server = wsgiserver.CherryPyWSGIServer( ( app.config['HOST'], app.config['PORT'] ), dispatcher )

if __name__ == '__main__':
  try:
    print 'Starting server at %s:%d' % ( app.config['HOST'], app.config['PORT'] )
    server.start()
  except KeyboardInterrupt:
    server.stop()
