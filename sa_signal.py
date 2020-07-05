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
CHUNK = 1024 # 1024 bytes of data read from the buffer
RECORD_SECONDS = 0.1
WAVE_OUTPUT_FILENAME = "file.wav"

app = QtGui.QApplication([])

p = pg.plot()
p.setWindowTitle('pyqtgraph example: PlotSpeedTest')
# p.setRange(QtCore.QRectF(0, -2000, 25e-3, 4000)) 
p.setLabel('bottom', 'time', units='sec')
p.setLogMode(False, True)
p.setRange(QtCore.QRectF(0, 1, RATE/2, 3)) 
curve = p.plot()

lastTime = time()
fps = None
# define callback (2)

class Helper(QtCore.QObject):
    changed = QtCore.pyqtSignal(object)

def callback(in_data, frame_count, time_info, status):
    helper.changed.emit(in_data)


def update(in_data): 
    global curve, data, ptr, p, lastTime, fps

    # d = stream.read(CHUNK)
    data = np.frombuffer(in_data, dtype=np.int16);
    x = np.arange(len(data))/RATE
    y = data
    # curve.setData(x, y)

    D = np.abs(np.fft.rfft(data-data.mean()))
    f = np.arange(len(D))*RATE/CHUNK
    curve.setData(f, D)

    now = time()
    dt = now - lastTime
    lastTime = now
    if fps is None:
        fps = 1.0/dt
    else:
        s = np.clip(dt*3., 0, 1)
        fps = fps * (1-s) + (1.0/dt) * s
    p.setTitle('%0.2f fps' % fps)
    # app.processEvents()  ## force complete redraw for every plot

if False:
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(0)

helper = Helper()
helper.changed.connect(update)

audio = pyaudio.PyAudio()

# Claim the microphone
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    stream_callback=callback,
                    input=True)#,
                    #frames_per_buffer=CHUNK)
stream.start_stream()

    


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
