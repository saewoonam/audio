import sonar
import queue
import math
import numpy as np
import pyaudio

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)


fs= 44100
f = 220;
duration = lcm(fs,f)
# duration = 44100
t = np.arange(duration/10)/fs
data =0.1* np.sin(2*np.pi*f*t)
#data = np.bartlett(len(data))*data

p = pyaudio.PyAudio() #instantiate PyAudio

out = p.open(format=pyaudio.paFloat32, channels=1, rate=int(fs),output=True,output_device_index=2)
for i in range(5):
    out.write( data.astype(np.float32).tobytes() )
