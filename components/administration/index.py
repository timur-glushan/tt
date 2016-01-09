from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import urllib

#helpers section



# request hooks section
@app.before_request
def administration_before_request():
  pass

@app.teardown_request
def administration_teardown_request( exception ):
  pass



# routes section
@app.route( '/administration/', methods=['GET', 'POST'] )
@app.authorized_group('administrator','privileged_manager')
def administration_index():
  title = g._t('administration')
  return render_template('administration/index/index.html', title=title)
