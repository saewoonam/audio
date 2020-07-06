import numpy as np
import pyaudio
import sys
import scipy
import scipy.signal
import time
from pyqtgraph.Qt import QtGui, QtCore 
import pyqtgraph as pg
app = QtGui.QApplication([])

#  Setup pyaudio parameters
FORMAT=pyaudio.paFloat32
dtype = np.float32
FORMAT=pyaudio.paInt16
dtype = np.int16
Fs= 44100
# Fs= 96000
CHANNELS = 1
RATE = Fs
CHUNK=RATE//1
CHUNK=256
# CH is not used, for speaker output
CH = 1

# show all audio devices connected to the computer
def show_devices(audio):
    # audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        print (audio.get_device_info_by_index(i))
        print('-'*80)

# initialize audio, microphone, pass callback as a parameter
def init_audio(callback):
    global audio, stream
    audio = pyaudio.PyAudio()
    show_devices(audio)

    stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    stream_callback=callback,
                        #  The microphone on my laptop shows up at index 1 when
                        #  connected to an external monitor
                    input_device_index=1,
                    frames_per_buffer=CHUNK)


#  Setup plotting window
win = pg.GraphicsLayoutWidget(show=True, title=f"Pyaudio+pyqtgraph, fs={Fs}")
win.resize(500,300)
p = win.addPlot()
p.setLabel('bottom', 'time', units='sec')
p.setRange(QtCore.QRectF(0, -1000, CHUNK/RATE, 2000)) 
filtered = p.plot()
curve = p.plot()
win.nextRow()
p2 = win.addPlot()
p2.setLabel('bottom', 'frequency', units='Hz')
p2.setLogMode(False, True)
p2.setRange(QtCore.QRectF(0, 0, RATE/2, 5)) 
fft1 = p2.plot()
fft2 = p2.plot()

# setup filter parameters
data = []
b, a = scipy.signal.butter(4, 0.1, btype='high')
# use zi to eliminate transients on successive filter of blocks of data
zi = np.zeros(max(len(a), len(b))-1)

#  pyaudio callback for processing data from the microphone
def callback(in_data, frame_count, time_info, status):
    global data, a, b, bag, f, zi
    # print('time_info', time_info, 'status',status)
    data = np.frombuffer(in_data, dtype=dtype)
    f,zi = scipy.signal.lfilter(b, a, data, zi=zi)
    # emit a signal to tell pyqtgraph we have data to plot
    helper.update.emit()
    return (None, pyaudio.paContinue)

#  This is called by qt slot/signal to update the graph
def update():
    global curve, c2, p, a, b, filtered, f, data, ff1, fft2
    x = np.arange(len(data))/RATE
    y = data
    # plot raw data in yellow
    filtered.setData(x, y, pen='y')
    # plot filtered datat in red
    curve.setData(x, f, pen='r')
    # compute and plot fft's of raw and filtered data
    window = np.bartlett(len(data))
    D = np.abs(np.fft.rfft(data*window))
    D2 = np.abs(np.fft.rfft(f*window))
    freq = np.arange(len(D))*RATE/CHUNK
    fft1.setData(freq, D, pen='y')
    fft2.setData(freq, D2, pen='b')

# This is a class to signal that data is ready to be plotted...Interface to QT
# objects
#   Could not get the helper to pass parameters to update...used globals
class Helper(QtCore.QObject):
    update = QtCore.pyqtSignal()


helper = Helper()
helper.update.connect(update)

init_audio(callback)
#  start_stream is not needed... it is running already for some reason
stream.start_stream()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    # import sys
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()
    app.exec_()
