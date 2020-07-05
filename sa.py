#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import pyaudio

FORMAT = pyaudio.paInt16 # We use 16 bit format per sample
CHANNELS = 1
RATE = 44100
# RATE = 96000 
# RATE = 48000 
CHUNK = 1<<10 # 1024 bytes of data read from the buffer

app = QtGui.QApplication([])

win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyaudio pyqtgraph')

# p = pg.plot()
p1 = win.addPlot()
p1.setLabel('bottom', 'time', units='sec')
p1.setRange(QtCore.QRectF(0, -500, CHUNK/RATE, 1000)) 
curve1 = p1.plot()
def makeBox(p):
    p.showAxis('right', show=True)
    p.getAxis('right').setStyle(showValues=False)
    p.showAxis('top', show=True)
    p.getAxis('top').setStyle(showValues=False)
    p.showGrid(x=True, y=True)
makeBox(p1)

win.nextRow()
p = win.addPlot()
p.setTitle('Spectrum')
p.setLabel('bottom', 'frequency', units='Hz')
p.setLogMode(False, True)
p.setRange(QtCore.QRectF(0, 1, RATE/2, 3)) 
makeBox(p)
curve = p.plot()

lastTime = time()
fps = None

def update(): 
    global curve, data, ptr, p, lastTime, fps

    in_data = stream.read(CHUNK)
    data = np.frombuffer(in_data, dtype=np.int16);
    x = np.arange(len(data))/RATE
    y = data
    curve1.setData(x, y, pen='r')
    data = (data-data.mean()) * np.bartlett(len(data))
    D = np.abs(np.fft.rfft(data))
    f = np.arange(len(D))*RATE/CHUNK
    curve.setData(f, D, pen='y')

    now = time()
    dt = now - lastTime
    lastTime = now
    if fps is None:
        fps = 1.0/dt
    else:
        s = np.clip(dt*3., 0, 1)
        fps = fps * (1-s) + (1.0/dt) * s
    # p1.setTitle('%0.2f fps' % fps)
    p1.setTitle('%0.2f' % (dt*1000))
    app.processEvents()  ## force complete redraw for every plot
    # win.repaint()

if True:
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(0)

audio = pyaudio.PyAudio()

# Claim the microphone
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True)
stream.start_stream()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
