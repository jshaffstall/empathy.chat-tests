import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import unittest
from empathy_chat import parameters as p
from empathy_chat import invites
    

class InviteTest(unittest.TestCase):
  def test_url(self):
    invite = invites.Invite(link_key='test')
    self.assertEqual(invite.url, p.URL + "#?invite=test")

  def test_update(self):
    invite1 = invites.Invite(invite_id="1")
    invite2 = invites.Invite()
    invite2.update(invite1)
    self.assertEqual(invite2.invite_id, "1")
    
  def test_invalid_invite(self):
    invite1 = invites.Invite()
    invite2 = invites.Invite(rel_to_inviter="12", inviter_guess="1234")
    invite3 = invites.Invite(rel_to_inviter="12345678", inviter_guess="1")
    invite4 = invites.Invite(rel_to_inviter="12345678", inviter_guess="1234")
    invite5 = invites.Invite(rel_to_invitee="12345678", invitee_guess="1234")
    self.assertEqual(len(invite1.invalid_invite()), 2)
    self.assertEqual(invite2.invalid_invite(), ["Please add a description of your relationship."])
    self.assertEqual(invite3.invalid_invite(), ["Wrong number of digits entered."])
    self.assertFalse(invite4.invalid_invite())
    self.assertTrue(invite4.invalid_response())
    self.assertFalse(invite5.invalid_response())

  def test_rel_item(self):
    invite1 = invites.Invite(rel_to_inviter="12345678", inviter_guess="1234")
    item1 = invite1.rel_item(for_response=False)
    self.assertEqual(item1['relationship'], invite1.rel_to_inviter)
    self.assertEqual(item1['phone_last4'], invite1.inviter_guess)
#     self.assertEqual(item1['name'], invite1.invitee.name if invite1.invitee else "")
    item2 = invite1.rel_item(for_response=True)
    self.assertEqual(item2['relationship'], invite1.rel_to_invitee)
    self.assertEqual(item2['phone_last4'], invite1.invitee_guess)
#     self.assertEqual(item2['name'], invite1.inviter.name if invite1.inviter else "")
    
    item1['relationship'] = "abcdefgh"
    item1['phone_last4'] = "4321"
    item2['relationship'] = "1234efgh"
    invite1.update_from_rel_item(item1, for_response=False)
    invite1.update_from_rel_item(item2, for_response=True)
    self.assertEqual(invite1.rel_to_inviter, item1['relationship'])
    self.assertEqual(invite1.inviter_guess, item1['phone_last4'])
    self.assertEqual(invite1.rel_to_invitee, item2['relationship'])
