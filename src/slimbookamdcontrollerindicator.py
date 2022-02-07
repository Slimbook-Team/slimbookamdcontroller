#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import signal
import subprocess
import os
import gi
import sys

gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import AyatanaAppIndicator3 as AppIndicator3
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from configparser import ConfigParser

# We want load first current location
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
if CURRENT_PATH not in sys.path:
    sys.path = [CURRENT_PATH] + sys.path
import utils

srcpath = '/usr/share/slimbookamdcontroller/src'
sys.path.insert(1, srcpath)

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

#Variables

USER_NAME = utils.get_user()

HOMEDIR = subprocess.getoutput("echo ~"+USER_NAME)

_ = utils.load_translation('slimbookamdcontrollerindicator')

CONFIG_FILE = HOMEDIR + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf'
ICON_FILE = CURRENT_PATH+'/amd.png'
config = ConfigParser()

#Menu
class Indicator():
	modo_actual="none"
	parameters=('','','')
	icono_actual = ICON_FILE

	def __init__(self):
		self.app = 'show_proc'
		iconpath = CURRENT_PATH+'/amd.png'
		# after you defined the initial indicator, you can alter the icon!
		self.testindicator = AppIndicator3.Indicator.new(
			self.app, iconpath, AppIndicator3.IndicatorCategory.OTHER)
		self.testindicator.set_icon_theme_path(os.path.join(CURRENT_PATH, 'images'))
		self.testindicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
		self.testindicator.set_menu(self.create_menu())
		self.inicio()

	def create_menu(self):
		menu = Gtk.Menu()
	
		icon_bajo = Gtk.Image()
		icon_bajo.set_from_file(CURRENT_PATH+'/images/amd-1.png')

		icon_medio = Gtk.Image()
		icon_medio.set_from_file(CURRENT_PATH+'/images/amd-2.png')

		icon_alto = Gtk.Image()
		icon_alto.set_from_file(CURRENT_PATH+'/images/amd-3.png')


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
		subprocess.Popen('slimbookamdcontroller', shell = True)

	def inicio(self):
		config = ConfigParser()
		config.read(CONFIG_FILE)

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
		
		config.read(CONFIG_FILE)

        # We change our variable: config.set(section, variable, value)
		config.set('CONFIGURATION', str(variable), str(value))

		with open(CONFIG_FILE, 'w') as configfile:
				config.write(configfile)

		print("Updated "+variable+" --> "+value+"\n")

	#Funcion para configuracion de bajo rendimiento
	def bajorendimiento(self, widgets):
		self.modo_actual="low"
		self.icono_actual=CURRENT_PATH+'/images/amd-1.png'
		self.testindicator.set_icon(CURRENT_PATH+'/images/amd-1.png')
            
		self.update_config_file("mode", self.modo_actual)
		subprocess.Popen('pkexec slimbookamdcontroller-pkexec', shell=True)

	#Funcion para configuracion de medio rendimiento
	def mediorendimiento(self, widget):
		self.modo_actual="medium"
		self.icono_actual=CURRENT_PATH+'/images/amd-2.png'
		self.testindicator.set_icon(CURRENT_PATH+'/images/amd-2.png')
		
		self.update_config_file("mode", self.modo_actual)
		subprocess.Popen('pkexec slimbookamdcontroller-pkexec', shell=True)

	#Funcion para configuracion de alto rendimiento
	def altorendimiento(self, widget):
		self.modo_actual="high"
		self.icono_actual=CURRENT_PATH+'/images/amd-3.png'
		self.testindicator.set_icon(CURRENT_PATH+'/images/amd-3.png')

		self.update_config_file("mode", self.modo_actual)
		subprocess.Popen('pkexec slimbookamdcontroller-pkexec', shell=True)


call = subprocess.getstatusoutput('mokutil --sb-state | grep -i "SecureBoot disabled"')

if not call[0] == 0:
	print('Disable Secureboot, please.')


Indicator()

signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()