#This file just reads and applies ryzen configuaration info from .config
import os
import signal
import sys
import gi
import subprocess
import configparser

from os.path import expanduser

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

user_name = subprocess.getoutput("logname")
user = subprocess.getoutput("echo ~"+user_name)
config_file = user+'/.config/slimbookamdcontroller/slimbookamdcontroller.conf'
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
parameters = config.get('CONFIGURATION', 'cpu-parameters').split('-')
print("Parameters: "+str(parameters))

if modo_actual == "low":

    print('Setting '+modo_actual+' to : '+parameters[0]+' '+parameters[1]+' '+parameters[2]+'.\n')

    call = os.system('sudo /usr/share/slimbookamdcontroller/ryzenadj --tctl-temp=95'+' --slow-limit='+parameters[0]+' --stapm-limit='+parameters[1]+' --fast-limit='+parameters[2]+'')
    
if modo_actual == "medium":

    print('Setting '+modo_actual+' to : '+parameters[3]+' '+parameters[4]+' '+parameters[5]+'.\n')

    call = os.system('sudo /usr/share/slimbookamdcontroller/ryzenadj --tctl-temp=95'+' --slow-limit='+parameters[3]+' --stapm-limit='+parameters[4]+' --fast-limit='+parameters[5]+'')

if modo_actual == "high":

    print('Setting '+modo_actual+' to : '+parameters[6]+' '+parameters[7]+' '+parameters[8]+'.\n')

    call = os.system('sudo /usr/share/slimbookamdcontroller/ryzenadj --tctl-temp=95'+' --slow-limit='+parameters[6]+' --stapm-limit='+parameters[7]+' --fast-limit='+parameters[8]+'')

print('--------------------------------------------')
print('Exit: '+str(call))
print('--------------------------------------------')



        