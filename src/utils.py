import getpass
import gettext
import os
import subprocess
import locale


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