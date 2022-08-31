import anvil.users


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
    
  def catch_dispatches(self, dispatch):
    self.dispatches.append(dispatch)


class UserLoggedIn:
  def __init__(self, user_id=None):
    self._user_id = user_id
  def __enter__(self):
    return anvil.server.call('force_login', self._user_id)
  def __exit__(self, exc_type, exc_value, exc_tb):
    anvil.users.logout()
    