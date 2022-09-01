#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
from configparser import ConfigParser
from os import path as path

APP = 'SlimbookAmdController'
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
VERSION_FILE = ConfigParser()
VERSION_FILE.read(path.join(CURRENT_PATH, '..', '{}.desktop'.format(APP.casefold())))
VERSION = VERSION_FILE.get('Desktop Entry', 'Version') if VERSION_FILE.has_option('Desktop Entry', 'Version') else None
BUILD_PATH = path.join(CURRENT_PATH, '..', '..', '..', '{}_{}'.format(
    APP, VERSION)) if VERSION else None


if path.exists(BUILD_PATH):
    shutil.rmtree(BUILD_PATH)

print(path.exists(BUILD_PATH), BUILD_PATH)

CHILD_BUILD_PATH = path.join(BUILD_PATH, '{}-{}'.format(
    APP, VERSION).casefold()) if VERSION else None

shutil.copytree(path.join(CURRENT_PATH, '..'), CHILD_BUILD_PATH)

print(path.exists(CHILD_BUILD_PATH), CHILD_BUILD_PATH)

os.chdir(CHILD_BUILD_PATH)

p = subprocess.Popen('dh_make --createorig -C p -y', shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
print(p.wait())
p = subprocess.Popen('debuild -D', shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
print(p.wait())
os.system('xdg-open "%s"' % BUILD_PATH)
exit(0)
