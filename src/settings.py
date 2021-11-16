from configparser import ConfigParser

import gi
import os
import re
import utils

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
APP_NAME= 'slimbookamdcontroller'

USER_NAME = utils.get_user()
HOMEDIR = os.path.expanduser('~')

CONFIG_FILE = '{}/.config/{}/{}.conf'.format(HOMEDIR, APP_NAME, APP_NAME)
print(CONFIG_FILE)

config = ConfigParser()
config.read(CONFIG_FILE)

_ = utils.load_translation(APP_NAME)

CPU = utils.get_cpu_info('name')

patron = re.compile('[ ](.*)[ ]*([0-9]).*([0-9]{4,})(\w*)')
type = patron.search(CPU).group(1).strip()
version = patron.search(CPU).group(2)
number = patron.search(CPU).group(3)
line_suffix = patron.search(CPU).group(4)

MODEL_CPU = type+'-'+version+'-'+number+line_suffix

class WarnDialog(Gtk.Dialog):
    def __init__(self, parent, label):
        super().__init__(title=_("Warning"),transient_for=parent)
        self.set_name('warn')
        self.add_buttons(
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.set_default_size(500, 200)

        label.set_line_wrap(True)
        box = self.get_content_area()
        box.add(label)
        self.show_all()

class Settings_dialog(Gtk.Dialog):
    FIELDS = {
                'U':'8000-8000-8000/11000-11000-15000/25000-30000-35000/ 10/25 w',
                'HS':'10000-10000-10000/15000-15000-25000/60000-65000-70000/ 35/35 w',
                'HX':'10000-10000-10000/15000-15000-25000/70000-80000-100000/ 35/45 w',
                'H':'10000-10000-10000/15000-15000-25000/70000-80000-100000/ 35/45 w'
            }

    def __init__(self, parent):
        
        if config.has_option('USER-CPU', 'cpu-parameters') and config['USER-CPU']['cpu-parameters']!= '':
            values = config['USER-CPU']['cpu-parameters'].split('/')
            print('Loads from file.')
        else:
            try:
                values = self.FIELDS.get(line_suffix).split('/')
            except:
                values = ['0-0-0', '0-0-0', '0-0-0', '0', '0']
                
            print('Creates values.')

        length = len(values)-1
        values[length] = values[length][:values[length].find('w')]
        

        self.val = '{}/{}/{}/'.format(values[0],values[1],values[2])

        try:
            self.val = self.val+ '{}/{} w'.format(values[3], values[4][:values[4].find('w')])

        except:
            self.val = self.val+ '{} w'.format(values[3][:values[3].find('w')])
        
        print('CPU-Parameters: '+self.val)

        self.lowmode = (values[0].split('-'))
        self.midmode = (values[1].split('-'))
        self.highmode = (values[2].split('-'))

        self.low_default = float(values[3])
        try:
            self.high_default = float(values[4])
        except:
            self.high_default = float(values[3])
            print('Not found 4th value')

        super().__init__(title="Settings", transient_for=parent)
        self.set_name('dialog')
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        # WINDOW
        self.set_name('settings')

        center = Gtk.Align.CENTER
        left = Gtk.Align.START
        right = Gtk.Align.END

        win_grid = Gtk.Grid(column_homogeneous=False,
                            row_homogeneous=True,
                            column_spacing=10,
                            row_spacing=10)

        grid = Gtk.Grid(column_homogeneous=False,
                        row_homogeneous=True,
                        column_spacing=20,
                        row_spacing=10)

        self.get_content_area().add(win_grid)

        if self.low_default < 20:
            min = self.low_default - self.low_default/2 
        else:
            min = self.low_default - 3*(self.low_default/4)
        max = self.high_default*2

        # Low TDP Column

        label1 = Gtk.Label(label=_('Low TDP'))

        self.entry01 = _create_gui_element(
            float(self.lowmode[0])/1000, min, max)
        self.entry02 = _create_gui_element(
            float(self.midmode[0])/1000, min, max)
        self.entry03 = _create_gui_element(
            float(self.highmode[0])/1000, min, max)

        grid.attach(self.entry01, 1, 1, 1, 1)
        grid.attach(self.entry02, 1, 2, 1, 1)
        grid.attach(self.entry03, 1, 3, 1, 1)
        grid.attach(label1, 1, 0, 1, 1)


        # Mantained TDP Column

        label1 = Gtk.Label(label=_('Medium TDP'))
        self.entry1 = _create_gui_element(
            float(self.lowmode[1])/1000, min, max)
        self.entry2 = _create_gui_element(
            float(self.midmode[1])/1000, min, max)
        self.entry3 = _create_gui_element(
            float(self.highmode[1])/1000, min, max)

        grid.attach(self.entry1, 2, 1, 1, 1)
        grid.attach(self.entry2, 2, 2, 1, 1)
        grid.attach(self.entry3, 2, 3, 1, 1)
        grid.attach(label1, 2, 0, 1, 1)

        # High Power TDP Column

        label2 = Gtk.Label(_('High Power TDP'))

        self.entry4 = _create_gui_element(
            float(self.lowmode[2])/1000, min, max)
        self.entry5 = _create_gui_element(
            float(self.midmode[2])/1000, min, max)
        self.entry6 = _create_gui_element(
            float(self.highmode[2])/1000, min, max)

        grid.attach(self.entry4, 3, 1, 1, 1)
        grid.attach(self.entry5, 3, 2, 1, 1)
        grid.attach(self.entry6, 3, 3, 1, 1)
        grid.attach(label2, 3, 0, 1, 1)

        # Modes Column
        
        low_lbl = Gtk.Label(label=_('Low'), halign=left)
        mid_lbl = Gtk.Label(label=_('Medium'), halign=left)
        high_lbl = Gtk.Label(label=_('High'), halign=left)

        grid.attach(low_lbl, 0, 1, 1, 1)
        grid.attach(mid_lbl, 0, 2, 1, 1)
        grid.attach(high_lbl, 0, 3, 1, 1)

        separator = Gtk.Separator.new(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_valign(center)
        win_grid.attach(separator, 0, 4, 5, 1)

        recommended_lbl = Gtk.Label(
            label=_('Recommended values:'), halign=left)
        recommended_lbl.set_tooltip_text(_('This values are based on your CPU line suffix'))
        low_lbl = Gtk.Label(
            label=_('Low: {} watts'.format(self.low_default)), halign=left)

        high_lbl = Gtk.Label(
            label=_('High: {} watts.'.format(self.high_default)), halign=left)

        values_box = Gtk.VBox()
        values_box.add(low_lbl)
        values_box.add(high_lbl)

        win_grid.attach(recommended_lbl, 0, 5, 1, 1)
        win_grid.attach(values_box, 0, 6, 2, 2)
        win_grid.attach(grid, 0, 0, 5, 4)

        self.show_all()

class Dialog(Gtk.Window):
    
    print(MODEL_CPU)
    def __init__(self):
        Gtk.Window.__init__(self, title="Settings")
        
        self.set_icon_from_file(CURRENT_PATH+'/images/slimbookamdcontroller.svg')
        if type.find('Ryzen') == -1:
            if not config.has_option('PROCESSORS',MODEL_CPU):
                label = Gtk.Label(label=_(
                "Your processor is not supported yet. Do you want to add '{}' to the list?\n"+
                "If this is the case, you should go to the processor's vendor page and get information about your TDP values.").format(CPU))
                
                dialog = WarnDialog(self, label)

                response = dialog.run()

                dialog.close()
                dialog.destroy()
                    
            dialog = Settings_dialog(self)
            dialog.show_all()
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                self.accept(dialog)
                dialog.close()
                dialog.destroy()
                
            elif response == Gtk.ResponseType.CANCEL:
                dialog.close()
                dialog.destroy()
            
            
        else:
            label = Gtk.Label(label=_('Any AMD Ryzen processor detected!'))
            dialog = WarnDialog(self, label)
            response = dialog.run()

        dialog.close()
        dialog.destroy()

    def accept(self, dialog):
        new_values = '{}-{}-{}/{}-{}-{}/{}-{}-{}/  {}/{}/'.format(
                                           int(dialog.entry01.get_text())*1000,
                                           int(dialog.entry1.get_text())*1000,
                                           int(dialog.entry4.get_text())*1000,
                                           int(dialog.entry02.get_text())*1000,
                                           int(dialog.entry2.get_text())*1000,
                                           int(dialog.entry5.get_text())*1000,
                                           int(dialog.entry03.get_text())*1000,
                                           int(dialog.entry3.get_text())*1000,
                                           int(dialog.entry6.get_text())*1000,
                                           dialog.low_default, dialog.high_default)

        if config.has_option('PROCESSORS',MODEL_CPU):
            print('Processor values modified.')
            config.set('USER-CPU','cpu-parameters', new_values)

        else: 
            print('Processor added')
            config.set('PROCESSORS', MODEL_CPU, dialog.val)
            config.set('USER-CPU','cpu-parameters', new_values)
            print(config['PROCESSORS'][MODEL_CPU])

        with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)

def _create_gui_element(value, low, max):

    spin_button = Gtk.SpinButton()
    spin_button.set_adjustment(Gtk.Adjustment(
        value=value,
        lower=low,
        upper=max,
        step_incr=1,
        page_incr=10,
    ))

    spin_button.set_numeric(True)

    return spin_button

style_provider = Gtk.CssProvider()
style_provider.load_from_path(CURRENT_PATH+'/css/style.css')

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)
if __name__ == "__main__":
    Dialog()
    Gtk.main()
