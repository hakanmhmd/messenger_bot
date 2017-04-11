from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests, random, re
from pprint import pprint

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
        
        return HttpResponse()

