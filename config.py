class Config:
    def __init__(self):
        """ Sets good defaults for the config values """
        ### Loggin configs #####################################################
        # useful for debuggin microphone issues
        self.device_logging = False
        self.volume_logging = False


        ### Configuration for pyaudio ##########################################
        # Think of this as the size of the buffer for the audio stream. Lowering
        # this cause the image to refresh faster. However, if it is too low then
        # the program won't be able clear the buffer fast enough (too much
        # rendering).
        self.input_frames_per_block = 1024

        # This is a constant for the microphone
        self.rate = 44100

        # number of audio channels
        self.channels = 1


        ### Configuration for plotter ##########################################
        # Allows for flipping the direction of the display. By default low
        # frequencies go in the center
        self.flip_freq = True

        # height and width of the visualizer (larger looks better but is slower)
        # MUST BE EVEN
        self.width = 60
        self.height = self.width # symmetric by default
        self.wave_height = self.width / 6

        # set initial camera angle and posisiton
        self.camera_x_pan = -1.2*self.width
        self.camera_y_pan = -0.4*self.height
        self.camera_z_pan = (self.width + self.height)/2.3
        self.camera_azim_orbit = 153
        self.camera_elev_orbit = 0

        # color of the visualizer (brightness will be varied throughout
        self.color = [0.541, 0.2, 0.141, 1]


        ### Misc. Configs ######################################################
        # viewing the entire frequency spectrum makes it hard to see finer detail
        # in general it is always desireable to see the lowest frequencies so
        # this value describes the bottom fraction of the spectrum which will
        # be shown
        self.percent_freq_display = 0.1

        # this visualizer using exponential moving averages to smooth the movement
        # cause both by variation in frequency and in volume
        # lower is a slower moving average
        self.freq_alpha = 0.3
        self.volume_alpha = 0.03

