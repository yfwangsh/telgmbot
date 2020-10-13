import subprocess
import glob
import os
s_version='1.0'
s_type=1

'''
        context['scripts'] = self.cmdworkers
        context['conf'] = telbotwrapper.conf
        context['event'] = event
        context['authorfunc'] = self.doauthorize
        context['reloadfunc'] = self.reload
        context['cmd'] = None
        context['args'] = None
'''
def help():
    cmdlist = []
    for _script in glob.glob('scripts/shell/*.sh'):
        script_name_origin = os.path.basename(_script)
        script_name = script_name_origin.replace('.sh', '')
        cmdlist.append(script_name)
    return 'exec support commands: \n'+'\n'.join(cmdlist)

def doauthorize(context):
    authfunc = context.get('authorfunc')
    event = context.get('event')
    return authfunc(event)

async def process(context):
    #event = context.get('event')
    args = context.get('args')
    if args is not None and len(args) > 0:
        cmdname = args[0]
        for _script in glob.glob('scripts/shell/*.sh'):
            #print(_script)
            #cmdstr = _script
            script_name_origin = os.path.basename(_script)
            script_name = script_name_origin.replace('.sh', '')
            if script_name == cmdname:
                pargs = [_script]
                    
                
                if len(args) > 1:
                    pargs.extend(args[1:])
                    #cmdstr = _script + ' ' + ' '.join(args[1:])
                #print(cmdstr)
                output = runcmd(pargs)
                msg = output[1]
                errmsg = output[2]
                try:
                    if type(msg) == bytes:
                        msg = msg.decode()
                        errmsg = errmsg.decode()
                except UnicodeDecodeError as e:
                    try:
                        if type(msg) == bytes:
                            msg = msg.decode('gb2312')
                            errmsg = errmsg.decode('gb2312')
                    except:
                        pass
                if output[0] != 0:
                    print(errmsg)
                return output[0], msg

def runcmd(cmds):
    # Popen call wrapper.return (code, stdout, stderr)
    child = subprocess.Popen(args=cmds, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = child.communicate()
    ret = child.wait()
    return (ret, out, err)

        
if __name__ == '__main__':
    cmdarglist = ['./script/shell/test/sh']
    _, out, _ = runcmd(cmdarglist)
    print(out)
    print('------------------------------------------------------')
    cmdarglist.extend(['a','b'])
    _, out, _ = runcmd(cmdarglist)
    print(out)
    