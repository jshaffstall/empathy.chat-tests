import anvil.secrets as secrets
import anvil.server
import sys
import unittest


@anvil.server.callable
def server_auto_tests(verbosity=1):
  #unittest.main(exit=False)
  test_modules = ['helper_test', 'invite_test', 'relationship_test', 
                  'exchange_controller_test', 'network_controller_test',
                  'invite_fast_server_test', 'server_auto_test', 
                  'request_test',
                 ]
  test = unittest.TestLoader().loadTestsFromNames(test_modules)
  unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity).run(test)

  
@anvil.server.callable
def slow_tests(verbosity=2):
  #unittest.main(exit=False)
  from empathy_chat.exchange_interactor import prune_old_exchanges
  from .request_slow_test import ADMIN, USER2, USER3
  print(f"USER2: {secrets.get_secret('test_user2_email')}, USER3: {secrets.get_secret('test_user3_email')}")
  prune_old_exchanges()
  pre_status_dict = {ADMIN: ADMIN['status'], USER2: USER2['status'], USER3: USER3['status'],}
  test_modules = ['exchange_slow_test', 'request_slow_test',] # 'invite_server_test', 'exchange_test', 'misc_server_test'
  test = unittest.TestLoader().loadTestsFromNames(test_modules)
  unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity).run(test)
  for u in pre_status_dict:
    u['status'] = pre_status_dict[u]
