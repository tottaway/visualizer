import pyaudio

# shamelessly adapted from here: https://stackoverflow.com/a/4160733    
class AudioConnection:
    def __init__(self, config):
        self.config = config
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.errorcount = 0
        self.noisycount = 0

    def stop(self):
        self.stream.close()

    def open_mic_stream( self ):
        stream = self.pa.open(format = pyaudio.paInt32,
                              channels = self.config.channels,
                              rate = self.config.rate,
                              input = True,
                              frames_per_buffer = self.config.input_frames_per_block)
        return stream

    def listen(self):
        try:
            block = self.stream.read(self.config.input_frames_per_block)
        except:
            # dammit. 
            self.errorcount += 1
            # print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.noisycount = 1
            return 
        return block
