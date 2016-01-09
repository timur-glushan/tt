#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app
import json

@app.update('2.1.0.1', 'update_variable_data_add_maintainer_feedback')
def update_variable_data_add_maintainer_feedback():
  """Create all the required variables if not defined"""
  from application import db
  from models.variable import Variable
  
  itemList = [
    {'scope': 'general', 'name': 'feedback', 'raw_value': json.dumps('timur.glushan@p-product.com')},
    {'scope': 'general', 'name': 'maintainer', 'raw_value': json.dumps('Timur Glushan')},
    {'scope': 'general', 'name': 'thanks_to', 'raw_value': json.dumps(['Lana Glushan', 'Nadya Mezenina', 'Gleb Dzyba', 'Leonid Usov'])}
  ]
  
  for item in itemList:
    variable = Variable.query.filter_by(scope=item['scope'], name=item['name']).first()
    if not variable:
      variable = Variable()
      variable.scope = item['scope']
      variable.name = item['name']
      variable.raw_value = item['raw_value']
      variable.save()
    else:
      variable.raw_value = item['raw_value']
      variable.save()



@app.update('2.1.0.1', 'update_translation_data_add_about_page_translations')
def update_translation_data_add_about_page_translations():
  """Create all the required translations if not defined"""
  from application import db
  from models.translation import Translation
  
  itemDict = {
    'about service': {
      'en': 'About T<sup>3</sup>',
      'ru': 'О сервисе T<sup>3</sup>',
      'uk': 'Про сервіс T<sup>3</sup>'
    },
    'and others': {
      'en': 'and many others',
      'ru': 'и многим другим',
      'uk': 'та багатьом іншим'
    },
    'changes_v2.1.0.1': {
      'en': """<ul>
          <li></li>
          <li></li>
          <li></li>
          <li></li>
          <li></li>
          <li></li>
          <li></li>
          <li>Added the "About" page</li>
        </ul>""",
      'ru': '',
      'uk': ''
    },
    'common:changes': {
      'en': 'Changes',
      'ru': 'Изменения',
      'uk': 'Що нового'
    },
    'common:version_short': {
      'en': 'ver',
      'ru': 'ver',
      'uk': 'ver'
    },
    'thanks to': {
      'en': 'Thanks to',
      'ru': 'Отдельная благодарность',
      'uk': 'Дуже дякую'
    }
  }
  
  for name, itemDictValue in itemDict.items():
    for language, value in itemDictValue.items():
      translation = Translation.query.filter_by(name=name, language=language).first()
      if not translation:
        translation = Translation()
        translation.language = language
        translation.name = name
        translation.value = value
        translation.save()
      else:
        translation.value = value
        translation.save()



@app.update('2.1.0.2', 'update_translation_changelist_for_undelete')
def update_translation_changelist_for_undelete():
  """Create all the required translations if not defined"""
  from application import db
  from models.translation import Translation
  
  itemDict = {
    'changes_v2.1.0.2': {
      'en': """<ul>
          <li>Added the un-delete feature</li>
        </ul>""",
      'ru': """<ul>
          <li>Добавлена возможность отмены удаления</li>
        </ul>""",
      'uk': """<ul>
          <li>Додано можливість скасувати видалення</li>
        </ul>""",
    }
  }
  
  for name, itemDictValue in itemDict.items():
    for language, value in itemDictValue.items():
      translation = Translation.query.filter_by(name=name, language=language).first()
      if not translation:
        translation = Translation()
        translation.language = language
        translation.name = name
        translation.value = value
        translation.save()
      else:
        translation.value = value
        translation.save()



@app.update('2.1.0.3', 'update_floats_separator')
def update_floats_separator():
  """Create all the required translations if not defined"""
  from application import db
  from models.translation import Translation

  itemDict = {
    'changes_v2.1.0.3': {
      'en': """<ul>
          <li>Added a preference: decimal separator for the floating-point numbers</li>
        </ul>""",
      'ru': """<ul>
          <li>Добавлена настройка: разделитель для дробной части в числах с плавающей точкой</li>
        </ul>""",
      'uk': """<ul>
          <li>Додано налаштування: роздільник для дробової частини в числах з плаваючою точкою</li>
        </ul>""",
    },
    'floats format': {
      'en': 'Decimal Separator',
      'ru': 'Разделитель в дробях',
      'uk': 'Роздільник в дробових числах'
    },
    'comma': {
      'en': 'Comma',
      'ru': 'Запятая',
      'uk': 'Кома'
    },
    'dot': {
      'en': 'Dot',
      'ru': 'Точка',
      'uk': 'Крапка'
    }
  }

  for name, itemDictValue in itemDict.items():
    for language, value in itemDictValue.items():
      translation = Translation.query.filter_by(name=name, language=language).first()
      if not translation:
        translation = Translation()
        translation.language = language
        translation.name = name
        translation.value = value
        translation.save()
      else:
        translation.value = value
        translation.save()