#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import gettext
import signal
import subprocess
import os
import gi
import configparser
import gettext, locale
import sys

gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from configparser import ConfigParser
from os.path import expanduser


srcpath = '/usr/share/slimbookamdcontroller/src'
sys.path.insert(1, srcpath)

#from Tkinter import*

currpath = os.path.dirname(os.path.realpath(__file__))

#Variables
USERNAME = subprocess.getstatusoutput("logname")

# 1. Try getting logged username  2. This user is not root  3. Check user exists (no 'reboot' user exists) 
if USERNAME[0] == 0 and USERNAME[1] != 'root' and subprocess.getstatusoutput('getent passwd '+USERNAME[1])[0] == 0:
    USER_NAME = USERNAME[1]
else:
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = subprocess.getoutput("echo ~"+USER_NAME)

directorio = '~/.config/slimbookamdcontroller'
fichero = HOMEDIR + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf'
iconapp = currpath+'/amd.png'

entorno_usu = locale.getlocale()[0]

if entorno_usu.find("en") >= 0 or entorno_usu.find("es") >= 0 or entorno_usu.find("fr") >= 0:
	idiomas = [entorno_usu]
else: 
    idiomas = ['en_EN'] 

#idiomas = ['fr_FR']

# Configurar el acceso al catálogo de mensajes
t = gettext.translation('slimbookamdcontrollerindicator', 
                        currpath+'/locale', 
                        languages=idiomas,
                        fallback=True,)
_ = t.gettext

#Menu
class Indicator():
	modo_actual="none"
	parameters=('','','')
	icono_actual = iconapp

	def __init__(self):
		self.app = 'show_proc'
		iconpath = currpath+'/amd.png'
		# after you defined the initial indicator, you can alter the icon!
		self.testindicator = AppIndicator3.Indicator.new(
			self.app, iconpath, AppIndicator3.IndicatorCategory.OTHER)
		self.testindicator.set_icon_theme_path(os.path.join(currpath, 'images'))
		self.testindicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
		self.testindicator.set_menu(self.create_menu())
		self.inicio()

	def create_menu(self):
		menu = Gtk.Menu()
	
		icon_bajo = Gtk.Image()
		icon_bajo.set_from_file(currpath+'/images/amd-1.png')

		icon_medio = Gtk.Image()
		icon_medio.set_from_file(currpath+'/images/amd-2.png')

		icon_alto = Gtk.Image()
		icon_alto.set_from_file(currpath+'/images/amd-3.png')


		item_bajo = Gtk.ImageMenuItem(label=_('Low performance'), image = icon_bajo)
		item_bajo.connect('activate', self.bajorendimiento)
		item_bajo.set_always_show_image(True)

		item_medio = Gtk.ImageMenuItem(label=_('Medium performance'), image=icon_medio)
		item_medio.connect('activate', self.mediorendimiento)

		item_medio.set_always_show_image(True)

		item_alto = Gtk.ImageMenuItem(label=_('High performance'), image= icon_alto)
		item_alto.connect('activate', self.altorendimiento)
		item_alto.set_always_show_image(True)

		item_ventana = Gtk.MenuItem(label=_('Preferences'))
		item_ventana.connect('activate', self.openWindow)

		item_separador = Gtk.SeparatorMenuItem()

		item_quit = Gtk.MenuItem(label=_('Exit'))
		item_quit.connect('activate', self.exit)

		
		menu.append(item_bajo)
		menu.append(item_medio)
		menu.append(item_alto)
		menu.append(item_separador)
		menu.append(item_ventana)
		menu.append(item_quit)
		menu.show_all()

		return menu

	def exit(self, source):
		Gtk.main_quit()

	def openWindow(self, source):
		os.system("slimbookamdcontroller")

	def inicio(self):
		config = configparser.ConfigParser()
		config.read(fichero)

		print('Loading data from .conf:\n')

		#Mostramos indicador, o no :):
		if config.get('CONFIGURATION', 'show-icon') == 'on':
			self.testindicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
			print('- Autostart enabled')
		else:
			self.testindicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
			print('- Autostart disabled')


		#Cargamos los parametros de la CPU
		params = config.get('USER-CPU', 'cpu-parameters').split('/')
		self.parameters = params
		
		print('- CPU Parameters: {}'.format(str(self.parameters)))


		if config.get('CONFIGURATION', 'mode') == "low":
			print('- Low\n')
			self.bajorendimiento('x')
		else:
			if config.get('CONFIGURATION', 'mode') == "medium":
				print('- Medium\n')
				self.mediorendimiento('x')
			else:
				print('- High\n')
				self.altorendimiento('x')
		
		print("\nData loaded from .conf\n")

	def update_config_file(self, variable, value):
		
		fichero = HOMEDIR + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf'

		config = configparser.ConfigParser()
		config.read(fichero)

        # We change our variable: config.set(section, variable, value)
		config.set('CONFIGURATION', str(variable), str(value))

        # Writing our configuration file 
		with open(fichero, 'w') as configfile:
				config.write(configfile)

		print("Variable |"+variable+"| updated, actual value: "+value+"\n")

	#Funcion para configuracion de bajo rendimiento
	def bajorendimiento(self, widgets):
		self.modo_actual="low"
		self.icono_actual=currpath+'/images/amd-1.png'
		self.testindicator.set_icon(currpath+'/images/amd-1.png')
            
		self.update_config_file("mode", self.modo_actual)
		subprocess.Popen('python3 {}/applyconfig.py'.format(currpath), shell = True)

	#Funcion para configuracion de medio rendimiento
	def mediorendimiento(self, widget):
		self.modo_actual="medium"
		self.icono_actual=currpath+'/images/amd-2.png'
		self.testindicator.set_icon(currpath+'/images/amd-2.png')
		
		self.update_config_file("mode", self.modo_actual)
		subprocess.Popen('python3 {}/applyconfig.py'.format(currpath), shell = True)

	#Funcion para configuracion de alto rendimiento
	def altorendimiento(self, widget):
		self.modo_actual="high"
		self.icono_actual=currpath+'/images/amd-3.png'
		self.testindicator.set_icon(currpath+'/images/amd-3.png')

		self.update_config_file("mode", self.modo_actual)
		subprocess.Popen('python3 {}/applyconfig.py'.format(currpath), shell = True)

Indicator()

signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()