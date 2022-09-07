import unittest
from .test_helper import MockServer, DispatchCollector
from empathy_chat import parameters as p
from empathy_chat import invites
from empathy_chat import invited
from empathy_chat.glob import publisher


class InvitedTest(unittest.TestCase):
  def setUp(self):
    self.collector = DispatchCollector()
    publisher.subscribe("invited1_error", self, self.collector.catch_dispatch)
  
  def test_invalid_invite1(self):
    invite = invites.Invite()
    invited.submit_response(invite)
    self.assertEqual(len(self.collector.dispatches), 1)

  def test_invalid_invite2(self): 
    invite= invites.Invite(rel_to_invitee="12", invitee_guess="1234")
    invited.submit_response(invite)
    self.assertEqual(self.collector.dispatches[0].title, "Please add a description of your relationship.")

  def test_invalid_invite3(self): 
    invite= invites.Invite(rel_to_invitee="12345678", invitee_guess="1")
    invited.submit_response(invite)
    self.assertEqual(self.collector.dispatches[0].title, "Wrong number of digits entered.")  

  def test_invalid_invite4(self):
    invite = invites.Invite(rel_to_inviter="12345678", inviter_guess="1234")
    invited.submit_response(invite)
    self.assertEqual(len(self.collector.dispatches), 1)

  def test_valid_invite(self):
    invite = invites.Invite(rel_to_invitee="12345678", invitee_guess="1234")
    _submit_response = invited._submit_response
    invited._submit_response = lambda invite: None
    invited.submit_response(invite)
    self.assertFalse(self.collector.dispatches)
    invited._submit_response = _submit_response

  def tearDown(self):
    publisher.unsubscribe("invited1_error", self)