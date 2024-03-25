import anvil.server
import anvil.tz
from anvil import tables
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.secrets as secrets
import datetime
from empathy_chat import accounts


@tables.in_transaction(relaxed=True)
def init_tables():
  ems = {key: secrets.get_secret(key) for key in ('admin_email', 'test_user2_email', 'test_user3_email')}
  app_tables.users.add_rows([{'email': ems['admin_email']}, {'email': ems['test_user2_email']}, {'email': ems['test_user3_email']}])
  test_chars = { 
    ems['admin_email']: { 'confirmed_email': True,
      'contributor': False,
      'email': ems['admin_email'],
      'enabled': True,
      'first_name': 'Tim',
      'how_empathy': ('Feel free to interrupt with empathy guesses, preferably in '
                      'something close to the classic form: "Are you feeling '
                      '_________ because you\'re needing ________?"'),
      'init_date': datetime.datetime(2024, 3, 22, 21, 44, 50, 753923, tzinfo=anvil.tz.tzoffset(hours=0)),
      'last_login': datetime.datetime(2024, 3, 22, 22, 9, 45, 266000, tzinfo=anvil.tz.tzoffset(hours=0)),
      'n_password_failures': 0,
      'profile': ('Experience exchanging empathy with buddies weekly for around '
                  'five years\n'
                  'NYCNVC Empathy and Self-Empathy Intensives participant'),
      'profile_updated': datetime.datetime(2022, 4, 11, 15, 19, 24, 237099, tzinfo=anvil.tz.tzoffset(hours=0)),
      'profile_url': 'https://www.linkedin.com/in/tim-huegerich-26101a8/',
      'remembered_logins': [ { 'login_time': '2024-03-22T21:44:50.219533Z',
                              'token_hash': '32243fcc10e0df574d5471ac3abb57465e118954f7b017084875a7af808754db'}],
      'signed_up': datetime.datetime(2018, 10, 13, 22, 45, 38, 174000, tzinfo=anvil.tz.tzoffset(hours=0)),
      'trust_level': 10,
      'url_confirmed_date': datetime.datetime(2022, 4, 11, 0, 0, tzinfo=anvil.tz.tzoffset(hours=0))},
    ems['test_user2_email']: { 'confirmed_email': True,
      'contributor': False,
      'email': ems['test_user2_email'],
      'enabled': True,
      'first_name': 'Julie',
      'how_empathy': 'test how',
      'init_date': datetime.datetime(2023, 5, 30, 20, 55, 28, 581452, tzinfo=anvil.tz.tzoffset(hours=0)),
      'last_login': datetime.datetime(2023, 11, 5, 1, 43, 23, 558000, tzinfo=anvil.tz.tzoffset(hours=0)),
      'n_password_failures': 0,
      'profile': '',
      'profile_updated': None,
      'profile_url': '',
      'remembered_logins': [],
      'signed_up': datetime.datetime(2021, 9, 30, 20, 51, 29, 751000, tzinfo=anvil.tz.tzoffset(hours=0)),
      'trust_level': 2,
      'url_confirmed_date': None},
    ems['test_user3_email']: { 'confirmed_email': True,
      'contributor': True,
      'email': ems['test_user3_email'],
      'enabled': True,
      'first_name': 'Linda',
      'how_empathy': 'Please wait until I request an empathy guess.',
      'init_date': datetime.datetime(2023, 11, 29, 19, 36, 35, 200730, tzinfo=anvil.tz.tzoffset(hours=0)),
      'last_login': datetime.datetime(2024, 1, 28, 19, 54, 44, 203000, tzinfo=anvil.tz.tzoffset(hours=0)),
      'n_password_failures': 0,
      'profile': '3 years of Compassion Course. New to empathy buddy chats but '
                "I've participated in a CC Empathy Cafe.",
      'profile_updated': datetime.datetime(2023, 5, 31, 12, 29, 43, 209488, tzinfo=anvil.tz.tzoffset(hours=0)),
      'profile_url': '',
      'remembered_logins': [],
      'signed_up': datetime.datetime(2019, 1, 16, 2, 36, 59, 247000, tzinfo=anvil.tz.tzoffset(hours=0)),
      'trust_level': 3,
      'url_confirmed_date': None},
  }
  
  user_rows = {row['email']: row for row in app_tables.users.search(email=q.any_of(*list(ems.values())))}
  for u in user_rows.values():
    accounts.init_user_info(u)
    u.update(test_chars[u['email']])
  
  app_tables.connections.add_rows(
    [ { 'current': True,
        'date': datetime.datetime(2021, 11, 19, 17, 57, 15, 84823, tzinfo=anvil.tz.tzoffset(hours=0)),
        'date_described': datetime.datetime(2021, 11, 19, 17, 57, 15, 84823, tzinfo=anvil.tz.tzoffset(hours=0)),
        'distance': 1,
        'relationship2to1': 'less privileged alter ego',
        'user1': user_rows[ems['admin_email']],
        'user2': user_rows[ems['test_user3_email']]},
      { 'current': True,
        'date': datetime.datetime(2021, 11, 19, 17, 59, 24, 245897, tzinfo=anvil.tz.tzoffset(hours=0)),
        'date_described': datetime.datetime(2021, 11, 19, 17, 59, 24, 245897, tzinfo=anvil.tz.tzoffset(hours=0)),
        'distance': 1,
        'relationship2to1': 'alter ego',
        'user1': user_rows[ems['test_user3_email']],
        'user2': user_rows[ems['admin_email']]},
    ]
  )
  
  app_tables.groups.add_rows(
    [ { 'created': datetime.datetime(2022, 1, 13, 20, 51, 57, 483756, tzinfo=anvil.tz.tzoffset(hours=0)),
        'current': True,
        'hosts': [user_rows[ems['admin_email']]],
        'name': 'New Group1a'},
      { 'created': datetime.datetime(2022, 1, 13, 21, 8, 39, 683864, tzinfo=anvil.tz.tzoffset(hours=0)),
        'current': True,
        'hosts': [user_rows[ems['admin_email']]],
        'name': 'New Group4'},
    ]
  )
  group_rows = {row['name']: row for row in app_tables.groups.search(name=q.any_of('New Group1a', 'New Group4'))}

  
  app_tables.group_members.add_rows(
    [ { 'group': group_rows['New Group1a'],
        'guest_allowed': False,
        'invite': None,
        'user': user_rows[ems['test_user3_email']]},
      { 'group': group_rows['New Group4'],
        'guest_allowed': True,
        'invite': None,
        'user': user_rows[ems['test_user2_email']]},
      { 'group': group_rows['New Group4'],
        'guest_allowed': None,
        'invite': None,
        'user': user_rows[ems['test_user3_email']]},
    ]
  )