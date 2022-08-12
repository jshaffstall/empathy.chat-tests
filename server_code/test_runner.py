import anvil.server
import sys
import unittest


@anvil.server.callable
def server_auto_tests(verbosity=1):
  #unittest.main(exit=False)
  import sys
  test_modules = ['helper_test', 'invite_test', 'relationship_test', 
                  'exchange_controller_test', 'network_controller_test']
  test = unittest.TestLoader().loadTestsFromNames(test_modules)
  unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity).run(test)
