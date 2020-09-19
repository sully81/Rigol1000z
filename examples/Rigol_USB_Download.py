import visa
# visa.log_to_screen()
import rigol1000z
import matplotlib.pyplot as plt
import time
import numpy as np
import os
import shutil
import create_thd
import windows_sleep_inhibit as inihibit
from datetime import datetime

def curr_probe_cal(slope, offset, val):
    return np.array(val) * slope + offset

probe_cal_slope = 3.258  # measured against a fluke multimeter
probe_cal_offset = -0.1202556871

# The following lines of code prevent windows from going to sleep
osSleep = None
# in Windows, prevent the OS from sleeping while we run
if os.name == 'nt':
    osSleep = inihibit.WindowsInhibitor()
    osSleep.inhibit()

sample_rate = 200000  # sample rate of the oscilloscope in Hz
record_time_length = 240.0  # time duration of the recording.  This should be set to the total time length of the scope's memory.
record_time_delay = 2.0  # time delay before starting the waveform test in canape

rm = visa.ResourceManager()
print("resources = ", rm.list_resources())
scope_resource = rm.open_resource(rm.list_resources()[1])
print("oscilloscope = ", scope_resource)
scope = rigol1000z.Rigol1000z(scope_resource)
# scope.run()
# scope[1].set_vertical_scale_V(0.1)
# # scope[1].set_offset_V(-0.03)
# scope.set_memory_depth(12e6)
# scope.timebase = 20

# scope.stop()
# time.sleep(0.5)




time_start_download = time.time()
dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%d-%b-%Y_%H-%M-%S")

output_filename = 'ScopeDownload' + '_' + timestampStr + '.thd'

# waveform_y = np.array(scope.get_waveform_samples(1, mode='RAW')) * scale_factor
# waveform_x = np.array(scope.waveform_time_values)
waveform_x, waveform_y = scope[1].get_data('raw')
waveform_x1, waveform_y1 = scope[2].get_data('raw')

# convert from measured volts to amps
# scale_factor = 10.0 / 3.0  # convert from Volts to Amps (wire is looped 3 time through clamp)
# waveform_y = waveform_y * scale_factor
waveform_y = curr_probe_cal(probe_cal_slope, probe_cal_offset, waveform_y)

time_download_complete = time.time()
print("time to download: ", time_download_complete - time_start_download)

create_thd.create_thd(output_filename, sample_rate, [waveform_y, waveform_y1],
                      ['act_curr', 'pwm_dc'])

# cwd = os.getcwd()
# batchManager_folder = r"C:\Users\SulliPW\datk\pro\batchManager"
# os.chdir(batchManager_folder)
# os.system("batchManager.bat")
# os.chdir(cwd)

if osSleep:
    osSleep.uninhibit()

scope_resource.close()