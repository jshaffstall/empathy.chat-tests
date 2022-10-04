from ._anvil_designer import MatchFormTemplate
from anvil import *
from anvil.js import window, ExternalError


class MatchForm(MatchFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    clip_urls = server.call_s('get_urls', ['doorbell_mp3',
                                           'doorbell_wav',
                                           'bowl_struck_wav',
                                          ])
    self.call_js('loadClips', *clip_urls)

  def _play_sound(self, audio_id):
    try:
      self.call_js('playSound', audio_id)
      #raise ExternalError
    except ExternalError as err:
      print(f"Error playing {audio_id} sound: {repr(err)}")       

  def doorbell_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self._play_sound('doorbell')

  def play_chime_click(self, **event_args):
    """This method is called when the button is clicked"""
    self._play_sound('ding')

  def my_timer_1_elapsed(self, **event_args):
    self._play_sound('ding')




