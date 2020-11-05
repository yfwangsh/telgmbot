import os
import  hashlib
from telethon import Button
s_version='1.0'
s_type=0

def help():
    return ':show : show available commands to file'

def doauthorize(context):
    return True

async def process(context):
    conf = context['conf'] 
    sscmdstring = conf.getConf('local', 'mlistcmds')
    supportcmds = sscmdstring.split('|')
    result = {}
    buttons = []
    args = context.get('args')
    resultmsg = 'invalid param for show'
    if args is not None and len(args) > 0:
        fileid = args[0]
        filename = getfilename(context, fileid)
        resultmsg = 'available operation for %s'%(filename)
        for supcmd in supportcmds:
            btext = '%s %s'%(supcmd, filename)
            buttons.append([Button.text(btext,single_use=True)])
    buttons.append([Button.text('NOP',single_use=True)])
    result['msg'] =resultmsg
    result['retexec'] = 0
    result['buttons'] = buttons
    #result['parse_mod'] = 0
    return result

def processtxt(text):
    if len(text) > 64:
        return text[0:60] + '...'
    return text
def getfilename(context, fileid):
    conf = context['conf'] 
    mdir = conf.getConf('local', 'storage_path')
    flist = os.listdir(mdir)
    for fe in flist:
        srcfileid = hashlib.sha1(fe.encode('utf8')).hexdigest()
        if srcfileid == fileid:
            return fe
    return None    
if __name__ == '__main__':
    hashtext = hashlib.sha1('abcdsklfjksldf'.encode('utf8')).hexdigest()
    
    hashbytes = hashtext.encode()
    print(hashbytes)
    print(hashbytes.decode())