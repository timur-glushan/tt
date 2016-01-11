class TicketHelper:
  @classmethod
  def listTickets(cls, priorities=None, resolutions=None, accounts=None, assignees=None, components=None, versions=None, created_since=None, created_by=None):
    from models.account import Account
    from models.ticket import Priority
    from models.ticket import Resolution
    from models.ticket import Ticket
    
    """query = Ticket.query\
      .join(Ticket.account)\
      .join(Ticket.assignee).label('assignees')\
      .join(Ticket.component)\
      .join(Ticket.project)\
      .join(Ticket.priority)\
      .join(Ticket.resolution)\
      .join(Ticket.version)"""
    query = Ticket.query
    if created_since:
      query = query.filter(Ticket.created>=created_since)
    if created_by:
      query = query.filter(Ticket.created>=created_by)
    if priorities:
      query = query.filter(Ticket.priority_id.in_(priorities))
    if resolutions:
      query = query.filter(Ticket.resolution_id.in_(resolutions))
    if accounts:
      query = query.filter(Ticket.account_id.in_(accounts))
    if assignees:
      query = query.filter(Ticket.assignee_id.in_(assignees))
    if components:
      query = query.filter(Ticket.component_id.in_(components))
    if versions:
      query = query.filter(Ticket.version_id.in_(versions))
    
    query = query.order_by(Ticket.created)
    
    return query.all()

  def listActiveTickets(cls, priorities=None, resolutions=None, accounts=None, assignees=None, components=None, created_since=None, created_by=None):
    from models.account import Account
    from models.ticket import Priority
    from models.ticket import Resolution
    from models.ticket import Ticket

    """query = Ticket.query\
      .filter(~Ticket.status.in_(Ticket._r(Ticket.STATUS_DELETED)))\
      .join(Ticket.account)\
      .filter(~Account.status.in_(Account._r(Account.STATUS_DELETED)))\ """
    query = Ticket.query\
      .filter(~Ticket.status.in_(Ticket._r(Ticket.STATUS_DELETED)))\
      .join(Ticket.assignee)\
      .filter(~Account.status.in_(Account._r(Account.STATUS_DELETED)))\
      .join(Ticket.component, aliased=True)\
      .filter(~Component.status.in_(Component._r(Component.STATUS_DELETED)))\
      .join(Ticket.project, aliased=True)\
      .filter(~Project.status.in_(Project._r(Project.STATUS_DELETED)))\
      .join(Ticket.priority)\
      .filter(~Priority.status.in_(Priority._r(Priority.STATUS_DELETED)))\
      .join(Ticket.resolution)\
      .filter(~Resolution.status.in_(Resolution._r(Resolution.STATUS_DELETED)))\
      .join(Ticket.version)\
      .filter(~Version.status.in_(Version._r(Version.STATUS_DELETED)))
    if created_since:
      query = query.filter(Ticket.created>=created_since)
    if created_by:
      query = query.filter(Ticket.created>=created_by)
    if priorities:
      query = query.filter(Ticket.priority_id.in_(priorities))
    if resolutions:
      query = query.filter(Ticket.resolution_id.in_(resolutions))
    if accounts:
      query = query.filter(Ticket.account_id.in_(accounts))
    if assignees:
      query = query.filter(Ticket.assignee_id.in_(assignees))
    if components:
      query = query.filter(Ticket.component_id.in_(components))
    if versions:
      query = query.filter(Ticket.version_id.in_(versions))

    query = query.order_by(Ticket.created)

    return query.all()



  @classmethod
  def getAlias(component_id):
    from model.project import Component
    from model.ticket import Ticket

    component = Component.query.filter_by(id=component_id).first()

    max_ticket_id = 0
    max_ticket = Ticket.query.filter_by(component_id=component_id).order_by(Ticket.alias.desc).first()
    if max_ticket and max_ticket.alias:
      max_ticket_id_value = max_ticket.alias.split('-')[-1]
      if max_ticket_id_value and max_ticket_id_value.isdigit():
        max_ticket_id = max_ticket_id_value
    alias = coponent.path()+'-'+(max_ticket_id+1)

    return alias
