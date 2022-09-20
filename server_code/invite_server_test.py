import anvil.users
import anvil.secrets as secrets
import anvil.tables
from anvil.tables import app_tables, order_by
import anvil.tables.query as q
from .misc_server_test import ADMIN, USER2
from empathy_chat import invites
from empathy_chat import invites_server
from empathy_chat import parameters as p
from empathy_chat import connections as c
from empathy_chat import server_misc as sm
from empathy_chat.exceptions import MistakenGuessError, InvalidInviteError, MistakenVisitError
from anvil_extras.server_utils import timed
import unittest


class InvitedFasterTests(unittest.TestCase):
  def test_invalid_visit(self):
    with self.assertRaises(InvalidInviteError) as context:
      invite2c = invites_server.load_from_link_key("invalid_link_key")
    self.assertTrue("Invalid invite link" in str(context.exception))
    

class InviteLinkTest(unittest.TestCase):
  def setUp(self):
    self.start_time = sm.now()

  def test_invalid_add(self):
    invite1 = invites.Invite(inviter_guess="6666")
    s_invite1 = invites_server.Invite(invite1)
    with self.assertRaises(InvalidInviteError) as context:
      s_invite1.add()

  def add_link_invite(self, inviter_guess="6666"):
    self.invite1 = invites.Invite(rel_to_inviter='test subject 1', inviter_guess=inviter_guess)
    self.s_invite1 = invites_server.Invite(self.invite1)
    #self.invite1.relay('add')
    self.s_invite1.add()
    self.invite1 = self.s_invite1.portable()

  def cancel_link_invite(self): 
    self.s_invite1.cancel()
    self.assertFalse(self.s_invite1.inviter)

  def test_new_link(self):
    self.add_link_invite()
    self.assertEqual(self.invite1.inviter.user_id, ADMIN.get_id())
    self.assertTrue(self.invite1.link_key)
    self.cancel_link_invite()

#   def test_new_link2(self):
#     self.test_new_link()
     
  @timed
  def test_logged_in_visit_mistaken_inviter_guess(self):
    self.add_link_invite()
    anvil.users.force_login(USER2)
    with self.assertRaises(MistakenGuessError) as context:
      invite = invites_server.load_from_link_key(self.s_invite1.link_key)
    self.assertTrue(p.MISTAKEN_INVITER_GUESS_ERROR in str(context.exception))
    test_prompts = app_tables.prompts.search(user=ADMIN, 
                                             spec={'name': 'invite_guess_fail', 'to_id': USER2.get_id()})
    self.assertEqual(len(test_prompts), 1)
    for test_prompt in test_prompts:
      test_prompt.delete()
    
  def test_logged_in_visit_correct_inviter_guess(self):
    self.add_link_invite(inviter_guess=USER2['phone'][-4:])
    anvil.users.force_login(USER2)
    invite = invites_server.load_from_link_key(self.s_invite1.link_key)
    self.assertEqual(invite.rel_to_inviter, 'test subject 1')
    self.assertEqual(invite.link_key, self.s_invite1.link_key)

  def test_new_visit(self):
    self.add_link_invite()
    anvil.users.logout()
    invite2c = invites_server.load_from_link_key(self.s_invite1.link_key)
    self.assertFalse(invite2c.invitee)
    self.assertTrue(invite2c.invite_id)
    self.assertFalse(self.s_invite1.authorizes_signup())

  def test_own_link_visit(self):
    self.add_link_invite()
    with self.assertRaises(MistakenVisitError) as context:
      invite2c = invites_server.load_from_link_key(self.s_invite1.link_key)
    self.assertTrue("your own invite link" in str(context.exception))
  
  def test_old_visit(self):
    self.add_link_invite()
    link_key = self.s_invite1.link_key
    self.cancel_link_invite()
    anvil.users.logout()
    with self.assertRaises(InvalidInviteError) as context:
      invite2c = invites_server.load_from_link_key(link_key)
    self.assertTrue("This invite link is no longer active." in str(context.exception))

  def test_new_authorizes(self):
    self.add_link_invite()
    anvil.users.logout()
    invite2c = invites_server.load_from_link_key(self.s_invite1.link_key)
    s_invite2c = invites_server.Invite(invite2c)
    s_invite2c['invitee_guess'] = "6688"
    self.assertTrue(s_invite2c.authorizes_signup())
  
  def test_new_connect_failed_guess(self):
    invite2 = invites.Invite(rel_to_inviter='test subject 1 dup', inviter_guess="6666")
    s_invite2 = invites_server.Invite(invite2)
    s_invite2.invitee = USER2
    with self.assertRaises(MistakenGuessError) as context:
      s_invite2.add()
    test_prompts = app_tables.prompts.search(user=ADMIN, 
                                             spec={'name': 'invite_guess_fail', 'to_id': USER2.get_id()})
    #print({'name': 'invite_guess_fail', 'to_id': USER2.get_id()})
    self.assertEqual(len(test_prompts), 0)
    for test_prompt in test_prompts:
      test_prompt.delete()
  
  def tearDown(self):
    anvil.users.force_login(ADMIN)
    test_invites = app_tables.invites.search(user1=q.any_of(ADMIN, USER2), date=q.greater_than_or_equal_to(self.start_time))
    for test_invite in test_invites:
      test_invite.delete()


class InviteConnectTest(unittest.TestCase):
  def setUp(self):
    self.start_time = sm.now()

  def add_connect_invite(self, inviter_guess="5555"):
    invite2 = invites.Invite(rel_to_inviter='test subject 1', inviter_guess=inviter_guess)
    self.s_invite2 = invites_server.Invite(invite2)
    self.s_invite2.invitee = USER2
    self.s_invite2.add()
    self.assertEqual(self.s_invite2.inviter, ADMIN)
 
  def cancel_connect_invite(self): 
    self.s_invite2.cancel()
    self.assertFalse(self.s_invite2.inviter)
    
  def test_new_connect1(self):
    self.add_connect_invite()
    self.assertFalse(self.s_invite2.link_key)
    self.assertTrue(self.s_invite2.invitee)
    self.assertFalse(self.s_invite2.authorizes_signup())
    #test_new_connect_dup
    invite2dup = invites.Invite(rel_to_inviter='test subject 1 dup', inviter_guess="5555")
    s_invite2dup = invites_server.Invite(invite2dup)
    s_invite2dup.invitee = USER2
    with self.assertRaises(InvalidInviteError) as context:
      s_invite2dup.add()
    self.cancel_connect_invite()   
  
  @timed
  def test_logged_in_connect_response_success(self):
    self.add_connect_invite()
    self.s_invite2['invitee_guess'] = "6688"
    self.s_invite2['rel_to_invitee'] = "tester 3"
    self.assertEqual(self.s_invite2.inviter, ADMIN)
    anvil.users.force_login(USER2)
    invites_server.respond_to_close_invite(self.s_invite2.portable())
    self.assertEqual(c.distance(ADMIN, USER2, up_to_distance=1), 1)
    anvil.users.force_login(ADMIN)
    c.disconnect(USER2.get_id())

  def test_logged_in_connect_response_failed_guess(self):
    self.add_connect_invite()
    self.s_invite2['invitee_guess'] = "5678"
    self.s_invite2['rel_to_invitee'] = "tester 3"
    self.assertEqual(self.s_invite2.inviter, ADMIN)
    anvil.users.force_login(USER2)
    with self.assertRaises(MistakenGuessError) as context:
      invites_server.respond_to_close_invite(self.s_invite2.portable())
    self.assertTrue("did not accurately provide the last 4 digits" in str(context.exception))

  def test_logged_in_connect_response_failed_inviter_guess(self):
    self.add_connect_invite()
    self.s_invite2['invitee_guess'] = "6688"
    self.s_invite2['rel_to_invitee'] = "tester 3"
    self.assertEqual(self.s_invite2.inviter, ADMIN)
    anvil.users.force_login(USER2)
    USER2['phone'] = "1234"
    with self.assertRaises(MistakenGuessError) as context:
      invites_server.respond_to_close_invite(self.s_invite2.portable())
    self.assertTrue(p.MISTAKEN_INVITER_GUESS_ERROR in str(context.exception))
    test_prompts = app_tables.prompts.search(user=ADMIN, 
                                             spec={'name': 'invite_guess_fail', 'to_id': USER2.get_id()})
    self.assertEqual(len(test_prompts), 1)
    for test_prompt in test_prompts:
      test_prompt.delete()

  def tearDown(self):
    anvil.users.force_login(ADMIN)
    test_invites = app_tables.invites.search(user1=q.any_of(ADMIN, USER2), date=q.greater_than_or_equal_to(self.start_time))
    for test_invite in test_invites:
      test_invite.delete()
    USER2['phone'] = "+12625555555"
    