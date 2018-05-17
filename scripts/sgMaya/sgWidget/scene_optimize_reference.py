#coding=utf-8

from maya import cmds, OpenMaya
import maya.OpenMayaUI
import pymel.core
import copy
import os, json

from maya import cmds

if int(cmds.about(v=1)) < 2017:
    from PySide import QtGui, QtCore
    import shiboken
    from PySide.QtGui import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QColor, QLabel, \
        QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QCursor, QMessageBox, QBrush, \
        QSplitter, \
        QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QDoubleValidator, QSlider, \
        QIntValidator, \
        QImage, QPixmap, QTransform, QPaintEvent, QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, \
        QGroupBox, QAction, \
        QFont, QGridLayout, QAbstractScrollArea
else:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    from PySide2.QtWidgets import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QVBoxLayout, QLabel, \
        QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QMessageBox, QSplitter, \
        QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QSlider, \
        QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction, QGridLayout, QAbstractScrollArea

    from PySide2.QtGui import QColor, QCursor, QBrush, QDoubleValidator, QIntValidator, QImage, QPixmap, QTransform, \
        QPaintEvent, QFont



path_basedir = cmds.about(pd=1) + "/pingo/scene_optimize_reference"
path_refereceBaseInfo = cmds.about(pd=1) + "/pingo/scene_optimize_export/referenceBasePath.txt"


class Cmds_file_control(object):

    def __init__(self, *args, **kwargs):
        pass


    def makeFolder(self, pathName):
        if os.path.exists(pathName): return None
        os.makedirs(pathName)
        return pathName


    def makeFile(self, filePath):
        if os.path.exists(filePath): return None
        filePath = filePath.replace("\\", "/")
        splits = filePath.split('/')
        folder = '/'.join(splits[:-1])
        self.makeFolder(folder)
        f = open(filePath, "w")
        json.dump({}, f)
        f.close()


    def writeData(self, data, filePath):
        self.makeFile(filePath)
        f = open(filePath, 'w')
        json.dump(data, f, indent=2)
        f.close()


    def readData(self, filePath):
        self.makeFile(filePath)

        f = open(filePath, 'r')
        data = {}
        try:
            data = json.load(f)
        except:
            pass
        f.close()

        return data


    def save_shapeInfo(self, path):

        data = self.readData(path)
        data['x'] = self.x()
        data['y'] = self.y()
        data['width'] = self.width()
        data['height'] = self.height()
        self.writeData(data, path)


    def load_shapeInfo(self, path):

        data = self.readData(path)
        try:
            x = data['x']
            y = data['y']
            width = data['width']
            height = data['height']
        except:
            return
        self.move(x, y)
        self.resize(width, height)


    def save_lineEdit_text(self, lineEdit, path ):

        data = self.readData( path )
        data['lineEdit'] = lineEdit.text()
        self.writeData( data, path )


    def load_lineEdit_text(self, lineEdit, path ):

        data = self.readData( path )
        if data.has_key( 'lineEdit' ):
            lineEdit.setText( data['lineEdit'] )


    def save_comboBox(self, comboBox, path ):

        data = self.readData( path )
        data[ 'selectedItem' ] = comboBox.currentText()
        self.writeData( data, path )


    def load_comboBox(self, comboBox, path ):

        data = self.readData( path )
        if data.has_key( 'selectedItem' ):
            itemText = data['selectedItem' ]
        else:
            return
        for i in range( comboBox.count() ):
            if itemText == comboBox.itemText( i ):
                comboBox.setCurrentIndex( i )
                break

    def get_csv_form_google_spreadsheets( self, link_attributeList, targetPath):

        #print "before get google spreadsheets"
        import re, urllib, urllib2, os, ssl
        p = re.compile('/d/.+/')
        m = p.search(link_attributeList)
        id_sheet = m.group()[3:-1]
        dirPath = os.path.dirname(targetPath)
        if not os.path.exists(dirPath): os.makedirs( dirPath )
        link_donwload_attributeList = 'https://docs.google.com/spreadsheets/d/%s/export?format=csv' % id_sheet
        try:
            context = ssl._create_unverified_context()
            response = urllib2.urlopen(link_donwload_attributeList,
                                       context=context)  # How should i pass authorization details here?
            data = response.read()
            f = open(targetPath, 'w')
            f.write(data)
            f.close()
        except:
            testfile = urllib.URLopener()
            testfile.retrieve(link_donwload_attributeList, targetPath)
        #print "after get google spreadsheets"


    def get_dictList_from_csvPath( self, csvPath):

        csvData = []
        import csv
        f = open(csvPath, 'r')
        rdr = csv.reader(f)
        for line in rdr:
            csvData.append(line)
        f.close()

        keys = csvData[0]
        dictList =[]
        for i in range(1, len(csvData)):
            targetDict = {}
            for j in range( len( csvData[i] ) ):
                targetDict[ keys[j] ] = csvData[i][j]
            dictList.append( targetDict )
        return dictList


    def save_checkBoxValue(self, checkBox, filePath ):

        data = self.readData(filePath)
        data['checkValue'] = checkBox.isChecked()
        self.writeData( data, filePath )


    def load_checkBoxValue(self, checkBox, filePath ):

        data = self.readData(filePath)
        if data.has_key("checkValue"):
            checkBox.setChecked(data['checkValue'])


    def save_splitterPosition(self, splitter, filePath ):

        data = self.readData(filePath)
        data['size'] = splitter.sizes()
        self.writeData(data, filePath)


    def load_splitterPosition(self, splitter, filePath ):

        data = self.readData(filePath)
        if data.has_key( 'size' ):
            splitter.setSizes( [ value for value in data['size'] ] )




class Commands:

    @staticmethod
    def getTopTransformNodes():

        trs = cmds.ls(type='transform')

        topTransforms = []
        for tr in trs:
            if cmds.listRelatives(tr, p=1): continue
            topTransforms.append(pymel.core.ls(tr)[0])

        return topTransforms


    @staticmethod
    def cleanMeshInScene(*args):
        from maya import cmds
        def cleanMesh(targetObj):
            targetShapes = cmds.listRelatives(targetObj, s=1, f=1)
            for targetShape in targetShapes:
                if not cmds.getAttr(targetShape + '.io'): continue
                if cmds.listConnections(targetShape + '.outMesh', s=0, d=1): continue
                if cmds.listConnections(targetShape + '.worldMesh', s=0, d=1): continue
                cmds.delete(targetShape)
                cmds.warning("%s is deleted" % targetShape)

        meshs = cmds.ls(type='mesh')

        meshObjs = []
        for mesh in meshs:
            if cmds.getAttr(mesh + '.io'): continue
            meshP = cmds.listRelatives(mesh, p=1, f=1)[0]
            if meshP in meshObjs: continue
            meshObjs.append(meshP)
        for meshObj in meshObjs:
            cleanMesh(meshObj)

    @staticmethod
    def cleanScene():
        import pymel.core
        import maya.mel

        audio = pymel.core.ls(type='audio')
        if audio:
            try:
                pymel.core.delete(audio)
            except:
                pass

        for unknown in pymel.core.ls(type='unknown'):
            try:
                pymel.core.delete(unknown)
            except:
                pass

        displayLayers = pymel.core.ls(type='displayLayer')
        for displayLayer in displayLayers:
            if not displayLayer.v.get(): continue
            if displayLayer.name() == 'defaultLayer': continue
            try:
                pymel.core.delete(displayLayer)
            except:
                pass

        sels = pymel.core.ls(type='renderLayer')
        for sel in sels:
            if sel == 'defaultRenderLayer': continue
            try:
                pymel.core.delete(sel)
            except:
                pass
        maya.mel.eval('MLdeleteUnused;')

        try:
            pymel.core.delete('frameCounterUpdate')
        except:
            pass
        try:
            pymel.core.delete('timeCodeUpdate')
        except:
            pass



    @staticmethod
    def removeUnknownPlugin():
        plugins = cmds.unknownPlugin(q=1, list=1)
        if not plugins: plugins = []
        for plugin in plugins:
            try:
                cmds.unknownPlugin(plugin, remove=1)
            except:
                pass


    @staticmethod
    def clearSceneExceptSelected(targetNodes):

        from maya import mel
        targetNodes = pymel.core.ls(targetNodes)
        for ref in pymel.core.ls(type='reference'):
            if ref in targetNodes: continue
            try:
                cmds.file(removeReference=1, referenceNode=ref.name())
            except:
                pass

        for topNode in Commands.getTopTransformNodes():
            if topNode in targetNodes: continue
            try:
                pymel.core.delete(topNode)
            except:
                pass

        Commands.cleanMeshInScene()
        Commands.cleanScene()
        Commands.removeUnknownPlugin()
        mel.eval('MLdeleteUnused')




class Widget_Separator( QFrame ):

    def __init__(self, *args, **kwargs ):
        super( Widget_Separator, self ).__init__( *args, **kwargs )
        self.setFrameShape(QFrame.HLine)




class Widget_basePath( QWidget, Cmds_file_control ):

    path_uiInfo = path_basedir + "/Widget_export_basePath.json"

    def __init__(self, *args,  **kwargs):
        super( Widget_basePath, self ).__init__( *args, **kwargs )
        mainLayout = QHBoxLayout(self);mainLayout.setContentsMargins(0, 0, 0, 0)

        label = QLabel( "Base Path : " )
        label.setStyleSheet( "font-size: 14px;" )
        lineEdit = QLineEdit(); lineEdit.setFixedHeight( 25 )
        button = QPushButton( "..." ); button.setMaximumWidth( 30 )

        mainLayout.addWidget( label )
        mainLayout.addWidget( lineEdit )
        mainLayout.addWidget( button )

        targetdir = os.path.splitext(cmds.file(q=1, sceneName=1))[0]
        button.clicked.connect( self.getBasePath )
        lineEdit.returnPressed.connect( self.cmd_loadList )
        self.lineEdit = lineEdit
        lineEdit.setText( targetdir )


    def cmd_loadList(self):
        if not self.parentWidget(): return
        self.parentWidget().w_referenceFiles.cmd_loadList()


    def getBasePath(self):

        if int(cmds.about(v=1)) < 2017:
            import shiboken
            from PySide.QtGui import QFileDialog, QWidget, QDialog
        else:
            import shiboken2 as shiboken
            from PySide2.QtWidgets import QFileDialog, QWidget, QDialog

        winName = "dialog_getDirectory"
        mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)

        existing_widgets = mayaWin.findChildren(QDialog, winName)
        if existing_widgets: map(lambda x: x.deleteLater(), existing_widgets)

        dialog = QFileDialog( mayaWin )
        dialog.setObjectName( winName )
        dialog.setDirectory( os.path.splitext( cmds.file( q=1, sceneName=1 ) )[0] )
        choosedFolder = dialog.getExistingDirectory()
        if choosedFolder: self.lineEdit.setText(choosedFolder)

        self.cmd_loadList()




class TreeWidgetItem_file( QTreeWidgetItem, Cmds_file_control ):

    def __init__(self, *args, **kwargs ):

        super(TreeWidgetItem_file, self).__init__(*args, **kwargs)


    def setCheckState(self):

        allChecked = True
        originalCheckValues = []
        for checkBox in [ self.treeWidget().topLevelItem(i).checkBox for i in range( self.treeWidget().topLevelItemCount() )]:
            if not checkBox.isChecked():
                allChecked = False;
            originalCheckValues.append( checkBox.isChecked() )

        if allChecked:
            self.treeWidget().checkBox_allItems.setChecked( True )
        else:
            self.treeWidget().checkBox_allItems.setChecked( False )

        for i in range( self.treeWidget().topLevelItemCount() ):
            checkBox = self.treeWidget().topLevelItem(i).checkBox
            checkBox.setChecked( originalCheckValues[i] )


    def addFilePath(self, fileName, enableValue=True ):

        self.checkBox = QCheckBox();
        self.checkBox.setFixedWidth(20)
        self.checkBox.setChecked(True)
        self.lineEdit = QLineEdit()
        self.lineEdit.setText( fileName )
        self.lineEdit.setReadOnly( True )

        self.treeWidget().setItemWidget( self, 0, self.checkBox )
        self.treeWidget().setItemWidget( self, 1, self.lineEdit )

        self.checkBox.stateChanged.connect(self.setCheckState)

        self.checkBox.setEnabled(enableValue)
        self.lineEdit.setEnabled(enableValue)




class Widget_referenceFiles( QWidget, Cmds_file_control ):

    def __init__(self, *args, **kwargs ):

        super( Widget_referenceFiles, self ).__init__( *args, **kwargs )
        self.installEventFilter( self )
        mainLayout = QVBoxLayout( self ); mainLayout.setContentsMargins( 0,0,0,0 ); mainLayout.setSpacing( 8 )

        treeWidget = QTreeWidget()
        headerItem = treeWidget.headerItem()
        checkBox_allItems = QCheckBox( treeWidget ); checkBox_allItems.setFixedWidth( 20 )
        checkBox_allItems.setChecked( True )
        checkBox_allItems.setStyleSheet( "margin: 6px 6px" )
        treeWidget.setItemWidget( headerItem, 0, checkBox_allItems )
        headerItem.setText( 0, "" )
        headerItem.setText( 1, "Reference File Name" )
        treeWidget.setRootIsDecorated( False )
        treeWidget.setStyleSheet("QTreeWidget::item { border-left: 1px solid gray;border-bottom: 1px solid gray; padding: 3px}\
                                 QTreeWidget{ font-size:13px;}" )
        treeWidget.header().setStyleSheet( "font-size:12px;" )
        treeWidget.setColumnWidth( 0, 22 )

        w_buttons = QWidget()
        lay_buttons = QHBoxLayout(w_buttons);
        lay_buttons.setContentsMargins(0, 0, 0, 0)
        buttonReference = QPushButton("REFERENCE")
        buttonCleanExceptSelected = QPushButton("CLEAN EXCEPT SELECTED")
        lay_buttons.addWidget(buttonCleanExceptSelected)
        lay_buttons.addWidget(buttonReference)

        mainLayout.addWidget( treeWidget )
        mainLayout.addWidget( w_buttons )

        self.treeWidget = treeWidget

        self.treeWidget.setSelectionMode( QAbstractItemView.ExtendedSelection )
        self.treeWidget.checkBox_allItems = checkBox_allItems

        checkBox_allItems.stateChanged.connect( self.cmd_setCheckAsset )
        treeWidget.itemPressed.connect( self.cmd_selectItems )
        buttonReference.clicked.connect(self.referenceFiles)
        buttonCleanExceptSelected.clicked.connect( self.cmd_cleanScene )

        self.cmd_loadList()



    def cmd_cleanScene(self):
        targetNodes = pymel.core.ls( sl=1 )
        Commands.clearSceneExceptSelected( targetNodes )



    def cmd_setCheckAsset(self):

        if self.treeWidget.checkBox_allItems.isChecked():
            for item in [ self.treeWidget.topLevelItem(i) for i in range( self.treeWidget.topLevelItemCount() ) ]:
                if item.checkBox.isEnabled() : item.checkBox.setChecked( True )
        else:
            for item in [self.treeWidget.topLevelItem(i) for i in range(self.treeWidget.topLevelItemCount())]:
                if item.checkBox.isEnabled(): item.checkBox.setChecked( False )


    def cmd_selectItems(self, itemWidget, column ):
        if column == 0:
            itemWidget.checkBox.setChecked( not itemWidget.checkBox.isChecked() )
        else:
            pymel.core.select( [ item.asset for item in self.treeWidget.selectedItems() ] )


    def cmd_loadList( self ):

        if not self.parentWidget(): return
        basePath = self.parentWidget().w_basePath.lineEdit.text()

        files = []
        for root, dirs, names in os.walk( basePath ):
            files += [ name for name in names if os.path.splitext( name )[-1].lower() in ['.ma','.mb'] and  not os.path.splitext( name )[0].split( '_' )[0] in ["emptyScene","optimized"] ]
            break

        self.treeWidget.clear()

        refPaths = []
        for refNode in pymel.core.ls(type='reference'):
            try:os.path.normcase(pymel.core.referenceQuery(refNode, f=1).split('{')[0])
            except: continue
            if not refNode.attr('sharedReference').listConnections(s=0, d=1):
                refPaths.append( os.path.normcase(pymel.core.referenceQuery(refNode, f=1).split('{')[0]) )

        scenePath = os.path.normcase( cmds.file( q=1, sceneName=1 ) )
        for fileName in files:
            filePath = os.path.normcase( basePath + '/' + fileName )
            if scenePath == filePath: continue
            item = TreeWidgetItem_file(self.treeWidget)
            enableValue = True if not filePath in refPaths else False
            item.addFilePath( fileName, enableValue )

        self.treeWidget.checkBox_allItems.setChecked( True )
        self.treeWidget.resizeColumnToContents( 0 )
        self.treeWidget.setColumnWidth( 0, self.treeWidget.columnWidth( 0 ) + 10 )


    def referenceFiles(self):

        basePath = self.parentWidget().w_basePath.lineEdit.text()
        items = [ self.treeWidget.topLevelItem( i ) for i in range(self.treeWidget.topLevelItemCount()) ]
        checkValues =[]
        for checkValue, fileName in [ [item.checkBox.isChecked() and item.checkBox.isEnabled(), item.lineEdit.text() ] for item in items ]:
            checkValues.append( checkValue )
            if not checkValue: continue
            onlyFileName = os.path.splitext( fileName )[0]
            cmds.file( basePath + '/' +  fileName, r=1, type= "mayaBinary", ignoreVersion=1, gl=1, mergeNamespacesOnClash=True, namespace=onlyFileName, options="v=0",
                       loadReferenceDepth = "topOnly" )
        self.cmd_loadList()
        items = [ self.treeWidget.topLevelItem( i ) for i in range(self.treeWidget.topLevelItemCount()) ]
        for i in range( len( items ) ):
            if not items[i].checkBox.isEnabled(): continue
            items[i].checkBox.setChecked( checkValues[i] )


    def saveAsOptmized(self):

        import ntpath
        scenePath = cmds.file( q=1, sceneName=1 )
        baseFolder = os.path.dirname( scenePath )
        fileName = ntpath.split( baseFolder )[-1]

        optimizedScenePath = baseFolder + '/optimized_' + fileName + '.mb'
        enabledSave = True
        if os.path.exists( optimizedScenePath ):
            txSave = "Save"
            txCancel = "Cancel"
            confirmResult = cmds.confirmDialog(title='Confirm', message='Scene aleady exists. Do you want to replace it?',
                                               button=[txSave, txCancel],
                                               defaultButton=txCancel, parent= Window.objectName )
            enabledSave = True if confirmResult == txSave else False
        if enabledSave:
            cmds.file(rename=optimizedScenePath)
            cmds.file(s=1, f=1)






class Window( QDialog, Cmds_file_control ):

    mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    objectName = "sg_pingo_widget_scene_optimize_reference"
    title = "PINGO - Scene Optimize Reference"
    defaultWidth = 400
    defaultHeight = 100
    path_uiInfo = path_basedir + "/Main_Window.json"

    def __init__(self, *args, **kwrgs):

        existing_widgets = Window.mayaWin.findChildren( QDialog, Window.objectName )
        if existing_widgets: map( lambda x: x.deleteLater(), existing_widgets )

        super( Window, self ).__init__(  *args, **kwrgs )
        self.installEventFilter( self )
        self.setObjectName( Window.objectName )
        self.setWindowTitle( Window.title )

        mainLayout = QVBoxLayout( self )

        w_basePath        = Widget_basePath()
        button_emptyScene = QPushButton( "Open Empty Scene" )
        w_referenceFiles  = Widget_referenceFiles()
        button_reload     = QPushButton( "RELOAD" )

        mainLayout.addWidget( w_basePath )
        mainLayout.addWidget( button_emptyScene )
        mainLayout.addWidget( w_referenceFiles )
        mainLayout.addWidget( button_reload )

        self.resize( Window.defaultWidth, Window.defaultHeight )
        self.load_shapeInfo( Window.path_uiInfo )

        self.w_basePath    = w_basePath
        self.w_referenceFiles = w_referenceFiles
        self.button_reload  = button_reload

        button_emptyScene.clicked.connect( self.openEmptyScene )
        button_reload.clicked.connect( self.cmd_reload )
        w_referenceFiles.cmd_loadList()

        self.button_emptyScene = button_emptyScene
        self.setEmptySceneButtonCondition()
        self.setStyle()


    def setStyle(self):
        self.setStyleSheet( "font-size:13px" )


    def cmd_reload(self):
        Window(Window.mayaWin).show()



    def setEmptySceneButtonCondition(self):

        basePath = self.w_basePath.lineEdit.text()
        emptyScenePath = basePath + '/emptyScene.mb'
        if os.path.exists( emptyScenePath ):
            self.button_emptyScene.setEnabled( True )
        else:
            self.button_emptyScene.setEnabled( False )


    def openEmptyScene(self):

        from maya import cmds, mel

        def _openEmptyScene():
            basePath = self.w_basePath.lineEdit.text()
            emptyScenePath = basePath + '/emptyScene.mb'
            cmds.file(emptyScenePath, options="v=0;", ignoreVersion=1, loadReferenceDepth="none", typ="mayaBinary", o=1,
                      f=1)
            mel.eval('addRecentFile("%s","mayaBinary");' % emptyScenePath)

        if cmds.file(modified=1, q=1):
            txOpen = "Open"
            txCancel = "Cancel"
            result = cmds.confirmDialog(title='Confirm',
                                               message='Scene is not saved. continue?',
                                               button=[txOpen, txCancel],
                                               defaultButton=txCancel, parent=Window.objectName)
            if result == txOpen:
                _openEmptyScene()
        else:
            _openEmptyScene()
        self.w_referenceFiles.cmd_loadList()


    def eventFilter(self, *args, **kwargs ):
        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Move ]:
            try:self.save_shapeInfo( Window.path_uiInfo )
            except:pass



def show():
    from maya import mel, cmds
    plugins = ['AbcExport', 'AbcImport']
    for plugin in plugins:
        if not cmds.pluginInfo(plugin, q=1, l=1):
            cmds.loadPlugin(plugin)

    try: cmds.deleteUI( Window.objectName, wnd=1 )
    except:pass
    Window( Window.mayaWin ).show()



if __name__ == '__main__':
    show()