import anvil.secrets as secrets
import anvil.tables
from anvil.tables import app_tables, order_by
import anvil.tables.query as q
from empathy_chat import invites
from empathy_chat import invites_server
from empathy_chat import parameters as p
from empathy_chat import connections as c
from empathy_chat import server_misc as sm
from anvil_extras.server_utils import timed
import unittest


class InviteBasicTest(unittest.TestCase):
  def test_conversion(self):
    invite1 = invites.Invite(rel_to_inviter='test subject 1', inviter_guess="6666")
    s_invite1 = invites_server.Invite(invite1)
    self.assertEqual(s_invite1.inviter_guess, "6666")
    invite2 = s_invite1.portable()
    self.assertEqual(invite2.rel_to_inviter, 'test subject 1')
    
    
class InviteTest(unittest.TestCase):
  def setUp(self):
    self.start_time = sm.now()
    self.user = app_tables.users.get(email=secrets.get_secret('admin_email')) #anvil.users.get_user()
    self.poptibo = app_tables.users.get(email=secrets.get_secret('test_user2_email'))

  def test_invalid_add(self):
    invite1 = invites.Invite(inviter_guess="6666")
    s_invite1 = invites_server.Invite(invite1)
    errors = s_invite1.add()
    self.assertTrue(errors)

  def add_link_invite(self):
    self.invite1 = invites.Invite(rel_to_inviter='test subject 1', inviter_guess="6666")
    self.s_invite1 = invites_server.Invite(self.invite1)
    #self.invite1.relay('add')
    errors = self.s_invite1.add()
    self.assertFalse(errors)
    self.invite1 = self.s_invite1.portable()

  def cancel_link_invite(self): 
    self.s_invite1.cancel()
    self.assertFalse(self.s_invite1.inviter)
    
  def add_connect_invite(self):
    port_invitee = sm.get_port_user(self.poptibo, user1=self.user)
    self.invite2 = invites.Invite(rel_to_inviter='test subject 1', inviter_guess="5555", invitee=port_invitee)
    self.s_invite2 = invites_server.Invite(self.invite2)
    errors = self.s_invite2.add()
    self.assertFalse(errors)
    self.assertEqual(self.s_invite2.inviter, self.user)
    self.invite2 = self.s_invite2.portable()    
 
  def cancel_connect_invite(self): 
    self.s_invite2.cancel()
    self.assertFalse(self.s_invite2.inviter)

  def test_new_link(self):
    self.add_link_invite()
    self.assertEqual(self.invite1.inviter.user_id, self.user.get_id())
    self.assertTrue(self.invite1.link_key)
    self.cancel_link_invite()

#   def test_new_link2(self):
#     self.test_new_link()

  def test_new_connect1(self):
    self.add_connect_invite()
    self.assertEqual(self.invite2.inviter.user_id, self.user.get_id())
    self.assertFalse(self.invite2.link_key)
    self.assertTrue(self.invite2.invitee)
    #test_new_connect_dup
    port_invitee = sm.get_port_user(self.poptibo, user1=self.user)
    invite2dup = invites.Invite(rel_to_inviter='test subject 1 dup', inviter_guess="5555", invitee=port_invitee)
    s_invite2dup = invites_server.Invite(invite2dup)
    errors = s_invite2dup.add()
    self.assertTrue(errors)
    self.cancel_connect_invite()   
    
  def test_new_connect_failed_guess(self):
    port_invitee = sm.get_port_user(self.poptibo, user1=self.user)
    invite2 = invites.Invite(rel_to_inviter='test subject 1 dup', inviter_guess="6666", invitee=port_invitee)
    s_invite2 = invites_server.Invite(invite2)
    errors = s_invite2.add()
    self.assertTrue(errors)
    test_prompts = app_tables.prompts.search(user=self.user, 
                                             spec={'name': 'invite_guess_fail', 'to_id': self.poptibo.get_id()})
    #print({'name': 'invite_guess_fail', 'to_id': self.poptibo.get_id()})
    self.assertEqual(len(test_prompts), 1)
    for test_prompt in test_prompts:
      test_prompt.delete()
     
  @timed
  def test_logged_in_visit1(self):
    self.add_link_invite()
    invite2a = invites.Invite(link_key=self.invite1.link_key)
#     s_invite2a = invites_server.Invite(invite2a)
#     errors = s_invite2a.visit(user=self.poptibo)
    errors = invite2a.relay('visit', {'user': self.poptibo})
    self.assertTrue(errors)
    self.assertEqual(errors[0], p.MISTAKEN_INVITER_GUESS_ERROR)

  def test_logged_in_visit2(self):
    self.add_link_invite()
    self.s_invite1.inviter_guess = self.poptibo['phone'][-4:]
    self.s_invite1.edit_invite()
    invite2b = invites.Invite(link_key=self.s_invite1.link_key)
    s_invite2b = invites_server.Invite(invite2b)
    errors = s_invite2b.visit(**{'user': self.poptibo})
    self.assertFalse(errors)
    self.assertEqual(s_invite2b.invitee, self.poptibo)

  def test_new_visit(self):
    self.add_link_invite()
    invite2c = invites.Invite(link_key=self.invite1.link_key)
    s_invite2c = invites_server.Invite(invite2c)
    errors = s_invite2c.relay('visit', {'user': None})
    self.assertFalse(errors)
    self.assertFalse(invite2c.invitee)

  def test_old_visit(self):
    self.add_link_invite()
    invite2c = invites.Invite(link_key=self.invite1.link_key)
    self.cancel_link_invite()
    s_invite2c = invites_server.Invite(invite2c)
    errors = s_invite2c.relay('visit', {'user': None})
    self.assertTrue("This invite link is no longer active." in errors)
    self.assertFalse(invite2c.invitee)

  def test_invalid_visit(self):
    invite2c = invites.Invite(link_key="invalid_link_key")
    s_invite2c = invites_server.Invite(invite2c)
    errors = s_invite2c.relay('visit', {'user': None})
    self.assertTrue("Invalid invite link" in errors)
    self.assertFalse(invite2c.invitee)
  
  @timed
  def test_connect_response(self):
    self.add_connect_invite()
#     self.invite2['invitee_guess'] = "6688"
#     self.invite2['rel_to_invitee'] = "tester 3"
#     errors = self.invite2.relay('respond')
    self.s_invite2['invitee_guess'] = "6688"
    self.s_invite2['rel_to_invitee'] = "tester 3"
    self.assertEqual(self.s_invite2.inviter, self.user)
    errors = self.s_invite2.relay('respond', {'user_id': self.poptibo.get_id()})
    self.assertFalse(errors)
    self.assertEqual(c.distance(self.user, self.poptibo, up_to_distance=1), 1)
    c.disconnect(self.poptibo.get_id())

  def tearDown(self):
    test_invites = app_tables.invites.search(user1=q.any_of(self.user, self.poptibo), date=q.greater_than_or_equal_to(self.start_time))
    for test_invite in test_invites:
      test_invite.delete()
