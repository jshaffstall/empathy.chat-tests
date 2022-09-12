import unittest
from .test_helper import MockServer, DispatchCollector, MockNotification
from empathy_chat import parameters as p
from empathy_chat import invites
from empathy_chat import invited_procedures as invited
from empathy_chat.glob import publisher
from empathy_chat.exceptions import MistakenGuessError


class Invited1Test(unittest.TestCase):
  def setUp(self):
    self.collector = DispatchCollector()
    publisher.subscribe("invited1_error", self, self.collector.catch_dispatch)
  
  def test_invalid_response1(self):
    invite = invites.Invite()
    invited.submit_response(invite)
    self.assertEqual(len(self.collector.dispatches), 1)

  def test_invalid_response2(self): 
    invite= invites.Invite(rel_to_invitee="12", invitee_guess="1234")
    invited.submit_response(invite)
    self.assertEqual(self.collector.dispatches[0].title, "Please add a description of your relationship.")

  def test_invalid_response3(self): 
    invite= invites.Invite(rel_to_invitee="12345678", invitee_guess="1")
    invited.submit_response(invite)
    self.assertEqual(self.collector.dispatches[0].title, "Wrong number of digits entered.")  

  def test_invalid_response4(self):
    invite = invites.Invite(rel_to_inviter="12345678", inviter_guess="1234")
    invited.submit_response(invite)
    self.assertEqual(len(self.collector.dispatches), 1)

  def test_valid_response(self):
    invite = invites.Invite(rel_to_invitee="12345678", invitee_guess="1234")
    _submit_response = invited._submit_response
    invited._submit_response = lambda invite: None
    invited.submit_response(invite)
    self.assertFalse(self.collector.dispatches)
    invited._submit_response = _submit_response

  def test_respond_error(self):
    invite = invites.Invite(rel_to_invitee="12345678", invitee_guess="1234")
    test_error = 'test_error'
    mock_server = MockServer(return_values={'respond_to_close_invite': None}, error=MistakenGuessError, error_text=test_error)
    invited.server = mock_server
    invited.submit_response(invite)
    self.assertEqual(len(self.collector.dispatches), 1)
    self.assertEqual(self.collector.dispatches[0].title, test_error)
  
  def tearDown(self):
    publisher.unsubscribe("invited1_error", self)


class InvitedTest(unittest.TestCase):
  def setUp(self):
    self.collector = DispatchCollector()
    publisher.subscribe("invited", self, self.collector.catch_dispatch)
  
  def test_mistaken_inviter_guess_error(self):
    invite = invites.Invite(rel_to_invitee="12345678", invitee_guess="1234")
    test_error = p.MISTAKEN_INVITER_GUESS_ERROR
    mock_server = MockServer(return_values={'respond_to_close_invite': None}, error=MistakenGuessError, error_text=test_error)
    invited.server = mock_server
    invited.Notification = MockNotification
    invited.submit_response(invite)
    notifications_shown = MockNotification.get_notifications_shown()
    self.assertEqual(notifications_shown[0], MockNotification(p.MISTAKEN_INVITER_GUESS_ERROR, title="Mistaken Invite", style="info", timeout=None))
    self.assertEqual(len(self.collector.dispatches), 1)
    self.assertEqual(self.collector.dispatches[0].title, "failure")

  def tearDown(self):
    publisher.unsubscribe("invited", self)
    MockNotification.clear_notifications_shown()


class InvitedSlowTest(unittest.TestCase):
  def setUp(self):
    self.collector = DispatchCollector()
    publisher.subscribe("invited", self, self.collector.catch_dispatch)
  
  def test_success_no_logged_in_user(self):
    invite = invites.Invite(rel_to_invitee="12345678", invitee_guess="1234", link_key="xxx")
    mock_server = MockServer(return_values={'respond_to_close_invite': None})
    invited.server = mock_server
    invited.submit_response(invite)
    notifications_shown = MockNotification.get_notifications_shown()
    self.assertFalse(notifications_shown)
    self.assertEqual(len(self.collector.dispatches), 1)
    self.assertEqual(self.collector.dispatches[0].title, "go_invited2")

  def tearDown(self):
    publisher.unsubscribe("invited", self)
    MockNotification.clear_notifications_shown()
    