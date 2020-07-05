import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.animation as animation

FORMAT = pyaudio.paInt16 # We use 16 bit format per sample
CHANNELS = 1
RATE = 44100
CHUNK = 1024 # 1024 bytes of data read from the buffer
RECORD_SECONDS = 0.1
WAVE_OUTPUT_FILENAME = "file.wav"

audio = pyaudio.PyAudio()

# Claim the microphone
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE, 
                    input=True)#,
                    #frames_per_buffer=CHUNK)
stream.start_stream()
# First set up the figure, the axis, and the plot element we want to animate
fig, (ax1, ax2) = plt.subplots(2,1)

ax1.set_xlim(( 0,1024/RATE))
ax1.set_ylim((-500, 500))

ax2.set_xlim(( 0,RATE/2))
ax2.set_ylim((1, 1e5))
ax2.set_yscale('log')

line1, = ax1.plot([], [], lw=2)
line2, = ax2.plot([], [], lw=2)

# initialization function: plot the background of each frame
def init():
    line.set_data([], [])
    return (line,)
# animation function. This is called sequentially
def animate(i):
    d = stream.read(CHUNK)
    data = np.frombuffer(d, dtype=np.int16);
    x = np.arange(len(data))/RATE
    y = data
    # print(x,y)
    line1.set_data(x, y)
    D = np.abs(np.fft.rfft(data-data.mean()))
    f = np.arange(len(D))*RATE/CHUNK
    line2.set_data(f, D)
    # print(RATE/CHUNK)
    # print(D)
    # print(max(f))
    # print('animate')
    return (line1, line2, )

# call the animator. blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, interval=0, blit=True)
plt.show()
