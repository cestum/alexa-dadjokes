"""
An extremely simple dad joke teller. Jokes are chosen randomly from /r/dadjokes. 

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import json
import random
import urllib
import re
# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(card_output, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': "Here is one. " + output
        },
        'card': {
            'type': 'Simple',
            'title': 'Joke',
            'content': card_output
        },
        # 'reprompt': {
        #     'outputSpeech': {
        #         'type': 'PlainText',
        #         'text': reprompt_text
        #     }
        # },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------
def getJoke():
    url = 'https://www.reddit.com/r/dadjokes/random.json?limit=1'
    response = urllib.urlopen(url).read()
    jsonStr = json.loads(response)   
    jsonStr = jsonStr[0]["data"]["children"][0]
    jokeq = jsonStr["data"]["title"]
    jokea = jsonStr["data"]["selftext"]
    if len(jokea) > 200:
        raise KeyError("Too long for a joke!")
    if(not re.match("""^[a-zA-Z0-9_\?\,"\'\!.\s\*]*$""", jokea + " " + jokeq)):
        raise KeyError("contains special character")
    return (jokeq,jokea)

def get_joke_response():
    session_attributes = {}
    result = None
    while result is None:
        try:
            result= getJoke()
        except KeyError as e:
            pass
    card_output = result[0] + " " + result[1]
    speech_output =  result[0] + " " + result[1]
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_output, speech_output, None, should_end_session))



# --------------- Events ------------------

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_joke_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == "AMAZON.HelpIntent" or intent_name == "askdad":
        return get_joke_response()
    else:
        raise ValueError("Invalid intent")




# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.xxx"):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
