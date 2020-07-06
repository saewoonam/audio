import numpy as np
import pyaudio
import sys
import scipy
import scipy.signal
import time
from pyqtgraph.Qt import QtGui, QtCore 
import pyqtgraph as pg
app = QtGui.QApplication([])

FORMAT=pyaudio.paFloat32
dtype = np.float32
FORMAT=pyaudio.paInt16
dtype = np.int16
fs= 44100
fs= 96000
CH = 1
audio = pyaudio.PyAudio()
def show_devices(audio):
    # audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        print (i, audio.get_device_info_by_index(i))


CHANNELS = 1
RATE = fs
CHUNK=RATE//1
b, a = scipy.signal.butter(4, 0.1, btype='high')

win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyaudio pyqtgraph')

# p = pg.plot()
p = win.addPlot()
p.setLabel('bottom', 'time', units='sec')
p.setRange(QtCore.QRectF(0, -1000, CHUNK/RATE, 2000)) 
curve = p.plot()
c2 = p.plot()

global data
data = []
def callback(in_data, frame_count, time_info, status):
    global data, a, b, bag
    # print('time_info', time_info, 'status',status)
    t = np.arange(CHUNK)/fs
    data = np.frombuffer(in_data, dtype=dtype)
    helper.update.emit()
    return (None, pyaudio.paContinue)

def update():
    global curve, c2, p, a, b
    x = np.arange(len(data))/RATE
    y = data
    f = scipy.signal.lfilter(b, a, data)
    c2.setData(x, y, pen='y')
    curve.setData(x, f, pen='r')

class Helper(QtCore.QObject):
    update = QtCore.pyqtSignal()
helper = Helper()
helper.update.connect(update)

stream = audio.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                stream_callback=callback,
                input_device_index=1,
                frames_per_buffer=CHUNK)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    # import sys
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()
    app.exec_()
