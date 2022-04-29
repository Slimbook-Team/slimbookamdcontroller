#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file checks if any new configuration has been added an then, adds it to old configuration file
# in order to keep old custom values.
# It also gives permisions to config directory

import os, pwd
import sys, logging
import subprocess
import configparser

APPNAME = 'slimbookamdcontroller'

USERNAME = subprocess.getstatusoutput("logname")
# print(str(USERNAME))

# 1. Try getting logged username  2. This user is not root  3. Check user exists (no 'reboot' user exists)
if USERNAME[0] == 0 and USERNAME[1] != 'root' and subprocess.getstatusoutput('getent passwd '+USERNAME[1])[0] == 0:
    print('Getting logname successfull')
    USER_NAME = USERNAME[1]
else:
    print('Getting logname ...')
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')
print('Config check executed as '+USER_NAME)

HOMEDIR = subprocess.getoutput("echo ~"+USER_NAME)

CURRPATH = os.path.dirname(os.path.realpath(__file__))

uid, gid = pwd.getpwnam(USER_NAME).pw_uid, pwd.getpwnam(USER_NAME).pw_gid

# There will always be a folder in src called configuration, where default configuration is stored.
# There will also be a route in
DEFAULT_CONF = CURRPATH+'/'+APPNAME+'.conf'
CONFIG_FILE = HOMEDIR+'/.config/'+APPNAME+'/'+APPNAME+'.conf'
CONFIG_FOLDER = HOMEDIR+'/.config/'+APPNAME
logger = logging.getLogger()

def main(args):

    check1()

    if subprocess.getoutput('whoami') == 'root':
        print('Giving permisions to config directory...')
        os.system('sudo chmod 777 -R '+HOMEDIR+'/.config/'+APPNAME)
        
    set_ownership(CONFIG_FOLDER)

def set_ownership(folder):
    folder_stat = os.stat(folder)
    f_uid = folder_stat.st_uid
    f_gid = folder_stat.st_gid
    logger.debug("Folder {}\nUser uid={}\nFolder uid={}".format(folder, uid, f_gid))

    if not uid == f_uid or not gid == f_gid:
        #logger.info('Setting {} ownership').format(folder)

        for dir_path, dir_name, filenames in os.walk(folder):
            logger.debug(dir_path)
            os.chown(dir_path, uid, gid)
            for filename in filenames:
                file_path = os.path.join(dir_path, filename)
                logger.debug(file_path)
                os.chown(file_path, uid, gid)

def check1():
    if os.path.isfile(CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        vars = subprocess.getoutput('cat '+DEFAULT_CONF).split('\n')
        # print(str(vars))
        incidences = False

        section = ''
        for var in vars:
            PROCS = {'U','H','HS','HX','G'}
            if var.find('=') != -1:
                # We get the line, then the variable name, then we remove spaces at the start or the end
                value = var.split('=')[1].strip()
                var = var.split('=')[0].strip()
                try:
                    config[section][var]
                    if var in PROCS :
                        # if new value different setting defaults 

                        oldvalue = config.get(section, var)
                        if oldvalue != value:
                            incidences = True
                            print('Updating default values and '+var)
                            config.set('USER-CPU', 'cpu-parameters', '')
                            config.set('PROCESSORS', var, value)

                except:
                    incidences = True
                    print('Not found: '+var)
                    try:
                        config.set(section, var, value)
                    except:
                        config.add_section(section)
                        print('Section added')
                        config.set(section, var, value)

            else:
                if var.startswith('[') and var.endswith(']'):
                    section = var[1:len(var)-1]
                    print('Checking section: '+section+'...')

        if incidences:
            try:
                configfile = open(CONFIG_FILE, 'w')
                config.write(configfile)
                configfile.close()
                print('Incidences corrected.')
            except:
                print('Incidences could not be corrected.')
        else:
            print('Incidences not found.')
    else:
        print('Creating config file ...')
        os.system('mkdir -p '+HOMEDIR+'/.config/'+APPNAME +
                  '/ && cp '+DEFAULT_CONF+' '+CONFIG_FILE)

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    #formatter = logging.Formatter('%(asctime)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

main(sys.argv)
