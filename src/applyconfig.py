#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#This file just reads and applies ryzen configuaration info from .config
import os
import sys
import subprocess
import configparser
import utils
import json
from pathlib import Path
from time import sleep

CONFIG_FILE = None

if (len(sys.argv)<2):
    status,value = subprocess.getstatusoutput("loginctl list-sessions -o json")
    sessions = json.loads(value)
    
    for session in sessions:
        state = session["state"]
        
        if state == "active":
            user = session["user"]
            gstatus,gvalue = subprocess.getstatusoutput("getent passwd {0}".format(user))
            tmp = gvalue.split(":")
            CONFIG_FILE = tmp[5] + "/.config/slimbookamdcontroller/slimbookamdcontroller.conf"
            break
else:
    CONFIG_FILE = sys.argv[1]

if (not CONFIG_FILE or not Path(CONFIG_FILE).exists()):
    print("Config file does not exists",file=sys.stderr)
    sys.exit(0)

print("Reading " + CONFIG_FILE, file=sys.stderr)
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

modes = {"low":0, "medium":1, "high":2}

mode = config.get('CONFIGURATION', 'mode')
parameters = config.get('USER-CPU', 'cpu-parameters').split('/')

mode = modes[mode]

set_parameters = parameters[mode].split('-')
child = subprocess.Popen([
    "/usr/bin/ryzenadj",
    "--tctl-temp=95",
    "--slow-limit=" + set_parameters[0],
    "--stapm-limit=" + set_parameters[1],
    "--fast-limit=" + set_parameters[2]
    ])

child.wait()


