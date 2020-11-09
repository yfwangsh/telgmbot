import os
import  hashlib
from telethon import Button
import random
import string

s_version='1.0'
s_type=0

s_prefix='!'

def help():
    return ':nmchg : change name of file with no space'

def doauthorize(context):
    authfunc = context.get('authorfunc')
    event = context.get('event')
    return authfunc(event)

async def process(context):
    result = {}
    #result['msg'] = 'mlist ok'
    result['retexec'] = 0
    result['msg'] = nmchg(context)
    #result['parse_mod'] = 0
    return result

def nmchg(context):
    conf = context['conf'] 
    dwlist = context['downloadcache'] 
    mdir = conf.getConf('local', 'storage_path')
    msg = 'result:\n'
    flist = os.listdir(mdir)
    idx = 1
    for fe in flist:
        newfe = fe.replace(' ','-')
        if newfe != fe:
            ss = dwlist.get(fe)
            if ss is None:
                os.rename(mdir + '/' + fe, mdir + '/' + newfe)
                msg = msg + '%s move to %s'%(fe, newfe)

            else:
                msg = msg + '%s can not be changed, downloading\n'%(fe)
        idx = idx + 1
    return msg
if __name__ == '__main__':
    msg = 'result:\n'
    mdir='media'
    dwlist={'0228 - 副本.xls':120, '这样写出好故事：人物对话.epub':300}
    flist = os.listdir(mdir)
    idx = 1
    for fe in flist:
        newfe = fe.replace(' ','-')
        if newfe != fe:
            ss = dwlist.get(fe)
            if ss is None:
                os.rename(mdir + '/' + fe, mdir + '/' + newfe)
                msg = msg + '%s move to %s\n'%(fe, newfe)

            else:
                msg = msg + '%s can not be changed, downloading\n'%(fe)
        idx = idx + 1
    print(msg)