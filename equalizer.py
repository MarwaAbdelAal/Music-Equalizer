from PyQt5 import QtWidgets, QtCore, uic, QtGui
from pyqtgraph import PlotWidget, plot
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import *   
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy import signal
from os import path
import pyqtgraph as pg
import numpy as np
import sys
import os
from scipy.io import wavfile
from scipy import signal
import simpleaudio as sa
from scipy.fft import rfft, rfftfreq, fft, fftfreq, ifft, irfft
from matplotlib import pyplot as plt
import librosa
import sounddevice as sd
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from fpdf import FPDF
import pyqtgraph.exporters

MAIN_WINDOW,_=loadUiType(path.join(path.dirname(__file__),"sigview.ui"))
MAIN_WINDOW2,_=loadUiType(path.join(path.dirname(__file__),"fft2.ui"))

class MainApp(QMainWindow,MAIN_WINDOW):
    # Some Variables initialization
    sliderArray = []
    gainArray = []
    fileName, sampling_rate, audioData, length = 0

    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.timer= QtCore.QTimer()
        self.speed = 150        
        sliderArray=[self.verticalSlider,self.verticalSlider_2,self.verticalSlider_3,self.verticalSlider_4,self.verticalSlider_5,self.verticalSlider_6,self.verticalSlider_7,self.verticalSlider_8,self.verticalSlider_9,self.verticalSlider_10]
        self.graphWidgets=[self.graphWidget,self.graphWidget2]
 
        # design graphWidgets
        for i in range(2):
            self.graphWidgets[i].plotItem.showGrid(True, True, alpha=0.8)
            self.graphWidgets[i].setBackground('w')
        self.graphWidgets[0].plotItem.setTitle("Before Equalization")
        self.graphWidgets[1].plotItem.setTitle("After Equalization")

        self.comboBox.currentIndexChanged.connect(self.colorPallete)
        self.checkBox.stateChanged.connect(self.showSpectro)
        self.Menubar()
        self.Toolbar()
        self.showSpectro()
        self.ConnectSliders()
        self.newWindows = []  
        
    def Menubar(self):
        self.actionOpen_signal.triggered.connect(self.BrowseSignal)
        self.actionSave_signal_as.triggered.connect(self.saveFile)
        self.actionExit.triggered.connect(self.close)
        self.Add_New_window.triggered.connect(self.addNewWindow)

    def Toolbar(self):
        self.OpenSignalBtn.triggered.connect(self.BrowseSignal)
        self.DrawSig.triggered.connect(self.PlottingTimer)
        self.actionSpeed_Up.triggered.connect(lambda: self.speed_up())
        self.actionSpeed_down.triggered.connect(lambda: self.speed_down())
        self.AddPanel.triggered.connect(self.addNewWindow)
        self.PlayBtn.triggered.connect(self.play_audio)
        self.Stop.triggered.connect(self.stop_audio)
        self.ZoomIn.triggered.connect(self.zoomIn) 
        self.ZoomOut.triggered.connect(self.zoomOut) 
        self.LeftScroll.triggered.connect(self.ScrollLeft) 
        self.RightScroll.triggered.connect(self.ScrollRight)
        self.PDF.triggered.connect(self.printPDF) 
        self.Save_signal.triggered.connect(self.saveFile) 
        self.ShowFftButton.triggered.connect(self.showFFT) 

    def BrowseSignal(self):
        global fileName, sampling_rate, audioData, length
        self.graphWidgets[0].plotItem.clear()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        audioData, sampling_rate = librosa.load(fileName, sr=None, duration=20.0)
        length = len(audioData)
        self.changeslidervalue()
        self.plotAudio(audioData, length)
        self.graphWidgets[0].plotItem.getViewBox().setLimits(xMin=0,xMax=length)
    
    def plotAudio(self,file,length):
        self.graphWidgets[0].plot(file[0:length],pen="b")

    def PlottingTimer(self):
        for i in range(2):
            self.timer.stop()
            self.timer = QtCore.QTimer()
            self.timer.setInterval(self.speed)
            print ('speed:', self.speed)
    
            self.timer.timeout.connect(self.PlottingTimer)
            self.timer.start()
            xrange, yrange = self.graphWidgets[i].viewRange()
            scrollvalue = (xrange[1] - xrange[0])/50
            print('xrange[1]= ', xrange[1], 'xrange[0]= ', xrange[0])
            print('yrange[1]= ', yrange[1], 'yrange[0]= ', yrange[0])
            print('scrollvalue= ', scrollvalue)
            self.graphWidgets[i].setXRange(xrange[0]+scrollvalue, xrange[1]+scrollvalue, padding=0)

    def speed_up(self):
        if self.speed == 10:
            self.speed = 0
        elif self.speed > 0:
            self.speed -= 20
        self.PlottingTimer()     

    def speed_down(self):
        self.speed += 20
        self.PlottingTimer()

    def play_audio(self):
        sd.play(adjusted_audio, sampling_rate)

    def stop_audio(self):
        sd.stop()
        self.timer.stop()

    def changeslidervalue(self):
        global i
        i = 0
        gainArray = []
        while i < 10:
            gainArray.append(sliderArray[i].value())
            i += 1
        self.processAudio(audioData, sampling_rate, *gainArray)
        return gainArray

    def ConnectSliders(self):
        global i
        i = 0
        while i < 10:
            sliderArray[i].valueChanged.connect(self.changeslidervalue)
            i += 1

    def processAudio(self, audioData, sampling_rate, gain1, gain2, gain3, gain4, gain5, gain6, gain7, gain8, gain9, gain10):
        window_length = length
        sample_spacing = 1/sampling_rate
        global yf
        yf = rfft(audioData)
        xf = rfftfreq(window_length, sample_spacing)
        global bandwidth
        # bandwidth=len(xf)/10
        bandwidth1=np.where(xf==((sampling_rate)/20))
        bandwidth=bandwidth1[0][0]
        band1=yf[0:bandwidth]*gain1
        band2=yf[bandwidth:2*bandwidth]*gain2
        band3=yf[2*bandwidth:3*bandwidth]*gain3
        band4=yf[3*bandwidth:4*bandwidth]*gain4
        band5=yf[4*bandwidth:5*bandwidth]*gain5
        band6=yf[5*bandwidth:6*bandwidth]*gain6
        band7=yf[6*bandwidth:7*bandwidth]*gain7
        band8=yf[7*bandwidth:8*bandwidth]*gain8
        band9=yf[8*bandwidth:9*bandwidth]*gain9
        band10=yf[9*bandwidth:10*bandwidth]*gain10
        global new_yfft
        new_yfft=np.concatenate([band1,band2,band3,band4,band5,band6,band7,band8,band9,band10])
        new_yfft[len(new_yfft): len(yf)] = 0
        self.PlotNewSignal(new_yfft)
        self.colorPallete()
        self.play_audio()
        # ============================================================================

    def PlotNewSignal(self,new_yfft):
        global adjusted_audio
        adjusted_audio = irfft(new_yfft)
        self.graphWidgets[1].plotItem.clear()
        self.graphWidgets[1].plot(adjusted_audio,pen = "r")
        self.graphWidgets[1].plotItem.getViewBox().setLimits(xMin=0,xMax=length)
    
    def addNewWindow(self):
        window3=MainApp()
        window3.show()
        self.newWindows.append(window3)
        
    def zoomIn(self):
        # self.timer.stop()
        for i in range(2):
           self.graphWidgets[i].plotItem.getViewBox().scaleBy(x=0.5, y=1) #Increases the scale of X axis and Y axis

    def zoomOut(self):
        # self.timer.stop()
        for i in range(2):
           self.graphWidgets[i].plotItem.getViewBox().scaleBy(x=2, y=1) #Decreases scale of X axis and Y axis 

    def ScrollLeft(self):
        self.timer.stop()
        for i in range(2):
           self.graphWidgets[i].plotItem.getViewBox().translateBy(x=-(length/1000), y=0)

    def ScrollRight(self):
        self.timer.stop()
        for i in range(2):
           self.graphWidgets[i].plotItem.getViewBox().translateBy(x=(length/1000), y=0)
    
    def colorPallete(self):
        if self.comboBox.currentText()=='Palette 1':           
            self.spectro('viridis')
            self.spectroBefore('viridis')
        elif self.comboBox.currentText()=='Palette 2':
            self.spectro('plasma')
            self.spectroBefore('plasma')
        elif self.comboBox.currentText()=='Palette 3':
            self.spectro('cool')
            self.spectroBefore('cool')
        elif self.comboBox.currentText()=='Palette 4':
            self.spectro('rainbow')
            self.spectroBefore('rainbow')
        else:
            self.spectro('GnBu')
            self.spectroBefore('GnBu')

    def spectroBefore(self,colorMap):
        fig = plt.figure()
        plt.subplot(111)
        self.spectrogram= plt.specgram(audioData, Fs=sampling_rate, cmap=colorMap)
        plt.colorbar()
        fig.savefig('plot1.png')
        self.upload1()

    def spectro(self,colorMap):
        fig = plt.figure()
        plt.subplot(111)
        self.spectrogram= plt.specgram(adjusted_audio, Fs=sampling_rate, cmap=colorMap)
        plt.colorbar()
        fig.savefig('plot.png')
        self.upload()
    
    def upload1(self):
        self.spectroWidget2.setPixmap(QtGui.QPixmap("plot1.png"))
        self.spectroWidget2.setScaledContents(True)

    def upload(self):
        self.spectroWidget.setPixmap(QtGui.QPixmap("plot.png"))
        self.spectroWidget.setScaledContents(True)

    def showSpectro(self):
        if self.checkBox.isChecked()==True:
            self.verticalWidget.show()
        else:
            self.verticalWidget.hide()

    def generatePDF(self, filename):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 15)
        pdf.set_xy(0,0)
        for i in range(2):
            pdf.cell(0, 10,ln=1,align='C')
            exporter = pg.exporters.ImageExporter(self.graphWidgets[i].plotItem)               
            exporter.parameters()['width'] = 250  
            exporter.parameters()['height'] = 250         
            exporter.export('fileName'+str(i+1)+'.png')
            pdf.image(('fileName'+str(i+1)+'.png'),x=None,y=None, w=180,h=70)

        pdf.cell(0, 10,ln=1,align='C')
        pdf.image('plot1.png',x=None,y=None, w=200,h=100)

        pdf.cell(0, 10,ln=1,align='C')
        pdf.image('plot.png',x=None,y=None, w=200,h=100)

        pdf.output(filename)

    def printPDF(self):
        # allows the user to save the file and name it as they like
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export PDF", None, "PDF files (.pdf);;All Files()"
        )
        if filename:
            if QtCore.QFileInfo(filename).suffix() == "":
                filename += ".pdf"
            self.generatePDF(filename)

    def generate_WavFile(self, filename):
        maximum = np.max(np.abs(adjusted_audio))
        data = (adjusted_audio / maximum).astype(np.float32)
        save = wavfile.write(filename, int(sampling_rate), data)
        plt.subplot(211)
        plot(adjusted_audio)

    def saveFile(self):
        # allows the user to save the file and name it as they like
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export WAV", None, "WAV files (.wav);;All Files()"
        )
        if filename:
            if QtCore.QFileInfo(filename).suffix() == "":
                filename += ".wav"
            self.generate_WavFile(filename)
    def showFFT(self):
        window2.show()

class MainApp2(QMainWindow,MAIN_WINDOW2):
    def __init__(self,parent=None):
        super(MainApp2,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.pushButton.clicked.connect(self.fftt)
        
    def fftt(self):
        window_length = length
        sample_spacing = 1/sampling_rate  
        global yf
        yf = rfft(audioData)
        xf = rfftfreq(window_length, sample_spacing)
        
        self.fourWidget.plot(xf,np.abs(yf),pen = "b")
        print(len(new_yfft))
        print("len of yf",len(yf))
        print("len of xf",len(xf))
        self.fourWidget2.plot(xf[1:],np.abs(new_yfft)[ : len(xf)], pen='r')
        
def main():
    app = QApplication(sys.argv)
    window = MainApp()
    global window2
    window2 = MainApp2()
    window.show()
    # window2.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()