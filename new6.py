from PyQt5 import QtWidgets, QtCore, uic, QtGui, QtPrintSupport
from pyqtgraph import PlotWidget, plot
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import *   
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy import signal
from os import path
import pyqtgraph as pg
import queue as Q
import pandas as pd
import numpy as np
import sys
import os
from scipy.io.wavfile import read
from scipy import signal
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import wave
from scipy.signal import firwin,freqz
import simpleaudio as sa
from scipy.fft import rfft, rfftfreq
from matplotlib import pyplot as plt
import librosa
from scipy.signal import butter, lfilter
import sounddevice as sd

MAIN_WINDOW,_=loadUiType(path.join(path.dirname(__file__),"sigview.ui"))
MAIN_WINDOW2,_=loadUiType(path.join(path.dirname(__file__),"fft2.ui"))

class MainApp(QMainWindow,MAIN_WINDOW):
    
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        global gainArray
        # self.Toolbar()
        global sliderArray
        sliderArray = []
        sliderArray=[self.verticalSlider,self.verticalSlider_2,self.verticalSlider_3,self.verticalSlider_4,self.verticalSlider_5,self.verticalSlider_6,self.verticalSlider_7,self.verticalSlider_8,self.verticalSlider_9,self.verticalSlider_10]
        self.graphWidget.plotItem.showGrid(True, True, alpha=0.8)
        self.graphWidget.plotItem.setTitle("Before Equalization")
        self.graphWidget.setBackground('w')
        
        self.graphWidget2.plotItem.showGrid(True, True, alpha=0.8)
        self.graphWidget2.plotItem.setTitle("After Equalization")
        self.graphWidget2.setBackground('w')
        self.spectWidget.setBackground('#f2f2f2')
        self.spectWidget.getPlotItem().hideAxis('bottom')
        self.spectWidget.getPlotItem().hideAxis('left')
        self.Toolbar()
        self.loopslider()
        # self.fft()
        # self.plotAudio()
        # self.Menubar()
    
    # def init_UI(self):
    #     self.play = QtWidgets.QPushButton(self.centralwidget)
    #     self.play.setGeometry(QtCore.QRect(320, 170, 41, 23))
    #     self.play.setText("")

    def Toolbar(self):
        self.PlayBtn.triggered.connect(self.play_audio)
        self.OpenSignalBtn.triggered.connect(self.BrowseSignal)
        self.Stop.triggered.connect(self.stop_audio)
        self.LeftScroll.triggered.connect(self.ScrollLeft) 
        self.RightScroll.triggered.connect(self.ScrollRight)
        self.ZoomIn.triggered.connect(self.zoomIn) 
        self.ZoomOut.triggered.connect(self.zoomOut)
        self.spectrogram.triggered.connect(self.spectrogram) 

    def show2(self):
        self.window2=QtWidgets.QMainWindow()
        self.ui=MainApp2()
        self.ui.setupUi(self.window2)
        self.window2.show()

    def BrowseSignal(self):
        global fileName
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        global sampling_rate, audio2 
        audio2, sampling_rate = librosa.load(fileName, sr=None, duration=20.0)
        # audio_file = read(fileName)
        # audio = audio_file[1]
        # global audio2
        # audio2= audio.astype(float)
        global l
        l=len(audio2)
        self.play_audio()
        self.changeslidervalue()
        self.plotAudio(audio2,l)
        # MainApp2.fft()
        # self.play_audio(fileName)
        self.graphWidget.plotItem.getViewBox().setLimits(xMin=0,xMax=l)
        print(audio2)
        print(len(audio2))

    def plotAudio(self,file,length):
        self.graphWidget.plot(file[0:length],pen="b")

    def play_audio(self):
        global wave_obj
        wave_obj = sa.WaveObject.from_wave_file(fileName)
        global play_obj
        play_obj = wave_obj.play()
        # play_obj.wait_done()  # Wait until sound has finished playing 

    def stop_audio(self):
        stop_obj = play_obj.stop()

    def zoomIn(self):
        self.graphWidget2.plotItem.getViewBox().scaleBy(x=0.5, y=1) #Increases the scale of X axis and Y axis
        self.graphWidget.plotItem.getViewBox().scaleBy(x=0.5, y=1) #Increases the scale of X axis and Y axis

    def zoomOut(self):
        self.graphWidget2.plotItem.getViewBox().scaleBy(x=2, y=1) #Decreases scale of X axis and Y axis 
        self.graphWidget.plotItem.getViewBox().scaleBy(x=2, y=1) #Decreases scale of X axis and Y axis 

    def ScrollLeft(self):
        self.graphWidget.plotItem.getViewBox().translateBy(x=-1000, y=0)
        self.graphWidget2.plotItem.getViewBox().translateBy(x=-1000, y=0)

    def ScrollRight(self):
        self.graphWidget.plotItem.getViewBox().translateBy(x=1000, y=0)
        self.graphWidget2.plotItem.getViewBox().translateBy(x=1000, y=0)

    def loopslider(self):
            global i
            i = 0
            while i < 10:
                sliderArray[i].valueChanged.connect(self.changeslidervalue)
                i += 1

    def changeslidervalue(self):
        global i
        i = 0
        gainArray = []
        while i < 10:
            gainArray.append(sliderArray[i].value())
            i += 1
        print(gainArray)
        self.audioRun(*gainArray)
        return gainArray
            # self.audioRun(self.flag,*gainArray)
            # return gainArray

    def audioRun(self,*gainArray):
        Rs = self.processAudio(audio2, sampling_rate, *gainArray)
        self.plot(Rs,sampling_rate)
        return Rs

    def processAudio(self, audio2, sampling_rate, gain1, gain2, gain3, gain4, gain5, gain6, gain7, gain8, gain9, gain10):
        freq = np.arange(sampling_rate * 0.5)
        global size
        size = len(freq) / 10
        band1 = self.bandpass_filter(audio2, freq[21], freq[int(size)], sampling_rate, order=4) *10** (gain1)
        band2 = self.bandpass_filter(audio2, freq[int(size)], freq[2 * int(size)], sampling_rate, order=4) *10** (gain2)
        band3 = self.bandpass_filter(audio2, freq[2 * int(size)], freq[3 * int(size)], sampling_rate, order=4) *10** (gain3)
        band4 = self.bandpass_filter(audio2, freq[3 * int(size)], freq[4 * int(size)], sampling_rate, order=4) *10**  (gain4)
        band5 = self.bandpass_filter(audio2, freq[4 * int(size)], freq[5 * int(size)], sampling_rate, order=4) *10**  (gain5)
        band6 = self.bandpass_filter(audio2, freq[5 * int(size)], freq[6 * int(size)], sampling_rate, order=4) *10**  (gain6)
        band7 = self.bandpass_filter(audio2, freq[6 * int(size)], freq[7 * int(size)], sampling_rate, order=4) *10**  (gain7)
        band8 = self.bandpass_filter(audio2, freq[7 * int(size)], freq[8 * int(size)], sampling_rate, order=4) *10**  (gain8)
        band9 = self.bandpass_filter(audio2, freq[8 * int(size)], freq[9 * int(size)], sampling_rate, order=4) *10**  (gain9)
        band10 = self.bandpass_filter(audio2, freq[9 * int(size)], freq[-1], sampling_rate, order=3) *10** (gain10)
        osignal = band1 + band2 + band3 + band4 + band5 + band6 + band7 + band8 + band9 + band10
        return osignal
        # ============================================================================

    def bandpass_filter(self, audio2nyquistfreq, lowcut, highcut, sampling_rate, order=5):
        nyquistfreq = 0.5 * sampling_rate
        low = lowcut / nyquistfreq
        high = highcut / nyquistfreq
        b, a = butter(order, [low, high], btype='band', analog=False)
        filtered = lfilter(b, a, audio2)
        return filtered

    def plot(self,signal, sample_rate):
        global i
        i=2
       
        audio2fftafter = rfft(signal)
        global fftabsafter
        fftabsafter = abs(audio2fftafter)
        global freqsa
        freqsa = rfftfreq(len(audio2fftafter), 1 / sample_rate)
        # self.UI.pcArray[3].plot(freqsa[:int(freqsa.size / 2)], fftabsafter[:int(freqsa.size / 2)], pen='r')
        N1 = len(signal)
        T1 = int(N1 / sample_rate)
        self.graphWidget2.plot(signal[:T1 * sample_rate], pen='r')
        self.graphWidget2.plotItem.getViewBox().setLimits(xMin=0,xMax=l)
        sd.play(signal, sample_rate)
    
    def spectrogram(self):
        # self.spectWidgets[MainApp.currentSelected -1] = myPlotWidget(self.centralwidget, id = ((MainApp.currentSelected)+ 3 ))
        
        # self.verticalLayout_2.addWidget(self.spectWidgets[MainApp.currentSelected -1])

        # self.spectWidgets[MainApp.numOfGraphs -1].setEnabled(True)
        # win = self.spectWidgets[MainApp.currentSelected -1 ]
        # self.spectWidgetConfiguration(win)
        pg.setConfigOptions(imageAxisOrder='row-major')
        # the function that plot spectrogram of the selected signal
        f, t, Sxx = signal.spectrogram(audio2,10)

        # Item for displaying image audio2
        img = pg.ImageItem()
        self.spectWidget.addItem(img)
        # Add a histogram with which to control the gradient of the image
        hist = pg.HistogramLUTItem()
        # Link the histogram to the image
        hist.setImageItem(img)
        # Fit the min and max levels of the histogram to the audio2 available
        hist.setLevels(np.min(Sxx), np.max(Sxx))
        # This gradient is roughly comparable to the gradient used by Matplotlib
        # You can adjust it and then save it using hist.gradient.saveState()
        hist.gradient.restoreState(
        {'mode': 'rgb','ticks': [(0.5, (0, 182, 188, 255)),(1.0, (246, 111, 0, 255)),(0.0, (75, 0, 113, 255))]})

        # Sxx contains the amplitude for each pixel
        img.setImage(Sxx)
        # Scale the X and Y Axis to time and frequency (standard is pixels)
        img.scale(t[-1]/np.size(Sxx, axis=1),f[-1]/np.size(Sxx, axis=0))
        # Limit panning/zooming
        self.win.setLimits(xMin=t[0], xMax=t[-1], yMin=f[0], yMax=f[-1])
        # self.win.setLabel('bottom', "Time", units='s')
        # self.win.setLabel('left', "Frequency", units='Hz')
        # self.win.plotItem.setTitle("Spectrogram")    

class MainApp2(QMainWindow,MAIN_WINDOW2):
    def __init__(self,parent=None):
        super(MainApp2,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        # self.fftt()
        self.pushButton.clicked.connect(self.fftt)

    def fftt(self):
        # global fileName
        # fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        n=l
        T=1/sampling_rate
        yf = rfft(audio2)
        xf = rfftfreq(n,T)
        zf=np.abs(yf)
        self.fourWidget.plot(xf,zf,pen = "b")
        self.fourWidget2.plot(freqsa[:int(freqsa.size / 2)], fftabsafter[:int(freqsa.size / 2)], pen='r')
        # plt.plot(xf, np.abs(yf))
        # plt.grid()
        """ plt.xlable("Frequency -->")
        plt.ylable("Magnitude") """
        # plt.show()
        print("fftt")
        
        
def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window2 = MainApp2()
    window.show()
    window2.show()
    sys.exit(app.exec_())


if __name__=='__main__':
    main()