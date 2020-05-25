import sys

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np

class Plotter():
    def __init__(self, config):
        self.config = config
        X = self.config.width
        Y = self.config.height

        self.traces = dict()

        self.app = pg.mkQApp()
        self.view = gl.GLViewWidget()
        self.view.show()
        self.view.pan(self.config.camera_x_pan, self.config.camera_y_pan,
                self.config.camera_z_pan)
        self.view.orbit(self.config.camera_azim_orbit,
                self.config.camera_elev_orbit)

        self.xgrid = gl.GLGridItem()
        self.ygrid = gl.GLGridItem()
        self.zgrid = gl.GLGridItem()

        # self.xgrid.rotate(90, 0, 1, 0)
        # self.ygrid.rotate(90, 1, 0, 0)

        self.build_color_mask()


    def build_color_mask(self):
        # build a mesh
        x = np.linspace(-1, 1, self.config.width)
        y = np.linspace(-1, 1, self.config.height)
        x_mesh, y_mesh = np.meshgrid(x, y)

        # Build a mask for the circle inscribed in the square
        radius = np.sqrt(x_mesh**2 + y_mesh**2)
        self.circle_mask = np.where(radius<=1, 1, 0)


        self.colors = np.array(self.config.color)
        self.color_mask = (self.circle_mask[:, :, np.newaxis] *
                self.colors[np.newaxis, np.newaxis, :])

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def make_colors(self, z):
        return self.color_mask * z[:, :, np.newaxis]

    def trace(self,name,z):
        if name not in self.traces:
            X = self.config.width
            Y = self.config.height
            x = np.arange(-(X-1)/2, np.ceil((X-1)/2), 1)
            y = np.arange(-(Y-1)/2, np.ceil((Y-1)/2), 1)

            self.traces[name] = gl.GLSurfacePlotItem(x=x, y=y, z=z,
                    colors=self.make_colors(z), computeNormals=False)

            self.view.addItem(self.traces[name])
        else:
            self.traces[name].setData(z=z * self.config.wave_height,
                    colors=self.make_colors(z))
