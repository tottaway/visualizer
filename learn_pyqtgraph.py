import sys
import time
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg

# app = QtGui.QApplication(sys.argv) 

app = pg.mkQApp()

view = gl.GLViewWidget()
view.show()

xgrid = gl.GLGridItem()
ygrid = gl.GLGridItem()
zgrid = gl.GLGridItem()

xgrid.rotate(90, 0, 1, 0)
ygrid.rotate(90, 1, 0, 0)

surface = gl.GLSurfacePlotItem(z=np.random.normal(size=(100, 100)),
        colors=np.random.normal(size=(100, 100, 4)))
view.addItem(surface)

view.pan(50, 50, 60)

def update():
    surface.setData(z=np.random.normal(size=(100, 100))) 

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(2000)
          


if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()  # Start QApplication event loop ***
