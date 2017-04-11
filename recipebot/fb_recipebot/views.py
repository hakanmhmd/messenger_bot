from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse


class RecipebotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == '1375110023':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Invalid token!')
