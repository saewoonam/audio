import numpy as np
import pyaudio
import sys
import scipy
import scipy.signal
import time
import matplotlib.pyplot as plt

FORMAT=pyaudio.paFloat32
fs= 44100
fs= 96000
CH = 1
p = pyaudio.PyAudio()
def show_devices(audio):
    # audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        print (i, audio.get_device_info_by_index(i))

def play(out, data, reps=1):
    out.write( data.astype(np.float32).tobytes() )

def build_chirp(f1, f2):
    global fs, CH
    duration = fs/40
    t = np.arange(duration)/fs
    chirp = 0.75 * scipy.signal.chirp(t, f1, 25e-3, f2, phi=0)
    # chirp = np.hstack([chirp, chirp[::-1]])
    # data =0.5* np.sin(2*np.pi*f*t)
    chirp = np.bartlett(len(chirp))*chirp
    print('duration: ', duration/fs)
    stereo_signal = np.zeros([len(chirp), 2])   #these two lines are new
    stereo_signal[:, CH] = chirp[:]     #1 for right speaker, 0 for  left
    return stereo_signal
chirp = build_chirp(17e3, 18e3)
chirp2 = build_chirp(19e3, 20e3)

CHANNELS = 1
RATE = fs
CHUNK=RATE//4

global data
data = []
def callback(in_data, frame_count, time_info, status):
    global data
    # print('in_data', len(in_data), frame_count, time_info, status)
    data = np.frombuffer(in_data, dtype=np.float32)
    return (None, pyaudio.paComplete)


while True:
    out = p.open(format=pyaudio.paFloat32,
                 channels=2,
                 rate=int(fs),
                 output=True,
                 output_device_index=2)
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    stream_callback=callback,
                    input_device_index=1,
                    frames_per_buffer=CHUNK)
    play(out,chirp)
    # stream.start_stream()
    # print(stream.is_active())
    while stream.is_active():
       time.sleep(0.05)
    # print('data', data)
    stream.close()
    out.close()
    t = np.arange(CHUNK)/fs

    plt.clf()
    plt.subplot(311)

    plt.plot(t, data)
    b, a = scipy.signal.butter(4, 0.1, btype='high')
    f = scipy.signal.lfilter(b, a, data)
    plt.plot(t, f)
    plt.subplot(312)
    xcorr = np.correlate(data, chirp[:, CH], 'full')
    print(np.argmax(np.abs(xcorr))/fs*1000)
    start = len(chirp[:,CH])-1
    plt.plot(t, xcorr[start:])
    print(len(xcorr[:-start]))
    xcorr = np.correlate(f, chirp[:, CH], 'full')
    print(np.argmax(np.abs(xcorr))/fs*1000)
    plt.plot(t, xcorr[start:])
    plt.subplot(313)
    xcorr = np.correlate(data, chirp2[:, CH], 'full')
    plt.plot(t, xcorr[start:])
    plt.pause(0.001)
    # fig.drawnow()

