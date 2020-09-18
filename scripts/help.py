s_version='1.0'
s_type=1

def help():
    return 'usage /help [command]'

def doauthorize(context):
    return True

async def process(context):
    cmdworkers = context.get('scripts')
    args = context.get('args')
    if args is None:
        helpkeys = cmdworkers.keys()
        msg = 'all supported commands: \n' + '\n'.join(helpkeys)
        return 0, msg 
    if len(args) > 0 and cmdworkers is not None:
        worker = cmdworkers.get(args[0])
        if worker is not None:
            helpfunc = getattr(worker, 'help')
            return 0, helpfunc()