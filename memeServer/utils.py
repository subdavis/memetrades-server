from flask import jsonify
import random

from . import settings
#
# Some helper functions
#

def get_new_key():
    alphadigits = "0123456789abcdefghijklmnopqrstuvwxyz"
    return "".join([ alphadigits[random.randint(0,35)] for _ in range(settings.API_KEY_LENGTH) ])

def success():
    return jsonify({"status":"success"})

def fail():
    return jsonify({"status":"fail"})

def role_error(roles):
    return jsonify({"status": "fail", "reason": "user does not have permission"})