class ReportHelper:
	@classmethod
	def listReports(cls, start_date=None, end_date=None, accounts=None, components=None):
		from models.account import Account
		from models.report import Report
		
		query = Report.query\
			.join(Report.account)
		if start_date:
			query = query.filter(Report.due_date>=start_date)
		if end_date:
			query = query.filter(Report.due_date<=end_date)
		if accounts:
			query = query.filter(Report.account_id.in_(accounts))
		if components:
			query = query.filter(Report.component_id.in_(components))
		
		query = query.order_by(Account.first_name, Account.last_name, Account.alias, Report.due_date, Report.created)
		
		return query.all()
	
	@classmethod
	def listActiveReports(cls, start_date=None, end_date=None, accounts=None, components=None):
		from models.account import Account
		from models.project import Project, Component
		from models.report import Report
		
		query = Report.query\
			.filter(~Report.status.in_(Report._r(Report.STATUS_DELETED)))\
			.join(Report.account)\
			.filter(~Account.status.in_(Account._r(Account.STATUS_DELETED)))\
			.join(Report.component, aliased=True)\
			.filter(~Component.status.in_(Component._r(Component.STATUS_DELETED)))\
			.join(Report.project, aliased=True)\
			.filter(~Project.status.in_(Project._r(Project.STATUS_DELETED)))
		
		if start_date:
			query = query.filter(Report.due_date>=start_date)
		if end_date:
			query = query.filter(Report.due_date<=end_date)
		if accounts:
			query = query.filter(Report.account_id.in_(accounts))
		if components:
			query = query.filter(Report.component_id.in_(components))
		
		query = query.order_by(Account.first_name, Account.last_name, Account.alias, Report.due_date, Report.created)
		
		return query.all()
