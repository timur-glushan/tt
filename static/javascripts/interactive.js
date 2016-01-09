var getattr = function(object, property, defaultValue) {
	if (object===null) {
		throw new Error('Missing object to get a property')
	}
	if (property===null) {
		throw new Error('Missing property to evaluate')
	} else {
		property = (property instanceof Array) ? property : [property]
	}
	
	for (var i=0; i<property.length; i++) {
		if (typeof object[property[i]] === 'undefined') {
			return defaultValue;
		} else {
			object = object[property[i]];
		}
	}
	
	return object;
}

if (typeof window.TimeTracker === 'undefined') TimeTracker = {};

if (typeof TimeTracker.__interactive__ === 'undefined') {
	TimeTracker.__interactive__ = true;
	
	TimeTracker.processAJAXResponse = function(response) {
		$('.popup-form').modal('hide');
		$('.popup-form').remove();
		if (response && typeof response.status !== 'undefined' && response.status == 200) {
			if (typeof response.html !== 'undefined') {
				$(response.html).modal();
			} else if (typeof response.redirect !== 'undefined') {
				document.location.href = response.redirect;
			} else if (typeof response.callback !== 'undefined' && typeof response.callback === 'function') {
				callback();
			} else {
				//$('.popup-form').modal('hide');
				//setTimeout($('.popup-form').remove, 200);
			}
		} else if (response && typeof response.status !== 'undefined' && response.status == 400) {
			//$('.popup-form').modal('hide');
			//$('.popup-form').remove();
			$(response.html).modal();
		} else {
			$(response).modal();
		}
	}
	
	$(document).on('click', '.show-popup', function(e) {
		e.preventDefault();
		$.get($(this).attr('href'), {}, function(response) {
			TimeTracker.processAJAXResponse(response);
			/*
			if (response && typeof response.html !== 'undefined') {
				$(response.html).modal();
			}
			*/
		});
		return false;
	})

	$(document).on('submit', '.popup-form form', function(e) {
		e.preventDefault();
		
		// prevent double submission
		if ($(this).is('.processing')) {
			return false;
		}
		$(this).addClass('processing').addClass('loading');
		
		$.post($(this).attr('action'), $(this).serialize(), function(response) {
			TimeTracker.processAJAXResponse(response);
			/*
			if (response && typeof response.status !== 'undefined' && response.status == 200) {
				$('.popup-form').modal('hide');
				setTimeout($('.popup-form').remove, 200);
			} else if (response && typeof response.status !== 'undefined' && response.status == 400) {
				$('.popup-form').modal('hide');
				$('.popup-form').remove();
				$(response.html).modal();
			}
			*/
		});
		return false;
	});
	
	
	
	if (typeof TimeTracker.preferences === 'undefined') {
		TimeTracker.preferences = {
		 'options': {},
		 'values': {}
		}

		/* TODO: preferenceDefault should be optional,
		 *   null if not provided, set with .set() if provided
		 */
		TimeTracker.preferences.add = function(preferenceName,
				preferenceOptions, preferenceDefault) {
			TimeTracker.preferences.options[preferenceName] = preferenceOptions;

			// set the initial value
			TimeTracker.preferences.set(preferenceName, preferenceDefault);
		}

		TimeTracker.preferences.set = function(preferenceName,
				preferenceValue) {
			TimeTracker.preferences.values[preferenceName] = preferenceValue;
		}

		TimeTracker.preferences.get = function(preferenceName,
				fallbackValue) {
			if (!(preferenceName in TimeTracker.preferences.options)) {
				// in case if there is no such preference at all
				return null;
			}

			var preferenceValue = TimeTracker.preferences.values[preferenceName];
			if (typeof preferenceValue !== 'undefined') {
				// if a preference is found and it has a value
				return preferenceValue;
			} else {
				// if a preference is found, but it's value is undefined
				return fallbackValue;
			}
		}
	}



	if (typeof TimeTracker.project === 'undefined') {
		TimeTracker.project = {}
		
		if (typeof TimeTracker.project.resource === 'undefined') {
			TimeTracker.project.resource = {
				URL: '',
				vacation: {}
			}
		}
		
		TimeTracker.project.loadResource = function() {
			$.post(TimeTracker.project.resource.URL, null, function(response) {
				TimeTracker.project.resource.vacation = response.data;
			});
		}
		
		TimeTracker.project.displayVacation = function() {
			$('[value-project]').each(function() {
				var projectName = $(this).attr('value-project');
				if (projectName in TimeTracker.project.resource.vacation) {
					$(this).addClass('vacation');
					$(this).attr('title', TimeTracker.project.resource.vacation[projectName]);
				}
			});
		}
	}
	
	
	
	if (typeof TimeTracker.translations === 'undefined') {
		TimeTracker.translations = {}
		
		if (typeof TimeTracker.translations.resource === 'undefined') {
			TimeTracker.translations.resource = {
				URL: '',
				labels: {}
			}
		}
		
		TimeTracker.translations.loadResource = function() {
			$.post(TimeTracker.translations.resource.URL, null, function(response) {
				TimeTracker.translations.resource.labels = response.data;
			});
		}
		
		TimeTracker.translations.getLabel = function (label) {
			return (typeof TimeTracker.translations.resource.labels[label] !== 'undefined') 
				? TimeTracker.translations.resource.labels[label] 
				: '='+label;
		}
	}
	
	
	
	if (typeof TimeTracker.date === 'undefined') {
		TimeTracker.date = {};
		
		if (typeof TimeTracker.date.resource === 'undefined') {
			TimeTracker.date.resource = {
				URL: '',
				holidays: {
					weekdays: [],
					monthdays: [],
					dates: {}
				}
			}
		}
		
		TimeTracker.date.loadResource = function() {
			$.post(TimeTracker.date.resource.URL, null, function(response) {
				TimeTracker.date.resource.holidays = response.data;
			});
		}
		
		TimeTracker.date.displayHolidays = function() {
			$('[value-date]').each(function() {
				var dateValue = $(this).attr('value-date');
				var dateObject = new Date(dateValue);
				
				if (TimeTracker.date.resource.holidays.weekdays.indexOf(dateObject.getDay()) >= 0) {
					$(this).addClass('holiday');
					var titleText = _t('weekend');
					$(this).attr('title', titleText);
				}
				if (TimeTracker.date.resource.holidays.monthdays.indexOf(dateObject.getDate()) >= 0) {
					$(this).addClass('holiday');
					var titleText = _t('day off');
					$(this).attr('title',titleText);
				}
				if (dateValue in TimeTracker.date.resource.holidays.dates) {
					$(this).addClass('holiday');
					var titleText = _t(TimeTracker.date.resource.holidays.dates[dateValue]);
					$(this).attr('title', titleText);
				}
			});
		}
	}
	
	
	
	if (typeof TimeTracker.report === 'undefined') {
		TimeTracker.report = {}
		TimeTracker.report.flags = {
			SHOW_DELETED: true
		}
		
		TimeTracker.report.getFlag = function(flag) {
			if (flag in TimeTracker.report.flags) {
				return TimeTracker.report.flags[flag];
			} else {
				throw new Exception('TimeTracker.report.flags does not have a flag "'+flag+'"');
			}
		}
		
		TimeTracker.report.setFlag = function(flag, value) {
			if (flag in TimeTracker.report.flags) {
				TimeTracker.report.flags[flag] = value;
			} else {
				throw new Exception('TimeTracker.report.flags does not have a flag "'+flag+'"');
			}
		}
	}
	
	
	
	if (typeof TimeTracker.formats === 'undefined') {
		TimeTracker.formats = {}
	}



	if (typeof TimeTracker.time === 'undefined') {
		TimeTracker.time = {}
		TimeTracker.preferences.add('time', {
			HOURS: 'hours',
			FLOAT: 'float'
		})
		TimeTracker.preferences.set('time', 'float');

		TimeTracker.preferences.add('floats', {
			COMMA_SEPARATOR: ',',
			DOT_SEPARATOR: '.'
		})
		TimeTracker.preferences.set('floats', ',');



		TimeTracker.time.floatToHours = function(floatValue) {
			var hours = Math.floor(floatValue);
			var minutes = floatValue % 1;
			minutes = 60 * minutes;
			minutes = Math.round(minutes);
			if (minutes<10) {
				minutes = '0'+minutes;
			}
			return hours+':'+minutes
		}

		TimeTracker.time.floatToFloats = function(floatValue) {
			var floats = Number(floatValue).toFixed(2);
			var delimiter = TimeTracker.preferences.get('floats');

			floats = String(floats).replace('.', delimiter);
			return floats
		}
		
		
		
		TimeTracker.time.displayHours = function() {
			$('[value-hours]').each(function() {
				var timeValue = $(this).attr('value-hours');
				
				if (TimeTracker.preferences.get('time') == 'hours') {
					timeValue = TimeTracker.time.floatToHours(timeValue);
				} else if (TimeTracker.preferences.get('time') == 'float') {
					timeValue = TimeTracker.time.floatToFloats(timeValue);
				}
				
				$(this).text(timeValue);
			});
		}
		
		// TimeTracker.time.setTimeFormat(TimeTracker.time.formats.HOURS); TimeTracker.time.displayHours();
		
	}
	
	
	
	/*
	 * fixed header
	*/
	$(window).scroll(function() {
		if ( $(window).scrollTop() < 15 ) {
			$('body').removeClass('page-head-fixed');
		} else {
			$('body').addClass('page-head-fixed');
		}
	});
	
}

