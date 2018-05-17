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
        QFont, QGridLayout
else:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    from PySide2.QtWidgets import QListWidgetItem, QDialog, QListWidget, QMainWindow, QWidget, QVBoxLayout, QLabel, \
        QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QAbstractItemView, QMenu, QMessageBox, QSplitter, \
        QScrollArea, QSizePolicy, QTextEdit, QApplication, QFileDialog, QCheckBox, QSlider, \
        QTabWidget, QFrame, QTreeWidgetItem, QTreeWidget, QComboBox, QGroupBox, QAction, QGridLayout

    from PySide2.QtGui import QColor, QCursor, QBrush, QDoubleValidator, QIntValidator, QImage, QPixmap, QTransform, \
        QPaintEvent, QFont


path_uiInfo_basedir = cmds.about(pd=1) + "/pingo/face_shading_object_selector"

class Cmds_file_control(object):

    def __init__(self, *args, **kwargs):

        print "init cmds_file"
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


class Widget_listMeshs( QWidget ):

    def __init__(self, *args, **kwargs ):
        super( Widget_listMeshs, self ).__init__( *args, **kwargs )

        mainLayout = QVBoxLayout( self )
        listWidget = QListWidget()
        button = QPushButton( "Refresh" )
        w_buttons = QWidget()
        lay_buttons = QHBoxLayout( w_buttons ); lay_buttons.setContentsMargins( 0,0,0,0 )
        buttonSelect = QPushButton( "Select One Meterial Face Shaded Objects")
        buttonClear = QPushButton( "Clear")
        lay_buttons.addWidget( buttonSelect )
        lay_buttons.addWidget( buttonClear )
        mainLayout.addWidget( listWidget )
        mainLayout.addWidget(w_buttons)
        mainLayout.addWidget(button)
        listWidget.setSelectionMode( QAbstractItemView.ExtendedSelection)
        self.listWidget = listWidget
        self.load()
        QtCore.QObject.connect(button, QtCore.SIGNAL("clicked()"), self.load )
        QtCore.QObject.connect(buttonSelect, QtCore.SIGNAL("clicked()"), self.selectOneMeterialFaceShadedObjects)
        QtCore.QObject.connect(buttonClear, QtCore.SIGNAL("clicked()"),  self.cmd_clear )
        QtCore.QObject.connect( listWidget, QtCore.SIGNAL( "itemSelectionChanged()" ), self.selectItems )

        self.currentIndex = 0

    def load(self):
        import pymel.core
        def getFaceShadedMeshs():
            meshs = pymel.core.ls(type='mesh')

            targetMeshs = []
            for mesh in meshs:
                seCons = mesh.listConnections(s=1, d=0, type='shadingEngine', p=1, c=1)
                if not seCons: continue
                for origCon, srcCon in seCons:
                    if srcCon.longName() == 'memberWireframeColor':
                        targetMeshs.append(mesh.getParent())
                    continue
            return targetMeshs

        faceShadedMeshs = getFaceShadedMeshs()

        self.listWidget.clear()
        for mesh in faceShadedMeshs:
            self.listWidget.addItem( mesh.name() )

    def selectItems(self):
        items = []
        for item in self.listWidget.selectedItems():
            items.append( item.text() )
        pymel.core.select( items )


    def selectOneMeterialFaceShadedObjects(self):

        self.currentIndex += 1
        self.load()

        targetItems = {}
        for i in range( self.listWidget.count() ):
            item = self.listWidget.item( i )
            target = pymel.core.ls( item.text() )[0]
            targetShape = target.getShape()
            seCons = targetShape.listConnections(s=1, d=0, type='shadingEngine')
            shadingEngineName = seCons[0].name()
            if len( seCons ) == 1:
                if targetItems.has_key( shadingEngineName ):
                    targetItems[shadingEngineName].append( item )
                else:
                    targetItems[shadingEngineName] = [ item ]

        keys = targetItems.keys()
        keys.sort()
        targetKey = keys[ self.currentIndex % len( keys ) ]

        for i in range( self.listWidget.count() ):
            item = self.listWidget.item( i )
            item.setSelected( False )

        targetNames = []
        for targetItem in targetItems[ targetKey ]:
            targetItem.setSelected( True )
        self.selectItems()


    def cmd_clear(self):

        import pymel.core
        def getFaceShadedMeshs_oneShadere():
            meshs = pymel.core.ls(type='mesh')
            targetMeshs = []
            for mesh in meshs:
                seCons = mesh.listConnections(s=1, d=0, type='shadingEngine', p=1, c=1)
                if not seCons: continue
                for origCon, srcCon in seCons:
                    if srcCon.longName() == 'memberWireframeColor':
                        targetMeshs.append(mesh)
                    continue
            return targetMeshs

        targetMeshs = getFaceShadedMeshs_oneShadere()
        meshsDict = {}
        for targetMesh in targetMeshs:
            seCons = targetMesh.listConnections(s=1, d=0, type='shadingEngine')
            shadingEngineName = seCons[0].name()
            if len(seCons) == 1:
                if meshsDict.has_key(shadingEngineName):
                    meshsDict[shadingEngineName].append(targetMesh)
                else:
                    meshsDict[shadingEngineName] = [targetMesh]

        for shadingEngine in meshsDict.keys():
            print "shadingEngine : ", shadingEngine
            meshs = meshsDict[ shadingEngine ]
            [ cmds.sets( mesh.name(), e=1, forceElement = shadingEngine ) for mesh in meshs ]
        self.load()



class Window(QDialog, Cmds_file_control ):

    mayaWin = shiboken.wrapInstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    objectName = "sg_pingo_face_shading_object_selector"
    title = "PINGO - Face shading object selector"
    defaultWidth = 400
    defaultHeight = 400
    path_uiInfo = path_uiInfo_basedir + "/uiInfo.json"

    def __init__(self, *args, **kwrgs):

        existing_widgets = Window.mayaWin.findChildren( QDialog, Window.objectName )
        if existing_widgets: map( lambda x: x.deleteLater(), existing_widgets )

        super( Window, self ).__init__( *args, **kwrgs)
        self.installEventFilter( self )
        self.setObjectName( Window.objectName )
        self.setWindowTitle( Window.title )

        mainLayout = QVBoxLayout( self )
        w_listWidget = Widget_listMeshs()
        mainLayout.addWidget( w_listWidget )
        self.load_shapeInfo(Window.path_uiInfo)

    def eventFilter(self, *args, **kwargs ):
        event = args[1]
        if event.type() in [ QtCore.QEvent.Resize, QtCore.QEvent.Move ]:
            try:self.save_shapeInfo( Window.path_uiInfo )
            except:pass



def show():
    try: cmds.deleteUI( Window.objectName, wnd=1 )
    except:pass
    Window(Window.mayaWin).show()

if __name__ == '__main__':
    show()