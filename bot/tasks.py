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
from bot.IntentParser import *

logger = get_task_logger(__name__)

client = Wit(access_token=wit_server_AT)

WitResponseTypes = {

    'intent': Intent(),
    'greetings': Greeting(),
    'question': Question(),

}
#get the intent
def call_wit(msg):
    logging.info('\ncalling wit for %s' %msg)
    try:
        resp = client.message(msg)
        return (resp['entities'], True)
    except WitError as e:
        logging.info('Got WitError %s ' %e)
        return ({'e': e}, False)



@shared_task
def completeProfile(psid, received_msg):
    user = User.objects.get(psid=psid)
    received_msg = received_msg.strip().split(' ')
    if len(received_msg) != 1:
        msg = message_dict['reg_error']
        return send_msg(psid, msg)
        

    value = received_msg[0].lower()

    if '@' in value and user.email is None:#it's email and user hasn't set it yet
        if 'itbhu.ac.in' in value:
            temp = value.split('@')[0].split('.')[-1]
            if len(temp) != 5: #like eee15
                msg = message_dict['invalid_email']
                return send_msg(psid, msg)
                
            user.department = temp[:3]#eee
            user.email = value
            user.save()
            msg = message_dict['email_set'].format(value)
            send_msg(psid, msg)
            msg = message_dict['get_course']
            return send_msg(psid, msg)
            
        else:
            msg = message_dict['not_iit_email']
            return send_msg(psid, msg)
            

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
        return send_msg(psid, msg)
        

#will use graph API to save few user fields, rest to be asked in complete profile function
@shared_task
def newUser(psid):
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
    logging.info('New User %s %s' %(first_name, last_name))
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
    response, status = call_wit(message)
    msg_sent_count = 0
    logging.info('wit response: %s' % dict(response))
    if status:
        for responseType in response:
            logging.info('responseType '+ str(responseType))
            responseClass = WitResponseTypes[responseType]
            logging.info('Response Class: ' + responseClass.__class__.__name__)
            #every responseType has a list of such intent types
            for eachResponse in response[responseType]:
                logging.info('Checking eachResponse: %s' % eachResponse)
                method = getattr(responseClass, eachResponse['value'])
                logging.info('Calling method: ' + method.__name__)
                msgSent = method(psid, eachResponse['confidence'])
                msg_sent_count += bool(msgSent)

    else:#WitError
        msg = message_dict['wit_error']
        msgSent = send_msg(psid, msg)
        msg_sent_count += bool(msgSent)        

    if msg_sent_count == 0:
        msg = message_dict['no_idea']
        send_msg(psid, msg)



        

