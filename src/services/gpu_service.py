import pyamdgpuinfo
import subprocess
import re

from constants.gpu_constants import (
    REGEX_MODEL_WITH_MODEL_IN_BRACKETS_MATCH,
    REGEX_MODEL_WITH_MODEL_IN_BRACKETS_FINDALL,
    REGEX_MODEL_ONLY_SERIES_NAME_MATCH,
    REGEX_MODEL_ONLY_SERIES_NAME_FINDALL,
    UNKNOWN_MODEL,
)

class GpuService:
    index: int

    def __init__(self, index: int):
        self.index = index

    @staticmethod
    def exists_amd_gpus() -> bool:
        return GpuService.get_number_of_gpus() > 0

    @staticmethod
    def get_number_of_gpus() -> int:
        return pyamdgpuinfo.detect_gpus()

    def get_model(self) -> str:
        model= pyamdgpuinfo.get_gpu(self.index).name
        if model is not None:
            return model
        else:
            slot = pyamdgpuinfo.get_gpu(self.index).pci_slot[5:]
            lspci_output = subprocess.getstatusoutput("lspci | grep -i "+slot+" | cut -d ':' -f3")[1].strip()

            try:
                if re.match(REGEX_MODEL_WITH_MODEL_IN_BRACKETS_MATCH, lspci_output, re.MULTILINE) is not None:
                    matches = re.findall(REGEX_MODEL_WITH_MODEL_IN_BRACKETS_FINDALL, lspci_output, re.MULTILINE)
                    model = matches[1].replace('[', '').replace(']', '')
                elif re.match(REGEX_MODEL_ONLY_SERIES_NAME_MATCH, lspci_output, re.MULTILINE) is not None:
                    model = re.findall(REGEX_MODEL_ONLY_SERIES_NAME_FINDALL, lspci_output)[1]
            except Exception as e:
                print(e)

            if model is None:
                model = UNKNOWN_MODEL

            return model.strip()

    def get_vram(self) -> str:
        vram_size = GpuService._get_vram_size(self)
        return '{} {}'.format(GpuService._convert_bytes_to_mbytes(self, vram_size), 'MB')

    def get_vram_usage(self) -> str:
        vram_usage = pyamdgpuinfo.get_gpu(self.index).query_vram_usage()
        return '{} {}'.format(GpuService._convert_bytes_to_mbytes(self, vram_usage), 'MB')

    def get_temp(self) -> str:
        return '{} ºC'.format(pyamdgpuinfo.get_gpu(self.index).query_temperature())

    def get_slot(self) -> str:
        return pyamdgpuinfo.get_gpu(self.index).pci_slot

    def get_slck(self) -> str:
        sclk = GpuService._get_freq(self, 'S')
        return '{} MHz'.format(sclk)

    def get_mlck(self) -> str:
        mclk = GpuService._get_freq(self, 'M')
        return '{} MHz'.format(mclk)

    def get_gpu_voltage(self) -> str:
        try:
            voltage = pyamdgpuinfo.get_gpu(self.index).query_graphics_voltage()
            return '{} V'.format(round(voltage, 3))
        except:
            return '0 V'

    def _get_vram_size(self) -> str:
        return pyamdgpuinfo.get_gpu(self.index).memory_info['vram_size']

    def _get_mem_usage_size(self) -> str:
        return pyamdgpuinfo.get_gpu(self.index).query_vram_usage()

    def _get_freq(self, freq_type: str):
        freq = 0;
        if freq_type == 'S':
            freq = pyamdgpuinfo.get_gpu(self.index).query_sclk()
        elif freq_type == 'M':
            freq = pyamdgpuinfo.get_gpu(self.index).query_mclk()

        return round(float(freq)/1000.0**2)

    def _convert_bytes_to_gbytes(self, vram_size):
        return round(float(vram_size)/1024.0**3)

    def _convert_bytes_to_mbytes(self, vram_size):
        return round(float(vram_size)/1024.0**2)
