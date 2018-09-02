import tkinter as tk
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
from itertools import count
import csv
from optics.misc_utility.curve_fit_equations import linear_fit, linear

class KeithleyBreak:
    def __init__(self, window, sourcemeter, filepath, device, steps=11, stop_voltage=0.05, desired_resistance=80,
                 break_voltage=1.5, passes=1, increase_break_voltage=True, delta_break_voltage=0.005, start_voltage=.1,
                 delta_voltage=0.002, r_percent=.4, abort=False):




        # ready the device
        self._sourcemeter = sourcemeter
        self._sourcemeter.reset()
        self._sourcemeter.set_voltage(0)
        self._sourcemeter.configure_measurement()
        self._sourcemeter.configure_measurement(measurement_mode=0)
        self._sourcemeter.display_measurement(displayed_measurement_mode=1)
        self._sourcemeter.enable_output()
        self._sourcemeter.configure_measurement(measurement_mode=1, auto_range=False, manual_range=0.1)
        # set up the plots
        self._fig, (self._ax1, self._ax2, self._ax3) = plt.subplots(3)
        self._ax3.barh(1, 1, 0.35, color='w')
        self._ax1.title.set_text('Measured resistance: \nCurrent resistance: ')
        self._ax2.title.set_text('Breaking resistance: \nCurrent resistance: ')
        self._ax3.title.set_text('Percent of maximum current: ')
        self._ax3.set_xlim(0, 1)
        plt.tight_layout()
        self._fig.show()
        self._ln = None
        # create the filename
        os.makedirs(filepath, exist_ok=True)
        self._j = count(0)
        self._filename = os.path.join(filepath, '{}_k2400break_'.format(device))
        while os.path.exists(self._filename + '0.csv'):
            self._filename = self._filename + '1'
        # create the status tools
        self._abort = abort
        self._current_dropped = False
        self._message = 'Unknown error'
        # set the class variables
        self._sweep_resistance = 0
        self._desired_resistance = desired_resistance
        self._wait_time = 0.1
        self._writer = None
        self._break_voltage = break_voltage
        self._passes = passes
        self._increase_break_voltage = increase_break_voltage
        self._delta_break_voltage = delta_break_voltage
        self._start_voltage = start_voltage
        self._delta_voltage = delta_voltage
        self._r_percent = r_percent
        self._c = count(0)
        self._stop_voltage = stop_voltage
        self._steps = steps

        self._frame = frame

    def measure_resistance(self):
        values = np.zeros((self._steps+1, 2))
        for n, i in enumerate(np.linspace(0, self._stop_voltage, self._steps+1)):
            self._sourcemeter.set_voltage(i)
            v, j, _, _, _ = self._sourcemeter.read_points()
            values[n] = v, j
            self._frame.after(self._wait_time, self._ax1.scatter(i, j))
            self._ax1.set_ylim(np.amin(values[:, 1]) * 0.9, np.amax(values[:, 1]) * 1.1)
            self._ax1.title.set_text('Measuring resistance\nCurrent resistance: %s ohms' % np.ceil(i / j))
            self._fig.canvas.draw()
        self._sourcemeter.set_voltage(0)
        m, b, _, _ = linear_fit(values[:, 0], values[:, 1])
        self._sweep_resistance = 1/m
        self._writer.writerow([self._sweep_resistance])
        linspace = np.linspace(np.amin(values[:, 0]), np.amax(values[:, 0]), 100)
        self._ln, = self._ax1.plot(linspace, linear(linspace, m, b))
        self._ax1.title.set_text('Measured resistance: %s ohms\n ' % np.ceil(self._sweep_resistance))
        self._fig.canvas.draw()
        self.check_status()
