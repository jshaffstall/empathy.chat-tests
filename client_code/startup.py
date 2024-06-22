import anvil.server
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from . import auto_test
# from anvil_extras.utils import timed
# from . import network_controller_test


# @timed
# def client_auto_tests():
#   network_controller_test.ConnectionsTest().main()
#   network_controller_test.CreateFormTest().main()


auto_test.client_auto_tests()
anvil.server.call('server_auto_tests')
open_form('TestForm')