from wit import Wit
from wit.wit import WitError
from tpobot.settings import wit_server_AT

def send(request, response):
    print('Sending to user...', response['text'])

def my_action(request):
    print('Received from user...', request['text'])

actions = {
    'send': send,
    'my_action': my_action,
}
# print(wit_server_AT)
client = Wit(access_token=wit_server_AT, actions=actions)

request = {'text': 'hello'}
try:
	resp = client.message('asdff asdf asdf')
	print(resp)
except WitErro as e:
	print('err', e)

# session_id = 'my-user-session-42'
# context0 = {}
# try:
	
# 	context1 = client.run_actions(session_id, 'hellllo', context0)
# 	print('The session state is now: ' + str(context1))
# 	context2 = client.run_actions(session_id, 'halo', context1)
# 	print('The session state is now: ' + str(context2))
	
# except WitError as e:
# 	print('err', e)

