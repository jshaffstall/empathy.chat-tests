import anvil.users
from empathy_chat import glob


class MockServer:
  def __init__(self, return_values, error=None, error_text=""):
    self.return_values = return_values
    self.call_args = {}
    self.call_kwargs = {}
    self.error = error
    self.error_text = error_text

  def call(self, method, *args, **kwargs):
    self.call_args[method] = args
    self.call_kwargs[method] = kwargs
    if self.error:
      raise self.error(self.error_text)
    return self.return_values.get(method)

  def call_s(self, method, *args, **kwargs):
    return self.call(method, *args, **kwargs)


class DispatchCollector:
  def __init__(self):
    self.dispatches = []
    
  def catch_dispatch(self, dispatch):
    self.dispatches.append(dispatch)


_notifications_shown = []


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
    global _notifications_shown
    _notifications_shown.append(self)

  @staticmethod
  def get_notifications_shown():
    return _notifications_shown
  
  @staticmethod
  def clear_notifications_shown():
    global _notifications_shown
    _notifications_shown.clear()


class UserLoggedIn:
  def __init__(self, user_id=None):
    self._user_id = user_id
  def __enter__(self):
    user = anvil.server.call('force_login', self._user_id)
    glob.logged_in_user = user
    glob.logged_in_user_id = user.get_id()
    glob.trust_level = user['trust_level']
    glob.default_request = user['default_request']
    return user
  def __exit__(self, exc_type, exc_value, exc_tb):
    anvil.users.logout()
    glob.trust_level = 0
    glob.logged_in_user = None
    glob.logged_in_user_id = ""
    