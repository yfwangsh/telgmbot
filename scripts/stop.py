s_version='1.0'
s_type=0

def help():
    return '/stop : stop auto bot'

def doauthorize(context):
    authfunc = context.get('authorfunc')
    event = context.get('event')
    return authfunc(event)

async def process(context):
    stopfunc = context.get('stopfunc')
    await stopfunc()
    return 0, 'stopped'