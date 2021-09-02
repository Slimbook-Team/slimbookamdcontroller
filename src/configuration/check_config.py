#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file checks if any new configuration has been added an then, adds it to old configuration file
# in order to keep old custom values.
# It also gives permisions to config directory

import os
import sys
import subprocess
import configparser

APPNAME = 'slimbookamdcontroller'

USERNAME = subprocess.getstatusoutput("logname")

# 1. Try getting logged username  2. This user is not root  3. Check user exists (no 'reboot' user exists) 
if USERNAME[0] == 0 and USERNAME[1] != 'root' and subprocess.getstatusoutput('getent passwd '+USERNAME[1]) == 0:
    USER_NAME = USERNAME[1]
else:
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = subprocess.getoutput("echo ~"+USER_NAME)

CURRPATH = os.path.dirname(os.path.realpath(__file__))

# There will always be a folder in src called configuration, where default configuration is stored.
# There will also be a route in 
default = CURRPATH+'/'+APPNAME+'.conf'
config_file = HOMEDIR+'/.config/'+APPNAME+'/'+APPNAME+'.conf'

print('Config check executed as '+USERNAME[1])

def main(args):
  
    check1()

    if subprocess.getoutput('whoami') == 'root':
        print('Giving permisions to config directory...')
        os.system('sudo chmod 777 -R '+HOMEDIR+'/.config/'+APPNAME)
        
    print('Done')

def check1(): 
    if os.path.isfile(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        vars = subprocess.getoutput('cat '+default).split('\n')
        #print(str(vars))
        incidences = False

        section = ''
        for var in vars:
            
            if var.find('=') != -1:
                # We get the line, then the variable name, then we remove spaces at the start or the end
                value = var.split('=')[1].strip()
                var = var.split('=')[0].strip()
                try:
                    config[section][var]
                except:
                    incidences = True
                    print('Not found: '+var)
                    try:
                        config.set(section,var,value)
                    except:
                        config.add_section(section)
                        print('Section added')
                        config.set(section,var,value)
                    
            else:
                if var.startswith('[') and var.endswith(']'):                
                    section = var[1:len(var)-1]
                    print('Checking section: '+section+'...')
        
        if incidences:
            try:
                configfile = open(config_file, 'w')
                config.write(configfile)
                configfile.close()
                print('Incidences corrected.')
            except:
                print('Incidences could not be corrected.')
        else:
            print('Incidences not found.')
    else:
        print('Creating config file ...')
        os.system('mkdir -p '+HOMEDIR+'/.config/'+APPNAME+'/ && cp '+default+' '+config_file)


main(sys.argv)