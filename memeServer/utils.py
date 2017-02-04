import random

from . import settings

#
# Some helper functions
#

def get_new_key():
    alphadigits = "0123456789abcdefghijklmnopqrstuvwxyz"
    return "".join([ alphadigits[random.randint(0,35)] for _ in range(settings.API_KEY_LENGTH) ])
