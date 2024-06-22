import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.tables
from anvil.tables import app_tables
import anvil.server
import anvil.secrets as secrets
from empathy_chat import server_misc as sm
from empathy_chat import accounts
from empathy_chat.server_misc import authenticated_callable
from empathy_chat import matcher
from empathy_chat import request_interactor as ri
from empathy_chat import portable
from .misc_server_test import ADMIN
from . import request_slow_test as rst


@anvil.server.callable
def force_login(user_id=None):
  if user_id:
    user = app_tables.users.get_by_id(user_id)
  else:
    user = app_tables.users.get(email=secrets.get_secret('admin_email'))
  anvil.users.force_login(user)
  return user


@anvil.server.callable
@anvil.tables.in_transaction(relaxed=True)
def test_add_user(em, level=1):
  print("test_add_user", em, level)
  if True: #anvil.users.get_user()['trust_level'] >= sm.TEST_TRUST_LEVEL:
    if not anvil.server.session.get('test_record'):
      anvil.server.session['test_record'] = create_tests_record()
    new_user = app_tables.users.add_row(email=em,
                                        first_name = em,
                                        enabled=True,
                                       )
    accounts.init_user_info(new_user)
    new_user['trust_level'] = level
    test_users = anvil.server.session['test_record']['test_users']
    anvil.server.session['test_record']['test_users'] = test_users + [new_user]
    return new_user.get_id()


@anvil.server.callable
def test_add_proposal(user_id, port_prop):
  print("test_add_request", user_id)
  if True: #anvil.users.get_user()['trust_level'] >= sm.TEST_TRUST_LEVEL:
    user = sm.get_acting_user(user_id)
    matcher.propagate_update_needed()
    prop_id = rst.add_request(user, port_prop)
    # new_prop = matcher.Proposal.get_by_id(prop_id)
    # if new_prop: 
    #   _add_prop_row_to_test_record(new_prop._row)


# def create_tests_record():
#   return app_tables.test_data.add_row(test_users = [],
#                                       test_proposals = [],
#                                       test_times = [],
#                                      )


# @anvil.server.callable
# def add_now_proposal():
#   print("add_now_proposal")
#   if True: #anvil.users.get_user()['trust_level'] >= sm.TEST_TRUST_LEVEL:
#     tester = sm.get_acting_user()
#     matcher.propagate_update_needed()
#     anvil.server.call('add_proposal', portable.Proposal(times=[portable.ProposalTime(start_now=True)]), user_id=tester.get_id())
#     # tester_now_proptime = matcher.ProposalTime.get_now_proposing(tester)
#     # if tester_now_proptime:
#     #   _add_prop_row_to_test_record(tester_now_proptime.proposal._row)
    

@anvil.server.callable
def accept_now_proposal(user_id):
  print("accept_now_proposal", user_id)
  if True: #anvil.users.get_user()['trust_level'] >= sm.TEST_TRUST_LEVEL:
    tester = ADMIN
    matcher.propagate_update_needed()
    tester_now_request = ri.now_request(tester)
    if tester_now_request:
      state = matcher.accept_proposal(tester_now_request.request_id, user_id=user_id)
      # if state['status'] in ['pinging', 'matched']:
      #   _add_prop_row_to_test_record(tester_now_proptime.proposal._row)

    
# def _add_prop_row_to_test_record(prop_row):
#   print("_add_prop_row_to_test_record", prop_row['created'])
#   if not anvil.server.session.get('test_record'):
#     anvil.server.session['test_record'] = create_tests_record()
#   test_proposals = anvil.server.session['test_record']['test_proposals']
#   if prop_row not in test_proposals:
#     anvil.server.session['test_record']['test_proposals'] = test_proposals + [prop_row]
#     test_times = anvil.server.session['test_record']['test_times']
#     proptimes = matcher.ProposalTime.times_from_proposal(matcher.Proposal(prop_row))
#     anvil.server.session['test_record']['test_times'] = test_times + [proptime._row 
#                                                                       for proptime in proptimes]
 

@anvil.server.callable
def test_clear():
  print("('test_clear')")
  if True: #anvil.users.get_user()['trust_level'] >= sm.TEST_TRUST_LEVEL:
    anvil.server.launch_background_task('_clear_test_records')
  if anvil.server.session.get('test_record'):
    del anvil.server.session['test_record']


@anvil.server.background_task
@anvil.tables.in_transaction
def _clear_test_records():
  pass
#     test_records = app_tables.test_data.search()
#     test_matches = set()
#     test_times = set()
#     test_proposals = set()
#     for test_row in test_records:
#       for user in test_row['test_users']:
#         user.delete()
#       for time in test_row['test_times']:
#         print("time", time['expire_date'])
#         test_matches.add(app_tables.matches.get(proposal_time=time))
#         test_times.add(time)
#       for proposal in set(test_row['test_proposals']):
#         print("proposal", proposal['created'])
#         test_proposals.add(proposal)
#       test_row.delete()
#     for match in test_matches:
#       if match is not None:
#         print("match", match['match_commence'])
#         for chat_row in app_tables.chat.search(match=match):
#           chat_row.delete()
#         match.delete()
#     for time in test_times:
#       time.delete()
#     for proposal in test_proposals:
#       proposal.delete()
#     anvil.server.session['test_record'] = None


@anvil.server.callable
def test_get_user_list():
  from anvil import secrets
  from empathy_chat.exchange_interactor import prune_old_exchanges
  print("('test_get_user_list')")
  prune_old_exchanges()
  test_user = app_tables.users.get(email=secrets.get_secret('test_user_email'))
  to_return = [(test_user['email'], test_user.get_id())]
  users = app_tables.users.search()
  for u in users:
    if u != test_user:
      to_return += [(u['email'], u.get_id())]
  return to_return
