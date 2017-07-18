from wit import Wit
from wit.wit import WitError
from collections import defaultdict
import requests
import logging
import json
from tpobot.settings import AT, wit_server_AT

client = Wit(access_token=wit_server_AT)

#get the intent
def callWit(msg):
    logging.info('calling wit for %s' % msg)
    try:
        resp = client.message(msg)
        return (resp['entities'], True)
    except WitError as e:
        logging.info('Got WitError %s' % e)
        return ({'e': e}, False)


def getUserFromGraphAPI(psid):
    url = 'https://graph.facebook.com/v2.6/{0}?fields=first_name,last_name,'\
            'profile_pic,locale,timezone,gender&access_token={1}'
    url = url.format(psid, AT)
    # logging.info(url)
    response = requests.get(url)
    # logging.info('Got response of graph API, code: ' + str(response.status_code))
    return response.json()


def sendFBText(psid, msg):
    logging.info('sending msg %s' %msg)
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token={0}'
    url = url.format(AT)

    response_msg = json.dumps({'recipient':{'id': psid},
                                'message': {'text': msg}})

    headers = {'Content-Type': 'application/json'}
    try:
        status = requests.post(url, headers=headers, data=response_msg)
        logging.info(status.text)
        return True
    except Exception as e:
        logging.info("Got an Exception while sending message: %s" %e)
        return False
