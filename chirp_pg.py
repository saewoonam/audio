import numpy as np
import pyaudio
import sys
import scipy
import scipy.signal
import time
from pyqtgraph.Qt import QtGui, QtCore 
import pyqtgraph as pg
import threading

if True:
    INPUT_DEVICE = 0
    OUTPUT_DEVICE = 1
else:
    INPUT_DEVICE = 1
    OUTPUT_DEVICE = 2

app = QtGui.QApplication([])
PAUSED = False
CHIRPING = True
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
CHUNK=1<<12
# CH speaker channel
# 1 for right speaker, 0 for  left
CH = 1

# show all audio devices connected to the computer
def show_devices(audio):
    # audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        print (audio.get_device_info_by_index(i))
        print('-'*80)

# initialize audio, microphone, speaker, pass callback as a parameter
def init_audio(callback):
    global audio, stream, OUT_STREAM
    audio = pyaudio.PyAudio()
    show_devices(audio)

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        stream_callback=callback,
                        #  The microphone on my laptop shows up at index 1 when
                        #  connected to an external monitor
                        input_device_index=INPUT_DEVICE,
                        frames_per_buffer=CHUNK)
    OUT_STREAM = audio.open(format=pyaudio.paFloat32,
                        channels=2,
                        rate=int(Fs),
                        output=True,
                        #  my build-in speakers are index 2
                        output_device_index=OUTPUT_DEVICE)


def play():
    global OUT_STREAM, OUT_DATA, win
    # for count in range(10):
    while(win.isVisible()):
        while (CHIRPING and win.isVisible()):
            time.sleep(0.1)
            OUT_STREAM.write(OUT_DATA.astype(np.float32).tobytes())
        time.sleep(1)  # sleep briefly while not chirping

# build chirp signals
def build_chirp(f1, f2, real_duration=25e-3):
    global Fs, CH
    duration = int(Fs * real_duration)
    # duration = Fs/40
    t = np.arange(duration)/Fs
    chirp = 0.5 * scipy.signal.chirp(t, f1, real_duration, f2, phi=0)
    # chirp = np.hstack([chirp, chirp[::-1]])
    # data =0.5* np.sin(2*np.pi*f*t)
    chirp = np.blackman(len(chirp))*chirp
    print('chirp duration: ', duration/Fs)
    stereo_signal = np.zeros([len(chirp), 2])   # these two lines are new
    stereo_signal[:, CH] = chirp[:]  # 1 for right speaker, 0 for  left
    return stereo_signal

w = QtGui.QWidget()

## Create some widgets to be placed inside
btn = QtGui.QPushButton('pause')
btn_chirp = QtGui.QPushButton('chirp off')
# text = QtGui.QLineEdit('enter text')
# listw = QtGui.QListWidget()
win = pg.GraphicsLayoutWidget(show=True, title=f"Pyaudio+pyqtgraph, fs={Fs}")

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

## Add widgets to the layout in their proper positions
layout.addWidget(btn, 0, 0)   # button goes in upper-left
layout.addWidget(btn_chirp, 1, 0)   # button goes in upper-left
# layout.addWidget(text, 1, 0)   # text edit goes in middle-left
# layout.addWidget(listw, 2, 0)  # list widget goes in bottom-left
layout.addWidget(win, 0, 1, 5, 5)  # plot goes on right side, spanning 3 rows

## Display the widget as a new window
w.show()

def pause(evt):
    global PAUSED
    PAUSED = not PAUSED
    if PAUSED:
        btn.setText('Unpause')
    else:
        btn.setText('Pause')


def chirp_clicked(evt):
    global CHIRPING
    CHIRPING = not CHIRPING
    if CHIRPING:
        btn_chirp.setText('chirp off')
    else:
        btn_chirp.setText('chirp on')

btn.clicked.connect(pause)
btn_chirp.clicked.connect(chirp_clicked)

#  Setup plotting window
# win = pg.GraphicsLayoutWidget(show=True, title=f"Pyaudio+pyqtgraph, fs={Fs}")
win.resize(500,500)
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
win.nextRow()
p3 = win.addPlot()
p3.setLabel('bottom', 'time', units='sec')
p3.setRange(QtCore.QRectF(0, -1000, CHUNK/RATE, 2000)) 
corr1 = p3.plot()
corr2 = p3.plot()
h = p3.plot()

# setup filter parameters
data = []
b, a = scipy.signal.butter(4, 0.1, btype='high')
# use zi to eliminate transients on successive filter of blocks of data
zi = np.zeros(max(len(a), len(b))-1)

def calc_corr(f, c, t):
    ret = np.correlate(f, c, 'full')
    ret[:len(t)] += t
    new_tail = ret[-len(t):]
    return ret[:len(f)], new_tail 

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
    global PAUSED
    if not PAUSED:
        global curve, c2, p, a, b, filtered, f, data, ff1, fft2, corr1, corr2
        global tail1, tail2
        x = np.arange(len(data))/RATE
        y = data
        # plot raw data in yellow
        filtered.setData(x, y, pen='y')
        # plot filtered datat in red
        curve.setData(x, f, pen='r')
        # compute and plot fft's of raw and filtered data
        window = np.blackman(len(data))
        D = np.abs(np.fft.rfft(data*window))
        D2 = np.abs(np.fft.rfft(f*window))
        freq = np.arange(len(D))*RATE/CHUNK
        fft1.setData(freq, D, pen='y')
        fft2.setData(freq, D2, pen='b')
        xcorr1, tail1 = calc_corr(f, OUT_DATA[:, CH], tail1)
        xcorr2, tail2 = calc_corr(f, chirp2[:, CH], tail2)
        corr1.setData(x, np.abs(xcorr1[:len(data)]), pen='b')
        corr2.setData(x, xcorr2[:len(data)], pen='r')
        hilbert = np.abs(scipy.signal.hilbert(xcorr1[:len(data)]))
        h.setData(x, hilbert, pen='y')
        peaks, props = scipy.signal.find_peaks(hilbert, distance=40, height=150)
        print(peaks/Fs*1000, props)
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


chirp = build_chirp(18.6e3, 20e3, 2e-3)
chirp2 = build_chirp(16e3, 18e3, 2e-3)
audible_chirp = build_chirp(1e3, 2e3, 100e-3)

OUT_DATA = audible_chirp
OUT_DATA = chirp
tail1 = np.zeros(len(OUT_DATA)-1)
tail2 = np.zeros(len(chirp2)-1)

thread_play = threading.Thread(target=play)
thread_play.start()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    # import sys
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     QtGui.QApplication.instance().exec_()
    app.exec_()
