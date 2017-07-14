from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from tpobot.settings import AT, VT
import json
import requests

from .models import *


class IndexView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("lol, don't do this!")


def post_facebook_message(fbid, recevied_message):
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token={0}'
    url = url.format(AT)
    response_msg = json.dumps({
                        "recipient":{"id":fbid},
                        "message": {"text":recevied_message}
                        })
    headers = {"Content-Type": "application/json"}
    status = requests.post(url, headers=headers, data=response_msg)
    print('post message status:', status.json())


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
                    post_facebook_message(psid, message['message']['text'])
        return HttpResponse()



