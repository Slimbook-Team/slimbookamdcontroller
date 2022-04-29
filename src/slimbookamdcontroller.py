#!/usr/bin/python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser
import gi, os, subprocess, logging, sys
import shutil, math, re
import utils
from pathlib import Path
from constants.gpu_constants import DYNAMIC_GPU_PROPERTIES, GPU_FREQ, MEM_FREQ, MODEL, PCI_SLOT, TEMP, VRAM, VRAM_USAGE
import slimbookamdcontrollerinfo as info
try:
    from services.gpu_service import GpuService
except:
    pass

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gtk, GLib, GdkPixbuf

APPNAME = 'slimbookamdcontroller'
USER_NAME = utils.get_user()
HOMEDIR = os.path.expanduser('~'+USER_NAME)

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = '{}/.config/{}/{}.conf'.format(HOMEDIR, APPNAME, APPNAME)
LAUNCHER_DESKTOP = os.path.join(
    BASE_DIR, "{}-autostart.desktop".format(APPNAME))
AUTOSTART_DESKTOP = os.path.expanduser(
    "{}/.config/autostart/{}-autostart.desktop".format(HOMEDIR, APPNAME))

_ = utils.load_translation(APPNAME)

iconpath = CURRENT_PATH+'/amd.png'

cpu = utils.get_cpu_info('name')
patron = re.compile('[ ](.*)[ ]*([0-9]).*([0-9]{4,})(\w*)')
type = patron.search(cpu).group(1).strip()
gen = patron.search(cpu).group(2)
number = patron.search(cpu).group(3)
line_suffix = patron.search(cpu).group(4)

config = ConfigParser()
config.read(CONFIG_FILE)

class SlimbookAMD(Gtk.ApplicationWindow):

    modo_actual = ""
    indicador_actual = ""
    autostart_actual = ""
    parameters = ''
    cpu_ok = False

    switch1 = Gtk.Switch()
    switch1.set_halign(Gtk.Align.END)

    switch2 = Gtk.Switch()
    switch2.set_halign(Gtk.Align.END)

    rbutton1 = Gtk.RadioButton.new_with_label_from_widget(None, (_("Low")))
    rbutton2 = Gtk.RadioButton.new_with_mnemonic_from_widget(rbutton1, (_("Medium")))
    rbutton3 = Gtk.RadioButton.new_with_mnemonic_from_widget(rbutton1, (_("High")))

    def __init__(self):

        # VENTANA
        Gtk.Window.__init__(self, title="Slimbook AMD Controller")

        self.set_icon()
        self.inicio()

        self.set_decorated(False)

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

        separador = Gtk.Image.new_from_file(CURRENT_PATH+'/images/separador.png')
        separador.set_halign(Gtk.Align.CENTER)
        separador2 = Gtk.Image.new_from_file(CURRENT_PATH+'/images/separador.png')
        separador2.set_halign(Gtk.Align.CENTER)
        separador3 = Gtk.Image.new_from_file(CURRENT_PATH+'/images/separador.png')
        separador3.set_halign(Gtk.Align.CENTER)

        pixbuf1 = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=CURRENT_PATH+'/images/cross.png',
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

        idiomas = utils.get_languages()[0]

        print (idiomas)
        if idiomas.find("es") >= 0:  # Español
            img = 'modos_es.png'
        else:
            img = 'modos_en.png'  # Inglés

        modos = Gtk.Image.new_from_file(CURRENT_PATH+'/images/'+img)
        modos.get_style_context().add_class("cambModos")
        modos.set_halign(Gtk.Align.CENTER)

        # CAJA 1
        vbox1 = Gtk.VBox()
        self.rbutton1.connect("toggled", self.on_button_toggled, "low")
        self.rbutton1.set_name('radiobutton')
        self.rbutton1.set_halign(Gtk.Align.CENTER)

        rbutton1_img = Gtk.Image.new_from_file(CURRENT_PATH+'/images/modo1.png')
        rbutton1_img.set_halign(Gtk.Align.CENTER)

        vbox1.pack_start(rbutton1_img, False, False, 0)
        vbox1.pack_start(self.rbutton1, False, False, 0)

        # CAJA 2
        vbox2 = Gtk.VBox()
        self.rbutton2.connect("toggled", self.on_button_toggled, "medium")
        self.rbutton2.set_name('radiobutton')
        self.rbutton2.set_halign(Gtk.Align.CENTER)

        rbutton2_img = Gtk.Image.new_from_file(CURRENT_PATH+'/images/modo2.png')
        rbutton2_img.set_halign(Gtk.Align.CENTER)

        vbox2.pack_start(rbutton2_img, False, False, 0)
        vbox2.pack_start(self.rbutton2, False, False, 0)

        # CAJA 3
        vbox3 = Gtk.VBox()
        self.rbutton3.connect("toggled", self.on_button_toggled, "high")
        self.rbutton3.set_name('radiobutton')
        self.rbutton3.set_halign(Gtk.Align.CENTER)

        rbutton3_img = Gtk.Image.new_from_file(CURRENT_PATH+'/images/modo3.png')
        rbutton3_img.set_halign(Gtk.Align.CENTER)

        vbox3.pack_start(rbutton3_img, False, False, 0)
        vbox3.pack_start(self.rbutton3, False, False, 0)

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

    # GPU ------------------------------------------------------------------------------------
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
                MODEL: GpuService.get_model(gpu_index),
                VRAM: GpuService.get_vram(gpu_index),
                VRAM_USAGE: GpuService.get_vram_usage(gpu_index),
                TEMP: GpuService.get_temp(gpu_index),
                GPU_FREQ: GpuService.get_slck(gpu_index),
                MEM_FREQ: GpuService.get_mlck(gpu_index),
                PCI_SLOT: GpuService.get_slot(gpu_index)
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

                hbox.pack_start(Gtk.Label(label=_(key), xalign=0), True, True, 0)

                label = Gtk.Label(label=GPU_INFO[key], xalign=1)

                if key in DYNAMIC_GPU_PROPERTIES:
                    serviceFunction = None
                    if key == TEMP:
                        serviceFunction = GpuService.get_temp
                    elif key == GPU_FREQ:
                        serviceFunction = GpuService.get_slck
                    elif key == MEM_FREQ:
                        serviceFunction = GpuService.get_mlck
                    else:
                        serviceFunction = GpuService.get_vram_usage
                    GLib.timeout_add_seconds(
                        2, _update_label, label, serviceFunction, gpu_index)

                hbox.pack_start(label, True, True, 0)
                listbox.add(row)

            return box_outer

    # NOTEBOOK -------------------------------------------------------------------------------
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
            filename=CURRENT_PATH+'/images/question.png',
            width=23,
            height=23,
            preserve_aspect_ratio=True)

        iconApp = Gtk.Image.new_from_pixbuf(pixbuf)
        iconApp.get_style_context().add_class("help")

        evnt_box = Gtk.EventBox()
        evnt_box.set_halign(Gtk.Align.END)
        evnt_box.add(iconApp)

        evnt_box.connect("button_press_event", self.about_us)

        pixbuf1 = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename = CURRENT_PATH+'/images/settings.png',
			width = 20,
			height = 20,
			preserve_aspect_ratio=True)


        settings = Gtk.Image.new_from_pixbuf(pixbuf1)
        evnt_settings = Gtk.EventBox()
        evnt_settings.set_valign(Gtk.Align.CENTER)
        evnt_settings.set_halign(Gtk.Align.END)
        evnt_settings.add(settings)
        evnt_settings.connect("button_press_event", self.settings)
               
        hbox_close = Gtk.HBox()
        hbox_close.set_valign(Gtk.Align.START)
        hbox_close.set_halign(Gtk.Align.END)
        hbox_close.add(evnt_settings)
        hbox_close.add(evnt_close)

        version_tag = Gtk.Label(label='')
        version_tag.set_halign(Gtk.Align.START)
        version_tag.set_valign(Gtk.Align.END)
        version_tag.set_name('version')
        version_line = subprocess.getstatusoutput(
            "cat "+CURRENT_PATH+"/changelog |head -n1| egrep -o '\(.*\)'")
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
        grid.attach(self.switch1, 7, 4, 2, 1)
        grid.attach(separador, 2, 5, 8, 1)
        grid.attach(label2, 3, 6, 3, 1)
        grid.attach(self.switch2, 7, 6, 2, 1)
        grid.attach(separador2, 2, 7, 8, 1)

        """ grid.attach(hbox_consumo, 2, 8, 8, 1)
        grid.attach(modos, 2, 10, 8, 1)
        grid.attach(hbox_radios, 3, 11, 6, 2) """

        grid.attach(notebook, 3, 8, 6, 1)

        self.win_grid.attach(grid, 1, 1, 5, 5)
        self.win_grid.attach(botonesBox, 1, 7, 5, 1)
        self.win_grid.attach(version_tag, 1, 7, 5, 1)
        self.win_grid.attach(evnt_box, 5, 7, 1, 1)
        self.win_grid.attach(hbox_close, 5, 0, 1, 1)
        self.show_all()
        
        self.set_cpu()
    
        try:
            params = config.get('USER-CPU', 'cpu-parameters').split('/')
            self.parameters = params
        except:
            print('CPU not added')


    def settings(self, widget=None, x=None):
        import settings
        self.active = False
        dialog = settings.Dialog()

    def set_icon(self):
        if str(Path(__file__).parent.absolute()).startswith('/usr'):
            SHAREDIR = os.path.join('/usr', 'share')
            ICONDIR = os.path.join(
                SHAREDIR, 'icons', 'hicolor', 'scalable', 'apps')
        else:
            ROOTDIR = os.path.dirname(__file__)
            ICONDIR = os.path.normpath(
                os.path.join(ROOTDIR, 'images'))

        ICON = os.path.join(ICONDIR, 'slimbookamdcontroller.svg')

        try:
            self.set_icon_from_file(ICON)
        except:
            print("Icon not found")

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

        # Check secureboot        
        call = subprocess.getstatusoutput('mokutil --sb-state | grep -i "SecureBoot disabled"')

        if not call[0] == 0:
            print('mokutil --sb-state : shows SecureBoot State')
            self.dialog(_("Secureboot Warning"),
                        _("This computer has Secureboot enabled, which does not allow kernel to manage CPU parameters."))
            sys.exit(1)

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

            returncode = subprocess.call('pkexec slimbookamdcontroller-pkexec', shell=True, stdout=subprocess.PIPE)

            if (returncode == 0):
                os.system("notify-send 'Slimbook AMD Controller' '" + _("Changes have been executed correctly.") +
                          "' -i '" + CURRENT_PATH+'/images/slimbookamdcontroller.svg' + "'")
                # Comprobamos los switch
                self._inicio_automatico(self.switch1, self.switch1.get_state())

                self._show_indicator(self.switch2, self.switch2.get_state())

                # ACTUALIZAMOS VARIABLES
                self.update_config_file("mode", self.modo_actual)
                self.update_config_file("autostart", self.autostart_actual)
                self.update_config_file("show-icon", self.indicador_actual)

                self.reboot_indicator()

            else:
                os.system("notify-send 'Slimbook AMD Controller' '" + _("Your CPU is not avalible, this software might not work.") +
                          "' -i '" + CURRENT_PATH+'/images/slimbookamdcontroller.png' + "'")
        except Exception as e:
            print(e)
            os.system("notify-send 'Slimbook AMD Controller' '" + _("Your CPU is not avalible, this software might not work.") +
                      "' -i '" + CURRENT_PATH+'/images/slimbookamdcontroller.png' + "'")

        # CERRAMOS PROGRAMA
        Gtk.main_quit()

    def dialog(self, title, message, link=None):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.CLOSE,
            text=title,
        )

        dialog.format_secondary_text(
            message
        )

        dialog.set_position(Gtk.WindowPosition.CENTER)

        response = dialog.run()

        if response == Gtk.ResponseType.CLOSE:

            print("WARN dialog closed")

        dialog.destroy()

    def inicio(self):
        print('Loading configuration:\n')
        
        ################ UPDATE APROXIMATION
        # FIELDS = [
        # {
        #     'autostart': config.get('CONFIGURATION', 'autostart'),
        #     'show-icon': config.get('CONFIGURATION', 'show-icon'),
        #     'mode': config.get('CONFIGURATION', 'mode'),
        #     'cpu-parameters': config.get('USER-CPU', 'cpu-parameters'),

        # }]
        # try:
        #     for row, data in enumerate(FIELDS):
        #         print('Data:'+  str(data))
        #         self.loaded_data = data
        # except:
        #     from configuration import check_config

        # print(self.loaded_data.get('autostart'))
        ######################

        if not config.has_option('CONFIGURATION','autostart') == True:  # Testing conf
            from configuration import check_config
            
        elif config.get('CONFIGURATION', 'autostart') == 'on':
            self.autostart_actual = 'on'
            self.switch1.set_active(True)
            print('- Autostart enabled')

        else:
            self.autostart_actual = 'off'
            self.switch1.set_active(False)
            print('- Autostart disabled')

        if config.has_option('CONFIGURATION', 'show-icon') and config.get('CONFIGURATION', 'show-icon') == 'on':
            self.indicador_actual = 'on'
            self.switch2.set_active(True)
            print('- Indicator enabled')
        else:
            self.indicador_actual = 'off'
            self.switch2.set_active(False)
            print('- Indicator disabled')

        if config.get('CONFIGURATION', 'mode') == "low":
            print('- Low')
            self.modo_actual = 'low'
            self.rbutton1.set_active(True)

        elif config.get('CONFIGURATION', 'mode') == "medium":
                print('- Medium')
                self.modo_actual = 'medium'
                self.rbutton2.set_active(True)

        else:
            print('- High')
            self.modo_actual = 'high'
            self.rbutton3.set_active(True)

   
    # RECOGEMOS PARAMETROS DEL RYZEN ADJ
    def cpu_value(self, parameter):
        

        call = subprocess.getoutput(
            '/usr/share/slimbookamdcontroller/ryzenadj --info')
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
        subprocess.call('python3 {}/slimbookamdcontrollerindicator.py  &'.format(CURRENT_PATH), shell = True)

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
        if not config.has_option('USER-CPU', 'cpu-parameters') or len(config.get('USER-CPU', 'cpu-parameters')) <= 1:
            print('Setting cpu TDP values')
            cpu_codename = type+'-'+gen+'-'+number+line_suffix
                    
            if config.has_option('PROCESSORS',cpu_codename):
                print('Found processor in list')
                params = config['PROCESSORS'][cpu_codename]
                self.update_config_file('cpu-parameters', params, 'USER-CPU')
            else: 
                print('Could not find your proc in .conf')
                self.settings()
                config.read(CONFIG_FILE)       
        

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
        #os.system('sudo /usr/share/slimbookamdcontroller/ryzenadj --info')
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
style_provider.load_from_path(CURRENT_PATH+'/css/style.css')

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

win.connect("destroy", Gtk.main_quit)

Gtk.main()
