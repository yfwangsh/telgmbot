import os
import  hashlib
from telethon import Button
s_version='1.0'
s_type=0

def help():
    return ':back: do nothing'

def doauthorize(context):
    authfunc = context.get('authorfunc')
    event = context.get('event')
    return authfunc(event)

async def process(context):

    result = {}
    #result['msg'] = 'mlist ok'
    result['deleteEvent'] = True
    #result['parse_mod'] = 0
    return result
