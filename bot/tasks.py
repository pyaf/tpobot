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

def reg_error(psid, user):
    msg = message_dict['reg_error']
    send_msg(psid, msg)
    if user.email is None:
        msg = message_dict['get_email']
        send_msg(psid, msg)
    elif user.course is None:
        msg = message_dict['get_course']
        send_msg(psid, msg)
    return

@shared_task
def completeProfile(psid, received_msg):
    user = User.objects.get(psid=psid)
    received_msg = received_msg.strip().split(' ')
    if len(received_msg) != 2:
        reg_error(psid, user)
        return

    field = received_msg[0].lower() 
    value = received_msg[1].lower()

    #check for email
    if field == 'email':
        if user.email != None:#email already there
            msg = message_dict['email_already_set'].format(user.email)
            send_msg(psid, msg)
            return
        if '@' not in value or 'itbhu.ac.in' not in value:#will work for iitbhu too.
            msg = message_dict['invalid_email']
            send_msg(psid, msg)
            return

        temp = value.split('@')[0].split('.')[-1]
        user.department = temp[:3]
        user.email = value        
        user.save()
        msg = message_dict['email_set'].format(value)
        send_msg(psid, msg)
        msg = message_dict['get_course']
        send_msg(psid, msg)
        if user.course != None:
            user.profile_completed = True
            user.save()
        return

    elif field == 'course':
        if user.course != None:
            msg = message_dict['course_already_set'].format(user.course)
            send_msg(psid, msg)
            return
        elif value=='idd' or value=='btech' or value=='imd':
            user.course = value
            user.save()
            msg = message_dict['course_set'].format(value)
            send_msg(psid, msg)
            if user.email != None:
                user.profile_completed = True
                user.save()
                msg = message_dict['reg_success']
                send_msg(psid, msg)
            else:
                msg = message_dict['get_email']
                send_msg(psid, msg)
            return
        else:
            msg = message_dict['invalid_course']
            send_msg(psid, msg)
            return
    else:
        reg_error(psid, user)
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



        

