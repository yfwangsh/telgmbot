from telethon import TelegramClient,sync
import socks #如果你不需要通过代理连接Telegram，可以删掉这一行
from telethon.tl.types import InputMessagesFilterPhotos
from telethon.tl.types import InputMessagesFilterVideo
import asyncio
from telethon import events
from lib.common import Conf
from lib.common import mylogging

globalconf = Conf('conf/telbot.conf', type='raw')

def filterChat(e):
    if e.chat.id == int(globalconf.getConf('messagefilter','downmchatid')):
        return True
    return False

class telbotwrapper():
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
        self.conf = Conf('conf/telbot.conf', type='raw')
        self.log = mylogging(self.conf).getLogger()
        self.api_hash = self.conf.getConf('telegram', 'api_hash')
        self.api_id = self.conf.getConf('telegram', 'api_id')
        self.session = self.conf.getConf('telegram', 'session')
        self.storage = self.conf.getConf('local', 'storage_path')
        useproxy = self.conf.getConf('telegram', 'use_proxy')

        proxy = None
        if useproxy == '1':
            proxy = self.getproxy(self.conf.getConf('telegram', 'proxy_url'))            
        self.client = TelegramClient(self.session,api_id=self.api_id,api_hash=self.api_hash,proxy=proxy)
        self.client.add_event_handler(self.downloadhandler)
    async def start(self):
        await self.client.start()


    @events.register(events.NewMessage(func=filterChat))
    async def downloadhandler(self, event):
        dfile = event.message.file
        filename = dfile.name
        if filename is None:
            filename = dfile.id + dfile.ext
        path = await self.client.download_media(event.message, self.storage, progress_callback=self.callback)

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