from django.conf.urls import include, url
from .views import RecipebotView
urlpatterns = [
    url(r'^secretwebhook/?$', RecipebotView.as_view())
]