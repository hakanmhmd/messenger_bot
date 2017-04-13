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
    data = request.json
    print data
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

@app.post('/image-search')
def image_search():
    """
    Handler for image search webhook
    """
    # Dissect the body
    body = json.loads(request.body.read())
    action = body['result']['action']
    # Check for type of action
    if action == 'image':
        # Retrieve search query
        searchQuery = body['result']['parameters']['image_name']
        # GET request to getty
        url = GETTY_URL + searchQuery
        response = requests.get(url, headers={'Api-Key': GETTY_TOKEN})
        parsedResp = json.loads(response.content)
        # Get the required parameters
        imageUri = parsedResp['images'][0]['display_sizes'][0]['uri']
        
        # Build a json object to return
        data = {}
        data['speech'] = imageUri
        data['displayText'] = imageUri
        data['source'] = 'image_name'
        return json.dumps(data)

def send_image_message(sender_id, imageUri):
    """
    Function for returning image response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'attachment': {'type': 'image', 'payload': {'uri': imageUri}}}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content

def send_text_message(sender_id, text):
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
    request = ai.text_request()
    request.lang = 'en'
    request.session_id = 'messengerbot'
    request.query = input
    response = request.getresponse()
    
    parsedResp = json.loads(response.read())
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
        print('Sending messages... ' + speech)
        send_text_message(fb_id, speech)
    elif intentName == 'images.search':
        print('Sending image... ' + speech)
        send_image_message(fb_id, speech)



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