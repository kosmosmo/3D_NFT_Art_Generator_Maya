import sys
import os,subprocess
import urllib2,urllib
from PySide2 import QtCore, QtGui, QtUiTools, QtWidgets
import shiboken2,subprocess,json
import maya.cmds as cmds
import maya.OpenMayaUI as MayaUI
import gen_main
import farm_submission

SCRIPT_LOC = os.path.split(__file__)[0]


def loadUiWidget(uifilename, parent=None):
    loader = QtUiTools.QUiLoader()
    uifile = QtCore.QFile(uifilename)
    uifile.open(QtCore.QFile.ReadOnly)
    ui = loader.load(uifile, parent)
    uifile.close()
    return ui


def runMayaTemplateUi():
    if not cmds.file(q=True, sn=True):
        cmds.confirmDialog(
            title='Error',
            message='Project not set or file not saved.',
            button=['Cancel'],
            cancelButton='Cancel'
        )
    if not (cmds.window("templateUi", exists=True)):
        TemplateUi()
    else:
        sys.stdout.write("Tool is already open!\n")


class TemplateUi(QtWidgets.QMainWindow):
    def __init__(self):
        mainUI = SCRIPT_LOC + '\\main.ui'
        MayaMain = shiboken2.wrapInstance(long(MayaUI.MQtUtil.mainWindow()), QtWidgets.QWidget)
        super(TemplateUi, self).__init__(MayaMain)

        # main window load / settings
        self.MainWindowUI = loadUiWidget(mainUI, MayaMain)
        self.MainWindowUI.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.MainWindowUI.destroyed.connect(self.onExitCode)
        self.MainWindowUI.show()

        self.projectDirectory = cmds.workspace(q=True, rd=True)
        self.filepath = cmds.file(q=True, sn=True)
        self.filename = os.path.basename(self.filepath)
        self.filename_no_ext = self.filename.rsplit(".", 1)[0].split("#")[0]
        self.config_file = SCRIPT_LOC + '\\config.json'
        self.gen_project_path = ''
        self.layer_map_json = ''
        self.trait_map_json = ''
        self.config = ''

        self.onStart()
        #step1
        self.MainWindowUI.lineEdit_project_folder_1.textChanged.connect(self.update_project_path)
        self.MainWindowUI.pushButton_set_1.clicked.connect(lambda: self.set_project(self.MainWindowUI.lineEdit_project_1.text()))
        self.MainWindowUI.pushButton_open_1.clicked.connect(lambda: gen_main.open_folder(self.MainWindowUI.lineEdit_project_1.text()))
        # self.makeConnections()

        # step2
        self.MainWindowUI.pushButton_layer_map_2.clicked.connect(self.layer_map_button_onclick )
        self.MainWindowUI.pushButton_open_layer_map_2.clicked.connect(self.layer_map_file_open)

        # step3
        self.MainWindowUI.pushButton_weight_edit_3.clicked.connect(self.weight_edit)

        # step4
        self.MainWindowUI.lineEdit_total_art_4.textChanged.connect(self.art_changed)
        self.MainWindowUI.pushButton_gen_trait_4.clicked.connect(self.gen_trait_onclick)

        # step5
        self.MainWindowUI.pushButton_gen_5.clicked.connect(self.gen_onclick)
        self.MainWindowUI.pushButton_clear_5.clicked.connect(self.clear_onclick)
        self.MainWindowUI.checkBox_rend_over_5.clicked.connect(self.rend_over_onclick)
        self.MainWindowUI.comboBox_camera_5.currentIndexChanged.connect(self.camera_changed)
        self.MainWindowUI.lineEdit_width_5.textChanged.connect(self.height_width_changed)
        self.MainWindowUI.lineEdit_height_5.textChanged.connect(self.height_width_changed)
        self.MainWindowUI.lineEdit_key_5.textChanged.connect(self.key_changed)
        self.MainWindowUI.checkBox_aa_5.clicked.connect(self.aa_onclick)
        self.MainWindowUI.lineEdit_aa_5.setText(str(self.MainWindowUI.horizontalSlider_aa_5.value()))
        self.MainWindowUI.horizontalSlider_aa_5.valueChanged.connect(self.aa_slide_changed)
        self.MainWindowUI.pushButton_farm_set_5.clicked.connect(self.open_farm_set)

        # step6
        self.MainWindowUI.pushButton_farm_set_6.clicked.connect(self.open_farm_set)
        self.MainWindowUI.pushButton_render_6.clicked.connect(self.render_onclick)
        self.MainWindowUI.pushButton_clearlog_6.clicked.connect(lambda: self.log('',clear=True))

        self.log('running.')

        


    def onStart(self):
        self.MainWindowUI.lineEdit_project_folder_1.setText(self.filename_no_ext)
        self.update_project_path()
        self.get_render_global()
        self.config = gen_main.load_json(self.config_file)
        self.MainWindowUI.lineEdit_total_art_4.setText(str(self.config["total_art"]))
        self.MainWindowUI.lineEdit_key_5.setText( self.MainWindowUI.lineEdit_total_art_4.text())
        self.MainWindowUI.lineEdit_scene_5.setText('1')
        self.MainWindowUI.checkBox_rend_farm_6.setChecked(True)
        self.MainWindowUI.textEdit_log.setText(self.config['log'])
        self.update_json_path()

    def onExitCode(self):
        """Do this when the script is closed"""
        sys.stdout.write("UI successfully closed\n")

    def update_project_path(self):
        self.MainWindowUI.lineEdit_project_1.setText(self.projectDirectory + self.MainWindowUI.lineEdit_project_folder_1.text())
        self.update_json_path()

    def set_project(self,folder):
        if not os.path.exists(folder):os.makedirs(folder)
        if not os.path.exists(folder+ '/scenes'):os.makedirs(folder + '/scenes')
        if not os.path.exists(folder+ '/render'):os.makedirs(folder + '/render')
        self.update_json_path()
        self.log('Set project folder:'+self.MainWindowUI.lineEdit_project_1.text())



    def layer_map_button_onclick(self):
        layer_map = gen_main.create_layer_map_json()
        gen_main.write_to_json(self.layer_map_json,layer_map)
        self.update_json_path()
        self.log('Created layer map file!')

    def layer_map_file_open(self):
        if not os.path.isfile(self.layer_map_json):
            self.log('Layer map not created yet.')
            return
        subprocess.Popen(["notepad.exe",self.layer_map_json])

    def update_json_path(self):
        self.layer_map_json = self.MainWindowUI.lineEdit_project_1.text()+ '/layers_map.json'
        self.trait_map_json =  self.MainWindowUI.lineEdit_project_1.text()+ '/traits_map.json'
        if os.path.isfile(self.layer_map_json):
            self.MainWindowUI.lineEdit_layer_map_path_3.setText(self.layer_map_json)
        else:
            self.MainWindowUI.lineEdit_layer_map_path_3.setText('')

    def art_changed(self):
        total_art = self.MainWindowUI.lineEdit_total_art_4.text()
        if total_art == '':
            return
        if not total_art.isdigit():
            self.MainWindowUI.lineEdit_total_art_4.setText(total_art[:-1])
            return
        self.MainWindowUI.lineEdit_key_5.setText(self.MainWindowUI.lineEdit_total_art_4.text())
        self.MainWindowUI.lineEdit_scene_5.setText('1')
        self.config['total_art'] = int(total_art)
        gen_main.write_to_json(self.config_file,self.config)

    def gen_trait_onclick(self):
        if not os.path.isfile(self.layer_map_json):
            self.log('Run step 2 first.')
            return
        total_art = int(self.MainWindowUI.lineEdit_total_art_4.text())
        trait_map = gen_main.generate_trait_map(self.layer_map_json,total_art)
        gen_main.write_to_json(self.trait_map_json,trait_map)
        self.log('Created trait map')


    def get_render_global(self):
        width = cmds.getAttr('defaultResolution.width')
        height = cmds.getAttr('defaultResolution.height')
        self.MainWindowUI.lineEdit_width_5.setText(str(width))
        self.MainWindowUI.lineEdit_height_5.setText(str(height))
        cameras = cmds.ls(type=('camera'), l=True)
        self.MainWindowUI.comboBox_camera_5.addItems(cameras)
        for cam in cameras:
            if cmds.getAttr(cam+'.renderable') == True:
                index = self.MainWindowUI.comboBox_camera_5.findText(cam, QtCore.Qt.MatchFixedString)
                self.MainWindowUI.comboBox_camera_5.setCurrentIndex(index)

    def gen_onclick(self):
        if not os.path.isfile(self.trait_map_json):
            self.log('Run step 4 first.')
            return
        trait_map = gen_main.load_json(self.trait_map_json)
        layer_map = gen_main.load_json(self.layer_map_json)
        gen_main.set_keys(trait_map,layer_map,None)
        gen_path = self.MainWindowUI.lineEdit_project_1.text() + "/scenes/" + self.filename_no_ext + '#gen.ma'
        cmds.file(rename=self.MainWindowUI.lineEdit_project_1.text() + "/scenes/" + self.filename_no_ext + '#gen.ma')
        cmds.file(save=True, type="mayaAscii")
        if self.MainWindowUI.checkBox_ao.isChecked() == True:
            root = gen_main.get_root()
            def create_shader(name, node_type="aiAmbientOcclusion"):
                material = cmds.shadingNode(node_type, name=name, asShader=True)
                sg = cmds.sets(name="%sSG" % name, empty=True, renderable=True, noSurfaceShader=True)
                cmds.connectAttr("%s.outColor" % material, "%s.surfaceShader" % sg)
                return [material, sg]
            shaders = create_shader('gen_ao')
            cmds.setAttr(shaders[0] + '.falloff',3)
            cmds.select(root)
            cmds.sets(e=True,forceElement=shaders[1])
            cmds.file(
                rename=self.MainWindowUI.lineEdit_project_1.text() + "/scenes/" + self.filename_no_ext + '#ao.ma')
            cmds.file(save=True, type="mayaAscii")
            cmds.file(gen_path, o=True)
            self.log('AO file created')
        self.log('Master file created')
        #cmds.file(self.filepath, o=True)

    def clear_onclick(self):
        layer_map = gen_main.load_json(self.layer_map_json)
        gen_main.clear_keys(layer_map)
        self.log('clear key frames for current file')

    def rend_over_onclick(self):
        if self.MainWindowUI.checkBox_rend_over_5.isChecked() == True:
            self.MainWindowUI.lineEdit_width_5.setEnabled(True)
            self.MainWindowUI.lineEdit_height_5.setEnabled(True)
            self.MainWindowUI.comboBox_camera_5.setEnabled(True)
        else:
            self.MainWindowUI.lineEdit_width_5.setEnabled(False)
            self.MainWindowUI.lineEdit_height_5.setEnabled(False)
            self.MainWindowUI.comboBox_camera_5.setEnabled(False)

    def camera_changed(self):
        current_cam = self.MainWindowUI.comboBox_camera_5.currentText()
        cameras = cmds.ls(type=('camera'), l=True)
        for cam in cameras:
            if cam == current_cam:
                cmds.setAttr(current_cam+'.renderable', True)
            else:
                cmds.setAttr(cam + '.renderable', False)

    def height_width_changed(self):
        cmds.setAttr('defaultResolution.width',int(self.MainWindowUI.lineEdit_width_5.text()))
        cmds.setAttr('defaultResolution.height', int(self.MainWindowUI.lineEdit_height_5.text()))

    def key_changed(self):
        total = int(self.MainWindowUI.lineEdit_total_art_4.text())
        key = self.MainWindowUI.lineEdit_key_5.text()
        if key == '' or not key.isdigit() or key == '0':
            key = 1
        else:
            key = int(self.MainWindowUI.lineEdit_key_5.text())
        scene = total/key + (total%key > 0)
        self.MainWindowUI.lineEdit_scene_5.setText(str(scene))
        if key > total:
            self.MainWindowUI.lineEdit_key_5.setText(str(self.MainWindowUI.lineEdit_total_art_4.text()))
            self.MainWindowUI.lineEdit_scene_5.setText('1')


    def aa_onclick(self):
        if self.MainWindowUI.checkBox_aa_5.isChecked() == True:
            self.MainWindowUI.horizontalSlider_aa_5.setEnabled(True)
        else:
            self.MainWindowUI.horizontalSlider_aa_5.setEnabled(False)

    def aa_slide_changed(self):
        aa = self.MainWindowUI.horizontalSlider_aa_5.value()
        self.MainWindowUI.lineEdit_aa_5.setText(str(aa))
        cmds.setAttr( "defaultArnoldRenderOptions.AASamples",aa)


    def open_farm_set(self):
        self.gen_project_path = self.MainWindowUI.lineEdit_project_1.text()
        import farm_ui
        farm_ui.runMayaTemplateUi(self)
    
    def render_onclick(self):
        scene_folder = self.MainWindowUI.lineEdit_project_1.text() + '/scenes/'
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [scene_folder + f for f in listdir(scene_folder) if (isfile(join(scene_folder, f)) and f.endswith('.ma'))]
        for scene in onlyfiles:
            frame = '0-{}'.format(self.MainWindowUI.lineEdit_total_art_4.text())
            output = self.MainWindowUI.lineEdit_project_1.text() + '/render/'
            r = farm_submission.submit_to_deadline(scene,frame,output,self.config)
            base = os.path.basename(scene)
            if r[1] == 200:
                self.log(base + ' submitted')
            else:
                self.log(base + ' failed')

    
    def log(self,text,clear=False):
        if not clear:
            from datetime import datetime
            now = datetime.now()
            current_time = str(now.strftime("%m/%d-%H:%M:%S")) + ': '
            self.config['log'] =self.config['log'] + '\n' + current_time + text
        else:
            self.config['log'] = ''
        gen_main.write_to_json(self.config_file,self.config)
        self.MainWindowUI.textEdit_log.setText(self.config['log'])
        self.MainWindowUI.textEdit_log.verticalScrollBar().setValue(self.MainWindowUI.textEdit_log.verticalScrollBar().maximum())

    def weight_edit(self):
        cmds.confirmDialog(
            title='Error',
            message='Use Step2 Notepad to edit weight',
            button=['Cancel'],
            cancelButton='Cancel'
        )
        pass


