# -*- coding: utf-8 -*-

from __future__ import absolute_import
import Metashape
from PySide2 import QtCore, QtGui, QtWidgets,shiboken2
from pathlib import Path
import os
from os.path import dirname,exists,join,abspath
import glob
import sys
import importlib
import re

from ReloaderFiles.Ui_scriptReloader import Ui_Reloader
from ReloaderFiles import resources_Reloader


global currentFile
currentFile = str(__file__)


global mainpath
base = dirname(abspath(__file__))


mainpath = Path(base).parents[0]



global barMenu
barMenu = None
for w in QtWidgets.qApp.allWidgets():
    if w.inherits("QMenuBar"):
        ptr = shiboken2.getCppPointer(w)
        barMenu = shiboken2.wrapInstance(int(ptr[0]), QtWidgets.QWidget)


global listeModName
listeModName = [Path(f).stem for f in list(Path(mainpath).glob('*.py'))]


global listeModPath
listeModPath = [Path(f) for f in list(glob.glob('{}/*.py'.format(mainpath)))]




class Reloader(QtWidgets.QDialog):

    def __init__(self,parent):

        self.barMenu = barMenu        
        self.messageError = QtWidgets.QMessageBox()
        self.messageSuccess = QtWidgets.QMessageBox()
        self.modFound = None  
        QtWidgets.QDialog.__init__(self, parent)

        
        locale = QtCore.QLocale.system().name().split('_')[0]
        localepath = join(base,'Ui_scriptReloader_{}.qm'.format(locale))
        if exists(localepath):
            self.translator = QtCore.QTranslator()
            self.translator.load(localepath)
            QtCore.QCoreApplication.installTranslator(self.translator)
        self.ui = Ui_Reloader()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.fillCombo()
        self.run = False
        self.show()
             


    def fillCombo(self):

        for action in self.barMenu.actions()[9:] :
            if action.text() != 'Reloader':
                self.ui.comboPlugin.addItem(action.text())

    def selectFile(self):
        self.file = self.ui.comboPlugin.currentText()
        if self.file:
            return str(self.file)

    def getmod(self,mod):
        
        for f in listeModPath:
            if f == mod:
                return str(Path(mod).stem)

    def accept(self):

        self.name = self.selectFile()
        self.action = [action for action in self.barMenu.actions()[9:] if action.text() == self.name] 
        self.foundScript = [f for f in listeModName if f == self.name] 


        if not self.foundScript:
            self.listMod = [] 
            self.labels = []
            self.test = [] 
            self.labelName = None 
            self.otherScripts = [f for f in listeModPath if f.stem != self.name and f.as_posix() != currentFile]           
            
            for script in self.otherScripts:
                    with script.open() as f:
                        lines = f.readlines()
                        for line in lines: 
                            if 'Metashape.app.addMenuItem' in line :
                                if self.name in line:                       
                                    self.listMod.append(script)

                                                                                                   
                                elif self.name not in line:
                                    self.labelName = line.split(",")[0]                              
                                    self.labelName = self.labelName.split("(")[1]
                                    self.labels = [line for line in lines if line.startswith(self.labelName) or self.labelName in line and not 'Metashape.app.addMenuItem' in line
                                    and not ".{}".format(self.labelName) in line and not "({}".format(self.labelName) in line ]

                                    for label in self.labels:
                                        label= label.split('=')                                  
                                        label = re.sub(r"^\s+|\s+$", "", label[1])
                                        if "'\'" in label:
                                            label = label.split("'\'")[0]
                                            
                                        elif "/" in label:
                                            label = label.split("/")[0]
                                            
                                        if  "\'" in label:
                                            label = re.sub(r"\'", '',label)
                                            if label == self.name:                                                                                                          
                                                self.listMod.append(script)
                                        elif '\"' in label:
                                            label= re.sub(r'\"', '',label)
                                            if label == self.name:                                                                                                          
                                                self.listMod.append(script)

            
            if len(self.listMod) == 1 :
                for script in self.listMod:
                    self.barMenu.removeAction(self.action[0])
                    self.modFound = self.getmod(script)
                    importlib.import_module(self.modFound)
                    self.close()
                    self.messageSuccess.show()                    


            if len(self.listMod) >1:
                self.barMenu.removeAction(self.action[0])
                for script in self.listMod:
                    self.modFound = self.getmod(script)            
                    importlib.import_module(self.modFound)
                    self.close()
                    self.messageSuccess.show()
           
            if self.run == True:                                
                try:                  
                    del sys.modules[self.modFound]
                    importlib.reload(sys.modules[self.modFound])
                    self.run = False
                    self.close()
                    self.messageSuccess.show()
                


                except:
                    self.barMenu.removeAction(self.action[0])
                    importlib.import_module(self.modFound)

                    self.run = False
                    self.close()
                    self.messageSuccess.show()
            

        else:
            try:
                
                del sys.modules[self.name]
                importlib.reload(sys.modules[self.name])
                self.close()
                self.messageSuccess.show()                


            except:
                self.barMenu.removeAction(self.action[0])
                importlib.import_module(self.name)
                self.close()
                self.messageSuccess.show()




def main():

    app = QtWidgets.QApplication.instance()
    parent = app.activeWindow()
    Reloader(parent)



ico = ":/ReloaderFiles/reload.png"
Metashape.app.addMenuItem("Reloader", main ,icon=ico)
