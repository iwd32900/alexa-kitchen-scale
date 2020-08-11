# cups of volume per unit
UNITS = {
    'teaspoon': 1/48,
    'teaspoons': 1/48,
    'tablespoon': 1/16,
    'tablespoons': 1/16,
    'cup': 1,
    'cups': 1,
    'pint': 2,
    'pints': 2,
    'quart': 4,
    'quarts': 4,
    'gallon': 16,
    'gallons': 16,
}

# oz of weight per cup
INGREDIENTS = {
    'buttermilk': 8.75,
    'chocolate chips': 6.5,
    'cocoa': 3,
        'cocoa powder': 3,
    'coconut flakes': 2.75,
    'corn': 5,
        'corn kernels': 5,
        'frozen corn': 5,
    'corn syrup': 11,
        'dark corn syrup': 11,
        'light corn syrup': 11,
    'cornmeal': 4,
        'corn meal': 4,
    'cornstarch': 4.5,
        'corn starch': 4.5,
    'cream': 8.75,
        'heavy cream': 8.75,
        'whipping cream': 8.75,
    'Crisco': 6.5,
        'crisco': 6.5,
        'shortening': 6.5,
        'vegetable shortening': 6.5,
    'flour': 4.75,
        'all purpose flour': 4.75,
    'graham cracker crumbs': 3,
    'honey': 13.5,
    'jam': 12,
        'jelly': 12,
        'preserves': 12,
    'mayonaisse': 8,
        'mayo': 8,
    'milk': 8.75,
        'whole milk': 8.75,
        'skim milk': 8.75,
    'molasses': 11.75,
    'oats': 3.5,
        'old fashioned oats': 3.5,
    'oil': 7,
        'canola oil': 7,
        'olive oil': 7,
        'vegetable oil': 7,
    'peanut butter': 8.75,
    'powdered sugar': 3.75,
        'confectioners sugar': 3.75,
    'rice': 6.75,
    'sour cream': 7.75,
    'shredded cheese': 4,
        'shredded cheddar': 4,
        'shredded Cheddar': 4,
    'sifted flour': 4.125,
    'sifted powdered sugar': 3.25,
        'sifted confectioners sugar': 3.25,
    'sugar': 7,
        'brown sugar': 7,
        'dark brown sugar': 7,
        'granulated sugar': 7,
        'light brown sugar': 7,
    'sweetened condensed milk': 11.5,
}

def respond(output, reprompt=None, session={}, end=True):
    def make_ssml(text):
        return {
            'type': 'SSML',
            'ssml': '<speak>{}</speak>'.format(text)
        }
    response = {
        'version': '1.0',
        'sessionAttributes': session,
        'response': {
            'outputSpeech': make_ssml(output),
            'shouldEndSession': end
        }
    }
    if reprompt:
        response['response']['reprompt'] = make_ssml(reprompt)
    return response

def convert_to_cups(slots):
    frac = {
        'half': 2,
        'third': 3,
        'thirds': 3,
        '3rd': 3,
        '3rds': 3,
        'fourth': 4,
        'fourths': 4,
        '4th': 4,
        '4ths': 4,
        'quarter': 4,
        'quarters': 4,
        'eighth': 8,
        'eighths': 8,
        '8th': 8,
        '8ths': 8,
    }
    quantity = 0
    used_quantity = False
    if slots['decimal']:
        quantity += float("0." + slots['decimal'])
    if slots['denominator'] in frac:
        if slots['numerator']:
            numerator = int(slots['numerator'])
        elif slots['quantity'] not in [None, '?']:
            # For "one fourth cup", Alexa recognizes one as the quantity, not the numerator.
            # For "one and a fourth cup", Alexa translates "a" to numerator = 1.
            # So if we see denominator, quantity, and numerator = None, we're probably looking at a proper fraction.
            numerator = int(slots['quantity'])
            used_quantity = True
        else:
            numerator = 1
        denominator = frac[slots['denominator']]
        quantity += numerator /  denominator
    if slots['quantity'] not in [None, '?'] and not used_quantity:
        quantity += int(slots['quantity'])
    cups = quantity * UNITS[slots['unit']]
    return round(cups, 2)

def speak_ounces(weight_oz):
    frac = ["", "one eighth", "one quarter", "three eighths", "one half", "five eighths", "three quarters", "seven eighths"]
    eighths = int(round(weight_oz*8))
    if eighths == 0: return "zero"
    elif eighths < 8: return frac[eighths]
    elif eighths == 8: return "one"
    elif eighths % 8 == 0: return f"{eighths//8}"
    else: return f"{eighths//8} and {frac[eighths % 8]}"

def round_grams(weight_g):
    # Round to the nearest 2% (maximum 1% rounding error)
    if weight_g > 500:
        return int(10 * round(weight_g/10))
    # Round to the nearest 5% (maximum 2.5% rounding error)
    elif weight_g > 100:
        return int(5 * round(weight_g/5))
    else:
        return int(round(weight_g))

def on_GetWeight(intent, session):
    slots = {k: v.get('value') for k, v in intent['slots'].items()}
    print(f"Slots = {slots}")

    # "tablespoons" works fine in test, but not production, for some reason...
    if slots['unit'] in ['spoon', 'spoons'] and slots['denominator'] in ['tea', 'table']:
        slots['unit'] = slots['denominator'] + slots['unit']
        slots['denominator'] = None

    if slots['unit'] not in UNITS:
        return respond("Sorry, I don't recognize that unit of measurement.")

    if slots['ingredient'] not in INGREDIENTS:
        return respond("Sorry, I'm not familiar with that ingredient.")

    num_cups = convert_to_cups(slots)
    ingredient = slots['ingredient']
    weight_oz = num_cups * INGREDIENTS[ingredient]
    weight_g = weight_oz * 28.35

    return respond(f"{num_cups} cups of {ingredient} weighs {speak_ounces(weight_oz)} ounces, or {round_grams(weight_g)} grams.")

def on_Help():
    return respond("""
    Weights and Measures can help you with your kitchen scale.
    Say, "Alexa, ask Weights and Measures for one quarter cup of flour".
    Or, "Alexa, ask Weights and Measures for two point five cups of sugar".
    """)

def on_Stop():
    return respond("Goodbye!")

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return on_Help()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetWeightIntent":
        return on_GetWeight(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return on_Help()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return on_Stop()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if event['session']['application']['applicationId'] != "amzn1.ask.skill.127b4004-869d-4a54-ae0c-4b2b711019f5":
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
    else:
        raise ValueError("Invalid request type")
