#!/usr/bin/env python3
import json

quantities = [
    "oh point {decimal}", # 0.75
    "zero point {decimal}", # 0.75
    # Alexa doesn't like this one, gets confused
    #"{numerator} {denominator}",
    # Alexa recognizes this more reliably, though `quantity` actually means `numerator` here
    "{quantity} {denominator}", # three quarters
    "{quantity} and {numerator} {denominator}", # one and three quarters
    "{quantity} point {decimal}", # 1.75
    "{quantity}", # one
]

ingredients = [
    "{unit} of {ingredient}", # cups OF flour
    "{unit} {ingredient}", # cups flour
]

frames = [
    "about %s",
    "for %s",

    "the weight of %s",
    "about the weight of %s",
    "for the weight of %s",

    "how much is %s",
    "how much does %s weigh",

    "what is %s",
    "what is the weight of %s",
]

utterances = []
for frame in frames:
    for ingredient in ingredients:
        for quantity in quantities:
            utterances.append(frame % (quantity + " " + ingredient))

print(json.dumps(utterances, indent=4))