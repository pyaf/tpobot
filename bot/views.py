from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from tpobot.settings import AT, VT
import json
import requests
import logging

from bot.models import *
from bot.messages import *
from bot.tasks import *

def newSucker(psid):
    print('running catchTheSucker')
    url = 'https://graph.facebook.com/v2.6/{0}?fields=first_name,last_name,'\
            'profile_pic,locale,timezone,gender&access_token={1}'
    url = url.format(psid, AT)
    logging.info(url)
    response = requests.get(url)
    data = response.json()
    logging.info(data)

    sucker, created = Sucker.objects.get_or_create(psid=psid)
    if created:
        first_name = data['first_name']
        last_name = data['last_name']
        profile_pic = data['profile_pic']
        gender = data['gender']
        logging.info("New Sucker")
        sucker.first_name = first_name
        sucker.last_name = last_name
        sucker.gender = gender
        sucker.profile_pic = profile_pic
        sucker.save()

    return (sucker, created)

class IndexView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("lol, don't do this!")


class BotView(generic.View):
    def get(self, request, *args, **kwargs):
	    if self.request.GET['hub.verify_token'] == VT:
	        return HttpResponse(self.request.GET['hub.challenge'])
	    else:
	        return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print('\nGOT A POST REQUEST!')

        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    text =  message['message']['text']
                    psid = message['sender']['id']
                    print(text, psid)
                    sucker, created = newSucker(psid)
                    if created:
                        send_welcome_message.delay(sucker, psid)
                    else:
                        send_facebook_message.delay(sucker, psid, message['message']['text'])
        return HttpResponse()
