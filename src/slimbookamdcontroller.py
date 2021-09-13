#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gi.repository import Gdk, Gtk, GLib, GdkPixbuf
from configparser import ConfigParser
import os
import sys
import gi
import subprocess
import gettext
import locale
import shutil
import configparser
import math
import re  # Busca patrones expresiones regulares
from pathlib import Path
import slimbookamdcontrollerinfo as info
try:
    from services.gpu_service import GpuService
except:
    print()

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('AppIndicator3', '0.1')


srcpath = '/usr/share/slimbookamdcontroller/src'
sys.path.insert(1, srcpath)

USERNAME = subprocess.getstatusoutput("logname")

# 1. Try getting logged username  2. This user is not root  3. Check user exists (no 'reboot' user exists)
if USERNAME[0] == 0 and USERNAME[1] != 'root' and subprocess.getstatusoutput('getent passwd '+USERNAME[1]) == 0:
    USER_NAME = USERNAME[1]
else:
    USER_NAME = subprocess.getoutput('last -wn1 | head -n 1 | cut -f 1 -d " "')

HOMEDIR = subprocess.getoutput("echo ~"+USER_NAME)

currpath = os.path.dirname(os.path.realpath(__file__))
config_object = ConfigParser()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config_file = HOMEDIR+'/.config/slimbookamdcontroller/slimbookamdcontroller.conf'
LAUNCHER_DESKTOP = os.path.join(
    BASE_DIR, "slimbookamdcontroller-autostart.desktop")
AUTOSTART_DESKTOP = os.path.expanduser(
    "~/.config/autostart/slimbookamdcontroller-autostart.desktop")

# IDIOMAS ----------------------------------------------------------------

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

# Guardamos la salida del comando en una variable
cpu = subprocess.getoutput('cat /proc/cpuinfo | grep '+'name'+'| uniq')[13:]

# Que encuentre cuatro digitos juntos seguidos de 1 o 2 letras mayusculas
print(cpu)

patron = re.compile('[ ](.*)[ ]*([0-9]).*([0-9]{4,})(\w*)')
type = patron.search(cpu).group(1).strip()
gen = patron.search(cpu).group(2)
number = patron.search(cpu).group(3)
line_suffix = patron.search(cpu).group(4)

switch1 = Gtk.Switch()
switch1.set_halign(Gtk.Align.END)
switch2 = Gtk.Switch()
switch2.set_halign(Gtk.Align.END)

rbutton1 = Gtk.RadioButton.new_with_label_from_widget(None, (_("Low")))
rbutton2 = Gtk.RadioButton.new_with_mnemonic_from_widget(
    rbutton1, (_("Medium")))
rbutton3 = Gtk.RadioButton.new_with_mnemonic_from_widget(rbutton1, (_("High")))

config = configparser.ConfigParser()
check = config.read(config_file)


class SlimbookAMD(Gtk.ApplicationWindow):

    modo_actual = ""
    indicador_actual = ""
    autostart_actual = ""
    parameters = ''
    cpu_ok = False

    def __init__(self):

        # VENTANA
        Gtk.Window.__init__(self, title="Slimbook AMD Controller")

        if str(Path(__file__).parent.absolute()).startswith('/usr'):
            # print("yes")
            SHAREDIR = os.path.join('/usr', 'share')
            ICONDIR = os.path.join(
                SHAREDIR, 'icons', 'hicolor', 'scalable', 'apps')
        else:
            ROOTDIR = os.path.dirname(__file__)
            # print(ROOTDIR)
            ICONDIR = os.path.normpath(
                os.path.join(ROOTDIR, 'images'))
        # print(ICONDIR)
        ICON = os.path.join(ICONDIR, 'slimbookamdcontroller.svg')
        #print('Ruta icono: '+ICON)

        try:
            self.set_icon_from_file(ICON)
        except:
            print("Icon not found")
        self.set_decorated(False)
        # self.set_size_request(0,560) #anchoxalto
        self.set_position(Gtk.WindowPosition.CENTER)
        self.get_style_context().add_class("bg-image")

        # Movement
        self.active = True
        self.is_in_drag = False
        self.x_in_drag = 0
        self.y_in_drag = 0
        self.connect('button-press-event', self.on_mouse_button_pressed)
        self.connect('button-release-event', self.on_mouse_button_released)
        self.connect('motion-notify-event', self.on_mouse_moved)

        self.inicio()

        self.win_grid = Gtk.Grid(column_homogeneous=True,
                                 column_spacing=0,
                                 row_spacing=10)

        self.add(self.win_grid)

    # CONTENT --------------------------------------------------------------------------------

        label1 = Gtk.Label(label=_("Enable app at startup"))
        label1.set_halign(Gtk.Align.START)

        label2 = Gtk.Label(label=_("Show indicator icon"))
        label2.set_halign(Gtk.Align.START)

        button1 = Gtk.Button(label="Button 1")
        button1.set_halign(Gtk.Align.START)
        button1.get_style_context().add_class("button-none")

        button2 = Gtk.Button(label="Button 2")
        button2.set_halign(Gtk.Align.START)
        button2.get_style_context().add_class("button-none")

        separador = Gtk.Image.new_from_file(currpath+'/images/separador.png')
        separador.set_halign(Gtk.Align.CENTER)
        separador2 = Gtk.Image.new_from_file(currpath+'/images/separador.png')
        separador2.set_halign(Gtk.Align.CENTER)
        separador3 = Gtk.Image.new_from_file(currpath+'/images/separador.png')
        separador3.set_halign(Gtk.Align.CENTER)

        pixbuf1 = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/cross.png',
            width=20,
            height=20,
            preserve_aspect_ratio=True)

        close = Gtk.Image.new_from_pixbuf(pixbuf1)
        close.get_style_context().add_class("close")

        evnt_close = Gtk.EventBox()
        evnt_close.add(close)
        evnt_close.set_halign(Gtk.Align.END)
        evnt_close.connect("button_press_event", self.on_btnCerrar_clicked)

    # CPU ------------------------------------------------------------------------------------

        cpuGrid = Gtk.Grid(column_homogeneous=True,
                           column_spacing=0,
                           row_spacing=12)
        cpuGrid.set_name('cpuGrid')

        # CPU Name
        hbox_consumo = Gtk.HBox(spacing=15)

        cpu_name = Gtk.Label(label=cpu)
        cpu_name.set_halign(Gtk.Align.CENTER)
        hbox_consumo.pack_start(cpu_name, True, True, 0)

        # CPU Temp
        thermal_zones = subprocess.getstatusoutput(
            'ls /sys/class/thermal/ | grep thermal_zone')[1].split('\n')
        # print(str(thermal_zones))

        cpu_thermal_zone = None
        for thermal_zone in thermal_zones:
            if subprocess.getstatusoutput("cat /sys/class/thermal/"+thermal_zone+"/type | grep acpitz")[0] == 0:
                print('Found thermal zone!')
                cpu_thermal_zone = thermal_zone
                exit

        if cpu_thermal_zone != None:
            cpu_temp = subprocess.getstatusoutput(
                "cat /sys/class/thermal/"+cpu_thermal_zone+"/temp | sed 's/\(.\)..$/ °C/'")
            if cpu_temp[0] == 0:
                label = Gtk.Label(label=cpu_temp[1])

                def _update_label(label: Gtk.Label):
                    label.set_label(subprocess.getoutput(
                        "cat /sys/class/thermal/"+cpu_thermal_zone+"/temp | sed 's/\(.\)..$/ °C/'"))
                    return True

                GLib.timeout_add_seconds(2, _update_label, label)
                hbox_consumo.pack_start(label, True, True, 0)
            else:
                print('Cpu_temp 404')
        else:
            print('Thermal_zone 404')

        # consumo = Gtk.Label(label=_('Current consumption: ')+ self.cpu_value('slow-limit')+" - "+self.cpu_value('stapm-limit')+" - "+self.cpu_value('fast-limit')+" mW.")
        # consumo.set_halign(Gtk.Align.END)
        # hbox_consumo.pack_start(consumo, True, True, 0)

    # RADIOS ---------------------------------------------------------------------------------

        img = ''

        if entorno_usu.find("es") >= 0:  # Español
            img = 'modos_es.png'
        else:
            img = 'modos_en.png'  # Inglés

        modos = Gtk.Image.new_from_file(currpath+'/images/'+img)
        modos.get_style_context().add_class("cambModos")
        modos.set_halign(Gtk.Align.CENTER)

        # CAJA 1
        vbox1 = Gtk.VBox()
        rbutton1.connect("toggled", self.on_button_toggled, "low")
        rbutton1.set_name('radiobutton')
        rbutton1.set_halign(Gtk.Align.CENTER)

        rbutton1_img = Gtk.Image.new_from_file(currpath+'/images/modo1.png')
        rbutton1_img.set_halign(Gtk.Align.CENTER)

        vbox1.pack_start(rbutton1_img, False, False, 0)
        vbox1.pack_start(rbutton1, False, False, 0)

        # CAJA 2
        vbox2 = Gtk.VBox()
        rbutton2.connect("toggled", self.on_button_toggled, "medium")
        rbutton2.set_name('radiobutton')
        rbutton2.set_halign(Gtk.Align.CENTER)

        rbutton2_img = Gtk.Image.new_from_file(currpath+'/images/modo2.png')
        rbutton2_img.set_halign(Gtk.Align.CENTER)

        vbox2.pack_start(rbutton2_img, False, False, 0)
        vbox2.pack_start(rbutton2, False, False, 0)

        # CAJA 3
        vbox3 = Gtk.VBox()
        rbutton3.connect("toggled", self.on_button_toggled, "high")
        rbutton3.set_name('radiobutton')
        rbutton3.set_halign(Gtk.Align.CENTER)

        rbutton3_img = Gtk.Image.new_from_file(currpath+'/images/modo3.png')
        rbutton3_img.set_halign(Gtk.Align.CENTER)

        vbox3.pack_start(rbutton3_img, False, False, 0)
        vbox3.pack_start(rbutton3, False, False, 0)

        hbox_radios = Gtk.HBox(spacing=70)
        hbox_radios.add(vbox1)
        hbox_radios.add(vbox2)
        hbox_radios.add(vbox3)

        cpuGrid.attach(hbox_consumo, 4, 8, 5, 1)
        cpuGrid.attach(modos, 5, 10, 3, 1)
        cpuGrid.attach(hbox_radios, 4, 11, 5, 2)

    # BUTTONS --------------------------------------------------------------------------------

        botonesBox = Gtk.Box(spacing=10)
        botonesBox.set_name('botonesBox')
        botonesBox.set_halign(Gtk.Align.CENTER)
        botonesBox.set_name('buttons')

        # ACEPTAR
        btnAceptar = Gtk.ToggleButton(label=_("ACCEPT"))
        btnAceptar.set_size_request(125, 30)
        btnAceptar.connect("toggled", self.on_btnAceptar_clicked)
        botonesBox.pack_start(btnAceptar, True, True, 0)

        # CERRAR
        btnCancelar = Gtk.ToggleButton(label=_("CANCEL"))
        btnCancelar.set_size_request(125, 30)
        btnCancelar.connect("toggled", self.on_btnCerrar_clicked, 'x')
        botonesBox.pack_start(btnCancelar, True, True, 0)

    # GPU --------------------------------------------------------------------------------
        def add_gpus_pages(notebook: Gtk.Notebook):
            number_of_gpus = GpuService.get_number_of_gpus()
            for gpu_index in range(number_of_gpus):
                page = Gtk.Box()
                page.set_border_width(10)
                page.set_halign(Gtk.Align.START)
                page.add(build_gpu_listbox(gpu_index))
                notebook.append_page(page, Gtk.Label(
                    label="GPU {}".format(gpu_index)))
            return

        def _update_label(label: Gtk.Label, serviceFunction, gpu_index: int):
            label.set_label(serviceFunction(gpu_index))
            return True

        def build_gpu_listbox(gpu_index: int) -> Gtk.Box:
            GPU_INFO = {
                'Model': GpuService.get_model(gpu_index),
                'VRAM': GpuService.get_vram(gpu_index),
                'VRAM Usage': GpuService.get_vram_usage(gpu_index),
                'Temp': GpuService.get_temp(gpu_index),
                'GPU Freq': GpuService.get_slck(gpu_index),
                'Mem Freq': GpuService.get_mlck(gpu_index),
                'PCI Slot': GpuService.get_slot(gpu_index)
            }

            box_outer = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL, spacing=6)

            listbox = Gtk.ListBox()
            listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            box_outer.pack_start(listbox, True, True, 0)

            for key in GPU_INFO:
                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(
                    orientation=Gtk.Orientation.HORIZONTAL, spacing=100)
                row.add(hbox)

                hbox.pack_start(Gtk.Label(label=key, xalign=0), True, True, 0)

                label = Gtk.Label(label=GPU_INFO[key], xalign=1)

                if key in ['Temp', 'GPU Freq', 'Mem Freq', 'VRAM Usage']:
                    serviceFunction = None
                    if key == 'Temp':
                        serviceFunction = GpuService.get_temp
                    elif key == 'GPU Freq':
                        serviceFunction = GpuService.get_slck
                    elif key == 'Mem Freq':
                        serviceFunction = GpuService.get_mlck
                    else:
                        serviceFunction = GpuService.get_vram_usage
                    GLib.timeout_add_seconds(
                        2, _update_label, label, serviceFunction, gpu_index)

                hbox.pack_start(label, True, True, 0)
                listbox.add(row)

            return box_outer

    # NOTEBOOK ----------------------------------------------------------------------------------
        notebook = Gtk.Notebook()

        page1 = Gtk.Box()
        page1.set_orientation(Gtk.Orientation.HORIZONTAL)
        page1.set_border_width(10)
        page1.set_halign(Gtk.Align.CENTER)
        page1.add(cpuGrid)
        notebook.append_page(page1, Gtk.Label(label="CPU"))
        try:
            if GpuService.exists_amd_gpus():
                add_gpus_pages(notebook)
        except:
            print()

    # BTNABOUT_US ----------------------------------------------------------------------------

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=currpath+'/images/question.png',
            width=23,
            height=23,
            preserve_aspect_ratio=True)

        iconApp = Gtk.Image.new_from_pixbuf(pixbuf)
        iconApp.get_style_context().add_class("help")

        evnt_box = Gtk.EventBox()
        evnt_box.set_halign(Gtk.Align.END)
        evnt_box.add(iconApp)

        evnt_box.connect("button_press_event", self.about_us)

        version_tag = Gtk.Label(label='')
        version_tag.set_halign(Gtk.Align.START)
        version_tag.set_valign(Gtk.Align.END)
        version_tag.set_name('version')
        version_line = subprocess.getstatusoutput(
            "cat "+currpath+"/changelog |head -n1| egrep -o '\(.*\)'")
        if version_line[0] == 0:
            version = version_line[1]
            version_tag.set_markup(
                '<span font="10">Version '+version[1:len(version)-1]+'</span>')
        version_tag.set_justify(Gtk.Justification.CENTER)

    # GRID ATTACH ----------------------------------------------------------------------------
        grid = Gtk.Grid(column_homogeneous=False,
                        column_spacing=0,
                        row_spacing=10)

        grid.set_name('label')

        grid.attach(button1, 1, 1, 2, 1)
        grid.attach(button2, 9, 1, 2, 1)

        grid.attach(label1, 3, 4, 3, 1)
        grid.attach(switch1, 7, 4, 2, 1)
        grid.attach(separador, 2, 5, 8, 1)
        grid.attach(label2, 3, 6, 3, 1)
        grid.attach(switch2, 7, 6, 2, 1)
        grid.attach(separador2, 2, 7, 8, 1)

        """ grid.attach(hbox_consumo, 2, 8, 8, 1)
        grid.attach(modos, 2, 10, 8, 1)
        grid.attach(hbox_radios, 3, 11, 6, 2) """

        grid.attach(notebook, 3, 8, 6, 1)

        self.win_grid.attach(grid, 1, 1, 5, 5)
        self.win_grid.attach(botonesBox, 1, 7, 5, 1)
        self.win_grid.attach(version_tag, 1, 7, 5, 1)
        self.win_grid.attach(evnt_box, 5, 7, 1, 1)
        self.win_grid.attach(evnt_close, 5, 0, 1, 1)

    def on_realize(self, widget):
        monitor = Gdk.Display.get_primary_monitor(Gdk.Display.get_default())
        scale = monitor.get_scale_factor()
        monitor_width = monitor.get_geometry().width / scale
        monitor_height = monitor.get_geometry().height / scale
        width = self.get_preferred_width()[0]
        height = self.get_preferred_height()[0]
        self.move((monitor_width - width)/2, (monitor_height - height)/2)

    def on_mouse_moved(self, widget, event):
        if self.is_in_drag:
            xi, yi = self.get_position()
            xf = int(xi + event.x_root - self.x_in_drag)
            yf = int(yi + event.y_root - self.y_in_drag)
            if math.sqrt(math.pow(xf-xi, 2) + math.pow(yf-yi, 2)) > 10:
                self.x_in_drag = event.x_root
                self.y_in_drag = event.y_root
                self.move(xf, yf)

    def on_mouse_button_released(self, widget, event):
        if event.button == 1:
            self.is_in_drag = False
            self.x_in_drag = event.x_root
            self.y_in_drag = event.y_root

    def on_mouse_button_pressed(self, widget, event):

        # print(str(self.active))

        if event.button == 1 and self.active == True:
            self.is_in_drag = True
            self.x_in_drag, self.y_in_drag = self.get_position()
            self.x_in_drag = event.x_root
            self.y_in_drag = event.y_root
            return True
        return False

    def on_button_toggled(self, button, name):
        self.modo_actual = name

    def on_btnAceptar_clicked(self, widget):

        call = ''

        if self.modo_actual == "low":
            mode = 0

        if self.modo_actual == "medium":
            mode = 1

        if self.modo_actual == "high":
            mode = 2

        try:
            # This throws an exception if cpu is not found
            set_parameters = self.parameters[mode].split('-')
            print(set_parameters)

            print('Updating '+self.modo_actual+' to : ' +
                  set_parameters[0]+' '+set_parameters[1]+' '+set_parameters[2]+'.\n')

            call = subprocess.getstatusoutput(
                'python3 '+currpath+'/applyconfig.py')[0]

            if (call == 0):
                os.system("notify-send 'Slimbook AMD Controller' '" + _("Changes have been executed correctly.") +
                          "' -i '" + currpath+'/images/slimbookamdcontroller.svg' + "'")
                # Comprobamos los switch
                self._inicio_automatico(switch1, switch1.get_state())

                self._show_indicator(switch2, switch2.get_state())

                # ACTUALIZAMOS VARIABLES
                self.update_config_file("mode", self.modo_actual)
                self.update_config_file("autostart", self.autostart_actual)
                self.update_config_file("show-icon", self.indicador_actual)

                self.reboot_indicator()

            else:
                os.system("notify-send 'Slimbook AMD Controller' '" + _("Your CPU is not avalible, this software might not work.") +
                          "' -i '" + currpath+'/images/slimbookamdcontroller.png' + "'")
        except Exception:
            os.system("notify-send 'Slimbook AMD Controller' '" + _("Your CPU is not avalible, this software might not work.") +
                      "' -i '" + currpath+'/images/slimbookamdcontroller.png' + "'")

        print(HOMEDIR + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf')

        # CERRAMOS PROGRAMA
        Gtk.main_quit()

    def inicio(self):
        print('Loading data from .conf:\n')

        # Inicio automatico :):
        try:
            config['CONFIGURATION']['autostart']  # Testing conf
        except:
            print('Importando check_config')
            from configuration import check_config
            config.read(config_file)

        if config.get('CONFIGURATION', 'autostart') == 'on':
            self.autostart_actual = 'on'
            switch1.set_active(True)
            print('- Autostart enabled')

        else:
            self.autostart_actual = 'off'
            switch1.set_active(False)
            print('- Autostart disabled')

        # Mostramos indicador, o no :):
        if config.get('CONFIGURATION', 'show-icon') == 'on':
            self.indicador_actual = 'on'
            switch2.set_active(True)
            print('- Indicator enabled')
        else:
            self.indicador_actual = 'off'
            switch2.set_active(False)
            print('- Indicator disabled')

        # RadiobuttonSelection
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

        # CPU Parameters

        params = config.get('USER-CPU', 'cpu-parameters').split('/')

        if len(params) <= 1:
            print()
            print('Setting cpu TDP values')
            self.set_cpu()
            print()
            params = config.get('USER-CPU', 'cpu-parameters').split('/')
            # print(str(params))

        config.read(config_file)
        self.parameters = params
        print('- CPU Parameters: ' + str(self.parameters))

        print("\n.conf data loaded succesfully!\n")

        print('\nINFO:')
        os.system('sudo /usr/share/slimbookamdcontroller/ryzenadj --info')
        print('\n')
    
    # RECOGEMOS PARAMETROS DEL RYZEN ADJ
    def cpu_value(self, parameter):
        call = subprocess.getoutput(
            'sudo /usr/share/slimbookamdcontroller/ryzenadj --info')
        salida = str(call)

        index = str(salida.find(parameter))
        #print('Indice: '+index)

        # Que encuentre cuatro digitos juntos seguidos de 1 o 2 letras mayusculas
        patron = re.compile("([0-9]{1,2}\.[0-9]{3,})[ ]\|[ ]("+parameter+")")
        value = patron.search(call).group(1)
        param = patron.search(call).group(2)

        print('Value: '+str(value))
        print('Param: '+param)

        return value

    def reboot_indicator(self):

        print('\nProcess PID')
        indicator = subprocess.getoutput(
            'pgrep -f slimbookamdcontrollerindicator')
        print(indicator)

        os.system('kill -9 '+indicator)
        print('Starting indicator...')
        os.system('python3 '+currpath+'/slimbookamdcontrollerindicator.py  &')
        print()

    # Copies autostart file in directory
    def _inicio_automatico(self, switch, state):

        if not os.path.exists(HOMEDIR+'/.config/autostart'):
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

        print('Autostart now: ' + self.autostart_actual+'')

    def set_cpu(self):

        print(type, gen, number, line_suffix)
        if type.find('Ryzen') != -1:

            cpu_parse = type+'-'+gen+'-'+number+line_suffix
            print('Searching '+cpu_parse+'...')
            try:
                params = config['PROCESSORS'][cpu_parse]
                self.update_config_file('cpu-parameters', params, 'USER-CPU')
                self.cpu_ok = True
            except Exception as e:
                print(str(e))
                print('Could not find your proc in .conf')
                print('Trying to set default TDP values')
                try:
                    params = config['PROCESSORS'][line_suffix]
                    self.update_config_file(
                        'cpu-parameters', params, 'USER-CPU')
                    self.cpu_ok = True
                    print('TDP default values applied!')
                except Exception:
                    self.cpu_ok = False
                    print('Failed setting TDP default values!')
        else:
            print('Not an AMD Ryzen')

    def _show_indicator(self, switch, state):

        if switch.get_active() is True:
            print("\nIndicator Enabled")
            # --> Luego esta variable será guardada y cargada desde el programa indicador
            self.indicador_actual = 'on'
        else:
            print("\nIndicator Disabled")
            self.indicador_actual = 'off'

        print('Indicador now: ' + self.indicador_actual)
        print()

    def about_us(self, widget, x):
        self.active = False
        print('\nINFO:')
        os.system('sudo /usr/share/slimbookamdcontroller/ryzenadj --info')
        print('\n')
        # Abre la ventana de info

        dialog = info.PreferencesDialog()
        dialog.connect("destroy", self.close_dialog)

        dialog.show_all()

        #os.system('python3 '+currpath+'/slimbookamdcontrollerinfo.py')

    def close_dialog(self, dialog):
        dialog.close()

        self.active = True

    def on_btnCerrar_clicked(self, widget, x):
        Gtk.main_quit()

    def update_config_file(self, variable, value, section='CONFIGURATION'):

        fichero = HOMEDIR + '/.config/slimbookamdcontroller/slimbookamdcontroller.conf'
        config.read(fichero)

        # We change our variable: config.set(section, variable, value)
        config.set(section, str(variable), str(value))

        # Writing our configuration file
        with open(fichero, 'w') as configfile:
            config.write(configfile)

        print("\n- Variable |"+variable +
              "| updated in .conf, actual value: "+value)


win = SlimbookAMD()

style_provider = Gtk.CssProvider()
style_provider.load_from_path(currpath+'/css/style.css')

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
