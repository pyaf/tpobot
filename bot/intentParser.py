import logging
import json
import requests
from tpobot.settings import AT
from bot.messages import message_dict
from bot.models import User

def send_msg(psid, msg):
    logging.info('sending msg %s' %msg)
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token={0}'
    url = url.format(AT)

    response_msg = json.dumps({
                        'recipient':{'id': psid},
                        'message': {'text': msg}
                        })

    headers = {'Content-Type': 'application/json'}
    try:
        status = requests.post(url, headers=headers, data=response_msg)
        logging.info('Sent message status: %s', status.content)
        return True
    except Exception as e:
        logging.info("Got an Exception while sending message: %s" %e)
        return False

def toggleUserSubcription(psid, flag=False):
    user = User.objects.get(psid=psid)
    if (flag and not user.subscribed) or (not flag and user.subscribed):
        user.subscribed = flag
        user.save()
        if flag:
            return send_msg(psid, message_dict['activate'])
        else:
            return send_msg(psid, message_dict['deactivate'])
    else:

        msg = 'Your account is already so. 😪'
        return send_msg(psid, msg)

'''
My wit uses three entities namely intent, greetings and question
''' 

class Intent(object):
    def haalchaal(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['haalchaal']
            return send_msg(psid, msg)
        
    def update(self, psid, confidence):
        pass

    def feature(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['features']
            return send_msg(psid, msg)
        

    def help(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['help']
            return send_msg(psid, msg)
        
    def deactivate(self, psid, confidence):
        if confidence > 0.75:
            toggleUserSubcription(psid, flag=False)
        
    def activate(self, psid, confidence):
        if confidence > 0.75:
            toggleUserSubcription(psid, flag=True)
        
    def happiness(self, psid, confidence):
        if confidence > 0.60:
            msg = random.choice(['😁','😃','😄','😉','😊','😎','😘','🙂'])
            return send_msg(psid, msg)
        
    def abuse(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['abuse']
            return send_msg(psid, msg)

            
class Greeting(object):

    def true(self, psid, confidence):
        if confidence > 0.80:
            msg = message_dict['greetings']
            return send_msg(psid, msg)  

class Question(object):

    def master(self, psid, confidence):
        if confidence>0.90:
            msg = message_dict['master']
            return send_msg(psid, msg)
        

