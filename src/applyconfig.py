#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#This file just reads and applies ryzen configuaration info from .config
import os
import sys
import gi
import subprocess
import configparser
from time import sleep

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

USERNAME = subprocess.getstatusoutput("logname")

# 1. Try getting logged username  2. This user is not root  3. Check user exists (no 'reboot' user exists) 
if USERNAME[0] == 0 and USERNAME[1] != 'root' and subprocess.getstatusoutput('getent passwd '+USERNAME[1]) == 0:
    USER_NAME = USERNAME[1]
else:
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = subprocess.getoutput("echo ~"+USER_NAME)

config_file = HOMEDIR+'/.config/slimbookamdcontroller/slimbookamdcontroller.conf'
print("Reading "+config_file)
config = configparser.ConfigParser()


if config.read(config_file):
    print("File detected!\n")
else:
    print("File not detected!\n")

call=''      

#READING VARIABLES
modo_actual = config.get('CONFIGURATION', 'mode')
print("Current mode: "+modo_actual)
parameters = config.get('USER-CPU', 'cpu-parameters').split('/')
print("Parameters: "+str(parameters))

mode = -1

if modo_actual == "low":
    mode = 0    
    
if modo_actual == "medium":
    mode = 1

if modo_actual == "high":
    mode = 2

set_parameters = parameters[mode].split('-')
sleep(3)
print('Setting '+modo_actual+' to : '+set_parameters[0]+' '+set_parameters[1]+' '+set_parameters[2]+'.\n')
call = os.system('sudo /usr/share/slimbookamdcontroller/ryzenadj --tctl-temp=95'+' --slow-limit='+set_parameters[0]+' --stapm-limit='+set_parameters[1]+' --fast-limit='+set_parameters[2]+'')

print('--------------------------------------------')
print('Exit: '+str(call))
print('--------------------------------------------')

#print(str('sys.exit('+str(call)+')'))
if call != 0:
    (sys.exit(1))
       