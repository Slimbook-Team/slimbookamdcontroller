import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GLib
import utils
APPNAME = 'slimbookamdcontroller'
_ = utils.load_translation(APPNAME)

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np

try:
    from services.gpu_service import GpuService
except:
    pass
from constants.gpu_constants import DYNAMIC_GPU_PROPERTIES, GPU_FREQ, GPU_VOLT, MEM_FREQ, MODEL, TEMP, VRAM, VRAM_USAGE


class GpuSection():
    def __init__(self, notebook):
        self.notebook = notebook
        self._optionSelected = 'temp'
        self._isOptionChanged = False
        self._x_array = []
        self._y_array = []

    def get_x_array(self):
        return self._x_array

    def get_y_array(self):
        return self._y_array

    def set_x_array(self, x_array):
        self._x_array = x_array

    def set_y_array(self, y_array):
        self._y_array = y_array

    def add(self):
        try:
            if GpuService.exists_amd_gpus():
                self.notebook = self.__add_gpus_pages()
        except NameError:
            print(NameError)
        finally:
            return self.notebook

    def __add_gpus_pages(self):
        number_of_gpus = GpuService.get_number_of_gpus()
        for gpu_index in range(number_of_gpus):
            page = Gtk.Box()
            page.set_border_width(10)
            page.set_halign(Gtk.Align.CENTER)
            box = self.__build_gpu_listbox(gpu_index)
            page.add(box)
            self.notebook.append_page(page, Gtk.Label(
                label="GPU {}".format(gpu_index)))
        return self.notebook

    def __update_label(self, label: Gtk.Label, serviceFunction):
        label.set_label(serviceFunction())
        return True


    def __build_gpu_listbox(self, gpu_index: int) -> Gtk.Grid:
        gpu = GpuService(gpu_index)

        GPU_INFO = {
            MODEL: gpu.get_model(),
            VRAM: gpu.get_vram(),
            VRAM_USAGE: gpu.get_vram_usage(),
            TEMP: gpu.get_temp(),
            GPU_FREQ: gpu.get_slck(),
            MEM_FREQ: gpu.get_mlck(),
            GPU_VOLT: gpu.get_gpu_voltage()
        }

        grid = Gtk.Grid(column_homogeneous=True, column_spacing=6, row_spacing=6)

        for index, key in enumerate(GPU_INFO):
            hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            hbox_context = hbox.get_style_context()
            hbox_context.add_class('box-gpu-property')

            hbox.pack_start(Gtk.Label(label=_(key), xalign=0), True, True, 1)

            label = Gtk.Label(label=GPU_INFO[key], xalign=0)

            if self.__is_dynamic_property(key):
                serviceFunction = None
                if key == TEMP:
                    serviceFunction = gpu.get_temp
                elif key == GPU_FREQ:
                    serviceFunction = gpu.get_slck
                elif key == MEM_FREQ:
                    serviceFunction = gpu.get_mlck
                elif key == GPU_VOLT:
                    serviceFunction = gpu.get_gpu_voltage
                else:
                    serviceFunction = gpu.get_vram_usage
                GLib.timeout_add_seconds(2, self.__update_label, label, serviceFunction)

            hbox.pack_start(label, expand = True, fill = True, padding = 1)
            grid.attach(hbox, 0, index, 1, 1)

        grid.attach(self.__radio_buttons(), 1, 0, 1, 1)

        canvas = self.__renderChart(gpu)
        box_canvas = Gtk.Box()
        box_canvas.add(canvas)
        grid.attach(box_canvas, 1, 1, 1, 6)

        return grid

    def __radio_buttons(self):
        radio_buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        radio_buttons_box.set_halign(Gtk.Align.CENTER)

        button1 = Gtk.RadioButton.new_with_label_from_widget(None, "ºC")
        button1.connect("toggled", self.on_button_toggled, "temp")
        radio_buttons_box.pack_start(button1, False, False, 0)

        button2 = Gtk.RadioButton.new_from_widget(button1)
        button2.set_label("GPU")
        button2.connect("toggled", self.on_button_toggled, "gpuclk")
        radio_buttons_box.pack_start(button2, False, False, 0)

        button3 = Gtk.RadioButton.new_with_mnemonic_from_widget(button1, "Mem")
        button3.connect("toggled", self.on_button_toggled, "memclk")
        radio_buttons_box.pack_start(button3, False, False, 0)

        button4 = Gtk.RadioButton.new_with_mnemonic_from_widget(button1, "Volt")
        button4.connect("toggled", self.on_button_toggled, "gpuvolt")
        radio_buttons_box.pack_start(button4, False, False, 0)

        button5 = Gtk.RadioButton.new_with_mnemonic_from_widget(button1, "RAM")
        button5.connect("toggled", self.on_button_toggled, "vramusage")
        radio_buttons_box.pack_start(button5, False, False, 0)

        return radio_buttons_box

    def __is_dynamic_property(self, key):
        if key in DYNAMIC_GPU_PROPERTIES:
            return True
        return False

    def on_button_toggled(self, button, name):
        self._optionSelected = name
        self._isOptionChanged = True

    def __renderChart(self, gpu: GpuService) -> FigureCanvas:
        fig = Figure(figsize=(5, 4), dpi=100, )
        fig.patch.set_alpha(0.0)
        fig.set_tight_layout({"pad": .0})

        ax = fig.add_subplot()
        self.__setAxStyle(ax)

        GLib.timeout_add_seconds(1, self.__update_plot, gpu, ax)

        canvas = FigureCanvas(fig)
        canvas.set_size_request(400, 200)
        GLib.timeout_add_seconds(1, self.__drawCanvas, canvas )
        return canvas

    def __setAxStyle(self, ax):
        ax.set_facecolor('blue')
        ax.patch.set_alpha(0.1)
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_xticklabels([])
        ax.set_xticks([])
        ax.set_ylim(bottom=0)
        ax.set_ylim(top=self.__get_max_value())
        return True

    def  __update_plot(self, gpu: GpuService, ax):
        if self._isOptionChanged:
            self._isOptionChanged = False
            self._x_array = []
            self._y_array = []

        if len(self._x_array) > 0:
            self._x_array.append(self._x_array[-1] + 1)
        else:
            self._x_array.append(0)

        if self._optionSelected == "temp":
            self._y_array.append( float(gpu.get_temp().split(' ºC')[0]) )
        elif self._optionSelected == "gpuclk":
            self._y_array.append( float(gpu.get_slck().split(' MHz')[0]) )
        elif self._optionSelected == "memclk":
            self._y_array.append( float(gpu.get_mlck().split(' MHz')[0]) )
        elif self._optionSelected == "gpuvolt":
            self._y_array.append( float(gpu.get_gpu_voltage().split(' V')[0]) )
        elif self._optionSelected == "vramusage":
            self._y_array.append( float(gpu.get_vram_usage().split(' MB')[0]) )

        self.__clean_old_array_values()
        ax.cla()
        self.__setAxStyle(ax)
        ax.plot(self._x_array, self._y_array, '#641515')
        return True

    def __clean_old_array_values(self):
        if len(self._x_array) > 7 and len(self._y_array) > 7:
            self._x_array = self._x_array[1:]
            self._y_array = self._y_array[1:]
        return

    def __get_max_value(self):
        max_value = 0
        if len(self._y_array) > 0:
            max_value = np.max(self._y_array)
        if self._optionSelected == "temp":
            return max_value + 10
        return max_value + 200

    def __drawCanvas(self, canvas):
        canvas.draw()
        return True