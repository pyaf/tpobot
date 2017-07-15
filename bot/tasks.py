from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from celery import shared_task
import requests
import logging
import json

from tpobot.settings import AT
from bot.models import Sucker
from bot.messages import *

logger = get_task_logger(__name__)


@shared_task
def send_welcome_message(user, psid):
    msg = message_dict['welcome'].format(user.first_name)
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token={0}'
    url = url.format(AT)

    response_msg = json.dumps({
                        "recipient":{"id":psid},
                        "message": {"text": msg}
                        })
    headers = {"Content-Type": "application/json"}

    status = requests.post(url, headers=headers, data=response_msg)
    print('post message status:', status.json())


@shared_task
def send_facebook_message(sucker, psid, msg):
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token={0}'
    url = url.format(AT)

    response_msg = json.dumps({
                        "recipient":{"id": psid},
                        "message": {"text": msg}
                        })

    headers = {"Content-Type": "application/json"}
    status = requests.post(url, headers=headers, data=response_msg)
    print('post message status:', status.json())
