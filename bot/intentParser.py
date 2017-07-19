# -*- coding: utf-8 -*-
import requests
import random
import json

from tpobot.settings import AT
from bot.messages import message_dict
from bot.models import User
from bot.apis import sendFBText

def toggleUserSubcription(psid, flag=False):
    user = User.objects.get(psid=psid)
    if (flag and not user.subscribed) or (not flag and user.subscribed):
        user.subscribed = flag
        user.save()
        msg = message_dict['activate'] if flag else message_dict['deactivate']
        return sendFBText(psid, msg)
    else:
        msg = 'Your account is already so. 😪'
        return sendFBText(psid, msg)

'''
My wit uses three entities namely intent, greetings and question
'''

class Intent(object):
    def haalchaal(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['haalchaal']
            return sendFBText(psid, msg)

    def update(self, psid, confidence):
        pass

    def feature(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['features']
            sendFBText(psid, msg)
            msg = message_dict['features1']
            sendFBText(psid, msg)
            msg = message_dict['features2']
            return sendFBText(psid, msg)

    def help(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['help']
            return sendFBText(psid, msg)

    def deactivate(self, psid, confidence):
        if confidence > 0.75:
            return toggleUserSubcription(psid, flag=False)

    def activate(self, psid, confidence):
        if confidence > 0.75:
            return toggleUserSubcription(psid, flag=True)

    def happiness(self, psid, confidence):
        if confidence > 0.60:
            msg = random.choice(['😁','😃','😄','😉','😊','😎','😘','🙂'])
            return sendFBText(psid, msg)

    def abuse(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['abuse']
            sendFBText(psid, msg)
            return sendFBText(psid, message_dict['lol'])

    def company(self, psid, confidence):
        if confidence > 0.90:
            pass


class Greeting(object):

    def true(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['greetings']
            return sendFBText(psid, msg)


class Question(object):

    def master(self, psid, confidence):
        if confidence>0.90:
            msg = message_dict['master']
            return sendFBText(psid, msg)
