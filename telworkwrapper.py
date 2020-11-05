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
from telethon import Button
from lib.common import Conf
from lib.common import mylogging

DEFAULT_CMD_PREFIX = '/'
CMD_PREFIX = ':'
def filterChat(e):
    targetchat = int(telbotwrapper.conf.getConf('messagefilter','downmchatid'))
    if e.chat is not None and e.chat.id == targetchat:
        return True
    '''
    if abs(e.chat_id) == targetchat:
        return True
    '''
    return False

def channelfilter(e):
    targetchat = int(telbotwrapper.conf.getConf('messagefilter','botchatid'))
    if e.chat is not None and e.chat.id == targetchat:
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
        self.bottoken = telbotwrapper.conf.getConf('telegram', 'bottoken')
        self.role = telbotwrapper.conf.getConf('server', 'role')
        self.instanceid = telbotwrapper.conf.getConf('server', 'instanceid')
        useproxy = telbotwrapper.conf.getConf('telegram', 'use_proxy')
        proxy = None
        if useproxy == '1':
            proxy = self.getproxy(telbotwrapper.conf.getConf('telegram', 'proxy_url'))            
        #self.client = TelegramClient(self.session,api_id=self.api_id,api_hash=self.api_hash,proxy=proxy)
        self.client = TelegramClient(self.session,api_id=self.api_id,api_hash=self.api_hash,proxy=proxy)
        if self.role == 'primary':
            self.client.add_event_handler(self.cmdhandler)
            self.client.add_event_handler(self.downloadhandler)
            self.client.add_event_handler(self.callbackhandler)
            self.client.add_event_handler(self.innercmdhandler)
        else:
            self.client.add_event_handler(self.debughandler)
        self.cmdworkers = {}

    async def start(self):
        self.loadcmdworker()
        await self.client.start(bot_token=self.bottoken)

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
                if event.from_id == effid or event.sender_id == effid:
                    return True
            except Exception:
                pass
        return False
    def buildcontext(self, event, content, callbackquery=False):
        context = {}
        context['scripts'] = self.cmdworkers
        context['conf'] = telbotwrapper.conf
        context['event'] = event
        context['authorfunc'] = self.doauthorize
        context['reloadfunc'] = self.reload
        context['stopfunc'] = self.disconnect
        context['cmd'] = None
        context['args'] = None
        update = ''
        if callbackquery:
            update = content.decode()
        else:
            update = content
        if update is not None and update.startswith(CMD_PREFIX): 
            args = update[1:].split(' ')
            context['cmd'] = args[0].lower()
            if len(args) > 1:
                context['args'] = args[1:]
        return context
        
    async def proceed(self, context):
        cmd = context.get('cmd')
        event = context.get('event')
        if cmd is not None and self.cmdworkers.get(cmd) is not None:
            worker = self.cmdworkers.get(cmd)
            authorfunc = getattr(worker, 'doauthorize')
            processfunc = getattr(worker, 'process')
            if authorfunc(context):
                replyctx = await processfunc(context)
                msg = replyctx.get('msg')
                parse_mod = replyctx.get('parse_mod')
                retexec = replyctx.get('retexec')
                buttons = replyctx.get('buttons')
                if retexec == 0:
                    await event.respond('%s'%(msg),parse_mode=parse_mod, buttons = buttons)
                else:
                    await event.reply('command %s execute fail(%d): %s'%(cmd, retexec, msg),parse_mode=parse_mod)
        else:
            await event.reply('command %s is not supported!'%(cmd))

    @events.register(events.NewMessage(pattern=r'#[a-zA-Z]+[\s\S]*'))
    async def innercmdhandler(self, event):
        print(event.message.text)
        rtext = event.message.text
        if rtext.find(CMD_PREFIX) > 0:
            target = rtext[1:rtext.find(CMD_PREFIX)].strip()
            cmdmsg = rtext[rtext.find(CMD_PREFIX):]
            if target == self.instanceid:
                context = self.buildcontext(event, cmdmsg)
                await self.proceed(context)

    @events.register(events.CallbackQuery)
    async def callbackhandler(self, event):
        context = self.buildcontext(event, event.data, callbackquery=True)
        await self.proceed(context)
           
    @events.register(events.NewMessage(func=channelfilter, pattern=r':[a-zA-Z]+[\s\S]*'))
    async def cmdhandler(self, event):
        context = self.buildcontext(event, event.message.text)
        await self.proceed(context)
   
    @events.register(events.NewMessage(func=filterChat))
    async def downloadhandler(self, event):
        dfile = event.message.file
        if dfile is not None:
            filename = dfile.name
            if filename is None:
                filename = dfile.id + dfile.ext
            path = await self.client.download_media(event.message, self.storage, progress_callback=self.callback) 
            self.log.debug('%s download to %s'%(filename, path))
            raise StopPropagation
    
    
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