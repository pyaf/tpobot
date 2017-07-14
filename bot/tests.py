from django.test import TestCase
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from tpobot.settings import AT
import requests

@shared_task
def catchTheSucker(psid):
    print('running catchTheSucker')
    url = 'https://graph.facebook.com/v2.6/{0}?fields=first_name,last_name,\
            profile_pic,locale,timezone,gender,link&access_token={1}'
    url = url.format(psid, AT)
    response = requests.get(url)
    print(response)
