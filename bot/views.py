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

class IndexView(generic.View):
    template_name = 'privacy.html'
    def get(self, request, *args, **kwargs):
        return render(self.request, self.template_name, {})


class Webhook(generic.View):
    def get(self, request, *args, **kwargs):
	    if self.request.GET['hub.verify_token'] == VT:
	        return HttpResponse(self.request.GET['hub.challenge'])
	    else:
	        return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            incoming_message = json.loads(self.request.body.decode('utf-8'))
            for entry in incoming_message['entry']:
                for message in entry['messaging']:
                    if 'message' in message:
                        text =  message['message']['text']
                        psid = message['sender']['id']
                        print(text, psid)
                        try:
                            user = User.objects.get(psid=psid)
                            if user.valid:
                                if user.profile_completed:
                                    analyseMessage.delay(psid, text)
                                else:#get user profile completed
                                    completeProfile.delay(psid, text)
                            else:
                                gotInactiveUser.delay(psid)
                        except Exception as e:
                            # print('\nnew user,, yaaayyye')
                            newUser.delay(psid)
        except Exception as e:
            # print(incoming_message)
            print("Exception: ", e)
        return HttpResponse()
