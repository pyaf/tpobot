from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from celery import shared_task
import requests
import logging
import json
from wit import Wit
from wit.wit import WitError
from collections import defaultdict

from tpobot.settings import AT, wit_server_AT
from bot.models import User
from bot.messages import *

logger = get_task_logger(__name__)

client = Wit(access_token=wit_server_AT)

#get the intent
def call_wit(msg):
    logging.info('\ncalling wit for %s' %msg)
    try:
        resp = client.message(msg)
        return defaultdict(lambda:None, resp['entities'])
    except WitErro as e:
        return {'e': e}


def send_msg(psid, msg):
    logging.info("sending msg %s" %msg)
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token={0}'
    url = url.format(AT)
    response_msg = json.dumps({
                        "recipient":{"id": psid},
                        "message": {"text": msg}
                        })

    headers = {"Content-Type": "application/json"}
    status = requests.post(url, headers=headers, data=response_msg)
    logging.info('sent message status: %s', status.content)

@shared_task
def completeProfile(psid, received_msg):
    user = User.objects.get(psid=psid)
    received_msg = received_msg.strip().split(' ')
    if len(received_msg) != 1:
        msg = message_dict['reg_error']
        send_msg(psid, msg)
        return

    value = received_msg[0].lower()

    if '@' in value and user.email is None:#it's email and user hasn't set it yet
        if 'itbhu.ac.in' in value:
            temp = value.split('@')[0].split('.')[-1]
            if len(temp) != 5: #like eee15
                msg = message_dict['invalid_email']
                send_msg(psid, msg)
                return
            user.department = temp[:3]#eee
            user.email = value
            user.save()
            msg = message_dict['email_set'].format(value)
            send_msg(psid, msg)
            msg = message_dict['get_course']
            send_msg(psid, msg)
            return
        else:
            msg = message_dict['not_iit_email']
            send_msg(psid, msg)
            return

    elif (value=='idd' or value=='btech' or value=='imd') and \
                                user.course is None and user.email:
        #true when email is set, course isn't, you got a valid value

        user.course = value
        user.profile_completed = True
        user.save()
        msg = message_dict['course_set'].format(value)
        send_msg(psid, msg)
        msg = message_dict['reg_success']
        send_msg(psid, msg)
    else:
        msg = message_dict['reg_error']
        send_msg(psid, msg)
        return

@shared_task
def newUser(psid):
#will use graph API to save few user fields, rest to be asked in complete profile function
    url = 'https://graph.facebook.com/v2.6/{0}?fields=first_name,last_name,'\
            'profile_pic,locale,timezone,gender&access_token={1}'
    url = url.format(psid, AT)
    # logging.info(url)
    response = requests.get(url)
    data = response.json()
    logging.info('Got response of graph API, code: ' + str(response.status_code))
    first_name = data['first_name']
    last_name = data['last_name']
    profile_pic = data['profile_pic']
    gender = data['gender']
    logging.info("New User %s %s" %(first_name, last_name))
    user = User.objects.create(psid=psid, 
                                    first_name = first_name, 
                                    last_name = last_name, 
                                    gender = gender, 
                                    profile_pic = profile_pic)

    msg = message_dict['welcome']
    send_msg(psid, msg)
    msg = message_dict['get_email']
    send_msg(psid, msg)



@shared_task
def analyseMessage(psid, message):
    response = call_wit(message)
    logging.info('\n wit response: \n')
    logging.info(dict(response))
    msg = None
    if not response['e']:#no error, got some intents
        try:
            if response['greetings'][0]['confidence'] > 0.80:
                msg = message_dict['greetings']
                send_msg(psid, msg)
        except:
            pass
        try:
            intent = response['intent'][0] 
            if intent:
                if intent['value']=='haalchaal' and intent['confidence'] > 0.80:
                    msg = message_dict['haalchaal']
                    send_msg(psid, msg)
                if intent['value']=='intern_update' and intent['confidence'] > 0.80:
                    pass
                if intent['value']=='feature' and intent['confidence'] > 0.80:
                    msg = message_dict['features']
                    send_msg(psid, msg)
        except:
            pass
        try:
            question = response['question'][0]
            if question['value']=='master' and question['confidence'] > 0.80:
                msg = message_dict['master']
                print('\ngot master', msg)
                send_msg(psid, msg)
        except:
            pass

    if not msg:
        msg = message_dict['no_idea']
        send_msg(psid, msg)



        

