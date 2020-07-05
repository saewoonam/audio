import sonar
import queue
import math
import numpy as np
import pyaudio

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)


fs= 44100
f = 440;
duration = lcm(fs,f)
# duration = 44100
t = np.arange(duration/10)/fs
data =1* np.sin(2*np.pi*f*t)
#data = np.bartlett(len(data))*data

p = pyaudio.PyAudio() #instantiate PyAudio

def show_devices(audio):
    # audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        print (i, audio.get_device_info_by_index(i)['maxOutputChannels'])

show_devices(p)

out = p.open(format=pyaudio.paFloat32, channels=1, rate=int(fs),output=True,output_device_index=2)
for i in range(5):
    out.write( data.astype(np.float32).tobytes() )
