import cmath
import sys

import pyaudio

import numpy as np
import skimage.measure 
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg

from pprint import pprint


INPUT_FRAMES_PER_BLOCK = 4086
max_freq = 1000
min_freq = 0
ALPHA = 0.5
pool_factor = 32
RATE = 44100
Y_MIN = 0
Y_MAX = 2.5
X = 50
Y = 50
WAVE_HEIGHT = 7

# shamelessly adapted from here: https://stackoverflow.com/a/4160733    
class Visualizer(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.errorcount = 0
        self.noisycount = 0

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )
            device_index = 7

        return device_index

    def open_mic_stream( self ):
        device_index = self.find_input_device()

        stream = self.pa.open(   format = pyaudio.paInt32,
                                 channels = 1,
                                 rate = RATE,
                                 input = True,
                                 # input_device_index = device_index,
                                 frames_per_buffer =  INPUT_FRAMES_PER_BLOCK)
        return stream

    def tapDetected(self):
        print("Tap!")

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except:
            # dammit. 
            self.errorcount += 1
            # print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.noisycount = 1
            return 
        return block

class Plot2D():
    def __init__(self):
        self.traces = dict()

        #QtGui.QApplication.setGraphicsSystem('raster')
        self.app = pg.mkQApp()
        self.view = gl.GLViewWidget()
        self.view.show()

        self.xgrid = gl.GLGridItem()
        self.ygrid = gl.GLGridItem()
        self.zgrid = gl.GLGridItem()

        self.xgrid.rotate(90, 0, 1, 0)
        self.ygrid.rotate(90, 1, 0, 0)

        #mw = QtGui.QMainWindow()
        #mw.resize(800,800)

        # self.win = pg.GraphicsWindow(title="Basic plotting examples")
        # self.win.setWindowTitle('pyqtgraph example: Plotting')
        # self.v = self.win.addViewBox()
        # self.v.setLimits(yMin=Y_MIN, yMax=Y_MAX, minYRange=Y_MAX - Y_MIN)
        # # Enable antialiasing for prettier plots
        # pg.setConfigOptions(antialias=True)

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def make_colors(self, z):
        return (np.ones((X, Y, 4)) *
               np.array([0.541, 0.2, 0.141, 1])[np.newaxis, np.newaxis, :] *
               z[:, :, np.newaxis] / WAVE_HEIGHT)
    def trace(self,name,x,y,z):
        if name not in self.traces:
            self.traces[name] = gl.GLSurfacePlotItem(x=x, y=y, z=z, colors=self.make_colors(z))
            self.view.addItem(self.traces[name])
        else:
            self.traces[name].setData(x=x, y=y, z=z, colors=self.make_colors(z))

if __name__ == "__main__":
    p = Plot2D()
    
    v = Visualizer()
    first_pass = True

    display_data = np.zeros((X, Y))
    x_values = np.arange(-(X-1)/2, np.ceil((X-1)/2), 1)
    y_values = np.arange(-(Y-1)/2, np.ceil((Y-1)/2), 1)
    x_values_mesh, y_values_mesh = np.meshgrid(x_values, y_values)

    max_radius = np.sqrt((X/2)**2 + (Y/2)**2)
    radii = np.sqrt(x_values_mesh**2 + y_values_mesh**2) / max_radius

    def update():
        global p, current_block, first_pass, prev_freq
        # get data from speaker
        data = np.fromstring(v.listen(), dtype=np.int32)

        # apply fft
        next_block = np.fft.fft(data)
        # TODO: What is this?
        # https://gist.github.com/netom/8221b3588158021704d5891a4f9c0edd
        next_block = np.log10(np.sqrt(
            np.real(next_block) ** 2 + np.imag(next_block)**2) / INPUT_FRAMES_PER_BLOCK) * 10

        # normalize 
        # data_mean = data_mean * 0.7 + 0.3 * np.abs(np.mean(data))
        # print("mean" + str(data_mean / max_volume))
        freq_max = np.max(next_block)
        next_block = (next_block / freq_max) * WAVE_HEIGHT

        # make courser and reduce noise
        # should probably have a better way of doing this
        next_block = skimage.measure.block_reduce(next_block, (pool_factor,), np.max)

        # special case first pass since I don't really know what the dimesions
        # will be ahead of time (I could probably calculate them if I wanted to)
        if not first_pass:
            current_block = (ALPHA * current_block) + ((1-ALPHA) * next_block)
        else:
            current_block = next_block
            first_pass = False

        current_block = np.nan_to_num(current_block)
        freqs = np.fft.fftfreq(next_block.size, 1/RATE)
        max_freq = np.max(np.abs(freqs))
        freqs /= max_freq

        for radius in np.unique(radii):
            closet_freq_idx = np.argmin(np.abs(radius - freqs))
            display_data[np.where(radii == radius)] = current_block[closet_freq_idx]


        p.trace("sound",x_values, y_values, display_data)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(20)

    p.start()

