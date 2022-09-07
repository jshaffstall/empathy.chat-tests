import anvil.users
from empathy_chat import glob


class MockServer:
  def __init__(self, return_values):
    self.return_values = return_values
    self.call_args = {}
    self.call_kwargs = {}

  def call(self, method, *args, **kwargs):
    self.call_args[method] = args
    self.call_kwargs[method] = kwargs
    return self.return_values.get(method)

  def call_s(self, method, *args, **kwargs):
    return self.call(method, *args, **kwargs)


class DispatchCollector:
  def __init__(self):
    self.dispatches = []
    
  def catch_dispatch(self, dispatch):
    self.dispatches.append(dispatch)


notifications_shown = []


class MockNotification:
  def __init__(self, message, title="", style="info", timeout=2):
    self.message = message
    self.title = title
    self.style = style
    self.timeout = timeout

  def __repr__(self):
    return f"MockNotification({self.message!r}, {self.title!r}, {self.style!r}, {self.timeout!r})"

  def __eq__(self, other):
    if self.__class__ is other.__class__:
      return repr(self) == repr(other)
    else:
      return NotImplemented
  
  def show(self):
    global notifications
    notifications_shown.append(self)


class UserLoggedIn:
  def __init__(self, user_id=None):
    self._user_id = user_id
  def __enter__(self):
    user = anvil.server.call('force_login', self._user_id)
    glob.logged_in_user = user
    glob.logged_in_user_id = user.get_id()
    glob.trust_level = user['trust_level']
    return user
  def __exit__(self, exc_type, exc_value, exc_tb):
    anvil.users.logout()
    glob.trust_level = 0
    glob.logged_in_user = None
    glob.logged_in_user_id = ""
    