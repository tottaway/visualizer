# builtins
import audioop
import numpy as np
from pyqtgraph.Qt import QtCore



def init_radii(config):
    """
    Returns a square matrix where the value of each point is proportional to
    the distance from that point to the center. Values are scaled and flipped
    according to the config
    Basically, it says for each point on the visualizer, which part of the
    frequency spectrum should be displayed
    """
    X = config.width
    Y = config.height
    x_values = np.arange(-(X-1)/2, np.ceil((X-1)/2), 1)
    y_values = np.arange(-(Y-1)/2, np.ceil((Y-1)/2), 1)
    x_values_mesh, y_values_mesh = np.meshgrid(x_values, y_values)

    max_radius = X/2
    radii = np.sqrt(x_values_mesh**2 + y_values_mesh**2) / max_radius


    # scale data and only include lower pitches
    radii *= config.percent_freq_display

    if config.flip_freq:
        radii = config.percent_freq_display - radii
        radii *= np.where(radii<0, 0, 1)

    return radii

def init_closest_freq_list(radii, config):
    """
    Returns a list of tuples (radius, index) where the index is the index in the
    block returned from the Fourier tranform which contains the height which
    should be displayed for a given radii
    Used to map Fourier transform result onto the visualizer
    """
    freqs = np.fft.fftfreq(config.input_frames_per_block, 1/config.rate)
    freqs /= np.max(freqs)
    closest_freq_list = []
    for radius in np.unique(radii):
        if radius < 0:
            radius = 0
        closest_freq_list.append((radius, np.argmin(np.abs(radius - freqs))))
    return closest_freq_list

def visualizer(p, conn, config):
    radii = init_radii(config)
    closest_freq_list = init_closest_freq_list(radii, config)
    display_data = np.zeros((config.width, config.height))

    current_block = np.zeros(config.input_frames_per_block)
    first_pass = True
    max_volume = 1e-7 # avoid divide by zero
    volume = 0

    def update():
        # Make sure these variables persist through iterations
        nonlocal current_block, first_pass, max_volume, volume

        # get data from speaker
        data = conn.listen()

        # Get exponential moving average of volume
        curr_volume = audioop.rms(data, 1)
        if curr_volume == 0:
            volume = 0
        else:
            volume = (config.volume_alpha * curr_volume +
                (1-config.volume_alpha) * volume)
        max_volume = max(volume, max_volume)
        if config.volume_logging:
            print(volume)

        # convert data into a numpy array and apply fast fourier transform
        data = np.fromstring(data, dtype=np.int32)
        next_block = np.fft.fft(data)

        # credit: https://gist.github.com/netom/8221b3588158021704d5891a4f9c0edd
        # Scale the data so it looks better
        # used to have imaginary part in here but fft was returning almost entierly
        # real values so I removed it
        next_block = np.log10(next_block / config.input_frames_per_block) * 20

        # normalize 
        freq_max = np.max(next_block)
        next_block /= freq_max 
        # scale based off volume (growing or shrinking by 50%)


        # Get exponential moving average of the frequencies
        if np.average(np.abs(next_block)) > 1e-3:
            if not first_pass:
                current_block = ((1-config.freq_alpha) * current_block +
                        config.freq_alpha * next_block)
            else:
                current_block = next_block
                first_pass = False
        elif volume == 0:
            current_block *= 0

        # Remove NANs
        current_block = np.nan_to_num(current_block)

        # build display data
        for radius, idx in closest_freq_list:
            display_data[np.where(radii == radius)] = current_block[idx]

        # render data
        p.trace("sound", display_data, volume / max_volume)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(1)

    p.start()

