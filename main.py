from visualizer import visualizer
from plot import Plotter
from audio import AudioConnection
from config import Config

CONFIG = Config()

if __name__ == "__main__":
    p = Plotter(CONFIG)
    conn = AudioConnection(CONFIG)
    visualizer(p, conn, CONFIG)

