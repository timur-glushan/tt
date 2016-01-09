if (typeof window.TimeTracker === 'undefined') TimeTracker = {};

TimeTracker.models = {};
TimeTracker.controllers = {};
TimeTracker.views = {};



/* MODELS */
TimeTracker.models.ReportList = function(reports, filters) {
	var dataTable = {
		BY_DATE: {},
		BY_DATE_DETAILED: {},
		BY_EMPLOYEE: {},
		STAT: {
			TOTAL: 0.0,
			OFF: 0.0,
			EMPLOYEES: [],
			PROJECTS: [],
			DATES: []
		}
	};
	var startDate = new Date(filters.start_date);
	var endDate = new Date(filters.end_date);
	
	// within the data per-date we need to add a date key
	for (var d=startDate; d<=endDate; d.setDaysForward(1)) {
		var dateString = d.getFullYear();
		dateString = dateString + '-' + (d.getMonth()<9 ? '0' : '') + (d.getMonth()+1);
		dateString = dateString + '-' +(d.getDate()<10 ? '0' : '') +  d.getDate();
		dataTable['BY_DATE'][dateString] = {};
		dataTable['BY_DATE_DETAILED'][dateString] = {};
	}
	
	$(reports).each(function() {
		var report = this;
		
		// check the "show deleted" flag, skip deleted if the flag is checked
		if (TimeTracker.report.getFlag('SHOW_DELETED') === false && report.deleted === true) {
			return;
		}
		
		/* SET THE DAILY VALUES */
		// date out of range, skip the report
		if (!(report.due_date in dataTable['BY_DATE'])) {
			return;
		}
		// first report for the employee within a given date, need to add an employee key for this date
		if (!(report.labels.account in dataTable['BY_DATE'][report.due_date])) {
			dataTable['BY_DATE'][report.due_date][report.labels.account] = {
				/* TODO: do we show the OFF as a project? */
				//OFF: 0.0,
				TOTAL: 0.0
			};
			dataTable['BY_DATE_DETAILED'][report.due_date][report.labels.account] = {}
		}
		// add a project for the employee per date, if not set yet
		if (!(report.labels.path in dataTable['BY_DATE'][report.due_date][report.labels.account])) {
			dataTable['BY_DATE'][report.due_date][report.labels.account][report.labels.path] = 0;
			dataTable['BY_DATE_DETAILED'][report.due_date][report.labels.account][report.labels.path] = [];
		}
		// add the report duration per date-employee-project
		dataTable['BY_DATE'][report.due_date][report.labels.account][report.labels.path] += report.duration;
		dataTable['BY_DATE_DETAILED'][report.due_date][report.labels.account][report.labels.path].push(report);
		
		// add the hours to TOTAL unless the project is one of the vacaion projects
		if (report.labels.path in TimeTracker.project.resource.vacation) {
			/* TODO: do we show the OFF as a project? */
			//dataTable['BY_DATE'][report.due_date][report.labels.account]['OFF'] += report.duration;
		} else {
			dataTable['BY_DATE'][report.due_date][report.labels.account]['TOTAL'] += report.duration;
		}
		
		/* SET THE TOTALS VALUES */
		// within the data per-employee we need to add an employee key
		if (!(report.labels.account in dataTable['BY_EMPLOYEE'])) {
			dataTable['BY_EMPLOYEE'][report.labels.account] = {
				/* TODO: do we show the OFF as a project? */
				//OFF: 0.0,
				TOTAL: 0.0
			};
		}
		// add a project for the employee, if not set yet
		if (!(report.labels.path in dataTable['BY_EMPLOYEE'][report.labels.account])) {
			dataTable['BY_EMPLOYEE'][report.labels.account][report.labels.path] = 0;
		}
		// add the report duration per employee-project
		dataTable['BY_EMPLOYEE'][report.labels.account][report.labels.path] += report.duration;
		
		// add the report duration per employee-TOTAL unless the project is one of the vacaion projects
		if (report.labels.path in TimeTracker.project.resource.vacation) {
			/* TODO: do we show the OFF as a project? */
			//dataTable['BY_EMPLOYEE'][report.labels.account]['OFF'] += report.duration;
		} else {
			dataTable['BY_EMPLOYEE'][report.labels.account]['TOTAL'] += report.duration;
		}
		
		/* SET THE STAT */
		// add the hours to TOTAL unless the project is one of the vacaion projects
		if (report.labels.path in TimeTracker.project.resource.vacation) {
			/* TODO: do we show the OFF as a project? */
			//dataTable['STAT']['OFF'] += report.duration;
		} else {
			dataTable['STAT']['TOTAL'] += report.duration;
		}
		if (dataTable['STAT']['EMPLOYEES'].indexOf(report.labels.account) < 0) {
			dataTable['STAT']['EMPLOYEES'].push(report.labels.account);
		}
		if (dataTable['STAT']['PROJECTS'].indexOf(report.labels.path) < 0) {
			dataTable['STAT']['PROJECTS'].push(report.labels.path);
		}
		if (dataTable['STAT']['DATES'].indexOf(report.due_date) < 0) {
			dataTable['STAT']['DATES'].push(report.due_date)
		}
	});
	
	return dataTable;
}



/* CONTROLLERS */
TimeTracker.controllers.ReportIndex = function() {
	$('form[name=statistics-form]').submit( function(e) {
		e.preventDefault();
		var formAction = $(this).attr('action');
		var formData = $(this).serialize();
		TimeTracker.controllers.ReportIndex.submitStatistics(formAction, formData);
		return false;
	});
	
	$('form[name=filter-form]').submit( function(e) {
		e.preventDefault();
		var formAction = $(this).attr('action');
		var formData = $(this).serialize();
		TimeTracker.controllers.ReportIndex.submitData(formAction, formData);
		return false;
	});
	
	/*
	 * initiate the filter-toggling links
	*/
	$(document).on('click', 'a.report-filter-link', function(e) {
		e.preventDefault();
		var start_date = $(this).attr('report-filter:start-date');
		var end_date = $(this).attr('report-filter:end-date');
		
		$('input[name=start_date]').parents('.date').datetimepicker().data('datetimepicker').setLocalDate(
			new Date(start_date)
		);
		
		$('input[name=end_date]').parents('.date').datetimepicker().data('datetimepicker').setLocalDate(
			new Date(end_date)
		);
		
		$('form[name=filter-form]').submit();
		
		return false;
	});
	
	setTimeout(function() {
		$('form[name=statistics-form]').submit();
		$('form[name=filter-form]').submit();
	}, 0);
}



TimeTracker.controllers.ReportIndex.submitStatistics = function(action, data) {
	$('#dashboard').addClass('loading');
	$.post(action, data, function(response) {
		$('#dashboard').empty();
		$('#dashboard').html(response.html);
		
		$('#dashboard').removeClass('loading');
		
		TimeTracker.time.displayHours();
	});
}



TimeTracker.controllers.ReportIndex.submitData = function(action, data) {
	$('#content, form[name=filter-form]').addClass('loading');
	
	$.post(action, data, function(response) {
		$('#content').empty();
		$(response.data.reports).each(function() {
			var report = this;
			
			// check the "show deleted" flag, skip deleted if the flag is checked
			if (TimeTracker.report.getFlag('SHOW_DELETED') === false && report.deleted === true) {
				return;
			}
			
			if (!$('#content .date-block[date="'+report.due_date+'"]').length) {
				$('#content').prepend(
'<div class="date-block" date="'+report.due_date+'">'+
	'<div class="title">'+report.labels.date+' <i class="muted pull-right"><span value-hours="0"></span> '+_t('time:hours short')+'</i></div>'+
'</div>');
			}
			$('#content .date-block[date="'+report.due_date+'"] .title').after(
'<div class="alert '+(report.deleted ? 'alert-danger' : 'alert-info')+'">'+
	'<div class="span1">'+
		'<strong value-hours="'+report.duration+'">'+report.duration+'</strong> '+_t('time:hours short')+
	'</div>'+
	'<div class="span2">'+
		' '+_t('common:on')+' <span value-project="'+report.labels.path+'"><strong><a href="'+report.links.project+'">'+report.labels.path+'</a></strong></span>'+
	'</div>'+
	'<div class="span2">'+
		' '+_t('common:by')+' <span value-employee="'+report.labels.account+'"><i><a href="'+report.links.account+'">'+report.labels.account+'</a></i></span>'+
	'</div>'+
	'<div class="span4">'+
		' <span class="muted">'+(report.summary.length<100 ? report.summary : report.summary.substr(0, 100)+'...')+'</span>'+
	'</div>'+
	'<div class="pull-right">'+
		' &nbsp;&nbsp;&nbsp;'+_t('multiple')+' <input type="checkbox" name="report[id]" value="'+report.id+'" />'+
	'</div>'+
	'<div class="pull-right">'+
		' <a class="show-popup edit-report-button" href="'+report.links.edit+'" title="'+_t('edit')+'"><i class="icon-edit"></i> '+_t('edit')+'</a>'+
		' <a class="show-popup delete-report-button" href="'+report.links.delete+'" title="'+_t('delete')+'"><i class="icon-remove"></i> '+_t('delete')+'</a>'+
	'</div>'+
	'<div class="clearfix"></div>'+
'</div>');
			totalHoursNode = $('#content .date-block[date="'+report.due_date+'"]').find('.title [value-hours]');
			totalHours = Number(totalHoursNode.attr('value-hours')) + Number(report.duration);
			totalHoursNode.attr('value-hours', totalHours).text(totalHours);
		});
		
		$('#content, form[name=filter-form]').removeClass('loading');
		
		//TimeTracker.time.displayHours();
		TimeTracker.time.displayHours();
		TimeTracker.date.displayHolidays();
		TimeTracker.project.displayVacation();
	});
}



TimeTracker.controllers.EffortIndex = function() {
	$('form[name=filter-form]').submit( function(e) {
		e.preventDefault();
		var formAction = $(this).attr('action');
		var formData = $(this).serialize()
		TimeTracker.controllers.EffortIndex.submit(formAction, formData);
		return false;
	});
	
	setTimeout(function() {
		$('form[name=filter-form]').submit();
	}, 0);
}

TimeTracker.controllers.EffortIndex.submit = function(action, data) {
	$('#content, form[name=filter-form]').addClass('loading');
	
	$.post(action, data, function(response) {
		$('#content').empty();
		
		var dataTable = TimeTracker.models.ReportList(response.data.reports, response.filters);
		
		var layout;
		switch ($('[name="filter[layout]"]').val()) {
			case 'group_projects':
				layout = 'GroupProjects';
				break;
			case 'group_days':
				layout = 'GroupDays';
				break;
			case 'group_identical':
				layout = 'GroupIdentical';
				break;
			case 'detailed':
				layout = 'Detailed';
				break;
			case 'by_project':
				layout = 'ByProject';
				break;
			case 'by_date':
			default:
				layout = 'ByDate';
		}
		var dataTableHTML = TimeTracker.views[layout](dataTable);
		
		// link to download the table as CSV file or Excel sheet
		dataTableHTML = '<ul class="nav nav-pills">'+
			'<li><span style="line-height:2.4em;"><i class="icon-download"></i> Download as </span></li>' + 
			'<li><a download="activity('+response.filters['employee'][0]+')'+response.filters.start_date+'_-_'+response.filters.start_date+'.csv" href="#" onclick="return ExcellentExport.csv(this, \'efforts-table\');">CSV</a></li>' + 
			'<li><a download="activity('+response.filters['employee'][0]+')'+response.filters.start_date+'_-_'+response.filters.start_date+'.xls" href="#" onclick="return ExcellentExport.excel(this, \'efforts-table\', \'Sheet Name Here\');">XLS</a></li>' + 
		'</ul>'+
			dataTableHTML;
		
		$('#content').append(dataTableHTML);
		
		$('#content, form[name=filter-form]').removeClass('loading');
		
		TimeTracker.time.displayHours();
		TimeTracker.date.displayHolidays();
		TimeTracker.project.displayVacation();
	});
}



TimeTracker.controllers.EffortSummary = function() {
	$('form[name=filter-form]').submit( function(e) {
		e.preventDefault();
		var formAction = $(this).attr('action');
		var formData = $(this).serialize()
		TimeTracker.controllers.EffortSummary.submit(formAction, formData);
		return false;
	});
	
	setTimeout(function() {
		$('form[name=filter-form]').submit();
	}, 0);
}

TimeTracker.controllers.EffortSummary.submit = function(action, data) {
	$('#content, form[name=filter-form]').addClass('loading');
	
	$.post(action, data, function(response) {
		$('#content').empty();
		
		var dataTable = TimeTracker.models.ReportList(response.data.reports, response.filters);
		
		var layout;
		switch ($('[name="filter[layout]"]').val()) {
			case 'group_projects':
				layout = 'GroupProjects';
				break;
			case 'group_days':
				layout = 'GroupDays';
				break;
			case 'group_identical':
				layout = 'GroupIdentical';
				break;
			case 'detailed':
				layout = 'Detailed';
				break;
			case 'by_project':
				layout = 'ByProject';
				break;
			case 'by_date':
			default:
				layout = 'ByDate';
		}
		var dataTableHTML = TimeTracker.views[layout](dataTable);
		
		// link to download the table as CSV file or Excel sheet
		dataTableHTML = '<ul class="nav nav-pills">'+
			'<li><span style="line-height:2.4em;"><i class="icon-download"></i> Download as </span></li>' + 
			'<li><a download="activity'+response.filters.start_date+'_-_'+response.filters.start_date+'.csv" href="#" onclick="return ExcellentExport.csv(this, \'efforts-table\');">CSV</a></li>' + 
			'<li><a download="activity'+response.filters.start_date+'_-_'+response.filters.start_date+'.xls" href="#" onclick="return ExcellentExport.excel(this, \'efforts-table\', \'Sheet Name Here\');">XLS</a></li>' + 
		'</ul>'+
			dataTableHTML;
		
		$('#content').append(dataTableHTML);
		
		$('#content, form[name=filter-form]').removeClass('loading');
		
		TimeTracker.time.displayHours();
		TimeTracker.date.displayHolidays();
		TimeTracker.project.displayVacation();
	});
}



/************************* VIEWS *************************/
TimeTracker.views.ByDate = function(dataTable) {
	var dataTableHTML = '<table id="efforts-table" class="table">';
	// render the dates as the table header
	dataTableHTML += '<tr>';
	// cell for employees column
	dataTableHTML += '<td>&nbsp;</td>';
	// cell for employees-projects column
	dataTableHTML += '<td>&nbsp;</td>';
	for (var dateHeader in dataTable['BY_DATE']) {
		dataTableHTML += '<th value-date="'+dateHeader+'">'+dateHeader.replace('-','<br/>')+'</th>';
	}
	// cell for employees TOTALs column
	dataTableHTML += '<td>&nbsp;</td>';
	dataTableHTML += '</tr>';
	
	// a variable to indicate the new employee rows by dividing with bold horizontal line
	var previousEmployee = null, style = null;
	
	for (var employeeHeader in dataTable['BY_EMPLOYEE']) {
		for (var projectHeader in dataTable['BY_EMPLOYEE'][employeeHeader]) {
			if (projectHeader == 'TOTAL') {
				continue;
			}
			
			style = (previousEmployee !== null && previousEmployee != employeeHeader) ? 'border-top:2px solid #000;' : '';
			previousEmployee = employeeHeader;
			
			dataTableHTML += '<tr style="'+style+'">';
			
			dataTableHTML += '<th value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
			dataTableHTML += '<th value-employee="'+employeeHeader+'" value-project="'+projectHeader+'">'+projectHeader+'</th>';
			for (var dateHeader in dataTable['BY_DATE']) {
				dataTableHTML += '<td value-employee="'+employeeHeader+'" value-project="'+projectHeader+'" value-date="'+dateHeader+'" value-hours="'+getattr(dataTable['BY_DATE'][dateHeader], [employeeHeader,projectHeader], '0')+'">&nbsp;</td>';
			}
			
			dataTableHTML += '<th value-employee="'+employeeHeader+'" value-project="TOTAL" value-hours="'+getattr(dataTable['BY_EMPLOYEE'], [employeeHeader,projectHeader], '0')+'">&nbsp;</th>';
			dataTableHTML += '</tr>';
		}
		// ADDING TOTALS BY DATE
		dataTableHTML += '<tr style="background-color:#eef;">';
		dataTableHTML += '<th value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
		dataTableHTML += '<th value-employee="'+employeeHeader+'" value-project="TOTAL">TOTAL</th>';
		for (var dateHeader in dataTable['BY_DATE']) {
			dataTableHTML += '<th value-employee="'+employeeHeader+'" value-project="TOTAL" value-date="'+dateHeader+'" value-hours="'+getattr(dataTable['BY_DATE'][dateHeader], [employeeHeader,'TOTAL'], '0')+'">&nbsp;</th>';
		}
		dataTableHTML += '<th value-employee="'+employeeHeader+'" value-project="TOTAL" value-hours="'+getattr(dataTable['BY_EMPLOYEE'], [employeeHeader,'TOTAL'], '0')+'">&nbsp;</th>';
		dataTableHTML += '</tr>';
	}
	dataTableHTML += '</table>';
	
	return dataTableHTML;
}



TimeTracker.views.ByProject = function(dataTable) {
	var dataTableHTML = '<table id="efforts-table" class="table">';
	// render the employees (of employees-projects) as the table header
	dataTableHTML += '<tr>';
	// cell for employee column
	dataTableHTML += '<td>&nbsp;</td>';
	
	// a variable to indicate the new employee rows by dividing with bold horizontal line
	var previousEmployee = null, style = null;
	
	for (var employeeHeader in dataTable['BY_EMPLOYEE']) {
		for (var projectHeader in dataTable['BY_EMPLOYEE'][employeeHeader]) {
			if (projectHeader=='TOTAL') {
				continue;
			}
			
			style = (previousEmployee !== null && previousEmployee != employeeHeader) ? 'border-left:2px solid #000;' : '';
			previousEmployee = employeeHeader;
			
			dataTableHTML += '<th style="'+style+'" value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
		}
		dataTableHTML += '<th value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
	}
	dataTableHTML += '</tr>';
	
	// render the projects (of employees-projects) as the table sub-header
	dataTableHTML += '<tr>';
	// cell for employee-project column
	dataTableHTML += '<td>&nbsp;</td>';
	
	// a variable to indicate the new employee rows by dividing with bold horizontal line
	var previousEmployee = null, style = null;
	
	for (var employeeHeader in dataTable['BY_EMPLOYEE']) {
		for (var projectHeader in dataTable['BY_EMPLOYEE'][employeeHeader]) {
			if (projectHeader=='TOTAL') {
				continue;
			}
			
			style = (previousEmployee !== null && previousEmployee != employeeHeader) ? 'border-left:2px solid #000;' : '';
			previousEmployee = employeeHeader;
			
			dataTableHTML += '<th style="'+style+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'">'+projectHeader+'</th>';
			
		}
		dataTableHTML += '<th value-employee="'+employeeHeader+'" value-project="TOTAL">TOTAL</th>';
	}
	dataTableHTML += '</tr>';
	
	for (var dateHeader in dataTable['BY_DATE']) {
		dataTableHTML += '<tr>';
		dataTableHTML += '<th value-date="'+dateHeader+'">'+dateHeader+'</th>';
		
		// a variable to indicate the new employee rows by dividing with bold horizontal line
		var previousEmployee = null, style = null;
		
		for (var employeeHeader in dataTable['BY_EMPLOYEE']) {
			for (var projectHeader in dataTable['BY_EMPLOYEE'][employeeHeader]) {
				if (projectHeader == 'TOTAL') {
					continue;
				}
				
				style = (previousEmployee !== null && previousEmployee != employeeHeader) ? 'border-left:2px solid #000;' : '';
				previousEmployee = employeeHeader;
				
				dataTableHTML += '<td style="'+style+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'" value-date="'+dateHeader+'" value-hours="'+getattr(dataTable['BY_DATE'][dateHeader], [employeeHeader,projectHeader], '0')+'">&nbsp;</td>';
				
			}
			dataTableHTML += '<th value-employee="'+employeeHeader+'" value-project="TOTAL" value-date="'+dateHeader+'" value-hours="'+getattr(dataTable['BY_DATE'][dateHeader], [employeeHeader,'TOTAL'], '0')+'">&nbsp;</th>';
		}
		dataTableHTML += '</tr>';
	}
	
	// a variable to indicate the new employee rows by dividing with bold horizontal line
	var previousEmployee = null, style = null;
	
	// Total per employee-project within the period
	dataTableHTML += '<tr>';
	// cell for employee-project column
	dataTableHTML += '<td>'+_t('total for period')+'</td>';
	for (var employeeHeader in dataTable['BY_EMPLOYEE']) {
		for (var projectHeader in dataTable['BY_EMPLOYEE'][employeeHeader]) {
			if (projectHeader == 'TOTAL') {
				continue;
			}
			
			style = (previousEmployee !== null && previousEmployee != employeeHeader) ? 'border-left:2px solid #000;' : '';
			previousEmployee = employeeHeader;
			
			dataTableHTML += '<th style="'+style+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'" value-hours="'+dataTable['BY_EMPLOYEE'][employeeHeader][projectHeader]+'">'+dataTable['BY_EMPLOYEE'][employeeHeader][projectHeader]+'</th>';
		}
		dataTableHTML += '<th value-employee="'+employeeHeader+'" value-project="'+projectHeader+'" value-hours="'+dataTable['BY_EMPLOYEE'][employeeHeader]['TOTAL']+'">'+dataTable['BY_EMPLOYEE'][employeeHeader]['TOTAL']+'</th>';
	}
	dataTableHTML += '</tr>';
	
	dataTableHTML += '</table>';
	
	return dataTableHTML;
}



TimeTracker.views.Detailed = function(dataTable) {
	var dataTableHTML = '<table id="efforts-table" class="table">';
	// render the employees (of employees-projects) as the table header
	dataTableHTML += '<tr>';
	// cell for date column
	dataTableHTML += '<td>&nbsp;</td>';
	// cell for date-employee column
	dataTableHTML += '<td>&nbsp;</td>';
	// cell for date-employee-project column
	dataTableHTML += '<td>&nbsp;</td>';
	// header columns
	dataTableHTML += '<th>'+_t('description')+'</th>';
	dataTableHTML += '<th>'+_t('time:hours short')+'</th>';
	dataTableHTML += '</tr>';
	for (var dateHeader in dataTable['BY_DATE_DETAILED']) {
		for (var employeeHeader in dataTable['BY_DATE_DETAILED'][dateHeader]) {
			for (var projectHeader in dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader]) {
				for (var i=0; i<dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader].length; i++) {
					dataTableHTML += '<tr>';
					dataTableHTML += '<th value-date="'+dateHeader+'">'+dateHeader+'</th>';
					dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
					dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'">'+projectHeader+'</td>';
					summary = dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].summary;
					summary = (summary.length<100 ? summary : summary.substr(0, 100)+'...');
					dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'">'+summary+'</td>';
					dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'" value-hours="'+dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].duration+'">'+dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].duration+'</td>';
					dataTableHTML += '</tr>';
				}
			}
			/*
			// total per date-employee
			dataTableHTML += '<tr>';
			dataTableHTML += '<th value-date="'+dateHeader+'">'+dateHeader+'</th>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="TOTAL">TOTAL</th>';
			dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="TOTAL">&nbsp;</td>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="TOTAL" value-hours="'+getattr(dataTable['BY_DATE'], [dateHeader,employeeHeader,'TOTAL'], '0')+'">'+getattr(dataTable['BY_DATE'], [dateHeader,employeeHeader,'TOTAL'], '0')+'</th>';
			dataTableHTML += '</tr>';
			*/
		}
	}
	
	// total, all rows
	dataTableHTML += '<tr>';
	dataTableHTML += '<th>&nbsp;</th>';
	dataTableHTML += '<th>&nbsp;</th>';
	dataTableHTML += '<th>&nbsp;</th>';
	dataTableHTML += '<th>'+_t('total for period')+'</th>';
	dataTableHTML += '<th value-hours="'+dataTable['STAT']['TOTAL']+'">'+dataTable['STAT']['TOTAL']+'</th>';
	dataTableHTML += '</tr>';
	dataTableHTML += '</table>';
	
	return dataTableHTML;
}



TimeTracker.views.GroupDays = function(dataTable) {
	var dataTableHTML = '<table id="efforts-table" class="table">';
	// render the employees (of employees-projects) as the table header
	dataTableHTML += '<tr>';
	// cell for date column
	dataTableHTML += '<td>&nbsp;</td>';
	// cell for date-employee column
	dataTableHTML += '<td>&nbsp;</td>';
	// header columns
	dataTableHTML += '<th>'+_t('description')+'</th>';
	dataTableHTML += '<th>'+_t('time:hours short')+'</th>';
	dataTableHTML += '</tr>';
	for (var dateHeader in dataTable['BY_DATE_DETAILED']) {
		for (var employeeHeader in dataTable['BY_DATE_DETAILED'][dateHeader]) {
			var summaryGrouped = [];
			var durationGrouped = 0;
			for (var projectHeader in dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader]) {
				for (var i=0; i<dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader].length; i++) {
					summary = dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].summary;
					summary = (summary.length<100 ? summary : summary.substr(0, 100)+'...');
					summaryGrouped.push('['+projectHeader+']'+' '+summary);
					durationGrouped += dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].duration;
				}
			}
			summaryGrouped = summaryGrouped.join('<br/>');
			dataTableHTML += '<tr>';
			dataTableHTML += '<th value-date="'+dateHeader+'">'+dateHeader+'</th>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
			dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'">'+summaryGrouped+'</td>';
			dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-hours="'+durationGrouped+'">'+durationGrouped+'</td>';
			dataTableHTML += '</tr>';
		}
	}
	dataTableHTML += '</table>';
	
	return dataTableHTML;
}



TimeTracker.views.GroupProjects = function(dataTable) {
	var dataTableHTML = '<table id="efforts-table" class="table">';
	// render the employees (of employees-projects) as the table header
	dataTableHTML += '<tr>';
	// cell for date column
	dataTableHTML += '<td>&nbsp;</td>';
	// cell for date-employee column
	dataTableHTML += '<td>&nbsp;</td>';
	// cell for date-employee-project column
	dataTableHTML += '<td>&nbsp;</td>';
	// header columns
	dataTableHTML += '<th>'+_t('description')+'</th>';
	dataTableHTML += '<th>'+_t('time:hours short')+'</th>';
	dataTableHTML += '</tr>';
	for (var dateHeader in dataTable['BY_DATE_DETAILED']) {
		for (var employeeHeader in dataTable['BY_DATE_DETAILED'][dateHeader]) {
			for (var projectHeader in dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader]) {
				var summaryGrouped = [];
				var durationGrouped = 0;
				for (var i=0; i<dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader].length; i++) {
					summary = dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].summary;
					summary = (summary.length<100 ? summary : summary.substr(0, 100)+'...');
					summaryGrouped.push(summary);
					durationGrouped += dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].duration;
				}
				summaryGrouped = summaryGrouped.join('<br/>');
				dataTableHTML += '<tr>';
				dataTableHTML += '<th value-date="'+dateHeader+'">'+dateHeader+'</th>';
				dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
				dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'">'+projectHeader+'</td>';
				dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'">'+summaryGrouped+'</td>';
				dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'" value-hours="'+durationGrouped+'">'+durationGrouped+'</td>';
				dataTableHTML += '</tr>';
			}
			/*
			dataTableHTML += '<tr>';
			dataTableHTML += '<th value-date="'+dateHeader+'">'+dateHeader+'</th>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="TOTAL">TOTAL</th>';
			dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="TOTAL">&nbsp;</td>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="TOTAL" value-hours="'+getattr(dataTable['BY_DATE'], [dateHeader,employeeHeader,'TOTAL'], '0')+'">'+getattr(dataTable['BY_DATE'], [dateHeader,employeeHeader,'TOTAL'], '0')+'</th>';
			dataTableHTML += '</tr>';
			*/
		}
	}
	
	// total, all rows
	dataTableHTML += '<tr>';
	dataTableHTML += '<th>&nbsp;</th>';
	dataTableHTML += '<th>&nbsp;</th>';
	dataTableHTML += '<th>&nbsp;</th>';
	dataTableHTML += '<th>'+_t('total for period')+'</th>';
	dataTableHTML += '<th value-hours="'+dataTable['STAT']['TOTAL']+'">'+dataTable['STAT']['TOTAL']+'</th>';
	dataTableHTML += '</tr>';
	dataTableHTML += '</table>';
	
	dataTableHTML += '</table>';
	
	return dataTableHTML;
}



TimeTracker.views.GroupIdentical = function(dataTable) {
	var dataTableHTML = '<table id="efforts-table" class="table">';
	// render the employees (of employees-projects) as the table header
	dataTableHTML += '<tr>';
	// cell for date column
	dataTableHTML += '<td>&nbsp;</td>';
	// cell for date-employee column
	dataTableHTML += '<td>&nbsp;</td>';
	// cell for date-employee-project column
	dataTableHTML += '<td>&nbsp;</td>';
	// header columns
	dataTableHTML += '<th>'+_t('description')+'</th>';
	dataTableHTML += '<th>'+_t('time:hours short')+'</th>';
	dataTableHTML += '</tr>';
	for (var dateHeader in dataTable['BY_DATE_DETAILED']) {
		for (var employeeHeader in dataTable['BY_DATE_DETAILED'][dateHeader]) {
			for (var projectHeader in dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader]) {
				// group the identical tasks
				var uniqueReports = []
				for (var i=0; i<dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader].length; i++) {
					var report = dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i];
					for (var j=0; j<uniqueReports.length; j++) {
						if (uniqueReports[j].summary == report.summary) {
							// found the identical
							uniqueReports[j].duration += report.duration;
							report = null;
							break;
						}
					}
					// if it's repeated it would be already reset to null
					if (report !== null) {
						uniqueReports.push(report);
					}
				}
				dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader] = uniqueReports;
				
				for (var i=0; i<dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader].length; i++) {
					dataTableHTML += '<tr>';
					dataTableHTML += '<th value-date="'+dateHeader+'">'+dateHeader+'</th>';
					dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
					dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'">'+projectHeader+'</td>';
					summary = dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].summary;
					summary = (summary.length<100 ? summary : summary.substr(0, 100)+'...');
					dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'">'+summary+'</td>';
					dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="'+projectHeader+'" value-hours="'+dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].duration+'">'+dataTable['BY_DATE_DETAILED'][dateHeader][employeeHeader][projectHeader][i].duration+'</td>';
					dataTableHTML += '</tr>';
				}
			}
			/*
			// total per date-employee
			dataTableHTML += '<tr>';
			dataTableHTML += '<th value-date="'+dateHeader+'">'+dateHeader+'</th>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'">'+employeeHeader+'</th>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="TOTAL">TOTAL</th>';
			dataTableHTML += '<td value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="TOTAL">&nbsp;</td>';
			dataTableHTML += '<th value-date="'+dateHeader+'" value-employee="'+employeeHeader+'" value-project="TOTAL" value-hours="'+getattr(dataTable['BY_DATE'], [dateHeader,employeeHeader,'TOTAL'], '0')+'">'+getattr(dataTable['BY_DATE'], [dateHeader,employeeHeader,'TOTAL'], '0')+'</th>';
			dataTableHTML += '</tr>';
			*/
		}
	}
	
	// total, all rows
	dataTableHTML += '<tr>';
	dataTableHTML += '<th>&nbsp;</th>';
	dataTableHTML += '<th>&nbsp;</th>';
	dataTableHTML += '<th>&nbsp;</th>';
	dataTableHTML += '<th>'+_t('total for period')+'</th>';
	dataTableHTML += '<th value-hours="'+dataTable['STAT']['TOTAL']+'">'+dataTable['STAT']['TOTAL']+'</th>';
	dataTableHTML += '</tr>';
	dataTableHTML += '</table>';
	
	return dataTableHTML;
}
