from configparser import ConfigParser
from configparser import RawConfigParser
from configparser import NoOptionError
from configparser import NoSectionError
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import os
import re
import inspect  
import threading
import logging
from logging import handlers

class handler():
    def __init__(self, conf=None, bot=None):
        self.version='1.0'
        self.weight = -1
        self.name = 'default'
        self.registered = True
        self.log = mylogging(conf).getLogger()
        self.myhandler = MessageHandler(Filters.command, self.worker)
        self.conf = conf
        self.needauth = False
        self.bot = None
    def worker(self, update, context):
        if self.doauthorized(update):
            self.proceed(update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, need authorized before process that command")

    def proceed(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

    def register(self, dispatcher, bot):
        if self.registered:
            dispatcher.add_handler(self.myhandler)
        else:
            self.log.debug("%s handler is not enabled"%(self.name,))
        self.bot = bot
    def unregister(self, dispatcher):
        if self.registered:
            dispatcher.remove_handler(self.myhandler)
    
    def doauthorized(self, update):
        if self.needauth:
            str_aids = self.conf.getConf('telegram', 'authorized_ids')
            aids = str_aids.split(';') 
            for aid in aids:
                try:
                    effid = int(aid)
                    if update.effective_user.id == effid:
                        return True
                except Exception:
                    pass
        else:
            return True
        return False

class mylogging():
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(mylogging, "_instance"):
            with mylogging._instance_lock:
                if not hasattr(mylogging, "_instance"):
                    mylogging._instance = object.__new__(cls)  
        return mylogging._instance

    def __init__(self, conf=None):
        logfile = 'logs/mylogging.log'
        if conf is not None:
            logfile = conf.getConf('log', 'logfile', logfile)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        rf_handler = handlers.TimedRotatingFileHandler(logfile, when='D', interval=1, backupCount=3)
        rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        rf_handler.setLevel(logging.INFO)
        logger.addHandler(rf_handler)
        self.log =  logger
    def getLogger(self):
        return self.log

class Conf:
    def getConf(self, section, key, default=None):
        value = default
        try:
            value = self.config.get(section, key)
        except NoSectionError:
            pass 
        except NoOptionError:
            pass        
        return value
    def getOptions(self, section):
        return self.config.items(section)
    @staticmethod
    def initConf(file, type=None):
        cp = None
        if type == 'raw':
            cp = RawConfigParser()
        else:
            cp = ConfigParser()
        cp.read(file)
        return cp
    def __init__(self, filename, type=None): 
        self.file = filename
        self.type = type
        self.config = Conf.initConf(filename, type)
    def reload(self):
        self.config = Conf.initConf(self.file, self.type)

class paramChecker:
    '''
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(paramChecker, "_instance"):
            with paramChecker._instance_lock:
                if not hasattr(paramChecker, "_instance"):
                    paramChecker._instance = object.__new__(cls)  
        return paramChecker._instance
    '''
    @staticmethod
    def cmdefileparacheck(value, option=None):
        ret = os.path.exists(value)
        if ret and option is not None and option.get('allowPath') is not None:
            ret = paramChecker.checkallowPath(value, option.get('allowPath'))            
        return ret
    @staticmethod
    def cmdnumbercheck(value, option=None):
        try:
            float(value)
        except ValueError:
            return False
        return True
    
    @staticmethod
    def cmdfilevalcheck(value, option=None):
        ret = False
        try:
            with open(value, 'x') as f:
                pass
            os.remove(value)
            ret = True
        except FileExistsError as err:
            ret = True
        except OSError as err:
            pass
        except Exception as err:
            print(type(err))
            print(err)
        if ret and option is not None and option.get('allowPath') is not None:
            ret = paramChecker.checkallowPath(value, option.get('allowPath'))            
        return ret
    @staticmethod
    def checkparamflag(value, option=None):
        pattern = '^(-{1,2}[a-zA-Z]+)$'
        regex = re.compile(pattern)
        if regex.match(value) is not None:
            return True
        return False
    @staticmethod
    def checkword(value, option=None):
        pattern = r'^([-|\w.]*)$'
        regex = re.compile(pattern)
        if regex.match(value) is not None:
            return True
        return False
    @staticmethod
    def checkallowPath(value, allowpath):
        realpath = os.path.realpath(value).lower()
        allowp = os.path.realpath(allowpath).lower()
        return realpath.startswith(allowp)

    @staticmethod
    def check(value, type, option=None):
        if type == 'EFILE':
            return paramChecker.cmdefileparacheck(value, option)
        elif type == 'NUMBER':
            return paramChecker.cmdnumbercheck(value, option)
        elif type == 'PMSIGN':
            return paramChecker.checkparamflag(value, option)
        elif type == 'FILE':
            return paramChecker.cmdfilevalcheck(value, option)
        elif type =='WORD':
            return paramChecker.checkword(value, option)
        return False
