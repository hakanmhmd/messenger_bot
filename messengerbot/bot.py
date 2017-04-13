#!/usr/bin/env python

import os
import requests
import apiai
import json
from sys import argv
from wit import Wit
from bottle import Bottle, request, debug
from dotenv import load_dotenv

# Setup Bottle Server
debug(True)
app = Bottle()


# Facebook Messenger GET Webhook
@app.get('/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    verify_token = request.query.get('hub.verify_token')
    # check whether the verify tokens match
    if verify_token == FB_VERIFY_TOKEN:
        # respond with the challenge to confirm
        challenge = request.query.get('hub.challenge')
        return challenge
    else:
        return 'Invalid Request or Verification Token'


# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    print('In webhook post')
    data = request.json
    if data['object'] == 'page':
        for entry in data['entry']:
            # get all the messages
            messages = entry['messaging']
            for message in messages:
                if 'message' in message:
                    # We retrieve the Facebook user ID of the sender
                    fb_id = message['sender']['id']
                    # We retrieve the message content
                    text = message['message']['text']
                    processMessage(fb_id, text)
    else:
        # Returned another event
        return 'Received Different Event'
    return None

# Fetch image from getty
def fetch_image_by_text(searchQuery):
    # GET request to getty
    url = GETTY_URL + searchQuery
    response = requests.get(url, headers={'Api-Key': GETTY_TOKEN})
    parsedResp = json.loads(response.content)
    # Get the required parameters
    imageUri = parsedResp['images'][0]['display_sizes'][0]['uri']

    return imageUri

def send_image_message(sender_id, imageUri):
    print('In send image message')
    """
    Function for returning image response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'attachment': {'type': 'image', 'payload': {'url': imageUri}}}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content

def send_text_message(sender_id, text):
    print('In send text message')
    """
    Function for returning text response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content


def processMessage(fb_id, input):
    print('In process message')
    request = ai.text_request()
    request.lang = 'en'
    request.session_id = 'messengerbot'
    request.query = input
    response = request.getresponse()
    
    parsedResp = json.loads(response.read())
    print parsedResp
    result = parsedResp.get('result')
    if result is None:
        return ''
    fulfillment = result.get('fulfillment')
    if fulfillment is None:
        return ''
    speech = fulfillment.get('speech')
    if speech is None:
        return ''
    
    metadata = result.get('metadata')
    intentName = metadata.get('intentName')
    if intentName is None:
        print('Sending message... ')
        send_text_message(fb_id, speech)
    elif intentName == 'images.search':
        print('Sending image... ')
        searchQuery = result['parameters']['image_name']
        if searchQuery == '':
            return send_text_message(fb_id, 'I could not find any images.')
        imageUri = fetch_image_by_text(searchQuery)
        send_image_message(fb_id, imageUri)



if __name__ == '__main__':
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    # Messenger API parameters
    FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')

    # A user secret to verify webhook get request.
    FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')

    #getty api
    GETTY_TOKEN = os.environ.get('GETTY_KEY')
    GETTY_URL = 'https://api.gettyimages.com/v3/search/images?fields=id,title,thumb,referral_destinations&sort_order=best&phrase='

    # Api.ai token for NLP
    API_AI_TOKEN = os.environ.get('API_AI_TOKEN')

    # AI instance
    ai = apiai.ApiAI(API_AI_TOKEN)

    # Run Server
    app.run(host='0.0.0.0', port=8000, reloader=True)