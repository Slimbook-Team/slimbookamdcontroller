MODEL = 'Model'
VRAM = 'VRAM'
VRAM_USAGE = 'VRAM Usage'
TEMP = 'Temp'
GPU_FREQ = 'GPU Freq'
MEM_FREQ = 'Mem Freq'
PCI_SLOT = 'PCI Slot'
GPU_VOLT = 'GPU Voltage'

DYNAMIC_GPU_PROPERTIES = [TEMP, GPU_FREQ, MEM_FREQ, VRAM_USAGE, GPU_VOLT]

UNKNOWN_MODEL = 'Unknown model'

REGEX_MODEL_WITH_MODEL_IN_BRACKETS_MATCH = r"Advanced\sMicro\sDevices,\sInc\..\[AMD\/ATI\]\s[a-zA-Z0-9\/\s]+\s\[[a-zA-Z0-9\s\/]+\]"
REGEX_MODEL_WITH_MODEL_IN_BRACKETS_FINDALL = r"\s\[[a-zA-Z0-9\s\/]+\]"

REGEX_MODEL_ONLY_SERIES_NAME_MATCH = r"Advanced\sMicro\sDevices,\sInc\..\[AMD\/ATI\]\s[a-zA-Z0-9\s\/]+\s\([a-zA-Z0-9\s\/]+\)"
REGEX_MODEL_ONLY_SERIES_NAME_FINDALL = r"\s[a-zA-Z0-9\s\/]+\s"