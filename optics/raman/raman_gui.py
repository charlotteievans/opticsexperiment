import ctypes
co_initialize = ctypes.windll.ole32.CoInitialize
import tkinter as tk
co_initialize(None)
from optics.hardware_control.ccd_controller import CCDController2
from optics.hardware_control.mono_controller import MonoController
from optics.raman.single_spectrum import BaseRamanMeasurement
from optics.raman.raman_time import RamanTime
from optics.raman.raman_voltage_waterfall import RamanVoltageWaterfall
from optics.raman.raman_polarization import RamanPolarization
from optics.raman.raman_map import RamanMapScan
from optics.gui.base_gui import BaseGUI
import time
from optics.raman import unit_conversions
from optics.under_development.sandbox import RamanLockinOutgoingPolarizationSweepBias


class RamanGUI(BaseGUI):
    def __init__(self, master, mono, ccd_controller, sr7270_single_reference, sr7270_dual_harmonic, waveplate,
                 powermeter, npc3sg_input, npc3sg_x, npc3sg_y, raman_gain, center_wavelength, grating, polarizer):
        self._master = master
        super().__init__(self._master)
        self._mono = mono
        self._ccd_controller = ccd_controller
        #self._raman_gain = self._ccd_controller.read_gain()
        #self._grating = self._mono.get_current_turret()[1]
        self._shutter = tk.StringVar()
        self._shutter.set('True')
        #self._center_wavelength = self._mono.read_wavelength()
        self._raman_gain = raman_gain
        self._center_wavelength = center_wavelength
        self._grating = grating
        self._units = tk.StringVar()
        self._units.set('cm^-1')
        self._darkcurrent = tk.StringVar()
        self._dark_corrected = tk.StringVar()
        self._dark_corrected.set('False')
        self._darkcurrent.set('False')
        self._sr7270_single_reference = sr7270_single_reference
        self._sr7270_dual_harmonic = sr7270_dual_harmonic
        self._powermeter = powermeter
        self._waveplate = waveplate
        self._npc3sg_input = npc3sg_input
        self._npc3sg_x = npc3sg_x
        self._npc3sg_y = npc3sg_y
        self._polarizer = polarizer

    def build_single_spectrum_gui(self):
        caption = "Single Raman spectrum"
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'integration time (s)': 1,
                        'acquisitions to average': 1}
        self.beginform(caption)
        self.make_option_menu('shutter open', self._shutter, ['True', 'False'])
        self.make_option_menu('units', self._units, ['cm^-1', 'nm', 'eV'])
        self.make_option_menu('dark current', self._darkcurrent, ['True', 'False'])
        self.make_option_menu('subtract background', self._dark_corrected, ['True', 'False'])
        self.endform(self.single_spectrum)

    def build_spectrum_map_gui(self):
        caption = 'Raman map'
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'integration time (s)': 1,
                        'acquisitions to average': 1, 'x pixel density': 10, 'y pixel density': 10, 'x range': 160,
                        'y range': 160, 'x center': 80, 'y center': 80}

    def single_spectrum(self, event=None):
        self.fetch(event)
        run = BaseRamanMeasurement(tk.Toplevel(self._master), self._ccd_controller, self._grating, self._raman_gain,
                                   self._center_wavelength, self._units.get(),
                                   float(self._inputs['integration time (s)']),
                                   int(self._inputs['acquisitions to average']),
                                   self.string_to_bool(self._shutter.get()),
                                   self.string_to_bool(self._darkcurrent.get()),
                                   self.string_to_bool(self._dark_corrected.get()), self._inputs['device'],
                                   self._inputs['file path'], self._fields['notes'],
                                   int(self._fields['scan']), waveplate=self._waveplate, powermeter=self._powermeter)
        run.main()

    def build_time_spectrum_gui(self):
        caption = 'Raman time waterfall spectrum'
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'integration time (s)': 1,
                        'acquisitions to average': 1, 'number of scans': 60, 'wait time between scans (s)': 1,
                        'start wavelength': '', 'stop wavelength': ''}
        self.beginform(caption)
        self.make_option_menu('shutter open', self._shutter, ['True', 'False'])
        self.make_option_menu('units', self._units, ['cm^-1', 'nm', 'eV'])
        self.make_option_menu('dark current', self._darkcurrent, ['True', 'False'])
        self.make_option_menu('subtract background', self._dark_corrected, ['True', 'False'])
        self.endform(self.time_spectrum)

    def time_spectrum(self, event=None):
        self.fetch(event)
        run = RamanTime(tk.Toplevel(self._master), self._ccd_controller, self._grating, self._raman_gain,
                                 self._center_wavelength, self._units.get(),
                                 float(self._inputs['integration time (s)']),
                                 int(self._inputs['acquisitions to average']),
                                 self.string_to_bool(self._shutter.get()),
                                 self.string_to_bool(self._darkcurrent.get()),
                                 self.string_to_bool(self._dark_corrected.get()), self._inputs['device'],
                                 self._inputs['file path'], self._fields['notes'],
                                 int(self._inputs['scan']), float(self._inputs['wait time between scans (s)']),
                                 int(self._inputs['number of scans']), float(self._inputs['start wavelength']),
                                 float(self._inputs['stop wavelength']), self._waveplate, self._powermeter,
                                 self._npc3sg_input)
        run.main()

    def build_voltage_waterfall_gui(self):
        caption = 'Raman vs. Applied voltage waterfall spectrum'
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'integration time (s)': 1,
                        'acquisitions to average': 1, 'number of scans': 60,
                        'start voltage (mV)': -100, 'stop voltage (mV)': 100, 'wait time between scans (s)': 1, }
        self.beginform(caption)
        self.make_option_menu('shutter open', self._shutter, ['True', 'False'])
        self.make_option_menu('units', self._units, ['cm^-1', 'nm', 'eV'])
        self.make_option_menu('dark current', self._darkcurrent, ['True', 'False'])
        self.make_option_menu('subtract background', self._dark_corrected, ['True', 'False'])
        self.endform(self.voltage_waterfall)

    def voltage_waterfall(self, event=None):
        self.fetch(event)
        run = RamanVoltageWaterfall(tk.Toplevel(self._master), self._ccd_controller, self._sr7270_dual_harmonic,
                                    self._grating, self._raman_gain,
                                    self._center_wavelength, self._units.get(),
                                    float(self._inputs['integration time (s)']),
                                    int(self._inputs['acquisitions to average']),
                                    self.string_to_bool(self._shutter.get()),
                                    self.string_to_bool(self._darkcurrent.get()),
                                    self.string_to_bool(self._dark_corrected.get()), self._inputs['device'],
                                    self._inputs['file path'], self._fields['notes'],
                                    int(self._inputs['scan']), float(self._inputs['wait time between scans (s)']),
                                    int(self._inputs['number of scans']), float(self._inputs['start voltage (mV)']),
                                    float(self._inputs['stop voltage (mV)']), waveplate=self._waveplate, powermeter=self._powermeter)
        run.main()

    def build_polarization_spectrum_gui(self):
        caption = 'Raman vs. laser polarization spectrum'
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'integration time (s)': 1,
                        'acquisitions to average': 1, 'start wavelength': '', 'stop wavelength': '',
                        'wait time between scans (s)': 1, 'polarization spacing': 1}
        self.beginform(caption)
        self.make_option_menu('shutter open', self._shutter, ['True', 'False'])
        self.make_option_menu('units', self._units, ['cm^-1', 'nm', 'eV'])
        self.make_option_menu('dark current', self._darkcurrent, ['True', 'False'])
        self.make_option_menu('subtract background', self._dark_corrected, ['True', 'False'])
        self.endform(self.polarization_spectrum)

    def polarization_spectrum(self, event=None):
        self.fetch(event)
        run = RamanPolarization(tk.Toplevel(self._master), self._ccd_controller, self._grating,
                                         self._raman_gain, self._center_wavelength, self._units.get(),
                                         float(self._inputs['integration time (s)']),
                                         int(self._inputs['acquisitions to average']),
                                         self.string_to_bool(self._shutter.get()),
                                         self.string_to_bool(self._darkcurrent.get()),
                                         self.string_to_bool(self._dark_corrected.get()), self._inputs['device'],
                                         self._inputs['file path'], self._fields['notes'],
                                         int(self._inputs['scan']), float(self._inputs['wait time between scans (s)']),
                                         float(self._inputs['polarization spacing']), float(self._inputs['start wavelength']),
                                float(self._inputs['stop wavelength']), self._waveplate, self._powermeter,
                                         self._npc3sg_input)
        run.main()

    def build_raman_map_gui(self):
        caption = 'Raman map'
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'integration time (s)': 1,
                        'acquisitions to average': 1, 'start wavelength': '', 'stop wavelength': '',
                        'wait time between scans (s)': 1, 'xd': 10, 'yd': 10,
                        'xr': 160, 'yr': 160, 'xc': 80, 'yc': 80}
        self.beginform(caption)
        self.make_option_menu('shutter open', self._shutter, ['True', 'False'])
        self.make_option_menu('units', self._units, ['cm^-1', 'nm', 'eV'])
        self.make_option_menu('dark current', self._darkcurrent, ['True', 'False'])
        self.make_option_menu('subtract background', self._dark_corrected, ['True', 'False'])
        self.endform(self.polarization_spectrum)

    def raman_map(self, event=None):
        self.fetch(event)
        run = RamanMapScan(tk.Toplevel(self._master), self._ccd_controller, self._grating,
                                         self._raman_gain, self._center_wavelength, self._units.get(),
                                         float(self._inputs['integration time (s)']),
                                         int(self._inputs['acquisitions to average']),
                                         self.string_to_bool(self._shutter.get()),
                                         self.string_to_bool(self._darkcurrent.get()),
                                         self.string_to_bool(self._dark_corrected.get()), self._inputs['file path'], self._fields['notes'],
                           self._inputs['device'],
                                         int(self._inputs['scan']), int(self._inputs['xd']),
                           int(self._inputs['yd']), int(self._inputs['xr']), int(self._inputs['yr']),
                           int(self._inputs['xc']), int(self._inputs['yc']),
                            self._npc3sg_x, self._npc3sg_y,
                           self._npc3sg_input, float(self._inputs['start wavelength']),
                                float(self._inputs['stop wavelength']), float(self._inputs['wait time between scans (s)']), self._powermeter,
                           self._waveplate, True)
        run.main()

    def build_bias_light_emission_gui(self):
        print(self._polarizer)
        caption = 'Bias polarization light emission measurement'
        self._fields = {'file path': "", 'device': "", 'scan': 0, 'notes': "", 'integration time (s)': 1,
                        'acquisitions to average': 1, 'start wavelength': '', 'stop wavelength': '',
                        'wait time (ms)': 10, 'start bias (mV)': 0, 'stop bias (mV)': 1000, 'bias steps': 10,
                        'osc (mV)': 7, 'polarization steps': 50, 'lock in measurements to average': 1,
                        'amplifier gain': 1000}
        self.beginform(caption)
        self.make_option_menu('units', self._units, ['cm^-1', 'nm', 'eV'])
        self.make_option_menu('dark current', self._darkcurrent, ['True', 'False'])
        self.make_option_menu('subtract background', self._dark_corrected, ['True', 'False'])
        self.endform(self.biaslightemission)

    def biaslightemission(self, event=None):
        self.fetch(event)
        run = RamanLockinOutgoingPolarizationSweepBias(tk.Toplevel(self._master), self._inputs['file path'],
                                                       self._inputs['notes'], self._inputs['device'],
                                                       int(self._inputs['scan']), int(self._inputs['amplifier gain']),
                                                       float(self._inputs['start bias (mV)']),
                                                       float(self._inputs['stop bias (mV)']),
                                                       int(self._inputs['bias steps']), float(self._inputs['osc (mV)']),
                                                       self._npc3sg_input, self._sr7270_dual_harmonic,
                                                       self._sr7270_single_reference,
                                                       self._powermeter, self._waveplate,
                                                       int(self._inputs['polarization steps']),
                                                       self._polarizer,
                                                       int(self._inputs['lock in measurements to average']),
                                                       float(self._inputs['wait time (ms)']), self._ccd_controller,
                                                       float(self._inputs['integration time (s)']),
                                                       self._raman_gain, int(self._inputs['acquisitions to average']),
                                                       self._units.get(),
                                                       self._grating, self._center_wavelength,
                                                       float(self._inputs['start wavelength']),
                                                       float(self._inputs['stop wavelength']),
                                                       self.string_to_bool(self._darkcurrent.get()),
                                                       self.string_to_bool(self._dark_corrected.get()))
        run.main()


class RamanBaseGUI(BaseGUI):
    def __init__(self, master, sr7270_single_reference=None, sr7270_dual_harmonic=None, waveplate=None, powermeter=None,
                 npc3sg_input=None, npc3sg_x=None, npc3sg_y=None, polarizer=None):
        self._master = master
        super().__init__(self._master)
        self._master.title('Optics Raman setup measurements')
        print('connecting Raman hardware (approx. 30 seconds)')
        self._mono = MonoController()
        print('MonoControl Success')
        self._ccd_controller = CCDController2()
        print('Raman hardware connection complete')
        self._gain = self._ccd_controller.read_gain()
        self._gain_options = tk.StringVar()
        gain_options = {0: 'high light', 1: 'best dynamic range', 2: 'high sensitivity'}
        self._gain_options.set(gain_options[self._gain])
        _, self._current_grating, _, _ = self._mono.get_current_turret()
        self._grating = tk.StringVar()
        self._newWindow = None
        self._app = None
        self._width = tk.StringVar()
        self._center_wavelength = self._mono.read_wavelength()
        self._sr7270_single_reference = sr7270_single_reference
        self._sr7270_dual_harmonic = sr7270_dual_harmonic
        self._waveplate = waveplate
        self._powermeter = powermeter
        self._npc3sg_input = npc3sg_input
        self._npc3sg_x = npc3sg_x
        self._npc3sg_y = npc3sg_y
        self._units = tk.StringVar()
        self._units.set('nm')
        self._polarizer = polarizer

    def new_window(self, measurementtype):
        self._newWindow = tk.Toplevel(self._master)
        self._app = RamanGUI(self._newWindow, self._mono, self._ccd_controller, self._sr7270_single_reference,
                             self._sr7270_dual_harmonic, self._waveplate, self._powermeter, self._npc3sg_input,
                             self._npc3sg_x, self._npc3sg_y, self._gain, self._center_wavelength, self._current_grating, self._polarizer)
        measurement = {'singlespectrum': self._app.build_single_spectrum_gui,
                       'timespectrum': self._app.build_time_spectrum_gui,
                       'voltagewaterfall': self._app.build_voltage_waterfall_gui,
                       'polarizationspectrum': self._app.build_polarization_spectrum_gui,
                       'ramanmap': self._app.build_raman_map_gui,
                       'biaslightemission': self._app.build_bias_light_emission_gui}
        measurement[measurementtype]()

    def build(self):
        row = self.makerow('Raman measurements')
        self.make_measurement_button(row, 'single spectrum', 'singlespectrum')
        self.make_measurement_button(row, 'time', 'timespectrum')
        self.make_measurement_button(row, 'polarization', 'polarizationspectrum')
        row = self.makerow('Raman waterfall measurements')
        self.make_measurement_button(row, 'voltage', 'voltagewaterfall')
        self.make_measurement_button(row, 'map', 'ramanmap')
        row = self.makerow('Light emission')
        self.make_measurement_button(row, 'bias polarization', 'biaslightemission')
        row = self.makerow('change paramaters')
        b1 = tk.Button(row, text='Raman gain',
                       command=self.change_gain_gui)
        b1.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        b = tk.Button(row, text='grating', command=self.change_grating_gui)
        b.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        b = tk.Button(row, text='slit width', command=self.change_slit_width_gui)
        b.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        b = tk.Button(row, text='center wavelength', command=self.change_center_wavelength_gui)
        b.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        b12 = tk.Button(self._master, text='Quit all windows', command=self._master.destroy)
        b12.pack()

    def to_bool(self, s):
        if s == 'True':
            return True
        else:
            return False

    def change_gain_gui(self):
        self._newWindow = tk.Toplevel(self._master)
        self._newWindow.title('Change Raman gain')
        label = tk.Label(self._newWindow, text='Change Raman gain')
        label.pack()
        gain_options = {0: 'high light', 1: 'best dynamic range', 2: 'high sensitivity'}
        self._gain_options.set(gain_options[self._gain])
        row = tk.Frame(self._newWindow)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab = tk.Label(row, width=15, text='gain', anchor='w')
        lab.pack(side=tk.LEFT)
        t = tk.OptionMenu(row, self._gain_options, *['high light', 'best dynamic range', 'high sensitivity'])
        t.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        self._newWindow.bind('<Return>', self.change_gain)
        self.makebutton('Run', self.change_gain, master=self._newWindow)
        self.makebutton('Quit', self._newWindow.destroy, master=self._newWindow)

    def change_gain(self):
        gain_options = {'high light': 0, 'best dynamic range': 1, 'high sensitivity': 2}
        self._gain = float(gain_options[self._gain_options.get()])
        self._ccd_controller.set_gain(self._gain)
        print('Raman gain set to {}'.format(self._gain_options.get()))

    def change_grating_gui(self):
        self._newWindow = tk.Toplevel(self._master)
        self._newWindow.title('Change Raman grating')
        label = tk.Label(self._newWindow, text='Change Raman grating')
        label.pack()
        self._grating.set(int(self._current_grating))
        row = tk.Frame(self._newWindow)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab = tk.Label(row, width=15, text='grating', anchor='w')
        lab.pack(side=tk.LEFT)
        t = tk.OptionMenu(row, self._grating, *[1200, 300, 150])
        t.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        self._newWindow.bind('<Return>', self.change_grating)
        self.makebutton('Run', self.change_grating, master=self._newWindow)
        self.makebutton('Quit', self._newWindow.destroy, master=self._newWindow)

    def change_grating(self):
        grating_options = {'1200': 0, '300': 1, '150': 2}
        turret, self._current_grating, blazes, description = self._mono.set_turret(
            int(grating_options[self._grating.get()]))
        now = time.time()
        while self._mono.is_busy():
            print('Moving turret')
            time.sleep(10)
            if time.time() > now + 120:
                print('Mono timeout')
                print('Restart connection')
                break
        print('Turret movement complete')
        print('Current turret: {}\nCurrent grating: {}\nCurrent blazes: {}'
              '\nCurrent description {}'.format(turret, self._current_grating, blazes, description))

    def change_slit_width_gui(self):
        self._newWindow = tk.Toplevel(self._master)
        self._newWindow.title('Change slit width')
        self._fields = {'slit width': self._mono.read_front_slit_width()}
        self.beginform('Change slit width', True, self._newWindow)
        self.makebutton('Run', self.change_slit_width, master=self._newWindow)
        self.makebutton('Quit', self._newWindow.destroy, master=self._newWindow)

    def change_slit_width(self, event=None):
        self.fetch(event)
        self._mono.set_front_slit_width(float(self._inputs['slit width']))
        while self._mono.is_busy():
            time.sleep(0.1)
        print('Front slit width changed to {}'.format(self._mono.read_front_slit_width()))

    def change_center_wavelength_gui(self):
        self._newWindow = tk.Toplevel(self._master)
        self._newWindow.title('Change center wavelength')
        self._fields = {'Center wavelength': self._center_wavelength}
        self.beginform('Change center wavelength', False, self._newWindow)
        self.make_option_menu('units', self._units, ['cm^-1', 'nm', 'eV'], master=self._newWindow)
        self.makebutton('Run', self.change_center_wavelength, master=self._newWindow)
        self.makebutton('Quit', self._newWindow.destroy, master=self._newWindow)

    def change_center_wavelength(self, event=None):
        self.fetch(event)
        unit = self._units.get()
        self._center_wavelength = float(self._inputs['Center wavelength'])
        if unit == 'cm^-1':
            self._center_wavelength = unit_conversions.convert_wavenumber_to_nm(self._center_wavelength)
        if unit == 'eV':
            self._center_wavelength = unit_conversions.convert_ev_to_nm(self._center_wavelength)
        self._mono.set_wavelength(self._center_wavelength)
        now = time.time()
        while self._mono.is_busy():
            if time.time() > now + 30:
                print('timed out')
                break
            time.sleep(1)
            print('monochrometer moving to center position')
        wavelength = self._mono.read_wavelength()
        print('Center wavelength set to {} nm, \n {} cm^-1, \n {} eV'.format(wavelength,
                                                                       unit_conversions.convert_nm_to_wavenumber(wavelength),
                                                                       unit_conversions.convert_nm_to_ev(wavelength)))




