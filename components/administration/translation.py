from application import app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import urllib

#helpers section



# request hooks section
@app.before_request
def translation_before_request():
  pass

@app.teardown_request
def translation_teardown_request( exception ):
  pass



# routes section
@app.route('/administration/translation', methods=['GET', 'POST'])
@app.authorized_group('administrator')
def translation_index():
  from models.translation import Translation
  
  title = g._t('translations')
  breadcrumbs = (
    (g._t('administration'), url_for('administration_index')),
    (title, "#"),
  )
  
  translationList = {}
  for translation in Translation.query.all():
    if not translationList.has_key(translation.name):
      translationList[translation.name] = {}
    translationList[translation.name][translation.language] = translation.value
  localeList = g._var('languages', scope='translation', default=[])
  return render_template('administration/translation/index.html', title=title, breadcrumbs=breadcrumbs, translationList=translationList, localeList=localeList )

@app.route('/administration/translation/add', endpoint='translation_add', methods=['GET', 'POST'])
@app.route('/administration/translation/<name>/edit', methods=['GET', 'POST'])
@app.authorized_group('administrator')
def translation_edit(name=None):
  from models.translation import Translation
  import urllib
  
  localeList = g._var('languages', scope='translation', default=[])
  translationList = {}
  
  for language in localeList:
    translation = None
    if name:
      name = urllib.unquote_plus(name)
      translation = Translation.query.filter_by(name=urllib.unquote_plus(name), language=language).first() or Translation(name=urllib.unquote_plus(name), language=language)
    if not translation:
      translation = Translation(language=language)
    translationList[language] = translation
  
  if request.method == 'POST' and request.form.get('csrf_token', None):
    for language in localeList:
      translationList[language].name = request.form.get('translation_name', None)
      translationList[language].value = request.form.get('translation_language_'+language, None)
      translationList[language].save()
    flash( g._t('translation submit success'))
    return redirect(url_for('translation_index'))
  
  if name:
    title = g._t('edit')
  else:
    title = g._t('add')
  breadcrumbs = (
    (g._t('administration'), url_for('administration_index')),
    (g._t('translations'), url_for('translation_index')),
    (title, "#")
  )
  
  return render_template('administration/translation/edit.html', title=title, breadcrumbs=breadcrumbs, localeList=localeList, translationList=translationList, name=name)

@app.route('/administration/translation/<name>/delete', methods=['GET', 'POST'])
@app.authorized_group('administrator')
def translation_delete(name):
  from models.translation import Translation
  import urllib
  
  name = urllib.unquote_plus(name)
  for translation in Translation.query.filter_by(name=name).all():
    translation.delete()
  flash(g._t('translation delete success'))
  return redirect(url_for('translation_index'))
