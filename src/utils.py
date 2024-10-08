import getpass
import gettext
import os
import subprocess
import locale

from pathlib import Path

CONFIG_FILE = str(Path.home()) + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf'

DB_FILE = 'processors.db'

def get_user(from_file=None):
    try:
        user_name = getpass.getuser()
    except Exception:
        user_name = os.getlogin()

    if from_file and os.path.exists(from_file):
        exit_code, candidate = subprocess.getstatusoutput('cat {} | tail -n 1 | cut -f 2 -d "@"'.format(from_file))
        if exit_code != 0:
            user_name = candidate

    if user_name == 'root':
        if 'SUDO_USER' in os.environ and os.environ['SUDO_USER'] != 'root':
            user_name = os.environ['SUDO_USER']
        else:
            user_name = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

    return user_name


def get_languages():
    languages = ['en']
    try:
        user_environ = locale.getlocale()[0]
        for lang in ["en", "es", "it", "fr"]:
            if user_environ.find(lang) >= 0:
                languages = [lang]
                break
    except Exception:
        pass
    return languages


def load_translation(filename):
    current_path = os.path.dirname(os.path.realpath(__file__))
    languages = get_languages()
    return gettext.translation(
        filename,
        os.path.join(current_path, 'translations'),
        languages=languages,
        fallback=True
    ).gettext

def get_cpu_info(var='info'):
    info = ()
    if var == 'name':
        return subprocess.getoutput('cat /proc/cpuinfo | grep name | uniq').split(':')[1].strip()
    if var == 'cores':
        return subprocess.getoutput('nproc')
    if var == 'threadspercore':
        cores = subprocess.getoutput('cat /proc/cpuinfo | grep "cpu cores" | uniq').split(':')[1].strip()
        return cores
    if var == 'info':
        print('Information get_cpu_info().\nOptions: \n\tname\n\tcores\n\tthreadspercore')

def get_secureboot_status():

    if (not Path("/sys/firmware/efi").exists()):
        return False
        
    SB_VAR = "/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c"
    
    if (not Path(SB_VAR).exists()):
        return False
    
    sb = False
    f = open(SB_VAR,"rb")
    var = list(f.read())
    if (var[4] == 1):
        sb = True
    f.close()
    
    return sb

def get_run_dir():
    return "/run/user/{0}".format(os.getuid())
    
def is_pid_alive(pid):
    try:
        os.kill(pid,0)
        return True
    except:
        return False

def get_pid_from_file(name):
    run = get_run_dir()
    filename = Path(run + "/" + name)
    
    if (filename.exists()):
        f=open(str(filename),"r")
        data=f.readlines()
        f.close()
        if (len(data)>0):
            return int(data[0])
        else:
            return 0
    else:
        return 0
    
def create_pid_file(name):
    
    filename = get_run_dir() + "/" + name
    f=open(filename,"w")
    f.write("{0}".format(os.getpid()))
    f.close()
    
    return True

def destroy_pid_file(name):
    filename = get_run_dir() + "/" + name
    
    if (Path(filename).exists()):
        os.remove(filename)

def application_lock(name):
    pid = get_pid_from_file(name)

    if (pid>0):
        if (is_pid_alive(pid)):
            print("process is already running",file=sys.stderr)
            sys.exit(1)
        
    create_pid_file(name)
    
def application_release(name):
    destroy_pid_file(name)

