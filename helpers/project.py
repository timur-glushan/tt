class ProjectHelper:
  @classmethod
  def __parseProjectArgument(cls, project_id):
    from models.project import Project
    
    if type(project_id) in [str, u' ']:
      project = Project.query.filter_by(id=project_id).first()
    else:
      project = project_id
    
    return project
  
  
  
  @classmethod
  def __parseAccountArgument(cls, account_id):
    from models.account import Account
    
    if type(account_id) in [str, u' ']:
      account = Account.query.filter_by(id=account_id).first()
    else:
      account = account_id
    
    return account
  
  
  
  @classmethod
  def projectHasManager(cls, project=None, account=None):
    #from models.project import Project
    from models.project import Membership, Role
    
    project = cls.__parseProjectArgument(project)
    account = cls.__parseAccountArgument(account)
    
    membership = Membership.query\
      .filter(Membership.project==project, Membership.account==account)\
      .join(Membership.role, aliased=True)\
      .filter(Role.alias==Role.ROLE_MANAGER)\
      .first()
    if membership:
      return True
    return False
  
  @classmethod
  def projectHasMember(cls, project=None, account=None):
    #from models.account import Account
    #from models.project import Project
    from models.project import Membership
    
    project = cls.__parseProjectArgument(project)
    account = cls.__parseAccountArgument(account)
    
    membership = Membership.query.filter_by(project=project, account=account).first()
    if membership:
      return True
    return False
  
  @classmethod
  def projectHasActiveMember(cls, project=None, account=None):
    #from models.account import Account
    #from models.project import Project
    from models.project import Membership
    
    project = cls.__parseProjectArgument(project)
    account = cls.__parseAccountArgument(account)
    
    membership = Membership.query.filter_by(project=project, account=account).first()
    if membership and (membership.status & (Membership.STATUS_ACTIVE | Membership.STATUS_DELETED) == Membership.STATUS_ACTIVE):
      return True
    return False
  
  @classmethod
  def projectIsGeneral(cls, project=None):
    #from models.project import Project
    from models.project import Label
    
    label = Label.query.filter_by(title=Label.LABEL_GENERAL, project=project).first()
    if label:
      return True
    return False
  
  @classmethod
  def projectIsHoliday(cls, project=None):
    #from models.project import Project
    from models.project import Label
    
    project = cls.__parseProjectArgument(project)
    
    label = Label.query.filter_by(title=Label.LABEL_HOLIDAY, project=project).first()
    if label:
      return True
    return False
  
  @classmethod
  def listVacationProjects(cls):
    from models.project import Project, Label
    
    return Project.query\
      .order_by(Project.alias)\
      .join(Project.labels, aliased=True)\
      .filter(Label.title==Label.LABEL_VACATION)\
      .all()
  
  @classmethod
  def listGeneralProjects(cls):
    from models.project import Project, Label
    
    return Project.query\
      .join(Project.labels, aliased=True)\
      .filter(Label.title==Label.LABEL_GENERAL)\
      .order_by(Label.title, Project.alias)\
      .all()
  
  @classmethod
  def listProjects(cls):
    from models.project import Project, Label
    
    return Project.query\
      .join(Project.labels)\
      .order_by(Label.title, Project.alias)\
      .all()
  
  @classmethod
  def listActiveProjects(cls):
    from models.project import Project, Label
    
    return Project.query\
      .join(Project.labels)\
      .filter(~Project.status.in_(Project._r(Project.STATUS_DELETED)))\
      .order_by(Label.title, Project.alias)\
      .all()
  
  @classmethod
  def listProjectsForMember(cls, account):
    from models.project import Project, Membership
    
    account = cls.__parseAccountArgument(account)
    
    return Project.query\
      .join(Project.members, aliased=True)\
      .filter(Membership.account==account)\
      .order_by(Project.alias)\
      .all() + cls.listGeneralProjects()
  
  @classmethod
  def listProjectsForActiveMember(cls, account):
    from models.project import Project, Membership
    
    account = cls.__parseAccountArgument(account)
    
    return Project.query\
      .filter(~Project.status.in_(Project._r(Project.STATUS_DELETED)))\
      .join(Project.members, aliased=True)\
      .filter(Membership.account==account, ~Membership.status.in_(Membership._r(Membership.STATUS_DELETED)))\
      .order_by(Project.alias)\
      .all() + cls.listGeneralProjects()
  
  
  
  @classmethod
  def listVacationComponents(cls):
    from models.project import Project, Component, Label
    
    return Component.query\
      .join(Component.project)\
      .join(Project.labels, aliased=True)\
      .filter(Label.title==Label.LABEL_VACATION)\
      .order_by(Project.alias, Component.alias)\
      .all()
  
  
  
  @classmethod
  def listGeneralComponents(cls):
    from models.project import Project, Component, Label
    
    return Component.query\
      .join(Component.project)\
      .join(Project.labels, aliased=True)\
      .filter(Label.title==Label.LABEL_GENERAL)\
      .order_by(Label.title, Project.alias, Component.alias)\
      .all()
  
  
  
  @classmethod
  def listAllComponents(cls):
    from models.project import Project, Component, Label
    
    return Component.query\
      .join(Component.project)\
      .join(Project.labels)\
      .order_by(Label.title, Project.alias, Component.alias)\
      .all()
  
  
  
  @classmethod
  def listAllActiveComponents(cls):
    from models.project import Project, Component, Label
    
    return Component.query\
      .join(Component.project)\
      .join(Project.labels)\
      .join(Project.members, aliased=True)\
      .filter(~Component.status.in_(Component._r(Component.STATUS_DELETED)))\
      .filter(~Project.status.in_(Project._r(Project.STATUS_DELETED)))\
      .order_by(Label.title, Project.alias, Component.alias)\
      .all()
  
  
  
  @classmethod
  def listComponents(cls, project):
    from models.project import Project, Component
    
    project = cls.__parseProjectArgument(project)
    
    return Component.query\
      .filter(Component.project_id==project.id)\
      .order_by(Component.alias)\
      .all()
    
  @classmethod
  def listActiveComponents(cls, project):
    from models.project import Project, Component
    
    project = cls.__parseProjectArgument(project)
    
    return Component.query\
      .filter(Component.project_id==project.id, ~Component.status.in_(Component._r(Component.STATUS_DELETED)))\
      .order_by(Component.alias)\
      .all()
  
  @classmethod
  def listAllComponentsForMember(cls, account):
    from models.project import Project, Component, Membership
    
    account = cls.__parseAccountArgument(account)
    
    return Component.query\
      .join(Component.project)\
      .join(Project.members, aliased=True)\
      .filter(Membership.account==account)\
      .order_by(Project.alias, Component.alias)\
      .all() + cls.listGeneralComponents()
      #.order_by(Component.project.alias)\
  
  @classmethod
  def listAllComponentsForActiveMember(cls, account):
    from models.project import Project, Component, Membership
    
    account = cls.__parseAccountArgument(account)
    
    return Component.query\
      .filter(~Component.status.in_(Component._r(Component.STATUS_DELETED)))\
      .join(Component.project)\
      .filter(~Project.status.in_(Project._r(Project.STATUS_DELETED)))\
      .join(Project.members, aliased=True)\
      .filter(Membership.account==account, ~Membership.status.in_(Membership._r(Membership.STATUS_DELETED)))\
      .order_by(Project.alias, Component.alias)\
      .all() + cls.listGeneralComponents()
      #.order_by(Project.alias)\
  
  @classmethod
  def listComponentsForMember(cls, project, account):
    from models.project import Project, Component, Membership
    
    project = cls.__parseProjectArgument(project)
    account = cls.__parseAccountArgument(account)
    
    return Component.query\
      .filter(Component.project_id==project.id)\
      .join(Component.project)\
      .join(Project.members, aliased=True)\
      .filter(Membership.account==account)\
      .order_by(Project.alias, Component.alias)\
      .all()
  
  @classmethod
  def listComponentsForActiveMember(cls, project, account):
    from models.project import Project, Component, Membership
    
    project = cls.__parseProjectArgument(project)
    account = cls.__parseAccountArgument(account)
    
    return Component.query\
      .filter(Component.project_id==project.id, ~Component.status.in_(Component._r(Component.STATUS_DELETED)))\
      .join(Component.project)\
      .filter(~Project.status.in_(Project._r(Project.STATUS_DELETED)))\
      .join(Project.members, aliased=True)\
      .filter(Membership.account==account, ~Membership.status.in_(Membership._r(Membership.STATUS_DELETED)))\
      .order_by(Project.alias, Component.alias)\
      .all()
  
  @classmethod
  def getDefaultComponent(cls, project):
    from models.project import Project, Component
    
    project = cls.__parseProjectArgument(project)
    
    return Component.query\
      .filter(Component.project_id==project.id, Component.alias==Component.COMPONENT_DEFAULT)\
      .order_by(Component.alias)\
      .all()
  
  
  
  @classmethod
  def listRoles(cls):
    from models.project import Role
    
    return Role.query\
      .order_by(Role.alias)\
      .all()
  
  
  
  @classmethod
  def getDefaultRole(cls):
    from models.project import Role
    
    return Role.query\
      .filter(Role.alias==Role.ROLE_DEFAULT)\
      .first()
  
  
  
  @classmethod
  def profileHasSubordinate(cls, account, subordinate):
    from models.account import Account
    from models.project import Project, Membership, Role
    
    account = cls.__parseAccountArgument(account)
    subordinate = cls.__parseAccountArgument(subordinate)
    
    return account.query\
      .filter(Membership.account_id==account.id)\
      .join(Membership.role, aliased=True)\
      .filter(Role.alias==Role.ROLE_MANAGER)\
      .join(Membership.project, aliased=True)\
      .join(Project.members, aliased=True)\
      .filter(Membership.account_id==subordinate.id)\
      .count() > 0
