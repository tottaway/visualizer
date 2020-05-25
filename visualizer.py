# builtins
import audioop

import numpy as np

from pyqtgraph.Qt import QtCore

from plot import Plotter
from audio import AudioConnection
from config import Config

CONFIG = Config()


def init_radii():
    X = CONFIG.width
    Y = CONFIG.height
    x_values = np.arange(-(X-1)/2, np.ceil((X-1)/2), 1)
    y_values = np.arange(-(Y-1)/2, np.ceil((Y-1)/2), 1)
    x_values_mesh, y_values_mesh = np.meshgrid(x_values, y_values)

    max_radius = np.sqrt((X/2)**2 + (Y/2)**2)
    radii = np.sqrt(x_values_mesh**2 + y_values_mesh**2) / max_radius


    # scale data and only include lower pitches
    radii = radii * CONFIG.percent_freq_display

    if CONFIG.flip_freq:
        radii = np.max(np.max(radii)) - radii

    return radii

def init_closest_freq_list(radii):
    freqs = np.fft.fftfreq(CONFIG.input_frames_per_block, 1/CONFIG.rate)
    freqs /= np.max(freqs)
    closest_freq_list = []
    for radius in np.unique(radii):
        closest_freq_list.append((radius, np.argmin(np.abs(radius - freqs))))
    return closest_freq_list

if __name__ == "__main__":
    p = Plotter(CONFIG)
    
    conn = AudioConnection(CONFIG)
    first_pass = True

    radii = init_radii()
    closest_freq_list = init_closest_freq_list(radii)
    display_data = np.zeros((CONFIG.width, CONFIG.height))

    def update():
        # Make sure these variables persist through iterations
        global freqs, current_block, first_pass, prev_freq, max_volume, volume

        # get data from speaker
        data = conn.listen()

        # Get exponential moving average of volume
        curr_volume = audioop.rms(data, 1)
        if not first_pass:
            volume = (CONFIG.volume_alpha * curr_volume +
                    (1-CONFIG.volume_alpha) * volume)
            max_volume = max(volume, max_volume)
        else:
            volume = curr_volume
            max_volume = max(volume, 0.00001)
        if CONFIG.volume_logging:
            print(volume)

        # convert data into a numpy array and apply fast fourier transform
        data = np.fromstring(data, dtype=np.int32)
        next_block = np.fft.fft(data)

        # credit: https://gist.github.com/netom/8221b3588158021704d5891a4f9c0edd
        # Scale the data so it looks better
        # used to have imaginary part in here but fft was returning almost entierly
        # real values so I removed it
        next_block = np.log10(next_block / CONFIG.input_frames_per_block) * 20

        # normalize 
        freq_max = np.max(next_block)
        next_block /= freq_max 
        # scale based off volume (growing or shrinking by 50%)
        next_block *= 0.5+(volume/ max_volume)


        # Get exponential moving average of the frequencies
        if not first_pass:
            current_block = ((1-CONFIG.freq_alpha) * current_block +
                    CONFIG.freq_alpha * next_block)
        else:
            current_block = next_block
            first_pass = False

        # Remove NANs
        current_block = np.nan_to_num(current_block)

        # build display data
        for radius, idx in closest_freq_list:
            display_data[np.where(radii == radius)] = current_block[idx]

        # render data
        p.trace("sound", display_data)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(1)

    p.start()

