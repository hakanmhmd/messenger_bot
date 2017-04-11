from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests, random, re
from pprint import pprint


def post_fb_message(id, message):
    post_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAUs8meKfw4BANFv1Xwlpvb4X6s6Gk5vkmXGyYAJhouKkdAZA3wEvyr0fGEw8kv9WIcihGpvaPWa2ZBxIEUNrE4fetMkcZCfB9hZADPS7mAmNZCOuzWJggUOxmkpdr68H9RtQ4YgZCCX40HLSWAuNdqOhDldEujZA12mnYC2VnwaAZDZD'
    user_url = "https://graph.facebook.com/v2.6/%s"%id
    user_params = {'fields':'first_name,last_name,profile_pic', 'access_token':'EAAUs8meKfw4BANFv1Xwlpvb4X6s6Gk5vkmXGyYAJhouKkdAZA3wEvyr0fGEw8kv9WIcihGpvaPWa2ZBxIEUNrE4fetMkcZCfB9hZADPS7mAmNZCOuzWJggUOxmkpdr68H9RtQ4YgZCCX40HLSWAuNdqOhDldEujZA12mnYC2VnwaAZDZD'}
    user = requests.get(user_url, user_params).json()
    reply_msg = 'Hey '+ user['first_name']+': ' + message
    reply = json.dumps({"recipient":{"id":id}, "message":{"text":reply_msg}})
    status = requests.post(post_url, headers={"Content-Type": "application/json"}, data=reply)

class RecipebotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == '1375110023':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Invalid token!')
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
    
    #Handle fb messages
    def post(self, request, *args, **kwargs):
        message = json.loads(self.request.body.decode('utf-8'))
        for entry in message['entry']:
            for entryMessage in entry['messaging']:
                pprint(entryMessage)
                if 'message' in entryMessage:
                    post_fb_message(entryMessage['sender']['id'], entryMessage['message']['text'])
        return HttpResponse()

