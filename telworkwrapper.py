from telethon import TelegramClient,sync
import socks #如果你不需要通过代理连接Telegram，可以删掉这一行
from telethon.tl.types import InputMessagesFilterPhotos
from telethon.tl.types import InputMessagesFilterVideo
from telethon.events import StopPropagation
import asyncio
import glob
import sys
import os
import importlib
from telethon import events
from lib.common import Conf
from lib.common import mylogging



def filterChat(e):
    if e.chat.id == int(telbotwrapper.conf.getConf('messagefilter','downmchatid')):
        return True
    return False

def channelfilter(e):
    if e.chat.id == int(telbotwrapper.conf.getConf('messagefilter','botchatid')):
        return True
    return False
    

class telbotwrapper():
    conf = Conf('conf/telbot.conf', type='raw')
    @staticmethod
    def getproxy(proxyurl):
        proxy = None
        if proxyurl is not None:
            zproxy = proxyurl.split(':')
            if len(zproxy) == 2:
                proxy_host = zproxy[0]
                proxy_port = int(zproxy[1])
                proxy = (socks.SOCKS5,proxy_host,proxy_port)
        return proxy
    def __init__(self):
        self.log = mylogging(telbotwrapper.conf).getLogger()
        self.api_hash = telbotwrapper.conf.getConf('telegram', 'api_hash')
        self.api_id = telbotwrapper.conf.getConf('telegram', 'api_id')
        self.session = telbotwrapper.conf.getConf('telegram', 'session')
        self.storage = telbotwrapper.conf.getConf('local', 'storage_path')
        useproxy = telbotwrapper.conf.getConf('telegram', 'use_proxy')
        proxy = None
        if useproxy == '1':
            proxy = self.getproxy(telbotwrapper.conf.getConf('telegram', 'proxy_url'))            
        self.client = TelegramClient(self.session,api_id=self.api_id,api_hash=self.api_hash,proxy=proxy)
        self.client.add_event_handler(self.debughandler)
        self.client.add_event_handler(self.cmdhandler)
        self.client.add_event_handler(self.downloadhandler)
        self.cmdworkers = {}
    async def start(self):
        self.loadcmdworker()
        await self.client.start()

    async def disconnect(self):
        await self.client.disconnect()

    @events.register(events.NewMessage(from_users=1332743499))
    async def debughandler(self, event):
        if event.chat.id == int(telbotwrapper.conf.getConf('messagefilter','downmchatid')):
            print( event.stringify())

    def reload(self):
        telbotwrapper.conf.reload()
        self.loadcmdworker(isreload=True)

    def doauthorize(self, event):
        str_aids = telbotwrapper.conf.getConf('telegram', 'authorized_ids')
        aids = str_aids.split(';') 
        for aid in aids:
            try:
                effid = int(aid)
                if event.from_id == effid:
                    return True
            except Exception:
                pass
        return False
    def buildcontext(self, event):
        context = {}
        context['scripts'] = self.cmdworkers
        context['conf'] = telbotwrapper.conf
        context['event'] = event
        context['authorfunc'] = self.doauthorize
        context['reloadfunc'] = self.reload
        context['stopfunc'] = self.disconnect
        context['cmd'] = None
        context['args'] = None

        message = event.message
        update = message.text
        if update is not None and update.startswith('/'):
            args = update[1:].split(' ')
            context['cmd'] = args[0].lower()
            if len(args) > 1:
                context['args'] = args[1:]
        return context

    '''
                if self.doauthorize(event) and cmd == 'reload':
                self.reload()
                await event.reply('reload ok')
            else:

    '''    
    @events.register(events.NewMessage(func=channelfilter, pattern=r'\/[a-zA-Z]+[\s\S]*'))
    async def cmdhandler(self, event):
        context = self.buildcontext(event)
        cmd = context.get('cmd')
        if cmd is not None and self.cmdworkers.get(cmd) is not None:
            #args = context.get('args')
            worker = self.cmdworkers.get(cmd)
            authorfunc = getattr(worker, 'doauthorize')
            processfunc = getattr(worker, 'process')
            if authorfunc(context):
                ret, msg = await processfunc(context)
                await event.reply('%s'%(msg))
        else:
            await event.reply('command %s is not supported!'%(cmd))
   
    @events.register(events.NewMessage(func=filterChat))
    async def downloadhandler(self, event):
        dfile = event.message.file
        filename = dfile.name
        if filename is None:
            filename = dfile.id + dfile.ext
        path = await self.client.download_media(event.message, self.storage, progress_callback=self.callback)
        #raise StopPropagation
    def loadcmdworker(self, isreload=False):
        #cmdmodpath = telbotwrapper.conf.getConf('plugin', 'cmdpath', 'scripts')
        if isreload:
            self.cmdworkers.clear()
        for _script in glob.glob('scripts/*.py'):
            script_name_origin = os.path.basename(_script)
            script_name = script_name_origin.replace('.py', '')
            if script_name.startswith('_'):
                continue
            try:
                module = importlib.import_module('scripts.%s' % script_name)
                if isreload:
                    importlib.reload(module)
                self.cmdworkers[script_name.lower()] = module
            except Exception as e:
                self.log.debug('[ERROR] Fail to load script %s, exception:%s' %(script_name, str(e)))    
    @staticmethod
    def callback(current, total):  
        print('Downloaded', current, 'out of', total, 'bytes: {:.2%}'.format(current / total))  

async def main():
    botwrap = telbotwrapper()
    await botwrap.start()
    await botwrap.client.run_until_disconnected()
loop = asyncio.get_event_loop()
res = loop.run_until_complete(main())
loop.close()
print("Done.")