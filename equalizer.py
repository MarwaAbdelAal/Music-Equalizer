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
from scipy.io import wavfile
from scipy import signal
import wave
from scipy.signal import firwin,freqz
import simpleaudio as sa
from scipy.fft import rfft, rfftfreq, fft, fftfreq, ifft, irfft
from matplotlib import pyplot as plt
import librosa
from scipy.signal import butter, lfilter
import sounddevice as sd
import math

MAIN_WINDOW,_=loadUiType(path.join(path.dirname(__file__),"sigview.ui"))
MAIN_WINDOW2,_=loadUiType(path.join(path.dirname(__file__),"fft2.ui"))




class MainApp(QMainWindow,MAIN_WINDOW):
    
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        # global gainArray
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
        self.Menubar()
        self.loopslider()
       
    #connecting menubar buttons to their functions
    def Menubar(self):
        self.actionOpen_signal.triggered.connect(self.BrowseSignal)
        self.actionSave_signal_as.triggered.connect(self.saveFile)
       
    def Toolbar(self):
        self.PlayBtn.triggered.connect(self.play_audio)
        self.OpenSignalBtn.triggered.connect(self.BrowseSignal)
        self.Stop.triggered.connect(self.stop_audio)
        self.LeftScroll.triggered.connect(self.ScrollLeft) 
        self.RightScroll.triggered.connect(self.ScrollRight)
        self.ZoomIn.triggered.connect(self.zoomIn) 
        self.ZoomOut.triggered.connect(self.zoomOut)
        self.spectrogram.triggered.connect(self.spectro) 

    def BrowseSignal(self):
        global fileName
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        global sampling_rate, audio2 
        audio2, sampling_rate = librosa.load(fileName, sr=None, duration=20.0)
        
        global l
        l=len(audio2)
        self.changeslidervalue()
        self.plotAudio(audio2,l)
        self.graphWidget.plotItem.getViewBox().setLimits(xMin=0,xMax=l)
    
    def saveFile(self):
        maximum = np.max(np.abs(adjusted_file))
        print(type(maximum))
        print('adjusted_file',type(adjusted_file))
        data = (adjusted_file / maximum).astype(np.float32)
        name="audiofile_output.wav"
        # name=name.format(self.flag)
        save = wavfile.write(name, int(sampling_rate), data)
        plt.subplot(211)
        plot(adjusted_file)

    def plotAudio(self,file,length):
        self.graphWidget.plot(file[0:length],pen="b")

    def play_audio(self):
        global wave_obj
        wave_obj = sa.WaveObject.from_wave_file(fileName)
        global play_obj
        play_obj = wave_obj.play()

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
        self.audioRun(*gainArray)
        return gainArray

    def audioRun(self,*gainArray):
        Rs = self.processAudio(audio2, sampling_rate, *gainArray)
        # self.plot(Rs,sampling_rate)

    # def processAudio(self, audio2, sampling_rate, gain1, gain2, gain3, gain4, gain5, gain6, gain7, gain8, gain9, gain10):
    #     global yf
    #     yf = rfft(audio2)
    #     global bandwidth
    #     xf = rfftfreq(n,T)
    #     bandwidth1=np.where(xf==((sampling_rate)/20))
    #     bandwidth=bandwidth1[0][0]
    #     # bandwidth=int(sampling_rate/20)
    #     # bandwidth =int(len(yf)/10)
    #     band1=np.abs(yf)[0:bandwidth]*gain1
    #     band2=np.abs(yf)[bandwidth:2*bandwidth]*gain2
    #     band3=np.abs(yf)[2*bandwidth:3*bandwidth]*gain3
    #     band4=np.abs(yf)[3*bandwidth:4*bandwidth]*gain4
    #     band5=np.abs(yf)[4*bandwidth:5*bandwidth]*gain5
    #     band6=np.abs(yf)[5*bandwidth:6*bandwidth]*gain6
    #     band7=np.abs(yf)[6*bandwidth:7*bandwidth]*gain7
    #     band8=np.abs(yf)[7*bandwidth:8*bandwidth]*gain8
    #     band9=np.abs(yf)[8*bandwidth:9*bandwidth]*gain9
    #     band10=np.abs(yf)[9*bandwidth:10*bandwidth]*gain10
    #     global new_yfft
    #     new_yfft=np.concatenate([band1,band2,band3,band4,band5,band6,band7,band8,band9,band10])
    #     print("len of new_yfft 1 = ", len(new_yfft))
    #     # new_yfft[len(new_yfft): len(yf)] = 0
    #     # print("len of new_yfft 2 = ", len(new_yfft))
    #     self.plotting()
    #     self.spectro()

    def processAudio(self, audio2, sampling_rate, gain1, gain2, gain3, gain4, gain5, gain6, gain7, gain8, gain9, gain10):
        n=l
        global yf
        yf = rfft(audio2)
        T=1/sampling_rate
        # print (yf)
        xf = rfftfreq(n,T)
        # global zf
        # zf=np.abs(yf)
        global bandwidth
        # bandwidth=int(sampling_rate/20)
        bandwidth1=np.where(xf==((sampling_rate)/20))
        bandwidth=int(bandwidth1[0][0])
        band1=np.abs(yf)[0:bandwidth]*gain1
        band2=np.abs(yf)[bandwidth:2*bandwidth]*gain2
        band3=np.abs(yf)[2*bandwidth:3*bandwidth]*gain3
        band4=np.abs(yf)[3*bandwidth:4*bandwidth]*gain4
        band5=np.abs(yf)[4*bandwidth:5*bandwidth]*gain5
        band6=np.abs(yf)[5*bandwidth:6*bandwidth]*gain6
        band7=np.abs(yf)[6*bandwidth:7*bandwidth]*gain7
        band8=np.abs(yf)[7*bandwidth:8*bandwidth]*gain8
        band9=np.abs(yf)[8*bandwidth:9*bandwidth]*gain9
        band10=np.abs(yf)[9*bandwidth:10*bandwidth]*gain10
        global new_yfft
        new_yfft=np.concatenate([band1,band2,band3,band4,band5,band6,band7,band8,band9,band10])
        print("len of new_yfft 1 = ", len(new_yfft))
        new_yfft[len(new_yfft): len(yf)] = 0
        print("len of new_yfft 2 = ", len(new_yfft))
        # self.plotting(new_yfft)
        self.plotting()
        self.spectro(new_yfft)
        
        # ============================================================================
    # def plot(self,signal, sample_rate):
    def plotting(self):
        # s = irfft(yf)
        global adjusted_file
        adjusted_file = irfft(new_yfft)
        self.graphWidget2.plotItem.clear()
        # self.graphWidget2.plot(s[0:len(s)],pen = "r")
        self.graphWidget2.plot(adjusted_file[0:len(adjusted_file)],pen="r")
        self.graphWidget2.plotItem.getViewBox().setLimits(xMin=0,xMax=l)
        # pass
    
    def spectro(self, draw):
        pg.setConfigOptions(imageAxisOrder='row-major')
        # the function that plot spectrogram of the selected signal
        f, t, Sxx = signal.spectrogram(draw,10)

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
        self.spectWidget.setLimits(xMin=t[0], xMax=t[-1], yMin=f[0], yMax=f[-1])

class MainApp2(QMainWindow,MAIN_WINDOW2):
    def __init__(self,parent=None):
        super(MainApp2,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.pushButton.clicked.connect(self.fftt)
    def fftt(self):
        
        n=l # number of points
        T=1/sampling_rate # sample spacing (spacing between points) = time step 
        global yf
        yf = rfft(audio2)
        xf = rfftfreq(n,T) # sample freq
        # print ( len (xf))
        # print (len(np.abs(yf)))
        self.fourWidget.plot(xf,np.abs(yf),pen = "b")
        # print(len(new_yfft))
        print("len of yf",len(yf))
        print("len of xf",len(xf))
        # self.fourWidget2.plot(xf,np.abs(new_yfft)[0 : len(xf)], pen='r')
        self.fourWidget2.plot(xf[ 0 : len(new_yfft)],np.abs(new_yfft), pen='r')
        # self.fourWidget2.plot(xf,np.abs(new_yfft), pen='r')
        # self.fourWidget2.plot(xf[ 0 : len(new_yfft)],np.abs(new_yfft), pen='r')
        # self.fourWidget2.plot(xf[1:],np.abs(new_yfft), pen='r')
        
def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window2 = MainApp2()
    window.show()
    window2.show()
    sys.exit(app.exec_())


if __name__=='__main__':
    main()