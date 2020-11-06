import os
import  hashlib
from telethon import Button
s_version='1.0'
s_type=0

def help():
    return ':mlist : lists the media files'

def doauthorize(context):
    authfunc = context.get('authorfunc')
    event = context.get('event')
    return authfunc(event)

async def process(context):
    result = {}
    result['msg'] = 'mlist ok'
    result['retexec'] = 0
    result['buttons'] = listdir(context)
    #result['parse_mod'] = 0
    return result

SHOW_LEN=24
def processtxt(text):
    if len(text) > SHOW_LEN:
        return text[0:SHOW_LEN-4] + '...'
    return text
def listdir(context):
    conf = context['conf'] 
    mdir = conf.getConf('local', 'storage_path')
    lbs = []
    flist = os.listdir(mdir)
    for fe in flist:
        size = os.path.getsize(mdir + '/' + fe)
        txtmsg = '%s - (%f)'%(processtxt(fe), size/(1024*1024))
        data = '%s %s'%(':show', hashlib.sha1(fe.encode('utf8')).hexdigest())
        lbs.append([Button.inline(txtmsg, data)])
        #lbs.append(Button.text(fe,  single_use=True, selective=True))
    return lbs    
if __name__ == '__main__':
    rtext = ':abc /start wwww'
    print(rtext.find('/'))
    target = rtext[0:rtext.find('/')]
    cmdmsg = rtext[rtext.find('/'):]
    print('[' + target.strip() + ']')
    print(cmdmsg)