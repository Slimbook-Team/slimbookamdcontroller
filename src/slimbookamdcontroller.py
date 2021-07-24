#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import gi
import subprocess
import gettext, locale, time
import shutil
import configparser
import re #Busca patrones expresiones regulares
from pathlib import Path

from services.gpu_service import GpuService

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from configparser import ConfigParser
from gi.repository import Gdk, Gtk, GLib, GdkPixbuf, AppIndicator3
from os.path import expanduser

srcpath = '/usr/share/slimbookamdcontroller/src'
sys.path.insert(1, srcpath)

user_name = subprocess.getoutput("logname")
user = subprocess.getoutput("echo ~"+user_name)
currpath = os.path.dirname(os.path.realpath(__file__))
config_object = ConfigParser()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config_file = user+'/.config/slimbookamdcontroller/slimbookamdcontroller.conf'
LAUNCHER_DESKTOP = os.path.join(BASE_DIR, "slimbookamdcontroller-autostart.desktop")
AUTOSTART_DESKTOP = os.path.expanduser("~/.config/autostart/slimbookamdcontroller-autostart.desktop")

#IDIOMAS ----------------------------------------------------------------

# CMD(Genera .pot):  pygettext -d slimbookamdcontrollercopy slimbookamdcontrollercopy.py
# CMD(Genera .mo a partir de .po):  msgfmt -o slimbookamdcontrollercopy.po slimbookamdcontrollercopy.mo
try:
    entorno_usu = locale.getlocale()[0]
    if entorno_usu.find("en") >= 0 or entorno_usu.find("es") >= 0 or entorno_usu.find("fr") >= 0:
        idiomas = [entorno_usu]
    else: 
        idiomas = ['en_EN'] 
except:
    idiomas = ['en_EN'] 


print('Language: ', entorno_usu)
t = gettext.translation('slimbookamdcontroller',
						currpath+'/locale',
						languages=idiomas,
						fallback=True,) 
_ = t.gettext

iconpath = currpath+'/amd.png'

#Guardamos la salida del comando en una variable
cpu = subprocess.getoutput('cat /proc/cpuinfo | grep '+'name'+'| uniq')

#Que encuentre cuatro digitos juntos seguidos de 1 o 2 letras mayusculas
patron = re.compile('([0-9]{4,})([A-Z{1,2}])')
numeros = patron.search(cpu).group(1)
letras = patron.search(cpu).group(2)

switch1 = Gtk.Switch()
switch1.set_halign(Gtk.Align.END)
switch2 = Gtk.Switch()
switch2.set_halign(Gtk.Align.END)

rbutton1 = Gtk.RadioButton.new_with_label_from_widget(None, (_("Low")))
rbutton2 = Gtk.RadioButton.new_with_mnemonic_from_widget(rbutton1, (_("Medium")))
rbutton3 = Gtk.RadioButton.new_with_mnemonic_from_widget(rbutton1, (_("High")))


class SlimbookAMD(Gtk.ApplicationWindow):

    modo_actual = ""
    indicador_actual = ""
    autostart_actual = ""
    parameters=('','','')
    
    
    def __init__(self):
        
    #VENTANA
        Gtk.Window.__init__(self, title ="Slimbook AMD Controller")    
        
        if str(Path(__file__).parent.absolute()).startswith('/usr'):
            #print("yes")
            SHAREDIR = os.path.join('/usr', 'share')
            ICONDIR = os.path.join(SHAREDIR, 'icons', 'hicolor', 'scalable', 'apps')
        else:
            ROOTDIR = os.path.dirname(__file__)
            #print(ROOTDIR)
            ICONDIR = os.path.normpath(
                os.path.join(ROOTDIR, 'images'))
        #print(ICONDIR)
        ICON = os.path.join(ICONDIR, 'slimbookamdcontroller.svg')
        #print('Ruta icono: '+ICON)
        
        try: 
            self.set_icon_from_file(ICON)
        except:
            print("Icon not found")
        self.set_decorated(True)
        self.set_resizable(False)
        self.set_size_request(0,560) #anchoxalto
        self.set_position(Gtk.WindowPosition.CENTER)
        self.get_style_context().add_class("bg-image")

        self.inicio()

        grid = Gtk.Grid(column_homogeneous=False,
                         column_spacing=0,
                         row_spacing=12)
        grid.set_name('label')
        self.add(grid) 

        

    # CONTENT --------------------------------------------------------------------------------

        label1 = Gtk.Label(label=_("Enable app at startup"))
        label1.set_halign(Gtk.Align.START)
        
        label2 = Gtk.Label(label=_("Show indicator icon"))
        label2.set_halign(Gtk.Align.START)
       
        button1 = Gtk.Button(label ="Button 1")
        button1.set_halign(Gtk.Align.START)
        button1.get_style_context().add_class("button-none")

        button2 = Gtk.Button(label ="Button 2")
        button2.set_halign(Gtk.Align.START)
        button2.get_style_context().add_class("button-none")

        separador = Gtk.Image.new_from_file(currpath+'/images/separador.png')
        separador.set_halign(Gtk.Align.CENTER)
        separador2 = Gtk.Image.new_from_file(currpath+'/images/separador.png')
        separador2.set_halign(Gtk.Align.CENTER)
        separador3 = Gtk.Image.new_from_file(currpath+'/images/separador.png')
        separador3.set_halign(Gtk.Align.CENTER)


        pixbuf1 = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename = currpath+'/images/cross.png',
			width = 20,
			height = 20,
			preserve_aspect_ratio=True)

        
        close = Gtk.Image.new_from_pixbuf(pixbuf1)
        close.get_style_context().add_class("close")
        close.set_halign(Gtk.Align.END)

        evnt_close = Gtk.EventBox()
        evnt_close.add(close)
        evnt_close.connect("button_press_event", self.on_btnCerrar_clicked)


    # CPU ---------------------------------------------------------------------------------
        cpuGrid = Gtk.Grid(column_homogeneous=False,
                         column_spacing=0,
                         row_spacing=12)
        cpuGrid.set_name('cpuGrid')

        # Consumo Procesador
        hbox_consumo = Gtk.HBox()

        cpu_name = Gtk.Label(label=cpu[12:]) 
        cpu_name.set_halign(Gtk.Align.CENTER)

        """ consumo = Gtk.Label(label=_('Current consumption: ')+ self.cpu_value('slow-limit')+" - "+self.cpu_value('stapm-limit')+" - "+self.cpu_value('fast-limit')+" mW.")
        consumo.set_halign(Gtk.Align.END) """

        hbox_consumo.pack_start(cpu_name, True, True, 0)
        #hbox_consumo.pack_start(consumo, True, True, 0)

        img = ''

        if entorno_usu.find("es") >= 0:         #Español
            img='modos_es.png'
        else: 
            img='modos_en.png'                  #Inglés

        modos = Gtk.Image.new_from_file(currpath+'/images/'+img)
        modos.get_style_context().add_class("cambModos")
        modos.set_halign(Gtk.Align.CENTER)

        #CAJA 1
        vbox1 = Gtk.VBox()
        rbutton1.connect("toggled", self.on_button_toggled, "low")
        rbutton1.set_name('radiobutton') 
        rbutton1.set_halign(Gtk.Align.CENTER)

        rbutton1_img = Gtk.Image.new_from_file(currpath+'/images/modo1.png')
        rbutton1_img.set_halign(Gtk.Align.CENTER)

        vbox1.pack_start(rbutton1_img, False, False, 0)
        vbox1.pack_start(rbutton1, False, False, 0)
        
        #CAJA 2
        vbox2 = Gtk.VBox()
        rbutton2.connect("toggled", self.on_button_toggled, "medium")
        rbutton2.set_name('radiobutton')
        rbutton2.set_halign(Gtk.Align.CENTER)

        rbutton2_img = Gtk.Image.new_from_file(currpath+'/images/modo2.png')
        rbutton2_img.set_halign(Gtk.Align.CENTER)
        
        vbox2.pack_start(rbutton2_img, False, False, 0)
        vbox2.pack_start(rbutton2, False, False, 0)

        #CAJA 3
        vbox3 = Gtk.VBox()
        rbutton3.connect("toggled", self.on_button_toggled, "high")
        rbutton3.set_name('radiobutton')
        rbutton3.set_halign(Gtk.Align.CENTER)
        
        rbutton3_img = Gtk.Image.new_from_file(currpath+'/images/modo3.png')
        rbutton3_img.set_halign(Gtk.Align.CENTER)
        
        vbox3.pack_start(rbutton3_img, False, False, 0)
        vbox3.pack_start(rbutton3, False, False, 0)

        cpuGrid.attach(hbox_consumo, 4, 8, 5, 1)
        
        cpuGrid.attach(modos, 5, 10, 3, 1)

        cpuGrid.attach(vbox1, 5, 11, 1, 2)
        cpuGrid.attach(vbox2, 6, 11, 1, 2)
        cpuGrid.attach(vbox3, 7, 11, 1, 2)


    # GPU --------------------------------------------------------------------------------
        def add_gpus_pages(notebook: Gtk.Notebook):
            number_of_gpus = GpuService.get_number_of_gpus()
            for gpu_index in range(number_of_gpus):
                page = Gtk.Box()
                page.set_border_width(10)
                page.set_halign(Gtk.Align.CENTER)
                page.add(build_gpu_listbox(gpu_index))
                notebook.append_page(page, Gtk.Label(label="GPU {}".format(gpu_index)))
            return

        def _update_label(label: Gtk.Label, serviceFunction, gpu_index: int):
            label.set_label(serviceFunction(gpu_index))
            return True
        
        def build_gpu_listbox(gpu_index: int) -> Gtk.Box:
            GPU_INFO = {
                'Model': GpuService.get_model(gpu_index),
                'VRAM': GpuService.get_vram(gpu_index),
                'Temp': GpuService.get_temp(gpu_index),
                'GPU Freq': GpuService.get_slck(gpu_index),
                'Mem Freq': GpuService.get_mlck(gpu_index),
                'PCI Slot': GpuService.get_slot(gpu_index)
            }

            box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

            listbox = Gtk.ListBox()
            listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            box_outer.pack_start(listbox, True, True, 0)

            for key in GPU_INFO:
                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
                row.add(hbox)
                hbox.pack_start(Gtk.Label(label=key, xalign=0), True, True, 0)
                label = Gtk.Label(label=GPU_INFO[key])
                if key in ['Temp', 'GPU Freq', 'Mem Freq']:
                    serviceFunction = None
                    if key == 'Temp':
                        serviceFunction = GpuService.get_temp
                    elif key == 'GPU Freq':
                        serviceFunction = GpuService.get_slck
                    else:
                        serviceFunction = GpuService.get_mlck
                    GLib.timeout_add_seconds(2, _update_label, label, serviceFunction, gpu_index)
                hbox.pack_start(label, False, True, 0)
                listbox.add(row)

            return box_outer

    # NOTEBOOK ----------------------------------------------------------------------------------
        notebook = Gtk.Notebook()
        self.add(notebook)
        notebook.set_halign(Gtk.Align.CENTER)

        page1 = Gtk.Box()
        page1.set_orientation(Gtk.Orientation.HORIZONTAL)
        page1.set_border_width(10)
        page1.set_halign(Gtk.Align.CENTER)
        page1.add(cpuGrid)
        notebook.append_page(page1, Gtk.Label(label="CPU"))

        if GpuService.exists_amd_gpus():
            add_gpus_pages(notebook)


    # BUTTONS --------------------------------------------------------------------------------

        botonesBox = Gtk.Box(spacing=10)
        botonesBox.set_name('botonesBox')
        botonesBox.set_halign(Gtk.Align.CENTER)
        botonesBox.set_name('buttons')

        #ACEPTAR
        btnAceptar = Gtk.ToggleButton(label=_("ACCEPT"))
        btnAceptar.set_size_request(125, 30)
        btnAceptar.connect("toggled", self.on_btnAceptar_clicked)
        botonesBox.pack_start(btnAceptar, True, True, 0)

        #CERRAR
        btnCancelar = Gtk.ToggleButton(label=_("CANCEL"))
        btnCancelar.set_size_request(125, 30)
        btnCancelar.connect("toggled", self.on_btnCerrar_clicked, 'x')
        botonesBox.pack_start(btnCancelar, True, True, 0)


    # BTNABOUT_US ----------------------------------------------------------------------------

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename = currpath+'/images/question.png',
			width = 20,
			height = 20,
			preserve_aspect_ratio=True)

        iconApp = Gtk.Image.new_from_pixbuf(pixbuf)
        iconApp.get_style_context().add_class("help")
        iconApp.set_halign(Gtk.Align.END)


        evnt_box = Gtk.EventBox()
        evnt_box.add(iconApp)

        evnt_box.connect("button_press_event", self.about_us)

        #CURSOR

        """ cursor = Gdk.Cursor(Gdk.CursorType.HAND1) #esto crea un cursor que mostrara un lápiz
        evnt_box.get_root_window().set_cursor(cursor) #se lo asignamos a nuestro dibujable """
            

        """ dot_widget = self.dot_widget
        item = dot_widget.get_url(x, y)
        if item is None:
            item = dot_widget.get_jump(x, y)
        if item is not None:
            dot_widget.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))
            dot_widget.set_highlight(item.highlight)
        else:
            dot_widget.get_window().set_cursor(None)
            dot_widget.set_highlight(None)  """


    # GRID ATTACH ----------------------------------------------------------------------------

        grid.attach(button1, 1, 1, 2, 1)
        grid.attach(button2, 9, 1, 2, 1)

        grid.attach(label1, 5, 4, 3, 1)
        grid.attach(switch1, 7, 4, 2, 1)
        grid.attach(separador, 2, 5, 8, 1)
        grid.attach(label2, 5, 6, 3, 1)
        grid.attach(switch2, 7, 6, 2, 1)
        grid.attach(separador2, 2, 7, 8, 1)

        grid.attach(notebook, 0, 10, 12, 1)
        
        grid.attach(botonesBox, 6, 20, 1, 1)
        grid.attach(evnt_box, 9, 20, 2, 1)
        grid.attach(evnt_close, 9, 0, 2, 1)

  
    
    #Saves selection in a variable
    def on_button_toggled(self, button, name):
        self.modo_actual = name

    
    def on_btnAceptar_clicked(self, widget):
        
        call=''

        if self.modo_actual == "low":

            print('Updating '+self.modo_actual+' to : '+self.parameters[0]+' '+self.parameters[1]+' '+self.parameters[2]+'.\n')

            call=os.system('python3 '+currpath+'/applyconfig.py')

        if self.modo_actual == "medium":

            print('Updating '+self.modo_actual+' to : '+self.parameters[3]+' '+self.parameters[4]+' '+self.parameters[5]+'.\n')

            call=os.system('python3 '+currpath+'/applyconfig.py')

        if self.modo_actual == "high":
  
            print('Updating '+self.modo_actual+' to : '+self.parameters[6]+' '+self.parameters[7]+' '+self.parameters[8]+'.\n')

            call=os.system('python3 '+currpath+'/applyconfig.py')

        
        if (call == 0):
            os.system("notify-send 'Slimbook AMD Controller' '"+ _("Changes have been executed correctly.") +"' -i '" + currpath+'/images/icono.png' + "'")
        else:
            os.system("notify-send 'Slimbook AMD Controller' '"+ _("Your CPU is not avalible, this software might not work.") +"' -i '" + currpath+'/images/icono.png' + "'")
           

        #Comprobamos los switch
        self._inicio_automatico(switch1, switch1.get_state())

        self._show_indicator(switch2, switch2.get_state())

        

        #ACTUALIZAMOS VARIABLES
        self.update_config_file("mode", self.modo_actual)
        self.update_config_file("autostart", self.autostart_actual)
        self.update_config_file("show-icon", self.indicador_actual) 

        self.reboot_indicator()
        
        print(user + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf')
        
        #CERRAMOS PROGRAMA
        Gtk.main_quit()


    def inicio(self):
    
        self.creafichero() #--> COMPRUEBA SI EL FICHERO ESTA CREADO Y SI NO, LO CREA.
        config = configparser.ConfigParser()
        config.read(config_file)
        
        print('Loading data from .conf:\n')

        #Inicio automatico :):
        if config.get('CONFIGURATION', 'autostart') == 'on':
            self.autostart_actual = 'on'
            switch1.set_active(True)           
            print('- Autostart enabled')

        else:
            self.autostart_actual = 'off'
            switch1.set_active(False)
            print('- Autostart disabled')


        #Mostramos indicador, o no :):
        if config.get('CONFIGURATION', 'show-icon') == 'on':
            self.indicador_actual = 'on'
            switch2.set_active(True)
            print('- Indicator enabled')
        else:
            self.indicador_actual = 'off'
            switch2.set_active(False)
            print('- Indicator disabled')

        #RadiobuttonSelection        
        if config.get('CONFIGURATION', 'mode') == "low":
            print('- Low')
            self.modo_actual = 'low'
            rbutton1.set_active(True)
        else:
            if config.get('CONFIGURATION', 'mode') == "medium":
                print('- Medium')
                self.modo_actual = 'medium'
                rbutton2.set_active(True)

            else:
                print('- High')
                self.modo_actual = 'high'
                rbutton3.set_active(True)
        
        #CPU Parameters
        params = config.get('CONFIGURATION', 'cpu-parameters').split('-')
        self.parameters = params
        print('- CPU Parameters: '+ str(self.parameters))       

        print("\n.conf data loaded succesfully!\n")

        print('\nINFO:')
        os.system('sudo /usr/share/slimbookamdcontroller/ryzenadj --info')
        print('\n')
        


    #RECOGEMOS PARAMETROS DEL RYZEN ADJ
    def cpu_value(self, parameter):
        call = subprocess.getoutput('sudo /usr/share/slimbookamdcontroller/ryzenadj --info')
        salida = str(call)

        index = str(salida.find(parameter))
        #print('Indice: '+index)

        #Que encuentre cuatro digitos juntos seguidos de 1 o 2 letras mayusculas
        patron = re.compile("([0-9]{1,2}\.[0-9]{3,})[ ]\|[ ]("+parameter+")")
        value = patron.search(call).group(1)
        param = patron.search(call).group(2)

        print('Value: '+str(value))
        print('Param: '+param)

        return value
    

    def reboot_indicator(self):

        print('\nProcess PID')
        indicator = subprocess.getoutput('pgrep -f slimbookamdcontrollerindicator')
        print(indicator)

        os.system('kill -9 '+indicator)
        print('Starting indicator...')
        os.system('python3 '+currpath+'/slimbookamdcontrollerindicator.py  &')
        print()

    #Copies autostart file in directory
    def _inicio_automatico(self, switch, state):

        if not os.path.exists (user+'/.config/autostart'):
            os.system('mkdir ~/.config/autostart')    
            print('Dir autostart created.')

        if switch.get_active() is True:
            print("\nAutostart Enabled")           
            if not os.path.isfile(AUTOSTART_DESKTOP):
                shutil.copy(LAUNCHER_DESKTOP, AUTOSTART_DESKTOP)
                print("File .conf has been copied!.")
            self.autostart_actual = 'on'
        else:
            print("\nAutostart Disabled")
            if os.path.isfile(AUTOSTART_DESKTOP):
                os.remove(AUTOSTART_DESKTOP)                
                print("File .conf has been deleted.")
            self.autostart_actual = 'off'

        """ print('Mode now: '+ self.modo_actual) """
        print('Autostart now: '+ self.autostart_actual+'')
        """ print('Indicator now: '+ self.indicador_actual)
        print() """
    

    def _show_indicator(self, switch, state):

        if switch.get_active() is True:
            print("\nIndicator Enabled")
            self.indicador_actual = 'on' # --> Luego esta variable será guardada y cargada desde el programa indicador
        else:
            print("\nIndicator Disabled")
            self.indicador_actual= 'off'

        """
        print('Mode now: '+ self.modo_actual)
        print('Autostart now: '+ self.autostart_actual) """
        print('Indicador now: '+ self.indicador_actual)
        print()


    def about_us(self, widget, x):
        print('\nINFO:')
        os.system('sudo /usr/share/slimbookamdcontroller/ryzenadj --info')
        print('\n')
        #Abre la ventana de info
        from slimbookamdcontrollerinfo import PreferencesDialog
        #os.system('python3 '+currpath+'/slimbookamdcontrollerinfo.py')

    def on_btnCerrar_clicked(self, widget, x):
        Gtk.main_quit()
    
    #Funcion crear directorio /slimbookamdcontroller y crear fichero de configuracion si no existe ya.    
    def creafichero(self):
        if os.path.isfile(user+'/.config/slimbookamdcontroller/slimbookamdcontroller.conf'):
            print('File .conf already exists\n')           
        else:
            print ("File doesn't exist")

            if os.path.exists (user+'/.config/slimbookamdcontroller'):
                print('Directory already exists')
                os.system('touch ~/.config/slimbookamdcontroller/slimbookamdcontroller.conf')
                print('Creating file')

                with open( user + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf', 'w') as conf:
                    self.fichero_conf().write(conf)
                print('File created succesfully!')

            else:
                print("Directory doesen't exist")
                os.system('mkdir ~/.config/slimbookamdcontroller')
                os.system('touch ~/.config/slimbookamdcontroller/slimbookamdcontroller.conf')
                print('Creating file')

                with open( user + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf', 'w') as conf:
                    self.fichero_conf().write(conf)
                print('File created succesfully!')

    #Genera config_object para el .conf
    def fichero_conf(self):
        
        #CPU data comprobation 
        if letras == "U":
                self.parameters=('8000-8000-8000','11000-11000-15000','25000-30000-35000')
        else:
            if letras == "HS":
                self.parameters=('10000-10000-10000','15000-15000-25000','60000-65000-70000')
            else:
                if letras == "HX" or letras == "H":
                    self.parameters=('10000-10000-10000','15000-15000-25000','70000-80000-100000')
                else:
                    print("Procesador no concebido por este software")
                    self.parameters=('xxx','xxx','xxx')       
                    os.system("notify-send 'Slimbook AMD Controller' '"+ (_("Your CPU isn't avalible")) +"' -i '" + currpath+'/images/icono.png' + "'")
                    
        config_object["CONFIGURATION"] = {
        "mode": "low",                
        "autostart": "off",
        "show-icon": "off",
        "cpu-parameters":  self.parameters[0]+"-"+self.parameters[1]+"-"+self.parameters[2]
        }
        return config_object
  
    def update_config_file(self, variable, value):

        fichero = user + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf'
        config = configparser.ConfigParser()
        config.read(fichero)
        
        # We change our variable: config.set(section, variable, value)
        config.set('CONFIGURATION', str(variable), str(value))

        # Writing our configuration file 
        with open(fichero, 'w') as configfile:
            config.write(configfile)

        print("\n- Variable |"+variable+"| updated in .conf, actual value: "+value)

win = SlimbookAMD()

style_provider = Gtk.CssProvider()
style_provider.load_from_path(currpath+'/css/style.css')

Gtk.StyleContext.add_provider_for_screen (
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

win.set_deletable(False)

win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
