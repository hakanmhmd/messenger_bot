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
@app.get('/fb_recipebot/secretwebhook/')
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
@app.post('/fb_recipebot/secretwebhook/')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    data = request.json
    if data['object'] == 'page':
        for entry in data['entry']:
            # get all the messages
            messages = entry['messaging']
            for message in messages:
                if 'message' in message:
                    print(message)
                    # We retrieve the Facebook user ID of the sender
                    fb_id = message['sender']['id']
                    # We retrieve the message content
                    text = message['message']['text']
                    fb_message(fb_id, apiaiProcessing(text))
    else:
        # Returned another event
        return 'Received Different Event'
    return None


def fb_message(sender_id, text):
    """
    Function for returning response to messenger
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


def apiaiProcessing(input):
    request = ai.text_request()
    request.lang = 'en'
    request.session_id = 'messengerbot'
    request.query = input
    response = request.getresponse()

    parsedResp = json.loads(response.read())
    return parsedResp['result']['fulfillment']['speech']



if __name__ == '__main__':
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    # Messenger API parameters
    FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')

    # A user secret to verify webhook get request.
    FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')

    # Api.ai token for NLP
    API_AI_TOKEN = os.environ.get('API_AI_TOKEN')

    # AI instance
    ai = apiai.ApiAI(API_AI_TOKEN)

    # Run Server
    app.run(host='0.0.0.0', port=8000)