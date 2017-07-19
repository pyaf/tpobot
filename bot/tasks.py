from __future__ import absolute_import, unicode_literals
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from celery.utils.log import get_task_logger
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task

import traceback
import requests
import logging
import json
import os

from tpobot.settings import AT
from bot.models import User, Company
from bot.intentParser import Intent, Greeting, Question
from bot.spider import crawl
from bot.apis import callWit, getUserFromGraphAPI, sendFBText
from bot.messages import *

logger = get_task_logger(__name__)
# print('logger', __name__)
entityTypes = {
    'intent': Intent(),
    'greetings': Greeting(),
    'question': Question(),
}#all classes imported from intentParser

if os.environ.get('development', '') == 'True':
    mins = 1
else:
    mins = 15


@shared_task
def completeProfile(psid, received_msg):
    user = User.objects.get(psid=psid)
    received_msg = received_msg.strip().split(' ')
    if len(received_msg) != 1:
        msg = message_dict['reg_error']
        return sendFBText(psid, msg)


    value = received_msg[0].lower()

    if '@' in value and not user.email:#it's email and user hasn't set it yet
        if 'itbhu.ac.in' in value:
            temp = value.split('@')[0].split('.')[-1]
            if len(temp) != 5: #like eee15
                msg = message_dict['invalid_email']
                return sendFBText(psid, msg)
            try:
                if int(temp[3:]) >= 15:#let facchas get updates
                    user.purpose = 'internship'
                else:
                    user.purpose = 'placement'
                user.year = int(temp[3:])
                user.department = temp[:3]#eee
                user.email = value
                user.save()
                print('user course: %s\n\n' %user.purpose)
                msg = message_dict['email_set'].format(value)
                sendFBText(psid, msg)
                msg = message_dict['get_course']
                return sendFBText(psid, msg)
            except Exception as e:
                print(e)
                msg = message_dict['invalid_email']
                return sendFBText(psid, msg)
        else:
            msg = message_dict['not_iit_email']
            return sendFBText(psid, msg)


    elif (value=='idd' or value=='btech' or value=='imd') and \
                                not user.course and user.email:
        #true when email is set, course isn't, you got a valid value

        user.course = value
        user.profile_completed = True

        if (value=='idd' or value=='imd') and user.year == 14:
            user.valid=False#idd 4rth yr peeps, zivan ka koi purpose nhi
            user.save()
            msg = message_dict['idd_imd_4th_year']
            return sendFBText(psid, msg)
        user.save()
        msg = message_dict['course_set'].format(value)
        sendFBText(psid, msg)
        updateNewUser(psid)
        msg = message_dict['reg_success']
        return sendFBText(psid, msg)

    else:
        msg = message_dict['reg_error']
        return sendFBText(psid, msg)


#will use graph API to save few user fields, rest to be asked in complete profile function
@shared_task
def newUser(psid):
    data = getUserFromGraphAPI(psid)
    user = User.objects.create(psid=psid,
                            first_name = data['first_name'],
                            last_name = data['last_name'],
                            gender = data['gender'],
                            profile_pic = data['profile_pic'])
    msg = message_dict['welcome']
    sendFBText(psid, msg)
    msg = message_dict['get_email']
    sendFBText(psid, msg)


@shared_task
def analyseMessage(psid, message):
    response, status = callWit(message)
    msg_sent_count = 0
    if status:
        #entity like `intent`, `greetings`, `question` etc
        for entity in response:
            logging.info('Entity %s\n' % str(entity))
            entityClass = entityTypes[entity]
            logging.info('Enitity Class: %s\n' % entityClass.__class__.__name__)
            #every entity has a list of entity types like my `intent` has `happiness`
            for entityType in response[entity]:
                logging.info('Checking entityType: %s\n' % entityType)
                method = getattr(entityClass, entityType['value'])
                logging.info('Calling method: %s\n' % method.__name__)
                msgSent = method(psid, entityType['confidence'])
                msg_sent_count += bool(msgSent)

    else:#WitError
        msg = message_dict['wit_error']
        msgSent = sendFBText(psid, msg)
        msg_sent_count += bool(msgSent)

    logging.info("msg_sent_count: %s\n" % msg_sent_count)
    if msg_sent_count == 0:
        msg = message_dict['no_idea']
        sendFBText(psid, msg)


def updateNewUser(psid):
    user = User.objects.get(psid=psid)
    #logging.info('Gotta update new user %s ', user)
    companies = Company.objects.filter(course__icontains=user.course,
                             department__icontains=user.department,
                             purpose__icontains=user.purpose)

    if len(companies):
         msg = 'Companies opened for you so far:\n\n'
         sendFBText(psid, msg)
    else:
        msg = 'No company is open for you as for now, will inform you when one opens :)'
        return sendFBText(psid, msg)

    for company in companies:
        c = company.__dict__

        msg = c['company_name'] + '\n\n'
        for field in field_msg_dict:
            if c[field]:#if not none
                msg += field_msg_dict[field] + ': ' + c[field] + '\n'

        #logging.info(msg)
        sendFBText(psid, msg)

    msg = "That's it for now, will keep updating you :)"
    return sendFBText(psid, msg)

@shared_task
def informUsersAboutNewCompany(data_dict):
    msg = message_dict['new_company'].format(**data_dict)
    print('\n\n\n informUsersAboutNewCompany')
    for user in User.objects.filter(valid=True,
                            subscribed=True,
                            profile_completed=True,
                            course__in=data_dict['course'].split(),
                            department__in=data_dict['department'].split(),
                            purpose__in=data_dict['purpose'].lower().split()):

        sendFBText(user.psid, msg)


@shared_task
def updateUserAboutThisCompany(data_dict, changed_fields):
    company = Company.objects.get(company_name=data_dict['company_name'])

    msg = ''
    temp = '{0}: {1}\n'
    for field in changed_fields:
        msg += temp.format(field_msg_dict[field], data_dict[field])

    final_msg = message_dict['updated_company'].format(
                                                data_dict['company_name'],
                                                msg,
                                                data_dict['updated_at'])

    for user in User.objects.filter(valid=True,
                            subscribed=True,
                            profile_completed=True,
                            course__in=company.course.split(),
                            department__in=company.department.split(),
                            purpose__in=company.purpose.lower().split()):
        sendFBText(user.psid, final_msg)


@shared_task
def gotInactiveUser(psid):
    msg = message_dict['user_invalid']
    sendFBText(psid, msg)


@periodic_task(run_every=(crontab(minute='*/%d' %mins)), name="crawl_tpo", ignore_result=True)
def crawl_tpo():
    logging.info('Crawling TPO')
    data = crawl()#defined in spider

    for index in data:
        data_dict = data[index]
        try:
            company = Company.objects.get(company_name=data_dict['company_name'])
            if data_dict['updated_at'] != company.updated_at:
                changed_fields = company.update(data_dict)
                logging.info(data_dict['company_name'] + str(changed_fields))
                changed_fields.remove('updated_at')
                updateUserAboutThisCompany(data_dict, changed_fields)

        except ObjectDoesNotExist:
            logging.info("Got a new company")
            Company.objects.create(**data_dict)
            informUsersAboutNewCompany(data_dict)

        except Exception as e:
            logging.info("Got Error in updateUserAboutCompany %s" % e)
            logging.info(traceback.format_exc())

    logging.info('Crawling Done')
