import anvil.server
from anvil import *
# from anvil_extras.utils import timed
# from . import network_controller_test


# @timed
# def client_auto_tests():
#   network_controller_test.ConnectionsTest().main()
#   network_controller_test.CreateFormTest().main()


# client_auto_tests()
anvil.server.call('server_auto_tests')
open_form('TestForm')