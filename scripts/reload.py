s_version='1.0'
s_type=0

def help():
    return '/reload : reload configuration and script modules'

def doauthorize(context):
    authfunc = context.get('authorfunc')
    event = context.get('event')
    return authfunc(event)

async def process(context):
    reloadfunc = context.get('reloadfunc')
    reloadfunc()
    return 0, 'reload ok'