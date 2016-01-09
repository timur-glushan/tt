#!/usr/bin/python
# -*- coding: utf-8 -*-
from application import app

@app.install('install_couchdb_design_doc')
def install_couchdb_design_doc():
	"""Create the couchdb design documents"""
	from application import app
	from libraries.couchDB import CouchDB
	import json
	
	couchdb = CouchDB(
		host=app.config['COUCHDB']['host'], 
		database=app.config['COUCHDB']['database'], 
		name=app.config['COUCHDB']['name'], 
		password=app.config['COUCHDB']['password']
	)
	
	designDoc = {
		"_design/employees": 
"""{
   "_id": "_design/employees",
   "views": {
       "track": {
           "map": "function (doc) {\r\r\n    if (doc.type === 'report') {\r\r\n        var mode = 'online'\r\r\n        if (doc.offline) {\r\r\n            mode = 'offline'\r\r\n        }\r\r\n        emit([doc.employee, doc.due_date, doc.type, mode], doc.hours);\r\r\n    }\r\r\n    else if (doc.type === 'presence') {\r\r\n        if (doc.until_mod) {\r\r\n            emit([doc.employee, doc.due, doc.type, doc.state], (doc.until_mod - doc.since_mod) / 60.0);\r\r\n        }\r\r\n    }\r\r\n}",
           "reduce": "_sum"
       },
       "by_last_report": {
           "map": "function(doc) {\n  if (doc.type === 'employee'){\n     emit([doc.last_report], {_id: doc.last_report})\n  }\n}"
       },
       "employees_list": {
           "map": "function(doc) {\n  if (doc.type === 'employee'){\n     emit(doc._id, doc)\n  }\n}"
       }
   },
   "language": "javascript"
}""",
		
		"_design/projects": 
"""{
   "_id": "_design/projects",
   "views": {
       "list": {
           "map": "function (doc) {\r\r\n    if (doc.type === \"project\") {\r\r\n        emit(doc._id, doc);\r\r\n    }\r\r\n}"
       },
       "search_list": {
           "map": "function (doc) {\r\r\n    if (doc.type === \"project\") {\r\r\n        emit(doc._id, null);\r\r\n        afterSlash = doc._id.indexOf(\"/\") + 1;\r\r\n        if ((afterSlash > 0) && (afterSlash < doc._id.length)) {\r\r\n            emit(doc._id.substr(afterSlash), null);\r\r\n        }\r\r\n    }\r\r\n}"
       },
       "partitioned_list": {
           "map": "function (doc) {\r\r\n    emitPartitioned = function (name, parts, used_parts){\r\r\n        emit (name, used_parts);\r\r\n        if (parts && typeof parts === 'object') {\r\r\n            for (part in parts) {\r\r\n                desc = parts[part];\r\r\n                partDesc = {};\r\r\n                partDesc[part] = desc[\"\"] || desc;\r\r\n                newUsed = used_parts.concat([partDesc]);\r\r\n                if (part !== '') {\r\r\n                    newName = name + \"/\" + part;\r\r\n                    emitPartitioned(newName, desc, newUsed);\r\r\n                }\r\r\n             }\r\r\n        }\r\r\n    }\r\r\n    if (doc.type === \"project\") {\r\r\n        emitPartitioned(doc._id, doc.partitions, []);\r\r\n    }\r\r\n}"
       },
       "partitioned_search_list": {
           "map": "function (doc) {\r\r\n    emitPartitioned = function (name, parts, used_parts){\r\r\n        emit (name, used_parts);\r\r\n        if (parts && typeof parts === 'object') {\r\r\n            for (part in parts) {\r\r\n                desc = parts[part];\r\r\n                partDesc = {};\r\r\n                partDesc[part] = desc[\"\"] || desc;\r\r\n                newUsed = used_parts.concat([partDesc]);\r\r\n                if (part !== '') {\r\r\n                    newName = name + \"/\" + part;\r\r\n                    emitPartitioned(newName, desc, newUsed);\r\r\n                }\r\r\n             }\r\r\n        }\r\r\n    }\r\r\n    if (doc.type === \"project\") {\r\r\n        emitPartitioned(doc._id, doc.partitions, []);\r\r\n        afterSlash = doc._id.indexOf(\"/\") + 1;\r\r\n        if ((afterSlash > 0) && (afterSlash < doc._id.length)) {\r\r\n            emitPartitioned(doc._id.substr(afterSlash), doc.partitions, []);\r\r\n        }\r\r\n    }\r\r\n}"
       }
   }
}""",
		
		"_design/reports": 
"""{
   "_id": "_design/reports",
   "views": {
       "emp_duedate_id_into_entry_project_hours_summary_with_total": {
           "map": "function (doc) {\r\r\n    fullProject = function (reportDoc){\r\r\n        if ( (! reportDoc.partition) || (! reportDoc.partition.length) )\r\r\n            return reportDoc.project;\r\r\n        comps = new Array();\r\r\n        comps.push(reportDoc.project);\r\r\n        for ( i = 0; i < reportDoc.partition.length; i++) {\r\r\n            for ( p in reportDoc.partition[i] ) {\r\r\n                comps.push(p);\r\r\n                break;\r\r\n            }\r\r\n        }\r\r\n        return comps.join(\"/\");\r\r\n    }\r\r\n\tif (doc.type === 'report') {\r\r\n\t\temit([doc.employee, '_LOWER_TOTAL'], {\r\r\n\t\t\t\"count\": 1,\r\r\n\t\t\t\"total\": doc.hours\r\r\n\t\t});\r\r\n\t\temit([doc.employee, 'UPPER_TOTAL'], {\r\r\n\t\t\t\"count\": 1,\r\r\n\t\t\t\"total\": doc.hours\r\r\n\t\t});\r\r\n\t\temit([doc.employee, doc.due_date, '_LOWER_SUBTOTAL'], {\r\r\n\t\t\t\"count\": 1,\r\r\n\t\t\t\"total\": doc.hours\r\r\n\t\t});\r\r\n\t\temit([doc.employee, doc.due_date, 'UPPER_SUBTOTAL'], {\r\r\n\t\t\t\"count\": 1,\r\r\n\t\t\t\"total\": doc.hours\r\r\n\t\t});\r\r\n\t\temit([doc.employee, doc.due_date, doc._id], {\r\r\n\t\t\t\"offline\": doc.offline,\r\r\n\t\t\t\"entry_ts\": doc.entry_ts,\r\r\n\t\t\t\"project\": fullProject(doc),\r\r\n\t\t\t\"hours\": doc.hours,\r\r\n\t\t\t\"summary\": doc.summary,\r\r\n\t\t\t\"tags\": doc.tags\r\r\n\t\t})\r\r\n\t}\r\r\n}",
           "reduce": "function (keys, values, rereduce) {\r\r\n\tif (values[0].count) {\r\r\n\t\tvar count = 0;\r\r\n\t\tvar total = 0;\r\r\n\t\tfor (ix in values) {\r\r\n\t\t\tcount += values[ix].count;\r\r\n\t\t\ttotal += values[ix].total;\r\r\n\t\t}\r\r\n\t\treturn {\r\r\n\t\t\t\"count\": count,\r\r\n\t\t\t\"total\": total\r\r\n\t\t};\r\r\n\t}\r\r\n\telse return values[0];\r\r\n}"
       },
       "weekly_efforts": {
           "map": "function(doc) {\n  function getWeekNumber(d) {\n    // Copy date so don't modify original\n    d = new Date(d);\n    d.setHours(0,0,0);    \n    // Set to nearest Thursday: current date + 4 - current day number\n    // Make Sunday's day number 7\n    d.setDate(d.getDate() + 4 - (d.getDay()||7));    \n    // Get first day of year\n    var yearStart = new Date(d.getFullYear(),0,1);   \n    // Calculate full weeks to nearest Thursday\n    var weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7)\n    // Return array of year and week number\n    return '' + d.getFullYear() + '-W' + weekNo;\n  }\n  if (doc.type === 'report'){\n     due = getWeekNumber(doc.due_date);\n     emit([due, ' LOWER_TOTAL'], doc.hours);\n     emit([due, '\\ufff0UPPER_TOTAL'], doc.hours);\n     emit([due, doc.project], doc.hours);\n  }\n}",
           "reduce": "_sum"
       },
       "weekly_reports": {
           "map": "function(doc) {\n  function getWeekNumber(d) {\n    // Copy date so don't modify original\n    d = new Date(d);\n    d.setHours(0,0,0);    \n    // Set to nearest Thursday: current date + 4 - current day number\n    // Make Sunday's day number 7\n    d.setDate(d.getDate() + 4 - (d.getDay()||7));    \n    // Get first day of year\n    var yearStart = new Date(d.getFullYear(),0,1);   \n    // Calculate full weeks to nearest Thursday\n    var weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7)\n    // Return array of year and week number\n    return '' + d.getFullYear() + '-W' + weekNo;\n  }\n  if (doc.type === 'report'){\n     due = getWeekNumber(doc.due_date);\n     emit([due, ' LOWER_TOTAL'], doc.hours);\n     emit([due, '\\ufff0UPPER_TOTAL'], doc.hours);\n     emit([due, doc.employee], doc.hours)\n  }\n}",
           "reduce": "_sum"
       },
       "emp_proj_contributions": {
           "map": "function(doc) {\n  if (doc.type === 'report'){\n     //emit([doc.employee, '_LOWER_TOTAL'], doc.hours);\n     //emit([doc.employee, 'UPPER_TOTAL'], doc.hours);\n     //emit([doc.employee, doc.due_date, \"a_LOWER_SUBTOTAL\"], doc.hours);\n     //emit([doc.employee, doc.due_date, 'Z_UPPER_SUBTOTAL'], doc.hours);\n     emit([doc.employee, doc.project, doc.due_date], {'latest_due_date': doc.due_date, 'total_hours': doc.hours})\n  }\n}",
           "reduce": "function(key,value,rereduce){\n   var due = \"\";\n   var hours = 0;\n   for(var i = 0; i < value.length; i++ ){\n\tif( due < value[i].latest_due_date)\n\t\tdue = value[i].latest_due_date;\n\thours += value[i].total_hours;\n   }\n   return {'latest_due_date':due, 'total_hours':hours};\n}"
       },
       "emp_duemonth_project_into_hours": {
           "map": "function(doc) {\n  if (doc.type === 'report'){\n     emit([doc.employee, doc.due_date.substr(0,7), doc.project], doc.hours)\n  }\n}",
           "reduce": "function(key,value,rereduce){\n   return sum(value);\n}"
       },
       "monthly_efforts": {
           "map": "function(doc) {\n  function getMonth(d) {\n    return d.substr(0,7);\n  }\n  if (doc.type === 'report'){\n     due = getMonth(doc.due_date);\n     emit([due, doc.project, ' LOWER_TOTAL'], doc.hours);\n     emit([due, doc.project, '\\ufff0UPPER_TOTAL'], doc.hours);\n     emit([due, doc.project, doc.due_date.substr(8,2)], doc.hours);\n  }\n}",
           "reduce": "_sum"
       },
       "test": {
           "map": "function (doc) {\r\r\n\ttyw = require('views/lib/utils');\r\r\n\tif (doc.type === 'report') emit(doc.employee, tyw.toYearWeek('2013-03-17'));\r\r\n}"
       },
       "list": {
           "map": "function (doc) {\n    if (doc.type === 'report') {\n        d = new Date();\n        if (d.getMonth()==0)\n            dstr = (d.getFullYear()-1)+'-10-01';\n        else if (d.getMonth()==1)\n            dstr = (d.getFullYear()-1)+'-11-01';\n        else if (d.getMonth()>10)\n            dstr = d.getFullYear()+'-'+(d.getMonth()-1)+'-01';\n        else\n            dstr = d.getFullYear()+'-0'+(d.getMonth()-1)+'-01';\n        \n        if (doc.due_date && doc.due_date>dstr)\n            emit(doc._id, doc);\n    }\n}"
       },
       "emp_dueweek_project_into_hours": {
           "map": "function(doc) {\n  function getWeekNumber(d) {\n    // Copy date so don't modify original\n    d = new Date(d);\n    d.setHours(0,0,0);    \n    // Set to nearest Thursday: current date + 4 - current day number\n    // Make Sunday's day number 7\n    d.setDate(d.getDate() + 4 - (d.getDay()||7));    \n    // Get first day of year\n    var yearStart = new Date(d.getFullYear(),0,1);   \n    // Calculate full weeks to nearest Thursday\n    var weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7)\n    // Return array of year and week number\n    return '' + d.getFullYear() + '-W' + weekNo;\n  }\n  if (doc.type === 'report'){\n     emit([doc.employee, getWeekNumber(doc.due_date), doc.project], doc.hours)\n  }\n}",
           "reduce": "function(key,value,rereduce){\n   return sum(value);\n}"
       },
       "by_employee": {
           "map": "function(doc) {\n  //tyw = require('views/lib/utils').toYearWeek\n  if (doc.type === 'report')\n     emit(doc.employee, null);\n}"
       },
       "monthly_reports": {
           "map": "function (doc) {\r\r\n\tfunction getMonth(d) {\r\r\n\t\treturn d.substr(0, 7);\r\r\n\t}\r\r\n\tfullProject = function (reportDoc) {\r\r\n\t\tif ((!reportDoc.partition) || (!reportDoc.partition.length)) return reportDoc.project;\r\r\n\t\tcomps = new Array();\r\r\n\t\tcomps.push(reportDoc.project);\r\r\n\t\tfor (i = 0; i < reportDoc.partition.length; i++) {\r\r\n\t\t\tfor (p in reportDoc.partition[i]) {\r\r\n\t\t\t\tcomps.push(p);\r\r\n\t\t\t\tbreak;\r\r\n\t\t\t}\r\r\n\t\t}\r\r\n\t\treturn comps.join(\"/\");\r\r\n\t}\r\r\n\tif (doc.type === 'report' && doc.project !== 'OUT') {\r\r\n\t\tdueM = getMonth(doc.due_date);\r\r\n\t\tdueD = doc.due_date.substr(8, 2);\r\r\n\t\tvar allProjects = '\\ufff0__ALL_PROJECTS__';\r\r\n        \r\r\n        if ( doc.project !== 'MGM' ) {\r\r\n    \t\temit([dueM, doc.employee, allProjects, ' LOWER_TOTAL'], doc.hours);\r\r\n    \t\temit([dueM, doc.employee, allProjects, '\\ufff0UPPER_TOTAL'], doc.hours);\r\r\n    \t\temit([dueM, doc.employee, allProjects, dueD], doc.hours);\r\r\n\t\t}\r\r\n\r\r\n\t\temit([dueM, doc.employee, fullProject(doc), ' LOWER_TOTAL'], doc.hours);\r\r\n\t\temit([dueM, doc.employee, fullProject(doc), '\\ufff0UPPER_TOTAL'], doc.hours);\r\r\n\t\temit([dueM, doc.employee, fullProject(doc), dueD], doc.hours);\r\r\n\t}\r\r\n}",
           "reduce": "_sum"
       },
       "emp_duedate_project_into_hours": {
           "map": "function(doc) {\n  if (doc.type === 'report'){\n     //emit([doc.employee, '_LOWER_TOTAL'], doc.hours);\n     //emit([doc.employee, 'UPPER_TOTAL'], doc.hours);\n     //emit([doc.employee, doc.due_date, \"a_LOWER_SUBTOTAL\"], doc.hours);\n     //emit([doc.employee, doc.due_date, 'Z_UPPER_SUBTOTAL'], doc.hours);\n     emit([doc.employee, doc.due_date, doc.project], doc.hours)\n  }\n}",
           "reduce": "function(key,value,rereduce){\n   return sum(value);\n}"
       },
       "lib": {
           "utils": "exports.toYearWeek = function (d) {\n    // Copy date so don't modify original\n    d = new Date(d);\n    d.setHours(0,0,0);    \n    // Set to nearest Thursday: current date + 4 - current day number\n    // Make Sunday's day number 7\n    d.setDate(d.getDate() + 4 - (d.getDay()||7));    \n    // Get first day of year\n    var yearStart = new Date(d.getFullYear(),0,1);   \n    // Calculate full weeks to nearest Thursday\n    var weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7)\n    // Return array of year and week number\n    return '' + d.getFullYear() + '-W' + weekNo;\n  };"
       },
       "proj_emp_contributors": {
           "map": "function(doc) {\n  if (doc.type === 'report'){\n     //emit([doc.employee, '_LOWER_TOTAL'], doc.hours);\n     //emit([doc.employee, 'UPPER_TOTAL'], doc.hours);\n     //emit([doc.employee, doc.due_date, \"a_LOWER_SUBTOTAL\"], doc.hours);\n     //emit([doc.employee, doc.due_date, 'Z_UPPER_SUBTOTAL'], doc.hours);\n     emit([doc.project, doc.employee, doc.due_date], {'latest_due_date': doc.due_date, 'total_hours': doc.hours})\n  }\n}",
           "reduce": "function(key,value,rereduce){\n   var due = \"\";\n   var hours = 0;\n   for(var i = 0; i < value.length; i++ ){\n\tif( due < value[i].latest_due_date){\n\t\tdue = value[i].latest_due_date;\n\t}\n\thours += value[i].total_hours;\n   }\n   return {'latest_due_date':due, 'total_hours':hours};\n}"
       },
       "proj_due_emp_summ_into_hours": {
           "map": "function (doc) {\n\n    fullProject = function (reportDoc) {\n\n\t\tif ((!reportDoc.partition) || (!reportDoc.partition.length)) return reportDoc.project;\n\n\t\tcomps = new Array();\n\n\t\tcomps.push(reportDoc.project);\n\n\t\tfor (i = 0; i < reportDoc.partition.length; i++) {\n\n\t\t\tfor (p in reportDoc.partition[i]) {\n\n\t\t\t\tcomps.push(p);\n\n\t\t\t\tbreak;\n\n\t\t\t}\n\n\t\t}\n\n\t\treturn comps.join(\"/\");\n\n\t}\n\n\tif (doc.type == 'report') {\n\n\t\temit([fullProject(doc), doc.due_date, doc.employee, doc.summary], doc.hours);\n\n\t}\n\n}",
           "reduce": "_sum"
       },
       "on_reporter": {
           "map": "\nfunction(doc) {\n  if (doc.type === 'report' && doc.reporter== 'lana.ieremieva')\n     emit([doc.due_date, doc.project, doc.employee], doc);\n}\n"
       },
       "by_employee_due": {
           "map": "function (doc) {\r\r\n\temit(null, doc);\r\r\n\tif (doc.type === 'report') emit([doc.employee, doc.due_date], null);\r\r\n}"
       },
       "list_full": {
           "map": "function (doc) {\n    if (doc.type === 'report') {\n        emit(doc._id, doc);\n    }\n}"
       },
       "list_by_date": {
           "map": "function (doc) {\n    if (doc.type === 'report') {\n emit([doc.due_date], doc);\n    }\n}"
       },
       "list_by_employee": {
           "map": "function (doc) {\n    if (doc.type === 'report') {\n emit([doc.employee], doc);\n    }\n}"
       },
       "list_by_project": {
           "map": "function (doc) {\n    if (doc.type === 'report') {\n emit([doc.project], doc);\n    }\n}"
       }
   },
   "language": "javascript",
   "common": {
       "utils": " { exports.toYearWeek = function (d) {\n    // Copy date so don't modify original\n    d = new Date(d);\n    d.setHours(0,0,0);    \n    // Set to nearest Thursday: current date + 4 - current day number\n    // Make Sunday's day number 7\n    d.setDate(d.getDate() + 4 - (d.getDay()||7));    \n    // Get first day of year\n    var yearStart = new Date(d.getFullYear(),0,1);   \n    // Calculate full weeks to nearest Thursday\n    var weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7)\n    // Return array of year and week number\n    return '' + d.getFullYear() + '-W' + weekNo;\n  }\n }"
   }
}""",
		
		"_design/htmlproduce": 
"""{
   "_id": "_design/htmlproduce",
   "views": {
       "posts-by-date": {
           "map": "function(doc) { if(doc.type=='report')emit([doc.employee, doc.due_date.substr(0,7), doc.project], doc.hours);}"
       }
   },
   "lists": {
       "chart": "function (head, req) {\r\r\n\r\r\n\ttoHM = function (hours) {\r\r\n\t\tvar minutes = hours * 60;\r\r\n\t\thours = Math.floor(hours)\r\r\n\t\tminutes = Math.round(minutes) % 60;\r\r\n\t\treturn hours + \":\" + (\"0\" + minutes).slice(-2);\r\r\n\t};\r\r\n\r\r\n\tstart({\r\r\n\t\theaders: {\r\r\n\t\t\t'Content-Type': 'text/html;charset=utf-8'\r\r\n\t\t}\r\r\n\t});\r\r\n\tsend('<!DOCTYPE html><html><body>');\r\r\n\tsend('<style type=\"text/css\">');\r\r\n\tsend(\" table { border-collapse:collapse; } \" + \" tr.newSection {border-bottom: 2px solid black; font-weight:bold;}\" + \" td,th {padding: 1px 5px 1px 5px;}\" + \" tr.MGM.VAC { background-color: sandybrown; }\" + \" tr.MGM.SICK { background-color: aqua; }\" + \" tr.MGM.VAC.KZOT { background-color: magenta; }\");\r\r\n\tsend('</style>');\r\r\n\tsend('<table border=1 bordercolor=lightgray><tr><th>Month</th><th>Employee</th><th>Project</th>');\r\r\n\tfor (var i = 1; i < 32; i++) {\r\r\n\t\tsend('<th>' + i + '</th>');\r\r\n\t}\r\r\n\tsend('<th>Total Hours</th></tr>');\r\r\n\tvar row;\r\r\n\twhile (row = getRow()) {\r\r\n\t\tallProjects = (row.key[2].indexOf('__ALL_PROJECTS__') > -1);\r\r\n\t\tif (row.key[3].indexOf('TOTAL') > -1) {\r\r\n\r\r\n\t\t\tproj = row.key[2];\r\r\n\t\t\temp = row.key[1];\r\r\n\t\t\ttr = '<tr class=\"' + proj.replace(/\\x2f/g, \" \") + '\">';\r\r\n\r\r\n\t\t\tif (allProjects) {\r\r\n\t\t\t\ttr = '<tr class=\"newSection\">';\r\r\n\t\t\t\tproj = 'All Projects';\r\r\n\t\t\t\temp = emp + ' (total)';\r\r\n\t\t\t}\r\r\n\t\t\tsend(tr + '<td>' + row.key[0] + '</td>' + '<td>' + emp + '</td>' + '<td>' + proj + '</td>');\r\r\n\t\t}\r\r\n\t\telse {\r\r\n\t\t\tvar lastCol = 1;\r\r\n\t\t\tdo {\r\r\n\t\t\t\tif (row.key[3].indexOf('TOTAL') > -1) {\r\r\n\t\t\t\t\tfor (; lastCol < 32; lastCol++) {\r\r\n\t\t\t\t\t\tsend('<td></td>');\r\r\n\t\t\t\t\t}\r\r\n\t\t\t\t\tsend('<td>' + toHM(row.value) + '</td></tr>');\r\r\n\t\t\t\t\tbreak;\r\r\n\t\t\t\t}else {\r\r\n\t\t\t\t\tvar col = parseInt(row.key[3], 10);\r\r\n\t\t\t\t\tfor (; lastCol < col; lastCol++) {\r\r\n\t\t\t\t\t\tsend('<td></td>');\r\r\n\t\t\t\t\t}\r\r\n\t\t\t\t\tsend('<td>' + row.value.toFixed(2).replace(\".\",\",\") + '</td>');\r\r\n\t\t\t\t\tlastCol++;\r\r\n\t\t\t\t}\r\r\n\t\t\t}while (row = getRow())\r\r\n\t\t}\r\r\n\t}\r\r\n\tsend('</table></body></html>');\r\r\n}",
       "report": "function (head, req) {\r\r\n\r\r\n\ttoHM = function (hours) {\r\r\n\t\tvar minutes = hours * 60;\r\r\n\t\thours = Math.floor(hours)\r\r\n\t\tminutes = Math.round(minutes) % 60;\r\r\n\t\treturn hours + \":\" + (\"0\" + minutes).slice(-2);\r\r\n\t};\r\r\n\r\r\n\tstart({\r\r\n\t\theaders: {\r\r\n\t\t\t'Content-Type': 'text/html;charset=utf-8'\r\r\n\t\t}\r\r\n\t});\r\r\n\tsend('<!DOCTYPE html><html><body>');\r\r\n\tsend('<style type=\"text/css\">');\r\r\n\tsend(\r\r\n\t\" table { border-collapse:collapse; } \" +\r\r\n\t\" tr.newSection {border-top: 2px solid black; }\" + \r\r\n\t\" td,th {padding: 1px 5px 1px 5px;}\");\r\r\n    send('</style>');\r\r\n\tsend('<table border=1 bordercolor=lightgray><tr><th>Project</th><th>Due Date</th><th>Employee</th><th>Summary</th>');\r\r\n\tsend('<th>Total Hours</th></tr>');\r\r\n\tvar row;\r\r\n\tvar prevDue = \"\";\r\r\n\twhile (row = getRow()) {\r\r\n\t\tproj = row.key[0];\r\r\n\t\tdue = row.key[1];\r\r\n\t\temp = row.key[2];\r\r\n\t\tsummary = row.key[3];\r\r\n\t\ttr = '<tr>'\r\r\n\t\tif (due !== prevDue) {\r\r\n\t\t    tr = '<tr class=\"newSection\">';\r\r\n\t\t    prevDue = due;\r\r\n\t\t}\r\r\n        send(tr + '<td>' + proj + '</td><td>' + due + '</td><td>' + emp + '</td><td>' + summary + '</td>');\r\r\n\t\tsend('<td>' + toHM(row.value) + '</td></tr>');\r\r\n\t}\r\r\n\tsend('</table></body></html>');\r\r\n}"
   }
}"""
	}
	
	for docID, doc in designDoc.items():
		if not couchdb.getDocument(docID):
			couchdb.putDocument(docID, json.loads(doc))
