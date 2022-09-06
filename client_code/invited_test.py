import unittest
from empathy_chat import parameters as p
from empathy_chat import invites
from empathy_chat import invited
from empathy_chat.glob import publisher


class InvitedTest(unittest.TestCase):
  def setUp(self):
    self.latest_dispatch = None
    publisher.subscribe("invited1_error", self, self.dispatch_handler)

  def dispatch_handler(self, dispatch):
    self.latest_dispatch = dispatch
  
  def test_invalid_invite1(self):
    invite = invites.Invite()
    invited.submit_response(invite)
    self.assertTrue(self.latest_dispatch)

  def test_invalid_invite2(self): 
    invite= invites.Invite(rel_to_invitee="12", invitee_guess="1234")
    invited.submit_response(invite)
    self.assertEqual(self.latest_dispatch.title, "Please add a description of your relationship.")

  def test_invalid_invite3(self): 
    invite= invites.Invite(rel_to_invitee="12345678", invitee_guess="1")
    invited.submit_response(invite)
    self.assertEqual(self.latest_dispatch.title, "Wrong number of digits entered.")  

  def test_invalid_invite4(self):
    invite = invites.Invite(rel_to_inviter="12345678", inviter_guess="1234")
    invited.submit_response(invite)
    self.assertTrue(self.latest_dispatch)

  def test_invalid_invite5(self):
    invite = invites.Invite(rel_to_invitee="12345678", invitee_guess="1234")
    _submit_response = invited._submit_response
    invited._submit_response = lambda invite: None
    invited.submit_response(invite)
    self.assertFalse(self.latest_dispatch)
    invited._submit_response = _submit_response

  def tearDown(self):
    publisher.unsubscribe("invited1_error", self)