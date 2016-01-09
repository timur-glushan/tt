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
@app.route('/administration/variable', methods=['GET', 'POST'])
@app.authorized_group('administrator')
def variable_index():
  from models.variable import Variable
  
  title = g._t( 'variables' )
  breadcrumbs = (
    (g._t( 'administration' ), url_for( 'administration_index' )),
    (title, "#")
  )
  
  varList = Variable.query.order_by(Variable.name).all()
  return render_template( 'administration/variable/index.html', title=title, breadcrumbs=breadcrumbs, varList=varList )

@app.route('/administration/variable/add', endpoint='variable_add', methods=['GET', 'POST'])
@app.route('/administration/variable/<name>/<scope>/edit', methods=['GET', 'POST'])
@app.authorized_group('administrator')
def variable_edit(name=None, scope=None):
  from models.variable import Variable
  
  if name and scope:
    variable = Variable.query.filter_by(name=urllib.unquote_plus(name), scope=urllib.unquote_plus(scope)).first_or_404()
  else:
    variable = Variable()
  
  errors = []
  
  if request.method == 'POST' and request.values.get( 'csrf_token', None ):
    variable.scope = request.form.get('variable_scope')
    variable.name = request.form.get('variable_name')
    variable.raw_value = request.form.get('variable_raw_value')
    errors = variable.validate()
    if not len(errors):
      variable.save()
      flash( g._t('variable submit success'))
      return redirect(url_for('variable_index'))
  
  if name:
    title = g._t('edit')
  else:
    title = g._t('add')
  breadcrumbs = (
    (g._t('administration'), url_for('administration_index')),
    (g._t('variables'), url_for('variable_index')),
    (title, "#")
  )
  
  return render_template('administration/variable/edit.html', title=title, breadcrumbs=breadcrumbs, variable=variable, errors=errors)

@app.route('/administration/variable/<name>/<scope>/delete', methods=['GET', 'POST'])
@app.authorized_group('administrator')
def variable_delete(name, scope):
  from models.variable import Variable
  
  variable = Variable.query.filter_by(name=urllib.unquote_plus(name), scope=urllib.unquote_plus(scope)).first_or_404()
  
  variable.delete()
  flash( g._t( 'variable delete success' ) )
  return redirect( url_for( 'variable_index' ) )
