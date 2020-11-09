import os
import  hashlib
from telethon import Button
s_version='1.0'
s_type=0

s_prefix = ':'
def help():
    return ':back: do nothing'

def doauthorize(context):
    authfunc = context.get('authorfunc')
    event = context.get('event')
    return authfunc(event)

async def process(context):
    conf = context['conf'] 
    sscmdstring = conf.getConf('local', 'startcmds')
    supportcmds = sscmdstring.split('|')
    result = {}
    lbs = []
    idx = 1
    for supcmd in supportcmds:
        txtmsg = supcmd
        row = None
        data = '%s%s'%(s_prefix, supcmd)
        if idx%2 == 1:
            row = []
            lbs.append(row)
        else:
            cid = int((idx-1)/2)
            row = lbs[cid]
        row.append(Button.inline(txtmsg, data))
        idx = idx + 1
    result['msg'] = 'commands list here:'
    result['retexec'] = 0
    result['buttons'] = lbs
    #result['parse_mod'] = 0
    return result
