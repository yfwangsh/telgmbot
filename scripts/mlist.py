import os
import  hashlib
from telethon import Button
import random
import string

s_version='1.0'
s_type=0

s_prefix='!'

def help():
    return ':mlist : lists the media files'

def doauthorize(context):
    authfunc = context.get('authorfunc')
    event = context.get('event')
    return authfunc(event)

async def process(context):
    result = {}
    #result['msg'] = 'mlist ok'
    result['deleteEvent'] = True
    result['retexec'] = 0
    result['cachemsg'] = True
    result['buttons'], result['msg'] = listdir(context)
    #result['parse_mod'] = 0
    return result

SHOW_LEN=16
def processtxt(text):
    if len(text) > SHOW_LEN:
        return text[0:SHOW_LEN-4] + '...'
    return text
def listdir(context):
    conf = context['conf'] 
    dwlist = context['downloadcache'] 
    mdir = conf.getConf('local', 'storage_path')
    lbs = []
    msg = 'result:\n'
    flist = os.listdir(mdir)
    idx = 1
    for fe in flist:
        size = os.path.getsize(mdir + '/' + fe)
        dotag = '#'
        mgtag = ''
        ss = dwlist.get(fe)
        if ss is not None:
            mgtag ='/%d',(ss)
            dotag='*'
        txtmsg = '%s%d) %s - (%.2fM)'%(dotag,idx, processtxt(fe), size/(1024*1024))
        msg = msg + '%d) %s - (%.2fM%s) \n'%(idx, fe, size/(1024*1024),mgtag)
        data = '%s%s%s'%(s_prefix, hashlib.md5(fe.encode('utf8')).hexdigest(),context['msgkey'])
        lbs.append([Button.inline(txtmsg, data)])
        idx = idx + 1
        #lbs.append(Button.text(fe,  single_use=True, selective=True))
    return lbs, msg    
if __name__ == '__main__':
    rtext = ':abc /start wwww'
    al=[1,2,3,4]
    print(al[1])
    print('%.2f'%(2345/1000))
    print(rtext.find('/'))
    target = rtext[0:rtext.find('/')]
    cmdmsg = rtext[rtext.find('/'):]
    print('[' + target.strip() + ']')
    print(cmdmsg)
    for i in range(1,2):
        ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 24))
        data = '!%s%s'%(hashlib.md5(ran_str.encode('utf8')).hexdigest(), ran_str)
        print(hashlib.md5(ran_str.encode('utf8')).hexdigest())
        print(data[1:33])
        print ('%d, [%s]'%(len(data), ran_str))
        print(data[33:])
        
