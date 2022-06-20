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

try:
    from services.gpu_service import GpuService
except:
    pass
from constants.gpu_constants import DYNAMIC_GPU_PROPERTIES, GPU_FREQ, GPU_VOLT, MEM_FREQ, MODEL, TEMP, VRAM, VRAM_USAGE


class GpuSection():
    def __init__(self, notebook):
        self.notebook = notebook

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
            page.set_halign(Gtk.Align.START)
            box = self.__build_gpu_listbox(gpu_index)
            page.add(box)
            self.notebook.append_page(page, Gtk.Label(
                label="GPU {}".format(gpu_index)))
        return self.notebook

    def __update_label(self, label: Gtk.Label, serviceFunction):
        label.set_label(serviceFunction())
        return True


    def __build_gpu_listbox(self, gpu_index: int) -> Gtk.Box:
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

        box_outer = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(listbox, True, True, 0)

        for key in GPU_INFO:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL, spacing=1)
            hbox_context = hbox.get_style_context()
            hbox_context.add_class('box-gpu-property')
            row.add(hbox)

            hbox.pack_start(Gtk.Label(label=_(key), xalign=0), True, True, 0)

            label = Gtk.Label(label=GPU_INFO[key], xalign=0)

            if key in DYNAMIC_GPU_PROPERTIES:
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

            hbox.pack_start(label, True, True, 0)
            listbox.add(row)

        canvas = self.__renderChart(gpu)
        box_outer.add(canvas)

        return box_outer

    def __renderChart(self, gpu: GpuService) -> FigureCanvas:
        fig = Figure(figsize=(5, 4), dpi=100, )
        fig.patch.set_alpha(0.0)

        ax = fig.add_subplot()
        self.__setAxStyle(ax)

        x_array = [0]
        y_array = [0]
        GLib.timeout_add_seconds(2, self.__update_plot, gpu, ax, x_array, y_array)
        ax.plot(x_array, y_array, '#641515')

        canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
        canvas.set_size_request(400, 200)
        # canvas.draw()
        GLib.timeout_add_seconds(2, self.__drawCanvas, canvas )
        return canvas

    def __setAxStyle(self, ax):
        ax.set_facecolor('blue')
        ax.patch.set_alpha(0.1)
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_xticklabels([])
        ax.set_xticks([])
        return True

    def  __update_plot(self, gpu: GpuService, ax, x_array, y_array):
        x_array.append( x_array[len(x_array)-1]+1 )

        y_array.append( float(gpu.get_temp().split(' ºC')[0]) )
        ax.cla()
        self.__setAxStyle(ax)
        ax.plot(x_array, y_array, '#641515')
        return True

    def __drawCanvas(self, canvas):
        canvas.draw()
        return True