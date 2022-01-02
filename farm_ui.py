import sys
import os
import urllib2

from PySide2 import QtCore, QtGui, QtUiTools, QtWidgets
import shiboken2,subprocess,json
import maya.cmds as cmds
import maya.OpenMayaUI as MayaUI
import gen_main
import ui
import farm_submission

SCRIPT_LOC = os.path.split(__file__)[0]


def loadUiWidget(uifilename, parent=None):
    loader = QtUiTools.QUiLoader()
    uifile = QtCore.QFile(uifilename)
    uifile.open(QtCore.QFile.ReadOnly)
    ui = loader.load(uifile, parent)
    uifile.close()
    return ui


def runMayaTemplateUi(main_ui):
    if not (cmds.window("templateUi", exists=True)):
        TemplateUi(main_ui)
    else:
        sys.stdout.write("Tool is already open!\n")


class TemplateUi(QtWidgets.QMainWindow):
    def __init__(self, main_ui = None, **kwargs):
        mainUI = SCRIPT_LOC + '\\farm.ui'
        print (mainUI)
        MayaMain = shiboken2.wrapInstance(long(MayaUI.MQtUtil.mainWindow()), QtWidgets.QWidget)
        super(TemplateUi, self).__init__(MayaMain)
        self.main_ui = main_ui

        # main window load / settings
        self.MainWindowUI = loadUiWidget(mainUI, MayaMain)
        self.MainWindowUI.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.MainWindowUI.destroyed.connect(self.onExitCode)
        self.MainWindowUI.show()
        self.onStart()
        self.MainWindowUI.pushButton_save.clicked.connect(self.save_onclick)
        self.MainWindowUI.pushButton_test.clicked.connect(self.test_onclick)

    def onExitCode(self):
        """Do this when the script is closed"""
        sys.stdout.write("UI successfully closed\n")

    def onStart(self):
        self.MainWindowUI.lineEdit_maya_project.setText(self.main_ui.projectDirectory)
        self.MainWindowUI.lineEdit_deadlineweb.setText(self.main_ui.config['dealineurl'])
        self.MainWindowUI.lineEdit_batch.setText(self.main_ui.config['batch_name'])
        self.MainWindowUI.lineEdit_version.setText(self.main_ui.config['maya_version'])
        self.MainWindowUI.lineEdit_priority.setText(self.main_ui.config['priority'])
        self.MainWindowUI.lineEdit_pool.setText(self.main_ui.config['pool'])
        self.MainWindowUI.lineEdit_output.setText(self.main_ui.gen_project_path + '/render/')
        self.test_onclick()


    def save_onclick(self):
        self.main_ui.config['dealineurl'] = self.MainWindowUI.lineEdit_deadlineweb.text()
        self.main_ui.config['batch_name'] = self.MainWindowUI.lineEdit_batch.text()
        self.main_ui.config['maya_version'] = self.MainWindowUI.lineEdit_version.text()
        self.main_ui.config['priority'] = self.MainWindowUI.lineEdit_priority.text()
        self.main_ui.config['pool'] = self.MainWindowUI.lineEdit_pool.text()
        gen_main.write_to_json(self.main_ui.config_file,self.main_ui.config)
        self.feedback('Saved deadline config.')
    
    def test_onclick(self):
        r = farm_submission.request('GET',self.MainWindowUI.lineEdit_deadlineweb.text())
        self.feedback(r[0])
        if r[1] == 200:
            self.main_ui.log('deadline server is running')
        else:
            self.main_ui.log('deadline server is NOT running')
    
    def feedback(self,text):
        self.MainWindowUI.lineEdit_feed.setText(text)