from ._anvil_designer import TestFormTemplate
from anvil import *
import anvil.server
import anvil.users
from empathy_chat.MenuForm.DashForm.CreateForm import CreateForm
from empathy_chat import portable as t
from empathy_chat import glob
from empathy_chat import invites
from empathy_chat import ui_procedures as ui
from .. import auto_test
from ..test_helper import UserLoggedIn


class TestForm(TestFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def test_mode_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    self.test_column_panel.visible = self.test_mode.checked
    if self.test_mode.checked:
      self.test_requestuser_drop_down_refresh()

  def test_adduser_button_click(self, **event_args):
    email = self.test_adduser_email.text
    if email:
      anvil.server.call('test_add_user', email)
      self.test_adduser_email.text = ""
      self.test_requestuser_drop_down_refresh()
    else:
      alert("Email address required to add user.")

  def test_proposal_button_click(self, **event_args):
    user_id = self.test_requestuser_drop_down.selected_value
    with UserLoggedIn(user_id):
      glob.populate_lazy_vars()
      form_item = t.Proposal().create_form_item()
      content = CreateForm(item=form_item)
      self.proposal_alert = content
      out = alert(content=self.proposal_alert,
                  title="New Empathy Chat Proposal",
                  large=True,
                  dismissible=False,
                  buttons=[])
      if user_id and out is True:
        proposal = content.proposal()
        anvil.server.call('test_add_request', user_id, proposal)

  def test_clear_click(self, **event_args):
    anvil.server.call('test_clear')
    self.test_requestuser_drop_down_refresh()

  def test_requestuser_drop_down_refresh(self):
    out = anvil.server.call('test_get_user_list')
    self.test_requestuser_drop_down.items = out

  def test_other_action_click(self, **event_args):
    action = self.test_other_action_drop_down.selected_value
    user_id = self.test_requestuser_drop_down.selected_value
    with UserLoggedIn(user_id):
      anvil.server.call(action, user_id=user_id)

  def autotest_butten_click(self, **event_args):
    """This method is called when the button is clicked"""
    user_id = self.test_requestuser_drop_down.selected_value
    # with UserLoggedIn(user_id):
    #   auto_test.run_now_test()

  def slowtest_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    with UserLoggedIn():
      anvil.server.call('slow_tests')

  def slow_client_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    auto_test.client_slow_tests()

  def invite_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    user_id = self.test_requestuser_drop_down.selected_value
    with UserLoggedIn(user_id):
      invite = invites.Invite(
        inviter=t.User.from_logged_in(),
        rel_to_inviter='test subject 1', 
        inviter_guess='5555',
      )
      invite.relay('add')
      ui.copy_to_clipboard(invite.url, desc="The invite link")

  def matchform_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('MatchForm')

