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
    
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        global gainArray
        global sliderArray
        sliderArray = []
        sliderArray=[self.verticalSlider,self.verticalSlider_2,self.verticalSlider_3,self.verticalSlider_4,self.verticalSlider_5,self.verticalSlider_6,self.verticalSlider_7,self.verticalSlider_8,self.verticalSlider_9,self.verticalSlider_10]
        self.graphWidgets=[self.graphWidget,self.graphWidget2]
 
        # design graphWidgets
        for i in range(2):
            self.graphWidgets[i].plotItem.showGrid(True, True, alpha=0.8)
            self.graphWidgets[i].setBackground('w')
        self.graphWidgets[0].plotItem.setTitle("Before Equalization")
        self.graphWidgets[1].plotItem.setTitle("After Equalization")
        
        # Add line to graph plot
        self.vLine = pg.InfiniteLine(movable=True, angle=90, pen=[75, 82, 159, 200])
        self.graphWidgets[0].addItem(self.vLine)
        self.vLine.setPos(100)

        self.comboBox.currentIndexChanged.connect(self.colorPallete)
        self.checkBox.stateChanged.connect(self.showSpectro)
        self.Menubar()
        self.Toolbar()
        self.showSpectro()
        self.loopslider()
        self.newWindows = []  
        
    def Menubar(self):
        self.actionOpen_signal.triggered.connect(self.BrowseSignal)
        self.actionSave_signal_as.triggered.connect(self.saveFile)
        self.actionExit.triggered.connect(self.close)
        self.Add_New_window.triggered.connect(self.addNewWindow)

    def Toolbar(self):
        self.OpenSignalBtn.triggered.connect(self.BrowseSignal)
        self.Save_signal.triggered.connect(self.saveFile)
        self.DrawSig.triggered.connect(self.speedTimer)
        self.AddPanel.triggered.connect(self.addNewWindow)
        self.PlayBtn.triggered.connect(self.play_audio)
        self.Stop.triggered.connect(self.stop_audio)
        self.ZoomIn.triggered.connect(self.zoomIn) 
        self.ZoomOut.triggered.connect(self.zoomOut) 
        self.LeftScroll.triggered.connect(self.ScrollLeft) 
        self.RightScroll.triggered.connect(self.ScrollRight)
        self.PDF.triggered.connect(self.printPDF) 
   
    def BrowseSignal(self):
        global fileName
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        global sampling_rate, audio2 
        audio2, sampling_rate = librosa.load(fileName, sr=None, duration=20.0)
        global length
        length = len(audio2)
        self.changeslidervalue()
        self.plotAudio(audio2, length)
        self.graphWidgets[0].plotItem.getViewBox().setLimits(xMin=0,xMax=length)
    
    def stop_audio(self):
        sd.stop()
        self.timer.stop()
    
    def speedTimer(self):
        for i in range(2):
            self.graphWidgets[i].plotItem.getViewBox().scaleBy(x=0.1, y=1) #Increases the scale of X axis and Y axis
        self.timer= QtCore.QTimer()
        self.timer.setInterval(20) #delay interval for dynamic signal
        self.timer.timeout.connect(self.DynamicSignal)
        # self.timer.timeout.connect(self.DynamicSignal2)
        #connect timer to our dynamic signal
        self.timer.start()

    def DynamicSignal(self):
        for i in range(2):
           self.graphWidgets[i].plotItem.getViewBox().translateBy(x=length/100, y=0)

    def plotAudio(self,file,length):
        self.graphWidgets[0].plot(file[0:length],pen="b")

    def play_audio(self):
        sd.play(adjusted_file, sampling_rate)
    
    def addNewWindow(self):
        window3=MainApp()
        window3.show()
        self.newWindows.append(window3)
        
    def zoomIn(self):
        for i in range(2):
           self.graphWidgets[i].plotItem.getViewBox().scaleBy(x=0.5, y=1) #Increases the scale of X axis and Y axis

    def zoomOut(self):
        for i in range(2):
           self.graphWidgets[i].plotItem.getViewBox().scaleBy(x=2, y=1) #Decreases scale of X axis and Y axis 

    def ScrollLeft(self):
        for i in range(2):
           self.graphWidgets[i].plotItem.getViewBox().translateBy(x=-1000, y=0)

    def ScrollRight(self):
        for i in range(2):
           self.graphWidgets[i].plotItem.getViewBox().translateBy(x=1000, y=0)

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
        self.processAudio(audio2, sampling_rate, *gainArray)
        return gainArray

    def processAudio(self, audio2, sampling_rate, gain1, gain2, gain3, gain4, gain5, gain6, gain7, gain8, gain9, gain10):
        window_length = length
        global yf
        yf = rfft(audio2)
        sample_spacing = 1/sampling_rate
        xf = rfftfreq(window_length, sample_spacing)
        global bandwidth
        bandwidth1=np.where(xf==((sampling_rate)/20))
        bandwidth=bandwidth1[0][0]
        print("type of bandwidth",type(bandwidth))
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
        self.plotting(new_yfft)
        self.colorPallete()
        self.play_audio()
        # ============================================================================

    def plotting(self,new_yfft):
        global adjusted_file
        adjusted_file = irfft(new_yfft)
        self.graphWidgets[1].plotItem.clear()
        self.graphWidgets[1].plot(adjusted_file,pen = "r")
        self.graphWidgets[1].plotItem.getViewBox().setLimits(xMin=0,xMax=length)
    
    def colorPallete(self):
        if self.comboBox.currentText()=='Palette 1':           
            self.spectro('viridis')
        elif self.comboBox.currentText()=='Palette 2':
            self.spectro('plasma')
        elif self.comboBox.currentText()=='Palette 3':
            self.spectro('cool')
        elif self.comboBox.currentText()=='Palette 4':
            self.spectro('rainbow')
        else:
            self.spectro('GnBu')
           
    def showSpectro(self):
        if self.checkBox.isChecked()==True:
            self.verticalWidget.show()
        else:
            self.verticalWidget.hide()

    def spectro(self,colorMap):
        fig = plt.figure()
        plt.subplot(111)
        self.spectrogram= plt.specgram(adjusted_file, Fs=sampling_rate, cmap=colorMap)
        fig.savefig('plot.png')
        self.upload()
            
    def upload(self):
        self.spectroWidget.setPixmap(QtGui.QPixmap("plot.png"))
        self.spectroWidget.setScaledContents(True)

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
        maximum = np.max(np.abs(adjusted_file))
        data = (adjusted_file / maximum).astype(np.float32)
        save = wavfile.write(filename, int(sampling_rate), data)
        plt.subplot(211)
        plot(adjusted_file)

    def saveFile(self):
        # allows the user to save the file and name it as they like
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export WAV", None, "WAV files (.wav);;All Files()"
        )
        if filename:
            if QtCore.QFileInfo(filename).suffix() == "":
                filename += ".wav"
            self.generate_WavFile(filename)

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
        yf = rfft(audio2)
        xf = rfftfreq(window_length, sample_spacing)
        
        self.fourWidget.plot(xf,np.abs(yf),pen = "b")
        print(len(new_yfft))
        print("len of yf",len(yf))
        print("len of xf",len(xf))
        self.fourWidget2.plot(xf[1:],np.abs(new_yfft)[ : len(xf)], pen='r')
        
def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window2 = MainApp2()
    window.show()
    window2.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()