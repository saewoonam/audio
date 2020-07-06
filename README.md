# Simple python programs using pyaudio 
##  Relevant programs
1.  sa.py
    *  Spectrum analyzer program for the microphone
    *  Digitizes, filters, and computes FFT of signals from a microphone
    *  Uses pyqtgraph instead of matplotlib, much faster, better
       interactoin with OS 
    *  Works on osx, windows, linux
    *  Uses pyaudio callbacks to process signals as they are recorded by the
       microphone
    *  Must set the audio device index in the code for your machine
2.  chirp_pg.py
    *  Does above
    *  Plays chirps for the first 10 seconds, 1 per second

## Requirements
  * python3
  * pyqtgraph
  * pyaudio
  * pyqt (not sure this will be included automatically by pyqtgraph)

