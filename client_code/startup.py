def client_auto_tests():
  from anvil_extras.utils import timed
  
  @timed
  def tests_run_client_side():
    from . import exchange_controller_test as ect
    ect.ExchangeControllerTest().main()
  #   Seconds2WordsTest().main()
  #   FullNameTest().main()
  tests_run_client_side()


client_auto_tests()